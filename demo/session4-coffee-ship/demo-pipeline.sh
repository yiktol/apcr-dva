#!/usr/bin/env bash
#
# demo-pipeline.sh — a guided, step-by-step live demo of the Coffee Shop
# release pipeline. Shows a REAL code change ("Coffee Shop" -> "BeanThere Cafe")
# flowing through ONE pipeline run: rolling deploy to TEST, a manual approval
# gate verified against the TEST CloudFront URL, then a CodeDeploy blue/green
# canary to PROD, ending with the PROD page showing the new name.
#
# Nothing here is simulated. Every step runs a real AWS CLI call against the
# deployed CoffeeShipAppPipeline stack. Each step pauses with `read -p` so you
# can narrate and let the class watch the console in parallel.
#
# Prereq: ./deploy.sh has already stood the stack up and the first pipeline run
# has made both ECS services healthy. Region is pinned to ap-southeast-1.
set -euo pipefail

# --- Configuration ----------------------------------------------------------
export AWS_REGION="ap-southeast-1"
export AWS_DEFAULT_REGION="ap-southeast-1"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PIPELINE_STACK="CoffeeShipAppPipeline"
PIPELINE_NAME="coffee-ship"
CODEDEPLOY_APP="coffee-ship-prod"       # CodeDeploy application name (prod)
SOURCE_KEY="source.zip"

APP_JSX="${ROOT}/container/frontend/src/App.jsx"
INDEX_HTML="${ROOT}/container/frontend/index.html"
OLD_NAME="Coffee Shop"
NEW_NAME="BeanThere Cafe"

pause() { read -r -p "

>>> ${1:-Press Enter to continue...} "; }

echo "============================================================"
echo " Coffee Shop — guided pipeline demo (region: ${AWS_REGION})"
echo " One run: edit the app name, roll TEST, approve, blue/green PROD."
echo "============================================================"

for bin in aws zip python3 sed curl; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "ERROR: required tool '$bin' not found on PATH." >&2
    exit 1
  fi
done

# --- Step 1: resolve the two CloudFront URLs + the source bucket -------------
echo ""
echo "### Step 1 — Resolve both environments and the pipeline source bucket"
echo "    PROD is CloudFrontUrl; TEST is TestCloudFrontUrl. The source bucket is"
echo "    the pipeline's auto-named versioned S3 bucket (StackResources [0])."
pause "Resolve the stack outputs"

SOURCE_BUCKET="$(aws cloudformation describe-stack-resources \
  --stack-name "${PIPELINE_STACK}" \
  --query "StackResources[?ResourceType=='AWS::S3::Bucket'].PhysicalResourceId | [0]" \
  --output text)"
CLOUDFRONT_URL="$(aws cloudformation describe-stacks \
  --stack-name "${PIPELINE_STACK}" \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontUrl'].OutputValue | [0]" \
  --output text)"
TEST_CLOUDFRONT_URL="$(aws cloudformation describe-stacks \
  --stack-name "${PIPELINE_STACK}" \
  --query "Stacks[0].Outputs[?OutputKey=='TestCloudFrontUrl'].OutputValue | [0]" \
  --output text)"

if [[ -z "${SOURCE_BUCKET}" || "${SOURCE_BUCKET}" == "None" ]]; then
  echo "ERROR: could not resolve the pipeline source bucket from ${PIPELINE_STACK}." >&2
  exit 1
fi

echo "    Source bucket     : ${SOURCE_BUCKET}"
echo "    PROD CloudFront    : ${CLOUDFRONT_URL}   (OutputKey CloudFrontUrl)"
echo "    TEST CloudFront    : ${TEST_CLOUDFRONT_URL}   (OutputKey TestCloudFrontUrl)"

# --- Step 2: show the current PROD page (still "Coffee Shop") ----------------
echo ""
echo "### Step 2 — Baseline: PROD currently serves 'Coffee Shop'"
pause "curl the PROD CloudFront URL"
echo "    GET ${CLOUDFRONT_URL}/ (grep for the app name in the served HTML):"
curl -s "${CLOUDFRONT_URL}/" | grep -o 'Coffee Shop' | head -n1 || echo "    (name not found yet — distribution may still be warming up)"
echo "    /health:"
curl -s "${CLOUDFRONT_URL}/health" || true
echo ""

# --- Step 3: make the real code change (Coffee Shop -> BeanThere Cafe) -------
echo ""
echo "### Step 3 — The student edit: rename 'Coffee Shop' -> 'BeanThere Cafe'"
echo "    We change the APP_NAME constant in App.jsx and the <title> in"
echo "    index.html. This is a real source edit the pipeline will ship."
pause "Apply the sed edits and show the diff"

# macOS/BSD and GNU sed differ on -i; detect and branch so the demo is portable.
if sed --version >/dev/null 2>&1; then
  SED_INPLACE=(sed -i)          # GNU sed
else
  SED_INPLACE=(sed -i '')       # BSD/macOS sed
fi
"${SED_INPLACE[@]}" "s/${OLD_NAME}/${NEW_NAME}/g" "${APP_JSX}"
"${SED_INPLACE[@]}" "s/${OLD_NAME}/${NEW_NAME}/g" "${INDEX_HTML}"

echo "    Diff of the edited files:"
git -C "${ROOT}" --no-pager diff -- "${APP_JSX}" "${INDEX_HTML}" || true

# --- Step 4: package container/ and upload ONE source.zip --------------------
echo ""
echo "### Step 4 — Package container/ and upload source.zip (ONE pipeline run)"
echo "    Excludes *.pyc, __pycache__, node_modules/, dist/ — the multi-stage"
echo "    image rebuilds the SPA fresh. The upload triggers the pipeline."
pause "Zip and upload to s3://${SOURCE_BUCKET}/${SOURCE_KEY}"

TMP_ZIP="$(mktemp -t coffee-ship-source.XXXXXX).zip"
trap 'rm -f "${TMP_ZIP}"' EXIT
(
  cd "${ROOT}"
  zip -r "${TMP_ZIP}" container -x '*.pyc' -x '*__pycache__*' -x '*/node_modules/*' -x '*/dist/*' >/dev/null
)
aws s3 cp "${TMP_ZIP}" "s3://${SOURCE_BUCKET}/${SOURCE_KEY}"
echo "    Uploaded. Pipeline '${PIPELINE_NAME}' will start (Source -> Build ->"
echo "    Deploy-Test -> Approval -> Deploy-Prod)."

# --- Step 5: poll the pipeline until it reaches the Approval stage -----------
echo ""
echo "### Step 5 — Watch the pipeline until it reaches the Approval gate"
echo "    Source -> Build -> Deploy-Test (rolling to coffee-ship-test) run first."
pause "Poll get-pipeline-state until Approval is InProgress"

APPROVAL_TOKEN=""
while true; do
  STATE_JSON="$(aws codepipeline get-pipeline-state --name "${PIPELINE_NAME}" --output json)"
  echo "    $(date '+%H:%M:%S') stage status:"
  echo "${STATE_JSON}" | python3 -c '
import sys, json
st = json.load(sys.stdin)
for s in st.get("stageStates", []):
    le = s.get("latestExecution", {}) or {}
    print("      %-14s %s" % (s.get("stageName",""), le.get("status","")))
'
  # Extract the Approval action token (present only while the gate waits).
  APPROVAL_TOKEN="$(echo "${STATE_JSON}" | python3 -c '
import sys, json
st = json.load(sys.stdin)
for s in st.get("stageStates", []):
    if s.get("stageName") == "Approval":
        for a in s.get("actionStates", []):
            tok = (a.get("latestExecution") or {}).get("token")
            if tok:
                print(tok)
' 2>/dev/null || true)"
  if [[ -n "${APPROVAL_TOKEN}" ]]; then
    echo "    Pipeline is now waiting at Approval (token acquired)."
    break
  fi
  sleep 15
done

# --- Step 6: verify TEST shows the NEW name while PROD still shows the OLD ---
echo ""
echo "### Step 6 — Verify on TEST before approving"
echo "    Deploy-Test has already rolled coffee-ship-test. TEST should now show"
echo "    '${NEW_NAME}' while PROD still shows '${OLD_NAME}' (prod deploy not run)."
pause "curl TEST and PROD and compare"

echo "    TEST (${TEST_CLOUDFRONT_URL}):"
curl -s "${TEST_CLOUDFRONT_URL}/" | grep -o "${NEW_NAME}" | head -n1 \
  || echo "    (did not see '${NEW_NAME}' on TEST yet — give the rolling deploy a moment)"
echo "    PROD (${CLOUDFRONT_URL}):"
curl -s "${CLOUDFRONT_URL}/" | grep -o "${OLD_NAME}" | head -n1 \
  || echo "    (PROD no longer shows '${OLD_NAME}')"
echo ""
echo "    Headline: TEST = '${NEW_NAME}', PROD = '${OLD_NAME}'. That gap is the"
echo "    whole point of the Approval gate — you promote only after verifying TEST."

# --- Step 7: approve the manual gate -----------------------------------------
echo ""
echo "### Step 7 — Approve the manual gate to promote to PROD"
echo "    Uses the token captured in Step 5."
pause "put-approval-result (Approved)"

aws codepipeline put-approval-result \
  --pipeline-name "${PIPELINE_NAME}" \
  --stage-name Approval \
  --action-name Manual_Approval \
  --result summary=approved,status=Approved \
  --token "${APPROVAL_TOKEN}"
echo "    Approved. Deploy-Prod (CodeDeployEcsDeployAction) now starts the"
echo "    blue/green deployment on the coffee-ship-prod service."

# --- Step 8: watch the CodeDeploy blue/green deployment ----------------------
echo ""
echo "### Step 8 — Watch the CodeDeploy blue/green canary on PROD"
echo "    CodeDeploy app '${CODEDEPLOY_APP}' shifts 10% of traffic for 5 minutes"
echo "    (CANARY_10PERCENT_5MINUTES), then the rest. A new (green) task set"
echo "    comes up behind the test listener (:8080) before traffic shifts to it."
pause "list-deployments + get-deployment for the latest deployment"

# Grab the most recent deployment id for the prod CodeDeploy application.
DEPLOYMENT_ID=""
for _ in $(seq 1 20); do
  DEPLOYMENT_ID="$(aws deploy list-deployments \
    --application-name "${CODEDEPLOY_APP}" \
    --query 'deployments[0]' --output text 2>/dev/null || true)"
  if [[ -n "${DEPLOYMENT_ID}" && "${DEPLOYMENT_ID}" != "None" ]]; then
    break
  fi
  echo "    waiting for CodeDeploy to register the deployment..."
  sleep 10
done
echo "    Latest deployment: ${DEPLOYMENT_ID}"

if [[ -n "${DEPLOYMENT_ID}" && "${DEPLOYMENT_ID}" != "None" ]]; then
  while true; do
    DEP_JSON="$(aws deploy get-deployment --deployment-id "${DEPLOYMENT_ID}" --output json)"
    STATUS="$(echo "${DEP_JSON}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["deploymentInfo"].get("status",""))')"
    echo "    $(date '+%H:%M:%S') CodeDeploy status: ${STATUS}"
    echo "${DEP_JSON}" | python3 -c '
import sys, json
di = json.load(sys.stdin)["deploymentInfo"]
ov = di.get("deploymentOverview") or {}
if ov:
    print("      task sets:", ", ".join("%s=%s" % (k, v) for k, v in ov.items()))
'
    case "${STATUS}" in
      Succeeded) echo "    Blue/green deployment Succeeded."; break ;;
      Failed|Stopped) echo "    Deployment ${STATUS} — CodeDeploy auto-rollback should restore blue."; break ;;
      *) sleep 20 ;;
    esac
  done
fi

# --- Step 9: confirm PROD now serves "BeanThere Cafe" ------------------------
echo ""
echo "### Step 9 — PROD now serves '${NEW_NAME}'"
pause "curl the PROD CloudFront URL again"

echo "    PROD (${CLOUDFRONT_URL}):"
curl -s "${CLOUDFRONT_URL}/" | grep -o "${NEW_NAME}" | head -n1 \
  || echo "    (give the blue/green cutover a moment, then re-curl)"
echo "    /health:"
curl -s "${CLOUDFRONT_URL}/health" || true
echo ""

# --- Step 10: rollback notes -------------------------------------------------
echo ""
echo "### Step 10 — Rollback (how PROD protects itself)"
cat <<ROLLBACK
    The prod CodeDeploy deployment group has automatic rollback enabled on:
      - DEPLOYMENT_FAILURE  (a failed deployment), and
      - DEPLOYMENT_STOP_ON_ALARM (the 'coffee-ship-prod-unhealthy-hosts' alarm,
        evaluationPeriods 1 on the blue target group).
    If the green task set is unhealthy or the alarm fires during the canary,
    CodeDeploy keeps traffic on blue (or shifts it back) — no manual step.

    To roll back a *successful* deploy on purpose, redeploy the previous image
    (push the prior source.zip again) or stop the deployment while in progress:
      aws deploy stop-deployment --deployment-id ${DEPLOYMENT_ID:-<id>} \\
        --auto-rollback-enabled

    Revert the local edit for the next run:
      git -C "${ROOT}" checkout -- "${APP_JSX}" "${INDEX_HTML}"
ROLLBACK

echo ""
echo "============================================================"
echo " Demo complete. TEST got the change first (rolling), you verified it,"
echo " approved, and PROD took it via a CodeDeploy blue/green canary."
echo " Remember: './destroy.sh' when the session is over."
echo "============================================================"
