# Secure Coffee-Shop AI Assistant — Session 5 implementation review

The first-iteration implementation builds the two-stack CDK app, the three
Python Lambdas, the Strands agent wiring, the chat SPA, the diagram generator,
the deploy/destroy scripts, and the docs exactly as the approved design and plan
describe. Every one of the 25 acceptance criteria maps to a concrete artifact in
the tree, and the security controls the gate enumerates are all present and
wired correctly: WAF (common rule set + COUNT rate rule, regional, associated),
CloudFront+OAC with no ACM cert, KMS CMK on receipts/log destinations/both
tables, S3 TLS-only DENY, the ABAC `ResourceTag==PrincipalTag` statement, the
two Bedrock interface endpoints with a non-wildcard policy, the Guardrail +
published version, dual-ARN Bedrock grants, model-invocation logging to
CMK-encrypted destinations, X-Ray on API GW + Lambdas, Secrets Manager + SSM,
the imported VPC (no `AWS::EC2::VPC`), the Lambda in private subnets, the Strands
model wired to the apac inference profile with the guardrail id/version, the
human-in-the-loop pending-confirmation refund, and the tool-handler PII masking.

Verification evidence is complete (verification-notes.md records `tsc`, `cdk
synth --all`, the Template.fromStack assertions, `py_compile`, `pytest` 16
passed, the diagram build, and `bash -n`), all local-only, with the session4
diff confirmed empty. Two documented deviations (PII entity/action naming) are
driven by what `aws-cdk-lib@2.160.0` actually accepts and preserve the required
behavior.

Watch for: the X-Ray DynamoDB subsegment is produced implicitly by `patch_all()`
rather than an explicit named `ddb-*` subsegment the plan sketched (likely,
non-blocking); the guardrail PII action is `ANONYMIZE` and the entity is
`US_BANK_ACCOUNT_NUMBER` rather than the design's literal `MASK` /
`ACCOUNT_NUMBER` (confirmed, correct — those literals are invalid in this CDK
version).

**Verdict**: APPROVED

## High-level view

The stack split matches the design: `SecureAssistantSecurityData` owns the CMK,
both DynamoDB tables, the payment secret, the SSM config, the Guardrail +
version, and the invocation-logging singleton; `SecureAssistantAppEdgeAI` owns
the edge/compute/observability layer and receives everything else through typed
props. Cross-stack wiring is by props, not hardcoding.

Network and data security is intact. CloudFront serves a private SPA bucket via
OAC and routes `/api/*` to the API Gateway origin with no ACM certificate; the
regional WAF carries the AWS common rule set plus a rate-based rule explicitly in
COUNT mode and is associated to the API stage. The receipts bucket is
CMK-encrypted with a TLS-only DENY resource policy, paired with the presign
role's scoped `s3:GetObject` identity policy — the identity-vs-resource pairing
the design calls for.

Identity and access follow least privilege. The agent role grants InvokeModel /
InvokeModelWithResponseStream on both the inference-profile ARN and the
foundation-model ARN form, with ApplyGuardrail scoped to the guardrail ARN as a
documented defensive grant. The ABAC statement on the refund role compares
`aws:ResourceTag/team` to the literal `${aws:PrincipalTag/team}` (kept as a
single-quoted string so the IAM variable survives rendering), and both the role
and the pending-refunds table are tagged `team=support`.

The Strands assistant is wired correctly: `BedrockModel(model_id=
"apac.amazon.nova-micro-v1:0", region_name="ap-southeast-1", guardrail_id,
guardrail_version, guardrail_trace="enabled")`, no classic Agent or AgentCore,
reaching Bedrock only through the private-subnet interface endpoints. The
human-in-the-loop refund writes a PENDING record keyed by a server-generated
uuid4 token and moves no money; a separate confirm endpoint is the only executor
and is idempotent. The tool handlers mask/validate PII themselves because the
guardrail does not see tool-call arguments — the blind-spot mitigation.

Observability is present: X-Ray enabled on the API stage and all three Lambdas,
with `patch_all()` instrumenting boto3 and an explicit `bedrock-invoke`
subsegment around the model call. The invocation-logging config is provisioned
via an escape-hatch raw CfnResource (the typed class does not exist in this CDK
version) with both destinations CMK-encrypted.

The known gaps are small: the DynamoDB X-Ray subsegment relies on `patch_all()`
auto-instrumentation rather than an explicit named subsegment, and the two
guardrail-config naming deviations are forced by the CDK version. Neither blocks
the gate.

<details>
<summary>Issues (3)</summary>

1. **DynamoDB subsegment is implicit** — the handler wraps the model call in an
   explicit `bedrock-invoke` subsegment but relies on `patch_all()` to produce
   the DynamoDB subsegment rather than an explicit `ddb-*` subsegment the plan
   sketched. `patch_all()` does instrument boto3/DynamoDB, so acceptance #28 is
   satisfied; optionally add an explicit named subsegment for clarity.
   (likely, non-blocking)
2. **Guardrail PII action/entity renamed** — design said `ACCOUNT_NUMBER` with
   action `MASK`; implementation uses `US_BANK_ACCOUNT_NUMBER` with `ANONYMIZE`.
   These are the valid values in `aws-cdk-lib@2.160.0`; the required
   mask-PII-on-the-model-channel behavior is preserved. No action needed; keep
   the note in the deviation log. (confirmed, correct)
3. **ApplyGuardrail grant may be unused at runtime** — included defensively on
   both the endpoint policy and the agent role, scoped to the guardrail ARN. The
   inline-guardrail path may not issue a separate call. Documented in code; no
   action needed. (confirmed, intentional)

</details>

<details>
<summary>Details</summary>

### Gate control checklist (all confirmed present and correct)

Read against the synthesized-template evidence in verification-notes.md and the
source in `infra/lib/`:

- WAF WebACL `scope: REGIONAL` with `AWSManagedRulesCommonRuleSet`
  (`overrideAction: { none: {} }`) and a rate-based rule `action: { count: {} }`,
  `limit: 2000`, `aggregateKeyType: 'IP'`, plus a `CfnWebACLAssociation` to the
  API stage ARN. (app-edge-ai-stack.ts, asserted in template.test.ts)
- CloudFront `Distribution` with `S3BucketOrigin.withOriginAccessControl` default
  behavior and a `/api/*` `RestApiOrigin` behavior; no ACM certificate, no alias.
  (OAC resource count asserted = 1, certificate count = 0)
- KMS CMK (`enableKeyRotation: true`) encrypting the receipts bucket
  (`BucketEncryption.KMS`), both DynamoDB tables (`CUSTOMER_MANAGED` +
  `encryptionKey`), the CloudWatch invocation log group (`encryptionKey`), and
  the S3 invocation-log bucket.
- Receipts bucket `DenyInsecureTransport` statement: `Deny s3:*` for
  `AnyPrincipal` when `aws:SecureTransport = false`.
- ABAC statement: `StringEquals { 'aws:ResourceTag/team':
  '${aws:PrincipalTag/team}' }` on the refund role's `dynamodb:GetItem/UpdateItem`
  on the pending-refunds ARN; literal verified verbatim in the rendered template.
- Two `InterfaceVpcEndpoint`s (`BEDROCK_RUNTIME` + `BEDROCK`) in the three private
  subnets, `privateDnsEnabled`, a shared non-wildcard endpoint policy on the three
  Bedrock actions over the two Nova ARNs + guardrail ARN, and an endpoint SG
  admitting only `assistantSg` on 443.
- `CfnGuardrail` (HATE + VIOLENCE at HIGH input/output; PII entities set to the
  masking/anonymize action; DENY topic `legal-advice` as the BLOCK example) +
  `CfnGuardrailVersion`.
- Agent role grants `bedrock:InvokeModel` + `InvokeModelWithResponseStream` on
  BOTH `.../inference-profile/apac.amazon.nova-micro-v1:0` and
  `arn:aws:bedrock:*::foundation-model/amazon.nova-micro-v1:0`; scoped DynamoDB
  RW, Secrets read, SSM read, X-Ray write.
- `AWS::Bedrock::ModelInvocationLoggingConfiguration` (raw escape-hatch
  CfnResource) delivering to the CMK-encrypted CloudWatch log group + S3 bucket.
- API GW stage `tracingEnabled: true`; all three Lambdas `tracing: ACTIVE`
  (asserted `>= 3` Active-traced functions).
- Secrets Manager `session5/payment-processor-key` + SSM
  `/session5/assistant/config`; agent role scoped read on both.
- VPC imported via `fromVpcAttributes` with the six subnet ids and three AZs in
  order; `AWS::EC2::VPC` count = 0 in both templates.
- Assistant `DockerImageFunction` in the three private subnets with `assistantSg`.

### Strands wiring and the refund state machine

`handler.py` constructs `BedrockModel` with the apac inference-profile id as
`model_id`, pins the region, and forwards the guardrail kwargs — matching FR-19
and acceptance #16, with no classic Agent/AgentCore import. The guarded imports
let `py_compile`/`pytest` run without strands installed while the live container
path stays intact.

The refund flow is the design's human-in-the-loop contract. `initiate_refund`
validates and masks arguments, writes a `PENDING_CONFIRMATION` item keyed by a
fresh uuid4 with a TTL, appends `{token, amountMasked, orderMasked}` to the
request-scoped side channel, and returns a model-facing PENDING result — moving
no money. The `/api/chat` handler builds the HTTP envelope's `pendingRefund` from
that side channel, not from model text, closing the token-paraphrase gap. The
separate `refund_confirm` handler is the only executor: it validates the token
format, runs a conditional update that flips `PENDING_CONFIRMATION → CONFIRMED`
only once (409/410/404 for the other states, idempotent 200 on repeat), reads the
payment secret to exercise the grant, and stubs the processor call.

### PII masking as the tool-call blind-spot defense

`pii.py` is pure and documents the blind spot: the guardrail sees prompt and
completion only, never tool arguments or results, so the handlers mask
themselves. `tools.py` routes every argument through the masker before writing to
DynamoDB, and `test_tools.py` asserts a raw account number appears neither in the
written item nor in captured logs (acceptance #19). The guardrail PII config is
the second, model-channel layer, and the CMK on the log destination is the third
— matching the design's priority order.

### Deviations and their justification

The guardrail uses `US_BANK_ACCOUNT_NUMBER` / `ANONYMIZE` instead of the design's
`ACCOUNT_NUMBER` / `MASK`. `aws-cdk-lib@2.160.0`'s `CfnGuardrail` enum validation
rejects the design literals; the chosen values are the deployable equivalents
that preserve FR-21's intent (mask PII on the model channel). The invocation
logging uses a raw `CfnResource` because no typed construct exists at the pinned
version — the design anticipated this (Finding 1). Both deviations are recorded
in verification-notes.md.

### Verification evidence (not re-run, per the gate boundary)

verification-notes.md records the full local gate: `npm install`, `tsc --noEmit`
clean, `cdk synth --all` (both stacks, image asset staged only — no docker
build), the Template.fromStack assertions (20 passed), `py_compile` clean,
`pytest` (16 passed), the diagram build (svg+png, base64-embedded icons), and
`bash -n` on both scripts with the typed-`destroy` guard confirmed. No `cdk
deploy`, `bootstrap`, `docker push`, live `aws`, or Bedrock runtime calls — the
local-only boundary and acceptance #25 hold. `destroy.sh` removes the
invocation-logging singleton before the stack delete so the CMK is unpinned, and
the session4 diff is empty (acceptance #1).

</details>

<details>
<summary>File map</summary>

- `infra/lib/security-data-stack.ts` — CMK, two CMK-encrypted tables, payment
  secret, SSM config, Guardrail + version, CMK-encrypted invocation-logging.
- `infra/lib/app-edge-ai-stack.ts` — imported VPC, SGs, two Bedrock endpoints
  with non-wildcard policy, receipts/SPA buckets + TLS-only DENY, three Lambdas,
  dual-ARN + ABAC + identity/resource IAM, API GW (X-Ray), regional WAF +
  association, CloudFront OAC + `/api/*`, SPA deploy.
- `infra/lib/vpc-import.ts` — `fromVpcAttributes` import; no VPC created.
- `infra/test/template.test.ts` — Template.fromStack assertions for every control.
- `app/assistant/{handler,tools,pii}.py` — Strands agent, @tool handlers,
  pure PII helpers; side-channel refund token, blind-spot masking.
- `app/refund_confirm/handler.py` — idempotent confirm state machine (sole
  executor); secret read + stubbed processor.
- `app/presign/handler.py` — 15-min presigned GET URL, injectable generator.
- `app/{requirements.txt,Dockerfile}` — pinned deps; image built at deploy only.
- `app/tests/*` — pii/tools/refund/presign unit tests.
- `spa/{index.html,app.js,styles.css}` — chat UI, confirm button, receipt
  download; token treated as opaque.
- `diagram/build_diagram.py` — base64 icon-embed SVG + PNG generator.
- `deploy.sh` / `destroy.sh` — pinned region, numbered steps, typed-`destroy`
  guard, singleton teardown ordering.
- `README.md` / `FACILITATOR-RUNBOOK.md` — four acts, seven callouts, WAF
  tradeoff, OLX/Clariant talking points.

Full diff: `git -C /Users/erictole/demo/apcr-dva/.worktrees/session5 diff`
(new files under `demo/session5-secure-assistant/`).

</details>
