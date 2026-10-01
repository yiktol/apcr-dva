# coffee-ship — Facilitator runbook (five-act live demo)

A command-by-command script for running the DVA-C03 "Testing and Deployment"
demo live. Everything is pinned to **ap-southeast-1**. Paths are relative to
this folder (`demo/session4-coffee-ship`).

**Before you start:** `./deploy.sh` can take 15–25 minutes (CDK bootstrap +
Fargate/ALB provisioning). Deploy ahead of the session, or deploy during Act 1
and let it run while you talk. Keep this file open on screen.

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
# Container image: build, tag, push to ECR. The repo keeps the 10 newest images
# (lifecycle policy) so storage never grows unbounded.
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_URI=${ACCOUNT_ID}.dkr.ecr.ap-southeast-1.amazonaws.com/coffee-ship
aws ecr get-login-password --region ap-southeast-1 \
  | docker login --username AWS --password-stdin ${ACCOUNT_ID}.dkr.ecr.ap-southeast-1.amazonaws.com
docker build -t coffee-ship:latest container/
docker tag coffee-ship:latest ${ECR_URI}:latest
docker push ${ECR_URI}:latest
aws ecr describe-images --repository-name coffee-ship --region ap-southeast-1

# Lambda version + alias: SAM's AutoPublishAlias ('live') publishes an immutable
# version and moves the 'live' alias — CodeDeploy shifts traffic to that alias.
aws lambda list-versions-by-function --function-name coffee-ship-loyalty --region ap-southeast-1
aws lambda get-alias --function-name coffee-ship-loyalty --name live --region ap-southeast-1
```

**Services demonstrated:** Amazon ECR (build/push/tag + lifecycle policy),
Lambda versions and aliases.

---

## Act 4 — The pipeline

**Story:** one push drives source → build/test → manual approval → prod.

```bash
# Trigger the pipeline by uploading the SAM app as source.zip (deploy.sh does
# this for you). The source bucket name is auto-generated, so resolve it.
SOURCE_BUCKET=$(aws cloudformation describe-stack-resources \
  --stack-name CoffeeShipAppPipeline --region ap-southeast-1 \
  --query "StackResources[?ResourceType=='AWS::S3::Bucket'].PhysicalResourceId | [0]" --output text)
( cd app && zip -r /tmp/source.zip . -x '*__pycache__*' >/dev/null )
aws s3 cp /tmp/source.zip s3://${SOURCE_BUCKET}/source.zip --region ap-southeast-1

# Watch the stages: Source -> Build -> Deploy-Test -> Approval -> Deploy-Prod.
aws codepipeline get-pipeline-state --name coffee-ship --region ap-southeast-1 \
  --query 'stageStates[].{stage:stageName,status:latestExecution.status}'

# The Approval stage publishes to the SNS topic 'coffee-ship-approval'; approve
# it in the console (CodePipeline > coffee-ship > Approve), or via CLI with the
# token from get-pipeline-state.
```

**Services demonstrated:** CodePipeline (S3 source, no GitHub/CodeCommit),
CodeBuild, S3 artifacts, SNS manual-approval notification.

---

## Act 5 — Deploy safely, two ways

**Story:** shipping is a controlled, reversible event — canary with automatic
rollback, rolling update with a circuit breaker, and config/flag changes kept
out of code.

```bash
# 1) Lambda canary via CodeDeploy: 10% of traffic for 5 minutes, watched by a
#    CloudWatch alarm; if 'coffee-ship-loyalty-errors' fires, CodeDeploy rolls
#    back automatically. Point this out in the SAM template.
grep -n "DeploymentPreference" -A4 app/template.yaml
aws deploy list-deployments --region ap-southeast-1 \
  --query 'deployments' --output text   # watch the active canary deployment

# 2) ECS rolling update with a deployment circuit breaker. A bad image fails
#    health checks and ECS rolls the service back automatically.
aws ecs describe-services --cluster coffee-ship --services coffee-ship \
  --region ap-southeast-1 \
  --query 'services[0].deploymentConfiguration.deploymentCircuitBreaker'

# 3) AppConfig staged feature-flag flip (loyalty points on/off) — rolled out via
#    the 'coffee-ship-staged' deployment strategy, not a redeploy.
aws appconfig list-applications --region ap-southeast-1
# then start-deployment against the 'production' environment + loyalty profile.

# 4) Config vs secrets: non-secret tuning in Parameter Store, secrets in Secrets
#    Manager (never in code or env files committed to git).
aws ssm get-parameter --name /coffee-ship/loyalty/points-per-dollar --region ap-southeast-1
aws secretsmanager describe-secret --secret-id coffee-ship/payment-provider-api-key --region ap-southeast-1
```

**Services demonstrated:** CodeDeploy (Lambda canary + alarm rollback),
ECS/Fargate rolling deployment with circuit breaker, AWS AppConfig (staged
feature flag), SSM Parameter Store vs AWS Secrets Manager.

---

## Teardown (do not skip)

The ALB, Fargate task, and pipeline bill by the hour whether or not anyone is
using them. As soon as the session ends:

```bash
./destroy.sh      # type 'destroy' to confirm
```

Then confirm in the AWS console (ap-southeast-1) that no CloudFormation stacks,
load balancers, running Fargate tasks, or leftover EIPs remain.
