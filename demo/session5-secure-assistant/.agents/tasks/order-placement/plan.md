# Implementation Plan — Order placement, recent-orders panel, live status (session5 secure assistant)

Source of truth: `./design.md` (approved). This plan sequences that design faithfully; it does not re-decide the architecture. All paths are relative to `/Users/erictole/demo/apcr-dva/demo/session5-secure-assistant` unless absolute.

## Environment facts discovered during exploration

- Python unit tests: `python3 -m pytest app/tests -q` (run from the demo root). Baseline is green: 16 passed. `conftest.py` puts `app/` on `sys.path` so each Lambda imports as a package (`assistant.*`, `presign.handler`, `refund_confirm.handler`, and — after this task — `orders_list.handler`).
- Compile check: `python3 -m py_compile $(find app -name '*.py')` from the demo root.
- Infra typecheck: `cd infra && npx tsc --noEmit` (clean on baseline).
- Infra template assertions: `cd infra && npm test` (`ts-node test/template.test.ts`). NOTE: on the current baseline this prints `1 assertion(s) FAILED` for `AWS::Bedrock::ModelInvocationLoggingConfiguration` — that resource is provisioned via `AwsCustomResource`, not that CFN type, so the assertion is PRE-EXISTING-BROKEN and unrelated to this task. Do not try to "fix" it. Treat the infra test as passing if the only failure is that one line. If you add template assertions for the GSI / orders Lambda, keep them green.
- `dev-requirements.txt` = pytest 8.3.2 + botocore 1.35.76 (no boto3, no strands). Tests MUST stay strands-free and boto3-free, using injected table stubs.
- No JS test runner exists for `spa/` (confirmed: no jest/vitest). SPA correctness is verified by the live deploy smoke flow, not CI.
- `@tool` in `app/assistant/tools.py` degrades to an identity decorator when strands is absent, so factory-built tools are plain callables under test.
- `app/presign/__init__.py` and `app/refund_confirm/__init__.py` are empty package markers; `app/orders_list/__init__.py` must mirror them.
- Fixed menu prices already shown in `spa/index.html`: Flat White $4.50, Latte $4.75, Croissant $3.00, Coco Cake $5.25 — these are the `MENU_PRICES` source of truth.
- CloudFront live URL: `https://d1o0u6nv8iqp83.cloudfront.net`. ECR repo: `session5-secure-assistant`. Stacks: `SecureAssistantSecurityData`, `SecureAssistantAppEdgeAI`.

## HARD INVARIANTS (preserve in every item)

1. Side-channel-only ids: `orderId` (and refund token) surface to the HTTP envelope ONLY from `req_ctx`, never parsed from model text.
2. PII masking before writes: `summary` goes through `pii.mask_pii` before `put_item`; no raw PII in items or logs.
3. Server-side total: `total` is computed from the fixed `MENU_PRICES`, never taken from model/user; unknown item or bad quantity fails closed (REJECTED, writes nothing).
4. Least-privilege read-only orders Lambda: a NEW dedicated role with `grantReadData` + `kmsKey.grantDecrypt` only; never reuse the assistant role; never add write actions; code never calls `Scan`.
5. Same-origin SPA calls: all SPA fetches are relative `/api/...`.
6. No weakening of Guardrail / WAF / KMS / PrivateLink / TLS / region: no changes to those constructs. Region `ap-southeast-1` pinned everywhere.
7. No model-id change: `apac.amazon.nova-micro-v1:0` stays.
8. Stored-XSS invariant: the recent-orders panel renders every order field via `textContent`/`createElement`, never `innerHTML`.
9. Assistant IAM/env UNCHANGED: `ORDERS_TABLE` env + `ordersTable.grantReadWriteData` + `kmsKey.grantEncryptDecrypt` already exist on the assistant; do NOT broaden the assistant role.

---

## Items

- [ ] 1. Add server-side pricing, status derivation, and the two order tools to `app/assistant/tools.py`.
      Add `MENU_PRICES` (flat white 4.50, latte 4.75, croissant 3.00, coco cake 5.25), `_TOKEN_RE`, pure `price_order(summary) -> (total, normalized_summary) | REJECTED-dict` (locked grammar/normalization/rejection rules from design §3), `PREPARING_AFTER=20` / `READY_AFTER=60` + pure `derive_status(created_at, now)` (half-open intervals §4), factory `make_place_order(orders_table, req_ctx)` → `@tool place_order(items)` (price → generate `ORD-NNNNNN` → `pii.mask_pii` summary → `Decimal(str(total))` → conditional `put_item(ConditionExpression="attribute_not_exists(orderId)")` with one regenerate-and-retry on `ConditionalCheckFailedException` via `ClientError` branch, append authoritative record to `req_ctx['placed_orders']`, return model-facing dict §6.1), and factory `make_look_up_order(orders_table)` → `@tool look_up_order(order_id)` doing a real `GetItem` with the single locked return contract (`status` ∈ OK/NOT_FOUND/REJECTED, `orderStatus` derived, §6.2). REMOVE the bare `look_up_order` stub. Keep everything strands-free/boto3-free (no top-level boto3/botocore import; reference `ClientError` defensively at runtime).
      Files: app/assistant/tools.py
      Verify: `python3 -m py_compile app/assistant/tools.py` succeeds; `python3 -m pytest app/tests/test_tools.py -q` — after item 8 adds the new tests they pass. Immediately after this item alone, `python3 -c "from assistant import tools; print(tools.MENU_PRICES)"` works and the bare `tools.look_up_order` symbol no longer exists.

- [ ] 2. Wire the real OrdersTable into both order tools and surface `placedOrder` in `app/assistant/handler.py`.
      Replace the import line with EXACTLY `from .tools import make_initiate_refund, make_look_up_order, make_place_order` (no bare `look_up_order` reference may remain). In `_build_agent`, build `orders_table = ddb.Table(os.environ["ORDERS_TABLE"])` and `pending_table = ddb.Table(os.environ["PENDING_REFUNDS_TABLE"])`, bind `make_look_up_order(orders_table)` and `make_place_order(orders_table, req_ctx)`, and pass all three tools to `Agent(...)`. In `handler()` init `req_ctx = {"pending_refunds": [], "placed_orders": []}`. In `build_response` add a `placedOrder` branch built from `req_ctx['placed_orders'][-1]` (never from reply text), per §8.
      Files: app/assistant/handler.py
      Verify: `python3 -c "import assistant.handler"` succeeds with strands+boto3 absent (proves no stale bare symbol and `_build_agent` is not run at import); `python3 -m pytest app/tests -q` green after item 8.

- [ ] 3. Add the `byCreatedAt` GSI to OrdersTable in `infra/lib/security-data-stack.ts`.
      Call `ordersTable.addGlobalSecondaryIndex({ indexName: 'byCreatedAt', partitionKey: {name:'gsiPk', type: STRING}, sortKey: {name:'createdAt', type: NUMBER}, projectionType: ALL })` with the single-hot-partition demo-simplification comment from §2. Do not change encryption, billing, keys, or removal policy.
      Files: infra/lib/security-data-stack.ts
      Verify: `cd infra && npx tsc --noEmit` clean; `npx cdk synth SecureAssistantSecurityData` shows a `GlobalSecondaryIndexes` block with `IndexName: byCreatedAt` on the Orders table.

- [ ] 4. Create the new read-only `orders_list` Lambda.
      Create `app/orders_list/__init__.py` (EMPTY, mirrors presign/refund_confirm) and `app/orders_list/handler.py` mirroring `app/presign/handler.py`: guarded `boto3` + guarded xray `patch_all`, `_response` helper, a MIRRORED identical `derive_status` + `PREPARING_AFTER`/`READY_AFTER` (must match tools.py exactly), pure `list_recent_orders(table, gsi_name, now, limit=10)` doing `Query(IndexName=gsi_name, KeyConditionExpression gsiPk="ORDER", ScanIndexForward=False, Limit=limit)` returning `{"orders":[...]}` newest-first with `total` coerced to float and derived `status`, skipping items missing `orderId`/`createdAt`; `handler(event,_ctx)` reads env `ORDERS_TABLE` + `ORDERS_GSI_NAME`, wraps the query in try/except returning `_response(500, {"error":"could not list orders"})`, else `_response(200, body)`. No request input is read. Never call `scan`.
      Files: app/orders_list/__init__.py, app/orders_list/handler.py
      Verify: `python3 -m py_compile app/orders_list/handler.py`; `python3 -c "from orders_list.handler import list_recent_orders, derive_status"` (with `app/` on path) works; tests from item 8 pass.

- [ ] 5. Wire `GET /api/orders` to the new Lambda in `infra/lib/app-edge-ai-stack.ts`.
      Add `ordersListFn` (PYTHON_3_12, `handler.handler`, `code: fromAsset(path.join(appRoot,'orders_list'))`, 30s/256MB, ACTIVE tracing, env `AWS_REGION_PINNED=REGION`, `ORDERS_TABLE=ordersTable.tableName`, `ORDERS_GSI_NAME='byCreatedAt'`). Grant least-privilege read-only: `ordersTable.grantReadData(role)` + `kmsKey.grantDecrypt(role)` on the function's OWN role; do NOT touch the assistant role. Add route `const orders = apiRoot.addResource('orders'); orders.addMethod('GET', new apigateway.LambdaIntegration(ordersListFn));`. Leave CloudFront/WAF/endpoints unchanged (`/api/*` already covers it).
      Files: infra/lib/app-edge-ai-stack.ts
      Verify: `cd infra && npx tsc --noEmit` clean; `npx cdk synth SecureAssistantAppEdgeAI` shows a new Lambda + an `AWS::ApiGateway::Resource` PathPart `orders` with a `GET` method; `cd infra && npm test` has no NEW failures (the single pre-existing invocation-logging failure may remain).

- [ ] 6. Add the Recent Orders panel to the SPA.
      In `spa/index.html` add `<section id="recent">` with `<ul id="recentOrders" aria-live="polite">` between the Menu section and the footer, and add `<script src="orders.js"></script>` immediately after the existing `ui.js` tag (no `defer`). Create `spa/orders.js`: top-level `window.refreshRecentOrders = refreshRecentOrders;`, `refreshRecentOrders()` → `fetch("/api/orders")` (same-origin relative) → pure `renderOrders(listEl, orders)` that builds rows with `createElement`/`textContent` ONLY (never `innerHTML`) with status badges; on error leave the last list in place; on `DOMContentLoaded` do one refresh then `setInterval(refreshRecentOrders, 10000)`. In `spa/app.js` `sendMessage`, after the existing `pendingRefund` block, add the additive `data.placedOrder` block that appends a sys line and calls `window.refreshRecentOrders()` if present — the ONLY edit to app.js; do not touch the five bound ids or refund/receipt flows. In `spa/styles.css` add `.orders-list`, `.order-row`, `.badge`/`.badge-received`/`.badge-preparing`/`.badge-ready` using the existing palette + `--ready:#2f9e5a`. No CDNs/external fonts/new JS deps.
      Files: spa/index.html, spa/orders.js, spa/app.js, spa/styles.css
      Verify: no JS test runner exists; verify by grep that `orders.js` has no `innerHTML` and the five ids (`log`,`chatForm`,`message`,`orderId`,`receiptBtn`) are still bound in `app.js`; full live verification in item 10.

- [ ] 7. Correct and extend the two seed items in `deploy.sh`.
      Compute `NOW=$(date +%s)` before the seed. Change the two `put-item` lines to include `gsiPk={"S":"ORDER"}`, `status={"S":"RECEIVED"}`, `createdAt={"N":"$((NOW-90))"}` for ORD-000123 and `$((NOW-30))` for ORD-000456, and CORRECT their totals to the menu: ORD-000123 `7.50`, ORD-000456 `9.50` (design §11.4). Keep the rest of deploy.sh unchanged.
      Files: deploy.sh
      Verify: `bash -n deploy.sh` passes; grep confirms both put-item payloads carry `gsiPk`, `createdAt`, `status`, and totals `7.50`/`9.50`.

- [ ] 8. Add/replace Python unit tests (strands-free, boto3-free, injected stubs).
      In `app/tests/test_tools.py`: REWRITE `test_look_up_order_validates` to build via `make_look_up_order(_StubTable(...))` (bad id rejects without a table call; found case returns `status=="OK"` with `orderStatus` in the valid set) per §12. Add `_StubTable` and `price_order`/`derive_status`/`make_place_order` tests (valid multi-item total+normalized summary; unknown item/bad qty/empty → REJECTED writing nothing; `place_order` writes an item with `gsiPk=="ORDER"`, `status=="RECEIVED"`, `total` a `Decimal`, appends to `placed_orders`; conditional-put collision stub triggers the single retry). Add `build_response` placedOrder tests in a suitable module (both blocks present; side-channel id used even when reply_text contains a different fake id). Add a handler import-safety test asserting `import assistant.handler` succeeds and `_build_agent` is not called at import. Create `app/tests/test_orders_list.py`: inject a table stub whose `query(**kwargs)` records kwargs + returns canned Items; assert it queries `IndexName=byCreatedAt`, `gsiPk=="ORDER"`, `ScanIndexForward=False`, `Limit=10`, never calls `scan`, shapes `{"orders":[...]}` with float `total` + derived `status`, empty Items → `{"orders":[]}`, and the stub raising → `handler` returns `{"error":"could not list orders"}`. Add a shared test asserting the two `derive_status` copies agree across a sweep.
      Files: app/tests/test_tools.py, app/tests/test_orders_list.py (+ a build_response/handler test file)
      Verify: `python3 -m pytest app/tests -q` all green (16 existing adapted/kept + new).

- [ ] 9. Deploy in the correct order (region pinned ap-southeast-1).
      Because `app/assistant/**` changed, FIRST rebuild+push the assistant image: `BUILDX_NO_DEFAULT_ATTESTATIONS=1 docker buildx build --platform linux/amd64 --provenance=false --sbom=false --push -t <acct>.dkr.ecr.ap-southeast-1.amazonaws.com/session5-secure-assistant:latest ./app` (ecr login first). THEN `cd infra` and `AWS_REGION=ap-southeast-1 AWS_DEFAULT_REGION=ap-southeast-1 npx cdk deploy SecureAssistantSecurityData --require-approval never` (GSI), THEN the same for `SecureAssistantAppEdgeAI`. Finally confirm/force the assistant Lambda to the new image digest (update-function-code to the pushed digest if the tag didn't roll). Do NOT run destroy.sh. Do NOT commit.
      Files: (none — deployment)
      Verify: both `cdk deploy` commands finish `UPDATE_COMPLETE`; `aws lambda get-function --function-name <assistant>` shows the new image digest; the GSI shows `ACTIVE` via `aws dynamodb describe-table`.

- [ ] 10. Live verification against the deployed stack.
      Against `https://d1o0u6nv8iqp83.cloudfront.net` and same-origin `/api/*`: (a) `GET /api/orders` returns the two seeded orders newest-first with corrected totals (9.50 then 7.50) and derived statuses (ORD-000456 PREPARING, ORD-000123 READY); (b) open the SPA, confirm the Recent Orders panel renders and polls ~10s; (c) place an order via chat (e.g. "2x Latte, 1x Croissant"), confirm the reply + a `placedOrder` envelope, an immediate panel refresh, and a new RECEIVED row that advances to PREPARING→READY with age; (d) look up that order id via chat and confirm status; (e) existing chat/refund/receipt flows still work; (f) all calls are same-origin relative.
      Files: (none — verification)
      Verify: each checklist item observed; capture the `/api/orders` JSON and a placed-order id as evidence.

## Notes / assumptions

- The pre-existing failing infra template assertion (`AWS::Bedrock::ModelInvocationLoggingConfiguration`) is out of scope and must not be "fixed"; treat infra tests as passing if it is the only failure.
- `derive_status` is intentionally duplicated between `tools.py` and `orders_list/handler.py` (separate bundles); keep thresholds/behavior identical (item 8 pins this with a cross-check test).
- Seed totals are corrected to the menu (the menu is the single source of truth); this is a required change, not optional.
