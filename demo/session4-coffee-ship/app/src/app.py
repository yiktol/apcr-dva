"""coffee-shop loyalty Lambda handler.

Handles two event sources:

* API Gateway proxy events, where ``event['body']`` is a JSON **string**.
  A malformed/non-JSON body returns a 400 proxy response.
* SQS events, where each record's ``body`` is a JSON string order payload.

Loyalty points are computed from the order total. The module stays stdlib-only
at import time (no boto3 clients created on import) so unit tests run without AWS.
"""

import json
import os

# Points awarded per whole dollar of order total. Overridable via env for the
# deployed function; defaults keep the handler usable in tests without any env.
POINTS_PER_DOLLAR = int(os.environ.get("POINTS_PER_DOLLAR", "10"))


def compute_points(order):
    """Return loyalty points for an order dict.

    Points = floor(total) * POINTS_PER_DOLLAR. A missing or non-numeric total
    raises ValueError so callers can map it to a 400.
    """
    try:
        total = float(order["total"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("order is missing a numeric 'total'") from exc
    if total < 0:
        raise ValueError("order 'total' must not be negative")
    return int(total) * POINTS_PER_DOLLAR


def _proxy_response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def _handle_api_event(event):
    """Handle an API Gateway proxy event whose body is a JSON string."""
    raw_body = event.get("body")
    try:
        if not isinstance(raw_body, str):
            raise ValueError("API Gateway body must be a JSON string")
        order = json.loads(raw_body)
        if not isinstance(order, dict):
            raise ValueError("order payload must be a JSON object")
        points = compute_points(order)
    except (ValueError, json.JSONDecodeError) as exc:
        return _proxy_response(400, {"error": str(exc)})

    return _proxy_response(
        200,
        {
            "orderId": order.get("orderId"),
            "points": points,
        },
    )


def _handle_sqs_event(event):
    """Handle an SQS event; compute points per record body (JSON string)."""
    results = []
    for record in event.get("Records", []):
        order = json.loads(record["body"])
        results.append(
            {"orderId": order.get("orderId"), "points": compute_points(order)}
        )
    return {"processed": len(results), "results": results}


def handler(event, context):
    """Lambda entry point. Routes between API Gateway and SQS events."""
    if isinstance(event, dict) and "body" in event:
        return _handle_api_event(event)
    if isinstance(event, dict) and "Records" in event:
        return _handle_sqs_event(event)
    return _proxy_response(400, {"error": "unsupported event source"})
