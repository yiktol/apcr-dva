# coffee-ship — AWS DVA-C03 Testing & Deployment demo

A standalone, deployable demo for the "Testing and Deployment" portion of the
AWS Certified Developer – Associate (DVA-C03) material. It models a tiny
coffee-shop ordering app and walks through **how AWS lets you test before you
ship and deploy safely**: infrastructure as code, pre-ship testing, artifact
packaging, a release pipeline, and safe deployment strategies.

Everything lives under this one folder. Region is pinned to **ap-southeast-1**.

## What's in the box

| Path | What it is |
| --- | --- |
| `infra/` | AWS CDK v2 (TypeScript) app — `CoffeeShipNetworkData` + `CoffeeShipAppPipeline` stacks |
| `app/` | AWS SAM serverless app (Python 3.12 Lambda, API Gateway, SQS, DynamoDB, CodeDeploy canary) |
| `container/` | ECS/Fargate container path (stdlib Python HTTP service + Dockerfile + taskdef) |
| `events/` | Lambda test events (happy + malformed) for replay / `sam local` |
| `reference/` | "Same SQS queue three ways" teaching artifacts (CloudFormation / CDK / SAM) |
| `.kiro/hooks/` | Kiro hook that generates unit tests on Python file save |
| `deploy.sh` / `destroy.sh` | One-command stand-up and teardown |
| `FACILITATOR-RUNBOOK.md` | The five-act live demo script |

## Architecture

```
                         CodePipeline  (S3 source -> Build -> test -> approval -> prod)
                              |
  source.zip (SAM app) --> [S3 source bucket] --> [CodeBuild: sam validate + pytest + headless gate]
                                                        |
                                              (manual approval via SNS topic)
                                                        |
  Serverless path:  API Gateway --> Lambda (alias "live", CodeDeploy canary 10%/5min) --> DynamoDB "coffee-ship-orders"
                                              ^                                          ^
  Queue path:       SQS "coffee-ship-orders" |                                          |
  Container path:   ALB --> ECS Fargate service (circuit breaker) <-- image from ECR "coffee-ship"

  Networking: VPC with PUBLIC subnets only, 0 NAT gateways (cost control).
  Config:     SSM Parameter (loyalty points-per-dollar), Secrets Manager (payment API key),
              AppConfig application/environment/profile + staged deployment strategy.
```

Two deploy paths are demonstrated side by side:

- **Lambda canary** via SAM `DeploymentPreference` (`Canary10Percent5Minutes`) with a
  CloudWatch error alarm that triggers CodeDeploy rollback.
- **ECS rolling update** behind an ALB with a deployment **circuit breaker**
  (`minHealthyPercent 100` / `maxHealthyPercent 200`, rollback on failure).

The CDK app and the SAM app each declare name-consistent `coffee-ship-orders`
SQS/DynamoDB resources on purpose — that is the "declare the same thing more
than one way" teaching point, not a bug.

## Prerequisites

- An AWS account you can safely throw away (a **sandbox**, not production), with
  credentials configured for the CLI (`aws configure` / SSO profile).
- **AWS CLI v2**
- **Docker** (to build and push the container image)
- **Node.js + npm** (for the AWS CDK v2 toolkit; `cdk` is run via `npx`)
- **Python 3.12** (for the SAM app and tests)
- **AWS SAM CLI** (optional — used for `sam validate` and `sam local`; the
  pipeline build guards for its absence)

## Deploy

```bash
./deploy.sh
```

The script pins `ap-southeast-1`, then:

1. `npm install` + `cdk bootstrap` the account/region (idempotent).
2. `cdk deploy --all` — the `CoffeeShipNetworkData` and `CoffeeShipAppPipeline` stacks.
3. Builds the `container/` image and pushes it to the `coffee-ship` ECR repo.
4. Zips `app/` and uploads it as `source.zip` to the pipeline's S3 source
   bucket (resolved from the stack), which starts the `coffee-ship` pipeline.
5. Prints the **ALB URL** and the **API endpoint** at the end.

> The API endpoint comes from the `coffee-ship-app` SAM stack output
> `OrdersApiEndpoint`, which exists once the pipeline has deployed the app.

## Destroy

```bash
./destroy.sh
```

It asks you to type `destroy` to confirm, then deletes the SAM stack, empties
and removes the pipeline S3 buckets, clears the `coffee-ship` ECR images, and
runs `cdk destroy --all`.

## ⚠️ Cost warning

**This demo creates real, billable resources.** An ECS **Fargate** task, an
**Application Load Balancer**, and **CodePipeline/CodeBuild** all cost money for
every hour they exist, independent of traffic. DynamoDB and SQS are
pay-per-request and cheap at demo volume. To keep costs down the VPC uses
**public subnets only with zero NAT gateways** (NAT gateways are a common
surprise charge), Fargate is sized at **256 CPU / 512 MB** with
`desiredCount 1`, and ECR keeps only the 10 most recent images.

**Always run `./destroy.sh` as soon as the demo is over.** Leaving the ALB and
Fargate service running overnight is the most likely way to run up a bill.
