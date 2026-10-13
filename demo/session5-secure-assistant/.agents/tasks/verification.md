# Verification — X-Ray tracing of assistant DynamoDB (and Bedrock) calls

## Iteration note

`.agents/tasks/review.json` was present but contained `{"verdict":"APPROVED"}` and
its companion `review.md` describes a *different, already-approved* task (the
receipt write-on-order / head-check-before-presign fix). Neither file contains
any finding about X-Ray tracing. The current source had **no** `traced` helper,
no `xray_entity` params on the tool factories, and `_build_agent` was still being
called BEFORE the `with xray_recorder.in_subsegment(...)` block — so the X-Ray
tracing fix had not yet been implemented. This pass implements it from scratch.

## Root cause (given, confirmed)

The assistant Lambda has Active tracing, the role has `xray:PutTraceSegments`,
and `aws-xray-sdk==2.14.0` calls `patch_all()` at module import before any boto3
client is created — so the Lambda's own segment is emitted and the Lambda node
appears. BUT the Strands Agent (`strands-agents==1.23.0`) runs tool calls on a
ThreadPoolExecutor and the model invocation on its own async event loop — OFF
the Lambda main thread. `aws-xray-sdk`'s default context is THREAD-LOCAL, so a
subsegment opened on the main thread is invisible to boto3 calls on worker
threads; those calls find no active segment on their thread, hit the default
`AWS_XRAY_CONTEXT_MISSING` behavior, and the subsegments are silently dropped.
That is why DynamoDB/Bedrock were missing while the Lambda node still appeared.

## Fix approach (option 2 — make off-thread calls attach to the Lambda trace)

1. **New `app/assistant/tracing.py`** with two guarded helpers:
   - `capture_entity()` → `xray_recorder.get_trace_entity()` on the MAIN thread
     (returns `None` when aws-xray-sdk is absent or there is no active entity).
   - `traced(name, parent_entity, fn, *args, **kwargs)` → when aws-xray-sdk is
     available AND `parent_entity` is non-None, it calls
     `xray_recorder.set_trace_entity(parent_entity)` on the current (worker)
     thread, then wraps `fn` in `xray_recorder.in_subsegment(name)`. Otherwise it
     is a plain pass-through that just calls `fn`. The `aws_xray_sdk` import is
     guarded exactly like the existing optional-import patterns, so the module
     imports and the pytest suite stays green WITHOUT aws-xray-sdk installed.

2. **Where the parent entity is captured (correctness):** in
   `app/assistant/handler.handler()` the agent build + invoke were MOVED INSIDE
   the `with xray_recorder.in_subsegment("bedrock-invoke"):` block, and
   `capture_entity()` is called there so the captured entity is the LIVE Lambda
   subsegment (non-None in the deployed Lambda), not `None`. The captured entity
   is threaded into `_build_agent(req_ctx, xray_entity=...)` and from there into
   every tool factory.

3. **Tool factories** (`app/assistant/tools.py`) each gained an optional
   `xray_entity=None` parameter (default preserves every existing call /
   signature):
   - `make_look_up_order` wraps the GetItem via `traced("ddb-get_item", ...)`.
   - `make_place_order` wraps the PutItem via `traced("ddb-put_item", ...)` and
     the receipt S3 put via `traced("s3-put_object", ...)`.
   - `make_initiate_refund` wraps the PutItem via `traced("ddb-put_item", ...)`.
   - `make_get_receipt_url` wraps the GetItem via `traced("ddb-get_item", ...)`
     and the S3 head via `traced("s3-head_object", ...)`.
   Both guard patterns (the `@tool` identity fallback and the defensive
   boto3/botocore references) are preserved.

4. **Env var (defense in depth):** `AWS_XRAY_CONTEXT_MISSING=LOG_ERROR` added to
   the assistant Lambda environment in `infra/lib/app-edge-ai-stack.ts` (all
   existing env vars kept intact: AWS_REGION_PINNED, GUARDRAIL_ID,
   GUARDRAIL_VERSION, NOVA_MODEL_ID, ORDERS_TABLE, PENDING_REFUNDS_TABLE,
   PAYMENT_SECRET_NAME, CONFIG_PARAM_NAME, RECEIPTS_BUCKET). So any residual
   off-thread call that still finds no segment logs a warning instead of raising.

5. **Bedrock:** no special wrapping was needed. Because the Strands model
   invocation ultimately uses the `patch_all()`-instrumented bedrock-runtime
   client and the parent entity is re-attached inside `bedrock-invoke`, the
   `bedrock-runtime ConverseStream` subsegment DOES appear as a downstream edge
   in the live traces (see evidence). Bedrock traces.

## Files changed

- `app/assistant/tracing.py` — **new** guarded `capture_entity()` + `traced()`.
- `app/assistant/handler.py` — import `capture_entity`; move agent build+invoke
  inside the active `bedrock-invoke` subsegment; capture the live entity there;
  thread `xray_entity` into `_build_agent` and all four tool factories.
- `app/assistant/tools.py` — add optional `xray_entity=None` to all four tool
  factories; wrap each DynamoDB / S3 boto3 call in `traced(...)`.
- `infra/lib/app-edge-ai-stack.ts` — add `AWS_XRAY_CONTEXT_MISSING: 'LOG_ERROR'`
  to the assistant Lambda environment (all other env vars untouched).
- `app/tests/test_tracing.py` — **new** tests for the no-xray degrade path.
- `app/tests/test_tools.py` — new test that all four factories accept
  `xray_entity=None` and still work.

## Build / test results

- `python3 -m py_compile $(find app -name '*.py')` → OK.
- `python3 -m pytest app/tests -q` → **58 passed** (was 53; +4 in test_tracing,
  +1 in test_tools). Still green WITHOUT strands/boto3/aws-xray-sdk installed.
- `cd infra && npx tsc --noEmit` → clean (exit 0).
- `cdk synth SecureAssistantAppEdgeAI` → OK; synthesized template shows
  `AWS_XRAY_CONTEXT_MISSING: LOG_ERROR` on the AssistantFn.
- `npm test` → only the **2 known pre-existing out-of-scope SecurityData**
  failures remain ("Bedrock Guardrail with full feature surface" and "raw Bedrock
  invocation-logging config on CMK-encrypted destinations"). All AppEdgeAI
  assertions pass, including "three Lambda functions have Active X-Ray tracing".

## Image rebuild / push / Lambda update

- `aws ecr get-login-password | docker login …` → Login Succeeded.
- `BUILDX_NO_DEFAULT_ATTESTATIONS=1 docker buildx build --platform linux/amd64
  --provenance=false --sbom=false -t …/session5-secure-assistant:latest --push app`
  → pushed.
- New digest: `sha256:e7472dc28672a4ec2e1a48ccf24f303bd6e1c143f93dc9bbc5df7a2ff0106f68`.
- Env var deployed via `cdk deploy SecureAssistantAppEdgeAI --exclusively
  --require-approval never` (the EarlyValidation hook did NOT block it; deploy
  succeeded ~43s). The `update-function-configuration` fallback was not needed.
- `aws lambda update-function-code … --image-uri …@<digest>` → InProgress, then
  `aws lambda wait function-updated` → done.
- `GetFunctionConfiguration` confirms: `AWS_XRAY_CONTEXT_MISSING=LOG_ERROR`,
  TracingConfig Mode=Active, State=Active, LastUpdateStatus=Successful, all
  original env vars present.

## LIVE TRACE EVIDENCE (the whole point)

Warmed the function, then drove two tool calls against
`https://cafe-nova.aws.yikyakyuk.com/api/chat`:

- `{"message":"look up order ORD-000123"}` → HTTP 200, reply carried real
  DynamoDB data (summary "1x Flat White, 1x Croissant", total $7.50, READY) →
  `look_up_order` → DynamoDB **GetItem**.
- `{"message":"order 1x Latte"}` → HTTP 200, `placedOrder.orderId=ORD-015114`,
  `receipt` object returned → `place_order` → DynamoDB **PutItem** + S3 put.

`aws xray get-trace-summaries` (last ~8 min) found 3 AssistantFn traces; 2 list
`AWS::DynamoDB::Table` (OrdersTable) — and one also `AWS::S3::Bucket` — plus
`bedrock-runtime` as downstream service ids (previously absent).

`aws xray batch-get-traces` segment documents confirm the subsegment tree now
nests the AWS calls UNDER the Lambda segment via our named subsegments:

Lookup trace `1-6acdb989-55e9ea0b40fd8ca428bb1791`:
```
AssistantFn (AWS::Lambda::Function)
└─ bedrock-invoke            (namespace local)
   ├─ bedrock-runtime        (namespace aws, op ConverseStream)
   └─ ddb-get_item           (namespace local)      ← our wrapper
      └─ DynamoDB            (namespace aws, op GetItem, table …OrdersTable…)  ← NOW PRESENT
```

Place-order trace `1-6acdb996-25865025525d10d50485365e`:
```
AssistantFn (AWS::Lambda::Function)
└─ bedrock-invoke            (namespace local)
   ├─ bedrock-runtime        (namespace aws, op ConverseStream)
   ├─ s3-put_object          (namespace local)  → S3 (aws, op PutObject)
   ├─ ddb-put_item           (namespace local)  → DynamoDB (aws, op PutItem, …OrdersTable…)
   ├─ s3-head_object         (namespace local)  → S3 (aws, op HeadObject)
   └─ ddb-get_item           (namespace local)  → DynamoDB (aws, op GetItem, …OrdersTable…)
```

**Confirmed DynamoDB subsegments present:** `ddb-get_item` → `DynamoDB GetItem`
and `ddb-put_item` → `DynamoDB PutItem`, both nested under the Lambda segment and
pointing at `SecureAssistantSecurityData-OrdersTable315BB997-13G3WOYNBZXJU`.
Baseline before the fix: no DynamoDB subsegment appeared on the assistant trace.

**Bedrock:** `bedrock-runtime` (op `ConverseStream`) appears as a subsegment and a
downstream service-map edge in both traces — Bedrock traces too.

## Regression

- `get_receipt_url` for ORD-015114 → `receipt` object returned; curl of the
  presigned URL → **HTTP 200, 798 bytes, body starts `%PDF-1.4`** (valid PDF).
- `GET https://cafe-nova.aws.yikyakyuk.com/` → **HTTP 200** (custom domain + WAF
  intact). Chat lookup / place-order / receipt flows all still function.

## Commit

- Single commit on `main` (NOT pushed), hash **`177d51c`**, message
  `fix(xray): trace assistant DynamoDB calls across Strands worker threads`
  (7 files changed). This note was then re-staged into the same commit via a
  single `--amend`, so the final hash may differ by this trailing line; resolve
  the exact hash via `git log -1 --oneline`. The stale `review.json`/`review.md`
  (prior receipt task) were intentionally left OUT of this commit.
