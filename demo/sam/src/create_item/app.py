import json
import os
import uuid

import boto3

TABLE_NAME = os.environ.get("TABLE_NAME", "sam-demo-items")

# When running locally against DynamoDB Local, set DYNAMODB_ENDPOINT
# (e.g. http://dynamodb-local:8000). On AWS this is unset, so boto3 uses the
# real regional endpoint.
_ENDPOINT = os.environ.get("DYNAMODB_ENDPOINT") or None
dynamodb = boto3.resource("dynamodb", endpoint_url=_ENDPOINT)


def create_handler(event, context):
    """Handle POST /items. Creates an item in the DynamoDB table."""
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return _response(400, {"message": "Request body must be valid JSON"})

    item = {
        "id": body.get("id") or str(uuid.uuid4()),
        "name": body.get("name", ""),
        "description": body.get("description", ""),
    }

    table = dynamodb.Table(TABLE_NAME)
    table.put_item(Item=item)

    return _response(201, {"message": "Item created", "item": item})


def _response(status_code, body):
    return {
        "statusCode": status_code,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(body),
    }
