#!/usr/bin/env bash
#
# destroy.sh — tear down the coffee-ship demo so nothing keeps billing.
#
# Deletes the CDK stacks, empties & removes the pipeline source/artifact
# buckets, and clears the ECR images. This is DESTRUCTIVE and irreversible,
# so it prompts for confirmation before touching anything.
#
# Region is pinned to ap-southeast-1 to match deploy.sh.
set -euo pipefail

# --- Configuration ----------------------------------------------------------
export AWS_REGION="ap-southeast-1"
export AWS_DEFAULT_REGION="ap-southeast-1"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

NETWORK_STACK="CoffeeShipNetworkData"
PIPELINE_STACK="CoffeeShipAppPipeline"
SAM_STACK="coffee-ship-app"
ECR_REPO="coffee-ship"

echo "==> coffee-ship destroy (region: ${AWS_REGION})"

# --- Confirmation prompt guarding all destructive steps ----------------------
cat <<WARN
WARNING: this will PERMANENTLY DELETE the coffee-ship demo in ${AWS_REGION}:
  - CDK stacks: ${PIPELINE_STACK}, ${NETWORK_STACK}
  - SAM stack (if present): ${SAM_STACK}
  - all objects in the pipeline source & artifact S3 buckets
  - all images in the '${ECR_REPO}' ECR repository
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

# --- 1. Delete the SAM app stack (if the pipeline ever deployed it) ----------
echo "==> [1/5] Deleting SAM stack ${SAM_STACK} (if it exists)"
if aws cloudformation describe-stacks --stack-name "${SAM_STACK}" >/dev/null 2>&1; then
  aws cloudformation delete-stack --stack-name "${SAM_STACK}"
  aws cloudformation wait stack-delete-complete --stack-name "${SAM_STACK}" || true
else
  echo "    ${SAM_STACK} not found; skipping."
fi

# --- 2. Empty the pipeline S3 buckets so CDK can delete them ------------------
# The source and artifact buckets are auto-named; resolve them from the stack.
echo "==> [2/5] Emptying pipeline S3 buckets"
if aws cloudformation describe-stacks --stack-name "${PIPELINE_STACK}" >/dev/null 2>&1; then
  BUCKETS="$(aws cloudformation describe-stack-resources \
    --stack-name "${PIPELINE_STACK}" \
    --query "StackResources[?ResourceType=='AWS::S3::Bucket'].PhysicalResourceId" \
    --output text)"
  for b in ${BUCKETS}; do
    [[ -z "${b}" || "${b}" == "None" ]] && continue
    echo "    Emptying s3://${b}"
    # Remove current objects plus all versions/delete-markers (versioned bucket).
    aws s3 rm "s3://${b}" --recursive || true
    aws s3api delete-objects --bucket "${b}" \
      --delete "$(aws s3api list-object-versions --bucket "${b}" \
        --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' \
        --output json 2>/dev/null)" >/dev/null 2>&1 || true
    aws s3api delete-objects --bucket "${b}" \
      --delete "$(aws s3api list-object-versions --bucket "${b}" \
        --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' \
        --output json 2>/dev/null)" >/dev/null 2>&1 || true
  done
else
  echo "    ${PIPELINE_STACK} not found; skipping bucket cleanup."
fi

# --- 3. Delete all ECR images ------------------------------------------------
echo "==> [3/5] Deleting images in ECR repo '${ECR_REPO}'"
if aws ecr describe-repositories --repository-names "${ECR_REPO}" >/dev/null 2>&1; then
  IMAGE_IDS="$(aws ecr list-images --repository-name "${ECR_REPO}" \
    --query 'imageIds[*]' --output json)"
  if [[ "${IMAGE_IDS}" != "[]" && -n "${IMAGE_IDS}" ]]; then
    aws ecr batch-delete-image --repository-name "${ECR_REPO}" \
      --image-ids "${IMAGE_IDS}" >/dev/null || true
    echo "    Deleted images from '${ECR_REPO}'."
  else
    echo "    No images to delete."
  fi
else
  echo "    ECR repo '${ECR_REPO}' not found; skipping."
fi

# --- 4. Destroy the CDK stacks -----------------------------------------------
# NOTE: the two-environment resources — the SECOND CloudFront distribution
# (TestCloudFrontUrl, test ALB origin) and the CodeDeploy application +
# deployment group 'coffee-ship-prod' (prod blue/green) — are all declared
# in-stack, so `cdk destroy --all` removes them automatically. No extra manual
# deletion is needed for them beyond emptying the buckets/ECR done above.
echo "==> [4/5] Destroying CDK stacks (${PIPELINE_STACK}, ${NETWORK_STACK})"
(
  cd "${ROOT}/infra"
  npm install
  npx cdk destroy --all --force
)

# --- 5. Done -----------------------------------------------------------------
echo "==> [5/5] Teardown complete"
echo ""
echo "============================================================"
echo " coffee-ship demo destroyed in ${AWS_REGION}."
echo " Verify in the AWS console that no CloudFormation stacks,"
echo " ALBs, Fargate tasks, or NAT/EIP resources remain."
echo "============================================================"
