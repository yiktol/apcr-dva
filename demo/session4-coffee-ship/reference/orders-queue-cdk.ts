// The coffee-shop orders queue declared with AWS CDK (TypeScript).
// Teaching artifact only - not deployed. This snippet mirrors the OrdersQueue
// construct defined in infra/lib/network-data-stack.ts: same queue name,
// visibility timeout and retention period.
import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as sqs from 'aws-cdk-lib/aws-sqs';

export class OrdersQueueExample extends Construct {
  public readonly ordersQueue: sqs.Queue;

  constructor(scope: Construct, id: string) {
    super(scope, id);

    // Orders queue consumed by the serverless app.
    this.ordersQueue = new sqs.Queue(this, 'OrdersQueue', {
      queueName: 'coffee-shop-orders',
      visibilityTimeout: cdk.Duration.seconds(60),
      retentionPeriod: cdk.Duration.days(4),
    });
  }
}
