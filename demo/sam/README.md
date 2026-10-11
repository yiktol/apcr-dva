# SAM Demo — Validate and Test Locally

A sample AWS SAM application with the exact shape from the scenario:

- **API Gateway API** (`ItemsApi`)
- **Two Lambda functions** (`CreateItemFunction` → `POST /items`, `GetItemFunction` → `GET /items/{id}`)
- **DynamoDB table** (`ItemsTable`)

```
demo/sam/
├── template.yaml            # SAM template (API + 2 functions + table)
├── events/
│   ├── create_item.json     # Sample API event for POST /items
│   └── get_item.json        # Sample API event for GET /items/{id}
└── src/
    ├── create_item/app.py   # create_handler
    └── get_item/app.py      # get_handler
```

## The scenario question

> Which two AWS SAM CLI commands should the developer use to **validate** the
> template for syntax errors and **test** the API locally before deploying?

**Answer:**

1. **`sam validate`** — checks the SAM template for syntax errors (validates it
   against the SAM/CloudFormation spec). Add `--lint` for extra cfn-lint checks.
2. **`sam local start-api`** — starts a local HTTP server that emulates API
   Gateway so you can call the endpoints locally. (`sam local invoke` is the
   other local-testing command, used to test a single function directly.)

So the two commands are **`sam validate`** and **`sam local start-api`**
(with `sam local invoke` as the alternative for testing one function at a time).

## Commands

### 1. Validate the template for syntax errors

```bash
cd demo/sam
sam validate
# stricter linting:
sam validate --lint
```

### 2. Build (resolves dependencies; needed before local run)

```bash
sam build
```

### 3. Test the API locally

Emulate the whole API Gateway locally (requires Docker running):

```bash
sam local start-api
# then, in another terminal:
curl -XPOST http://127.0.0.1:3000/items \
  -d '{"id":"demo-1","name":"Flat White","description":"local test"}'
curl http://127.0.0.1:3000/items/demo-1
```

Or invoke a single Lambda function directly with a sample event:

```bash
sam local invoke CreateItemFunction -e events/create_item.json
sam local invoke GetItemFunction   -e events/get_item.json
```

## Testing locally with DynamoDB (important)

`sam local start-api` only runs the **Lambda functions** locally. The DynamoDB
table declared in `template.yaml` is **not** created anywhere, so a bare local
run fails with:

```
ResourceNotFoundException ... when calling the PutItem operation:
Requested resource not found
```

To exercise the full flow locally, run **DynamoDB Local** in Docker and point
the functions at it. The handlers read an optional `DYNAMODB_ENDPOINT` env var
(see `env.json`); when it is unset — as on AWS — boto3 uses the real regional
endpoint.

```bash
# shared network so the Lambda containers can reach DynamoDB Local by name
docker network create sam-local

# start DynamoDB Local
docker run -d --name dynamodb-local --network sam-local -p 8000:8000 \
  amazon/dynamodb-local

# create the table
aws dynamodb create-table \
  --endpoint-url http://127.0.0.1:8000 \
  --table-name sam-demo-items \
  --attribute-definitions AttributeName=id,AttributeType=S \
  --key-schema AttributeName=id,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST --region us-east-1

# run the API on that network, injecting the local endpoint
sam local start-api --docker-network sam-local --env-vars env.json
```

`commands.sh` wraps all of the above. From the container's point of view
DynamoDB Local is reachable at `http://dynamodb-local:8000` (the container name
on the shared network), which is what `env.json` sets.

## Notes

- `sam local` requires Docker to be installed and running.
- Re-run `sam build` after editing handler code so the local containers pick up
  the change.
- `GetItemFunction` returns `404` for `demo-1` until `CreateItemFunction` has
  written it to the same table.
- Deploy when ready with `sam deploy --guided`.
