#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { SecurityDataStack } from '../lib/security-data-stack';
import { AppEdgeAIStack } from '../lib/app-edge-ai-stack';

const app = new cdk.App();

// Region is pinned to ap-southeast-1 for the whole project. Account comes from
// CDK_DEFAULT_ACCOUNT (a dummy 12-digit value is fine for `cdk synth`).
const env: cdk.Environment = {
  region: 'ap-southeast-1',
  account: process.env.CDK_DEFAULT_ACCOUNT,
};

const securityData = new SecurityDataStack(app, 'SecureAssistantSecurityData', {
  env,
  description:
    'session5 secure assistant: KMS CMK, DynamoDB (orders + pending-refunds), receipts/log encryption key, Secrets Manager payment key, SSM config, Bedrock Guardrail + version, and Bedrock model-invocation logging. The security/data substrate referenced by the AppEdgeAI stack.',
});

new AppEdgeAIStack(app, 'SecureAssistantAppEdgeAI', {
  env,
  description:
    'session5 secure assistant: CloudFront (OAC SPA + /api/*) -> regional WAF -> API Gateway -> private-subnet Strands assistant Lambda -> Bedrock Nova Micro via PrivateLink; refund-confirm + presign Lambdas; receipts bucket (CMK, TLS-only); X-Ray throughout. Imports the SecurityData substrate.',
  kmsKey: securityData.kmsKey,
  ordersTable: securityData.ordersTable,
  pendingRefundsTable: securityData.pendingRefundsTable,
  paymentSecret: securityData.paymentSecret,
  configParam: securityData.configParam,
  guardrailId: securityData.guardrailId,
  guardrailVersion: securityData.guardrailVersion,
});

app.synth();
