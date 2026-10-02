# Design — Order placement, recent-orders panel, and live status (session5 secure assistant)

## Overview

This extends the already-deployed session5 secure coffee-shop assistant so the storefront can
*place* orders (not just look them up and refund them), persist them to the existing CMK-encrypted
`OrdersTable`, surface the most recent orders on the storefront page, and show a live-looking status
that advances with age. It mirrors the patterns already in the repo exactly:

- A new Strands `@tool place_order` built by a factory `make_place_order(orders_table, req_ctx)`, in
  the same shape as `make_initiate_refund` — it validates/masks via `pii.py`, writes the item, and
  appends an authoritative record to a request-scoped side channel so `build_response` surfaces the
  placed order **without parsing model text**.
- `look_up_order` converted from today's hardcoded stub into a factory `make_look_up_order(orders_table)`
  that does a real `GetItem` on the orders table.
- A single-partition "latest" GSI on `OrdersTable` so recent orders are a `Query` (never a `Scan`).
- A new least-privilege, read-only plain-zip boto3 Lambda `app/orders_list/handler.py` behind
  `GET /api/orders`, mirroring `app/presign`.
- A storefront **Recent Orders** panel (outside the chat overlay) that polls `GET /api/orders` and
  refreshes immediately after a chat places an order.

The technology stack is locked by the existing demo and is **not** changed by this design: Python 3.12
Lambdas (zip for `orders_list`, container for the assistant), `strands-agents` + `BedrockModel` with
`apac.amazon.nova-micro-v1:0` and the inline Bedrock Guardrail, `boto3`/DynamoDB with a customer-managed
KMS CMK, AWS CDK (TypeScript, `aws-cdk-lib`) for infra, API Gateway REST + CloudFront + WAF, and
dependency-light vanilla JS/CSS for the SPA. Everything stays in `ap-southeast-1`. No new runtime, no
new framework, no CDN.

---

## 1. OrdersTable item shape

The table is defined today in `security-data-stack.ts` with **only** `partitionKey orderId:S`,
`PAY_PER_REQUEST`, `CUSTOMER_MANAGED` CMK encryption. Every write (the `place_order` tool and the
`deploy.sh` seed) MUST produce the following item so both `GetItem` (look-up) and the GSI `Query`
(recent orders) work:

| Attribute   | DynamoDB type | Written by                | Notes |
|-------------|---------------|---------------------------|-------|
| `orderId`   | `S` (PK)      | `place_order` / seed      | `ORD-NNNNNN`, 6 digits. Must satisfy `pii.validate_order_id`. |
| `summary`   | `S`          | `place_order` / seed      | Human-readable line items the model passes (e.g. `"1x Flat White, 1x Croissant"`). Masked through `pii.mask_pii` before persisting. |
| `total`     | `N`          | `place_order` (server)    | Computed **server-side** from the fixed menu (Section 3). Stored as a DynamoDB Number. Never model/user-supplied. |
| `status`    | `S`          | `place_order` / seed      | Persisted **baseline** `"RECEIVED"`. The live-looking status is derived at read time (Section 4); the stored value stays `RECEIVED`. |
| `createdAt` | `N`          | `place_order` / seed      | Epoch seconds (`int(time.time())`). Doubles as the GSI sort key — drives both recency ordering and derived status. |
| `gsiPk`     | `S`          | `place_order` / seed      | **Constant** `"ORDER"`. Partition key of the latest GSI (Section 2). Single hot partition — acceptable demo simplification; documented in a code comment. |

Notes:
- `summary` is the canonical attribute name used across the write (`place_order`), the read
  (`look_up_order`, `orders_list`), the `/api/chat` envelope, and the SPA — matching the seed items in
  `deploy.sh`, which already write `summary`. (The already-made decision wrote "summary/items"; this
  design **locks the name to `summary`** to match the existing seed and SPA. Flagged in Section 11.)
- No PII is expected in any attribute; `summary` is still routed through `pii.mask_pii` before the
  write, consistent with the refund tool's "mask before persist" discipline and the tool-call blind
  spot documented in `pii.py`.
- `total` is written as a Number. The boto3 DynamoDB **resource** `Table` requires `Decimal` for
  numeric attributes — see the test-seam note in Section 10 for how `place_order` builds the item.

---

## 2. GSI — the "latest" single-partition index

Add to `OrdersTable` in `security-data-stack.ts`:

- **Index name:** `byCreatedAt`
- **Partition key:** `gsiPk` (`S`) — always the constant string `"ORDER"`
- **Sort key:** `createdAt` (`N`)
- **Projection:** `ALL` (the recent-orders response needs `summary`, `total`, `status`, `createdAt`).

CDK:

```ts
ordersTable.addGlobalSecondaryIndex({
  indexName: 'byCreatedAt',
  // Single constant partition ("ORDER") → one hot partition. This is an
  // ACCEPTABLE DEMO SIMPLIFICATION so recent orders is a Query (ScanIndexForward
  // =false, Limit 10), never a Scan. Do NOT generalise the PK for the demo.
  partitionKey: { name: 'gsiPk', type: dynamodb.AttributeType.STRING },
  sortKey: { name: 'createdAt', type: dynamodb.AttributeType.NUMBER },
  projectionType: dynamodb.ProjectionType.ALL,
});
```

Recent-orders query (in `orders_list`): `Query` on `IndexName=byCreatedAt`,
`KeyConditionExpression = gsiPk = "ORDER"`, `ScanIndexForward=False`, `Limit=10`. This returns the
newest 10 items directly, newest-first. **No `Scan` fallback** — if the query fails the Lambda returns
an error (Section 5), it does not scan the base table.

PAY_PER_REQUEST billing applies to the GSI automatically (inherited). No throughput config needed.

---

## 3. Fixed in-code menu price map (server-side totals)

`total` is **never** taken from the model or the user. `place_order` computes it from a small fixed
map that lives in `app/assistant/tools.py` (so it is pure and unit-testable without AWS). Prices match
the storefront menu in `spa/index.html`:

```python
# Fixed menu (USD). The SERVER-SIDE source of truth for order totals. The model
# NEVER supplies a price — it only names items; the tool prices them from here.
MENU_PRICES = {
    "flat white": 4.50,
    "latte": 4.75,
    "croissant": 3.00,
    "coco cake": 5.25,
}
```

Pricing contract for `place_order`:
- The model passes a `summary` string of the form `"<qty>x <item>, <qty>x <item>, ..."` (e.g.
  `"2x Latte, 1x Croissant"`). A pure helper `price_order(summary) -> (total, normalized_summary)`:
  1. Splits on commas, trims each token.
  2. Parses an optional leading quantity, then the item name, per the **locked token grammar** below.
  3. Normalizes the item name, then looks it up against `MENU_PRICES`.
  4. Sums `qty * price`. Rounds the total to 2 decimals.

- **Locked token grammar** (so the coder does not guess, and the server-authoritative pricing boundary
  is deterministic). Each comma-separated token is parsed with this regex:

  ```python
  import re
  # optional "<INT> x" / "<INT>x" (x or X, any surrounding whitespace), then the item name.
  _TOKEN_RE = re.compile(r"^\s*(?:(\d+)\s*[xX]\s*)?(.+?)\s*$")
  ```
  - The quantity group is **optional**; the `x`/`X` separator does **not** require a surrounding space,
    so both `"2x Latte"` and `"2xLatte"` parse to `qty=2, raw_item="Latte"`. A bare `"Latte"` parses to
    `qty=1, raw_item="Latte"`.
  - **Item-name normalization (locked):** `item_key = re.sub(r"\s+", " ", raw_item.strip()).lower()`.
    This trims, collapses any internal whitespace run (e.g. `"flat  white"` → `"flat white"`) to a
    single space, and lower-cases before the `MENU_PRICES` lookup. `MENU_PRICES` keys are already the
    lower-cased canonical names.
  - **Plurals are NOT accepted.** Only exact menu names (after normalization) match; `"lattes"`,
    `"croissants"`, etc. are treated as unknown menu items and rejected (fail closed — see below). The
    `place_order` docstring instructs the model to use exact singular menu names, so this is the model's
    contract, not a parser guess.
  - **`normalized_summary` reconstruction:** for each accepted token, re-emit
    `f"{qty}x {canonical_display}"` where `canonical_display` is the menu's display name derived from
    the matched key (title-cased: `"flat white"` → `"Flat White"`). Tokens are joined with `", "`. This
    makes the stored/echoed `summary` fully server-controlled, independent of the model's exact
    phrasing or casing.

- **Validation on failure (locked rules):**
  - Empty summary, or a summary with **no** recognizable menu items → the tool returns
    `{"status": "REJECTED", "reason": "no recognizable menu items"}` and writes **nothing**.
  - Any token naming an item **not** in `MENU_PRICES` → reject the whole order
    `{"status": "REJECTED", "reason": "unknown menu item: <name>"}` (fail closed; do not silently
    drop or zero-price an unknown item — never trust a model-supplied item we cannot price).
  - A quantity that is non-numeric, `<= 0`, or `> 20` → reject
    `{"status": "REJECTED", "reason": "invalid quantity"}` (upper bound keeps a demo order sane).
  - A computed `total <= 0` → reject `{"status": "REJECTED", "reason": "empty order"}`.
- A rejected order appends **nothing** to the side channel and writes **nothing** to DynamoDB.

`normalized_summary` (the canonicalized `"Nx Item"` list rebuilt from parsed tokens) is what gets
masked and stored as `summary`, so the persisted/echoed text is server-controlled, not raw model text.

---

## 4. Status age thresholds (read-time derived status)

There is **no** background worker. Status is a pure function of age at read time, exactly like
session4's `status_for(created_at, now)` (`demo/session4-coffee-ship/container/app.py`). We reuse that
pattern but with the session5 status labels and short thresholds so a facilitator sees movement within
a single session:

```python
# Read-time derived status. DEMO SIMPLIFICATION: there is no worker flipping
# rows; status is a pure function of age so a facilitator sees RECEIVED ->
# PREPARING -> READY within one session. Stored baseline stays "RECEIVED".
PREPARING_AFTER = 20   # seconds
READY_AFTER     = 60   # seconds

def derive_status(created_at: int, now: int) -> str:
    elapsed = int(now) - int(created_at)
    if elapsed < PREPARING_AFTER:
        return "RECEIVED"
    if elapsed < READY_AFTER:
        return "PREPARING"
    return "READY"
```

- Thresholds, written as **half-open intervals** so the boundary contract is unambiguous and matches
  the `elapsed < THRESHOLD` code exactly: `[0, 20)` s → `RECEIVED`, `[20, 60)` s → `PREPARING`,
  `[60, ∞)` s → `READY`. In particular `elapsed == 60` → `READY` (not PREPARING). (The already-made
  decision suggested 60/180s "tune to taste, keep short". 20/60s is chosen so all three states are
  visible comfortably inside a short demo window while the SPA polls every ~10s. These are easy to
  retune — single constants. The Section 12 boundary tests pin 19→RECEIVED, 20→PREPARING,
  59→PREPARING, 60→READY.)
- `derive_status` is the single source of truth, used by **both** `look_up_order` (the tool) and the
  `orders_list` Lambda. It lives where each needs it with the **same** thresholds. To avoid drift,
  put the canonical copy in `app/assistant/tools.py` and a mirrored, identical pure copy in
  `app/orders_list/handler.py` (the zip Lambda cannot import the assistant package). The constants and
  behavior MUST stay identical; both carry the same comment. (Mirroring is intentional — the two
  Lambdas ship as independent bundles; see Section 11 flag.)
- The derived status is a **presentation** detail. The stored `status` attribute remains `"RECEIVED"`;
  nothing updates the row after creation (orders are immutable, same as session4).

---

## 5. `GET /api/orders` — response shape and error cases

New plain-zip boto3 Lambda `app/orders_list/handler.py`, wired as `GET /api/orders` under `apiRoot`.
Mirrors `app/presign/handler.py` (guarded boto3 import, X-Ray `patch_all`, pure injectable core, thin
`handler`).

**Success (200):**

```json
{
  "orders": [
    { "orderId": "ORD-000456", "summary": "2x Latte", "total": 9.50, "status": "PREPARING", "createdAt": 1716900120 },
    { "orderId": "ORD-000123", "summary": "1x Flat White, 1x Croissant", "total": 7.50, "status": "READY", "createdAt": 1716900000 }
  ]
}
```

(Totals above match `MENU_PRICES`: `2 × 4.75 = 9.50` and `4.50 + 3.00 = 7.50`. Newest-first ordering
puts the larger `createdAt` first.)

- Up to 10 items, **newest-first** (from the `byCreatedAt` query with `ScanIndexForward=False`).
- `status` is the **derived** status (`derive_status(createdAt, now)`), not the stored baseline.
- `total` is emitted as a JSON number (coerce the DynamoDB `Decimal`/string to `float` in the Lambda).
- `createdAt` is an integer epoch second.
- Empty table → `{"orders": []}` with 200 (not an error).

**Pure core signature** (unit-testable with an injected table stub + injected `now`):

```python
def list_recent_orders(table, gsi_name, now, limit=10) -> dict:
    """Query the latest GSI newest-first and shape the public response.
    Returns {"orders": [...]} ; raises nothing for an empty result."""
```

**Error cases (locked):**

| Condition | HTTP | Body | Logged? |
|-----------|------|------|---------|
| DynamoDB `Query` raises (throttle, access denied, GSI missing) | `500` | `{"error": "could not list orders"}` | Yes — exception caught in `handler`, generic message only (no table name, no stack, no item data in the client body); X-Ray subsegment captures the trace. Recoverable from the client's view: the SPA keeps its last-rendered list and retries on the next poll. |
| Method/path other than `GET /api/orders` | n/a | — | API Gateway rejects before Lambda (no route). |
| Malformed/garbage query string | `200` | normal result | No input is read from the request — there are **no** request parameters; the endpoint is parameterless. Any query string is ignored. |

The endpoint takes **no** client input (no path/query/body params), so there is no request-side
validation to perform. This is deliberate: it keeps the surface minimal and removes an injection
vector. Validation that matters is on the **data** read back: coerce `total` to float defensively and
skip any item missing `orderId`/`createdAt` rather than emitting a malformed record.

---

## 6. Tool signatures + `req_ctx` keys

### 6.1 `place_order` (new)

```python
def make_place_order(orders_table, req_ctx):
    """Factory → @tool place_order, bound to the real OrdersTable + the request
    side channel. Mirrors make_initiate_refund."""

    @tool
    def place_order(items: str) -> dict:
        """Place a coffee-shop order. `items` is a comma-separated list like
        '2x Latte, 1x Croissant'. The server prices it from the fixed menu;
        prices are NEVER taken from this call."""
```

Behavior (locked):
1. `price_order(items)` → `(total, normalized_summary)` or a REJECTED dict (Section 3). On reject,
   return the dict; write nothing; append nothing.
2. Generate `order_id = "ORD-" + "".join(6 random digits)`. Use `random.randint(0, 999999)` zero-padded
   to 6 (`f"ORD-{n:06d}"`). Assert it passes `pii.validate_order_id` (regex `^ORD-[0-9]{6}$`) before
   use — the 6-digit zero-padded form always matches.
3. `summary = pii.mask_pii(normalized_summary)`.
4. `created_at = int(time.time())`.
5. `item = {orderId, summary, total: Decimal(str(total)), status: "RECEIVED", createdAt, gsiPk: "ORDER"}`.
   Write it with a **no-clobber condition** to remove the only data-loss path:
   `orders_table.put_item(Item=item, ConditionExpression="attribute_not_exists(orderId)")`. On a
   `ConditionalCheckFailedException` (the ~1-in-10^6 id collision), **regenerate the id once and retry**
   the conditional put; if the single retry also collides, return
   `{"status": "REJECTED", "reason": "could not allocate order id"}` and append nothing. The retry
   logic lives in the factory so it is covered by the injected-table-stub unit test (the stub can raise
   a `ConditionalCheckFailedException`-shaped error on the first call). The exception class is
   referenced defensively: catch `botocore.exceptions.ClientError` and branch on
   `err.response["Error"]["Code"] == "ConditionalCheckFailedException"` at runtime; in tests the stub
   raises a small fake with the same `.response` shape so no botocore import is needed to exercise the
   retry.
6. Append the authoritative record to the side channel:
   `req_ctx.setdefault("placed_orders", []).append({"orderId": order_id, "summary": summary, "total": total, "status": "RECEIVED"})`.
7. Return a model-facing dict `{"status": "RECEIVED", "orderId": order_id, "summary": summary, "total": total}`.

The `orderId` surfaced to the HTTP envelope comes from `req_ctx["placed_orders"]`, **never** parsed
from the model's reply — identical to how `pending_refunds` works today.

### 6.2 `look_up_order` (made real)

```python
def make_look_up_order(orders_table):
    """Factory → @tool look_up_order, bound to the real OrdersTable. Replaces
    the hardcoded stub. Read-only GetItem."""

    @tool
    def look_up_order(order_id: str) -> dict:
        """Look up an order by id (ORD-NNNNNN). Read-only."""
```

Behavior (locked):
1. `if not pii.validate_order_id(order_id): return {"status": "REJECTED", "reason": "invalid order id format"}` (unchanged).
2. `got = orders_table.get_item(Key={"orderId": order_id})`; `item = got.get("Item")`.
3. Not found → `{"status": "NOT_FOUND", "orderId": order_id}` (clean, no leak).
4. Found → the **single locked return shape** below.

**Locked `look_up_order` return contract** — there is exactly ONE shape; `status` is the tool-call
outcome and `orderStatus` is the derived order lifecycle. They never collapse into one key:

```python
# REJECTED (bad id, no table call):
{"status": "REJECTED", "reason": "invalid order id format"}

# NOT_FOUND (table returned no Item):
{"status": "NOT_FOUND", "orderId": order_id}

# OK (found): LOCKED shape
{"status": "OK",
 "orderId": order_id,
 "summary": item["summary"],
 "total": float(item["total"]),
 "orderStatus": derive_status(int(item["createdAt"]), int(time.time())),
 "createdAt": int(item["createdAt"])}
```

- Top-level `status` ∈ `{"OK", "NOT_FOUND", "REJECTED"}` — the outcome of the tool call.
- `orderStatus` ∈ `{"RECEIVED", "PREPARING", "READY"}` — the **derived** live lifecycle from
  `derive_status(createdAt, now)` (Section 4), so the model can tell the customer "it's being prepared".
- There is **no** `status_live` key and **no** second status alias. The already-made decision listed the
  return fields as `{orderId, summary, total, status, createdAt}`; this design renames the lifecycle
  field to `orderStatus` precisely because the tool-call envelope already owns the top-level `status`
  name. See the flag in Section 11.2.

`look_up_order` reads but never writes, and masks nothing on the way out beyond what the handler
already does (`pii.mask_pii(str(result))` is applied to the final agent text in `handler.py`).

### 6.3 `req_ctx` keys (locked)

| Key | Owner | Shape | Consumed by |
|-----|-------|-------|-------------|
| `pending_refunds` | `initiate_refund` (existing) | `[{token, amountMasked, orderMasked}]` | `build_response` → `pendingRefund` |
| `placed_orders`   | `place_order` (new)          | `[{orderId, summary, total, status}]` | `build_response` → `placedOrder` |

Both are initialized as empty lists in `handler.handler`:
`req_ctx = {"pending_refunds": [], "placed_orders": []}`.

---

## 7. handler.py wiring changes

`_build_agent(req_ctx)` currently builds **one** table from `PENDING_REFUNDS_TABLE` and binds it to the
refund tool, and imports the **bare** `look_up_order`. Required changes:

**Exact, complete new top-of-module import line (LOCKED).** Replace the current
`from .tools import look_up_order, make_initiate_refund` with EXACTLY:

```python
from .tools import make_initiate_refund, make_look_up_order, make_place_order
```

No other reference to a bare `look_up_order` symbol may remain anywhere in `handler.py` — the bare
`look_up_order` no longer exists in `tools` (it is now produced only by the `make_look_up_order`
factory, bound inside `_build_agent`). A stale bare reference would raise `ImportError` at container
start and take down `/api/chat` entirely, so this is a hard requirement, not a cleanup. (A Section 12
test asserts `import assistant.handler` succeeds with strands/boto3 absent and that `_build_agent` is
not invoked at import time.)

Full `_build_agent` shape after the change:

```python

def _build_agent(req_ctx):
    orders_table = None
    pending_table = None
    if boto3 is not None:
        ddb = boto3.resource("dynamodb")
        orders_table = ddb.Table(os.environ["ORDERS_TABLE"])            # NEW
        pending_table = ddb.Table(os.environ["PENDING_REFUNDS_TABLE"])  # existing
    ...
    initiate_refund = make_initiate_refund(pending_table, req_ctx, max_refund=_max_refund())
    look_up_order   = make_look_up_order(orders_table)                  # NEW (was bare import)
    place_order     = make_place_order(orders_table, req_ctx)           # NEW
    return Agent(model=model, tools=[look_up_order, place_order, initiate_refund])
```

- `ORDERS_TABLE` env is **already** set on the assistant Lambda in `app-edge-ai-stack.ts`, and the
  assistant role **already** has `ordersTable.grantReadWriteData` + `kmsKey.grantEncryptDecrypt`. No
  new assistant IAM is needed for `place_order` writes or `look_up_order` reads. **Do not broaden the
  assistant role.**
- `build_response` gains a `placedOrder` branch (Section 8).
- The import of the bare `look_up_order` from `tools` is removed (it becomes a factory). This is the
  change that makes look-up read the real table.

---

## 8. `/api/chat` envelope — the field the SPA reacts to

`build_response(reply_text, req_ctx)` adds a `placedOrder` branch, built the same way as
`pendingRefund` — from the side channel, never from model text:

```python
body = {"reply": reply_text}
pending = req_ctx.get("pending_refunds") or []
if pending:
    body["pendingRefund"] = { ... }               # unchanged
placed = req_ctx.get("placed_orders") or []
if placed:
    latest = placed[-1]
    body["placedOrder"] = {
        "orderId": latest["orderId"],
        "summary": latest["summary"],
        "total":   latest["total"],
        "status":  latest["status"],              # "RECEIVED" at placement time
    }
return body
```

The SPA reacts to **`data.placedOrder`** (presence + `placedOrder.orderId`) on the `/api/chat`
response to trigger an immediate recent-orders refresh (Section 9).

---

## 9. SPA — Recent Orders panel

### Placement and structure
A **Recent Orders** section on the storefront page itself (not inside the chat overlay). Add a new
`<section id="recent" class="section">` to `spa/index.html`, e.g. between the Menu section and the
footer, so it is visible without opening the chat:

```html
<section id="recent" class="section">
  <div class="section-inner">
    <h2 class="section-title">Recent Orders</h2>
    <p class="section-lead">Live from the counter — refreshes automatically.</p>
    <ul id="recentOrders" class="orders-list" aria-live="polite"></ul>
  </div>
</section>
```

**Stored-XSS invariant (LOCKED).** Order `summary`, `orderId`, `total`, and `status` are rendered via
`textContent` / `createElement` DOM nodes **only — never via `innerHTML`** (and never via a
template-string assigned to `innerHTML`). This holds **even though** `summary` is server-normalized
from `MENU_PRICES` keys and cannot contain markup today: the panel reads `summary` back from a stored
DynamoDB attribute written by `place_order`, so a future change to what `summary` may contain must not
be able to introduce stored XSS through this panel. `renderOrders(listEl, orders)` MUST set every field
with `node.textContent = ...` / `document.createElement(...)`; it must not build row markup by string
concatenation into `innerHTML`. (Note: the existing `app.js` renders the pending-refund box with
`innerHTML`; that pre-existing code is out of scope and unchanged — the new recent-orders rendering is
held to the stricter `textContent`-only rule.)

Each rendered row (built in JS, text set via `textContent`/DOM nodes — no `innerHTML` with order data,
per the invariant above):

```
[ ORD-000456 ]  2x Latte            $9.50   ( PREPARING )
[ ORD-000123 ]  1x Flat White, ...  $7.50   ( READY )
```

- A status **badge** with distinct colors per state: `RECEIVED`, `PREPARING`, `READY`.

### Fetch logic — new file `spa/orders.js`
A dedicated file so the five bound ids and chat/refund/receipt flows in `app.js` are untouched.

**Script tag placement (LOCKED).** `index.html` today ends with, in order:

```html
<script src="app.js"></script>
<script src="ui.js"></script>
```

Add the new tag **immediately after the existing `ui.js` tag** (no `defer`, matching the existing
tags):

```html
<script src="app.js"></script>
<script src="ui.js"></script>
<script src="orders.js"></script>
```

`orders.js`:

- Assigns the chat hook at **top-level evaluation** (NOT inside `DOMContentLoaded`):
  `window.refreshRecentOrders = refreshRecentOrders;` runs as the script is parsed, so the hook exists
  before the user can send a chat message that places an order. (`app.js`'s `sendMessage` already guards
  with `if (window.refreshRecentOrders)`, so even if a message somehow fired first it is a safe no-op;
  pinning the top-level assignment removes the race.)
- Defines `refreshRecentOrders()` → `fetch("/api/orders")` (same-origin relative), parses the JSON, and
  calls the pure `renderOrders(listEl, orders)` helper. On non-OK or network error it leaves the
  previously rendered list in place (no destructive clear) and simply waits for the next tick.
- On `DOMContentLoaded`: one immediate `refreshRecentOrders()`, then `setInterval(refreshRecentOrders, 10000)`
  (**poll interval 10s**, matching the status thresholds so movement is visible). Reading `#recentOrders`
  only inside this handler is safe because the element exists by then; the top-level hook assignment
  does not touch the DOM.

### Coupling to chat (minimal, non-breaking)
In `app.js` `sendMessage`, after the existing `pendingRefund` handling, add:

```js
if (data.placedOrder && data.placedOrder.orderId) {
  append("sys", "Order placed: " + data.placedOrder.orderId + " — " + data.placedOrder.summary);
  if (window.refreshRecentOrders) window.refreshRecentOrders();  // immediate refresh
}
```

This is the only edit to `app.js`, it is additive, and it does not touch `#log`, `#chatForm`,
`#message`, `#orderId`, `#receiptBtn` bindings or the refund/receipt code paths.

### Styling — `spa/styles.css`
Reuse the existing coffee palette + accent `#8c4fff`. Add `.orders-list`, `.order-row`, and
`.badge`/`.badge-received`/`.badge-preparing`/`.badge-ready` rules. Suggested badge colors drawn from
the existing variables: `RECEIVED` → `--muted`/caramel, `PREPARING` → accent `#8c4fff`, `READY` →
a green not currently in the palette (add one `--ready: #2f9e5a`). No CDNs, no external fonts, no new
JS dependencies. All calls same-origin relative `/api/...`.

### CloudFront
`GET /api/orders` is covered by the existing `/api/*` behavior (CACHING_DISABLED), so no distribution
change is needed — the poll always hits the origin and sees fresh data.

---

## 10. `orders_list` Lambda — env, IAM, wiring

### Package files
Create **two** files under a new `app/orders_list/` directory:
- `app/orders_list/__init__.py` — **empty**, matching `app/presign/__init__.py` and
  `app/refund_confirm/__init__.py`. This is required so the test harness can
  `import orders_list.handler` (`app/tests/conftest.py` puts `app/` on `sys.path` and imports each zip
  Lambda as a package). The `__init__.py` is **inert at runtime**: the deployed asset is
  `lambda.Code.fromAsset(.../orders_list)` with entrypoint `handler.handler`, so the package marker
  does not change the Lambda entrypoint — exactly like the existing `presign`/`refund_confirm` zips.
- `app/orders_list/handler.py` — the Lambda, below.

### Code: `app/orders_list/handler.py`
Mirror `app/presign/handler.py` structure:
- Guarded `import boto3`; guarded `from aws_xray_sdk.core import patch_all; patch_all()`.
- `_response(status, body)` helper (identical JSON envelope).
- Pure `list_recent_orders(table, gsi_name, now, limit=10)` + mirrored `derive_status` (Section 4).
- `handler(event, _context)`:
  ```python
  ddb = boto3.resource("dynamodb")
  table = ddb.Table(os.environ["ORDERS_TABLE"])
  try:
      body = list_recent_orders(table, os.environ["ORDERS_GSI_NAME"], int(time.time()))
  except Exception:
      return _response(500, {"error": "could not list orders"})
  return _response(200, body)
  ```

### Env
| Var | Value |
|-----|-------|
| `AWS_REGION_PINNED` | `ap-southeast-1` (consistency with the other Lambdas) |
| `ORDERS_TABLE` | `ordersTable.tableName` |
| `ORDERS_GSI_NAME` | `"byCreatedAt"` (the GSI name — passed in rather than hardcoded in Python) |

### CDK (new in `app-edge-ai-stack.ts`)
```ts
const ordersListFn = new lambda.Function(this, 'OrdersListFn', {
  runtime: lambda.Runtime.PYTHON_3_12,
  handler: 'handler.handler',
  code: lambda.Code.fromAsset(path.join(appRoot, 'orders_list')),
  timeout: cdk.Duration.seconds(30),
  memorySize: 256,
  tracing: lambda.Tracing.ACTIVE,
  environment: {
    AWS_REGION_PINNED: REGION,
    ORDERS_TABLE: ordersTable.tableName,
    ORDERS_GSI_NAME: 'byCreatedAt',
  },
});

// IAM: READ-ONLY, least privilege. grantReadData covers Query on the table AND
// its indexes (GetItem/Query/Scan read actions on table + table/index/*). We do
// NOT add Scan-specific perms and we do NOT reuse the assistant role.
const ordersListRole = ordersListFn.role as iam.Role;
ordersTable.grantReadData(ordersListRole);
kmsKey.grantDecrypt(ordersListRole);  // table is CMK-encrypted → decrypt needed to read items

// Route: GET /api/orders  (apiRoot already exists = api.root.addResource('api'))
const orders = apiRoot.addResource('orders');
orders.addMethod('GET', new apigateway.LambdaIntegration(ordersListFn));
```

IAM invariants held:
- `grantReadData` grants `dynamodb:GetItem/Query/Scan/BatchGet/...` on `tableArn` **and**
  `tableArn/index/*` — the GSI query is covered. It does **not** grant write actions. This is the CDK
  idiom; it includes `Scan` as a read action but the code never calls `Scan`. There is no narrower
  built-in grant; adding a hand-rolled Query-only policy is possible but `grantReadData` is the
  established repo pattern (presign/refund use the matching `grant*` helpers) — **chosen for
  consistency and because it stays read-only.** (Flagged in Section 11 so a reviewer can decide if the
  demo wants a bespoke `dynamodb:Query`-only statement to make "no Scan" explicit in IAM.)
- `kmsKey.grantDecrypt` only — the reader never encrypts.
- A **new** dedicated role (`ordersListFn.role`), not the assistant role. The assistant's grants are
  untouched.

---

## 11. Flags where the already-made decisions meet the existing code

1. **Attribute name `summary` vs `items`.** Decision 1 said "summary/items". The deployed `deploy.sh`
   seed and the SPA already use **`summary`**. Locked to `summary` everywhere to match. **No code
   conflict if everyone uses `summary`.**
2. **`look_up_order` return has two "status" meanings.** The tool-call envelope uses a top-level
   `"status"` (`OK`/`NOT_FOUND`/`REJECTED`), while decision 2 lists `status` among the order fields.
   Resolved by emitting the order lifecycle under **`orderStatus`** (derived) and keeping the top-level
   `"status"` as the call outcome. A coder must not collapse these into one key.
3. **`derive_status` is duplicated** in `app/assistant/tools.py` and `app/orders_list/handler.py`
   because the zip Lambda cannot import the assistant package (separate bundles, container vs zip). The
   two copies and their threshold constants MUST stay identical. This mirrors how `ORDER_ID_RE`/UUID
   regexes are repeated across `pii.py` and `refund_confirm/handler.py` today — accepted pattern.
4. **Seed items must gain `gsiPk` + `createdAt`, AND their `total`s must be corrected to the fixed
   menu.** Today `deploy.sh` seeds `ORD-000123` = `"1x Flat White, 1x Croissant"` with `total=12.50`
   and `ORD-000456` = `"2x Latte"` with `total=9.00`. Those totals **contradict** `MENU_PRICES`
   (Section 3), which prices the identical summaries at `4.50 + 3.00 = 7.50` and `2 × 4.75 = 9.50`.
   Since look-up (`float(item["total"])`) and the recent-orders panel both display the stored `total`,
   leaving the old values makes the two seeded orders show prices that disagree with what `place_order`
   would compute for the same items — the facilitator sees inconsistent math. **Decision: the seed is
   corrected to match `MENU_PRICES`** (the menu is the single source of truth; seed totals are not
   treated as independent history). Once the GSI exists, items without `gsiPk` also do not appear in
   the index, so the seed MUST additionally carry `gsiPk` + `createdAt` + `status`. The corrected seed
   `put-item` payloads (LOCKED), with `createdAt` set a bit in the past so one shows `READY` and one
   shows `PREPARING` immediately — compute the epoch values in `deploy.sh` from `now` (e.g.
   `NOW=$(date +%s)`, then `$((NOW-90))` / `$((NOW-30))`):

   ```json
   {"orderId":{"S":"ORD-000123"},"summary":{"S":"1x Flat White, 1x Croissant"},"total":{"N":"7.50"},"status":{"S":"RECEIVED"},"gsiPk":{"S":"ORDER"},"createdAt":{"N":"<NOW-90>"}}
   ```
   ```json
   {"orderId":{"S":"ORD-000456"},"summary":{"S":"2x Latte"},"total":{"N":"9.50"},"status":{"S":"RECEIVED"},"gsiPk":{"S":"ORDER"},"createdAt":{"N":"<NOW-30>"}}
   ```
   With thresholds `[20,60)` PREPARING / `[60,∞)` READY: `NOW-90` (90s old) → `ORD-000123` renders
   `READY`; `NOW-30` (30s old) → `ORD-000456` renders `PREPARING`. **Required change, not optional.**
5. **`_build_agent` binds the refund tool to `PENDING_REFUNDS_TABLE`, and currently builds only that
   one table.** `place_order`/`look_up_order` need the **orders** table. The handler must build a
   second `ddb.Table(os.environ["ORDERS_TABLE"])` and bind the new tools to it (Section 7). The
   `ORDERS_TABLE` env + the assistant's read/write grant on the orders table already exist — no infra
   change for the assistant.
6. **`total` numeric type.** The boto3 resource `Table.put_item` needs `Decimal` for a Number
   attribute; reads come back as `Decimal`. `place_order` builds `Decimal(str(total))`; readers coerce
   with `float(...)` before JSON. Keep the pure pricing helper returning a plain `float` so it stays
   AWS-free for unit tests; the `Decimal` conversion happens only at the `put_item` boundary.
7. **`orders_list` IAM uses `grantReadData` (includes Scan as an action).** The code never scans and
   decision 3 forbids a Scan **fallback**; the grant is still read-only. Flagged in case the demo wants
   IAM to literally exclude `dynamodb:Scan` for teaching emphasis.

---

## 12. Test seams (strands-free / boto3-free unit tests)

The design keeps every new piece unit-testable with the **existing** repo conventions (the `@tool`
identity-decorator fallback in `tools.py`, injected table stubs, injected `now`).

- **`price_order` / `MENU_PRICES`** — pure, no AWS, no strands. Unit tests: valid multi-item summary →
  correct total + normalized summary; unknown item → REJECTED; bad quantity → REJECTED; empty →
  REJECTED; case-insensitivity. These run with nothing installed.
- **`derive_status`** — pure function of `(created_at, now)`. Unit tests at the boundaries (19s→RECEIVED,
  20s→PREPARING, 59s→PREPARING, 60s→READY). Tested in both locations; a shared test asserts the two
  copies agree (import both, assert equal thresholds + equal outputs across a sweep).
- **`make_place_order`** — call the factory with a **table stub** (an object recording `put_item`
  kwargs) and a plain-dict `req_ctx`. Because the `@tool` decorator degrades to identity when strands
  is absent, the returned `place_order` is a plain callable. Assert: the stub received an item with the
  exact attribute set + types (`gsiPk == "ORDER"`, `status == "RECEIVED"`, `total` a `Decimal`),
  `req_ctx["placed_orders"]` got the authoritative record, the returned dict matches, and a REJECTED
  input wrote nothing / appended nothing. No boto3, no strands.
- **`make_look_up_order`** — table stub returning a canned `{"Item": {...}}` or `{}`. Assert OK shape
  (with derived `orderStatus`), NOT_FOUND when the stub returns `{}`, and REJECTED on a bad id. The id
  validation path needs no stub call.
- **Rewrite the existing `test_look_up_order_validates`.** `app/tests/test_tools.py` currently calls
  the removed bare symbol: `tools.look_up_order("ORD-000123")` / `tools.look_up_order("nope")`. After
  Section 7 that symbol no longer exists, so the test fails at collection. It MUST be rewritten to build
  the tool via the factory with a stub table, e.g.:

  ```python
  from decimal import Decimal

  def test_look_up_order_validates():
      # bad id rejects WITHOUT touching the table
      look_up = tools.make_look_up_order(_StubTable(item=None))
      assert look_up("nope")["status"] == "REJECTED"
      # found case returns OK with a derived orderStatus
      look_up_ok = tools.make_look_up_order(
          _StubTable(item={"summary": "1x Latte", "total": Decimal("4.75"), "createdAt": 0})
      )
      got = look_up_ok("ORD-000123")
      assert got["status"] == "OK"
      assert got["orderStatus"] in {"RECEIVED", "PREPARING", "READY"}
  ```
  where `_StubTable.get_item(Key=...)` returns `{"Item": item}` when `item` is not None else `{}`. This
  replaces the old assertions one-for-one; the suite stays green.
- **Handler import safety.** Add a test that `import assistant.handler` succeeds with strands and boto3
  absent (the module's guarded imports already support this), proving no stale bare `look_up_order`
  reference remains and that `_build_agent` is not executed at import time (it is only called inside
  `handler()`). This guards the HIGH risk that a half-done import migration crashes `/api/chat` at
  container start.
- **`list_recent_orders`** (orders_list) — importable as `from orders_list.handler import list_recent_orders`
  **only because** `app/orders_list/__init__.py` exists (Section 10); the test harness imports each zip
  Lambda as a package via `conftest.py`. Inject a table stub whose `query(**kwargs)` records the
  kwargs and returns a canned `{"Items": [...]}`. Assert: it queries `IndexName=byCreatedAt`,
  `KeyConditionExpression` on `gsiPk == "ORDER"`, `ScanIndexForward=False`, `Limit=10`; it never calls
  `scan`; the response is `{"orders": [...]}` with `total` as float and derived `status`; empty Items →
  `{"orders": []}`. The 500 path is covered by making the stub's `query` raise and asserting the
  `handler` wrapper returns `{"error": "could not list orders"}` (the handler is the only non-pure
  seam; the pure core raises and the wrapper maps it).
- **`build_response`** — already testable (no strands/boto3). Add cases: a `req_ctx` with
  `placed_orders` yields a `placedOrder` block; both `pending_refunds` and `placed_orders` present
  yields both blocks; the token/orderId come from the side channel, proving they are never parsed from
  `reply_text` (pass reply_text that contains a *different* fake id and assert the envelope uses the
  side-channel id).
- **SPA (`orders.js`)** — pure render helper (`renderOrders(listEl, orders)`) separated from fetch so
  it can be exercised with a fake `<ul>` + a DOM shim if a JS test runner exists; the fetch/poll glue
  stays thin. `renderOrders` sets every field via `textContent`/`createElement` (never `innerHTML`),
  per the Section 9 stored-XSS invariant. **No JS test runner exists in the repo today** (confirmed: no
  jest/vitest config under `spa/` or `infra/` for the SPA), so this seam is specified for correctness
  and future use but is not wired to CI; the SPA is verified by the deploy smoke flow.

---

## 13. Responses to design-review findings (`design-review.json`, verdict CHANGES_REQUESTED)

Every finding was re-verified against source before responding; all ten are addressed in this revision.

1. **[HIGH] Seed totals contradict the fixed menu.** ADDRESSED — Section 11.4 now corrects the seed
   totals to `MENU_PRICES` (`ORD-000123` → `7.50`, `ORD-000456` → `9.50`), adds `gsiPk`/`createdAt`/`status`,
   and states the menu is the single source of truth (seed totals are not independent history). The
   corrected `put-item` payloads and the `NOW-90`/`NOW-30` ages are written out.
2. **[HIGH] Existing `test_look_up_order_validates` breaks.** ADDRESSED — Section 12 adds an explicit
   instruction (with code) to rewrite that test to build the tool via `make_look_up_order` with a stub
   table (bad id rejects without a table call; found case returns `status == "OK"` with `orderStatus`).
3. **[HIGH] handler.py import migration risk.** ADDRESSED — Section 7 now states the exact, complete new
   import line and that no bare `look_up_order` reference may remain; Section 12 adds a test that
   `assistant.handler` imports cleanly with strands/boto3 absent and `_build_agent` is not called at
   import time.
4. **[MEDIUM] `look_up_order` return shape self-contradictory.** ADDRESSED — Section 6.2 was rewritten to
   a single locked contract: top-level `status` ∈ {OK,NOT_FOUND,REJECTED}, `orderStatus` ∈
   {RECEIVED,PREPARING,READY}, plus `orderId`/`summary`/`total`(float)/`createdAt`(int). The
   `status_live` and "status is the derived status" sentences are deleted.
5. **[MEDIUM] orders_list not importable by the test harness.** ADDRESSED — Section 10 now requires an
   empty `app/orders_list/__init__.py` matching `presign`/`refund_confirm`, confirms the deploy asset
   still ships `handler.handler` (the `__init__.py` is inert at runtime), and Section 12 references the
   package import.
6. **[MEDIUM] `price_order` grammar under-specified.** ADDRESSED — Section 3 locks the token regex
   (optional `INT [xX]`, space-optional), the item-name normalization (trim, collapse internal
   whitespace, lower-case before lookup), rejects plurals as unknown items (exact names only), and
   defines `normalized_summary` reconstruction.
7. **[MEDIUM] Stored-XSS invariant not stated for the panel.** ADDRESSED — Section 9 adds the locked
   invariant that `summary` (and all order fields) render via `textContent`/`createElement` only, never
   `innerHTML`, and that this holds even though `summary` is server-normalized; `renderOrders` must set
   every field with `textContent`/DOM nodes.
8. **[MEDIUM] Script load order / `window.refreshRecentOrders` timing.** ADDRESSED — Section 9 pins the
   `<script src="orders.js">` tag immediately after the existing `ui.js` tag (no `defer`) and requires
   `window.refreshRecentOrders` to be assigned at top-level evaluation, not inside `DOMContentLoaded`.
9. **[NIT] `derive_status` boundary wording.** ADDRESSED — Section 4 now states half-open intervals
   `[0,20)` RECEIVED, `[20,60)` PREPARING, `[60,∞)` READY, with `elapsed == 60 → READY` called out.
10. **[NIT] orderId collision without a no-clobber put.** ADDRESSED (adopted, not just backlogged) —
    Section 6.1 step 5 now writes with `ConditionExpression="attribute_not_exists(orderId)"`, regenerates
    the id and retries once on `ConditionalCheckFailedException`, and rejects cleanly if the retry also
    collides; the retry is covered by the injected-table-stub test without a botocore import.

The hard invariants are enforced at these owning layers: side-channel id flow (`place_order` +
`build_response`, proven by the reply-text test), server-side pricing (`price_order`, proven by the
"unknown item rejected / no price trusted" tests), PII masking before write (`place_order` masks
`summary` via `pii.mask_pii`), read-only least-privilege (`orders_list` IAM + the "never calls scan"
test), and same-origin SPA calls (relative `/api/...` only).
