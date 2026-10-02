"""Strands @tool handlers for the coffee-shop assistant.

The @tool decorator is guarded so this module stays importable (and the pure
logic stays unit-testable) WITHOUT strands-agents installed: if the import
fails, `tool` degrades to an identity decorator. The handlers below do real
work in plain Python and never require strands at import time.

PII is masked/validated HERE, by the handlers themselves, because the guardrail
does not see tool-call arguments or results (see pii.py — the tool-call blind
spot). Raw account numbers / SSNs / emails are NEVER written to DynamoDB or to a
log line.
"""
import random
import re
import time
import uuid
from decimal import Decimal

try:
    from strands import tool  # type: ignore
except Exception:  # pragma: no cover - strands not installed in test/py_compile
    def tool(func=None, **_kwargs):  # type: ignore
        """Fallback identity decorator so the module imports without strands."""
        if func is None:
            return lambda f: f
        return func

from . import pii

# Pending refunds expire after this many seconds (TTL on the DynamoDB item).
PENDING_TTL_SECONDS = 15 * 60

# Fixed menu (USD). The SERVER-SIDE source of truth for order totals. The model
# NEVER supplies a price — it only names items; the tool prices them from here.
MENU_PRICES = {
    "flat white": 4.50,
    "latte": 4.75,
    "croissant": 3.00,
    "coco cake": 5.25,
}

# optional "<INT> x" / "<INT>x" (x or X, any surrounding whitespace), then the item name.
_TOKEN_RE = re.compile(r"^\s*(?:(\d+)\s*[xX]\s*)?(.+?)\s*$")


def price_order(summary):
    """Price a comma-separated order summary server-side from MENU_PRICES.

    Returns (total: float, normalized_summary: str) on success, or a REJECTED
    dict (writing nothing) on any invalid input. The model names items; prices
    come only from MENU_PRICES — never from the model/user.
    """
    if not summary or not summary.strip():
        return {"status": "REJECTED", "reason": "no recognizable menu items"}

    total = 0.0
    parts = []
    for token in summary.split(","):
        if not token.strip():
            continue
        m = _TOKEN_RE.match(token)
        if not m:
            continue
        qty_raw, raw_item = m.group(1), m.group(2)
        item_key = re.sub(r"\s+", " ", raw_item.strip()).lower()
        if not item_key:
            continue
        if item_key not in MENU_PRICES:
            return {"status": "REJECTED", "reason": f"unknown menu item: {item_key}"}
        if qty_raw is None:
            qty = 1
        else:
            try:
                qty = int(qty_raw)
            except (TypeError, ValueError):
                return {"status": "REJECTED", "reason": "invalid quantity"}
        if qty <= 0 or qty > 20:
            return {"status": "REJECTED", "reason": "invalid quantity"}
        total += qty * MENU_PRICES[item_key]
        parts.append(f"{qty}x {item_key.title()}")

    if not parts:
        return {"status": "REJECTED", "reason": "no recognizable menu items"}
    total = round(total, 2)
    if total <= 0:
        return {"status": "REJECTED", "reason": "empty order"}
    return total, ", ".join(parts)


# Read-time derived status. DEMO SIMPLIFICATION: there is no worker flipping
# rows; status is a pure function of age so a facilitator sees RECEIVED ->
# PREPARING -> READY within one session. Stored baseline stays "RECEIVED".
PREPARING_AFTER = 20   # seconds
READY_AFTER = 60       # seconds


def derive_status(created_at: int, now: int) -> str:
    elapsed = int(now) - int(created_at)
    if elapsed < PREPARING_AFTER:
        return "RECEIVED"
    if elapsed < READY_AFTER:
        return "PREPARING"
    return "READY"


def make_place_order(orders_table, req_ctx):
    """Factory → @tool place_order, bound to the real OrdersTable + the request
    side channel. Mirrors make_initiate_refund."""

    @tool
    def place_order(items: str) -> dict:
        """Place a coffee-shop order. `items` is a comma-separated list like
        '2x Latte, 1x Croissant'. The server prices it from the fixed menu;
        prices are NEVER taken from this call. Use exact singular menu names.

        Args:
            items: comma-separated line items, e.g. '2x Latte, 1x Croissant'.
        """
        priced = price_order(items)
        if isinstance(priced, dict):
            # REJECTED — write nothing, append nothing.
            return priced
        total, normalized_summary = priced

        summary = pii.mask_pii(normalized_summary)
        created_at = int(time.time())

        for attempt in range(2):
            order_id = f"ORD-{random.randint(0, 999999):06d}"
            assert pii.validate_order_id(order_id)
            item = {
                "orderId": order_id,
                "summary": summary,
                "total": Decimal(str(total)),
                "status": "RECEIVED",
                "createdAt": created_at,
                "gsiPk": "ORDER",
            }
            try:
                orders_table.put_item(
                    Item=item,
                    ConditionExpression="attribute_not_exists(orderId)",
                )
            except Exception as err:  # defensive: catch ClientError at runtime
                # botocore is referenced defensively WITHOUT a top-level import
                # so this module stays importable under test.
                code = ""
                response = getattr(err, "response", None)
                if isinstance(response, dict):
                    code = response.get("Error", {}).get("Code", "")
                if code == "ConditionalCheckFailedException" and attempt == 0:
                    # ~1-in-10^6 id collision: regenerate once and retry.
                    continue
                if code == "ConditionalCheckFailedException":
                    return {
                        "status": "REJECTED",
                        "reason": "could not allocate order id",
                    }
                raise

            req_ctx.setdefault("placed_orders", []).append(
                {
                    "orderId": order_id,
                    "summary": summary,
                    "total": total,
                    "status": "RECEIVED",
                }
            )
            return {
                "status": "RECEIVED",
                "orderId": order_id,
                "summary": summary,
                "total": total,
            }

    return place_order


def make_look_up_order(orders_table):
    """Factory → @tool look_up_order, bound to the real OrdersTable. Replaces
    the hardcoded stub. Read-only GetItem."""

    @tool
    def look_up_order(order_id: str) -> dict:
        """Look up an order by id (ORD-NNNNNN). Read-only.

        Args:
            order_id: the order id, formatted ORD-NNNNNN.
        """
        if not pii.validate_order_id(order_id):
            return {"status": "REJECTED", "reason": "invalid order id format"}
        got = orders_table.get_item(Key={"orderId": order_id})
        item = got.get("Item")
        if not item:
            return {"status": "NOT_FOUND", "orderId": order_id}
        return {
            "status": "OK",
            "orderId": order_id,
            "summary": item["summary"],
            "total": float(item["total"]),
            "orderStatus": derive_status(int(item["createdAt"]), int(time.time())),
            "createdAt": int(item["createdAt"]),
        }

    return look_up_order


def make_initiate_refund(table, req_ctx, max_refund=50.0):
    """Factory returning the initiate_refund @tool bound to a table + req_ctx.

    `table` is an injected DynamoDB Table-like object (so tests pass a stub).
    `req_ctx` is a per-request mutable dict with a 'pending_refunds' list — the
    REQUEST-SCOPED SIDE CHANNEL. The tool appends the authoritative
    {token, amountMasked, orderMasked} record there so the /api/chat handler can
    build the HTTP response envelope from it WITHOUT parsing model text (the
    model may paraphrase a tool result, so the token must never be read back
    from model output).
    """

    @tool
    def initiate_refund(order_id: str, amount: float) -> dict:
        """Start a refund. This moves NO money — it only records a PENDING
        refund that a human must confirm via the separate confirm endpoint.

        Args:
            order_id: the order id, formatted ORD-NNNNNN.
            amount: the refund amount (must be > 0 and within the configured max).
        """
        if not pii.validate_order_id(order_id):
            return {"status": "REJECTED", "reason": "invalid order id format"}
        if not pii.validate_amount(amount, max_refund):
            return {
                "status": "REJECTED",
                "reason": f"amount must be > 0 and <= {max_refund}",
            }

        # Mask BEFORE persisting / returning. Even though order_id is validated
        # to a non-PII format, we route everything through the masker so a future
        # change cannot leak raw PII into the item or a log line.
        order_masked = pii.mask_pii(order_id)
        amount_masked = f"{float(amount):.2f}"

        token = str(uuid.uuid4())
        now = int(time.time())
        item = {
            "confirmationToken": token,
            "status": "PENDING_CONFIRMATION",
            "orderMasked": order_masked,
            "amount": amount_masked,
            "createdAt": now,
            "ttl": now + PENDING_TTL_SECONDS,
        }
        # Write the pending record. No raw PII is present in `item`.
        table.put_item(Item=item)

        # Append to the request-scoped side channel (authoritative token source
        # for the HTTP envelope).
        req_ctx.setdefault("pending_refunds", []).append(
            {
                "token": token,
                "amountMasked": amount_masked,
                "orderMasked": order_masked,
            }
        )

        return {
            "status": "PENDING_CONFIRMATION",
            "orderMasked": order_masked,
            "amountMasked": amount_masked,
            "message": (
                "A refund is pending your confirmation. No money has moved yet; "
                "confirm it to complete."
            ),
        }

    return initiate_refund
