# Implementation Plan — Guardrail expansion + receipt-download tool

Two independent features in the CDK v2 (TS) + Python-3.12 demo at
`/home/ubuntu/apcr-dva/demo/session5-secure-assistant`. Task 1 is pure infra
(TypeScript, no deploy needed to verify). Task 2 touches Python Lambda code,
IAM/env (TS), the SPA, and tests, and REQUIRES an out-of-band ECR image
rebuild+push before the AppEdgeAI deploy. The two tasks do not depend on each
other and may be done in either order; this plan lists Task 1 first.

## Baseline facts (verified during exploration)

- Installed `aws-cdk-lib` is **2.160.0**. `CfnGuardrail` nested types live in the
  `CfnGuardrail` namespace in
  `infra/node_modules/aws-cdk-lib/aws-bedrock/lib/bedrock.generated.d.ts`.
- Supported guardrail sub-configs in this version:
  `contentPolicyConfig.filtersConfig` (ContentFilterConfigProperty =
  `{type, inputStrength, outputStrength}` ONLY — no per-filter modality/toggle
  fields), `wordPolicyConfig.{managedWordListsConfig,wordsConfig}`,
  `sensitiveInformationPolicyConfig.{piiEntitiesConfig,regexesConfig}`,
  `topicPolicyConfig.topicsConfig`, and
  `contextualGroundingPolicyConfig.filtersConfig`
  (ContextualGroundingFilterConfigProperty = `{type, threshold}`).
- **NOT supported in 2.160.0:** `contentPolicyConfig.tierConfig` — the
  `ContentPolicyConfigProperty` interface has ONLY `filtersConfig`. **Skip
  tierConfig and record this in verification.md.** `contextualGroundingPolicyConfig`
  **IS** supported — include it.
- Baseline test state: `python3 -m pytest app/tests -q` → **45 passed**.
  `cd infra && npm test` → all assertions pass EXCEPT the one pre-existing,
  out-of-scope failure: `raw Bedrock invocation-logging config on CMK-encrypted
  destinations` (asserts `AWS::Bedrock::ModelInvocationLoggingConfiguration`,
  which is provisioned via an AwsCustomResource, not a CFN resource). **Do NOT
  fix that test.** No other test may break.
- The existing Guardrail template assertion uses `Match.arrayWith` /
  `Match.objectLike`, so additive expansion (keeping HATE/VIOLENCE HIGH, the 3
  PII entities, and the legal-advice DENY topic) will NOT break it.
- The assistant Lambda is a **container image** (ECR repo
  `session5-secure-assistant`, tag `:latest`) built+pushed out-of-band by
  `deploy.sh` step 3b — `cdk deploy` does NOT rebuild it. Any `app/assistant/*.py`
  change requires rebuild+push before/with the AppEdgeAI deploy.
- `app/presign/handler.py` already has the reusable pieces: `ORDER_ID_RE`,
  `EXPIRES_IN = 900`, `generate_url(s3_client, bucket, order_id, expires_in)`,
  and a documented SigV4 + regional-endpoint `boto3.client("s3", ...)`
  construction inside `handler()`. The SigV4 client construction is currently
  INLINE in `handler()`, not yet a shared function.
- Side-channel pattern: `req_ctx` dict in `app/assistant/handler.py` carries
  `pending_refunds` and `placed_orders`; `build_response()` reads the authoritative
  record from `req_ctx` (never from model text) and emits `pendingRefund` /
  `placedOrder` envelope objects. The SPA (`spa/app.js`) renders those.
- SPA CSS classes present: `.msg`, `.bot`, `.user`, `.sys`, `.pending`, `.log`.
- Assistant Lambda env today (in `app-edge-ai-stack.ts`) does NOT include
  `RECEIPTS_BUCKET`; the assistant role has `kmsKey.grantEncryptDecrypt` (so
  kms:Decrypt is already present) and DynamoDB RW, but NOT `s3:GetObject` on the
  receipts bucket. The presign role has `s3:GetObject` on `receipts/*` +
  `kmsKey.grantDecrypt`.

## Task-2 design decision (front-loaded): OPTION A

**Chosen: Option A** — a new local Strands `@tool get_receipt_url(order_id)` that
generates the presigned URL in-process via a SHARED signing helper. Rejected
Option B (assistant calls back through API Gateway/CloudFront+WAF to the presign
Lambda) because B adds a network round-trip from inside the VPC out through the
edge, needs egress/WAF allowances, couples the assistant to the public HTTP path,
and widens the blast radius for no benefit. Option A keeps signing in-process,
reuses the exact 15-minute SigV4 regional presign logic, and needs only a narrow
IAM read grant — least blast radius, best security. The shared helper guarantees
ONE copy of the signing code used by both the presign Lambda and the new tool.

---

## TASK 1 — Expand the Bedrock Guardrail

- [ ] 1. Expand the `AssistantGuardrail` `CfnGuardrail` in
      `/home/ubuntu/apcr-dva/demo/session5-secure-assistant/infra/lib/security-data-stack.ts`
      to exercise the full feature surface supported by aws-cdk-lib 2.160.0.
      Keep the published `CfnGuardrailVersion` wiring and the `guardrailId` /
      `guardrailVersion` public readonly contract UNCHANGED. Apply exactly:
      - `contentPolicyConfig.filtersConfig`: HATE, VIOLENCE, INSULTS, MISCONDUCT,
        SEXUAL each `inputStrength: 'HIGH', outputStrength: 'HIGH'`; plus
        PROMPT_ATTACK `inputStrength: 'HIGH', outputStrength: 'NONE'` (Bedrock
        rule: PROMPT_ATTACK is input-only). Do NOT add `tierConfig` (absent from
        the installed `ContentPolicyConfigProperty`).
      - `wordPolicyConfig`: `managedWordListsConfig: [{ type: 'PROFANITY' }]`
        and `wordsConfig: [{ text: 'competitorcafe' }, { text: 'freecoffeehack' }, { text: 'voucherabuse' }]`.
      - `sensitiveInformationPolicyConfig.piiEntitiesConfig`: keep the existing
        3 (US_BANK_ACCOUNT_NUMBER, US_SOCIAL_SECURITY_NUMBER, EMAIL — EMAIL stays
        ANONYMIZE). Add BLOCK for CREDIT_DEBIT_CARD_NUMBER, CREDIT_DEBIT_CARD_CVV,
        PIN, PASSWORD, AWS_ACCESS_KEY, AWS_SECRET_KEY; add ANONYMIZE for
        CREDIT_DEBIT_CARD_EXPIRY, PHONE, ADDRESS, NAME, US_BANK_ROUTING_NUMBER,
        AGE, USERNAME. (All identifiers verified present in the installed
        PiiEntityConfig docs/enum.)
      - `sensitiveInformationPolicyConfig.regexesConfig`:
        `[{ name: 'loyalty-card', description: 'Demo loyalty-card id', pattern: 'LOYALTY-[0-9]{8}', action: 'ANONYMIZE' }]`.
      - `topicPolicyConfig.topicsConfig`: keep legal-advice (DENY); add
        'medical-advice' and 'financial-investment-advice' DENY topics, each with
        a definition and 2 examples.
      - `contextualGroundingPolicyConfig.filtersConfig`:
        `[{ type: 'GROUNDING', threshold: 0.7 }, { type: 'RELEVANCE', threshold: 0.7 }]`.
      - Optionally refine `blockedInputMessaging` / `blockedOutputsMessaging`
        wording; keep them non-empty.
      Files: `infra/lib/security-data-stack.ts`
      Verify: `cd infra && npx tsc --noEmit` compiles clean (invalid property
      keys fail here); then
      `CDK_DEFAULT_ACCOUNT=875692608981 JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1 npx cdk synth SecureAssistantSecurityData`
      synthesizes without error and the emitted
      `AWS::Bedrock::Guardrail` shows all six content filters, the word policy,
      the expanded PII + regex, three topics, and the contextual-grounding block.

- [ ] 2. Extend the Guardrail assertions in
      `/home/ubuntu/apcr-dva/demo/session5-secure-assistant/infra/test/template.test.ts`
      (the existing `Bedrock Guardrail ...` check) to additionally assert, via
      `Match.arrayWith`/`Match.objectLike`: PROMPT_ATTACK with
      `OutputStrength: 'NONE'`; a WordPolicyConfig with the PROFANITY managed
      list; at least one BLOCK PII entity (e.g. CREDIT_DEBIT_CARD_NUMBER); the
      RegexesConfig loyalty pattern; the medical-advice DENY topic; and the
      ContextualGroundingPolicyConfig GROUNDING filter. Do NOT touch the
      pre-existing failing `raw Bedrock invocation-logging config` check.
      Files: `infra/test/template.test.ts`
      Verify: `cd infra && npm test` — all assertions pass EXCEPT the single
      known-failing `raw Bedrock invocation-logging config` one (unchanged
      failure count = 1). No other SecurityData assertion regresses.

- [ ] 3. Record Task-1 schema notes in
      `/home/ubuntu/apcr-dva/demo/session5-secure-assistant/.agents/tasks/verification.md`:
      state that `contentPolicyConfig.tierConfig` is NOT present in aws-cdk-lib
      2.160.0 `ContentPolicyConfigProperty` and was intentionally skipped; that
      `contextualGroundingPolicyConfig` IS supported and was included; and that
      the pre-existing `raw Bedrock invocation-logging config` template assertion
      fails on baseline and was deliberately left as-is.
      Files: `.agents/tasks/verification.md`
      Verify: file exists and names tierConfig-skip + the known-failing test.

## TASK 2 — Receipt-download link via S3 presign (Option A)

- [ ] 4. Create a SHARED presign helper so one copy of the SigV4+regional
      signing code serves both the presign Lambda and the new tool. Add
      `make_s3_presign_client(region=None)` to
      `/home/ubuntu/apcr-dva/demo/session5-secure-assistant/app/presign/handler.py`
      that returns the `boto3.client("s3", region_name, endpoint_url,
      config=Config(signature_version="s3v4", s3={"addressing_style":"virtual"}))`
      currently built inline in `handler()`, and refactor `handler()` to call it.
      Keep `generate_url`, `ORDER_ID_RE`, and `EXPIRES_IN` exactly as the single
      source of truth (the tool will import them). Guard the boto3 import exactly
      as the module already does so the module stays importable without boto3.
      Files: `app/presign/handler.py`
      Verify: `python3 -m pytest app/tests/test_presign.py -q` — existing presign
      tests still pass (generate_url behavior unchanged).

- [ ] 5. Add the receipt tool factory to
      `/home/ubuntu/apcr-dva/demo/session5-secure-assistant/app/assistant/tools.py`:
      `make_get_receipt_url(req_ctx, bucket, region=None, orders_table=None)`
      returning a `@tool get_receipt_url(order_id)` that: validates with
      `pii.validate_order_id` (reject → `{"status":"REJECTED","reason":...}` and
      append nothing); optionally `orders_table.get_item` when a table is bound
      (NOT_FOUND if absent); builds the client via the shared
      `presign.handler.make_s3_presign_client(region)` and URL via
      `presign.handler.generate_url(client, bucket, order_id)`; appends
      `{"orderId","url","expiresIn"}` to `req_ctx.setdefault("receipts", [])`;
      returns `{"status":"OK","orderId","url","expiresIn"}`. Import presign
      helpers defensively (so tools.py stays importable without boto3/strands):
      e.g. `from presign.handler import generate_url, make_s3_presign_client,
      EXPIRES_IN` inside the factory or guarded at module top, mirroring the
      existing `try/except` guards. Never read the URL from model text.
      Files: `app/assistant/tools.py`
      Verify: `python3 -m pytest app/tests/test_tools.py -q` passes (after step 7
      adds the new tests).

- [ ] 6. Wire the tool + envelope in
      `/home/ubuntu/apcr-dva/demo/session5-secure-assistant/app/assistant/handler.py`:
      in `_build_agent`, read `os.environ["RECEIPTS_BUCKET"]` and
      `os.environ.get("AWS_REGION_PINNED","ap-southeast-1")`, build
      `get_receipt_url = make_get_receipt_url(req_ctx, bucket, region,
      orders_table)`, and add it to `tools=[...]`. Initialize
      `req_ctx = {"pending_refunds": [], "placed_orders": [], "receipts": []}` in
      `handler()`. Extend `build_response()` to add a top-level `receipt` object
      `{orderId,url,expiresIn}` from `req_ctx["receipts"][-1]` when present (same
      authoritative-side-channel pattern as `pendingRefund`/`placedOrder`).
      Import `make_get_receipt_url` from `.tools`.
      Files: `app/assistant/handler.py`
      Verify: `python3 -m pytest app/tests/test_handler.py -q` passes (extend in
      step 7); `python3 -m py_compile app/assistant/handler.py` clean.

- [ ] 7. Add unit tests (mock boto3/S3 + DynamoDB; no real AWS). Extend
      `/home/ubuntu/apcr-dva/demo/session5-secure-assistant/app/tests/test_tools.py`
      with: valid order id → `status OK`, a url is returned, and
      `req_ctx["receipts"][-1]` is populated with `{orderId,url,expiresIn}`;
      invalid order id → `REJECTED` and `req_ctx["receipts"] == []`. Use a fake
      presign client (like `FakeS3` in test_presign.py) injected via
      monkeypatching `presign.handler.make_s3_presign_client`, or pass a client
      factory the test controls. Add a `build_response` test in
      `/home/ubuntu/apcr-dva/demo/session5-secure-assistant/app/tests/test_handler.py`
      asserting the `receipt` object appears when `req_ctx["receipts"]` is
      non-empty and is absent otherwise. Keep the existing style (strands-free
      import, @tool guarded).
      Files: `app/tests/test_tools.py`, `app/tests/test_handler.py`
      Verify: `python3 -m pytest app/tests -q` — all prior 45 tests still pass
      plus the new ones (count increases).

- [ ] 8. Grant the assistant role receipts read + pass env in
      `/home/ubuntu/apcr-dva/demo/session5-secure-assistant/infra/lib/app-edge-ai-stack.ts`:
      add `RECEIPTS_BUCKET: receiptsBucket.bucketName` to the `AssistantFn`
      `environment` map; add an identity policy statement on `assistantRole`
      granting `s3:GetObject` on `receiptsBucket.arnForObjects('*')` (mirrors the
      presign role). `kms:Decrypt` is already covered by the existing
      `kmsKey.grantEncryptDecrypt(assistantRole)`, so no new KMS grant is needed
      (note this in the code comment). Place the receipts-bucket construct before
      the assistant Lambda if ordering requires it (it is already declared before
      the Lambda section — verify no forward-reference).
      Files: `infra/lib/app-edge-ai-stack.ts`
      Verify: `cd infra && npx tsc --noEmit` clean; `npm test` — AppEdgeAI
      assertions still pass (receipts TLS-deny, dual-ARN, etc. unchanged);
      synth of `SecureAssistantAppEdgeAI` succeeds and the AssistantFn env
      contains `RECEIPTS_BUCKET` and its role has an `s3:GetObject` on the
      receipts objects ARN.

- [ ] 9. Render the receipt link in the SPA. In
      `/home/ubuntu/apcr-dva/demo/session5-secure-assistant/spa/app.js`, after the
      `data.placedOrder` branch in `sendMessage`, add a `data.receipt &&
      data.receipt.url` branch that appends an assistant-styled message
      containing a clickable "Download receipt" anchor
      (`target="_blank" rel="noopener"`, href = `data.receipt.url`), built with
      a `renderReceipt(receipt)` helper mirroring `renderPendingRefund`'s DOM
      construction (use `textContent`/`createElement`, not innerHTML, for the URL
      to avoid injection). Add minimal CSS in
      `/home/ubuntu/apcr-dva/demo/session5-secure-assistant/spa/styles.css`
      reusing existing look (e.g. a `.receipt` block styled like `.pending`, and
      a `.receipt a`/button style consistent with existing buttons). No
      index.html change is required (the link renders into `#log`).
      Files: `spa/app.js`, `spa/styles.css` (and `spa/index.html` only if a new
      static control is wanted — not required).
      Verify: `node --check spa/app.js` parses clean; manual DOM reasoning: a
      response with a `receipt` object yields an anchor with the presigned href
      opening in a new tab. (SPA has no automated test harness in this repo.)

## Verification + deploy sequence (run in order)

- [ ] 10. Local full verification (no AWS):
      `cd /home/ubuntu/apcr-dva/demo/session5-secure-assistant`
      - `python3 -m py_compile $(find app -name '*.py')`
      - `python3 -m pytest app/tests -q` (all pass; count > 45)
      - `node --check spa/app.js`
      - `cd infra && npx tsc --noEmit`
      - `CDK_DEFAULT_ACCOUNT=875692608981 JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1 npx cdk synth --all`
      - `npm test` (only the known `raw Bedrock invocation-logging config`
        assertion fails; nothing else)
      Verify: all commands succeed with the single expected template failure.

- [ ] 11. Deploy. Do NOT modify deploy.sh/destroy.sh; replicate deploy.sh step
      ordering. Region `ap-southeast-1`, account `875692608981`.
      1. `cd infra && CDK_DEFAULT_ACCOUNT=875692608981 CDK_DEFAULT_REGION=ap-southeast-1 npx cdk deploy SecureAssistantSecurityData --require-approval never`
         (publishes a NEW guardrail version — expected).
      2. **Mandatory image rebuild+push (deploy.sh step 3b)** — assistant `.py`
         changed, so the ECR `:latest` image MUST be rebuilt before the AppEdgeAI
         deploy:
         ```
         ACCOUNT_ID=875692608981; AWS_REGION=ap-southeast-1
         REPO=session5-secure-assistant
         URI=${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${REPO}
         aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
         BUILDX_NO_DEFAULT_ATTESTATIONS=1 docker buildx build --platform linux/amd64 --provenance=false --sbom=false -t ${URI}:latest --push ./app
         ```
      3. `cd infra && CDK_DEFAULT_ACCOUNT=875692608981 CDK_DEFAULT_REGION=ap-southeast-1 npx cdk deploy SecureAssistantAppEdgeAI --require-approval never`
      4. Force the AssistantFn to pick up the new image if the ECR digest didn't
         change the CFN resource:
         `aws lambda update-function-code --function-name <AssistantFn physical name> --image-uri ${URI}:latest --region ap-southeast-1`
         (resolve the physical name via
         `aws cloudformation describe-stack-resources --stack-name SecureAssistantAppEdgeAI --query "StackResources[?ResourceType=='AWS::Lambda::Function' && contains(LogicalResourceId,'AssistantFn')].PhysicalResourceId" --output text`).
      Verify: both stacks deploy; a new `AWS::Bedrock::GuardrailVersion` exists;
      the AssistantFn env shows `RECEIPTS_BUCKET`.

- [ ] 12. Live smoke (optional, demo creds active): seed data already present
      (`ORD-000123` + `receipts/ORD-000123.pdf` from deploy.sh step 5). Open the
      SPA custom domain, ask "can I get my receipt for ORD-000123?", confirm a
      "Download receipt" link renders and the presigned URL downloads the PDF;
      ask for an invalid id and confirm no link renders. Do NOT change custom
      domain / ACM / Route53 / WAF / PrivateLink / region pinning.

## Do-NOT list (guardrails for the implementer)

- Do not add `contentPolicyConfig.tierConfig` (unsupported in 2.160.0).
- Do not fix the pre-existing `raw Bedrock invocation-logging config` test.
- Do not change the `guardrailId`/`guardrailVersion` cross-stack contract.
- Do not fork the presign signing code — both callers use the one shared helper.
- Do not read receipt URLs/tokens from model output; use the `req_ctx` side
  channel only.
- Do not weaken the presign model (15-min SigV4 regional GET,
  `receipts/{orderId}.pdf` only, order-id validated, private bucket).
- Do not modify deploy.sh/destroy.sh; do not run destroy; do not touch custom
  domain/ACM/Route53/CloudFront-WAF/API-GW-WAF/PrivateLink/region pinning.
- Rebuilding+pushing the ECR image is MANDATORY before the AppEdgeAI deploy
  whenever `app/assistant/*.py` changes.
