#!/usr/bin/env bash
#
# demo-pipeline.sh — a guided, step-by-step walkthrough of the Coffee Shop
# release pipeline. Shows a REAL code change ("Coffee Shop" -> "BeanThere Cafe")
# flowing through ONE pipeline run: rolling deploy to TEST, a manual approval
# gate verified against the TEST CloudFront URL, then a CodeDeploy blue/green
# canary to PROD, ending with the PROD page showing the new name.
#
# Nothing here is simulated. Every step runs a real AWS CLI call against the
# deployed CoffeeShopAppPipeline stack. In full-run mode each step pauses with
# `read -p` so you can narrate and let the class watch the console in parallel.
#
# USAGE:
#   ./demo-pipeline.sh            # interactive menu — pick all, one step, or a range
#   ./demo-pipeline.sh all        # run every step in order (the guided walkthrough)
#   ./demo-pipeline.sh 4          # run only step 4
#   ./demo-pipeline.sh 5-9        # run steps 5 through 9
#   ./demo-pipeline.sh 2 6 9      # run steps 2, 6 and 9 (in that order)
#   ./demo-pipeline.sh menu       # force the menu even if args are present
#
# Steps run standalone re-resolve whatever shared state they need (CloudFront
# URLs, the source bucket, the approval token, the deployment id), so you can
# jump straight to e.g. step 8 to re-watch a blue/green deploy.
#
# Prereq: ./deploy.sh has already stood the stack up and the first pipeline run
# has made both ECS services healthy. Region is pinned to ap-southeast-1.
set -euo pipefail

# --- Configuration ----------------------------------------------------------
export AWS_REGION="ap-southeast-1"
export AWS_DEFAULT_REGION="ap-southeast-1"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

PIPELINE_STACK="CoffeeShopAppPipeline"
PIPELINE_NAME="coffee-shop"
CODEDEPLOY_APP="coffee-shop-prod"       # CodeDeploy application name (prod)
SOURCE_KEY="source.zip"

APP_JSX="${ROOT}/container/frontend/src/App.jsx"
INDEX_HTML="${ROOT}/container/frontend/index.html"
OLD_NAME="Coffee Shop"
NEW_NAME="BeanThere Cafe"

# Shared state populated lazily by resolve_outputs / the steps that produce it.
SOURCE_BUCKET=""
CLOUDFRONT_URL=""
TEST_CLOUDFRONT_URL=""
APPROVAL_TOKEN=""
DEPLOYMENT_ID=""

# In full-run ("all") mode steps pause so you can narrate; when running a single
# step or a selected set, pauses are skipped so the step just runs.
INTERACTIVE=1

pause() {
  [[ "${INTERACTIVE}" == "1" ]] || return 0
  read -r -p "

>>> ${1:-Press Enter to continue...} "
}

# --- Shared helpers ----------------------------------------------------------

# Resolve the two CloudFront URLs and the source bucket from the stack. Safe to
# call repeatedly; only queries AWS the first time (so standalone steps can call
# it without re-hitting the API on every invocation within one run).
resolve_outputs() {
  [[ -n "${SOURCE_BUCKET}" && -n "${CLOUDFRONT_URL}" ]] && return 0
  # The stack has TWO buckets (pipeline source + pipeline artifacts). Select the
  # SOURCE bucket specifically (logical id starts with 'SourceBucket') — uploading
  # source.zip to the artifacts bucket would NOT trigger the pipeline.
  SOURCE_BUCKET="$(aws cloudformation describe-stack-resources \
    --stack-name "${PIPELINE_STACK}" \
    --query "StackResources[?ResourceType=='AWS::S3::Bucket' && starts_with(LogicalResourceId, 'SourceBucket')].PhysicalResourceId | [0]" \
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
    echo "       Is the stack deployed? Run ./deploy.sh first." >&2
    exit 1
  fi
}

# Fetch the Approval-stage token if the gate is currently waiting (prints empty
# otherwise). Used by step 7 when run standalone.
fetch_approval_token() {
  aws codepipeline get-pipeline-state --name "${PIPELINE_NAME}" --output json 2>/dev/null | python3 -c '
import sys, json
st = json.load(sys.stdin)
for s in st.get("stageStates", []):
    if s.get("stageName") == "Approval":
        for a in s.get("actionStates", []):
            tok = (a.get("latestExecution") or {}).get("token")
            if tok:
                print(tok)
' 2>/dev/null || true
}

# Resolve the most recent prod CodeDeploy deployment id (used by steps 8/10).
fetch_latest_deployment_id() {
  aws deploy list-deployments --application-name "${CODEDEPLOY_APP}" \
    --query 'deployments[0]' --output text 2>/dev/null || true
}

# --- Steps -------------------------------------------------------------------

step1() {
  echo ""
  echo "### Step 1 — Resolve both environments and the pipeline source bucket"
  echo "    PROD is CloudFrontUrl; TEST is TestCloudFrontUrl. The source bucket is"
  echo "    the pipeline's auto-named versioned S3 bucket (StackResources [0])."
  pause "Resolve the stack outputs"
  resolve_outputs
  echo "    Source bucket     : ${SOURCE_BUCKET}"
  echo "    PROD CloudFront    : ${CLOUDFRONT_URL}   (OutputKey CloudFrontUrl)"
  echo "    TEST CloudFront    : ${TEST_CLOUDFRONT_URL}   (OutputKey TestCloudFrontUrl)"
}

step2() {
  resolve_outputs
  echo ""
  echo "### Step 2 — Baseline: PROD currently serves '${OLD_NAME}'"
  pause "curl the PROD CloudFront URL"
  echo "    GET ${CLOUDFRONT_URL}/ (grep for the app name in the served HTML):"
  curl -s "${CLOUDFRONT_URL}/" | grep -o "${OLD_NAME}" | head -n1 \
    || echo "    (name not found yet — distribution may still be warming up, or PROD already shows '${NEW_NAME}')"
  echo "    /health:"
  curl -s "${CLOUDFRONT_URL}/health" || true
  echo ""
}

step3() {
  echo ""
  echo "### Step 3 — The student edit: rename '${OLD_NAME}' -> '${NEW_NAME}'"
  echo "    We change the APP_NAME constant in App.jsx and the <title> in"
  echo "    index.html. This is a real source edit the pipeline will ship."
  pause "Apply the sed edits and show the diff"

  # macOS/BSD and GNU sed differ on -i; detect and branch so this is portable.
  if sed --version >/dev/null 2>&1; then
    SED_INPLACE=(sed -i)          # GNU sed
  else
    SED_INPLACE=(sed -i '')       # BSD/macOS sed
  fi
  "${SED_INPLACE[@]}" "s/${OLD_NAME}/${NEW_NAME}/g" "${APP_JSX}"
  "${SED_INPLACE[@]}" "s/${OLD_NAME}/${NEW_NAME}/g" "${INDEX_HTML}"

  echo "    Diff of the edited files:"
  git -C "${ROOT}" --no-pager diff -- "${APP_JSX}" "${INDEX_HTML}" || true
}

step4() {
  resolve_outputs
  echo ""
  echo "### Step 4 — Package container/ and upload source.zip (ONE pipeline run)"
  echo "    Excludes *.pyc, __pycache__, node_modules/, dist/ — the multi-stage"
  echo "    image rebuilds the SPA fresh. The upload triggers the pipeline."
  pause "Zip and upload to s3://${SOURCE_BUCKET}/${SOURCE_KEY}"

  local tmp_zip
  tmp_zip="$(mktemp -t coffee-shop-source.XXXXXX).zip"
  (
    cd "${ROOT}"
    zip -r "${tmp_zip}" container -x '*.pyc' -x '*__pycache__*' -x '*/node_modules/*' -x '*/dist/*' >/dev/null
  )
  aws s3 cp "${tmp_zip}" "s3://${SOURCE_BUCKET}/${SOURCE_KEY}"
  rm -f "${tmp_zip}"
  echo "    Uploaded. Pipeline '${PIPELINE_NAME}' will start (Source -> Build ->"
  echo "    Deploy-Test -> Approval -> Deploy-Prod)."
}

step5() {
  echo ""
  echo "### Step 5 — Watch the pipeline until it reaches the Approval gate"
  echo "    Source -> Build -> Deploy-Test (rolling to coffee-shop-test) run first."
  pause "Poll get-pipeline-state until Approval is InProgress"

  while true; do
    local state_json
    state_json="$(aws codepipeline get-pipeline-state --name "${PIPELINE_NAME}" --output json)"
    echo "    $(date '+%H:%M:%S') stage status:"
    echo "${state_json}" | python3 -c '
import sys, json
st = json.load(sys.stdin)
for s in st.get("stageStates", []):
    le = s.get("latestExecution", {}) or {}
    print("      %-14s %s" % (s.get("stageName",""), le.get("status","")))
'
    APPROVAL_TOKEN="$(echo "${state_json}" | python3 -c '
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
}

step6() {
  resolve_outputs
  echo ""
  echo "### Step 6 — Verify on TEST before approving"
  echo "    Deploy-Test has already rolled coffee-shop-test. TEST should now show"
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
}

step7() {
  echo ""
  echo "### Step 7 — Approve the manual gate to promote to PROD"
  # If we don't already hold a token (e.g. this step is run standalone), fetch it.
  if [[ -z "${APPROVAL_TOKEN}" ]]; then
    echo "    No token in memory — fetching the current Approval token..."
    APPROVAL_TOKEN="$(fetch_approval_token)"
  fi
  if [[ -z "${APPROVAL_TOKEN}" ]]; then
    echo "    The Approval stage is not waiting right now (no token). Run step 4 to"
    echo "    trigger a run, then step 5 to wait for the gate, before approving." >&2
    return 1
  fi
  echo "    Using the Approval token."
  pause "put-approval-result (Approved)"

  aws codepipeline put-approval-result \
    --pipeline-name "${PIPELINE_NAME}" \
    --stage-name Approval \
    --action-name Manual_Approval \
    --result summary=approved,status=Approved \
    --token "${APPROVAL_TOKEN}"
  echo "    Approved. Deploy-Prod (CodeDeployEcsDeployAction) now starts the"
  echo "    blue/green deployment on the coffee-shop-prod service."
}

step8() {
  echo ""
  echo "### Step 8 — Watch the CodeDeploy blue/green canary on PROD"
  echo "    CodeDeploy app '${CODEDEPLOY_APP}' shifts 10% of traffic for 5 minutes"
  echo "    (CANARY_10PERCENT_5MINUTES), then the rest. A new (green) task set"
  echo "    comes up behind the test listener (:8080) before traffic shifts to it."
  pause "list-deployments + get-deployment for the latest deployment"

  DEPLOYMENT_ID=""
  for _ in $(seq 1 20); do
    DEPLOYMENT_ID="$(fetch_latest_deployment_id)"
    if [[ -n "${DEPLOYMENT_ID}" && "${DEPLOYMENT_ID}" != "None" ]]; then
      break
    fi
    echo "    waiting for CodeDeploy to register the deployment..."
    sleep 10
  done
  echo "    Latest deployment: ${DEPLOYMENT_ID}"

  if [[ -z "${DEPLOYMENT_ID}" || "${DEPLOYMENT_ID}" == "None" ]]; then
    echo "    No CodeDeploy deployment found. Approve the gate (step 7) first." >&2
    return 1
  fi

  while true; do
    local dep_json status
    dep_json="$(aws deploy get-deployment --deployment-id "${DEPLOYMENT_ID}" --output json)"
    status="$(echo "${dep_json}" | python3 -c 'import sys,json;print(json.load(sys.stdin)["deploymentInfo"].get("status",""))')"
    echo "    $(date '+%H:%M:%S') CodeDeploy status: ${status}"
    echo "${dep_json}" | python3 -c '
import sys, json
di = json.load(sys.stdin)["deploymentInfo"]
ov = di.get("deploymentOverview") or {}
if ov:
    print("      task sets:", ", ".join("%s=%s" % (k, v) for k, v in ov.items()))
'
    case "${status}" in
      Succeeded) echo "    Blue/green deployment Succeeded."; break ;;
      Failed|Stopped) echo "    Deployment ${status} — CodeDeploy auto-rollback should restore blue."; break ;;
      *) sleep 20 ;;
    esac
  done
}

step9() {
  resolve_outputs
  echo ""
  echo "### Step 9 — PROD now serves '${NEW_NAME}'"
  pause "curl the PROD CloudFront URL again"

  echo "    PROD (${CLOUDFRONT_URL}):"
  curl -s "${CLOUDFRONT_URL}/" | grep -o "${NEW_NAME}" | head -n1 \
    || echo "    (give the blue/green cutover a moment, then re-curl)"
  echo "    /health:"
  curl -s "${CLOUDFRONT_URL}/health" || true
  echo ""
}

step10() {
  echo ""
  echo "### Step 10 — Rollback (how PROD protects itself)"
  [[ -n "${DEPLOYMENT_ID}" ]] || DEPLOYMENT_ID="$(fetch_latest_deployment_id)"
  cat <<ROLLBACK
    The prod CodeDeploy deployment group has automatic rollback enabled on:
      - DEPLOYMENT_FAILURE  (a failed deployment), and
      - DEPLOYMENT_STOP_ON_ALARM (the 'coffee-shop-prod-unhealthy-hosts' alarm,
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
}

# Ordered list of steps and one-line descriptions for the menu.
STEP_IDS=(1 2 3 4 5 6 7 8 9 10)
step_desc() {
  case "$1" in
    1)  echo "Resolve CloudFront URLs + source bucket" ;;
    2)  echo "Baseline: PROD serves '${OLD_NAME}'" ;;
    3)  echo "Student edit: rename -> '${NEW_NAME}'" ;;
    4)  echo "Package container/ and upload source.zip (triggers the run)" ;;
    5)  echo "Watch the pipeline to the Approval gate" ;;
    6)  echo "Verify on TEST before approving (TEST new vs PROD old)" ;;
    7)  echo "Approve the manual gate" ;;
    8)  echo "Watch the CodeDeploy blue/green canary on PROD" ;;
    9)  echo "Confirm PROD now serves '${NEW_NAME}'" ;;
    10) echo "Rollback notes" ;;
  esac
}

run_step() {
  case "$1" in
    1) step1 ;; 2) step2 ;; 3) step3 ;; 4) step4 ;; 5) step5 ;;
    6) step6 ;; 7) step7 ;; 8) step8 ;; 9) step9 ;; 10) step10 ;;
    *) echo "Unknown step: $1" >&2; return 1 ;;
  esac
}

# Expand a selection token into step numbers:
#   "all" -> 1..10 ; "4" -> 4 ; "5-9" -> 5 6 7 8 9
expand_selection() {
  local tok="$1"
  if [[ "${tok}" == "all" ]]; then
    printf '%s\n' "${STEP_IDS[@]}"
    return 0
  fi
  if [[ "${tok}" =~ ^([0-9]+)-([0-9]+)$ ]]; then
    local lo="${BASH_REMATCH[1]}" hi="${BASH_REMATCH[2]}"
    seq "${lo}" "${hi}"
    return 0
  fi
  if [[ "${tok}" =~ ^[0-9]+$ ]]; then
    echo "${tok}"
    return 0
  fi
  echo "ERROR: unrecognized selection '${tok}' (use: all | N | N-M)" >&2
  return 1
}

# Run a whitespace-separated set of step numbers in ascending order, de-duped.
run_selection() {
  local raw=("$@") expanded=() s
  for s in "${raw[@]}"; do
    while IFS= read -r n; do expanded+=("$n"); done < <(expand_selection "$s")
  done
  # sort numerically + unique, then run
  local ordered
  ordered="$(printf '%s\n' "${expanded[@]}" | sort -n -u)"
  while IFS= read -r n; do
    [[ -n "$n" ]] && run_step "$n"
  done <<< "${ordered}"
}

print_menu() {
  echo "============================================================"
  echo " Coffee Shop — guided pipeline walkthrough (region: ${AWS_REGION})"
  echo " Select what to run:"
  echo "------------------------------------------------------------"
  local id
  for id in "${STEP_IDS[@]}"; do
    printf "  %2s) %s\n" "${id}" "$(step_desc "${id}")"
  done
  echo "------------------------------------------------------------"
  echo "   a) ALL steps in order (the full guided walkthrough)"
  echo "   q) quit"
  echo "------------------------------------------------------------"
  echo " Enter a choice: a | q | a step number (e.g. 4) | a range (5-9)"
  echo " | or several (e.g. '2 6 9')."
  echo "============================================================"
}

interactive_menu() {
  while true; do
    print_menu
    local choice
    read -r -p "> " choice || { echo; exit 0; }
    choice="$(echo "${choice}" | tr '[:upper:]' '[:lower:]' | xargs || true)"
    case "${choice}" in
      ""|q|quit|exit) echo "Bye."; exit 0 ;;
      a|all)
        INTERACTIVE=1
        run_selection all
        echo ""
        echo "Walkthrough complete. (Back to menu — pick 'q' to quit.)"
        ;;
      *)
        # One or more step tokens; validate before running.
        local toks ok=1 t
        read -r -a toks <<< "${choice}"
        for t in "${toks[@]}"; do
          expand_selection "$t" >/dev/null 2>&1 || { echo "Invalid: '$t'"; ok=0; }
        done
        if [[ "${ok}" == "1" ]]; then
          # Single-step/selection runs skip the narration pauses by default.
          if [[ "${#toks[@]}" == "1" && ! "${toks[0]}" =~ - ]]; then
            INTERACTIVE=0
          else
            INTERACTIVE=1
          fi
          run_selection "${toks[@]}"
          INTERACTIVE=1
          echo ""
          echo "Done. (Back to menu — pick 'q' to quit.)"
        fi
        ;;
    esac
  done
}

# --- Entry point -------------------------------------------------------------

# Preflight: required tools.
for bin in aws zip python3 sed curl; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "ERROR: required tool '$bin' not found on PATH." >&2
    exit 1
  fi
done

if [[ "$#" -eq 0 || "${1:-}" == "menu" ]]; then
  interactive_menu
elif [[ "${1:-}" == "all" ]]; then
  INTERACTIVE=1
  echo "============================================================"
  echo " Coffee Shop — full guided pipeline walkthrough"
  echo "============================================================"
  run_selection all
  echo ""
  echo "============================================================"
  echo " Walkthrough complete. TEST got the change first (rolling), you verified"
  echo " it, approved, and PROD took it via a CodeDeploy blue/green canary."
  echo " Remember: './destroy.sh' when the session is over."
  echo "============================================================"
else
  # Non-interactive: run exactly the steps given as args (no pauses).
  INTERACTIVE=0
  run_selection "$@"
fi
