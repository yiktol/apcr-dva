"""presign Lambda — generate a 15-minute presigned GET URL for a receipt.

The receipts bucket is KMS-encrypted and private (OAC/BLOCK_ALL); the presigned
URL lets the browser GET a single object for a short window. The signer role has
a narrowly-scoped s3:GetObject identity policy; the bucket's resource policy
denies non-TLS access.

URL-generation logic is a pure, injectable function so it is unit-testable with
a botocore stub and no live AWS.
"""
import json
import os
import re

try:
    import boto3  # type: ignore
except Exception:  # pragma: no cover
    boto3 = None  # type: ignore

try:
    from aws_xray_sdk.core import patch_all  # type: ignore

    patch_all()
except Exception:  # pragma: no cover
    pass

ORDER_ID_RE = re.compile(r"^ORD-[0-9]{6}$")
EXPIRES_IN = 15 * 60  # 15-minute GET


def _response(status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }


def generate_url(s3_client, bucket: str, order_id: str, expires_in: int = EXPIRES_IN):
    """Generate a presigned GET URL for receipts/{order_id}.pdf.

    Returns (url, None) on success or (None, error_response) on bad input.
    """
    if not order_id or not ORDER_ID_RE.match(order_id):
        return None, _response(400, {"error": "invalid order id"})
    key = f"receipts/{order_id}.pdf"
    url = s3_client.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": key},
        ExpiresIn=expires_in,
    )
    return url, None


def handler(event, _context):  # pragma: no cover - exercised live only
    params = event.get("pathParameters") or {}
    order_id = params.get("orderId")
    bucket = os.environ["RECEIPTS_BUCKET"]
    s3_client = boto3.client("s3")
    try:
        url, err = generate_url(s3_client, bucket, order_id)
    except Exception:
        return _response(500, {"error": "could not generate url"})
    if err is not None:
        return err
    return _response(200, {"url": url, "expiresIn": EXPIRES_IN})
