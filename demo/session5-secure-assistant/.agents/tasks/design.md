# Session 5 — Secure Coffee-Shop AI Assistant: Technical Design

## Overview

This design builds a standalone, locally-synthesizable AWS CDK v2 (TypeScript)
demo at `.worktrees/session5/demo/session5-secure-assistant` that secures a
coffee-shop AI customer-support assistant built with the **Strands Agents SDK**.
It teaches the DVA-C03 **Security & Observability** domain across four acts
(network/data security, identity/access, Strands assistant secured,
observability). The assistant runs as a Python 3.12 Lambda in the VPC private
subnets, invokes **Amazon Nova Micro** via the APAC inference profile over a
Bedrock-runtime PrivateLink endpoint, is wrapped by a Bedrock Guardrail, and is
fronted by a CloudFront distribution that serves an OAC-private SPA plus an
`/api/*` API origin protected by a regional WAF.

The project mirrors `demo/session4-coffee-ship` conventions exactly — same
`aws-cdk-lib@2.160.0` toolchain, same `bin/`+`lib/` two-stack split, same
`ec2.Vpc.fromVpcAttributes` import style, same `deploy.sh`/`destroy.sh` shape
with `set -euo pipefail` and pinned region, and the same base64 icon-embed SVG
diagram generator from `container/build_diagram.py`. Session4 is **not
modified**. The technology stack is locked by this design: CDK v2 TypeScript for
infra, Python 3.12 + `strands-agents`/`strands-agents-tools`/`boto3` for Lambda,
plain HTML/JS for the SPA, and `build_diagram.py` + `rsvg-convert` for the
diagram.

Verification is **local only** throughout: `npm install` + `tsc --noEmit`, `cdk
synth` (dummy account, no lookups), `python3 -m py_compile`, `python3
build_diagram.py` + `rsvg-convert`, `bash -n` on the scripts, and `pytest` on
the pure Python handlers. **No** `cdk deploy`, `docker push`, or Bedrock/
Guardrail runtime calls occur during authoring.

---

## Technology stack (locked)

| Layer | Choice | Version / pin |
| --- | --- | --- |
| Infra | AWS CDK v2, TypeScript | `aws-cdk-lib` **exactly `2.160.0`**, `constructs ^10.3.0`, `aws-cdk 2.160.0`, `typescript ~5.5.4`, `ts-node ^10.9.2`, `@types/node ^20.14.0` (identical to session4) |
| Agent runtime | Python 3.12 Lambda | `strands-agents==1.23.0`, `strands-agents-tools==0.2.9`, `boto3==1.35.76`, `aws-xray-sdk==2.14.0` |

> Strands version note (resolves Finding 6 — NIT): the pin is `strands-agents==1.23.0`
> to match the version available/installed in this environment (verified
> `importlib.metadata.version('strands-agents') == '1.23.0'`). The guardrail
> kwargs `guardrail_id`, `guardrail_version`, `guardrail_trace` are **not**
> first-class `BedrockModel.__init__` parameters; they are accepted and
> forwarded through `**model_config` (confirmed present in the installed
> `BedrockModel` source), so the wiring below is valid for 1.23.0. Verification
> is `py_compile` only (no `pip install`), so the pin is a deploy-time
> declaration, not something exercised during authoring.
| SPA | Plain HTML/CSS/JS (no build step) | assets committed as static files; S3 `BucketDeployment` from a source dir |
| Diagram | Python stdlib (`base64`,`os`) + `rsvg-convert` | icons from `/Users/erictole/demo/apcr-dva/aws-icons` |

Rationale for the SPA choice (resolves requirements A4): plain HTML/JS keeps
`cdk synth` fully self-contained with **no npm build dependency for the
frontend** and no `cdk.out` asset bundling that would need Docker. Session4
used a Vite SPA because it was baked into a container image at pipeline time;
here the SPA is served statically from S3 via CloudFront, so a build step adds
risk (NFR-4: synth must succeed offline) with no benefit. `s3deploy.Source.asset`
on a directory of static files synthesizes to a zip asset with no bundler.

---

## Repository layout

```
session5-secure-assistant/
  infra/
    bin/secure-assistant.ts              # app entry, env pinned ap-southeast-1
    lib/security-data-stack.ts           # SecurityData stack
    lib/app-edge-ai-stack.ts             # AppEdgeAI stack
    lib/vpc-import.ts                     # shared fromVpcAttributes helper
    package.json  tsconfig.json  cdk.json
    test/template.test.ts                # cdk assertions (Template.fromStack)
  app/
    assistant/handler.py                 # Strands agent Lambda (API-backed)
    assistant/tools.py                   # @tool handlers + PII masking (pure)
    assistant/pii.py                     # pure PII validate/mask helpers
    refund_confirm/handler.py            # confirm-refund Lambda
    presign/handler.py                   # presigned receipt URL Lambda
    requirements.txt                     # runtime pins
    dev-requirements.txt                 # pytest pins
    Dockerfile                           # container image for the assistant Lambda
    tests/test_tools.py tests/test_pii.py tests/test_refund.py tests/test_presign.py
  spa/
    index.html  app.js  styles.css       # chat + receipt download + confirm button
  diagram/
    build_diagram.py                     # base64 icon-embed SVG generator
    architecture.svg architecture.png    # generated artifacts
  deploy.sh  destroy.sh
  README.md  FACILITATOR-RUNBOOK.md
```

---

## Stack split and cross-stack wiring

Two stacks, matching the session4 `NetworkDataStack` + `AppPipelineStack`
pattern and FR-4:

- **`SecureAssistantSecurityData`** (`SecurityData` stack) — the security and
  data substrate that must exist first and is referenced by resource/ARN:
  KMS CMK; DynamoDB `orders` and `pending-refunds` tables; receipts S3 bucket
  (TLS-only deny policy); Secrets Manager payment key; SSM config parameter;
  the `CfnGuardrail` + `CfnGuardrailVersion`; and the Bedrock invocation-logging
  configuration — provisioned via an **escape-hatch `cdk.CfnResource` of type
  `AWS::Bedrock::ModelInvocationLoggingConfiguration`** (there is no
  `CfnModelInvocationLoggingConfiguration` L2/L1 in `aws-cdk-lib@2.160.0` — see
  Decision 5), whose CloudWatch log group / S3 destination is CMK-encrypted. It
  exposes typed public readonly members.

- **`SecureAssistantAppEdgeAI`** (`AppEdgeAI` stack) — the edge + compute +
  observability layer: imported VPC, security groups, the `bedrock-runtime`
  (and `bedrock` control-plane) interface VPC endpoints, the three Lambdas, the
  API Gateway REST API (X-Ray on), the regional WAF WebACL + association, the
  CloudFront distribution (OAC S3 origin + `/api/*` API origin), the SPA
  `BucketDeployment`, and all IAM roles/policies (identity policies live with
  the roles here; resource policies live on the resources, some in SecurityData).

Cross-stack references are passed via **stack props** (session4 style), never
hardcoded. `AppEdgeAIStackProps` carries: `kmsKey: kms.IKey`, `ordersTable`,
`pendingRefundsTable: dynamodb.ITable`, `receiptsBucket: s3.IBucket`,
`paymentSecret: secretsmanager.ISecret`, `configParam: ssm.IStringParameter`,
`guardrailId: string`, `guardrailVersion: string`. Guardrail id/version are
read from the `CfnGuardrail`/`CfnGuardrailVersion` attributes
(`guardrail.attrGuardrailId`, `version.attrVersion`) and passed as strings so
the agent Lambda receives them as environment variables.

Both stacks share one `env = { region: 'ap-southeast-1', account:
process.env.CDK_DEFAULT_ACCOUNT }` from `bin/secure-assistant.ts`, exactly like
session4. Because the two stacks share a region/account and pass live token
references, CDK renders cross-stack `Export`/`Fn::ImportValue` automatically.

---

## VPC import (never create a VPC)

`lib/vpc-import.ts` exports a function returning `ec2.IVpc` via
`ec2.Vpc.fromVpcAttributes` — **not** `fromLookup` (NFR-4: no context lookup, so
synth needs no live AWS). This differs from session4, which imported via
`Fn.importValue` of CloudFormation exports; the requirement here gives explicit
literal ids, so we pass them directly as literals (clearer, and avoids depending
on export names that may not exist in a dummy synth account):

```ts
const vpc = ec2.Vpc.fromVpcAttributes(scope, 'ImportedVpc', {
  vpcId: 'vpc-01857e627d800ca7a',
  vpcCidrBlock: '10.1.0.0/16',
  availabilityZones: ['ap-southeast-1a', 'ap-southeast-1b', 'ap-southeast-1c'],
  privateSubnetIds: [
    'subnet-031c1ad1112e14559',  // 1a
    'subnet-000af0b0c27929d53',  // 1b
    'subnet-09bb34168e90ddd6f',  // 1c
  ],
  publicSubnetIds: [
    'subnet-05de990ce1677a9b8',  // 1a
    'subnet-029d8307a796a725c',  // 1b
    'subnet-03bb2e0d84b125eb0',  // 1c
  ],
  // Private subnets have a NAT route; the agent still reaches Bedrock ONLY via
  // the interface endpoint (see decision 4), not via NAT.
});
```

AZ order lines up positionally with subnet order (acceptance #5). The private
subnets are selected for Lambda VPC config and the interface endpoints via
`vpc.selectSubnets({ subnets: [ec2.Subnet.fromSubnetId(...)...] })` or by
passing the three `privateSubnetIds` through a `SubnetSelection` of explicit
`subnetFilters`. Edge case: `fromVpcAttributes` produces an `IVpc` with no
`isolatedSubnets`; constructs that default to private-with-egress still resolve
because `privateSubnetIds` are supplied. The synthesized template must contain
**no** `AWS::EC2::VPC` resource (acceptance #5) — a `cdk synth | grep` assertion
and a `Template.resourceCountIs('AWS::EC2::VPC', 0)` unit test enforce this.

---

## The six required decisions

### Decision 1 — WAF scope: REGIONAL on the API (chosen)

**Chosen: a `wafv2.CfnWebACL` with `scope: 'REGIONAL'` in ap-southeast-1,
associated to the API Gateway stage via `wafv2.CfnWebACLAssociation`.** The
alternative — a `CLOUDFRONT`-scoped WebACL — must be created in **us-east-1**
and attached to the distribution's `webAclId`. We reject it because this is a
single-region, single-account demo (NFR-1/NFR-4) and a CloudFront WebACL would
force a second stack pinned to `us-east-1`, adding cross-region deployment risk
with no teaching gain the regional ACL does not already deliver.

Tradeoff documented in the runbook (FR-37): a regional WebACL on the API filters
requests **at the API** after they traverse CloudFront, so CloudFront-edge
request volume is not filtered at the edge; a CloudFront WebACL would filter
earlier (closer to the viewer) and cover the whole distribution including the
S3/SPA path. For the demo's threat model (protect the mutating `/api/*`
surface), regional-on-the-API is sufficient and lower-risk to deploy. The
runbook states the rule explicitly: **a CloudFront-scoped WAF WebACL must be
created in us-east-1** (and is a sibling fact to the ACM us-east-1 rule).

WebACL contents (FR-11, acceptance #8):
- `AWSManagedRulesCommonRuleSet` (managed rule group, `vendorName: 'AWS'`,
  `overrideAction: { none: {} }` so the group's own actions apply).
- A **rate-based rule** with `action: { count: {} }` (COUNT mode, by design —
  not BLOCK; out-of-scope note in requirements), `limit: 2000`,
  `aggregateKeyType: 'IP'`.
- `visibilityConfig` with CloudWatch metrics enabled on the ACL and each rule.

### Decision 2 — Assistant packaging: Lambda **container image** (chosen)

**Chosen: `lambda.DockerImageFunction` built from `app/Dockerfile`
(`public.ecr.aws/lambda/python:3.12` base, `pip install -r requirements.txt`).**
`strands-agents` and `strands-agents-tools` are real PyPI dependencies (not
stdlib), so a plain `lambda.Function` with inline/asset code would need those
wheels bundled. The container image is the cleanest way to carry heavyweight,
possibly-native deps and is explicitly acceptable per the requirements.

Local-synth safety — the correct contract (resolves Finding 2 — MEDIUM; the
earlier draft wrongly claimed `cdk synth` shells out to `docker build` and that
`CDK_DOCKER=echo` is what makes synth safe): in `aws-cdk-lib@2.160.0`,
`lambda.DockerImageCode.fromImageAsset('../app', { ... })` at **synth** time
only runs `AssetStaging` (hashes the build context and copies the source into
`cdk.out`) and emits a Docker **image asset manifest** via
`stack.synthesizer.addDockerImageAsset(...)`. **It does not run `docker build`
at synth** — the build is deferred to **deploy** time by `cdk-assets`. The
`CDK_DOCKER` env var is consumed only by the `Code.fromAsset({ bundling })`
local-bundling path, which the agent Lambda does **not** use. So `cdk synth`
for the `DockerImageFunction` needs **no Docker** and performs no build, which
satisfies the local-only boundary directly. The real `docker build`/push
happens inside `deploy.sh` at deploy time (the orchestrator builds and pushes).
The two non-agent Lambdas (`refund_confirm`, `presign`) are plain
`lambda.Function` with `lambda.Code.fromAsset('app/refund_confirm')` /
`.../presign` (pure boto3, no heavy deps) so they synth with a simple zip asset
and no Docker.

> Implementation note for the builder: `CDK_DOCKER=echo` is kept in the
> verification command only as a defensive belt-and-suspenders note — it is
> **not** load-bearing, because synth does not build the image regardless. Do
> not build scaffolding (e.g. a context-flag stub-zip fallback) around a
> non-problem; if `cdk synth` ever fails for the image asset, the cause is asset
> *staging* (missing build context / Dockerfile path), not a Docker build.
> Ensure `app/` and `app/Dockerfile` exist so staging succeeds. The synthesized
> template for a deploy contains an `AWS::Lambda::Function` with
> `PackageType: Image`.

The agent Lambda runs **in the VPC private subnets** (`vpc`, `vpcSubnets:
{ subnets: [the three private subnets] }`, a dedicated `assistantSg`), timeout
60s, memory 1024 MB, `tracing: lambda.Tracing.ACTIVE`.

### Decision 3 — CloudFront origin shape: S3+OAC SPA + API-Gateway `/api/*` (chosen)

**Chosen: one `cloudfront.Distribution` with (a) a default behavior serving the
private SPA bucket via `origins.S3BucketOrigin.withOriginAccessControl(bucket)`
(OAC, L2, auto-wires the bucket policy to allow only this distribution), and (b)
an additional behavior for path pattern `/api/*` whose origin is the **API
Gateway REST API** via `origins.RestApiOrigin(api)`.** No custom domain, no
Route53, no ACM cert — `defaultRootObject: 'index.html'`, default CloudFront
domain + default `*.cloudfront.net` cert.

API Gateway REST (not HTTP API, not a Lambda Function URL) is chosen because:
(1) it supports native X-Ray tracing toggle (`tracingEnabled: true` on the
stage) which Act 4 requires on "API Gateway" specifically; (2) it integrates
cleanly as a `RestApiOrigin`; (3) a regional WAF `CfnWebACLAssociation` attaches
directly to a REST API stage ARN. A Lambda Function URL cannot carry a regional
WAF association and has weaker X-Ray story, so it is rejected.

Behaviors:
- Default (`/*`): S3+OAC origin, `viewerProtocolPolicy: REDIRECT_TO_HTTPS`,
  `cachePolicy: CACHING_OPTIMIZED`, `allowedMethods: GET/HEAD`.
- `/api/*`: `RestApiOrigin`, `REDIRECT_TO_HTTPS`, `cachePolicy:
  CACHING_DISABLED`, `originRequestPolicy: ALL_VIEWER_EXCEPT_HOST_HEADER`
  (REST API origins reject a forwarded `Host`), `allowedMethods: ALLOW_ALL`.

The SPA calls same-origin `"/api/..."` so the browser never sees the API GW
domain directly — but note the API stage URL is still reachable directly; the
regional WAF is what protects it. Edge: because `/api/*` strips the `/api`
prefix is NOT automatic in CloudFront, the REST API defines its resources under
a top-level `/api` resource (so the viewer path `/api/chat` maps to API resource
`/api/chat`); the design keeps the `/api` prefix in the API to avoid a
path-rewrite Lambda@Edge.

API routes (REST API, regional endpoint):
- `POST /api/chat` → assistant container Lambda (proxy integration).
- `POST /api/refunds/confirm` → `refund_confirm` Lambda.
- `GET  /api/receipts/{orderId}/url` → `presign` Lambda.

### Decision 4 — Private-subnet assistant reaches Bedrock ONLY via the interface endpoint (chosen)

**Chosen: an `ec2.InterfaceVpcEndpoint` for
`ec2.InterfaceVpcEndpointAwsService.BEDROCK_RUNTIME` in the three private
subnets, with a restrictive endpoint policy and a tight endpoint SG; plus a
second interface endpoint for `BEDROCK` (control plane) because `ApplyGuardrail`
and guardrail metadata resolve against the bedrock (not bedrock-runtime)
service.** `privateDnsEnabled: true` so the standard
`bedrock-runtime.ap-southeast-1.amazonaws.com` SDK endpoint resolves to the
endpoint ENIs inside the VPC.

Teaching point (made explicit in code comments + runbook): **"private subnet"
does not mean "private path to Bedrock."** A Lambda in a private subnet with a
NAT route would reach Bedrock over the public internet via NAT. Routing Bedrock
traffic over PrivateLink requires the interface endpoint; with `privateDns`
enabled the SDK call transparently uses it. We additionally **do not** rely on
NAT for Bedrock: the agent SG egress is scoped so that the only 443 path that
matters for Bedrock is to the endpoint SG.

Endpoint policy (non-wildcard, acceptance #13) — allows only:
`bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`,
`bedrock:ApplyGuardrail` on `Resource`:
- `arn:aws:bedrock:ap-southeast-1:875692608981:inference-profile/apac.amazon.nova-micro-v1:0`
- `arn:aws:bedrock:*::foundation-model/amazon.nova-micro-v1:0`
- the guardrail ARN (for `ApplyGuardrail`).

`bedrock:ApplyGuardrail` is included **defensively** (resolves Finding 7 — NIT):
with the guardrail applied **inline** via the `InvokeModel` request parameters
(the Strands `BedrockModel` guardrail-config path), the SDK may **not** issue a
separate `ApplyGuardrail` API call, so this grant can be unused at runtime. It
is kept because it is least-privilege-scoped to the guardrail ARN and makes the
policy robust if the wiring ever calls `ApplyGuardrail` directly; it is not
asserted as required by the chosen inline path.
Principal `*` (endpoint policies are resource-style; the identity policy on the
agent role is the second gate — see identity-vs-resource coverage).

Endpoint SG (`bedrockEndpointSg`): ingress TCP 443 **only** from `assistantSg`;
no egress rule needed beyond default. The agent SG (`assistantSg`) egress: 443
to `bedrockEndpointSg` (and 443 to the DynamoDB/Secrets/SSM gateway/interface
endpoints as applicable). Edge: `ec2.Port.tcp(443)` ingress is added via
`bedrockEndpointSg.addIngressRule(assistantSg, ec2.Port.tcp(443))`.

### Decision 5 — Guardrail application + invocation-logging masking ORDER (chosen)

**Chosen: a `bedrock.CfnGuardrail` (content filters Hate + Violence at HIGH; PII
entities ACCOUNT_NUMBER/US_SOCIAL_SECURITY_NUMBER/EMAIL set to MASK in both
input and output; one BLOCK example via a denied topic "legal-advice" and/or a
`BLOCK`-action PII entity; `blockedInputMessaging`/`blockedOutputsMessaging`
set), published as a `bedrock.CfnGuardrailVersion`. It is attached to the
Strands `BedrockModel` by passing `guardrail_id`, `guardrail_version`, and
`guardrail_trace='enabled'`. Bedrock invocation logging sends logs to a
CMK-encrypted CloudWatch Logs group and an S3 destination, both encrypted with
the demo CMK.**

Invocation-logging construct (resolves Finding 1 — HIGH): `aws-cdk-lib@2.160.0`
does **not** export a `CfnModelInvocationLoggingConfiguration` (the
`aws-bedrock` module only ships `CfnAgent/CfnAgentAlias/CfnDataSource/CfnFlow/
CfnFlowAlias/CfnFlowVersion/CfnGuardrail/CfnGuardrailVersion/CfnKnowledgeBase/
CfnPrompt/CfnPromptVersion` — verified by enumerating the module at the pinned
version). Using the non-existent construct would fail `tsc`/`cdk synth`.
Instead, provision it with an escape-hatch L1 `cdk.CfnResource` of the raw
CloudFormation type, with the exact `LoggingConfig` JSON shape pinned here:

```ts
new cdk.CfnResource(this, 'BedrockInvokeLogging', {
  type: 'AWS::Bedrock::ModelInvocationLoggingConfiguration',
  properties: {
    LoggingConfig: {
      CloudWatchConfig: {
        LogGroupName: invokeLogGroup.logGroupName,     // CMK-encrypted log group
        RoleArn: bedrockLoggingRole.roleArn,           // role Bedrock assumes to write
      },
      S3Config: {
        BucketName: invokeLogBucket.bucketName,        // SSE-KMS with the demo CMK
        KeyPrefix: 'bedrock/',
      },
      TextDataDeliveryEnabled: true,
      EmbeddingDataDeliveryEnabled: false,
      ImageDataDeliveryEnabled: false,
    },
  },
});
```

Both destinations are declared so the demo shows CloudWatch + S3 delivery; the
`invokeLogGroup` uses `encryptionKey: key` and `invokeLogBucket` uses
`BucketEncryption.KMS` with the demo CMK. This resource is a **per-account/region
singleton** (CloudFormation manages the single config), which `destroy.sh`
tears down explicitly before the stack delete so the CMK is not pinned. The
synth assertion matches on the raw type:
`template.hasResource('AWS::Bedrock::ModelInvocationLoggingConfiguration', ...)`.

Ordering — the "PII trap" (taught in runbook, enforced in code) — defense in
depth, stated in priority order (resolves Finding 4 — MEDIUM; the earlier draft
asserted a Bedrock runtime ordering guarantee that is outside the local-only
boundary and was not established):
1. **Tool/handler-layer PII masking is the primary, in-your-control defense.**
   `tools.py`/`pii.py` validate and mask account/SSN/email on every tool
   argument before anything is persisted or logged, so raw PII never reaches
   DynamoDB or application logs regardless of Bedrock behavior. This is the only
   layer that covers tool-call data (the guardrail does not — see Decision 6).
2. **CMK-encrypt the invocation-log destination** (CloudWatch log group + S3)
   so anything Bedrock captures is encrypted at rest under the demo CMK.
3. **Guardrail input/output PII masking is a best-effort model-channel control.**
   The guardrail is configured to MASK PII on the prompt/completion, but the
   exact relationship between the logged `InvokeModel` payload and the
   pre/post-guardrail content is a **runtime Bedrock behavior this design does
   not assert and does not verify here** (no runtime calls in the local-only
   boundary). Validate at deploy — it is listed in the Integration-only
   to-verify set. The teaching callout stays: **mask at the tool layer BEFORE
   invoke; never rely on logging to redact; encrypt the log destination.**
4. Because order matters at deploy, `deploy.sh` creates the guardrail + version
   (SecurityData) before the agent Lambda env is populated, and the invocation
   logging config is a singleton account/region resource created in
   SecurityData.

CMK key policy grants the Bedrock logging service principal
(`delivery.logs.amazonaws.com` / the Bedrock logging role) `kms:GenerateDataKey*`
+ `kms:Decrypt` on the log destination (edge: without this the logging config
creation fails at deploy; documented, not executed here).

### Decision 6 — Strands human-in-the-loop refund + guardrail tool-call blind spot (chosen)

**Chosen: `initiate_refund(order_id, amount)` is a `@tool` that moves NO money.
It validates+masks inputs, writes a `pending-refunds` DynamoDB item keyed by a
freshly generated `confirmationToken` (uuid4) with `status='PENDING_CONFIRMATION'`,
`ttl`, masked order reference, and amount, then returns a structured
PENDING-CONFIRMATION result to the model/SPA. A SEPARATE endpoint
`POST /api/refunds/confirm` (the `refund_confirm` Lambda, NOT a Strands tool)
is the only path that executes the refund: it looks up the token, verifies
`status==PENDING_CONFIRMATION` and not expired, flips it to `CONFIRMED`
(idempotently), and records the (simulated) payment action.** No real payment
call is made (the payment key is read from Secrets Manager to demonstrate the
grant, but the demo stubs the processor call).

Guardrail tool-call BLIND SPOT (FR-25, enforced in code + documented): the
Bedrock guardrail inspects the model's prompt and completion, but it does
**not** inspect or mask PII inside **tool-call arguments or tool results**. So a
model that passes a raw account number as a tool argument would hand raw PII to
`initiate_refund`. Mitigation: `tools.py` handlers call `pii.mask_pii(...)` and
`pii.validate(...)` **themselves** on every argument before persisting to
DynamoDB or logging, and never write a raw account/SSN/email into the
pending-refund record or any log line. `app/assistant/pii.py` holds pure
functions (`mask_account`, `mask_ssn`, `mask_email`, `mask_pii`, `validate`)
with code comments explaining the blind spot. This is unit-tested (acceptance
#19): assert a raw account number never appears in the written item or captured
log output.

**Token side-channel contract (resolves Finding 3 — MEDIUM).** A Strands
`@tool` return value is consumed by the **model**, which may paraphrase it, so
the confirmation token must **never** be surfaced to the SPA by parsing model
text. Instead the `/api/chat` handler captures the token from a request-scoped
side channel and builds the HTTP envelope from that captured value:

- Before invoking the agent, the handler creates a per-request mutable context
  object `req_ctx = {"pending_refunds": []}` and makes it available to the tool
  (bound via a closure/factory `make_initiate_refund(table, req_ctx)` so the
  `@tool` closes over `req_ctx`, or passed through Strands' per-invocation
  context). `initiate_refund` appends the record it just wrote —
  `{"token": <uuid4>, "amountMasked": ..., "orderMasked": ...}` — to
  `req_ctx["pending_refunds"]` in addition to returning its model-facing
  PENDING-CONFIRMATION result.
- After `agent(message)` returns, the handler reads `req_ctx["pending_refunds"]`
  (the authoritative, handler-captured values — not model output) and builds the
  response envelope `{"reply": <assistant text>, "pendingRefund": {"token",
  "amountMasked", "orderMasked"}}` from the most recent entry (or omits
  `pendingRefund` when the list is empty).
- The token is a server-generated uuid4 written to DynamoDB by the tool; the SPA
  only ever echoes it back to `/api/refunds/confirm`. The model never needs to
  reproduce the token verbatim. This contract is stated identically in the SPA
  section below so the two agree.

Strands wiring (FR-19, acceptance #16), in `app/assistant/handler.py`:
```python
from strands import Agent, tool
from strands.models import BedrockModel

model = BedrockModel(
    model_id="apac.amazon.nova-micro-v1:0",   # the apac. inference-profile id IS the model_id
    region_name="ap-southeast-1",
    # guardrail_id/guardrail_version/guardrail_trace are forwarded via **model_config
    # (not first-class __init__ params in strands-agents 1.23.0) and configure the
    # inline guardrail applied as part of the InvokeModel request.
    guardrail_id=os.environ["GUARDRAIL_ID"],
    guardrail_version=os.environ["GUARDRAIL_VERSION"],
    guardrail_trace="enabled",
)
agent = Agent(model=model, tools=[look_up_order, initiate_refund])
```
No Bedrock classic Agent, no AgentCore. The `boto3` Bedrock client inside Strands
transparently uses the VPC interface endpoint (private DNS).

---

## KMS CMK usage

One customer-managed `kms.Key` (`SecureAssistantKey`, `enableKeyRotation: true`,
`alias: 'alias/session5-secure-assistant'`, `removalPolicy: DESTROY` for demo)
in SecurityData encrypts:
- the **receipts S3 bucket** (`encryption: S3_MANAGED` → replaced with
  `BucketEncryption.KMS`, `encryptionKey: key`, `bucketKeyEnabled: true`);
- the **Bedrock invocation-log destination** — the CloudWatch log group
  (`encryptionKey: key`) and the S3 log bucket (`BucketEncryption.KMS`) targeted
  by the `AWS::Bedrock::ModelInvocationLoggingConfiguration` escape-hatch
  resource (Decision 5);
- both **DynamoDB tables** (`encryption:
  dynamodb.TableEncryption.CUSTOMER_MANAGED`, `encryptionKey: key`).

Key policy: root account admin; `grantEncryptDecrypt` to the agent role and the
`presign`/`refund_confirm` roles as needed; explicit grant to the Bedrock
logging delivery principal for the log destination. The SPA bucket uses
`S3_MANAGED` (no sensitive data; keeps OAC wiring simple), while the receipts
bucket uses the CMK (sensitive receipts).

---

## S3 buckets and the TLS-only DENY policy

- **SPA bucket** — `blockPublicAccess: BLOCK_ALL`, no public access; served only
  via CloudFront OAC. `BucketDeployment` uploads `spa/` static assets. A
  TLS-only deny statement is also attached (defense in depth).
- **Receipts bucket** — `blockPublicAccess: BLOCK_ALL`, CMK-encrypted, holds
  demo receipt objects (seeded by `deploy.sh`). It carries the **TLS-only DENY**
  resource policy (FR-14, acceptance #10):
```ts
receiptsBucket.addToResourcePolicy(new iam.PolicyStatement({
  sid: 'DenyInsecureTransport',
  effect: iam.Effect.DENY,
  principals: [new iam.AnyPrincipal()],
  actions: ['s3:*'],
  resources: [receiptsBucket.bucketArn, receiptsBucket.arnForObjects('*')],
  conditions: { Bool: { 'aws:SecureTransport': 'false' } },
}));
```
This is the **resource policy** half of the identity-vs-resource pairing: the
`presign` Lambda role has an **identity policy** granting `s3:GetObject` on
`receiptsBucket.arnForObjects('*')` (needed to generate a presigned URL whose
signature is valid), while the receipts bucket's **resource policy** denies all
non-TLS access and (optionally) scopes `s3:GetObject` to the presign role.
Acceptance #16/#11: at least one protected resource (the receipts bucket) has
both.

---

## IAM: least privilege, ABAC, identity-vs-resource

**Agent role** (acceptance #15) — identity policy grants, with explicit
resource ARNs and no broad wildcard beyond the foundation-model ARN form:
- `bedrock:InvokeModel` + `bedrock:InvokeModelWithResponseStream` +
  `bedrock:ApplyGuardrail` on BOTH
  `arn:aws:bedrock:ap-southeast-1:875692608981:inference-profile/apac.amazon.nova-micro-v1:0`
  AND `arn:aws:bedrock:*::foundation-model/amazon.nova-micro-v1:0` (the `*`
  region/account in the foundation-model ARN is the required AWS ARN form, not
  an over-grant), plus the guardrail ARN for `ApplyGuardrail` — the latter
  included **defensively** (the inline-guardrail wiring may not issue a separate
  `ApplyGuardrail` call; see Decision 4).
- DynamoDB RW scoped to the `orders` + `pending-refunds` table ARNs
  (`grantReadWriteData`).
- `secretsmanager:GetSecretValue` on the payment secret ARN only (FR-6).
- `ssm:GetParameter` on the config parameter ARN only (FR-7).
- `xray:PutTraceSegments` + `xray:PutTelemetryRecords` (X-Ray write).
- `kms:Decrypt`/`GenerateDataKey` on the CMK (for KMS-encrypted DynamoDB/
  receipts access).
- VPC ENI permissions come from the Lambda VPC managed policy.

**ABAC policy** (FR-15, acceptance #11) — a support-operator role (or the
`refund_confirm` role) carries a statement allowed only when the resource tag
equals the principal tag:
```ts
new iam.PolicyStatement({
  sid: 'AbacTagMatch',
  effect: iam.Effect.ALLOW,
  actions: ['dynamodb:GetItem', 'dynamodb:UpdateItem'],
  resources: [pendingRefundsTable.tableArn],
  conditions: {
    // IMPORTANT: single-quoted (non-template) string. `${aws:PrincipalTag/team}`
    // is an IAM policy variable that must reach the rendered policy VERBATIM.
    // A backtick template literal would make JS try to evaluate `aws:...`
    // (not a valid JS expression -> compile error / wrong value), so this MUST
    // NOT be a template literal. (resolves Finding 5 — MEDIUM)
    StringEquals: { 'aws:ResourceTag/team': '${aws:PrincipalTag/team}' },
  },
});
```
A synth assertion checks the rendered statement contains the literal string
`${aws:PrincipalTag/team}` (not an evaluated/empty value), guarding against an
accidental template-literal regression. The `pending-refunds` table and the
operator role are both tagged `team=support`
(via `cdk.Tags.of(...).add('team','support')`) so the condition resolves true
for the demo while illustrating the ABAC pattern. This is a teaching construct;
the functional refund path uses the direct scoped grant.

**Identity-vs-resource coverage summary** (FR-16): the receipts bucket (identity
grant on presign role + resource deny policy) and the Bedrock interface endpoint
(agent identity policy + endpoint resource policy) each demonstrate the pairing.

All roles use scoped actions and ARNs; no `Action: '*'` and no `Resource: '*'`
except the AWS-required foundation-model ARN wildcard form (acceptance #15,
NFR-3). `@aws-cdk/aws-iam:minimizePolicies` is already true in `cdk.json`.

---

## DynamoDB

- `orders` — PK `orderId` (S), on-demand (`PAY_PER_REQUEST`), CMK-encrypted,
  `removalPolicy: DESTROY`. Seeded with demo orders by `deploy.sh`.
- `pending-refunds` — PK `confirmationToken` (S), on-demand, CMK-encrypted, TTL
  attribute `ttl` enabled (pending refunds auto-expire), `removalPolicy:
  DESTROY`. Tagged `team=support` for the ABAC demo.

---

## Secrets Manager + SSM

- Payment-processor key in Secrets Manager (`generateSecretString`, like
  session4's payment secret), name `session5/payment-processor-key`. Agent role
  gets `GetSecretValue` on it only.
- SSM `StringParameter` `/session5/assistant/config` holding assistant config
  (JSON string: greeting, max refund amount, etc.). Agent role gets
  `GetParameter` on it only.

---

## Lambdas (Python 3.12)

- **assistant** (`app/assistant/handler.py`) — container-image Lambda, VPC
  private subnets, Strands agent. Patches X-Ray via `aws_xray_sdk` to
  instrument boto3 (Bedrock + DynamoDB) as **subsegments** (FR-28, acceptance
  #20): `from aws_xray_sdk.core import patch_all; patch_all()` plus explicit
  `xray_recorder.in_subsegment('bedrock-invoke')` / `'ddb-...'` wrappers around
  the Strands model call and tool DynamoDB writes. Entry: API GW proxy event →
  parse user message → `agent(message)` → return guardrail-safe reply + any
  pending-refund token/summary.
- **refund_confirm** (`app/refund_confirm/handler.py`) — zip Lambda, confirms
  the token, flips `pending-refunds` status, stubs payment, returns result.
- **presign** (`app/presign/handler.py`) — zip Lambda, generates a time-limited
  (`ExpiresIn=300`) presigned GET URL for `receipts/{orderId}.pdf`, validating
  `orderId` format first.

`app/assistant/pii.py` and `app/assistant/tools.py` are structured as **pure,
unit-testable functions** (NFR-6): masking/validation take plain args and return
values; DynamoDB access is injected (a `table` resource passed in) so tests use
a fake/moto-free stub. `requirements.txt` pins `strands-agents`,
`strands-agents-tools`, `boto3`, `aws-xray-sdk` (acceptance #17);
`dev-requirements.txt` pins `pytest`.

---

## Error handling (per fallible operation)

| Operation | Failure condition | Recoverable? | Caller receives | Logged? |
| --- | --- | --- | --- | --- |
| `POST /api/chat` body parse | missing/invalid JSON, empty message | recoverable | `400 {"error":"invalid request"}` | WARN, no PII |
| Bedrock invoke (Strands) | throttling / endpoint unreachable / model error | recoverable (surface friendly msg) | `502 {"error":"assistant unavailable"}` | ERROR with request id, no prompt PII |
| Guardrail BLOCK on input/output | content filter or blocked topic trips | expected, not an error | `200` with the guardrail's blocked message | INFO (guardrail trace), no raw PII |
| `initiate_refund` arg validation | malformed order id / non-numeric amount / amount over config max | recoverable | tool returns `{"status":"REJECTED","reason":...}` (masked) | WARN, masked |
| DynamoDB write (pending-refunds) | ConditionalCheckFailed / throttle | recoverable | retry once then `500 {"error":"could not create pending refund"}` | ERROR, token only (no PII) |
| `refund_confirm` token lookup | token not found / already confirmed / expired | recoverable | `404`/`409`/`410` respectively with a clear message | WARN |
| `presign` orderId validation | bad `orderId` format | recoverable | `400 {"error":"invalid order id"}` | WARN |
| `presign` S3 presign | KMS/permission error | recoverable | `500 {"error":"could not generate url"}` | ERROR |
| Secrets Manager read | access denied / not found | fatal to that request | `500` generic | ERROR, key name not value |

Principle: user-facing errors are generic and PII-free; detailed diagnostics go
to CloudWatch at the stated level with request ids but never raw account/SSN/
email. The guardrail BLOCK path is treated as a normal `200` outcome, not an
exception, so the SPA renders the guardrail's own refusal text.

---

## Input validation rules (per external input)

| Input | Required | Type / limit | On failure |
| --- | --- | --- | --- |
| chat `message` | required | string, 1–2000 chars | `400` |
| `order_id` (tool + presign) | required | matches `^ORD-[0-9]{6}$` | reject/`400` |
| refund `amount` | required | number > 0, ≤ `maxRefund` from SSM config | tool `REJECTED` |
| `confirmationToken` | required | uuid4 format | `400` |
| account number (if present in tool args) | optional | digits; **masked** before any persist/log | mask, never store raw |
| email / SSN in tool args | optional | masked before persist/log | mask |

Validation lives in the Lambda handlers/tools (the enforcement layer closest to
the data), because the guardrail does not see tool arguments (decision 6).

---

## Invariant ownership

- **No raw PII at rest or in logs** — owned by the **tool/handler layer**
  (`pii.py` masking), because the guardrail cannot see tool-call data. Enforced
  in code + unit test.
- **No money moves without explicit confirmation** — owned by the **split
  between `initiate_refund` (write-pending-only) and the `refund_confirm`
  endpoint (the only executor)**. The tool literally has no code path that
  settles a payment.
- **Bedrock reachable only via PrivateLink with least-privilege actions** —
  owned jointly by the **endpoint policy (resource)** and the **agent identity
  policy**; both must allow for a call to succeed.
- **Data encrypted at rest with the CMK** — owned by the **SecurityData stack**
  resource definitions (DynamoDB/receipts/log destination all reference the one
  key).
- **TLS-only to receipts** — owned by the **receipts bucket resource policy**.

---

## Observability (Act 4)

- **API Gateway**: `deployOptions.tracingEnabled: true` on the REST stage
  (acceptance #20) and `metricsEnabled`/access logging to a CMK-encryptable log
  group.
- **Lambdas**: `tracing: lambda.Tracing.ACTIVE` on all three functions; X-Ray
  write perms on the roles.
- **Subsegments**: the assistant instruments Bedrock and DynamoDB calls as X-Ray
  subsegments via `aws_xray_sdk` (`patch_all()` + explicit `in_subsegment`
  wrappers) so the trace map shows `chat → Bedrock` and `chat → DynamoDB`.
- CloudWatch is the natural home for the guardrail invocation logs and Lambda
  logs; the invocation-log destination is CMK-encrypted (decision 5).

---

## SPA shape (`spa/`)

Plain `index.html` + `app.js` + `styles.css`, no build. A single-page chat UI:
- A message list + input box that `POST`s `{message}` to `"/api/chat"`
  (same-origin via CloudFront `/api/*`).
- When a response includes a pending refund (`{pendingRefund:{token, amountMasked,
  orderMasked}}`), the SPA renders a **Confirm refund** button that `POST`s
  `{token}` to `"/api/refunds/confirm"` (FR-24, acceptance #21). The `token` in
  that envelope is produced by the `/api/chat` handler from its **request-scoped
  side channel** (`req_ctx["pending_refunds"]`), never parsed from model text —
  see the "Token side-channel contract" in Decision 6. The SPA treats `token`
  as an opaque string and only echoes it back to the confirm endpoint.
- A **Download receipt** control that `GET`s `"/api/receipts/{orderId}/url"`,
  then opens the returned presigned URL (FR-12/FR-31, acceptance #21).
- No secrets or API keys in the SPA; all auth-sensitive work is server-side.

---

## deploy.sh / destroy.sh

`deploy.sh` (`set -euo pipefail`, `AWS_REGION`/`AWS_DEFAULT_REGION=ap-southeast-1`,
numbered-step echo like session4):
1. Preflight tool check (`aws docker node npm python3 zip rsvg-convert`).
2. `cd infra && npm install && npx cdk bootstrap` (idempotent).
3. Build + push the assistant container image to the asset ECR repo (this is
   where the Docker build actually happens — never at synth), then
   `cdk deploy SecureAssistantSecurityData` first (CMK, tables, guardrail+version,
   secret, SSM, invocation logging), capturing the guardrail id/version outputs.
4. `cdk deploy SecureAssistantAppEdgeAI` (passes guardrail id/version context).
5. Seed demo data: put a couple of `orders` items, upload a sample receipt PDF
   to the receipts bucket, put the SSM config.
6. Resolve + print the CloudFront URL (the single entry point).

`destroy.sh` (`set -euo pipefail`, region pinned, **guarded**: prompts and
aborts unless the operator types `destroy` — acceptance #22). Teardown order
(KMS-dependent and bucket-emptying first, matching session4's pattern):
1. Confirmation prompt.
2. Empty the SPA + receipts buckets (all versions/delete markers).
3. Delete the Bedrock invocation-logging configuration
   (`AWS::Bedrock::ModelInvocationLoggingConfiguration`, an account/region
   singleton — removed with `aws bedrock delete-model-invocation-logging-configuration`
   or by letting the stack delete the escape-hatch resource first) so the CMK is
   not pinned.
4. `cdk destroy --all --force` (AppEdgeAI then SecurityData ordering handled by
   CDK dependency graph).
5. Sweep any leftover asset buckets / log groups.

Both scripts pass `bash -n` (acceptance #22). Neither is executed during
authoring.

---

## Diagram (`diagram/build_diagram.py`)

Reuses the session4 base64 icon-embed approach verbatim in structure
(`data_uri()` reads each `*_64.svg` and inlines it as
`data:image/svg+xml;base64,...`; zones, curved bezier `edge()`, numbered steps,
legend, drop-shadow filter). `ICON_BASE` points at
`/Users/erictole/demo/apcr-dva/aws-icons/Architecture-Service-Icons_04302026`.
It writes `architecture.svg` and the runbook/`deploy.sh` convert to PNG via
`rsvg-convert -o architecture.png architecture.svg` (FR-35, acceptance #23).

Verified icon paths (all exist in the icon set):
```
cloudfront : Arch_Networking-Content-Delivery/64/Arch_Amazon-CloudFront_64.svg
waf        : Arch_Security-Identity/64/Arch_AWS-WAF_64.svg
apigw      : Arch_Networking-Content-Delivery/64/Arch_Amazon-API-Gateway_64.svg
lambda     : Arch_Compute/64/Arch_AWS-Lambda_64.svg
bedrock    : Arch_Artificial-Intelligence/64/Arch_Amazon-Bedrock_64.svg
privatelink: Arch_Networking-Content-Delivery/64/Arch_AWS-PrivateLink_64.svg
vpc        : Arch_Networking-Content-Delivery/64/Arch_Amazon-Virtual-Private-Cloud_64.svg
dynamodb   : Arch_Databases/64/Arch_Amazon-DynamoDB_64.svg
s3         : Arch_Storage/64/Arch_Amazon-Simple-Storage-Service_64.svg
kms        : Arch_Security-Identity/64/Arch_AWS-Key-Management-Service_64.svg
secrets    : Arch_Security-Identity/64/Arch_AWS-Secrets-Manager_64.svg
iam        : Arch_Security-Identity/64/Arch_AWS-Identity-and-Access-Management_64.svg
ssm        : Arch_Management-Tools/64/Arch_AWS-Systems-Manager_64.svg
xray       : Arch_Developer-Tools/64/Arch_AWS-X-Ray_64.svg
cloudwatch : Arch_Management-Tools/64/Arch_Amazon-CloudWatch_64.svg
```
Diagram content: Viewer → CloudFront (default domain); CloudFront default
behavior → S3+OAC SPA bucket; CloudFront `/api/*` → WAF (regional) → API Gateway
→ assistant Lambda (in VPC private subnets); Lambda → PrivateLink
`bedrock-runtime` endpoint → Bedrock Nova Micro (guardrail attached); Lambda →
DynamoDB `orders`/`pending-refunds` (CMK); Lambda → Secrets Manager + SSM;
presign Lambda → receipts S3 (CMK, TLS-only); Bedrock invocation logs → CMK
CloudWatch; X-Ray across API GW + Lambdas; four act zones color-coded (network/
data, identity, Strands assistant, observability).

---

## Docs (README + FACILITATOR-RUNBOOK)

The runbook walks the **four acts** with **OLX** and **Clariant** talking points
and contains all seven required callouts (acceptance #24): ACM us-east-1 rule;
Nova inference-profile requirement; Strands guardrail wiring; guardrail
tool-call blind spot; human-in-the-loop refund; invocation-logging PII trap; the
Strands Agents SDK note — plus the regional-WAF-vs-us-east-1-CloudFront-WAF
tradeoff.

---

## Testability

- **Unit-testable (pytest, pure functions):** `pii.py` masking/validation;
  `tools.py` `initiate_refund` (asserts PENDING_CONFIRMATION, token written, no
  money, no raw PII) and the confirm flow; `presign` URL generation (botocore
  stub); input validators. Acceptance #18/#19 map directly to tests.
- **cdk-synth-assertable (`Template.fromStack`):** no `AWS::EC2::VPC`; two
  stacks; CloudFront with OAC S3 origin + `/api/*` behavior and no ACM cert;
  WebACL with managed common rule set + COUNT rate rule associated regionally;
  CMK on receipts + log destination + both tables; receipts TLS-only Deny; ABAC
  `ResourceTag==PrincipalTag`; `CfnGuardrail` filters/PII/BLOCK + published
  version; `bedrock-runtime` interface endpoint with non-wildcard policy + SG;
  the raw `AWS::Bedrock::ModelInvocationLoggingConfiguration` resource with a
  CMK-encrypted CloudWatch + S3 destination (asserted via `hasResource` on the
  raw CFN type, **not** an L1 class); agent role Bedrock dual-ARN grant; X-Ray
  on API GW + Lambda; the literal `${aws:PrincipalTag/team}` present verbatim in
  the rendered ABAC statement (not an evaluated/empty value).
- **Integration-only (NOT run here, documented):** live Bedrock/Guardrail
  invocation, CloudFront propagation, real presigned-URL fetch, WAF counting,
  and the Bedrock **guardrail-masking-vs-invocation-logging interaction** (does
  the logged `InvokeModel` payload reflect guardrail-redacted content?) — all
  require a live deploy and are explicitly out of the local verification
  boundary.

The design keeps every unit of behavior either a pure function or a synthesized
template assertion, so the whole thing is verifiable with the local-only command
set and no live AWS.

---

## Verification plan (local only)

1. `cd infra && npm install && npx tsc --noEmit` → no errors.
2. `cd infra && CDK_DEFAULT_ACCOUNT=111111111111 npx cdk synth` → `cdk.out`
   templates, no live calls. (Synth only **stages** the agent image build
   context and emits an image-asset manifest; it does **not** run `docker build`
   — that is deferred to deploy. `CDK_DOCKER=echo` may be exported as a
   defensive no-op but is not required for a safe synth.)
3. `python3 -m py_compile` on every `.py`.
4. `pytest` on `app/tests/`.
5. `cd diagram && python3 build_diagram.py && rsvg-convert -o architecture.png
   architecture.svg`.
6. `bash -n deploy.sh && bash -n destroy.sh`.
No `cdk deploy`, `docker push`, or Bedrock calls (acceptance #25).

---

## Responses to design review (revision pass)

Review verdict was `CHANGES_REQUESTED` (1 HIGH, 4 MEDIUM, 2 NIT). Every HIGH and
MEDIUM finding is resolved in this revision; both NITs are addressed. Changes
stay aligned with the original requirements (local-only verification, pinned
facts, the six required decisions).

- **Finding 1 (HIGH) — `CfnModelInvocationLoggingConfiguration` absent in
  `aws-cdk-lib@2.160.0`. RESOLVED.** Independently re-verified by enumerating
  the `aws-bedrock` `Cfn*` exports at the pinned version (no such construct).
  Decision 5 now provisions invocation logging via an escape-hatch
  `cdk.CfnResource` of type `AWS::Bedrock::ModelInvocationLoggingConfiguration`
  with the exact `LoggingConfig` JSON (CloudWatch + S3, both CMK-encrypted)
  pinned inline. The stack-split blurb, KMS section, destroy.sh teardown step,
  and the synth-assertion list were all updated to the raw CFN type and a
  `hasResource` assertion. (FR-26, acceptance #14)

- **Finding 2 (MEDIUM) — `CDK_DOCKER=echo` false premise. RESOLVED.** Decision 2
  now states the correct 2.160.0 behavior: `DockerImageCode.fromImageAsset`
  stages the build context and emits an image-asset manifest at synth and
  defers `docker build` to deploy via cdk-assets; `CDK_DOCKER` is only consumed
  by the `Code.fromAsset({ bundling })` path the agent Lambda does not use.
  `CDK_DOCKER=echo` is demoted to a non-load-bearing defensive note; the
  context-flag/stub-zip fallback is dropped. Verification plan step 2 updated to
  match. (NFR-1, NFR-4, acceptance #4, #25)

- **Finding 3 (MEDIUM) — token path to SPA underspecified. RESOLVED.** Decision 6
  adds an explicit "Token side-channel contract": the `/api/chat` handler
  captures the uuid4 token from a request-scoped `req_ctx["pending_refunds"]`
  side channel the tool appends to, and builds the response envelope from that
  captured value — never from parsing model output. The SPA section now
  references the same contract so the two agree. (FR-23, FR-24, acceptance #18,
  #21)

- **Finding 4 (MEDIUM) — unverified "mask-before-logging" ordering guarantee.
  RESOLVED.** Decision 5 drops the asserted runtime ordering guarantee and
  restates the PII trap as defense-in-depth in priority order: (1) tool/handler
  masking (in our control), (2) CMK-encrypt the log destination, (3) guardrail
  masking as best-effort whose interaction with invocation logging is NOT
  verified here and must be validated at deploy. That interaction is added to
  the Integration-only to-verify list. (FR-25, FR-26, NFR-3)

- **Finding 5 (MEDIUM) — ABAC `PrincipalTag` would not render as a policy
  variable. RESOLVED.** The IAM section now mandates a single-quoted
  (non-template) string so `${aws:PrincipalTag/team}` survives verbatim to the
  rendered policy, with a code comment explaining why a backtick template
  literal is forbidden, plus a synth assertion that the literal appears in the
  rendered statement. (FR-15, acceptance #11)

- **Finding 6 (NIT) — Strands version pin / `**model_config` forwarding.
  ADDRESSED.** The tech-stack table pins `strands-agents==1.23.0` (matching the
  verified installed version) and notes that `guardrail_id`/`guardrail_version`/
  `guardrail_trace` are forwarded through `**model_config`, not first-class
  `__init__` params. The wiring snippet carries a matching comment. (NFR-2,
  acceptance #16, #17)

- **Finding 7 (NIT) — `bedrock:ApplyGuardrail` may be unused by the inline
  wiring. ADDRESSED.** Both the endpoint policy (Decision 4) and the agent
  identity policy (IAM section) now annotate the `ApplyGuardrail` grant as
  included **defensively**; the inline-guardrail path may not issue a separate
  `ApplyGuardrail` call. The grant stays (least-privilege-scoped to the guardrail
  ARN). (FR-20, FR-22, acceptance #13, #15)
