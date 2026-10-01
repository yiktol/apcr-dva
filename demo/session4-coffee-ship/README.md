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
| `container/` | ECS/Fargate container path: React (Vite) SPA at `container/frontend/`, a **boto3** Python HTTP service (`app.py`) that serves the baked SPA + same-origin order API (DynamoDB orders, SSM loyalty rate), the `container/architecture.svg` diagram (built by `container/build_diagram.py` from official AWS icons), and a multi-stage `Dockerfile` (node build stage + python runtime that `pip install`s boto3) |
| `events/` | Lambda test events (happy + malformed) for replay / `sam local` |
| `reference/` | "Same SQS queue three ways" teaching artifacts (CloudFormation / CDK / SAM) |
| `.kiro/hooks/` | Kiro hook that generates unit tests on Python file save |
| `deploy.sh` / `destroy.sh` | One-command stand-up and teardown |
| `FACILITATOR-RUNBOOK.md` | The five-act live demo script |

## Architecture

```
  Container release path (the pipeline this demo runs) — ONE pipeline, TWO envs:

  source.zip (container/)                CodePipeline "coffee-ship"
       |                   Source(S3) -> Build -> Deploy-Test -> Approval -> Deploy-Prod
       v                        |          |            |           |            |
  [S3 source bucket] ------------          |            |     (SNS approval)     |
                                           v            v                        v
                       [CodeBuild privileged/Docker]  EcsDeployAction      CodeDeployEcsDeployAction
                        multi-stage docker build       (ROLLING to          (BLUE/GREEN canary
                        (node: npm run build SPA         coffee-ship-test)    10%/5min to
                         -> python runtime serves it)                         coffee-ship-prod,
                        push :latest + :<tag> to ECR    \                     alarm auto-rollback)
                        emit imagedefinitions.json +     \                     /
                        imageDetails.json/taskdef/appspec v                   v
                                                   TEST ECS service     PROD ECS service
                                                   (coffee-ship-test)   (coffee-ship-prod,
                                                          |              CODE_DEPLOY controller)
        Browser --> CloudFront (TestCloudFrontUrl) --> test ALB --------'      |
       (Coffee Shop                                   (SG = CF prefix list)    |
        web app, SPA)                                                          |
        Browser --> CloudFront (CloudFrontUrl) --> prod ALB (blue/green TGs) --'
                                                   (SG = CF prefix list only)
                                       prod task pulls image from ECR "coffee-ship",
                                       serves the baked SPA + same-origin order API
                                       (boto3) --> DynamoDB "coffee-ship-orders"
                                               --> SSM loyalty points-per-dollar

  Serverless path (separate, SAM-managed, out of this pipeline):
     API Gateway --> Lambda (alias "live", CodeDeploy canary 10%/5min) --> DynamoDB "coffee-ship-orders"
     Queue path:  SQS "coffee-ship-orders"

  Networking: the EXISTING VPC is imported from CloudFormation exports (VpcId,
              VpcCidrBlock, PublicSubnetOne/Two/Three) — this demo does NOT create a VPC.
  Edge:       Neither ALB is reachable from the public internet directly. A CloudFront
              distribution sits in front of each (CloudFrontUrl -> prod ALB, TestCloudFrontUrl
              -> test ALB), and each ALB security group only admits the AWS managed CloudFront
              origin-facing prefix list (no 0.0.0.0/0 ingress). Reach each app via its
              CloudFront URL, never the ALB DNS name.
  Config:     SSM Parameter (loyalty points-per-dollar), Secrets Manager (payment API key),
              AppConfig application/environment/profile + staged deployment strategy.
```

### The web app (what CloudFront serves)

CloudFront serves the **Coffee Shop web app** — a React (Vite) single-page app
baked into the container image. There are two front doors: **CloudFrontUrl**
serves the PROD environment (`coffee-ship-prod`) and **TestCloudFrontUrl** serves
the TEST environment (`coffee-ship-test`); both run the same image. The browser
loads HTML/JS from `GET /`, and the app calls the **same-origin** JSON API (no
CORS, no base URL):

- `POST /order` places an order in the **DynamoDB `coffee-ship-orders`** table and
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
Parameter** `/coffee-ship/loyalty/points-per-dollar` (cached in-process, default
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
(User → CloudFront `TestCloudFrontUrl` → test ALB → `coffee-ship-test` ECS,
deployed by a rolling `EcsDeployAction`) and PROD (User → CloudFront
`CloudFrontUrl` → prod ALB with blue/green target groups → `coffee-ship-prod`
ECS on the `CODE_DEPLOY` controller) — plus the CI/CD path (S3 `source.zip` →
EventBridge → CodePipeline → CodeBuild → ECR → rolling to TEST, then Approval,
then `CodeDeployEcsDeployAction` blue/green to PROD). Regenerate it with
`python3 container/build_diagram.py`, then copy it to the top-level
`architecture.svg` and run `rsvg-convert container/architecture.svg -o
architecture.png` to refresh the PNG.

The container release pipeline is **real end to end**: the Build stage runs that
multi-stage `docker build` of `container/` (so `npm run build` happens inside the
image) and pushes to the `coffee-ship` ECR repo (both `:latest` and a unique
per-build tag), writes `imagedefinitions.json` (container name `web`, image = the
unique tag) for the rolling TEST deploy and `imageDetails.json` + `taskdef.json`
+ `appspec.yaml` for the CodeDeploy PROD deploy. Deploy-Test is a real rolling
`EcsDeployAction` to the `coffee-ship-test` service; Deploy-Prod is a real
`CodeDeployEcsDeployAction` doing a blue/green canary on the `coffee-ship-prod`
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
  failure), via a rolling `EcsDeployAction` to `coffee-ship-test`.
- **PROD — ECS blue/green via CodeDeploy** on `coffee-ship-prod` (CODE_DEPLOY
  controller, two target groups, prod + test listeners): a
  `CANARY_10PERCENT_5MINUTES` traffic shift with automatic rollback on failure
  **and** on the `coffee-ship-prod-unhealthy-hosts` alarm. **Blue/green IS now
  demonstrated** by this demo (it was not before — both prod and test used to be
  rolling on one cluster).
- **Lambda canary** via SAM `DeploymentPreference` (`Canary10Percent5Minutes`) with a
  CloudWatch error alarm that triggers CodeDeploy rollback (serverless path).

### Bootstrap order (important — chicken-and-egg)

Both ECS services reference `coffee-ship:latest`, but the ECR repo is **empty**
until the pipeline builds the first image, and the PROD service is on the
`CODE_DEPLOY` controller (CodeDeploy owns its task set after the first run). So:

1. Deploy the stacks (`CoffeeShipNetworkData` + `CoffeeShipAppPipeline`). This
   creates the empty ECR repo, **two** ECS services (`coffee-ship-test` and
   `coffee-ship-prod` — neither stabilizes yet, expected), **two** ALBs, **two**
   CloudFront distributions (`CloudFrontUrl` + `TestCloudFrontUrl`), the
   CodeDeploy application/deployment group for prod, and the pipeline.
2. Run the pipeline once: upload a `source.zip` containing `container/` (the SPA
   source at `container/frontend/`, `container/architecture.svg`, `app.py`,
   `Dockerfile`, and `container/buildspec.yml`; local `node_modules/`/`dist/`
   are excluded and rebuilt inside the image). Build runs the multi-stage docker
   build, pushes `:latest` + a unique tag to ECR, and emits the rolling artifact
   (`imagedefinitions.json`) **and** the CodeDeploy artifacts
   (`imageDetails.json`, `taskdef.json`, `appspec.yaml`). Deploy-Test rolls the
   `coffee-ship-test` service — it becomes healthy and is reachable at
   `TestCloudFrontUrl`.
3. Verify on `TestCloudFrontUrl`, then approve the manual gate. Deploy-Prod runs
   the `CodeDeployEcsDeployAction` blue/green canary on `coffee-ship-prod` — the
   first run brings the green task set up and shifts traffic, making the prod
   service healthy. Curl `CloudFrontUrl` to see the live PROD app.

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
3. Zips `container/` as `source.zip` (SPA source + `architecture.svg` included;
   `node_modules/`/`dist/` excluded) and uploads it to the pipeline's S3 source
   bucket (resolved from the stack), which starts the `coffee-ship` pipeline.
   The pipeline's CodeBuild stage does the real multi-stage `docker build` (which
   runs `npm run build` for the SPA) + push to ECR, then the ECS deploy stages
   roll the service onto the new image.
4. Prints **both CloudFront URLs** at the end — `CloudFront URL` (PROD) and
   `Test CloudFront` (TEST). Neither ALB is publicly reachable; always use the
   CloudFront URLs. Open the PROD URL in a browser to see the Coffee Shop web app.

> The URLs come from the `CoffeeShipAppPipeline` stack outputs `CloudFrontUrl`
> (PROD) and `TestCloudFrontUrl` (TEST).

### Demo the pipeline

Once deployed and healthy, run the guided, step-by-step pipeline demo:

```bash
./demo-pipeline.sh
```

It renames the app from **Coffee Shop** to **BeanThere Cafe**, uploads one
`source.zip`, rolls `coffee-ship-test`, pauses so you verify the change on
`TestCloudFrontUrl` (while PROD still shows **Coffee Shop**), then — after you
approve — runs the CodeDeploy **blue/green** canary to `coffee-ship-prod` and
shows PROD serving **BeanThere Cafe**. `DEMO-SCRIPT.md` has the same steps as
copy-pasteable commands.

## Destroy

```bash
./destroy.sh
```

It asks you to type `destroy` to confirm, then deletes the SAM stack, empties
and removes the pipeline S3 buckets, clears the `coffee-ship` ECR images, and
runs `cdk destroy --all`. The two-environment resources — the second CloudFront
distribution (`TestCloudFrontUrl`) and the `coffee-ship-prod` CodeDeploy
application/deployment group — are in-stack, so `cdk destroy --all` removes them
automatically; no extra manual deletion is needed.

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
