import json
import os

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "sam-demo-items")

# When running locally against DynamoDB Local, set DYNAMODB_ENDPOINT
# (e.g. http://dynamodb-local:8000). On AWS this is unset, so boto3 uses the
# real regional endpoint.
_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT") or None
dynamodb = boto3.resource("dynamodb", endpoint_url=_ENDPOINT)


def get_handler(event, context):
    """Handle GET /items/{id}. Reads a single item from the DynamoDB table."""
    path_params = event.get("pathParameters") or {}
    item_id = path_params.get("id")

    if not item_id:
        return _response(400, {"message": "Missing path parameter: id"})

    table = dynamodb.Table(TABLE_NAME)
    result = table.get_item(Key={"id": item_id})
    item = result.get("Item")

    if not item:
        return _response(404, {"message": f"Item '{item_id}' not found"})

    return _response(200, {"item": item})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
