#!/usr/bin/env bash
# Quick usage for the SAM demo app (API Gateway + 2 Lambda functions + DynamoDB).
# Run these from the demo/sam directory.
set -euo pipefail

cd "$(dirname "$0")"

# 1. Validate the template for syntax errors (--lint adds stricter cfn-lint checks)
sam validate --lint

# 2. Build (resolve dependencies; needed before running locally).
#    Re-run this whenever template.yaml OR handler code changes.
#
#    NOTE: for `sam local --env-vars` to inject DYNAMODB_ENDPOINT into the
#    containers, that variable MUST be declared in template.yaml under
#    Globals > Function > Environment > Variables (it is). SAM silently drops
#    any --env-vars key that the template does not declare.
sam build

# ---------------------------------------------------------------------------
# 3. Test the API locally
#
# NOTE: `sam local start-api` only runs the Lambda FUNCTIONS locally. The
# DynamoDB table in template.yaml is NOT created locally, so a bare run gives
# `ResourceNotFoundException ... Requested resource not found` on PutItem.
# Spin up DynamoDB Local and point the functions at it (via env.json).
# ---------------------------------------------------------------------------

# 3a. Shared Docker network so the Lambda containers can reach DynamoDB Local
docker network create sam-local 2>/dev/null || true

# 3b. Start DynamoDB Local with -sharedDb.
#
# IMPORTANT: without -sharedDb, DynamoDB Local keeps a SEPARATE database per
# (access-key-id, region). A table created by the AWS CLI then isn't visible to
# the Lambda if SAM resolves different creds/region -> `Cannot do operations on
# a non-existent table`. -sharedDb makes ONE database shared across all creds
# and regions, so the table is always visible. (-inMemory means data is wiped
# on restart; drop it and add `-v $(pwd)/.ddb:/home/dynamodblocal/data` plus
# `-dbPath /home/dynamodblocal/data` if you want persistence.)
#
# Recreate the container so the -sharedDb flag definitely applies (a previously
# started container keeps its original args).
docker rm -f dynamodb-local 2>/dev/null || true
docker run -d --name dynamodb-local --network sam-local -p 8000:8000 \
  amazon/dynamodb-local -jar DynamoDBLocal.jar -inMemory -sharedDb

# Wait for it to accept connections
for i in $(seq 1 10); do
  aws dynamodb list-tables --endpoint-url http://127.0.0.1:8000 \
    --region us-east-1 >/dev/null 2>&1 && break
  sleep 1
done

# 3c. Create the table (ignore error if it already exists). With -sharedDb the
# creds/region used here don't matter for visibility, but we keep them aligned
# with env.json for clarity.
AWS_ACCESS_KEY_ID=local \
AWS_SECRET_ACCESS_KEY=local \
AWS_DEFAULT_REGION=us-east-1 \
aws dynamodb create-table \
  --endpoint-url http://127.0.0.1:8000 \
  --table-name sam-demo-items \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-east-1 2>/dev/null || echo "table already exists, continuing"

# 3d. Start the local API on the shared network, injecting the local endpoint.
#     env.json sets DYNAMODB_ENDPOINT=http://dynamodb-local:8000 per function.
sam local start-api --docker-network sam-local --env-vars env.json
# then, in another terminal:
curl -XPOST http://127.0.0.1:3000/items \
-d '{"id":"demo-1","name":"Flat White","description":"local test"}'
curl http://127.0.0.1:3000/items/demo-1

# Or test one function at a time with a sample event (same network + env):
#   sam local invoke CreateItemFunction -e events/create_item.json \
#     --docker-network sam-local --env-vars env.json
#   sam local invoke GetItemFunction -e events/get_item.json \
#     --docker-network sam-local --env-vars env.json

# Tear down DynamoDB Local when done:
#   docker rm -f dynamodb-local

# Deploy to AWS when ready (DYNAMODB_ENDPOINT is unset there, so boto3 uses
# the real regional endpoint):
#   sam deploy --guided
