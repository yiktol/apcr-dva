# Verification — Session 5 Secure Assistant (final local-only record)

Scope: the approved Session 5 "Secure Coffee-Shop AI Assistant" demo in
`demo/session5-secure-assistant` on branch `session5-secure-assistant`
(worktree `/Users/erictole/demo/apcr-dva/.worktrees/session5`).

**LOCAL-ONLY. NO live AWS resources were created.** No `cdk deploy`, no
`cdk bootstrap`, no `docker build`/`docker push`, no `aws` API calls, and no
Bedrock / Guardrail invocation were run at any point. Everything below is `cdk
synth` (offline template generation), TypeScript/Python compile, unit tests,
and static inspection of the synthesized CloudFormation templates in
`infra/cdk.out/` (a local directory, git-ignored).

## Environment
- node v25.6.1, npm, Python 3.13.3, pytest 8.3.2, rsvg-convert present.
- `aws-cdk-lib` pinned to exactly `2.160.0` (confirmed in `infra/package.json`).

## Commands run and results

| # | Command (cwd) | Result |
|---|---------------|--------|
| 1 | `npm install` (infra) | OK — dependencies installed, no errors. |
| 2 | `npx tsc --noEmit` (infra) | **Clean** — exit 0, no type errors. |
| 3 | `CDK_DEFAULT_ACCOUNT=875692608981 JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1 npx cdk synth --all` (infra) | **PASS** — both stacks synthesize. Only CDK CLI telemetry/version notices (no errors). Produced `SecureAssistantSecurityData.template.json` + `SecureAssistantAppEdgeAI.template.json`. The assistant `DockerImageFunction` is only STAGED (image-asset manifest); no `docker build` runs at synth. |
| 4 | `npm test` (infra; ts-node `Template.fromStack` assertions) | **PASS** — all 20 assertions passed. |
| 5 | `python3 -m py_compile` on all `app/**/*.py` (sources + tests) | **Clean**. |
| 6 | `python3 -m pytest app/tests -q` | **PASS** — 16 passed (strands imports guarded; run without strands installed). |
| 7 | `python3 build_diagram.py` + `rsvg-convert -o architecture.png architecture.svg` (diagram) | **PASS** — `architecture.svg` (87,282 bytes) + `architecture.png` (239,396 bytes) produced; 16 real icons embedded as `data:image/svg+xml;base64`; external `href="http"`/`href="file"` count = 0. |
| 8 | `bash -n deploy.sh` / `bash -n destroy.sh` | **PASS** — both parse clean. |

No check failed, so no fixes were required.

## Synthesized-template inspection (static)

Each required element was confirmed by inspecting the JSON templates in
`infra/cdk.out/`. Stack key: **SD** = `SecureAssistantSecurityData`,
**AE** = `SecureAssistantAppEdgeAI`.

| Required element | Where | Result |
|------------------|-------|--------|
| WAF WebACL + managed rule group + rate-based rule (COUNT mode) | AE | **PRESENT** — 1 `AWS::WAFv2::WebACL`, Scope `REGIONAL`. Rule `AWSManagedRulesCommonRuleSet` (ManagedRuleGroupStatement, override None); rule `RateLimit` (RateBasedStatement, limit 2000, aggregateKey IP) with `Action: { Count: {} }` → COUNT mode. |
| WebACL association | AE | **PRESENT** — 1 `AWS::WAFv2::WebACLAssociation` to the regional API GW stage ARN. |
| CloudFront + OAC | AE | **PRESENT** — 1 `AWS::CloudFront::Distribution`, 1 `AWS::CloudFront::OriginAccessControl`. `/api/*` cache behavior present; `ViewerCertificate` is the default (no ACM cert / custom domain). |
| KMS CMK on receipts bucket + log destination | SD + AE | **PRESENT** — 1 `AWS::KMS::Key` (SD) with `EnableKeyRotation: true`. Receipts bucket (AE) `SSEAlgorithm: aws:kms` using the imported CMK ARN. Bedrock invocation log group (SD) has `KmsKeyId`; invocation-log S3 bucket (SD) is `aws:kms`. |
| S3 bucket policy denying non-TLS | AE | **PRESENT** — receipts bucket (and SPA bucket) have a `Deny` statement conditioned on `aws:SecureTransport = false`. |
| ABAC policy (ResourceTag + PrincipalTag) | AE | **PRESENT** — refund-confirm role policy carries `aws:ResourceTag/team` StringEquals `${aws:PrincipalTag/team}`; the literal `${aws:PrincipalTag/team}` survives verbatim into the rendered template (not collapsed by a JS template literal). |
| bedrock-runtime interface VPC endpoint + endpoint policy | AE | **PRESENT** — 2 `AWS::EC2::VPCEndpoint` (Interface, `PrivateDnsEnabled: true`): bedrock-runtime + bedrock control-plane. Each has a non-wildcard `PolicyDocument` scoped to the three Bedrock actions on the inference-profile ARN, foundation-model ARN, and guardrail ARN. |
| Bedrock Guardrail (content + PII filters) + version | SD | **PRESENT** — 1 `AWS::Bedrock::Guardrail`: content filters `HATE` + `VIOLENCE`; PII entities `US_BANK_ACCOUNT_NUMBER` / `US_SOCIAL_SECURITY_NUMBER` / `EMAIL` (action `ANONYMIZE`); DENY topic `legal-advice`. 1 `AWS::Bedrock::GuardrailVersion` referencing the guardrail → published version. |
| Assistant role IAM allowing invoke on BOTH ARNs | AE | **PRESENT** — `AssistantFnServiceRoleDefaultPolicy` grants `bedrock:InvokeModel` + `...WithResponseStream` on BOTH `inference-profile/apac.amazon.nova-micro-v1:0` AND `*::foundation-model/amazon.nova-micro-v1:0`. |
| Model invocation logging to a KMS-encrypted destination | SD | **PRESENT** — `AWS::Bedrock::ModelInvocationLoggingConfiguration` (raw CfnResource escape hatch; no L1/L2 in aws-cdk-lib@2.160.0) delivering to the CMK-encrypted CloudWatch log group + CMK-encrypted S3 bucket. |
| X-Ray on API GW + Lambda | AE | **PRESENT** — API GW stage `TracingEnabled: true`; `AssistantFn`, `RefundConfirmFn`, `PresignFn` all `TracingConfig.Mode: Active`. |
| Secrets Manager + SSM | SD | **PRESENT** — `AWS::SecretsManager::Secret` `session5/payment-processor-key`; `AWS::SSM::Parameter` `/session5/assistant/config`. |
| VPC imported (NO `AWS::EC2::VPC` created) | SD + AE | **CONFIRMED** — `AWS::EC2::VPC` count = 0 in BOTH templates. VPC comes from `ec2.Vpc.fromVpcAttributes` (no `fromLookup`, no context lookup). |
| Assistant Lambda in private subnets | AE | **PRESENT** — `AssistantFn` is `PackageType: Image`, has a `VpcConfig`, placed in the three explicitly-imported private subnets. |
| Strands `model_id` = APAC inference profile; guardrail id/version passed to `BedrockModel` | `app/assistant/handler.py` | **CONFIRMED** — `_build_agent` sets `model_id = NOVA_MODEL_ID` env (default `apac.amazon.nova-micro-v1:0`), `region_name = ap-southeast-1`, and forwards `guardrail_id` / `guardrail_version` / `guardrail_trace="enabled"` to `BedrockModel`. The `NOVA_MODEL_ID`, `GUARDRAIL_ID`, `GUARDRAIL_VERSION` env vars are wired on `AssistantFn` in the AE template. |

## Behavior confirmations

- **Human-in-the-loop pending-confirmation refund flow** — CONFIRMED.
  `tools.make_initiate_refund` writes a `PENDING_CONFIRMATION` DynamoDB item
  with a uuid4 token + TTL and moves no money (test: item has no `paid`/
  `settled` field; bad order id / amount ≤ 0 / amount > max are REJECTED and
  nothing is written). The separate `refund_confirm.confirm_refund` state
  machine is the ONLY executor: 400 bad-token-format, 404 unknown, 410 expired,
  409 not-pending, 200 confirm, and idempotent 200 (no second update) on an
  already-CONFIRMED token. All six paths covered by passing unit tests.
- **Tool-handler PII masking** — CONFIRMED. `pii.mask_pii` masks account
  numbers / SSNs / emails keeping only last-4; `initiate_refund` routes
  order/amount through the masker before persisting, and a test asserts a raw
  12-digit account value never appears in the written item nor in captured log
  output. The guardrail tool-call blind spot is handled in-handler by design.

## Notes / deviations (carried from implementation)
- PII entity for a bank account is `US_BANK_ACCOUNT_NUMBER` (the valid Bedrock
  entity; there is no generic `ACCOUNT_NUMBER`). SSN = `US_SOCIAL_SECURITY_NUMBER`,
  email = `EMAIL`. PII action is `ANONYMIZE` (the valid CfnGuardrail
  mask-equivalent action; `MASK` is not a valid value).
- `AWS::Bedrock::ModelInvocationLoggingConfiguration` has no L1/L2 construct in
  aws-cdk-lib@2.160.0, so it is provisioned via a raw `CfnResource` escape hatch.

## No-live-resources statement
All verification was performed locally. `cdk synth` only generates
CloudFormation templates into the local, git-ignored `infra/cdk.out/`
directory; it does not call AWS. **No AWS account was mutated and no AWS
resources were created, deployed, or invoked.**
