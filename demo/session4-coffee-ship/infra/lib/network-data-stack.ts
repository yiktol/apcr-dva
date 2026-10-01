import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as ec2 from 'aws-cdk-lib/aws-ec2';
import * as dynamodb from 'aws-cdk-lib/aws-dynamodb';
import * as sqs from 'aws-cdk-lib/aws-sqs';
import * as ssm from 'aws-cdk-lib/aws-ssm';
import * as secretsmanager from 'aws-cdk-lib/aws-secretsmanager';
import * as appconfig from 'aws-cdk-lib/aws-appconfig';

/**
 * Network + data layer for the coffee-ship demo.
 *
 * Cost-light by design: public subnets only, zero NAT gateways, on-demand
 * DynamoDB. Exposes the VPC, orders queue and orders table so the pipeline
 * stack can wire the ECS service and app to them.
 */
export class NetworkDataStack extends cdk.Stack {
  public readonly vpc: ec2.Vpc;
  public readonly ordersQueue: sqs.Queue;
  public readonly ordersTable: dynamodb.Table;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    // VPC with PUBLIC subnets only and no NAT gateways (keeps the demo cheap).
    this.vpc = new ec2.Vpc(this, 'CoffeeShipVpc', {
      maxAzs: 2,
      natGateways: 0,
      subnetConfiguration: [
        {
          name: 'public',
          subnetType: ec2.SubnetType.PUBLIC,
          cidrMask: 24,
        },
      ],
    });

    // Orders table: on-demand billing, orderId partition key.
    this.ordersTable = new dynamodb.Table(this, 'OrdersTable', {
      tableName: 'coffee-ship-orders',
      partitionKey: { name: 'orderId', type: dynamodb.AttributeType.STRING },
      billingMode: dynamodb.BillingMode.PAY_PER_REQUEST,
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    // Orders queue consumed by the serverless app.
    this.ordersQueue = new sqs.Queue(this, 'OrdersQueue', {
      queueName: 'coffee-ship-orders',
      visibilityTimeout: cdk.Duration.seconds(60),
      retentionPeriod: cdk.Duration.days(4),
    });

    // Non-secret loyalty configuration value (plain SSM parameter).
    new ssm.StringParameter(this, 'LoyaltyConfigParam', {
      parameterName: '/coffee-ship/loyalty/points-per-dollar',
      stringValue: '10',
      description: 'Non-secret loyalty config: loyalty points earned per dollar spent',
    });

    // Placeholder payment-provider API key stored in Secrets Manager.
    new secretsmanager.Secret(this, 'PaymentProviderApiKey', {
      secretName: 'coffee-ship/payment-provider-api-key',
      description: 'Placeholder payment-provider API key for the coffee-ship demo',
      generateSecretString: {
        secretStringTemplate: JSON.stringify({ provider: 'demo-payments' }),
        generateStringKey: 'apiKey',
        passwordLength: 32,
        excludePunctuation: true,
      },
    });

    // AppConfig: application + environment + freeform hosted configuration
    // profile for the "loyalty points" feature flag, plus a staged
    // deployment strategy.
    const appConfigApp = new appconfig.Application(this, 'CoffeeShipAppConfig', {
      applicationName: 'coffee-ship',
      description: 'AppConfig application for coffee-ship feature flags',
    });

    new appconfig.Environment(this, 'CoffeeShipAppConfigEnv', {
      application: appConfigApp,
      environmentName: 'production',
      description: 'Production environment for coffee-ship feature flags',
    });

    new appconfig.HostedConfiguration(this, 'LoyaltyPointsConfig', {
      application: appConfigApp,
      name: 'loyalty-points-feature-flag',
      description: 'Feature flag controlling the loyalty points feature',
      content: appconfig.ConfigurationContent.fromInlineJson(
        JSON.stringify({ loyaltyPointsEnabled: true }),
      ),
      deploymentStrategy: new appconfig.DeploymentStrategy(this, 'StagedDeploymentStrategy', {
        deploymentStrategyName: 'coffee-ship-staged',
        rolloutStrategy: appconfig.RolloutStrategy.linear({
          growthFactor: 20,
          deploymentDuration: cdk.Duration.minutes(10),
          finalBakeTime: cdk.Duration.minutes(5),
        }),
      }),
    });
  }
}
