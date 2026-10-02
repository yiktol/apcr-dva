"""refund_confirm Lambda — the ONLY executor of a confirmed refund.

Human-in-the-loop: initiate_refund (the Strands tool) only writes a PENDING
record. This endpoint, carrying the confirmation token, is the single path that
executes the refund. It flips the pending-refunds item to CONFIRMED
idempotently, reads the payment secret to demonstrate the grant, and STUBS the
processor call (no real money moves).

Pure logic (token validation, the confirm state machine) is factored into
module functions so it is unit-testable with an injected table stub and no live
AWS.
"""
import json
import os
import re
import time

try:
    import boto3  # type: ignore
except Exception:  # pragma: no cover
    boto3 = None  # type: ignore

try:
    from aws_xray_sdk.core import patch_all  # type: ignore

    patch_all()
except Exception:  # pragma: no cover
    pass

UUID4_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$",
    re.IGNORECASE,
)


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def confirm_refund(table, token: str, now: int = None) -> dict:
    """Confirm a pending refund by token (pure state machine over the table).

    Returns {"status": <HTTP>, "body": {...}}:
      400 invalid token format, 404 unknown token, 410 expired,
      409 already confirmed, 200 confirmed (idempotent on repeat).
    """
    if now is None:
        now = int(time.time())
    if not token or not UUID4_RE.match(token):
        return {"status": 400, "body": {"error": "invalid confirmation token"}}

    got = table.get_item(Key={"confirmationToken": token})
    item = got.get("Item") if got else None
    if not item:
        return {"status": 404, "body": {"error": "refund not found"}}

    ttl = int(item.get("ttl", 0))
    status = item.get("status")

    if status == "CONFIRMED":
        # Idempotent: a repeat confirm is a success, not a double-spend.
        return {
            "status": 200,
            "body": {"status": "CONFIRMED", "token": token, "idempotent": True},
        }

    if ttl and ttl < now:
        return {"status": 410, "body": {"error": "refund expired"}}

    if status != "PENDING_CONFIRMATION":
        return {"status": 409, "body": {"error": "refund not pending"}}

    # Conditional update: only flip if still PENDING_CONFIRMATION (guards against
    # a concurrent confirm).
    table.update_item(
        Key={"confirmationToken": token},
        UpdateExpression="SET #s = :c, confirmedAt = :t",
        ConditionExpression="#s = :p",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={
            ":c": "CONFIRMED",
            ":p": "PENDING_CONFIRMATION",
            ":t": now,
        },
    )
    return {"status": 200, "body": {"status": "CONFIRMED", "token": token}}


def _settle_payment_stub() -> None:  # pragma: no cover - requires boto3
    """Demonstrate the Secrets Manager grant, then STUB the processor call."""
    if boto3 is None:
        return
    sm = boto3.client("secretsmanager")
    # Read the secret to prove the least-privilege grant works. We reference the
    # key by name and never log its value. The real processor call is stubbed.
    sm.get_secret_value(SecretId=os.environ["PAYMENT_SECRET_NAME"])
    # ... a real integration would call the processor here. Demo moves no money.


def handler(event, _context):  # pragma: no cover - exercised live only
    try:
        data = json.loads(event.get("body") or "{}")
    except (ValueError, TypeError):
        return _response(400, {"error": "invalid request"})

    token = data.get("token")
    ddb = boto3.resource("dynamodb")
    table = ddb.Table(os.environ["PENDING_REFUNDS_TABLE"])

    result = confirm_refund(table, token)
    if result["status"] == 200 and not result["body"].get("idempotent"):
        _settle_payment_stub()
    return _response(result["status"], result["body"])
