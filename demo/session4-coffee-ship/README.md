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
  Container release path (the pipeline this demo runs):

  source.zip (container/)                CodePipeline "coffee-ship"
       |                        Source(S3) -> Build -> Deploy-Test -> Approval -> Deploy-Prod
       v                             |          |            |           |            |
  [S3 source bucket] -----------------          |            |     (SNS approval)     |
                                                 v            v                        v
                       [CodeBuild privileged/Docker]   [ECS deploy]              [ECS deploy]
                        docker build container/          (rolling)                 (rolling)
                        push :latest + :<tag> to ECR        \                        /
                        emit imagedefinitions.json           \                      /
                                                              v                    v
                                            CloudFront --> ALB (SG = CloudFront prefix list only)
                                                               --> ECS Fargate service (circuit breaker)
                                                                     ^ image pulled from ECR "coffee-ship"

  Serverless path (separate, SAM-managed, out of this pipeline):
     API Gateway --> Lambda (alias "live", CodeDeploy canary 10%/5min) --> DynamoDB "coffee-ship-orders"
     Queue path:  SQS "coffee-ship-orders"

  Networking: the EXISTING VPC is imported from CloudFormation exports (VpcId,
              VpcCidrBlock, PublicSubnetOne/Two/Three) — this demo does NOT create a VPC.
  Edge:       The ALB is NOT reachable from the public internet directly. CloudFront sits in
              front of it, and the ALB security group only admits the AWS managed CloudFront
              origin-facing prefix list (no 0.0.0.0/0 ingress). Reach the app via the
              CloudFront URL, never the ALB DNS name.
  Config:     SSM Parameter (loyalty points-per-dollar), Secrets Manager (payment API key),
              AppConfig application/environment/profile + staged deployment strategy.
```

The container release pipeline is **real end to end**: the Build stage does a
`docker build` of `container/` and pushes the image to the `coffee-ship` ECR
repo (both `:latest` and a unique per-build tag), writes `imagedefinitions.json`
(container name `web`, image = the unique tag), and the Deploy-Test / Deploy-Prod
stages are real `EcsDeployAction`s that register a new task definition and roll
the one `coffee-ship` ECS service. Edit `container/app.py`, push a new
`source.zip`, approve, and the live response served through CloudFront changes —
there is no placeholder/no-op gate and no stand-in image.

Two safe-deploy strategies are demonstrated side by side:

- **ECS rolling update** behind an ALB with a deployment **circuit breaker**
  (`minHealthyPercent 100` / `maxHealthyPercent 200`, rollback on failure) —
  driven by the container pipeline above.
- **Lambda canary** via SAM `DeploymentPreference` (`Canary10Percent5Minutes`) with a
  CloudWatch error alarm that triggers CodeDeploy rollback (serverless path).

### Bootstrap order (important — chicken-and-egg)

The ECS service references `coffee-ship:latest`, but the ECR repo is **empty**
until the pipeline builds the first image. So:

1. Deploy the stacks (`CoffeeShipNetworkData` + `CoffeeShipAppPipeline`). This
   creates the empty ECR repo, the ECS service (which will **not** stabilize
   yet — expected), the ALB, CloudFront, and the pipeline.
2. Run the pipeline once: upload a `source.zip` containing `container/` and
   `container/buildspec.yml`. Build pushes `:latest` + a unique tag to ECR, and
   Deploy-Test rolls the service to the new image — now it becomes healthy.
3. Approve the manual gate; Deploy-Prod rolls the same service to the approved
   image. Curl the CloudFront URL to see the live app.

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
2. `cdk deploy --all` — the `CoffeeShipNetworkData` and `CoffeeShipAppPipeline`
   stacks (the VPC is imported from CloudFormation exports, not created). On
   this first deploy the ECS service will not stabilize yet because ECR is still
   empty — that is expected (see **Bootstrap order** above).
3. Zips `container/` as `source.zip` and uploads it to the pipeline's S3 source
   bucket (resolved from the stack), which starts the `coffee-ship` pipeline.
   The pipeline's CodeBuild stage does the real `docker build` + push to ECR,
   then the ECS deploy stages roll the service onto the new image.
4. Prints the **CloudFront URL** at the end — the public entry point. The ALB is
   not publicly reachable; always use the CloudFront URL.

> The CloudFront URL comes from the `CoffeeShipAppPipeline` stack output
> `CloudFrontUrl`.

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
