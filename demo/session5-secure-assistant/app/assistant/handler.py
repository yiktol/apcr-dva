"""Assistant Lambda handler — Strands Agent + Nova Micro + Guardrail + X-Ray.

The strands imports are guarded so this module is importable for py_compile and
unit tests WITHOUT strands installed. The pure request-shaping logic
(build_response, input validation) is testable directly; the live agent path
only runs in the deployed container (where strands + boto3 are present).
"""
import json
import os

# ---- Guarded heavy imports ------------------------------------------------
try:
    import boto3  # type: ignore
except Exception:  # pragma: no cover
    boto3 = None  # type: ignore

try:
    from aws_xray_sdk.core import patch_all, xray_recorder  # type: ignore

    patch_all()  # instrument boto3 (Bedrock + DynamoDB) as X-Ray subsegments
    _XRAY = True
except Exception:  # pragma: no cover
    _XRAY = False

    class _NullSub:
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

    class _NullRecorder:
        def in_subsegment(self, *_a, **_k):
            return _NullSub()

    xray_recorder = _NullRecorder()  # type: ignore

try:
    from strands import Agent  # type: ignore
    from strands.models import BedrockModel  # type: ignore

    _STRANDS = True
except Exception:  # pragma: no cover
    _STRANDS = False

from . import pii
from .tools import make_initiate_refund, make_look_up_order, make_place_order

MAX_MESSAGE_LEN = 2000


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def parse_message(event: dict):
    """Extract + validate the chat message from an API GW proxy event.

    Returns (message, None) on success or (None, error_response) on failure.
    """
    try:
        body = event.get("body") or "{}"
        if event.get("isBase64Encoded"):
            import base64

            body = base64.b64decode(body).decode("utf-8")
        data = json.loads(body)
    except (ValueError, TypeError):
        return None, _response(400, {"error": "invalid request"})

    message = data.get("message")
    if not isinstance(message, str) or not (1 <= len(message) <= MAX_MESSAGE_LEN):
        return None, _response(400, {"error": "invalid request"})
    return message, None


def build_response(reply_text: str, req_ctx: dict) -> dict:
    """Build the HTTP envelope from the handler-captured side channel.

    The pendingRefund token comes from req_ctx (authoritative), NOT from parsing
    the model's reply text.
    """
    body = {"reply": reply_text}
    pending = req_ctx.get("pending_refunds") or []
    if pending:
        latest = pending[-1]
        body["pendingRefund"] = {
            "token": latest["token"],
            "amountMasked": latest["amountMasked"],
            "orderMasked": latest["orderMasked"],
        }
    placed = req_ctx.get("placed_orders") or []
    if placed:
        latest = placed[-1]
        body["placedOrder"] = {
            "orderId": latest["orderId"],
            "summary": latest["summary"],
            "total": latest["total"],
            "status": latest["status"],
        }
    return body


def _build_agent(req_ctx: dict):  # pragma: no cover - requires strands + boto3
    """Construct the Strands Agent with Nova Micro + the guardrail."""
    orders_table = None
    pending_table = None
    if boto3 is not None:
        ddb = boto3.resource("dynamodb")
        orders_table = ddb.Table(os.environ["ORDERS_TABLE"])
        pending_table = ddb.Table(os.environ["PENDING_REFUNDS_TABLE"])

    model = BedrockModel(
        model_id=os.environ.get("NOVA_MODEL_ID", "apac.amazon.nova-micro-v1:0"),
        region_name=os.environ.get("AWS_REGION_PINNED", "ap-southeast-1"),
        # guardrail_id / guardrail_version / guardrail_trace are NOT first-class
        # BedrockModel.__init__ params in strands-agents==1.23.0; they are
        # accepted and forwarded through **model_config and configure the inline
        # guardrail applied as part of the InvokeModel request.
        guardrail_id=os.environ["GUARDRAIL_ID"],
        guardrail_version=os.environ["GUARDRAIL_VERSION"],
        guardrail_trace="enabled",
    )
    initiate_refund = make_initiate_refund(
        pending_table, req_ctx, max_refund=_max_refund()
    )
    look_up_order = make_look_up_order(orders_table)
    place_order = make_place_order(orders_table, req_ctx)
    return Agent(model=model, tools=[look_up_order, place_order, initiate_refund])


def _max_refund() -> float:  # pragma: no cover - requires boto3 at runtime
    try:
        if boto3 is None:
            return 50.0
        ssm = boto3.client("ssm")
        raw = ssm.get_parameter(Name=os.environ["CONFIG_PARAM_NAME"])[
            "Parameter"
        ]["Value"]
        return float(json.loads(raw).get("maxRefund", 50))
    except Exception:
        return 50.0


def handler(event, _context):  # pragma: no cover - exercised live only
    """API GW proxy entry point for POST /api/chat."""
    message, err = parse_message(event)
    if err is not None:
        return err

    if not _STRANDS:
        # Defensive: should never happen in the deployed container.
        return _response(502, {"error": "assistant unavailable"})

    req_ctx = {"pending_refunds": [], "placed_orders": []}
    try:
        agent = _build_agent(req_ctx)
        with xray_recorder.in_subsegment("bedrock-invoke"):
            result = agent(message)
        # Strip the model's internal <thinking> reasoning BEFORE masking so only
        # the user-facing reply (with PII masked) is returned.
        reply_text = pii.mask_pii(pii.strip_reasoning(str(result)))
    except Exception:
        # Never leak prompt/PII in the error surface.
        return _response(502, {"error": "assistant unavailable"})

    return _response(200, build_response(reply_text, req_ctx))
