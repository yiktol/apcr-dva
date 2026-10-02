# Implementation Plan — Session 5: Secure Coffee-Shop AI Assistant

Implements the approved design at `.agents/tasks/design.md` (requirements at
`.agents/tasks/requirements.md`). All work happens under the worktree at
`/Users/erictole/demo/apcr-dva/.worktrees/session5/demo/session5-secure-assistant`
(abbreviated `<ROOT>` below). Use absolute paths; use
`git -C /Users/erictole/demo/apcr-dva/.worktrees/session5` for any git.

## Ground rules for every item (read before starting)

- **Do NOT modify** `/Users/erictole/demo/apcr-dva/demo/session4-coffee-ship`. It
  is the reference only. Acceptance #1 requires its git diff to stay empty.
- **Local-only verification boundary (authoritative, non-negotiable).** The only
  commands allowed during authoring/verification are: `npm install` + `npx tsc
  --noEmit` + `npx cdk synth` (in `infra/`, with a dummy `CDK_DEFAULT_ACCOUNT`),
  `python3 -m py_compile`, `pytest`, `python3 build_diagram.py` + `rsvg-convert`,
  and `bash -n` on the shell scripts. **NEVER** run `cdk deploy`, `cdk bootstrap`,
  `docker build`, `docker push`, `aws ...` live calls, or any Bedrock/Guardrail
  runtime invocation. `deploy.sh`/`destroy.sh` are authored but never executed
  here (acceptance #25).
- Pinned facts (never re-decide): account `875692608981`, region
  `ap-southeast-1`, Nova via `apac.amazon.nova-micro-v1:0` inference profile,
  `aws-cdk-lib` exactly `2.160.0`, VPC id `vpc-01857e627d800ca7a` and the six
  subnet ids / three AZs from the design's VPC-import section.
- Follow session4 conventions exactly where they apply: `infra/package.json`
  toolchain, `infra/tsconfig.json`, `infra/cdk.json` context flags (incl.
  `@aws-cdk/aws-iam:minimizePolicies: true`), two-stack `bin/`+`lib/` split with
  cross-stack refs via stack props, `set -euo pipefail` + numbered-step echo
  scripts with a typed-`destroy` guard, and the base64 icon-embed `build_diagram.py`.
- Each item must leave the project in a buildable state (`tsc --noEmit` + `cdk
  synth` succeed, `py_compile` passes) before the next item starts.

The three NIT findings from design review are folded into the relevant items:
NIT-6 (pin `strands-agents==1.23.0`, guardrail kwargs via `**model_config`) in
item 9; NIT-7 (`bedrock:ApplyGuardrail` is defensive, scoped to the guardrail
ARN) in items 5 and 7.

---

## Phase A — CDK scaffolding (must compile and synth before any stack logic)

- [ ] 1. Scaffold the `infra/` CDK project skeleton so `tsc` and `cdk synth` run
      against an empty-but-valid app. Create `infra/package.json` (name
      `secure-assistant-infra`, `bin.secure-assistant = bin/secure-assistant.ts`,
      deps `aws-cdk-lib: "2.160.0"` + `constructs: "^10.3.0"`, devDeps `aws-cdk:
      2.160.0`, `typescript: ~5.5.4`, `ts-node: ^10.9.2`, `@types/node:
      ^20.14.0` — identical pins to session4), `infra/tsconfig.json` (copy
      session4's verbatim, incl. `experimentalDecorators: true`),
      `infra/cdk.json` (`app: "npx ts-node --prefer-ts-exts
      bin/secure-assistant.ts"` + the full session4 `context` block incl.
      `@aws-cdk/aws-iam:minimizePolicies: true`), and a minimal
      `bin/secure-assistant.ts` that constructs `new cdk.App()` with
      `env = { region: 'ap-southeast-1', account: process.env.CDK_DEFAULT_ACCOUNT }`
      and calls `app.synth()` (stacks added in later items). Add
      `infra/.gitignore` ignoring `node_modules/`, `cdk.out/`, `*.js`, `*.d.ts`.
      Files: `<ROOT>/infra/package.json`, `<ROOT>/infra/tsconfig.json`,
      `<ROOT>/infra/cdk.json`, `<ROOT>/infra/bin/secure-assistant.ts`,
      `<ROOT>/infra/.gitignore`.
      Verify: `cd <ROOT>/infra && npm install && npx tsc --noEmit` → no errors;
      `CDK_DEFAULT_ACCOUNT=111111111111 npx cdk synth` → produces `cdk.out` with
      no live calls. Confirm `infra/package.json` pins `aws-cdk-lib` to exactly
      `2.160.0` (acceptance #2, #3, #4).

- [ ] 2. Add the shared VPC-import helper `lib/vpc-import.ts` exporting a function
      `importVpc(scope: Construct): ec2.IVpc` that returns
      `ec2.Vpc.fromVpcAttributes(scope, 'ImportedVpc', {...})` using the literal
      ids from the design (vpcId `vpc-01857e627d800ca7a`, cidr `10.1.0.0/16`, AZs
      `[ap-southeast-1a,1b,1c]`, the three `privateSubnetIds` and three
      `publicSubnetIds` in AZ-matched order) — **not** `fromLookup` (NFR-4).
      Export a helper returning the three private subnets as a `SubnetSelection`
      via `ec2.Subnet.fromSubnetId` so Lambdas/endpoints select them explicitly.
      Add a code comment: private subnets have a NAT route but Bedrock traffic
      goes via the interface endpoint (item 7), not NAT.
      Files: `<ROOT>/infra/lib/vpc-import.ts`.
      Verify: `cd <ROOT>/infra && npx tsc --noEmit` → no errors (helper is
      imported by stacks in later items; a stray-unused-export is fine under the
      session4 `noUnusedLocals: false`).

## Phase B — SecurityData stack (the substrate referenced by AppEdgeAI)

- [ ] 3. Create the `SecureAssistantSecurityData` stack in
      `lib/security-data-stack.ts` with the KMS CMK, DynamoDB tables, Secrets
      Manager secret, and SSM parameter, exposing typed `public readonly`
      members for cross-stack wiring. Specifically: one `kms.Key`
      (`enableKeyRotation: true`, `alias: 'alias/session5-secure-assistant'`,
      `removalPolicy: DESTROY`); `orders` table (PK `orderId` S, `PAY_PER_REQUEST`,
      `encryption: CUSTOMER_MANAGED` + `encryptionKey: key`, DESTROY); `pending-refunds`
      table (PK `confirmationToken` S, `PAY_PER_REQUEST`, CMK, TTL attribute `ttl`
      enabled, DESTROY, tagged `team=support` via `cdk.Tags.of(table).add('team',
      'support')`); Secrets Manager secret `session5/payment-processor-key`
      (`generateSecretString` like session4's payment secret); SSM `StringParameter`
      `/session5/assistant/config` holding a JSON string (greeting, maxRefund, etc).
      Register the stack in `bin/secure-assistant.ts` with the shared `env`.
      Files: `<ROOT>/infra/lib/security-data-stack.ts`,
      `<ROOT>/infra/bin/secure-assistant.ts`.
      Verify: `cd <ROOT>/infra && npx tsc --noEmit && CDK_DEFAULT_ACCOUNT=111111111111
      npx cdk synth SecureAssistantSecurityData` → synth succeeds; template shows
      a CMK, two DynamoDB tables with customer-managed KMS, the secret, and the
      SSM parameter (acceptance #6, #9).

- [ ] 4. Add the Bedrock Guardrail, its published version, and the Bedrock
      invocation-logging configuration to the SecurityData stack. Create a
      `bedrock.CfnGuardrail` with content filters **Hate** and **Violence** at
      **HIGH** (input+output), PII entities `ACCOUNT_NUMBER`,
      `US_SOCIAL_SECURITY_NUMBER`, `EMAIL` set to **MASK** (input+output), one
      **BLOCK** example (a denied topic `legal-advice` and/or a BLOCK-action PII
      entity), and `blockedInputMessaging`/`blockedOutputsMessaging`; publish a
      `bedrock.CfnGuardrailVersion`. Expose `guardrailId` (from
      `guardrail.attrGuardrailId`) and `guardrailVersion` (from
      `version.attrVersion`) as public readonly strings. Create a CMK-encrypted
      CloudWatch `logs.LogGroup` (`encryptionKey: key`) and a CMK-encrypted S3
      log bucket (`BucketEncryption.KMS`, `encryptionKey: key`, `BLOCK_ALL`), a
      Bedrock logging IAM role, grant the Bedrock logging/delivery principal
      `kms:GenerateDataKey*`+`kms:Decrypt` on the CMK, and provision invocation
      logging via an **escape-hatch** `new cdk.CfnResource(this,
      'BedrockInvokeLogging', { type: 'AWS::Bedrock::ModelInvocationLoggingConfiguration',
      properties: { LoggingConfig: {...} } })` with the exact `LoggingConfig` JSON
      from design Decision 5 (CloudWatch + S3 destinations, both CMK-encrypted).
      Do NOT use a `CfnModelInvocationLoggingConfiguration` class — it does not
      exist in `aws-cdk-lib@2.160.0` (design Finding 1).
      Files: `<ROOT>/infra/lib/security-data-stack.ts`.
      Verify: `cd <ROOT>/infra && npx tsc --noEmit && CDK_DEFAULT_ACCOUNT=111111111111
      npx cdk synth SecureAssistantSecurityData` → synth succeeds; the template
      contains a `CfnGuardrail` (Hate+Violence HIGH, PII MASK, a BLOCK example) +
      `CfnGuardrailVersion`, and a raw `AWS::Bedrock::ModelInvocationLoggingConfiguration`
      resource whose destinations reference the CMK (acceptance #12, #14).

## Phase C — AppEdgeAI stack (edge + compute + observability)

- [ ] 5. Create the `SecureAssistantAppEdgeAI` stack shell in
      `lib/app-edge-ai-stack.ts` with its `AppEdgeAIStackProps` interface and
      imported VPC. Define `AppEdgeAIStackProps extends cdk.StackProps` carrying
      `kmsKey: kms.IKey`, `ordersTable`/`pendingRefundsTable: dynamodb.ITable`,
      `receiptsBucket` is created here (not passed), `paymentSecret:
      secretsmanager.ISecret`, `configParam: ssm.IStringParameter`, `guardrailId:
      string`, `guardrailVersion: string`. In the constructor, import the VPC via
      the item-2 helper and create the security groups: `assistantSg` (agent
      Lambda) and `bedrockEndpointSg`. Register the stack in
      `bin/secure-assistant.ts`, passing the SecurityData members through props
      (session4 wiring style). Nothing else yet.
      Files: `<ROOT>/infra/lib/app-edge-ai-stack.ts`,
      `<ROOT>/infra/bin/secure-assistant.ts`.
      Verify: `cd <ROOT>/infra && npx tsc --noEmit && CDK_DEFAULT_ACCOUNT=111111111111
      npx cdk synth --all` → two stacks synth; template shows no `AWS::EC2::VPC`
      resource (acceptance #5, #6).

- [ ] 6. Add the receipts S3 bucket (CMK, TLS-only DENY), the SPA bucket
      (OAC-ready), and their resource policies to the AppEdgeAI stack. Receipts
      bucket: `BucketEncryption.KMS` with `props.kmsKey`, `bucketKeyEnabled`,
      `BLOCK_ALL`, `removalPolicy: DESTROY` + `autoDeleteObjects: true`; attach
      the TLS-only `DenyInsecureTransport` resource policy (DENY `s3:*` for
      `AnyPrincipal` when `aws:SecureTransport = false`) exactly as in design.
      SPA bucket: `S3_MANAGED`, `BLOCK_ALL`, DESTROY + autoDelete, plus a
      defensive TLS-only deny.
      Files: `<ROOT>/infra/lib/app-edge-ai-stack.ts`.
      Verify: `cd <ROOT>/infra && npx tsc --noEmit && CDK_DEFAULT_ACCOUNT=111111111111
      npx cdk synth SecureAssistantAppEdgeAI` → template shows the receipts
      bucket resource policy with a `Deny` on `aws:SecureTransport = false`
      (acceptance #10) and the receipts bucket encrypted with the CMK (#9).

- [ ] 7. Add the two Bedrock interface VPC endpoints with endpoint policy + tight
      SG to the AppEdgeAI stack. Create `ec2.InterfaceVpcEndpoint` for
      `BEDROCK_RUNTIME` and one for `BEDROCK` (control plane) in the three private
      subnets, `privateDnsEnabled: true`, `securityGroups: [bedrockEndpointSg]`.
      `bedrockEndpointSg.addIngressRule(assistantSg, ec2.Port.tcp(443))` only.
      Attach a **non-wildcard** endpoint policy allowing `bedrock:InvokeModel`,
      `bedrock:InvokeModelWithResponseStream`, `bedrock:ApplyGuardrail` on the
      inference-profile ARN
      `arn:aws:bedrock:ap-southeast-1:875692608981:inference-profile/apac.amazon.nova-micro-v1:0`,
      the foundation-model ARN `arn:aws:bedrock:*::foundation-model/amazon.nova-micro-v1:0`,
      and the guardrail ARN (for `ApplyGuardrail`). Add a code comment that
      `ApplyGuardrail` is included **defensively** (inline-guardrail wiring may
      not issue a separate call — design Finding 7). Add a code comment: private
      subnet != private path to Bedrock; PrivateLink is what keeps it off NAT.
      Files: `<ROOT>/infra/lib/app-edge-ai-stack.ts`.
      Verify: `cd <ROOT>/infra && npx tsc --noEmit && CDK_DEFAULT_ACCOUNT=111111111111
      npx cdk synth SecureAssistantAppEdgeAI` → template shows a `bedrock-runtime`
      interface endpoint in the private subnets with a non-wildcard policy and an
      SG admitting only `assistantSg` on 443 (acceptance #13).

- [ ] 8. Add the three Lambda functions, their IAM roles (least privilege + ABAC
      + identity/resource pairing), and X-Ray tracing to the AppEdgeAI stack —
      wired to the Python sources authored in Phase D. The **assistant** is a
      `lambda.DockerImageFunction` from `lambda.DockerImageCode.fromImageAsset('<ROOT>/app',
      { file: 'Dockerfile' })`, in the three private subnets with `assistantSg`,
      `timeout: 60s`, `memory: 1024`, `tracing: ACTIVE`, env `GUARDRAIL_ID`,
      `GUARDRAIL_VERSION`, table names, secret/param names, region. The
      **refund_confirm** and **presign** are `lambda.Function`
      (`runtime: PYTHON_3_12`, `code: fromAsset('<ROOT>/app/refund_confirm' | '.../presign')`,
      `tracing: ACTIVE`). IAM: agent role grants `bedrock:InvokeModel` +
      `InvokeModelWithResponseStream` on **both** the inference-profile ARN and
      the foundation-model ARN (plus `ApplyGuardrail` defensively on the guardrail
      ARN), DynamoDB RW scoped to the two tables, `secretsmanager:GetSecretValue`
      on the payment secret ARN only, `ssm:GetParameter` on the config param ARN
      only, X-Ray write, and `kms` decrypt/generate on the CMK; presign role gets
      an **identity** `s3:GetObject` on `receiptsBucket.arnForObjects('*')`
      (pairs with the item-6 resource DENY → acceptance #11/#16). Add the **ABAC**
      policy statement on the refund_confirm/operator role: ALLOW
      `dynamodb:GetItem`/`UpdateItem` on the pending-refunds ARN conditioned
      `StringEquals: { 'aws:ResourceTag/team': '${aws:PrincipalTag/team}' }` —
      **single-quoted non-template string** so the IAM variable survives verbatim
      (design Finding 5), with the code comment explaining why a backtick literal
      is forbidden; tag the operator role `team=support`. No `Action:'*'`/`Resource:'*'`
      except the foundation-model ARN wildcard form.
      Files: `<ROOT>/infra/lib/app-edge-ai-stack.ts`.
      Verify: `cd <ROOT>/infra && npx tsc --noEmit && CDK_DEFAULT_ACCOUNT=111111111111
      npx cdk synth SecureAssistantAppEdgeAI` → synth succeeds (image asset only
      staged, no `docker build` at synth — design Decision 2); template shows the
      agent role dual-ARN Bedrock grant (#15), the literal `${aws:PrincipalTag/team}`
      in the rendered ABAC statement (#11), and no VPC resource. (This item
      depends on Phase D sources existing; if authoring stacks first, create empty
      `app/` + `app/Dockerfile` + `app/refund_confirm/` + `app/presign/` dirs so
      asset staging resolves, then flesh them out in Phase D.)

- [ ] 9. Add the API Gateway REST API (X-Ray on), the regional WAF WebACL +
      association, and the CloudFront distribution (OAC S3 + `/api/*`) to the
      AppEdgeAI stack, plus the SPA `BucketDeployment` and the CloudFront URL
      output. REST API (`apigateway.RestApi`, regional) with
      `deployOptions.tracingEnabled: true` and a top-level `/api` resource holding
      `POST /api/chat`→assistant, `POST /api/refunds/confirm`→refund_confirm, `GET
      /api/receipts/{orderId}/url`→presign (proxy integrations). Regional
      `wafv2.CfnWebACL` (`scope: 'REGIONAL'`) with `AWSManagedRulesCommonRuleSet`
      (`overrideAction: { none: {} }`) and a rate-based rule `action: { count: {} }`
      (COUNT mode, `limit: 2000`, `aggregateKeyType: 'IP'`), CloudWatch metrics
      on; associate to the API stage via `wafv2.CfnWebACLAssociation`.
      `cloudfront.Distribution`: default behavior = SPA bucket via
      `origins.S3BucketOrigin.withOriginAccessControl(spaBucket)` (OAC,
      `REDIRECT_TO_HTTPS`, `CACHING_OPTIMIZED`, GET/HEAD), additional behavior
      `/api/*` = `origins.RestApiOrigin(api)` (`REDIRECT_TO_HTTPS`,
      `CACHING_DISABLED`, `originRequestPolicy: ALL_VIEWER_EXCEPT_HOST_HEADER`,
      `ALLOW_ALL`), `defaultRootObject: 'index.html'`, default CloudFront
      domain/cert (no ACM, no alias). Add `s3deploy.BucketDeployment` from
      `<ROOT>/spa` to the SPA bucket. `CfnOutput` the CloudFront URL.
      Files: `<ROOT>/infra/lib/app-edge-ai-stack.ts`.
      Verify: `cd <ROOT>/infra && npx tsc --noEmit && CDK_DEFAULT_ACCOUNT=111111111111
      npx cdk synth SecureAssistantAppEdgeAI` → template has a CloudFront
      distribution with an OAC S3 origin + `/api/*` behavior and NO
      `AWS::CertificateManager::Certificate`/alias (#7), a WebACL with the common
      rule set + a COUNT rate rule associated regionally (#8), and `tracingEnabled`
      on the API stage (#20). (Needs `<ROOT>/spa` to exist — create it in Phase E
      first, or a placeholder `index.html` so `BucketDeployment` staging resolves.)

## Phase D — Python Lambda sources (pure, unit-testable)

- [ ] 10. Create the PII helpers and Strands tools as pure functions.
      `app/assistant/pii.py`: `mask_account`, `mask_ssn`, `mask_email`,
      `mask_pii`, `validate` — pure functions, with code comments explaining the
      **guardrail tool-call blind spot** (the guardrail does not see tool
      args/results, so handlers mask themselves). `app/assistant/tools.py`:
      `look_up_order(order_id)` (read-only; validates `^ORD-[0-9]{6}$`) and a
      factory `make_initiate_refund(table, req_ctx)` returning an `@tool`
      `initiate_refund(order_id, amount)` that validates+masks args, writes a
      `pending-refunds` item keyed by a fresh `uuid4` `confirmationToken` with
      `status='PENDING_CONFIRMATION'`, `ttl`, masked order ref, amount — **moves
      no money** — appends `{token, amountMasked, orderMasked}` to
      `req_ctx['pending_refunds']` (the request-scoped side channel, design
      Decision 6), and returns a PENDING-CONFIRMATION dict. DynamoDB access is
      injected (`table` arg) so tests use a stub. Never write raw PII.
      Files: `<ROOT>/app/assistant/pii.py`, `<ROOT>/app/assistant/tools.py`.
      Verify: `python3 -m py_compile <ROOT>/app/assistant/pii.py
      <ROOT>/app/assistant/tools.py` → no errors.

- [ ] 11. Create the assistant Lambda handler wiring Strands + Nova Micro +
      guardrail + X-Ray subsegments. `app/assistant/handler.py`: `from
      strands import Agent, tool`; `from strands.models import BedrockModel`;
      construct `BedrockModel(model_id='apac.amazon.nova-micro-v1:0',
      region_name='ap-southeast-1', guardrail_id=os.environ['GUARDRAIL_ID'],
      guardrail_version=os.environ['GUARDRAIL_VERSION'],
      guardrail_trace='enabled')` with a comment noting the guardrail kwargs are
      forwarded via `**model_config` in `strands-agents==1.23.0` (design NIT-6);
      no Bedrock classic Agent / AgentCore. Build a per-request `req_ctx =
      {'pending_refunds': []}`, bind `make_initiate_refund(table, req_ctx)`,
      `Agent(model=model, tools=[look_up_order, initiate_refund])`. Parse the API
      GW proxy event (validate `message` 1–2000 chars → 400 on bad input),
      `from aws_xray_sdk.core import patch_all; patch_all()`, wrap the model call
      in `xray_recorder.in_subsegment('bedrock-invoke')` and DynamoDB access in a
      `'ddb-...'` subsegment (acceptance #20, #28), then build the response
      envelope `{reply, pendingRefund?}` from `req_ctx['pending_refunds']` (not
      from model text — Decision 6 side-channel contract). Handle errors per the
      design error table (generic, PII-free). Add `app/assistant/__init__.py` if
      needed for imports.
      Files: `<ROOT>/app/assistant/handler.py`.
      Verify: `python3 -m py_compile <ROOT>/app/assistant/handler.py` → no errors
      (no runtime import of `strands` required for py_compile) (acceptance #16).

- [ ] 12. Create the `refund_confirm` and `presign` Lambda handlers.
      `app/refund_confirm/handler.py`: validate `confirmationToken` (uuid4
      format → 400), look up the pending-refunds item (404 missing / 409 already
      confirmed / 410 expired), idempotently flip `status` to `CONFIRMED`, read
      the payment secret to demonstrate the grant, **stub** the processor call
      (moves no real money), return a result. `app/presign/handler.py`: validate
      `orderId` (`^ORD-[0-9]{6}$` → 400), generate a presigned GET URL
      (`ExpiresIn=300`) for `receipts/{orderId}.pdf`, 500 on KMS/permission
      error. Keep URL-generation logic as an injectable/pure function for tests.
      Files: `<ROOT>/app/refund_confirm/handler.py`,
      `<ROOT>/app/presign/handler.py`.
      Verify: `python3 -m py_compile <ROOT>/app/refund_confirm/handler.py
      <ROOT>/app/presign/handler.py` → no errors.

- [ ] 13. Create the Lambda dependency manifests and the assistant Dockerfile.
      `app/requirements.txt` pinning `strands-agents==1.23.0`,
      `strands-agents-tools==0.2.9`, `boto3==1.35.76`, `aws-xray-sdk==2.14.0`
      (acceptance #17). `app/dev-requirements.txt` pinning `pytest`.
      `app/Dockerfile`: `FROM public.ecr.aws/lambda/python:3.12`, copy
      `requirements.txt`, `pip install -r requirements.txt`, copy `assistant/`,
      set `CMD ["assistant.handler.handler"]` (or the matching module path).
      Files: `<ROOT>/app/requirements.txt`, `<ROOT>/app/dev-requirements.txt`,
      `<ROOT>/app/Dockerfile`.
      Verify: `bash -n` not applicable; confirm `app/requirements.txt` pins the
      three required packages to explicit versions. (The image is built only at
      deploy — never here; design Decision 2.)

- [ ] 14. Write the pytest unit tests for the pure handlers.
      `app/tests/conftest.py` adds `app/` to `sys.path` (session4 pattern) so
      `assistant.pii`/`assistant.tools`/`refund_confirm.handler`/`presign.handler`
      import. `test_pii.py` (masking/validation). `test_tools.py`:
      `initiate_refund` returns PENDING_CONFIRMATION, writes a token, moves no
      money, and a raw account number never appears in the written item nor in a
      captured log line (acceptance #18, #19). `test_refund.py`: the confirm step
      executes only with a matching token (idempotent, expiry/already-confirmed
      paths). `test_presign.py`: URL generation via a botocore stub + bad-orderId
      rejection. Use injected table/stub objects — no live AWS, no moto needed.
      Files: `<ROOT>/app/tests/conftest.py`, `<ROOT>/app/tests/test_pii.py`,
      `<ROOT>/app/tests/test_tools.py`, `<ROOT>/app/tests/test_refund.py`,
      `<ROOT>/app/tests/test_presign.py`.
      Verify: `cd <ROOT> && python3 -m pytest app/tests -q` → all tests pass;
      `python3 -m py_compile` on every `.py` under `app/` → no errors (#22).

## Phase E — SPA

- [ ] 15. Create the dependency-light chat SPA (no build step). `spa/index.html`
      (chat UI shell), `spa/app.js`, `spa/styles.css`. `app.js`: POST `{message}`
      to same-origin `"/api/chat"`; when the response carries
      `{pendingRefund:{token, amountMasked, orderMasked}}`, render a **Confirm
      refund** button that POSTs `{token}` to `"/api/refunds/confirm"` (treat the
      token as opaque, never parse it from assistant text); a **Download receipt**
      control that GETs `"/api/receipts/{orderId}/url"` then opens the returned
      presigned URL. No secrets/API keys in the SPA. (If item 9 was authored
      before this, replace the placeholder `index.html` created there.)
      Files: `<ROOT>/spa/index.html`, `<ROOT>/spa/app.js`, `<ROOT>/spa/styles.css`.
      Verify: `cd <ROOT>/infra && CDK_DEFAULT_ACCOUNT=111111111111 npx cdk synth
      SecureAssistantAppEdgeAI` → the `BucketDeployment` stages `spa/` with no
      bundler/npm build (acceptance #21 UI controls present; verified visually in
      the SPA source).

## Phase F — Diagram, scripts, docs

- [ ] 16. Create the architecture diagram generator reusing the session4 base64
      icon-embed approach. `diagram/build_diagram.py` modeled on
      `demo/session4-coffee-ship/container/build_diagram.py` (`data_uri()`
      inlining each `*_64.svg` as `data:image/svg+xml;base64`, zones, curved
      bezier `edge()`, numbered steps, legend, drop-shadow). `ICON_BASE =
      "/Users/erictole/demo/apcr-dva/aws-icons/Architecture-Service-Icons_04302026"`
      with the verified icon relative paths from design (cloudfront, waf, apigw,
      lambda, bedrock, privatelink, vpc, dynamodb, s3, kms, secrets, iam, ssm,
      xray, cloudwatch — all confirmed present). Draw: Viewer → CloudFront →
      {S3+OAC SPA; `/api/*` → WAF → API GW → assistant Lambda in VPC private
      subnets}; Lambda → PrivateLink bedrock-runtime → Bedrock Nova Micro
      (guardrail); Lambda → DynamoDB (CMK) + Secrets + SSM; presign → receipts S3
      (CMK, TLS-only); Bedrock invocation logs → CMK CloudWatch; X-Ray across API
      GW + Lambdas; four color-coded act zones. Write `diagram/architecture.svg`.
      Files: `<ROOT>/diagram/build_diagram.py`.
      Verify: `cd <ROOT>/diagram && python3 build_diagram.py && rsvg-convert -o
      architecture.png architecture.svg` → both `architecture.svg` and
      `architecture.png` produced; icons embedded as base64 (no external file
      refs in the SVG) (acceptance #23).

- [ ] 17. Author `deploy.sh` and `destroy.sh` (not executed here). `deploy.sh`
      (`set -euo pipefail`, `AWS_REGION`/`AWS_DEFAULT_REGION=ap-southeast-1`,
      numbered-step echo): preflight (`aws docker node npm python3 zip
      rsvg-convert`), `npm install` + `cdk bootstrap`, build+push the assistant
      image (this is where docker build happens — never at synth), `cdk deploy
      SecureAssistantSecurityData` (capture guardrail id/version), `cdk deploy
      SecureAssistantAppEdgeAI`, seed demo data (orders items, a sample receipt
      PDF to the receipts bucket, the SSM config), resolve+print the CloudFront
      URL. `destroy.sh` (`set -euo pipefail`, region pinned, **guarded**: aborts
      unless the operator types `destroy`): confirm prompt, empty SPA+receipts
      buckets (all versions/delete markers), delete the Bedrock
      invocation-logging configuration (account/region singleton) so the CMK is
      not pinned, `cdk destroy --all --force`, sweep leftover asset buckets/log
      groups. Follow the session4 script structure.
      Files: `<ROOT>/deploy.sh`, `<ROOT>/destroy.sh`.
      Verify: `bash -n <ROOT>/deploy.sh && bash -n <ROOT>/destroy.sh` → pass;
      confirm `destroy.sh` aborts unless `destroy` is typed (acceptance #22).

- [ ] 18. Write `README.md` and `FACILITATOR-RUNBOOK.md` walking the four acts
      with **OLX** and **Clariant** talking points and all seven required
      callouts: ACM us-east-1 rule (taught though no cert is provisioned); Nova
      inference-profile requirement; Strands guardrail wiring; guardrail
      tool-call blind spot; human-in-the-loop refund; invocation-logging PII trap;
      the Strands Agents SDK note — plus the regional-WAF-vs-us-east-1-CloudFront-WAF
      tradeoff (design FR-36/FR-37). Reference the diagram and the local-only
      verification boundary. Match session4 doc tone.
      Files: `<ROOT>/README.md`, `<ROOT>/FACILITATOR-RUNBOOK.md`.
      Verify: confirm both docs contain all seven callouts + the regional-WAF
      tradeoff + OLX/Clariant references across the four acts (acceptance #24).

## Phase G — add CDK template assertions and run the full local gate

- [ ] 19. Add the `cdk` template-assertion test and run the complete local
      verification suite end-to-end. Create `infra/test/template.test.ts` using
      `Template.fromStack` to assert: `resourceCountIs('AWS::EC2::VPC', 0)`; two
      stacks; CloudFront with an OAC S3 origin + `/api/*` behavior and no ACM
      cert; WebACL with the common rule set + a COUNT rate rule associated
      regionally; CMK on receipts + log destination + both tables; receipts
      TLS-only Deny; ABAC statement containing the literal `${aws:PrincipalTag/team}`
      verbatim; `CfnGuardrail` (filters/PII/BLOCK) + published version;
      `bedrock-runtime` interface endpoint with non-wildcard policy + SG;
      `hasResource('AWS::Bedrock::ModelInvocationLoggingConfiguration', ...)` on
      the raw CFN type with a CMK-encrypted destination; agent-role dual-ARN
      Bedrock grant; X-Ray on API GW + Lambda. (Add `jest`/`aws-cdk-lib`
      assertions + a test runner to `infra/package.json` devDeps and a `test`
      script, consistent with the pinned toolchain, or run via `ts-node` if a
      test runner is not already present — do not change the `aws-cdk-lib` pin.)
      Files: `<ROOT>/infra/test/template.test.ts`, `<ROOT>/infra/package.json`.
      Verify (full local gate, in order — all must pass):
      1. `cd <ROOT>/infra && npm install && npx tsc --noEmit`
      2. `cd <ROOT>/infra && CDK_DEFAULT_ACCOUNT=111111111111 npx cdk synth --all`
      3. `cd <ROOT>/infra && npm test` (the template assertions)
      4. `cd <ROOT> && python3 -m py_compile $(find app -name '*.py')`
      5. `cd <ROOT> && python3 -m pytest app/tests -q`
      6. `cd <ROOT>/diagram && python3 build_diagram.py && rsvg-convert -o architecture.png architecture.svg`
      7. `bash -n <ROOT>/deploy.sh && bash -n <ROOT>/destroy.sh`
      NO `cdk deploy`, `cdk bootstrap`, `docker build/push`, live `aws` calls, or
      Bedrock invocation at any point (acceptance #25).

- [ ] 20. Final consistency sweep against the acceptance criteria. Confirm the
      directory holds `infra/`, `spa/`, `app/`, `deploy.sh`, `destroy.sh`,
      `README.md`, `FACILITATOR-RUNBOOK.md`, and the diagram generator; confirm
      `git -C /Users/erictole/demo/apcr-dva/.worktrees/session5 status` shows the
      new files only under `demo/session5-secure-assistant/` and that
      `demo/session4-coffee-ship` has an empty diff (acceptance #1). Walk each of
      the 25 acceptance criteria and confirm the corresponding artifact/assertion
      exists. Fix any gap, then re-run the full local gate from item 19.
      Files: none (verification + targeted fixes only).
      Verify: re-run the item-19 gate (all pass) and `git -C
      /Users/erictole/demo/apcr-dva/.worktrees/session5 status --short` shows no
      changes under `demo/session4-coffee-ship`.

---

## Notes and assumptions

- **Authoring order vs. dependency order.** Phase C stack items (8, 9) reference
  the Phase D/E sources via asset paths. Either author Phase D/E first, or create
  the directories (`app/`, `app/Dockerfile`, `app/refund_confirm/`,
  `app/presign/`, `spa/index.html`) as minimal placeholders when doing the stack
  items so `cdk synth` asset staging resolves, then flesh them out. The item
  text calls this out where it matters; the full gate in item 19 is the real
  acceptance.
- **No `CfnModelInvocationLoggingConfiguration` class** exists in
  `aws-cdk-lib@2.160.0` — invocation logging is an escape-hatch
  `cdk.CfnResource` of type `AWS::Bedrock::ModelInvocationLoggingConfiguration`
  (design Finding 1). Assert via `hasResource` on the raw type, not an L1 class.
- **Docker at synth.** `DockerImageCode.fromImageAsset` only *stages* the build
  context and emits an image-asset manifest at synth; it does **not** run
  `docker build` (design Decision 2). No `CDK_DOCKER=echo` is required; the real
  build happens in `deploy.sh` at deploy time, which is never executed here.
- **CDK test runner.** Session4 ships no `infra/test/` or test runner, so item 19
  adds one (jest or ts-node-driven) within the pinned toolchain without touching
  the `aws-cdk-lib` 2.160.0 pin. If adding jest proves heavy, the template
  assertions may instead run as a standalone `ts-node` script invoked by the
  `test` npm script — either satisfies the local-only gate.
- A sample receipt PDF for the receipts bucket is seeded by `deploy.sh` at deploy
  time (not committed), consistent with session4 seeding demo data in the script.
