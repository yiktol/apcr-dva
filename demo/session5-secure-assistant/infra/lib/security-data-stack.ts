import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as kms from 'aws-cdk-lib/aws-kms';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as logs from 'aws-cdk-lib/aws-logs';
import * as s3 from 'aws-cdk-lib/aws-s3';
import * as iam from 'aws-cdk-lib/aws-iam';
import * as bedrock from 'aws-cdk-lib/aws-bedrock';
import {
  AwsCustomResource,
  AwsCustomResourcePolicy,
  PhysicalResourceId,
} from 'aws-cdk-lib/custom-resources';

/**
 * SecurityData stack — the security + data substrate that must exist first and
 * is referenced (by resource/ARN) by the AppEdgeAI stack:
 *   - one customer-managed KMS CMK (encrypts DynamoDB, receipts, and the Bedrock
 *     invocation-log destination),
 *   - the `orders` and `pending-refunds` DynamoDB tables (CMK-encrypted),
 *   - the Secrets Manager payment-processor key,
 *   - the SSM assistant-config parameter,
 *   - the Bedrock Guardrail + its PUBLISHED version,
 *   - the Bedrock model-invocation-logging configuration to a CMK-encrypted
 *     CloudWatch log group + S3 bucket.
 *
 * All members needed cross-stack are exposed as typed `public readonly`.
 */
export class SecurityDataStack extends cdk.Stack {
  public readonly kmsKey: kms.IKey;
  public readonly ordersTable: dynamodb.ITable;
  public readonly pendingRefundsTable: dynamodb.ITable;
  public readonly paymentSecret: secretsmanager.ISecret;
  public readonly configParam: ssm.IStringParameter;
  public readonly guardrailId: string;
  public readonly guardrailVersion: string;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // ---- KMS CMK ----------------------------------------------------------
    // One customer-managed key encrypts the DynamoDB tables, the receipts
    // bucket (in AppEdgeAI), and the Bedrock invocation-log destination.
    const key = new kms.Key(this, 'SecureAssistantKey', {
      enableKeyRotation: true,
      alias: 'alias/session5-secure-assistant',
      description:
        'session5 secure assistant CMK: DynamoDB, receipts, and Bedrock invocation logs.',
      removalPolicy: cdk.RemovalPolicy.DESTROY, // demo only
    });
    this.kmsKey = key;

    // Allow CloudWatch Logs in THIS region to use the CMK so a log group can be
    // encrypted with it. CloudWatch Logs requires the regional service
    // principal logs.<region>.amazonaws.com on the key policy, scoped by the
    // ArnLike encryption-context condition to this account's log groups.
    // Without this, creating a CMK-encrypted log group fails with
    // "The specified KMS key does not exist or is not allowed to be used".
    key.addToResourcePolicy(
      new iam.PolicyStatement({
        sid: 'AllowCloudWatchLogsUseOfTheKey',
        principals: [
          new iam.ServicePrincipal(`logs.${this.region}.amazonaws.com`),
        ],
        actions: [
          'kms:Encrypt*',
          'kms:Decrypt*',
          'kms:ReEncrypt*',
          'kms:GenerateDataKey*',
          'kms:Describe*',
        ],
        resources: ['*'],
        conditions: {
          ArnLike: {
            'kms:EncryptionContext:aws:logs:arn': `arn:aws:logs:${this.region}:${this.account}:log-group:*`,
          },
        },
      }),
    );

    // ---- DynamoDB tables (CMK-encrypted) ----------------------------------
    const ordersTable = new dynamodb.Table(this, 'OrdersTable', {
      partitionKey: { name: 'orderId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED,
      encryptionKey: key,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // demo only
    });
    this.ordersTable = ordersTable;

    const pendingRefundsTable = new dynamodb.Table(this, 'PendingRefundsTable', {
      partitionKey: {
        name: 'confirmationToken',
        type: dynamodb.AttributeType.STRING,
      },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      encryption: dynamodb.TableEncryption.CUSTOMER_MANAGED,
      encryptionKey: key,
      timeToLiveAttribute: 'ttl', // pending refunds auto-expire
      removalPolicy: cdk.RemovalPolicy.DESTROY, // demo only
    });
    // Tag the table team=support so the ABAC demo (resource-tag == principal-tag)
    // on the support-operator role resolves true for the demo.
    cdk.Tags.of(pendingRefundsTable).add('team', 'support');
    this.pendingRefundsTable = pendingRefundsTable;

    // ---- Secrets Manager payment key --------------------------------------
    this.paymentSecret = new secretsmanager.Secret(this, 'PaymentSecret', {
      secretName: 'session5/payment-processor-key',
      description:
        'session5 demo payment-processor API key (stubbed; the refund path never calls a real processor).',
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ provider: 'demo-processor' }),
        generateStringKey: 'apiKey',
        excludePunctuation: true,
        passwordLength: 40,
      },
    });

    // ---- SSM assistant config ---------------------------------------------
    this.configParam = new ssm.StringParameter(this, 'AssistantConfig', {
      parameterName: '/session5/assistant/config',
      stringValue: JSON.stringify({
        greeting: 'Hi! I am the coffee-shop assistant. How can I help?',
        maxRefund: 50,
        currency: 'USD',
      }),
      description: 'session5 assistant runtime config (greeting, max refund).',
    });

    // ---- Bedrock Guardrail + published version ----------------------------
    // Content filters Hate + Violence at HIGH (input+output); PII MASK for
    // bank-account / SSN / email on both input and output; a BLOCK example via
    // a denied topic ("legal-advice"). Published as a version so it can be
    // referenced by id+version from the Strands BedrockModel.
    const guardrail = new bedrock.CfnGuardrail(this, 'AssistantGuardrail', {
      name: 'session5-secure-assistant',
      description:
        'session5 secure assistant guardrail: Hate+Violence HIGH, PII mask, legal-advice blocked.',
      blockedInputMessaging:
        'I can only help with coffee-shop orders, receipts, and refunds.',
      blockedOutputsMessaging:
        'I can only help with coffee-shop orders, receipts, and refunds.',
      contentPolicyConfig: {
        filtersConfig: [
          { type: 'HATE', inputStrength: 'HIGH', outputStrength: 'HIGH' },
          { type: 'VIOLENCE', inputStrength: 'HIGH', outputStrength: 'HIGH' },
        ],
      },
      sensitiveInformationPolicyConfig: {
        // MASK PII on both input and output. NOTE: the valid Bedrock entity for
        // a bank account number is US_BANK_ACCOUNT_NUMBER (there is no generic
        // ACCOUNT_NUMBER entity). These guardrail masks cover the MODEL channel
        // only — they do NOT see tool-call arguments/results (the "tool-call
        // blind spot"); the Lambda tool handlers mask PII themselves.
        piiEntitiesConfig: [
          { type: 'US_BANK_ACCOUNT_NUMBER', action: 'ANONYMIZE' },
          { type: 'US_SOCIAL_SECURITY_NUMBER', action: 'ANONYMIZE' },
          { type: 'EMAIL', action: 'ANONYMIZE' },
        ],
      },
      topicPolicyConfig: {
        // The BLOCK example: refuse legal-advice requests outright.
        topicsConfig: [
          {
            name: 'legal-advice',
            definition:
              'Requests for legal advice, interpretation of law, or representation.',
            type: 'DENY',
            examples: [
              'Can you give me legal advice about disputing this charge?',
              'What are my legal rights to sue the coffee shop?',
            ],
          },
        ],
      },
    });

    const guardrailVersion = new bedrock.CfnGuardrailVersion(
      this,
      'AssistantGuardrailVersion',
      {
        guardrailIdentifier: guardrail.attrGuardrailId,
        description: 'Published version wired into the Strands BedrockModel.',
      },
    );

    this.guardrailId = guardrail.attrGuardrailId;
    this.guardrailVersion = guardrailVersion.attrVersion;

    // ---- Bedrock invocation logging (CMK-encrypted destinations) ----------
    // CloudWatch log group for the model invocation logs (CMK-encrypted).
    const invokeLogGroup = new logs.LogGroup(this, 'BedrockInvokeLogGroup', {
      logGroupName: '/session5/bedrock/model-invocations',
      retention: logs.RetentionDays.ONE_MONTH,
      encryptionKey: key,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // demo only
    });

    // S3 destination for the model invocation logs (CMK-encrypted).
    const invokeLogBucket = new s3.Bucket(this, 'BedrockInvokeLogBucket', {
      encryption: s3.BucketEncryption.KMS,
      encryptionKey: key,
      bucketKeyEnabled: true,
      blockPublicAccess: s3.BlockPublicAccess.BLOCK_ALL,
      enforceSSL: true,
      removalPolicy: cdk.RemovalPolicy.DESTROY, // demo only
      autoDeleteObjects: true,
    });
    // Bedrock validates (when PutModelInvocationLoggingConfiguration runs) that
    // the bucket policy lets the Bedrock SERVICE write delivery objects. Grant
    // bedrock.amazonaws.com s3:PutObject, scoped to this account/this logging
    // config via aws:SourceAccount + aws:SourceArn. Without this the custom
    // resource fails with "Failed to validate permissions for bucket".
    invokeLogBucket.addToResourcePolicy(
      new iam.PolicyStatement({
        sid: 'AllowBedrockModelInvocationLoggingWrite',
        principals: [new iam.ServicePrincipal('bedrock.amazonaws.com')],
        actions: ['s3:PutObject'],
        resources: [invokeLogBucket.arnForObjects('bedrock/*')],
        conditions: {
          StringEquals: {
            'aws:SourceAccount': this.account,
            's3:x-amz-acl': 'bucket-owner-full-control',
          },
          ArnLike: {
            'aws:SourceArn': `arn:aws:bedrock:${this.region}:${this.account}:*`,
          },
        },
      }),
    );

    // Role Bedrock assumes to write the CloudWatch invocation logs.
    const bedrockLoggingRole = new iam.Role(this, 'BedrockLoggingRole', {
      assumedBy: new iam.ServicePrincipal('bedrock.amazonaws.com'),
      description:
        'Role Bedrock assumes to deliver model-invocation logs to CloudWatch + S3.',
    });
    invokeLogGroup.grantWrite(bedrockLoggingRole);
    invokeLogBucket.grantWrite(bedrockLoggingRole);

    // The CloudWatch Logs service encrypts the (already-CMK) log group entries;
    // allow the logs delivery principal to use the key for the log group.
    key.grant(
      new iam.ServicePrincipal('delivery.logs.amazonaws.com'),
      'kms:GenerateDataKey*',
      'kms:Decrypt',
    );
    // The Bedrock logging role must be able to encrypt what it writes.
    key.grantEncryptDecrypt(bedrockLoggingRole);
    // Bedrock also writes S3 delivery objects as the SERVICE, so the CMK must
    // let bedrock.amazonaws.com generate a data key for the CMK-encrypted
    // destination bucket (scoped to this account).
    key.addToResourcePolicy(
      new iam.PolicyStatement({
        sid: 'AllowBedrockServiceUseOfTheKeyForLogDelivery',
        principals: [new iam.ServicePrincipal('bedrock.amazonaws.com')],
        actions: ['kms:GenerateDataKey*', 'kms:Decrypt'],
        resources: ['*'],
        conditions: {
          StringEquals: { 'aws:SourceAccount': this.account },
        },
      }),
    );

    // Bedrock model-invocation logging is NOT a CloudFormation resource type
    // (there is no AWS::Bedrock::ModelInvocationLoggingConfiguration, and no
    // L1/L2 in aws-cdk-lib@2.160.0). It is an account/Region SINGLETON set via
    // the Bedrock control-plane API PutModelInvocationLoggingConfiguration.
    // Provision it with an AwsCustomResource that calls that API on
    // create/update and DeleteModelInvocationLoggingConfiguration on delete, so
    // the CMK destinations are not pinned when the stack is torn down.
    const loggingConfig = {
      cloudWatchConfig: {
        logGroupName: invokeLogGroup.logGroupName,
        roleArn: bedrockLoggingRole.roleArn,
      },
      s3Config: {
        bucketName: invokeLogBucket.bucketName,
        keyPrefix: 'bedrock/',
      },
      textDataDeliveryEnabled: true,
      embeddingDataDeliveryEnabled: false,
      imageDataDeliveryEnabled: false,
    };
    const invokeLogging = new AwsCustomResource(this, 'BedrockInvokeLogging', {
      resourceType: 'Custom::BedrockModelInvocationLogging',
      onCreate: {
        service: 'Bedrock',
        action: 'putModelInvocationLoggingConfiguration',
        parameters: { loggingConfig },
        physicalResourceId: PhysicalResourceId.of(
          `bedrock-invocation-logging-${this.region}`,
        ),
      },
      onUpdate: {
        service: 'Bedrock',
        action: 'putModelInvocationLoggingConfiguration',
        parameters: { loggingConfig },
        physicalResourceId: PhysicalResourceId.of(
          `bedrock-invocation-logging-${this.region}`,
        ),
      },
      onDelete: {
        service: 'Bedrock',
        action: 'deleteModelInvocationLoggingConfiguration',
      },
      policy: AwsCustomResourcePolicy.fromStatements([
        new iam.PolicyStatement({
          actions: [
            'bedrock:PutModelInvocationLoggingConfiguration',
            'bedrock:DeleteModelInvocationLoggingConfiguration',
            'bedrock:GetModelInvocationLoggingConfiguration',
          ],
          resources: ['*'], // these actions do not support resource scoping
        }),
        // The custom-resource Lambda must pass the Bedrock logging role to the
        // Bedrock service when configuring CloudWatch delivery.
        new iam.PolicyStatement({
          actions: ['iam:PassRole'],
          resources: [bedrockLoggingRole.roleArn],
        }),
      ]),
      installLatestAwsSdk: false,
    });
    // Ensure the destinations + grants exist before the logging config is made.
    invokeLogging.node.addDependency(invokeLogGroup);
    invokeLogging.node.addDependency(invokeLogBucket);
    invokeLogging.node.addDependency(bedrockLoggingRole);

    // ---- Outputs ----------------------------------------------------------
    new cdk.CfnOutput(this, 'GuardrailIdOutput', { value: this.guardrailId });
    new cdk.CfnOutput(this, 'GuardrailVersionOutput', {
      value: this.guardrailVersion,
    });
    new cdk.CfnOutput(this, 'KmsKeyArnOutput', { value: key.keyArn });
  }
}
