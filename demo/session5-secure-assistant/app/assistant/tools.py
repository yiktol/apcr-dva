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
import time
import uuid

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


@tool
def look_up_order(order_id: str) -> dict:
    """Look up a coffee-shop order by its id (read-only).

    Args:
        order_id: the order id, formatted ORD-NNNNNN.
    """
    if not pii.validate_order_id(order_id):
        return {"status": "REJECTED", "reason": "invalid order id format"}
    # Demo lookup: in the deployed demo this reads the orders table. Here we
    # return a stable shape; the handler injects the real table for live calls.
    return {
        "status": "OK",
        "orderId": order_id,
        "summary": "1x Flat White, 1x Croissant",
    }


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
