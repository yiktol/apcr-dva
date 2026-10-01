# FEAT-002 Verification

Grant the ECS task role `ssm:GetParameter` on the loyalty parameter.

## Commands run (local only, no AWS mutation)

```
cd infra && npm install            # ok
npx tsc --noEmit                   # exit 0, no type errors (TSC_CLEAN)
CDK_DEFAULT_ACCOUNT=875692608981 JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1 \
  npx cdk synth CoffeeShipAppPipeline > /dev/null   # exit 0
```

Grepped: `infra/cdk.out/CoffeeShipAppPipeline.template.json`

## Findings

### (a) ssm:GetParameter on the loyalty param, attached to the ECS task role — PASS
The synthesized task-role default policy (`PolicyName: CoffeeShipServiceTaskDefTaskRoleDefaultPolicyBAC190E2`, attached to role ref `CoffeeShipServiceTaskDefTaskRole86B28230`) contains a new statement:

```
Action: [ "ssm:GetParameter", "ssm:GetParameterHistory", "ssm:GetParameters" ]
Effect: Allow
Resource: Fn::Join [ "", [
  "arn:aws:ssm:ap-southeast-1:875692608981:parameter",
  { "Fn::ImportValue": "CoffeeShipNetworkData:ExportsOutputRefLoyaltyConfigParamA2A1FCF2389050AE" }
] ]
```

- Loyalty parameter logical id (NetworkDataStack): `LoyaltyConfigParam` (CDK logical id suffix `A2A1FCF2`).
- Cross-stack export consumed by the pipeline stack: `CoffeeShipNetworkData:ExportsOutputRefLoyaltyConfigParamA2A1FCF2389050AE`.
- ARN form resolved at deploy time: `arn:aws:ssm:ap-southeast-1:875692608981:parameter/coffee-ship/loyalty/points-per-dollar` (the parameter name begins with `/`, so the join yields `.../parameter/coffee-ship/...`).

### (b) ALB SG ingress is SourcePrefixListId only, no 0.0.0.0/0 — PASS
The ALB security group ingress block:

```
SecurityGroupIngress:
  - Description: "Allow HTTP only from the CloudFront origin-facing prefix list"
    IpProtocol: tcp, FromPort: 80, ToPort: 80
    SourcePrefixListId: { Ref: CloudFrontPrefixListId }
```

`grep -c '"CidrIp": "0.0.0.0/0"'` returns 1, and that single match is the ECS **Service** SG default `SecurityGroupEgress` ("Allow all outbound traffic by default", IpProtocol -1) — a CDK default, NOT an ALB ingress rule. No `0.0.0.0/0` appears in any `SecurityGroupIngress`.

### (c) CloudFront distribution present — PASS
`grep -c 'AWS::CloudFront::Distribution'` = 1 (`CoffeeShipCdn`).

### (d) No VPC created — PASS
`grep -c 'AWS::EC2::VPC"'` = 0. VPC is imported via `Fn::ImportValue: VpcId`.

### (e) Both EcsDeployAction stages present — PASS
Actions `Deploy_To_Test` and `Deploy_To_Prod` both present in the pipeline (stages Deploy-Test and Deploy-Prod).

### (f) EventBridge S3 Object Created rule for source.zip — PASS
EventBridge rule present with detailType `Object Created` and object key `source.zip`.

### (g) tsc --noEmit clean — PASS
`npx tsc --noEmit` exits 0 with no type errors.

## Preserved (unchanged) security properties
CloudFront distribution, ALB-SG CloudFront-prefix-list lock (no 0.0.0.0/0 ingress), imported VPC (no VPC created), ECR keep-10 lifecycle, both EcsDeployAction stages, and the EventBridge S3 Object Created trigger are all intact. Only the three FEAT-002 edits were made.
