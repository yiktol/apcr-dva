#!/usr/bin/env bash
#
# destroy.sh — tear down the session5 secure-assistant resources.
#
# Deletes the CDK stacks, empties & removes the SPA + receipts + invocation-log
# buckets, and removes the Bedrock model-invocation-logging configuration (an
# account/region singleton) so the CMK is not pinned. DESTRUCTIVE and
# irreversible — guarded: you must type 'destroy' to proceed.
#
# Region is pinned to ap-southeast-1 to match deploy.sh.
set -euo pipefail

# --- Configuration ----------------------------------------------------------
export AWS_REGION="ap-southeast-1"
export AWS_DEFAULT_REGION="ap-southeast-1"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SECURITY_STACK="SecureAssistantSecurityData"
APP_STACK="SecureAssistantAppEdgeAI"

echo "==> secure-assistant destroy (region: ${AWS_REGION})"

# --- Confirmation prompt guarding all destructive steps ----------------------
cat <<WARN
WARNING: this will PERMANENTLY DELETE the secure-assistant resources in ${AWS_REGION}:
  - CDK stacks: ${APP_STACK}, ${SECURITY_STACK}
  - all objects in the SPA, receipts, and invocation-log S3 buckets
  - the Bedrock model-invocation-logging configuration (account/region singleton)
  - the Bedrock Guardrail + version, the CMK, the DynamoDB tables, the secret
This action cannot be undone.
WARN
read -r -p "Type 'destroy' to confirm: " CONFIRM
if [[ "${CONFIRM}" != "destroy" ]]; then
  echo "Aborted. Nothing was deleted."
  exit 0
fi

for bin in aws node npm; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "ERROR: required tool '$bin' not found on PATH." >&2
    exit 1
  fi
done

# --- 1. Delete the Bedrock invocation-logging configuration ------------------
# This is a per-account/region singleton. Removing it first unpins the CMK so
# the key (and the log destinations) can be deleted cleanly by the stack.
echo "==> [1/5] Deleting Bedrock model-invocation-logging configuration"
aws bedrock delete-model-invocation-logging-configuration --region "${AWS_REGION}" 2>/dev/null \
  && echo "    Removed." \
  || echo "    None present (or already removed); continuing."

# --- 2. Empty the S3 buckets so CDK can delete them --------------------------
echo "==> [2/5] Emptying SPA / receipts / invocation-log S3 buckets"
empty_bucket() {
  local b="$1"
  [[ -z "${b}" || "${b}" == "None" ]] && return 0
  echo "    Emptying s3://${b}"
  aws s3 rm "s3://${b}" --recursive >/dev/null 2>&1 || true
  aws s3api delete-objects --bucket "${b}" --region "${AWS_REGION}" \
    --delete "$(aws s3api list-object-versions --bucket "${b}" --region "${AWS_REGION}" \
      --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' --output json 2>/dev/null)" >/dev/null 2>&1 || true
  aws s3api delete-objects --bucket "${b}" --region "${AWS_REGION}" \
    --delete "$(aws s3api list-object-versions --bucket "${b}" --region "${AWS_REGION}" \
      --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' --output json 2>/dev/null)" >/dev/null 2>&1 || true
}

for STACK in "${APP_STACK}" "${SECURITY_STACK}"; do
  if aws cloudformation describe-stacks --stack-name "${STACK}" --region "${AWS_REGION}" >/dev/null 2>&1; then
    BUCKETS="$(aws cloudformation describe-stack-resources \
      --stack-name "${STACK}" --region "${AWS_REGION}" \
      --query "StackResources[?ResourceType=='AWS::S3::Bucket'].PhysicalResourceId" \
      --output text 2>/dev/null || true)"
    for b in ${BUCKETS}; do empty_bucket "${b}"; done
  fi
done

# --- 3. Destroy the CDK stacks (AppEdgeAI then SecurityData via dep graph) ----
echo "==> [3/5] Destroying CDK stacks (${APP_STACK}, ${SECURITY_STACK})"
(
  cd "${ROOT}/infra"
  npm install
  if npx cdk destroy --all --force; then
    exit 0
  fi
  echo "    cdk destroy failed; retrying stack deletes directly."
  for s in "${APP_STACK}" "${SECURITY_STACK}"; do
    if aws cloudformation describe-stacks --stack-name "${s}" --region "${AWS_REGION}" >/dev/null 2>&1; then
      aws cloudformation delete-stack --stack-name "${s}" --region "${AWS_REGION}"
      aws cloudformation wait stack-delete-complete --stack-name "${s}" --region "${AWS_REGION}" 2>/dev/null || true
    fi
  done
)

# --- 4. Sweep any leftover asset buckets / log groups ------------------------
echo "==> [4/5] Sweeping leftover asset buckets and the invocation log group"
LEFTOVER="$(aws s3api list-buckets \
  --query "Buckets[?starts_with(Name, 'secureassistant')].Name" --output text 2>/dev/null || true)"
for b in ${LEFTOVER}; do
  empty_bucket "${b}"
  aws s3api delete-bucket --bucket "${b}" --region "${AWS_REGION}" 2>/dev/null || true
done
aws logs delete-log-group --log-group-name "/session5/bedrock/model-invocations" \
  --region "${AWS_REGION}" 2>/dev/null || true

# --- 5. Done -----------------------------------------------------------------
echo "==> [5/5] Teardown complete"
echo ""
echo "============================================================"
echo " secure-assistant destroyed in ${AWS_REGION}."
echo " Verify in the console that no CloudFormation stacks, CloudFront"
echo " distributions, Guardrails, interface endpoints, KMS keys, or S3"
echo " buckets remain."
echo "============================================================"
