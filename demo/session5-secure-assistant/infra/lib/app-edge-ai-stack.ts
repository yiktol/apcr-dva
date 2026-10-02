import * as cdk from 'aws-cdk-lib';
import * as path from 'path';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as s3deploy from 'aws-cdk-lib/aws-s3-deployment';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as lambda from 'aws-cdk-lib/aws-lambda';
import * as ecr from 'aws-cdk-lib/aws-ecr';
import * as apigateway from 'aws-cdk-lib/aws-apigateway';
import * as wafv2 from 'aws-cdk-lib/aws-wafv2';
import * as cloudfront from 'aws-cdk-lib/aws-cloudfront';
import * as origins from 'aws-cdk-lib/aws-cloudfront-origins';
import { importVpc, privateSubnetSelection } from './vpc-import';

const REGION = 'ap-southeast-1';
// The APAC Nova Micro inference-profile id doubles as the model_id passed to the
// Strands BedrockModel. Both the inference-profile ARN and the foundation-model
// ARN form are granted (the AWS-required dual-ARN shape for inference profiles).
const NOVA_PROFILE_ARN = `arn:aws:bedrock:${REGION}:875692608981:inference-profile/apac.amazon.nova-micro-v1:0`;
const NOVA_FOUNDATION_ARN =
  'arn:aws:bedrock:*::foundation-model/amazon.nova-micro-v1:0';

export interface AppEdgeAIStackProps extends cdk.StackProps {
  readonly kmsKey: kms.IKey;
  readonly ordersTable: dynamodb.ITable;
  readonly pendingRefundsTable: dynamodb.ITable;
  readonly paymentSecret: secretsmanager.ISecret;
  readonly configParam: ssm.IStringParameter;
  readonly guardrailId: string;
  readonly guardrailVersion: string;
}

/**
 * AppEdgeAI stack — the edge + compute + observability layer: imported VPC,
 * security groups, the two Bedrock interface endpoints, the receipts + SPA S3
 * buckets, the three Lambdas (assistant container image + refund-confirm +
 * presign) with least-privilege / ABAC / identity+resource IAM, the regional
 * WAF, the API Gateway REST API (X-Ray on), and the CloudFront distribution
 * (OAC SPA default + /api/* API behavior).
 */
export class AppEdgeAIStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props: AppEdgeAIStackProps) {
    super(scope, id, props);

    const {
      kmsKey,
      ordersTable,
      pendingRefundsTable,
      paymentSecret,
      configParam,
      guardrailId,
      guardrailVersion,
    } = props;

    // ---- Imported VPC + security groups -----------------------------------
    const vpc = importVpc(this);
    const privateSubnets = privateSubnetSelection(this);

    // The assistant Lambda's SG. Egress is allowed (default) so it can reach the
    // interface endpoints / gateway endpoints; the ONLY Bedrock path that
    // matters is 443 to the endpoint SG below.
    const assistantSg = new ec2.SecurityGroup(this, 'AssistantSg', {
      vpc,
      description: 'session5 assistant Lambda SG',
      allowAllOutbound: true,
    });

    // The Bedrock interface-endpoint SG: ingress 443 ONLY from the assistant SG.
    const bedrockEndpointSg = new ec2.SecurityGroup(this, 'BedrockEndpointSg', {
      vpc,
      description: 'session5 Bedrock interface endpoint SG (443 from assistant only)',
      allowAllOutbound: true,
    });
    bedrockEndpointSg.addIngressRule(
      assistantSg,
      ec2.Port.tcp(443),
      'HTTPS from the assistant Lambda only',
    );

    const guardrailArn = `arn:aws:bedrock:${REGION}:${this.account}:guardrail/${guardrailId}`;

    // ---- Bedrock interface VPC endpoints -----------------------------------
    // TEACHING POINT: a Lambda in a "private subnet" with a NAT route would
    // reach Bedrock over the public internet via NAT. Routing Bedrock traffic
    // over PrivateLink requires THIS interface endpoint; with privateDns enabled
    // the standard bedrock-runtime.<region>.amazonaws.com SDK endpoint resolves
    // to the endpoint ENIs inside the VPC. "private subnet" != "private path".
    const bedrockRuntimeEndpoint = new ec2.InterfaceVpcEndpoint(
      this,
      'BedrockRuntimeEndpoint',
      {
        vpc,
        service: ec2.InterfaceVpcEndpointAwsService.BEDROCK_RUNTIME,
        subnets: privateSubnets,
        securityGroups: [bedrockEndpointSg],
        privateDnsEnabled: true,
      },
    );

    // Control-plane endpoint: ApplyGuardrail / guardrail metadata resolve
    // against the bedrock (not bedrock-runtime) service.
    const bedrockControlEndpoint = new ec2.InterfaceVpcEndpoint(
      this,
      'BedrockControlEndpoint',
      {
        vpc,
        service: ec2.InterfaceVpcEndpointAwsService.BEDROCK,
        subnets: privateSubnets,
        securityGroups: [bedrockEndpointSg],
        privateDnsEnabled: true,
      },
    );

    // Non-wildcard endpoint policy: only the three Bedrock actions on the Nova
    // inference-profile + foundation-model ARNs + the guardrail ARN. This is the
    // RESOURCE half of the identity-vs-resource pairing for Bedrock access.
    // bedrock:ApplyGuardrail is included DEFENSIVELY — the inline-guardrail
    // wiring (guardrail config on InvokeModel) may not issue a separate
    // ApplyGuardrail call, so this grant can be unused at runtime; it is kept
    // least-privilege-scoped to the guardrail ARN.
    const endpointStatement = new iam.PolicyStatement({
      effect: iam.Effect.ALLOW,
      principals: [new iam.AnyPrincipal()],
      actions: [
        'bedrock:InvokeModel',
        'bedrock:InvokeModelWithResponseStream',
        'bedrock:ApplyGuardrail',
      ],
      resources: [NOVA_PROFILE_ARN, NOVA_FOUNDATION_ARN, guardrailArn],
    });
    bedrockRuntimeEndpoint.addToPolicy(endpointStatement);
    bedrockControlEndpoint.addToPolicy(endpointStatement);

    // ---- Receipts bucket (CMK, TLS-only DENY) ------------------------------
    const receiptsBucket = new s3.Bucket(this, 'ReceiptsBucket', {
      encryption: s3.BucketEncryption.KMS,
      encryptionKey: kmsKey,
      bucketKeyEnabled: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // demo only
      autoDeleteObjects: true,
    });
    // RESOURCE policy half of the identity-vs-resource pairing on receipts:
    // DENY all S3 when the request is not over TLS.
    receiptsBucket.addToResourcePolicy(
      new iam.PolicyStatement({
        sid: 'DenyInsecureTransport',
        effect: iam.Effect.DENY,
        principals: [new iam.AnyPrincipal()],
        actions: ['s3:*'],
        resources: [receiptsBucket.bucketArn, receiptsBucket.arnForObjects('*')],
        conditions: { Bool: { 'aws:SecureTransport': 'false' } },
      }),
    );

    // ---- SPA bucket (OAC-served, private) ----------------------------------
    const spaBucket = new s3.Bucket(this, 'SpaBucket', {
      encryption: s3.BucketEncryption.S3_MANAGED,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // demo only
      autoDeleteObjects: true,
    });
    // Defense-in-depth TLS-only deny on the SPA bucket too.
    spaBucket.addToResourcePolicy(
      new iam.PolicyStatement({
        sid: 'DenyInsecureTransport',
        effect: iam.Effect.DENY,
        principals: [new iam.AnyPrincipal()],
        actions: ['s3:*'],
        resources: [spaBucket.bucketArn, spaBucket.arnForObjects('*')],
        conditions: { Bool: { 'aws:SecureTransport': 'false' } },
      }),
    );

    // ---- Lambda functions --------------------------------------------------
    const appRoot = path.join(__dirname, '..', '..', 'app');

    // Assistant: container-image Lambda in the private subnets.
    //
    // The image is published to a DEDICATED ECR repo (not a CDK asset) and
    // referenced here by a fixed tag. This is deliberate: CDK's fromImageAsset
    // builds via the local buildx/colima toolchain, which on this host emits an
    // OCI image index with provenance/attestation manifests that AWS Lambda
    // REJECTS ("image manifest ... media type ... is not supported"). deploy.sh
    // builds + pushes a Lambda-compatible single Docker-schema2 image to this
    // repo (buildx --provenance=false --sbom=false) BEFORE deploying this stack.
    // The repo is created + populated by deploy.sh BEFORE this stack deploys,
    // so we IMPORT it by name here (CDK does not own its lifecycle; destroy.sh
    // deletes it).
    const assistantRepo = ecr.Repository.fromRepositoryName(
      this,
      'AssistantRepo',
      'session5-secure-assistant',
    );
    const assistantFn = new lambda.DockerImageFunction(this, 'AssistantFn', {
      code: lambda.DockerImageCode.fromEcr(assistantRepo, {
        tagOrDigest: 'latest',
      }),
      // Match the image platform; Lambda default architecture is x86_64.
      architecture: lambda.Architecture.X86_64,
      vpc,
      vpcSubnets: privateSubnets,
      securityGroups: [assistantSg],
      timeout: cdk.Duration.seconds(60),
      memorySize: 1024,
      tracing: lambda.Tracing.ACTIVE,
      environment: {
        AWS_REGION_PINNED: REGION,
        GUARDRAIL_ID: guardrailId,
        GUARDRAIL_VERSION: guardrailVersion,
        NOVA_MODEL_ID: 'apac.amazon.nova-micro-v1:0',
        ORDERS_TABLE: ordersTable.tableName,
        PENDING_REFUNDS_TABLE: pendingRefundsTable.tableName,
        PAYMENT_SECRET_NAME: paymentSecret.secretName,
        CONFIG_PARAM_NAME: configParam.parameterName,
      },
    });

    // Refund-confirm: plain zip Lambda (pure boto3). The ONLY executor of a
    // confirmed refund (moves money is stubbed).
    const refundConfirmFn = new lambda.Function(this, 'RefundConfirmFn', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset(path.join(appRoot, 'refund_confirm')),
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
      tracing: lambda.Tracing.ACTIVE,
      environment: {
        AWS_REGION_PINNED: REGION,
        PENDING_REFUNDS_TABLE: pendingRefundsTable.tableName,
        PAYMENT_SECRET_NAME: paymentSecret.secretName,
      },
    });

    // Presign: plain zip Lambda. Generates a 15-min GET presigned URL for a
    // receipt object.
    const presignFn = new lambda.Function(this, 'PresignFn', {
      runtime: lambda.Runtime.PYTHON_3_12,
      handler: 'handler.handler',
      code: lambda.Code.fromAsset(path.join(appRoot, 'presign')),
      timeout: cdk.Duration.seconds(30),
      memorySize: 256,
      tracing: lambda.Tracing.ACTIVE,
      environment: {
        AWS_REGION_PINNED: REGION,
        RECEIPTS_BUCKET: receiptsBucket.bucketName,
      },
    });

    // ---- IAM: assistant role (least privilege, dual-ARN Bedrock grant) -----
    const assistantRole = assistantFn.role as iam.Role;
    assistantRole.addToPolicy(
      new iam.PolicyStatement({
        sid: 'BedrockInvokeNova',
        effect: iam.Effect.ALLOW,
        actions: [
          'bedrock:InvokeModel',
          'bedrock:InvokeModelWithResponseStream',
        ],
        // BOTH the inference-profile ARN and the foundation-model ARN form (the
        // *::foundation-model/... wildcard is the AWS-required ARN shape, not an
        // over-grant).
        resources: [NOVA_PROFILE_ARN, NOVA_FOUNDATION_ARN],
      }),
    );
    assistantRole.addToPolicy(
      new iam.PolicyStatement({
        // Included DEFENSIVELY — the inline guardrail path may not issue a
        // separate ApplyGuardrail call; scoped tightly to the guardrail ARN.
        sid: 'BedrockApplyGuardrail',
        effect: iam.Effect.ALLOW,
        actions: ['bedrock:ApplyGuardrail'],
        resources: [guardrailArn],
      }),
    );
    ordersTable.grantReadWriteData(assistantRole);
    pendingRefundsTable.grantReadWriteData(assistantRole);
    paymentSecret.grantRead(assistantRole);
    configParam.grantRead(assistantRole);
    kmsKey.grantEncryptDecrypt(assistantRole);
    // X-Ray write (ACTIVE tracing wires the managed policy, but keep an explicit
    // scoped grant too for teaching clarity).
    assistantRole.addToPolicy(
      new iam.PolicyStatement({
        sid: 'XRayWrite',
        effect: iam.Effect.ALLOW,
        actions: [
          'xray:PutTraceSegments',
          'xray:PutTelemetryRecords',
        ],
        resources: ['*'], // X-Ray write actions do not support resource scoping
      }),
    );

    // ---- IAM: refund-confirm role (ABAC + scoped grants) -------------------
    const refundRole = refundConfirmFn.role as iam.Role;
    pendingRefundsTable.grantReadWriteData(refundRole);
    paymentSecret.grantRead(refundRole);
    kmsKey.grantEncryptDecrypt(refundRole);
    // Tag the operator/refund role team=support so the ABAC condition resolves
    // true against the pending-refunds table (also tagged team=support).
    cdk.Tags.of(refundRole).add('team', 'support');
    refundRole.addToPolicy(
      new iam.PolicyStatement({
        sid: 'AbacTagMatch',
        effect: iam.Effect.ALLOW,
        actions: ['dynamodb:GetItem', 'dynamodb:UpdateItem'],
        resources: [pendingRefundsTable.tableArn],
        conditions: {
          // IMPORTANT: single-quoted (non-template) string. The IAM policy
          // variable ${aws:PrincipalTag/team} must reach the RENDERED policy
          // VERBATIM. A backtick template literal would make JS try to
          // interpolate `aws:...` (not a valid JS expression) — so this MUST NOT
          // be a template literal.
          StringEquals: {
            'aws:ResourceTag/team': '${aws:PrincipalTag/team}',
          },
        },
      }),
    );

    // ---- IAM: presign role (identity half of the pairing) ------------------
    const presignRole = presignFn.role as iam.Role;
    // IDENTITY policy: s3:GetObject on receipts objects (needed so the presigned
    // URL's signature is valid). Pairs with the receipts bucket RESOURCE DENY.
    presignRole.addToPolicy(
      new iam.PolicyStatement({
        sid: 'ReadReceipts',
        effect: iam.Effect.ALLOW,
        actions: ['s3:GetObject'],
        resources: [receiptsBucket.arnForObjects('*')],
      }),
    );
    kmsKey.grantDecrypt(presignRole);

    // ---- API Gateway REST API (X-Ray on) -----------------------------------
    const api = new apigateway.RestApi(this, 'AssistantApi', {
      restApiName: 'session5-secure-assistant',
      description: 'session5 secure assistant API (behind CloudFront /api/*).',
      endpointConfiguration: { types: [apigateway.EndpointType.REGIONAL] },
      deployOptions: {
        stageName: 'prod',
        tracingEnabled: true, // X-Ray on the API GW stage (Act 4)
        metricsEnabled: true,
      },
    });

    // Keep the /api prefix in the API so the viewer path /api/chat maps 1:1 to
    // the API resource /api/chat (CloudFront does not strip the /api prefix).
    const apiRoot = api.root.addResource('api');
    const chat = apiRoot.addResource('chat');
    chat.addMethod('POST', new apigateway.LambdaIntegration(assistantFn));

    const refunds = apiRoot.addResource('refunds');
    const confirm = refunds.addResource('confirm');
    confirm.addMethod(
      'POST',
      new apigateway.LambdaIntegration(refundConfirmFn),
    );

    const receipts = apiRoot.addResource('receipts');
    const receiptById = receipts.addResource('{orderId}');
    const receiptUrl = receiptById.addResource('url');
    receiptUrl.addMethod('GET', new apigateway.LambdaIntegration(presignFn));

    // ---- Regional WAF WebACL + association ---------------------------------
    const webAcl = new wafv2.CfnWebACL(this, 'ApiWebAcl', {
      scope: 'REGIONAL',
      defaultAction: { allow: {} },
      visibilityConfig: {
        cloudWatchMetricsEnabled: true,
        metricName: 'session5-api-acl',
        sampledRequestsEnabled: true,
      },
      rules: [
        {
          name: 'AWSManagedRulesCommonRuleSet',
          priority: 0,
          overrideAction: { none: {} }, // let the managed group's own actions apply
          statement: {
            managedRuleGroupStatement: {
              vendorName: 'AWS',
              name: 'AWSManagedRulesCommonRuleSet',
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: 'common-rule-set',
            sampledRequestsEnabled: true,
          },
        },
        {
          name: 'RateLimit',
          priority: 1,
          // COUNT mode by design (demo): count, do not block. To BLOCK, replace
          // `action: { count: {} }` with `action: { block: {} }`.
          action: { count: {} },
          statement: {
            rateBasedStatement: {
              limit: 2000,
              aggregateKeyType: 'IP',
            },
          },
          visibilityConfig: {
            cloudWatchMetricsEnabled: true,
            metricName: 'rate-limit',
            sampledRequestsEnabled: true,
          },
        },
      ],
    });

    // Associate the regional WebACL with the deployed API stage.
    const stageArn = `arn:aws:apigateway:${REGION}::/restapis/${api.restApiId}/stages/${api.deploymentStage.stageName}`;
    new wafv2.CfnWebACLAssociation(this, 'ApiWebAclAssociation', {
      resourceArn: stageArn,
      webAclArn: webAcl.attrArn,
    });

    // ---- CloudFront distribution (OAC SPA default + /api/* API) ------------
    const distribution = new cloudfront.Distribution(this, 'Distribution', {
      comment: 'session5 secure assistant (SPA + /api/*)',
      defaultRootObject: 'index.html',
      defaultBehavior: {
        origin: origins.S3BucketOrigin.withOriginAccessControl(spaBucket),
        viewerProtocolPolicy: cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
        cachePolicy: cloudfront.CachePolicy.CACHING_OPTIMIZED,
        allowedMethods: cloudfront.AllowedMethods.ALLOW_GET_HEAD,
      },
      additionalBehaviors: {
        '/api/*': {
          origin: new origins.RestApiOrigin(api),
          viewerProtocolPolicy:
            cloudfront.ViewerProtocolPolicy.REDIRECT_TO_HTTPS,
          cachePolicy: cloudfront.CachePolicy.CACHING_DISABLED,
          originRequestPolicy:
            cloudfront.OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER,
          allowedMethods: cloudfront.AllowedMethods.ALLOW_ALL,
        },
      },
      // Default CloudFront domain + default *.cloudfront.net cert — no custom
      // domain, no Route53, no ACM certificate.
    });

    // ---- SPA deploy --------------------------------------------------------
    new s3deploy.BucketDeployment(this, 'SpaDeployment', {
      sources: [s3deploy.Source.asset(path.join(__dirname, '..', '..', 'spa'))],
      destinationBucket: spaBucket,
      distribution,
      distributionPaths: ['/*'],
    });

    // ---- Outputs -----------------------------------------------------------
    new cdk.CfnOutput(this, 'CloudFrontUrl', {
      value: `https://${distribution.distributionDomainName}`,
      description: 'The single entry point (SPA + /api/*).',
    });
    new cdk.CfnOutput(this, 'ApiUrl', {
      value: api.url,
      description: 'API Gateway stage URL (protected by the regional WAF).',
    });
    new cdk.CfnOutput(this, 'ReceiptsBucketName', {
      value: receiptsBucket.bucketName,
    });
  }
}
