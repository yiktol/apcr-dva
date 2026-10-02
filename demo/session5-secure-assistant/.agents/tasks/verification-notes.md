# Verification notes — Session 5 Secure Assistant (first iteration)

No `code-review.json` existed at start, so this was a first-from-scratch
implementation per `plan.md` / `design.md`. All verification is LOCAL ONLY — no
`cdk deploy`, `cdk bootstrap`, `docker build`/`push`, live `aws` calls, or
Bedrock/Guardrail invocation at any point.

## Environment
- node v25.6.1, npm, Python 3.13.3, rsvg-convert present.
- aws-cdk-lib pinned to exactly 2.160.0 (confirmed in infra/package.json).

## Commands run and results

1. `cd infra && npm install` → added 27 packages, OK.
2. `cd infra && npx tsc --noEmit` → clean (no errors). Fixed one issue found en
   route: the Bedrock interface-endpoint policy was built via
   `PolicyDocument.statements` (private); switched to a standalone
   `iam.PolicyStatement`.
3. `cd infra && CDK_DEFAULT_ACCOUNT=875692608981 JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1 npx cdk synth --all`
   → both stacks (SecureAssistantSecurityData, SecureAssistantAppEdgeAI)
   synthesize successfully. Only expected warnings from
   `fromVpcAttributes` subnets (no routeTableId) — no errors. The assistant
   `DockerImageFunction` is only STAGED at synth (image-asset manifest), no
   `docker build` runs.
4. Synthesized-template spot checks (grep against cdk.out):
   - `AWS::EC2::VPC` count = 0 in BOTH templates (VPC imported, never created).
   - `AWS::Bedrock::ModelInvocationLoggingConfiguration` present (raw CfnResource
     escape hatch — the class does not exist in aws-cdk-lib@2.160.0; verified by
     enumerating the aws-bedrock Cfn* exports).
   - `AWS::Bedrock::Guardrail` + `AWS::Bedrock::GuardrailVersion` present.
   - Literal `${aws:PrincipalTag/team}` present verbatim in the AppEdgeAI
     template (ABAC not collapsed by a template literal).
   - `PackageType: Image` present (assistant container Lambda).
   - `AWS::WAFv2::WebACL` present (regional).
5. `cd infra && npm test` (ts-node Template.fromStack assertions) → all 20
   assertions passed:
   no VPC (both stacks); KMS CMK w/ rotation; 2 DynamoDB tables CMK-encrypted;
   Guardrail (Hate+Violence HIGH, PII mask US_BANK_ACCOUNT_NUMBER/
   US_SOCIAL_SECURITY_NUMBER/EMAIL, BLOCK topic legal-advice) + published
   version; raw invocation-logging config on CMK destinations; CMK log group;
   CloudFront w/ no ACM cert + /api/* behavior + OAC; regional WebACL w/ common
   rule set + COUNT rate rule; WebACL association; API GW stage TracingEnabled;
   receipts TLS-only DENY; assistant image Lambda in VPC w/ Active tracing; two
   Bedrock interface endpoints; dual-ARN Bedrock grant (inference-profile +
   foundation-model); ABAC literal; >=3 Active-traced Lambdas.
6. `python3 -m py_compile $(find app -name '*.py')` → clean.
7. `python3 -m pytest app/tests -q` → 16 passed (pii masking/validation;
   initiate_refund PENDING + token written + no money + no raw PII in item/logs;
   refund-confirm happy/idempotent/expired/unknown/bad-token; presign URL gen +
   bad-orderId reject). Strands imports are guarded so tests run without strands
   installed.
8. `cd diagram && python3 build_diagram.py && rsvg-convert -o architecture.png architecture.svg`
   → architecture.svg (87282 bytes) + architecture.png (239396 bytes) produced;
   icons embedded as base64 (grep for external hrefs = 0).
9. `bash -n deploy.sh && bash -n destroy.sh` → both pass. destroy.sh aborts
   unless the operator types `destroy`.

## Notes / deviations
- PII entity for a bank account number: the design text said `ACCOUNT_NUMBER`,
  but the valid Bedrock PII entity (per aws-cdk-lib@2.160.0 CfnGuardrail docs)
  is `US_BANK_ACCOUNT_NUMBER`. Used the valid entity so the guardrail config is
  deployable. SSN=`US_SOCIAL_SECURITY_NUMBER`, email=`EMAIL`. PII action is
  `ANONYMIZE` (the Bedrock MASK-equivalent action; `MASK` is not a valid
  CfnGuardrail PII action value).
- session4-coffee-ship git diff is EMPTY (not modified).
