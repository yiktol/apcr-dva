/**
 * Template assertions for the two stacks. Run via `npm test`
 * (ts-node --prefer-ts-exts test/template.test.ts). A tiny assert harness keeps
 * the pinned toolchain unchanged (no jest). Exits non-zero on any failure.
 */
import * as cdk from 'aws-cdk-lib';
import { Template, Match } from 'aws-cdk-lib/assertions';
import { SecurityDataStack } from '../lib/security-data-stack';
import { AppEdgeAIStack } from '../lib/app-edge-ai-stack';

let failures = 0;
function check(name: string, fn: () => void): void {
  try {
    fn();
    console.log(`  ok  - ${name}`);
  } catch (e) {
    failures += 1;
    console.error(`  FAIL - ${name}`);
    console.error(`        ${(e as Error).message.split('\n')[0]}`);
  }
}

const app = new cdk.App();
const env = { region: 'ap-southeast-1', account: '875692608981' };

const security = new SecurityDataStack(app, 'SecureAssistantSecurityData', { env });
const appEdge = new AppEdgeAIStack(app, 'SecureAssistantAppEdgeAI', {
  env,
  kmsKey: security.kmsKey,
  ordersTable: security.ordersTable,
  pendingRefundsTable: security.pendingRefundsTable,
  paymentSecret: security.paymentSecret,
  configParam: security.configParam,
  guardrailId: security.guardrailId,
  guardrailVersion: security.guardrailVersion,
});

const sec = Template.fromStack(security);
const edge = Template.fromStack(appEdge);

console.log('SecurityData stack:');

check('no AWS::EC2::VPC in SecurityData', () => {
  sec.resourceCountIs('AWS::EC2::VPC', 0);
});

check('one KMS CMK with rotation', () => {
  sec.hasResourceProperties('AWS::KMS::Key', {
    EnableKeyRotation: true,
  });
});

check('two DynamoDB tables with customer-managed KMS', () => {
  sec.resourceCountIs('AWS::DynamoDB::Table', 2);
  sec.hasResourceProperties('AWS::DynamoDB::Table', {
    SSESpecification: { SSEEnabled: true, SSEType: 'KMS' },
  });
});

check('Bedrock Guardrail with Hate+Violence HIGH + PII mask + BLOCK topic', () => {
  sec.hasResourceProperties('AWS::Bedrock::Guardrail', {
    ContentPolicyConfig: {
      FiltersConfig: Match.arrayWith([
        Match.objectLike({ Type: 'HATE', InputStrength: 'HIGH', OutputStrength: 'HIGH' }),
        Match.objectLike({ Type: 'VIOLENCE', InputStrength: 'HIGH', OutputStrength: 'HIGH' }),
      ]),
    },
    SensitiveInformationPolicyConfig: {
      PiiEntitiesConfig: Match.arrayWith([
        Match.objectLike({ Type: 'US_BANK_ACCOUNT_NUMBER' }),
        Match.objectLike({ Type: 'US_SOCIAL_SECURITY_NUMBER' }),
        Match.objectLike({ Type: 'EMAIL' }),
      ]),
    },
    TopicPolicyConfig: {
      TopicsConfig: Match.arrayWith([
        Match.objectLike({ Name: 'legal-advice', Type: 'DENY' }),
      ]),
    },
  });
});

check('published Guardrail version', () => {
  sec.resourceCountIs('AWS::Bedrock::GuardrailVersion', 1);
});

check('raw Bedrock invocation-logging config on CMK-encrypted destinations', () => {
  sec.hasResource('AWS::Bedrock::ModelInvocationLoggingConfiguration', {
    Properties: {
      LoggingConfig: Match.objectLike({
        CloudWatchConfig: Match.anyValue(),
        S3Config: Match.anyValue(),
        TextDataDeliveryEnabled: true,
      }),
    },
  });
});

check('invocation CloudWatch log group is CMK-encrypted', () => {
  sec.hasResourceProperties('AWS::Logs::LogGroup', {
    KmsKeyId: Match.anyValue(),
  });
});

check('Orders table has the byCreatedAt GSI (gsiPk HASH / createdAt RANGE)', () => {
  sec.hasResourceProperties('AWS::DynamoDB::Table', {
    GlobalSecondaryIndexes: Match.arrayWith([
      Match.objectLike({
        IndexName: 'byCreatedAt',
        KeySchema: [
          { AttributeName: 'gsiPk', KeyType: 'HASH' },
          { AttributeName: 'createdAt', KeyType: 'RANGE' },
        ],
        Projection: { ProjectionType: 'ALL' },
      }),
    ]),
  });
});

console.log('AppEdgeAI stack:');

check('no AWS::EC2::VPC in AppEdgeAI', () => {
  edge.resourceCountIs('AWS::EC2::VPC', 0);
});

check('CloudFront distribution with no ACM cert', () => {
  edge.resourceCountIs('AWS::CloudFront::Distribution', 1);
  edge.resourceCountIs('AWS::CertificateManager::Certificate', 0);
});

check('CloudFront has an /api/* cache behavior', () => {
  edge.hasResourceProperties('AWS::CloudFront::Distribution', {
    DistributionConfig: Match.objectLike({
      CacheBehaviors: Match.arrayWith([
        Match.objectLike({ PathPattern: '/api/*' }),
      ]),
    }),
  });
});

check('CloudFront uses an Origin Access Control', () => {
  edge.resourceCountIs('AWS::CloudFront::OriginAccessControl', 1);
});

check('regional WebACL with common rule set + a COUNT rate rule', () => {
  edge.hasResourceProperties('AWS::WAFv2::WebACL', {
    Scope: 'REGIONAL',
    Rules: Match.arrayWith([
      Match.objectLike({
        Name: 'AWSManagedRulesCommonRuleSet',
        Statement: Match.objectLike({
          ManagedRuleGroupStatement: Match.objectLike({
            Name: 'AWSManagedRulesCommonRuleSet',
            VendorName: 'AWS',
          }),
        }),
      }),
      Match.objectLike({
        Name: 'RateLimit',
        Action: { Count: {} },
        Statement: Match.objectLike({
          RateBasedStatement: Match.objectLike({ Limit: 2000, AggregateKeyType: 'IP' }),
        }),
      }),
    ]),
  });
});

check('WebACL associated to the API stage (regional)', () => {
  edge.resourceCountIs('AWS::WAFv2::WebACLAssociation', 1);
});

check('API Gateway stage has X-Ray tracing enabled', () => {
  edge.hasResourceProperties('AWS::ApiGateway::Stage', {
    TracingEnabled: true,
  });
});

check('receipts bucket has a TLS-only DENY resource policy', () => {
  edge.hasResourceProperties('AWS::S3::BucketPolicy', {
    PolicyDocument: Match.objectLike({
      Statement: Match.arrayWith([
        Match.objectLike({
          Effect: 'Deny',
          Condition: { Bool: { 'aws:SecureTransport': 'false' } },
        }),
      ]),
    }),
  });
});

check('assistant Lambda is a container image in the VPC', () => {
  edge.hasResourceProperties('AWS::Lambda::Function', {
    PackageType: 'Image',
    VpcConfig: Match.anyValue(),
    TracingConfig: { Mode: 'Active' },
  });
});

check('two bedrock interface endpoints', () => {
  edge.resourceCountIs('AWS::EC2::VPCEndpoint', 2);
});

check('agent role grants InvokeModel on BOTH ARNs (dual-ARN)', () => {
  // The rendered policy contains the inference-profile ARN and the
  // foundation-model ARN form.
  const json = JSON.stringify(edge.toJSON());
  if (!json.includes('inference-profile/apac.amazon.nova-micro-v1:0')) {
    throw new Error('inference-profile ARN missing from AppEdgeAI template');
  }
  if (!json.includes('foundation-model/amazon.nova-micro-v1:0')) {
    throw new Error('foundation-model ARN missing from AppEdgeAI template');
  }
});

check('ABAC statement keeps the literal ${aws:PrincipalTag/team}', () => {
  const json = JSON.stringify(edge.toJSON());
  if (!json.includes('${aws:PrincipalTag/team}')) {
    throw new Error('literal ${aws:PrincipalTag/team} not found (template-literal regression?)');
  }
});

check('API Gateway has an orders resource with a GET method', () => {
  edge.hasResourceProperties('AWS::ApiGateway::Resource', {
    PathPart: 'orders',
  });
  edge.hasResourceProperties('AWS::ApiGateway::Method', {
    HttpMethod: 'GET',
    ResourceId: { Ref: Match.stringLikeRegexp('AssistantApiapiorders') },
  });
});

check('three Lambda functions have Active X-Ray tracing', () => {
  // 3 app Lambdas (assistant + refund_confirm + presign). Allow >=3 because the
  // s3 auto-delete + bucket-notifications custom resources add helper functions.
  const fns = edge.findResources('AWS::Lambda::Function');
  const active = Object.values(fns).filter(
    (f: any) => f.Properties?.TracingConfig?.Mode === 'Active',
  );
  if (active.length < 3) {
    throw new Error(`expected >=3 Active-traced Lambdas, found ${active.length}`);
  }
});

console.log('');
if (failures > 0) {
  console.error(`${failures} assertion(s) FAILED`);
  process.exit(1);
}
console.log('all template assertions passed');
