# coffee-shop — Facilitator runbook (five-act live walkthrough)

A command-by-command script for running the DVA-C03 "Testing and Deployment"
walkthrough live. Everything is pinned to **ap-southeast-1**. Paths are relative
to this folder (`demo/session4-coffee-ship`).

**Before you start:** `./deploy.sh` can take 15–25 minutes (CDK bootstrap +
Fargate/ALB provisioning). Deploy ahead of the session, or deploy during Act 1
and let it run while you talk. Keep this file open on screen.

**Prerequisite — Docker with buildx:** the container image is a multi-stage
build, and the seed step builds for **linux/amd64** (Fargate's architecture).
On Apple Silicon you need Docker **buildx** available (Docker Desktop ships it;
with colima, install the `docker-buildx` CLI plugin into `~/.docker/cli-plugins/`
and `docker buildx create --use`). Without buildx the cross-architecture build
fails and the seed image never lands in ECR.

**What `deploy.sh` stands up:** the **container path only** — the two ECS
environments (test + prod), the pipeline, ECR, DynamoDB, SQS, SSM, Secrets, and
AppConfig. The serverless **SAM app under `app/`** (Lambda + API Gateway) is a
separate, optional path used only for the "same thing declared more than one way"
teaching point; `deploy.sh` does **not** deploy it. Commands below that target a
Lambda function or `sam local` only apply if you have separately deployed the SAM
app (`cd app && sam deploy --guided`); otherwise treat those as read-only
walkthroughs of the template.

> Teardown reminder: this stack bills by the hour (Fargate + ALB + pipeline).
> Run `./destroy.sh` the moment the session ends — see the Teardown section.

---

## Act 1 — Infrastructure as code: the same queue three ways

**Story:** before we test or deploy anything, we define infrastructure
declaratively, and the same resource can be expressed in raw CloudFormation,
CDK, or SAM.

```bash
# Show the orders queue declared three ways and talk through the trade-offs.
sed -n '1,40p' reference/orders-queue.cfn.json      # raw CloudFormation
sed -n '1,40p' reference/orders-queue-cdk.ts        # CDK (TypeScript)
sed -n '1,40p' reference/orders-queue.sam.yaml      # SAM
cat reference/README.md                             # why / when to use each

# Validate the SAM app template before shipping.
cd app && sam validate --lint ; cd ..

# Preview the CDK change set (concept): synth renders the CloudFormation that
# 'cdk deploy' would apply; 'cdk diff' is the live change-set preview.
cd infra && npx cdk synth > /dev/null && npx cdk diff || true ; cd ..
```

**Services demonstrated:** CloudFormation, AWS CDK, AWS SAM, SQS, CloudFormation
change sets.

---

## Act 2 — Test before shipping

**Story:** we catch problems locally and in CI before any traffic sees them.

```bash
# Unit tests for the Lambda loyalty handler.
cd app && python3 -m pip install -r dev-requirements.txt && python3 -m pytest -q ; cd ..

# Replay recorded Lambda test events — happy path and the malformed/400 path.
#   events/apigw-happy.json      -> 200 with loyalty points (body is a STRING)
#   events/apigw-malformed.json  -> 400
sam local invoke --event events/apigw-happy.json      # (from app/, if SAM CLI present)
sam local invoke --event events/apigw-malformed.json

# Run the API locally.
cd app && sam local start-api ; cd ..   # then: curl -X POST localhost:3000/orders -d '{"orderId":"1","total":12.5}'

# Show the Kiro hook that regenerates unit tests whenever a .py file is saved,
# and the headless validation gate baked into the CI build.
cat .kiro/hooks/generate-tests-on-save.kiro.hook    # PostFileSave on \.py$ -> agent writes tests
grep -n "headless" app/buildspec.yml                # the fail-on-nonzero gate in CodeBuild
```

**Services demonstrated:** Lambda (test events), SAM CLI (`sam local`), pytest in
CodeBuild, Kiro agent hook, the headless review gate.

---

## Act 3 — Package the artifacts

**Story:** turn source into versioned, immutable artifacts — a container image
and a published Lambda version.

```bash
# Container image: build (linux/amd64, multi-stage) and push to ECR. The repo
# keeps the 10 newest images (lifecycle policy) so storage never grows unbounded.
# This is also exactly how deploy.sh seeds ECR before the ECS services come up.
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI=${ACCOUNT_ID}.dkr.ecr.ap-southeast-1.amazonaws.com/coffee-shop
aws ecr get-login-password --region ap-southeast-1 \
  | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.ap-southeast-1.amazonaws.com
# buildx builds for the Fargate architecture and pushes in one step.
docker buildx build --platform linux/amd64 -t ${ECR_URI}:latest --push container/
aws ecr describe-images --repository-name coffee-shop --region ap-southeast-1

# (Optional, SAM path only — skip unless you deployed the app/ SAM stack.)
# Lambda version + alias: SAM's AutoPublishAlias ('live') publishes an immutable
# version and moves the 'live' alias — CodeDeploy shifts traffic to that alias.
#   aws lambda list-versions-by-function --function-name <fn> --region ap-southeast-1
#   aws lambda get-alias --function-name <fn> --name live --region ap-southeast-1
```

**Services demonstrated:** Amazon ECR (build/push + lifecycle policy); Lambda
versions and aliases (in the optional SAM path).

---

## Act 4 — The pipeline (real, end-to-end, student-verifiable)

**Story:** a student edits the container app, pushes a new `source.zip`, and the
pipeline really rebuilds the Docker image, pushes it to ECR, and ships it to
**two distinct environments** — the **Coffee Shop web page** served through
CloudFront visibly changes. Deploy-Test is a **rolling** `EcsDeployAction` to the
`coffee-shop-test` service (reachable at `TestCloudFrontUrl`); after a manual
approval you verify on TEST, Deploy-Prod is a **CodeDeploy blue/green canary**
(`CodeDeployEcsDeployAction`) on the `coffee-shop-prod` service (reachable at
`CloudFrontUrl`). The image is a **multi-stage build**: a node stage runs
`npm ci && npm run build` on the React (Vite) SPA at `container/frontend/`, then
a python stage runs `pip install -r requirements.txt` (boto3), bakes
`frontend/dist` + `container/architecture.svg` into `/app/static`, and runs the
**boto3** `app.py` that serves both the SPA and the same-origin order API —
placing orders in the **DynamoDB `coffee-shop-orders`** table and reading the
**SSM** loyalty rate. There is no simulation and no placeholder: Build runs
`docker build`/`docker push`, Deploy-Test is a real rolling `EcsDeployAction`,
and Deploy-Prod is a real `CodeDeployEcsDeployAction` (blue/green).

> **Blue/green IS demonstrated here.** TEST uses a rolling update; PROD uses a
> CodeDeploy blue/green canary (10% for 5 min, then the rest) with automatic
> rollback. The two environments run on **separate ECS clusters**
> (`coffee-shop-test` and `coffee-shop-prod`) so the difference is real, not
> cosmetic. For a fully guided run, use `./demo-pipeline.sh` (or `DEMO-SCRIPT.md`).

**Bootstrap note:** `deploy.sh` seeds ECR with a first image before creating the
ECS services, so they come up healthy on the initial deploy. Each pipeline run's
Build emits the rolling artifact (`imagedefinitions.json`) **and** the CodeDeploy
artifacts (**`imageDetail.json`** — singular, the exact name the CodeDeploy ECS
blue/green action requires — plus `taskdef.json`, `appspec.yaml`). Deploy-Test
rolls `coffee-shop-test`; the approved Deploy-Prod runs the blue/green canary on
`coffee-shop-prod`.

```bash
# 0) Resolve the pipeline's auto-named S3 source bucket and BOTH CloudFront URLs.
SOURCE_BUCKET=$(aws cloudformation describe-stack-resources \
  --stack-name CoffeeShopAppPipeline --region ap-southeast-1 \
  --query "StackResources[?ResourceType=='AWS::S3::Bucket'].PhysicalResourceId | [0]" --output text)
CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
  --stack-name CoffeeShopAppPipeline --region ap-southeast-1 \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontUrl'].OutputValue | [0]" --output text)
TEST_CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
  --stack-name CoffeeShopAppPipeline --region ap-southeast-1 \
  --query "Stacks[0].Outputs[?OutputKey=='TestCloudFrontUrl'].OutputValue | [0]" --output text)
echo "Source bucket:   $SOURCE_BUCKET"
echo "PROD CloudFront: $CLOUDFRONT_URL"
echo "TEST CloudFront: $TEST_CLOUDFRONT_URL"

# 1) See the current live PROD page (served through CloudFront). GET / returns
#    the rendered Coffee Shop SPA (text/html 200); /health reports the running
#    version.
open "$CLOUDFRONT_URL/"              # the Coffee Shop web page in a browser
curl -s "$CLOUDFRONT_URL/health"    # -> {"status": "ok", "version": "v3"}

#    Place an order and watch it move through the states, then list recent orders.
#    POST /order writes to DynamoDB and returns the orderId + loyalty points
#    (points = floor(total) * the SSM loyalty rate /coffee-shop/loyalty/points-per-dollar).
#    The body is {items:[{id,name,qty,price}], total} (or {orderId, total}).
ORDER_ID=$(curl -s -X POST "$CLOUDFRONT_URL/order" \
  -H 'content-type: application/json' \
  -d '{"items":[{"id":"flat-white","name":"Flat White","qty":1,"price":12.5}],"total":12.5}' \
  | python3 -c 'import sys,json;print(json.load(sys.stdin)["orderId"])')
curl -s "$CLOUDFRONT_URL/order/$ORDER_ID"   # status RECEIVED (<10s)
sleep 12 ; curl -s "$CLOUDFRONT_URL/order/$ORDER_ID"   # status BREWING (10-25s)
sleep 15 ; curl -s "$CLOUDFRONT_URL/order/$ORDER_ID"   # status READY (>=25s)
curl -s "$CLOUDFRONT_URL/orders"            # the 10 most recent orders, newest first
#    In the browser the UI polls /order/{id} so the badge moves RECEIVED ->
#    BREWING -> READY on its own, and the recent-orders list updates live.

# 2) STUDENT EDIT: make a visible change the browser will show. The headline
#    scenario renames the app from "Coffee Shop" to "BeanThere Cafe" by editing the
#    APP_NAME constant in the SPA (and the <title> fallback):
sed -i '' 's/Coffee Shop/BeanThere Cafe/g' container/frontend/src/App.jsx   # macOS sed; GNU: sed -i
sed -i '' 's/Coffee Shop/BeanThere Cafe/g' container/frontend/index.html
#    You can also bump APP_VERSION in container/app.py or edit the React UI under
#    container/frontend/src/ — the node build stage rebuilds the SPA in the image.

# 3) Package container/ (with its buildspec, the frontend/ SPA source and
#    architecture.svg) as source.zip and upload it. This triggers the pipeline.
#    cd into this folder first so the zip is rooted at container/ (parity with
#    deploy.sh); node_modules/ and dist/ are excluded — the image rebuilds them.
cd demo/session4-coffee-ship   # (skip if you are already in this folder)
( zip -r /tmp/source.zip container -x '*.pyc' -x '*__pycache__*' -x '*/node_modules/*' -x '*/dist/*' >/dev/null )
aws s3 cp /tmp/source.zip s3://${SOURCE_BUCKET}/source.zip --region ap-southeast-1

# 4) Watch the stages: Source -> Build -> Deploy-Test -> Approval -> Deploy-Prod.
#    Build does the docker build + push to ECR and emits imagedefinitions.json
#    (rolling) + imageDetail.json/taskdef.json/appspec.yaml (CodeDeploy);
#    Deploy-Test is a real ECS rolling deploy to the coffee-shop-test service.
watch -n 10 "aws codepipeline get-pipeline-state --name coffee-shop --region ap-southeast-1 \
  --query 'stageStates[].{stage:stageName,status:latestExecution.status}' --output table"

# 4b) BEFORE approving, verify on TEST: coffee-shop-test already rolled, so the
#     TEST page shows 'BeanThere Cafe' while PROD still shows 'Coffee Shop'.
curl -s "$TEST_CLOUDFRONT_URL/" | grep -o 'BeanThere Cafe' | head -n1   # TEST = new name
curl -s "$CLOUDFRONT_URL/"      | grep -o 'Coffee Shop'    | head -n1   # PROD = old name

# 5) When the pipeline reaches Approval it publishes to the SNS topic
#    'coffee-shop-approval'. Approve in the console (CodePipeline > coffee-shop >
#    Review > Approve), or via CLI using the token from get-pipeline-state:
TOKEN=$(aws codepipeline get-pipeline-state --name coffee-shop --region ap-southeast-1 \
  --query "stageStates[?stageName=='Approval'].actionStates[0].latestExecution.token | [0]" --output text)
aws codepipeline put-approval-result --pipeline-name coffee-shop \
  --stage-name Approval --action-name Manual_Approval --region ap-southeast-1 \
  --result summary="approved",status=Approved --token "$TOKEN"

# 5b) Deploy-Prod runs the CodeDeployEcsDeployAction — a blue/green canary on
#     coffee-shop-prod. Watch the traffic shift (10% for 5 min, then the rest):
DEPLOYMENT_ID=$(aws deploy list-deployments --application-name coffee-shop-prod \
  --region ap-southeast-1 --query 'deployments[0]' --output text)
aws deploy get-deployment --deployment-id "$DEPLOYMENT_ID" --region ap-southeast-1 \
  --query 'deploymentInfo.{status:status,overview:deploymentOverview}'

# 6) After Deploy-Prod succeeds, reload the SAME PROD CloudFront URL and SEE the
#    change (CloudFront caching is disabled, so it is immediate once the
#    blue/green cutover finishes). The web page now shows 'BeanThere Cafe'.
open "$CLOUDFRONT_URL/"              # reload: the PROD page now shows 'BeanThere Cafe'
curl -s "$CLOUDFRONT_URL/" | grep -o 'BeanThere Cafe' | head -n1
```

**Services demonstrated:** CodePipeline (S3 source, no GitHub/CodeCommit),
CodeBuild (privileged multi-stage Docker build — React/Vite SPA + python
runtime — then ECR push), Amazon ECR, a rolling `EcsDeployAction` to TEST **and**
a CodeDeploy **blue/green** `CodeDeployEcsDeployAction` to PROD across two ECS
clusters, SNS manual-approval notification, CloudFront in front of each ALB
(`TestCloudFrontUrl` for test, `CloudFrontUrl` for prod), serving the rendered
Coffee Shop web page backed by
DynamoDB orders (RECEIVED -> BREWING -> READY) and the SSM loyalty rate.

---

## Act 5 — Deploy safely, three ways

**Story:** shipping is a controlled, reversible event — a Lambda canary with
automatic rollback, an ECS **rolling** update to TEST with a circuit breaker, an
ECS **blue/green** canary to PROD via CodeDeploy, and config/flag changes kept
out of code.

```bash
# 1) Lambda canary via CodeDeploy (SAM path — the template, not a live resource
#    unless you deployed app/). SAM's DeploymentPreference shifts 10% for 5
#    minutes watched by a CloudWatch alarm, rolling back automatically on alarm.
#    Show it in the template:
grep -n "DeploymentPreference" -A4 app/template.yaml

# 2) TEST — ECS ROLLING update with a deployment circuit breaker, on the
#    coffee-shop-test cluster/service. A bad image fails health checks and ECS
#    rolls the service back automatically.
aws ecs describe-services --cluster coffee-shop-test --services coffee-shop-test \
  --region ap-southeast-1 \
  --query 'services[0].deploymentConfiguration.deploymentCircuitBreaker'

# 2b) PROD — ECS BLUE/GREEN via CodeDeploy, on the coffee-shop-prod cluster/service
#     (DeploymentController == CODE_DEPLOY). The CodeDeploy app/deployment group
#     'coffee-shop-prod' runs the canary and auto-rolls-back on failure OR on the
#     'coffee-shop-prod-unhealthy-hosts' alarm. This is the blue/green path.
aws ecs describe-services --cluster coffee-shop-prod --services coffee-shop-prod \
  --region ap-southeast-1 \
  --query 'services[0].deploymentController.type'   # -> "CODE_DEPLOY"
aws deploy get-deployment-group --application-name coffee-shop-prod \
  --deployment-group-name coffee-shop-prod --region ap-southeast-1 \
  --query 'deploymentGroupInfo.{config:deploymentConfigName,style:deploymentStyle,autoRollback:autoRollbackConfiguration}'

# 3) AppConfig staged feature-flag flip (loyalty points on/off) — rolled out via
#    the 'coffee-shop-staged' deployment strategy, not a redeploy.
aws appconfig list-applications --region ap-southeast-1
# then start-deployment against the 'production' environment + loyalty profile.

# 4) Config vs secrets: non-secret tuning in Parameter Store, secrets in Secrets
#    Manager (never in code or env files committed to git).
aws ssm get-parameter --name /coffee-shop/loyalty/points-per-dollar --region ap-southeast-1
aws secretsmanager describe-secret --secret-id coffee-shop/payment-provider-api-key --region ap-southeast-1
```

**Services demonstrated:** CodeDeploy (Lambda canary + alarm rollback **and**
ECS blue/green canary for the `coffee-shop-prod` service), ECS/Fargate rolling
deployment with circuit breaker (the `coffee-shop-test` service), AWS AppConfig
(staged feature flag), SSM Parameter Store vs AWS Secrets Manager.

---

## Teardown (do not skip)

The ALB, Fargate task, and pipeline bill by the hour whether or not anyone is
using them. As soon as the session ends:

```bash
./destroy.sh      # type 'destroy' to confirm
```

Then confirm in the AWS console (ap-southeast-1) that no CloudFormation stacks,
load balancers, running Fargate tasks, or leftover EIPs remain.
