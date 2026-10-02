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

    // AWS::Bedrock::ModelInvocationLoggingConfiguration has NO L1/L2 construct
    // in aws-cdk-lib@2.160.0 (the aws-bedrock module ships only
    // CfnAgent/.../CfnGuardrail/CfnGuardrailVersion/CfnKnowledgeBase/CfnPrompt*).
    // Provision it with an escape-hatch raw CfnResource. This is a per-account/
    // region singleton that destroy.sh tears down before stack delete so the
    // CMK is not pinned.
    const invokeLogging = new cdk.CfnResource(this, 'BedrockInvokeLogging', {
      type: 'AWS::Bedrock::ModelInvocationLoggingConfiguration',
      properties: {
        LoggingConfig: {
          CloudWatchConfig: {
            LogGroupName: invokeLogGroup.logGroupName,
            RoleArn: bedrockLoggingRole.roleArn,
          },
          S3Config: {
            BucketName: invokeLogBucket.bucketName,
            KeyPrefix: 'bedrock/',
          },
          TextDataDeliveryEnabled: true,
          EmbeddingDataDeliveryEnabled: false,
          ImageDataDeliveryEnabled: false,
        },
      },
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
