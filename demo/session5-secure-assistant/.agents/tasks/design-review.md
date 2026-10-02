# Design Review — Session 5 Secure Coffee-Shop AI Assistant

Reviewed: `design.md` against `requirements.md`, fresh (no authoring context).
Assumptions were verified against actual source where the design makes a factual
claim (CDK library at the pinned 2.160.0 in session4's `node_modules`, the
installed `strands-agents==1.23.0`, the AWS icon set, and session4 scripts).

Verdict basis is mechanical: count HIGH + MEDIUM findings. This review has
**0 HIGH** and **0 MEDIUM** (3 NITs). Verdict: **APPROVED**.

---

## Six required decisions — resolution check

1. **WAF scope** — RESOLVED. Decision 1 picks a `wafv2.CfnWebACL` `scope:
   'REGIONAL'` associated to the API Gateway stage via `CfnWebACLAssociation`,
   with the managed common rule set (`overrideAction: {none:{}}`) and a
   rate-based rule in `action:{count:{}}`. `CfnWebACLAssociation` exists in
   `aws-wafv2` at 2.160.0 (verified). Tradeoff documented for FR-37.
2. **Assistant packaging** — RESOLVED. Decision 2 picks a
   `lambda.DockerImageFunction` via `DockerImageCode.fromImageAsset`
   (verified present at 2.160.0) for the agent; plain zip `lambda.Function` for
   the two boto3-only Lambdas. The synth-safety contract is now stated correctly
   (see Verified Assumptions).
3. **CloudFront origin shape** — RESOLVED. Decision 3 picks one Distribution
   with an OAC S3 default origin (`S3BucketOrigin.withOriginAccessControl`,
   verified present) plus an `/api/*` behavior to `RestApiOrigin` (verified
   present), default CloudFront domain/cert, no ACM, no Route 53. The `/api`
   prefix-passthrough choice (no path rewrite) is specified.
4. **Private-subnet → Bedrock via interface endpoint** — RESOLVED. Decision 4
   uses `InterfaceVpcEndpointAwsService.BEDROCK_RUNTIME` plus `BEDROCK` (both
   verified present at 2.160.0) in the three private subnets, `privateDnsEnabled`,
   non-wildcard endpoint policy, tight SG (443 from `assistantSg` only). The
   "private subnet ≠ private path" teaching point is explicit.
5. **Guardrail application + invocation-logging masking order** — RESOLVED.
   Decision 5 restates the ordering as defense-in-depth in priority order
   (tool-layer masking primary; CMK-encrypt log destination; guardrail masking
   best-effort and explicitly NOT asserted/verified in the local boundary). The
   invocation-logging resource is provisioned via an escape-hatch
   `cdk.CfnResource` of type `AWS::Bedrock::ModelInvocationLoggingConfiguration`
   because no L1/L2 exists at 2.160.0 (verified).
6. **Strands pending-confirmation human-in-the-loop refund** — RESOLVED.
   Decision 6 keeps `initiate_refund` write-pending-only (uuid4 token,
   `PENDING_CONFIRMATION`, no money) and makes `POST /api/refunds/confirm` (a
   non-tool Lambda) the only executor. The token side-channel contract routes
   the token to the SPA via a request-scoped `req_ctx`, not model text.

## Pinned facts — honored

- Region `ap-southeast-1` pinned in `env`, both scripts, and resources — yes.
- VPC imported via `fromVpcAttributes` (not `fromLookup`, not created) with the
  six literal subnet ids and three AZs in order — yes; a
  `resourceCountIs('AWS::EC2::VPC', 0)` assertion backs acceptance #5.
- Nova via `apac.amazon.nova-micro-v1:0` inference profile only — yes, as
  `model_id`, with dual-ARN IAM grant (inference-profile + foundation-model).
- Strands SDK agent (`BedrockModel` from `strands.models`), no classic Agent /
  AgentCore — yes; wiring verified valid against installed 1.23.0.
- No custom domain — yes (default CloudFront domain/cert).
- Local-only verification — yes (synth with dummy account, py_compile, pytest,
  diagram, bash -n; no deploy/push/runtime calls).

---

## Findings

### NIT-1 — `look_up_order` tool is referenced but never specified
Decision 6 wires `Agent(model=model, tools=[look_up_order, initiate_refund])`
and FR-23 requires a read-only `look_up_order(order_id)`, but the design never
specifies this tool's behavior, return shape, validation, PII masking of its
output, or how it reads the `orders` table (the Lambda section details only
`pii.py`, `initiate_refund`, confirm, and presign). A builder is left to invent
the read tool, including whether its result is masked before returning to the
model (the guardrail does not see tool results — same blind spot as
`initiate_refund`).

CONCRETE FIX: add a short spec, e.g.:
```python
@tool
def look_up_order(order_id: str) -> dict:
    """Read-only order status lookup. order_id must match ^ORD-[0-9]{6}$."""
    if not ORDER_ID_RE.match(order_id):
        return {"status": "REJECTED", "reason": "invalid order id"}
    item = orders_table.get_item(Key={"orderId": order_id}).get("Item")
    if not item:
        return {"status": "NOT_FOUND"}
    # mask any PII before returning to the model (tool-result blind spot)
    return {"status": "OK", "order": pii.mask_pii(item)}
```
and state that the orders table is injected the same way as the refund tool
(factory/closure), so `look_up_order` is unit-testable like the others.

### NIT-2 — Factory name vs. tool symbol passed to `Agent` are inconsistent
Decision 6 says `initiate_refund` is produced by a factory
`make_initiate_refund(table, req_ctx)` that closes over `req_ctx`, but the
wiring snippet passes the bare symbol `initiate_refund` to `Agent(tools=[...])`.
As written the two do not line up — the thing passed to `Agent` must be the
closure returned by the factory, and `look_up_order` likely needs the same
treatment (it needs the orders table).

CONCRETE FIX: make the handler build the tools from the factories and pass those
instances, e.g.:
```python
initiate_refund = make_initiate_refund(pending_refunds_table, req_ctx)
look_up_order   = make_look_up_order(orders_table)
agent = Agent(model=model, tools=[look_up_order, initiate_refund])
```
Pick one pattern (factory/closure vs. Strands per-invocation context) and state
it once so `tools.py` and `handler.py` agree.

### NIT-3 — Private-subnet selection method is ambiguous and the primary option is risky
Decision 4 / VPC-import section offer two selection methods for the Lambda and
endpoints: `vpc.selectSubnets({ subnets: [ec2.Subnet.fromSubnetId(...)] })` OR a
`SubnetSelection` with `subnetFilters`. `Subnet.fromSubnetId` yields a subnet
whose `availabilityZone` is a dummy placeholder token (CDK fills `dummy1a`
etc.), which triggers CDK's "subnet has no AZ information" warning and can
misplace Lambda ENIs / endpoint ENIs across AZs. Because `fromVpcAttributes`
already populates `vpc.privateSubnets` from the supplied `privateSubnetIds` +
`availabilityZones`, the clean path is to select by those.

CONCRETE FIX: pick one method and prefer the AZ-aware one:
```ts
// Imported VPC already has privateSubnets populated with real AZs:
const vpcSubnets = { subnets: vpc.privateSubnets };            // or:
const vpcSubnets = { subnetType: ec2.SubnetType.PRIVATE_WITH_EGRESS };
```
Use `vpcSubnets` for both the agent Lambda and the two interface endpoints;
avoid `Subnet.fromSubnetId` for selection. State the single chosen method in the
design.

---

## Verified Assumptions (checked against source)

- **No `CfnModelInvocationLoggingConfiguration` at `aws-cdk-lib@2.160.0`** —
  CONFIRMED. Enumerated `aws-bedrock` Cfn classes:
  `CfnAgent, CfnAgentAlias, CfnDataSource, CfnFlow, CfnFlowAlias, CfnFlowVersion,
  CfnGuardrail, CfnGuardrailVersion, CfnKnowledgeBase, CfnPrompt, CfnPromptVersion`
  — exactly the design's list, and no invocation-logging construct. The
  escape-hatch `cdk.CfnResource` of the raw CFN type is the correct resolution.
- **`DockerImageCode.fromImageAsset` exists at 2.160.0** — CONFIRMED
  (`aws-lambda/lib/image-function.js`). The design's corrected synth-safety
  contract (synth stages the context + emits an image-asset manifest; the real
  `docker build` is deferred to deploy via cdk-assets; `CDK_DOCKER=echo` is a
  non-load-bearing note) is consistent with CDK's documented asset-staging
  behavior and the local-only boundary.
- **`S3BucketOrigin.withOriginAccessControl` and `RestApiOrigin` exist at
  2.160.0** — CONFIRMED (`aws-cloudfront-origins`). OAC + `/api/*` origin shape
  is feasible as written.
- **`InterfaceVpcEndpointAwsService.BEDROCK_RUNTIME` and `.BEDROCK` exist at
  2.160.0** — CONFIRMED (`aws-ec2/lib/vpc-endpoint.js`; also `BEDROCK_AGENT`,
  `BEDROCK_AGENT_RUNTIME`). Decision 4's two interface endpoints are buildable.
- **`CfnWebACLAssociation`, `OriginRequestPolicy.ALL_VIEWER_EXCEPT_HOST_HEADER`,
  `dynamodb.TableEncryption.CUSTOMER_MANAGED` exist at 2.160.0** — CONFIRMED.
- **`strands-agents==1.23.0` is installed and the `BedrockModel` wiring is
  valid** — CONFIRMED. `BedrockModel.__init__(*, region_name=..., **model_config:
  Unpack[BedrockConfig])`; `BedrockConfig` declares `model_id`, `guardrail_id`,
  `guardrail_version`, `guardrail_trace` (the trace Literal includes
  `"enabled"`). The design's exact snippet
  `BedrockModel(model_id='apac.amazon.nova-micro-v1:0', region_name=
  'ap-southeast-1', guardrail_id=..., guardrail_version=..., guardrail_trace=
  'enabled')` is accepted. The design's framing ("forwarded through
  `**model_config`, not first-class `__init__` params") is accurate — they are
  typed config keys, not positional params. (Note: `BedrockModel` also exposes an
  `endpoint_url` param for PrivateLink, but the design's reliance on private DNS
  means it is not required.)
- **AWS icon set + all 15 diagram icon paths exist** — CONFIRMED under
  `/Users/erictole/demo/apcr-dva/aws-icons/Architecture-Service-Icons_04302026`,
  matching session4's `ICON_BASE`. `build_diagram.py` reuse is feasible.
- **Session4 patterns the design mirrors** — CONFIRMED. `deploy.sh`/`destroy.sh`
  use `set -euo pipefail`, pin `ap-southeast-1`, and the destroy guard reads and
  aborts unless the operator types `destroy`. Session4 imports the VPC via
  `fromVpcAttributes` with `Fn.importValue` tokens; the design's switch to
  literal ids is explicitly justified by NFR-4 (offline synth) and is a sound,
  documented deviation, not a defect.

## Unverified / Wrong Assumptions

- **Guardrail-masking vs. invocation-logging interaction** — correctly left
  UNVERIFIED by the design itself. Whether the logged `InvokeModel` payload
  reflects guardrail-redacted content is a runtime Bedrock behavior outside the
  local-only boundary; Decision 5 no longer asserts it and places it on the
  Integration-only to-verify list. This is the right call — no finding.
- No design assumption was found to be factually **wrong** against source. The
  one previously-wrong claim (synth shells out to `docker build`; `CDK_DOCKER=
  echo` makes synth safe) has been corrected in this revision and now matches
  CDK's actual asset-staging behavior.
