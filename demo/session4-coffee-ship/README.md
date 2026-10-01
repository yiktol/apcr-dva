# coffee-shop — AWS DVA-C03 Testing & Deployment project

A standalone, deployable project for the "Testing and Deployment" portion of the
AWS Certified Developer – Associate (DVA-C03) material. It models a tiny
coffee-shop ordering app and walks through **how AWS lets you test before you
ship and deploy safely**: infrastructure as code, pre-ship testing, artifact
packaging, a release pipeline, and safe deployment strategies.

Everything lives under this one folder. Region is pinned to **ap-southeast-1**.

## What's in the box

| Path | What it is |
| --- | --- |
| `infra/` | AWS CDK v2 (TypeScript) app — `CoffeeShopNetworkData` + `CoffeeShopAppPipeline` stacks |
| `app/` | AWS SAM serverless app (Python 3.12 Lambda, API Gateway, SQS, DynamoDB, CodeDeploy canary) |
| `container/` | ECS/Fargate container path: React (Vite) SPA at `container/frontend/`, a **boto3** Python HTTP service (`app.py`) that serves the baked SPA + same-origin order API (DynamoDB orders, SSM loyalty rate), the `container/architecture.svg` diagram (built by `container/build_diagram.py` from official AWS icons), and a multi-stage `Dockerfile` (node build stage + python runtime that `pip install`s boto3) |
| `events/` | Lambda test events (happy + malformed) for replay / `sam local` |
| `reference/` | "Same SQS queue three ways" teaching artifacts (CloudFormation / CDK / SAM) |
| `.kiro/hooks/` | Kiro hook that generates unit tests on Python file save |
| `deploy.sh` / `destroy.sh` | One-command stand-up and teardown |
| `FACILITATOR-RUNBOOK.md` | The five-act facilitator script |

## Architecture

```
  Container release path (the pipeline this project runs) — ONE pipeline, TWO envs:

  source.zip (container/)                CodePipeline "coffee-shop"
       |                   Source(S3) -> Build -> Deploy-Test -> Approval -> Deploy-Prod
       v                        |          |            |           |            |
  [S3 source bucket] ------------          |            |     (SNS approval)     |
                                           v            v                        v
                       [CodeBuild privileged/Docker]  EcsDeployAction      CodeDeployEcsDeployAction
                        multi-stage docker build       (ROLLING to          (BLUE/GREEN canary
                        (node: npm run build SPA         coffee-shop-test)    10%/5min to
                         -> python runtime serves it)                         coffee-shop-prod,
                        push :latest + :<tag> to ECR    \                     alarm auto-rollback)
                        emit imagedefinitions.json +     \                     /
                        imageDetails.json/taskdef/appspec v                   v
                                                   TEST ECS service     PROD ECS service
                                                   (coffee-shop-test)   (coffee-shop-prod,
                                                          |              CODE_DEPLOY controller)
        Browser --> CloudFront (TestCloudFrontUrl) --> test ALB --------'      |
       (Coffee Shop                                                            |
        web app, SPA)                                                          |
        Browser --> CloudFront (CloudFrontUrl) --> prod ALB (blue/green TGs) --'
                                       prod task pulls image from ECR "coffee-shop",
                                       serves the baked SPA + same-origin order API
                                       (boto3) --> DynamoDB "coffee-shop-orders"
                                               --> SSM loyalty points-per-dollar

  Serverless path (separate, SAM-managed, out of this pipeline):
     API Gateway --> Lambda (alias "live", CodeDeploy canary 10%/5min) --> DynamoDB "coffee-shop-orders"
     Queue path:  SQS "coffee-shop-orders"

  Networking: the VPC comes from CloudFormation exports (VpcId, VpcCidrBlock,
              PublicSubnetOne/Two/Three).
  Edge:       CloudFront sits in front of each ALB (CloudFrontUrl -> prod,
              TestCloudFrontUrl -> test); reach each app via its CloudFront URL.
  Config:     SSM Parameter (loyalty points-per-dollar), Secrets Manager (payment API key),
              AppConfig application/environment/profile + staged deployment strategy.
```

### The web app (what CloudFront serves)

CloudFront serves the **Coffee Shop web app** — a React (Vite) single-page app
baked into the container image. There are two front doors: **CloudFrontUrl**
serves the PROD environment (`coffee-shop-prod`) and **TestCloudFrontUrl** serves
the TEST environment (`coffee-shop-test`); both run the same image. The browser
loads HTML/JS from `GET /`, and the app calls the **same-origin** JSON API (no
CORS, no base URL):

- `POST /order` places an order in the **DynamoDB `coffee-shop-orders`** table and
  returns the new order (id + loyalty points earned).
- `GET /order/{id}` returns one order with its **current status**, computed from
  how long ago it was placed: `RECEIVED` (< 10s), `BREWING` (10–25s), `READY`
  (≥ 25s). The SPA polls this so you watch an order move through the three states.
- `GET /orders` returns the **10 most recent orders** (newest first) for the
  recent-orders list in the UI.
- `GET /health` returns `{"status":"ok","version":APP_VERSION}` and is always
  **200** (even with no AWS credentials or DynamoDB unreachable), so the ALB
  health check — which targets `GET /` — stays green. The SPA shows the version
  in its header.

Loyalty points are `floor(total) * rate`, where the **rate comes from the SSM
Parameter** `/coffee-shop/loyalty/points-per-dollar` (cached in-process, default
`10` if SSM is unavailable). The container uses **boto3** to reach DynamoDB and
SSM; `boto3` is imported under a guard so `python3 -m py_compile` and `/health`
still work without it.

The image is built by a **multi-stage `Dockerfile`**: a `node` stage runs
`npm ci && npm run build` on `container/frontend/` to produce `dist/`, then a
`python:3.12-slim` runtime stage runs `pip install -r requirements.txt` (boto3,
the one runtime dependency), copies `frontend/dist` and `container/architecture.svg`
into `/app/static`, and runs `app.py`. npm never runs in the final image.

### The architecture diagram

`container/architecture.svg` is **generated** by `container/build_diagram.py`,
which base64-embeds the official AWS service icons (the `*_64.svg` files under
the repo's `aws-icons/` set, including the **CodeDeploy** icon) so the SVG is
fully self-contained. It draws the **two environments distinctly** — TEST
(User → CloudFront `TestCloudFrontUrl` → test ALB → `coffee-shop-test` ECS,
deployed by a rolling `EcsDeployAction`) and PROD (User → CloudFront
`CloudFrontUrl` → prod ALB with blue/green target groups → `coffee-shop-prod`
ECS on the `CODE_DEPLOY` controller) — plus the CI/CD path (S3 `source.zip` →
EventBridge → CodePipeline → CodeBuild → ECR → rolling to TEST, then Approval,
then `CodeDeployEcsDeployAction` blue/green to PROD). Regenerate it with
`python3 container/build_diagram.py`, then copy it to the top-level
`architecture.svg` and run `rsvg-convert container/architecture.svg -o
architecture.png` to refresh the PNG.

The container release pipeline is **real end to end**: the Build stage runs that
multi-stage `docker build` of `container/` (so `npm run build` happens inside the
image) and pushes to the `coffee-shop` ECR repo (both `:latest` and a unique
per-build tag), writes `imagedefinitions.json` (container name `web`, image = the
unique tag) for the rolling TEST deploy and `imageDetails.json` + `taskdef.json`
+ `appspec.yaml` for the CodeDeploy PROD deploy. Deploy-Test is a real rolling
`EcsDeployAction` to the `coffee-shop-test` service; Deploy-Prod is a real
`CodeDeployEcsDeployAction` doing a blue/green canary on the `coffee-shop-prod`
service.

**Student edit loop:** edit the React app under `container/frontend/src/` (menu,
copy, styling) or bump `APP_VERSION` / change the API in `container/app.py`, push
a new `source.zip`, verify the change on the **TestCloudFrontUrl** page, approve
the manual gate, and the **Coffee Shop** web page served through the
**CloudFrontUrl** (PROD) page visibly changes. Run `./demo-pipeline.sh` (or follow
`DEMO-SCRIPT.md`) to walk a `Coffee Shop` → `BeanThere Cafe` rename through the
whole flow. There is no placeholder/no-op gate and no stand-in image.

Two safe-deploy strategies are demonstrated **side by side in the container
pipeline itself** (plus a third on the serverless path):

- **TEST — ECS rolling update** behind the test ALB with a deployment **circuit
  breaker** (`minHealthyPercent 100` / `maxHealthyPercent 200`, rollback on
  failure), via a rolling `EcsDeployAction` to `coffee-shop-test`.
- **PROD — ECS blue/green via CodeDeploy** on `coffee-shop-prod` (CODE_DEPLOY
  controller, two target groups, prod + test listeners): a
  `CANARY_10PERCENT_5MINUTES` traffic shift with automatic rollback on failure
  **and** on the `coffee-shop-prod-unhealthy-hosts` alarm. **Blue/green IS now
  demonstrated** here (it was not before — both prod and test used to be
  rolling on one cluster).
- **Lambda canary** via SAM `DeploymentPreference` (`Canary10Percent5Minutes`) with a
  CloudWatch error alarm that triggers CodeDeploy rollback (serverless path).

### Bootstrap order (important — chicken-and-egg)

Both ECS services reference `coffee-shop:latest`, but the ECR repo starts
**empty**, and the PROD service is on the `CODE_DEPLOY` controller. If the ECS
services were created before any image existed, they could not pull `:latest`
and would never stabilize (the test circuit breaker trips; the prod blue task
set never comes up). So the ECR repo is created in `CoffeeShopNetworkData`
(the first stack) and seeded **before** the services exist. `deploy.sh` does
exactly this, in order:

1. Deploy **`CoffeeShopNetworkData`** — creates the empty ECR repo (`coffee-shop`,
   keep-10 lifecycle), DynamoDB, SQS, SSM, Secrets, AppConfig. No services yet.
2. **Seed ECR**: `docker build --platform linux/amd64` the `container/` image and
   push it as `coffee-shop:latest`. The `--platform linux/amd64` is required —
   Fargate runs X86_64, so an arm64 host (Apple Silicon) must cross-build or the
   task fails to run.
3. Deploy **`CoffeeShopAppPipeline`** — now the **two** ECS services
   (`coffee-shop-test`, `coffee-shop-prod`) find `coffee-shop:latest` in ECR and
   stabilize. This also creates **two** ALBs, **two** CloudFront distributions
   (`CloudFrontUrl` + `TestCloudFrontUrl`), the CodeDeploy application/deployment
   group for prod, and the pipeline.
4. Run the pipeline once: `deploy.sh` uploads a `source.zip` of `container/` (SPA
   source at `container/frontend/`, `architecture.svg`, `app.py`, `Dockerfile`,
   `buildspec.yml`; local `node_modules/`/`dist/` excluded and rebuilt in the
   image). Build runs the multi-stage docker build, pushes `:latest` + a unique
   tag, and emits the rolling artifact (`imagedefinitions.json`) **and** the
   CodeDeploy artifacts (**`imageDetail.json`** — singular, the exact name the
   CodeDeployToECS blue/green action requires — plus `taskdef.json`,
   `appspec.yaml`). Deploy-Test rolls `coffee-shop-test`; verify it at
   `TestCloudFrontUrl`.
5. Approve the manual gate. Deploy-Prod runs the `CodeDeployEcsDeployAction`
   blue/green canary (10%/5min) on `coffee-shop-prod`: the green task set comes
   up (it needs the `/ecs/coffee-shop-prod` log group + `logs:CreateLogStream`
   on the prod execution role — both wired in the CDK), traffic shifts 10% →
   100% with alarm auto-rollback armed, and `CloudFrontUrl` shows the new app.

### Two gotchas this project already handles (so you don't rediscover them)

- **`imageDetail.json` is singular.** The rolling ECS deploy action reads
  `imagedefinitions.json`; the CodeDeploy ECS **blue/green** action reads
  `imageDetail.json` (singular). The buildspec emits both. Using the plural name
  for blue/green fails with `Exception while trying to read the image artifact
  file` before any deployment is created.
- **The prod task's log group must exist and be writable.** The rendered
  `taskdef.json` logs to `/ecs/coffee-shop-prod`; the CDK creates that log group
  explicitly and grants the prod execution role `logs:CreateLogStream`, or the
  green task fails with `TaskFailedToStart` and the canary stalls at 0%.

### Re-deploying onto an already-running stack

`deploy.sh` is written for a **clean** account. The ECR repo lives in
`CoffeeShopNetworkData`; if you are updating an older deployment where ECR was in
`CoffeeShopAppPipeline`, a straight `cdk deploy` will try to move the repo
(destroy + recreate), orphaning images. For a clean reproduction, run
`./destroy.sh` first (or use a fresh account), then `./deploy.sh`.

The CDK app and the SAM app each declare name-consistent `coffee-shop-orders`
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
2. `cdk deploy --all` — the `CoffeeShopNetworkData` and `CoffeeShopAppPipeline`
   stacks (the VPC comes from CloudFormation exports). On
   this first deploy the ECS service will not stabilize yet because ECR is still
   empty — that is expected (see **Bootstrap order** above).
3. Zips `container/` as `source.zip` (SPA source + `architecture.svg` included;
   `node_modules/`/`dist/` excluded) and uploads it to the pipeline's S3 source
   bucket (resolved from the stack), which starts the `coffee-shop` pipeline.
   The pipeline's CodeBuild stage does the real multi-stage `docker build` (which
   runs `npm run build` for the SPA) + push to ECR, then the ECS deploy stages
   roll the service onto the new image.
4. Prints **both CloudFront URLs** at the end — `CloudFront URL` (PROD) and
   `Test CloudFront` (TEST). Use the CloudFront URLs. Open the PROD URL in a
   browser to see the Coffee Shop web app.

> The URLs come from the `CoffeeShopAppPipeline` stack outputs `CloudFrontUrl`
> (PROD) and `TestCloudFrontUrl` (TEST).

### Run the pipeline

Once deployed and healthy, run the guided, step-by-step pipeline walkthrough:

```bash
./demo-pipeline.sh
```

It renames the app from **Coffee Shop** to **BeanThere Cafe**, uploads one
`source.zip`, rolls `coffee-shop-test`, pauses so you verify the change on
`TestCloudFrontUrl` (while PROD still shows **Coffee Shop**), then — after you
approve — runs the CodeDeploy **blue/green** canary to `coffee-shop-prod` and
shows PROD serving **BeanThere Cafe**. `DEMO-SCRIPT.md` has the same steps as
copy-pasteable commands.

## Destroy

```bash
./destroy.sh
```

It asks you to type `destroy` to confirm, then deletes the SAM stack, empties
and removes the pipeline S3 buckets, clears the `coffee-shop` ECR images, and
runs `cdk destroy --all`. The two-environment resources — the second CloudFront
distribution (`TestCloudFrontUrl`) and the `coffee-shop-prod` CodeDeploy
application/deployment group — are in-stack, so `cdk destroy --all` removes them
automatically; no extra manual deletion is needed.

## ⚠️ Cost warning

**This project creates real, billable resources.** An ECS **Fargate** task, an
**Application Load Balancer**, and **CodePipeline/CodeBuild** all cost money for
every hour they exist, independent of traffic. DynamoDB and SQS are
pay-per-request and cheap at this volume. To keep costs down the VPC uses
**public subnets only with zero NAT gateways** (NAT gateways are a common
surprise charge), Fargate is sized at **256 CPU / 512 MB** with
`desiredCount 1`, and ECR keeps only the 10 most recent images.

**Always run `./destroy.sh` as soon as you are done.** Leaving the ALB and
Fargate service running overnight is the most likely way to run up a bill.
