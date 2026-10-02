# Design Review — Order placement, recent-orders panel, live status (session5)

**Reviewer:** fresh-eyes design-review gate (no access to the context that produced the design).
**Design under review:** `.agents/tasks/order-placement/design.md`
**Verdict:** APPROVED (0 HIGH, 0 MEDIUM; 2 NIT)

This design went through a prior review round (its Section 13 answers ten earlier findings). I
re-verified every load-bearing claim directly against the source tree rather than trusting the
design's own summary. The design is unusually complete: item shape, GSI, pricing grammar, status
thresholds, tool/factory signatures, the side-channel key, PII masking, IAM, the SPA panel, and the
test seams are all pinned to a level a coder can implement without guessing. The two findings below
are documentation-accuracy nits that do not change the implementation a coder would produce if they
follow the design's own code snippets.

---

## Findings

### 1. [NIT] Section 9 asserts a guard in `app.js` that does not exist today

**Where:** Section 9, "Fetch logic" bullet on `window.refreshRecentOrders`:
> "(`app.js`'s `sendMessage` already guards with `if (window.refreshRecentOrders)`, so even if a
> message somehow fired first it is a safe no-op; pinning the top-level assignment removes the race.)"

**Problem:** I read `spa/app.js`. The current `sendMessage` has **no** reference to
`window.refreshRecentOrders` at all — the only post-reply handling is the `pendingRefund` block. The
guard the design describes as pre-existing is in fact introduced by the design's *own* new edit
(Section 9 "Coupling to chat"). The claim "already guards" is a wrong assumption about current code.

**Why it is only a NIT:** The design's own coupling snippet is
`if (data.placedOrder && data.placedOrder.orderId) { ...; if (window.refreshRecentOrders) window.refreshRecentOrders(); }`,
so a coder who implements the snippet verbatim gets the guard regardless. The false premise does not
produce wrong code; it only misdescribes the starting state.

**Concrete fix:** Reword to reflect that the guard is added by this change, e.g.:
> "The new coupling edit in `sendMessage` calls `refreshRecentOrders` through a
> `if (window.refreshRecentOrders)` guard, so even if the hook is somehow not yet assigned the call
> is a safe no-op; assigning the hook at top-level evaluation (not inside `DOMContentLoaded`) removes
> the race entirely."

### 2. [NIT] "No JS test runner exists in the repo" overlooks the infra template-test harness; new infra is left untested

**Where:** Section 12, final bullet:
> "**No JS test runner exists in the repo today** (confirmed: no jest/vitest config under `spa/` or
> `infra/` for the SPA) ..."

**Problem:** The parenthetical is narrowly true (there is no SPA test runner), but the repo *does*
ship an infra test harness: `infra/package.json` defines `"test": "ts-node --prefer-ts-exts
test/template.test.ts"`, and `infra/test/template.test.ts` asserts stack structure (table count,
Lambda count/tracing, CloudFront `/api/*`, WAF, guardrail, etc.). The design adds a GSI to
`OrdersTable`, a new `OrdersListFn` Lambda, and a `GET /api/orders` route, but says nothing about
`npm test` or extending `template.test.ts`.

I checked whether the design's additions *break* the existing assertions: they do not. The DynamoDB
table-count assertion is `resourceCountIs('AWS::DynamoDB::Table', 2)` (a GSI does not add a table),
and the Lambda assertion is `>= 3` Active-traced functions (a 4th Lambda still satisfies it). So the
suite stays green — this is a coverage gap, not a regression.

**Concrete fix:** (a) Correct the statement to "no JS/SPA unit-test runner exists; the infra harness
is `npm test` → `test/template.test.ts`." (b) Add two assertions to `template.test.ts` so the new
surface is pinned:
```ts
check('OrdersTable has the byCreatedAt GSI', () => {
  sec.hasResourceProperties('AWS::DynamoDB::Table', {
    GlobalSecondaryIndexes: Match.arrayWith([
      Match.objectLike({ IndexName: 'byCreatedAt' }),
    ]),
  });
});
check('an /api/orders GET method exists', () => {
  edge.hasResourceProperties('AWS::ApiGateway::Method', {
    HttpMethod: 'GET',
  });
});
```
and run `npm test` as part of verification alongside the Python unit tests.

---

## Verified Assumptions

Each item below was checked against the actual source, not the design's description of it.

1. **OrdersTable shape today.** `security-data-stack.ts` defines `OrdersTable` with **only**
   `partitionKey orderId:S`, `PAY_PER_REQUEST`, `CUSTOMER_MANAGED` CMK, no GSI. Matches Section 1/2.
2. **Assistant env + IAM already present.** `app-edge-ai-stack.ts` sets `ORDERS_TABLE:
   ordersTable.tableName` on the assistant Lambda and grants `ordersTable.grantReadWriteData(assistantRole)`
   + `kmsKey.grantEncryptDecrypt(assistantRole)`. Section 7's claim "no new assistant IAM / env needed,
   do not broaden the role" is correct.
3. **`apiRoot` exists.** `const apiRoot = api.root.addResource('api')` is present, so
   `apiRoot.addResource('orders')` in Section 10 is valid.
4. **`/api/*` is `CACHING_DISABLED`.** The CloudFront additional behavior for `/api/*` uses
   `CachePolicy.CACHING_DISABLED`, so `GET /api/orders` hits the origin fresh (Section 9 CloudFront note).
5. **SPA script order.** `spa/index.html` ends with `<script src="app.js">` then `<script src="ui.js">`
   (no `defer`); `spa/ui.js` exists. Section 9's LOCKED "insert `orders.js` immediately after `ui.js`"
   is accurate.
6. **Menu prices.** `spa/index.html` lists Flat White $4.50, Latte $4.75, Croissant $3.00, Coco Cake
   $5.25 — identical to the `MENU_PRICES` map in Section 3.
7. **Seed totals contradict the menu (justifies Section 11.4).** `deploy.sh` seeds `ORD-000123`
   `"1x Flat White, 1x Croissant"` with `total=12.50` and `ORD-000456` `"2x Latte"` with `total=9.00`,
   and writes only `orderId`/`summary`/`total` (no `gsiPk`/`createdAt`/`status`). The menu-correct
   values are `7.50` and `9.50`. The design's required seed correction + added attributes is justified
   and its corrected payloads are internally consistent with the thresholds (`NOW-90` → READY,
   `NOW-30` → PREPARING).
8. **`look_up_order` is a bare `@tool` stub today.** `tools.py` exports a module-level
   `look_up_order` returning a hardcoded dict; `handler.py` imports it bare via
   `from .tools import look_up_order, make_initiate_refund` and passes it to `Agent(... tools=[look_up_order, initiate_refund])`.
   Section 7's import-migration requirement (the HIGH it guards) is real and correctly specified.
9. **Existing test breaks without a rewrite.** `app/tests/test_tools.py::test_look_up_order_validates`
   calls `tools.look_up_order("ORD-000123")` / `tools.look_up_order("nope")`; once the bare symbol
   becomes a factory this fails at collection. Section 12's one-for-one rewrite is required and correct.
10. **Test harness imports zip Lambdas as packages.** `app/tests/conftest.py` puts `app/` on
    `sys.path`; `presign`/`refund_confirm` have empty `__init__.py`. Section 10's requirement for an
    empty `app/orders_list/__init__.py` (inert at runtime; deployed entrypoint stays `handler.handler`)
    is correct.
11. **presign is the right structural template.** `app/presign/handler.py` has guarded `boto3`,
    guarded `patch_all()`, a `_response(status, body)` helper, a pure injectable core, and a thin
    `handler`. Section 5/10's "mirror presign" is accurate.
12. **PII helpers exist.** `app/assistant/pii.py` provides `validate_order_id` (regex
    `^ORD-[0-9]{6}$`), `mask_pii`, and documents the tool-call blind spot. Sections 1/3/6 use these
    exactly. The server-normalized `summary` ("Nx Item" tokens) carries only 1–2 digit quantities, so
    the 10–12 digit `_ACCOUNT_RE` in `mask_pii` will not corrupt it.
13. **`@tool` degrades to identity without strands.** `tools.py` wraps the strands import in
    try/except so factory-built tools are plain callables in tests — the basis for the boto3-free /
    strands-free unit seams in Section 12.
14. **Locked invariants are untouched.** No proposed edit changes the model id
    (`apac.amazon.nova-micro-v1:0`), the guardrail config, the WAF (`CommonRuleSet` + COUNT rate rule),
    the KMS CMK, the Bedrock PrivateLink interface endpoints, the S3 TLS-only DENY policies, or the
    pinned `ap-southeast-1` region. The additions (GSI on OrdersTable, a new read-only Lambda + route,
    env on that new Lambda, SPA panel) are strictly additive.
15. **`addGlobalSecondaryIndex` is callable.** Inside `security-data-stack.ts` the local is a concrete
    `new dynamodb.Table(...)`, so `ordersTable.addGlobalSecondaryIndex(...)` compiles (the cross-stack
    `ITable` type does not block it because the call site is in the owning stack).

## Unverified / Wrong Assumptions

1. **WRONG — "`app.js`'s `sendMessage` already guards with `if (window.refreshRecentOrders)`"**
   (Section 9). No such guard exists in the current `spa/app.js`; it is introduced by this design's own
   edit. See Finding 1. Low impact because the design's snippet supplies the guard.
2. **IMPRECISE — "No JS test runner exists in the repo today"** (Section 12). True for the SPA, but the
   infra `npm test` harness (`test/template.test.ts`) exists and is not extended for the new GSI,
   Lambda, or route. See Finding 2. The existing assertions still pass with the additions.
3. **UNVERIFIABLE (runtime-only, acceptable) — strands `BedrockModel` forwards
   `guardrail_id`/`guardrail_version`/`guardrail_trace` through `**model_config`.** This is asserted in
   the *existing* `handler.py` comment and is unchanged by this design; it cannot be confirmed from the
   source tree (requires the installed `strands-agents==1.23.0` at runtime). Out of scope for this
   change — the design does not touch the model/guardrail wiring — so it is not a finding, only noted
   as not independently verified here.
4. **UNVERIFIED (environmental, out of scope) — `grantReadData` renders to `GetItem/Query/Scan/...` on
   `tableArn` and `tableArn/index/*`.** This is the standard CDK idiom and the design flags the Scan
   action is granted-but-unused (Section 10/11.7). Not re-synthesized here; it does not weaken the
   read-only, no-write posture the task requires.

---

## Verdict rationale

HIGH findings: 0. MEDIUM findings: 0. NIT findings: 2. Per the mechanical rule (any HIGH or MEDIUM →
CHANGES_REQUESTED; otherwise APPROVED), the verdict is **APPROVED**. The design pins every item the
task required — OrdersTable item shape and types, the `byCreatedAt` GSI (gsiPk:S / createdAt:N /
projection ALL) and the `ScanIndexForward=false, Limit=10` query, the server-side fixed price map and
locked token grammar, read-time status thresholds with write-time baseline `RECEIVED`, the
`GET /api/orders` response + error table, the `make_place_order` / `make_look_up_order` signatures and
the `req_ctx['placed_orders']` side channel (ids never parsed from model text), PII masking before
write, the read-only `orders_list` Lambda env + least-privilege IAM with the assistant grants
unchanged, the SPA recent-orders panel + 10s poll + `placedOrder` chat-envelope trigger, and the
strands-free / boto3-free unit seams. The two NITs are documentation-accuracy items that do not change
the resulting implementation and do not block.
