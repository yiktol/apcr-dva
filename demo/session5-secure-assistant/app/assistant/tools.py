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

# Presign helpers are imported defensively (mirroring the guarded strands import
# above) so this module stays importable for py_compile / unit tests WITHOUT
# boto3 installed. The signing CLIENT and URL builder are the SINGLE copy owned
# by presign.handler — the receipt tool never duplicates the SigV4 config.
try:
    from presign import handler as presign_handler  # type: ignore
    from presign.handler import EXPIRES_IN  # type: ignore
except Exception:  # pragma: no cover - boto3 absent / presign import unavailable
    presign_handler = None  # type: ignore
    EXPIRES_IN = 15 * 60  # type: ignore

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


def build_receipt_pdf(order_id: str, summary: str, total) -> bytes:
    """Build a minimal, VALID single-page PDF for an order receipt.

    Emits a real PDF object tree (Catalog -> Pages -> Page -> Contents, plus a
    standard Helvetica font) with a correct cross-reference table and %%EOF, so
    the file actually opens and renders in a PDF viewer — not just a header stub.

    Plain ASCII only — `summary` is already the PII-masked server summary, so no
    raw PII reaches the object. This is a demo artifact, not a production invoice.
    """
    try:
        total_str = f"{float(total):.2f}"
    except (TypeError, ValueError):
        total_str = str(total)

    def _esc(s: str) -> str:
        # Escape the characters that are special inside a PDF literal string,
        # and drop anything non-ASCII so the content stream stays 1 byte/char
        # (keeps our byte-offset math for the xref table correct).
        s = str(s).encode("ascii", "replace").decode("ascii")
        return s.replace("\\", r"\\").replace("(", r"\(").replace(")", r"\)")

    # Page text lines drawn with the Tj operator, one per line via T* / leading.
    lines = [
        "Coffee Shop - Order Receipt",
        "",
        f"Order ID: {order_id}",
        f"Items:    {summary}",
        f"Total:    USD {total_str}",
        "",
        "Thank you for your order!",
        "(session5 secure-assistant demo receipt)",
    ]
    # Build the content stream: start a text object, pick Helvetica 12 at 14pt
    # leading, move to a start position, then emit each line followed by T*.
    content_parts = ["BT", "/F1 12 Tf", "14 TL", "72 760 Td"]
    for ln in lines:
        content_parts.append(f"({_esc(ln)}) Tj")
        content_parts.append("T*")
    content_parts.append("ET")
    content = "\n".join(content_parts) + "\n"
    content_bytes = content.encode("ascii", "replace")

    # Five PDF objects: Catalog, Pages, Page, Contents stream, Font.
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length "
        + str(len(content_bytes)).encode("ascii")
        + b" >>\nstream\n"
        + content_bytes
        + b"endstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]

    # Assemble the file, tracking the byte offset of each object for the xref.
    pdf = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, obj in enumerate(objects, start=1):
        offsets.append(len(pdf))
        pdf += f"{i} 0 obj\n".encode("ascii") + obj + b"\nendobj\n"

    # Cross-reference table: one free entry (object 0) + one per object.
    xref_pos = len(pdf)
    n = len(objects) + 1
    xref = bytearray(f"xref\n0 {n}\n".encode("ascii"))
    xref += b"0000000000 65535 f \n"
    for off in offsets:
        xref += f"{off:010d} 00000 n \n".encode("ascii")
    pdf += xref

    pdf += (
        f"trailer\n<< /Size {n} /Root 1 0 R >>\nstartxref\n{xref_pos}\n".encode(
            "ascii"
        )
        + b"%%EOF\n"
    )
    return bytes(pdf)


def make_place_order(orders_table, req_ctx, receipts_bucket=None, region=None):
    """Factory → @tool place_order, bound to the real OrdersTable + the request
    side channel. Mirrors make_initiate_refund.

    When `receipts_bucket` is provided, a minimal receipt PDF is uploaded to
    receipts/{orderId}.pdf after a successful order write so the in-session
    order has a downloadable receipt. `receipts_bucket=None` (the default) skips
    the upload, keeping the old two-arg signature working for existing tests.
    """

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

            # Write the receipt PDF so an in-session order has a downloadable
            # receipt (receipts/{orderId}.pdf). The object inherits the bucket's
            # default CMK encryption (aws:kms), so no SSE params are passed; the
            # role's kms:GenerateDataKey*/Encrypt grant covers the write.
            # Upload failures MUST NOT break order placement — the order is
            # already committed to DynamoDB — so this is best-effort.
            if receipts_bucket:
                try:
                    client = presign_handler.make_s3_client(region)
                    client.put_object(
                        Bucket=receipts_bucket,
                        Key=presign_handler.receipt_key(order_id),
                        Body=build_receipt_pdf(order_id, summary, total),
                        ContentType="application/pdf",
                    )
                except Exception:  # best-effort: order already placed
                    # botocore ClientError (and any other error) is swallowed so
                    # the committed order still returns RECEIVED. No raw PII is
                    # in the summary (already masked), nothing is logged here.
                    pass

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


def make_get_receipt_url(req_ctx, bucket, region=None, orders_table=None):
    """Factory → @tool get_receipt_url, bound to the receipts bucket + the
    request side channel. Mirrors the other tool factories.

    The presigned URL is the SAME 15-minute SigV4 regional GET the presign
    Lambda produces — both obtain their client from
    presign.handler.make_s3_presign_client and build the URL via
    presign.handler.generate_url (ONE copy of the signing code). The URL is
    appended to the AUTHORITATIVE req_ctx['receipts'] side channel so the HTTP
    handler emits it in the envelope WITHOUT ever parsing it from model text.
    """

    @tool
    def get_receipt_url(order_id: str) -> dict:
        """Get a short-lived download link for an order's receipt PDF.

        IMPORTANT: Do NOT repeat, quote, or paste the returned `url` value in
        your reply text. The download link is delivered to the user through the
        app's UI automatically. In your reply, simply tell the user their
        receipt download link is ready below — never emit the raw URL string.

        Args:
            order_id: the order id, formatted ORD-NNNNNN.
        """
        if not pii.validate_order_id(order_id):
            # REJECTED — append nothing to the side channel.
            return {"status": "REJECTED", "reason": "invalid order id format"}

        # When bound to an orders table, confirm the order exists first; format
        # validation above is the minimum guarantee.
        if orders_table is not None:
            got = orders_table.get_item(Key={"orderId": order_id})
            if not got.get("Item"):
                return {"status": "NOT_FOUND", "orderId": order_id}

        # Verify the receipt object actually exists BEFORE handing out a link,
        # so a user never gets a URL that 403s. With only s3:GetObject (no
        # s3:ListBucket) head_object returns 403 for a missing key rather than
        # 404 — treat any ClientError (403/404/NoSuchKey) as 'not found' for UX.
        # botocore is referenced defensively WITHOUT a top-level import so this
        # module stays importable for py_compile / unit tests.
        head_client = presign_handler.make_s3_client(region)
        try:
            head_client.head_object(
                Bucket=bucket, Key=presign_handler.receipt_key(order_id)
            )
        except Exception:
            # Missing object (or no permission to confirm) → surface NOT_FOUND
            # and append NOTHING to the side channel.
            return {"status": "NOT_FOUND", "orderId": order_id}

        # Build the signing client + URL from the single shared presign source.
        client = presign_handler.make_s3_presign_client(region)
        url, err = presign_handler.generate_url(client, bucket, order_id)
        if err is not None:
            return {"status": "REJECTED", "reason": "invalid order id format"}

        # Authoritative side-channel record (never read the URL from model text).
        req_ctx.setdefault("receipts", []).append(
            {"orderId": order_id, "url": url, "expiresIn": EXPIRES_IN}
        )
        return {
            "status": "OK",
            "orderId": order_id,
            "url": url,
            "expiresIn": EXPIRES_IN,
        }

    return get_receipt_url
