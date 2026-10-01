#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { NetworkDataStack } from '../lib/network-data-stack';
import { AppPipelineStack } from '../lib/app-pipeline-stack';

const app = new cdk.App();

// Region is pinned to ap-southeast-1 for the whole demo. Account comes from
// CDK_DEFAULT_ACCOUNT (a dummy 12-digit value is fine for `cdk synth`).
const env: cdk.Environment = {
  region: 'ap-southeast-1',
  account: process.env.CDK_DEFAULT_ACCOUNT,
};

const networkData = new NetworkDataStack(app, 'CoffeeShipNetworkData', {
  env,
  description: 'coffee-ship demo: ECR, DynamoDB, SQS, SSM, Secrets Manager, AppConfig (VPC is imported, not created). ECR lives here so it can be seeded before the pipeline stack ECS services.',
});

new AppPipelineStack(app, 'CoffeeShipAppPipeline', {
  env,
  description: 'coffee-ship demo: two ECS Fargate environments (test rolling + prod CodeDeploy blue/green) behind ALBs fronted by CloudFront (ALB SGs locked to the CloudFront prefix list), CodePipeline (S3 source) with real CodeBuild (docker) + ECS/CodeDeploy deploy actions + manual approval. Uses the existing VPC imported from CloudFormation exports and the ECR repo from the network stack.',
  ordersQueue: networkData.ordersQueue,
  ordersTable: networkData.ordersTable,
  loyaltyParam: networkData.loyaltyParam,
  repository: networkData.repository,
});

app.synth();
