"""orders_list Lambda — list the most recent orders, newest-first.

Read-only, least-privilege boto3 Lambda behind GET /api/orders. It queries the
single-partition `byCreatedAt` GSI on the CMK-encrypted OrdersTable
(ScanIndexForward=False, Limit 10) so recent orders is a Query, NEVER a Scan.
The endpoint takes NO client input (parameterless) — there is nothing to
validate on the request side, which removes an injection vector. Validation
that matters is on the DATA read back (skip malformed items, coerce total).

The query/response-shaping logic is a pure, injectable function so it is
unit-testable with a table stub and no live AWS. Guarded imports keep the
module importable (and testable) WITHOUT boto3 installed.
"""
import json
import os
import time

try:
    import boto3  # type: ignore
except Exception:  # pragma: no cover
    boto3 = None  # type: ignore

try:
    from boto3.dynamodb.conditions import Key  # type: ignore
except Exception:  # pragma: no cover - boto3 not installed in test/py_compile
    Key = None  # type: ignore

try:
    from aws_xray_sdk.core import patch_all  # type: ignore

    patch_all()
except Exception:  # pragma: no cover
    pass


# Read-time derived status. DEMO SIMPLIFICATION: there is no worker flipping
# rows; status is a pure function of age so a facilitator sees RECEIVED ->
# PREPARING -> READY within one session. Stored baseline stays "RECEIVED".
# MIRRORED (identical constants + logic) from app/assistant/tools.py — the zip
# Lambda cannot import the assistant package.
PREPARING_AFTER = 20   # seconds
READY_AFTER = 60       # seconds


def derive_status(created_at: int, now: int) -> str:
    elapsed = int(now) - int(created_at)
    if elapsed < PREPARING_AFTER:
        return "RECEIVED"
    if elapsed < READY_AFTER:
        return "PREPARING"
    return "READY"


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _gsi_pk_condition():
    """Build the gsiPk == 'ORDER' KeyConditionExpression.

    Uses boto3's Key helper when available; falls back to the raw equality so
    the module stays importable (and the pure core testable) without boto3.
    """
    if Key is not None:
        return Key("gsiPk").eq("ORDER")
    return "gsiPk = ORDER"


def list_recent_orders(table, gsi_name, now, limit=10) -> dict:
    """Query the latest GSI newest-first and shape the public response.

    Returns {"orders": [...]} ; raises nothing for an empty result. Never
    calls scan — recent orders is a Query on the single-partition GSI.
    """
    resp = table.query(
        IndexName=gsi_name,
        KeyConditionExpression=_gsi_pk_condition(),
        ScanIndexForward=False,  # newest-first
        Limit=limit,
    )
    orders = []
    for item in resp.get("Items", []):
        order_id = item.get("orderId")
        created_at = item.get("createdAt")
        if order_id is None or created_at is None:
            # Skip malformed records rather than emitting a bad row.
            continue
        created_at = int(created_at)
        orders.append(
            {
                "orderId": order_id,
                "summary": item.get("summary"),
                "total": float(item.get("total", 0)),
                "status": derive_status(created_at, now),
                "createdAt": created_at,
            }
        )
    return {"orders": orders}


def handler(event, _context):  # pragma: no cover - exercised live only
    ddb = boto3.resource("dynamodb")
    table = ddb.Table(os.environ["ORDERS_TABLE"])
    try:
        body = list_recent_orders(table, os.environ["ORDERS_GSI_NAME"], int(time.time()))
    except Exception:
        return _response(500, {"error": "could not list orders"})
    return _response(200, body)
