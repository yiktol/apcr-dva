# Coffee Shop — pipeline demo script (copy-paste)

A step-by-step walkthrough of the Coffee Shop release pipeline that you can run
by hand, command by command. It mirrors `demo-pipeline.sh` (which runs the same
steps with narration and `read -p` pauses) — use the script for a hands-off
demo, or paste these commands one at a time to explain each stage.

The headline: a single pipeline run takes a real code change — renaming the app
from **"Coffee Shop"** to **"BeanThere Cafe"** — through a **rolling** deploy to
**TEST**, a **manual approval** gate you verify against the TEST CloudFront URL,
then a **CodeDeploy blue/green canary** to **PROD**. Nothing is simulated.

Prereq: `./deploy.sh` has already stood up `CoffeeShipAppPipeline` and the first
pipeline run has made both ECS services healthy. Region is **ap-southeast-1**.

```bash
export AWS_REGION=ap-southeast-1
export AWS_DEFAULT_REGION=ap-southeast-1
```

## 1. Resolve both environments and the source bucket

PROD is the `CloudFrontUrl` output; TEST is the `TestCloudFrontUrl` output. The
source bucket is the pipeline's auto-named versioned S3 bucket (`[0]`).

```bash
SOURCE_BUCKET=$(aws cloudformation describe-stack-resources \
  --stack-name CoffeeShipAppPipeline \
  --query "StackResources[?ResourceType=='AWS::S3::Bucket'].PhysicalResourceId | [0]" \
  --output text)
CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
  --stack-name CoffeeShipAppPipeline \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontUrl'].OutputValue | [0]" \
  --output text)
TEST_CLOUDFRONT_URL=$(aws cloudformation describe-stacks \
  --stack-name CoffeeShipAppPipeline \
  --query "Stacks[0].Outputs[?OutputKey=='TestCloudFrontUrl'].OutputValue | [0]" \
  --output text)
echo "Source bucket  : $SOURCE_BUCKET"
echo "PROD CloudFront: $CLOUDFRONT_URL"
echo "TEST CloudFront: $TEST_CLOUDFRONT_URL"
```

## 2. Baseline — PROD currently serves "Coffee Shop"

```bash
curl -s "$CLOUDFRONT_URL/" | grep -o 'Coffee Shop' | head -n1
curl -s "$CLOUDFRONT_URL/health"
```

## 3. The student edit — rename "Coffee Shop" to "BeanThere Cafe"

A real source edit the pipeline will ship: the `APP_NAME` constant in `App.jsx`
and the `<title>` in `index.html`. (GNU sed shown; on macOS use `sed -i ''`.)

```bash
sed -i "s/Coffee Shop/BeanThere Cafe/g" container/frontend/src/App.jsx
sed -i "s/Coffee Shop/BeanThere Cafe/g" container/frontend/index.html
git --no-pager diff -- container/frontend/src/App.jsx container/frontend/index.html
```

## 4. Package container/ and upload ONE source.zip

Excludes `*.pyc`, `__pycache__`, `node_modules/`, `dist/` — the multi-stage
image rebuilds the SPA fresh. The upload triggers the pipeline.

```bash
( zip -r /tmp/source.zip container \
    -x '*.pyc' -x '*__pycache__*' -x '*/node_modules/*' -x '*/dist/*' >/dev/null )
aws s3 cp /tmp/source.zip "s3://${SOURCE_BUCKET}/source.zip"
```

## 5. Watch the pipeline to the Approval gate

Source -> Build -> Deploy-Test (rolling to `coffee-ship-test`) run first, then
the pipeline parks at Approval. Poll until the Approval action is `InProgress`
and copy its token.

```bash
watch -n 15 "aws codepipeline get-pipeline-state --name coffee-ship \
  --query 'stageStates[].{stage:stageName,status:latestExecution.status}' --output table"

# Grab the approval token (present only while the gate waits):
TOKEN=$(aws codepipeline get-pipeline-state --name coffee-ship \
  --query "stageStates[?stageName=='Approval'].actionStates[0].latestExecution.token | [0]" \
  --output text)
echo "Approval token: $TOKEN"
```

## 6. Verify on TEST before approving

Deploy-Test has rolled `coffee-ship-test`, so TEST shows **BeanThere Cafe**
while PROD still shows **Coffee Shop**. That gap is the whole point of the gate.

```bash
echo "TEST:"; curl -s "$TEST_CLOUDFRONT_URL/" | grep -o 'BeanThere Cafe' | head -n1
echo "PROD:"; curl -s "$CLOUDFRONT_URL/"       | grep -o 'Coffee Shop'    | head -n1
```

## 7. Approve the manual gate

```bash
aws codepipeline put-approval-result \
  --pipeline-name coffee-ship \
  --stage-name Approval \
  --action-name Manual_Approval \
  --result summary=approved,status=Approved \
  --token "$TOKEN"
```

## 8. Watch the CodeDeploy blue/green canary on PROD

Deploy-Prod is a `CodeDeployEcsDeployAction`. The CodeDeploy application
`coffee-ship-prod` brings up a green task set behind the test listener (`:8080`),
shifts 10% of traffic for 5 minutes (`CANARY_10PERCENT_5MINUTES`), then the rest.

```bash
DEPLOYMENT_ID=$(aws deploy list-deployments \
  --application-name coffee-ship-prod \
  --query 'deployments[0]' --output text)
echo "Deployment: $DEPLOYMENT_ID"

# Poll the blue/green status + task-set overview:
aws deploy get-deployment --deployment-id "$DEPLOYMENT_ID" \
  --query 'deploymentInfo.{status:status,overview:deploymentOverview}'
```

## 9. PROD now serves "BeanThere Cafe"

```bash
curl -s "$CLOUDFRONT_URL/" | grep -o 'BeanThere Cafe' | head -n1
curl -s "$CLOUDFRONT_URL/health"
```

## 10. Rollback

The prod CodeDeploy deployment group auto-rolls-back on **DEPLOYMENT_FAILURE**
and on **DEPLOYMENT_STOP_ON_ALARM** (the `coffee-ship-prod-unhealthy-hosts`
alarm, `evaluationPeriods 1` on the blue target group). If the green task set is
unhealthy or the alarm fires during the canary, CodeDeploy keeps traffic on blue
— no manual step.

```bash
# Stop (and roll back) an in-progress deployment on purpose:
aws deploy stop-deployment --deployment-id "$DEPLOYMENT_ID" --auto-rollback-enabled

# To roll back a *successful* deploy, re-ship the previous image by uploading
# the prior source.zip again (same Step 4 upload).

# Revert the local edit for the next run:
git checkout -- container/frontend/src/App.jsx container/frontend/index.html
```

---

**What this demonstrates:** two distinct environments from one pipeline —
`coffee-ship-test` deployed by a rolling `EcsDeployAction`, and
`coffee-ship-prod` deployed by a CodeDeploy **blue/green** canary (10%/5min) with
automatic alarm rollback — gated by a manual approval you verify on TEST first.
