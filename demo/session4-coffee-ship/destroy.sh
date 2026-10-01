#!/usr/bin/env bash
#
# destroy.sh — tear down the coffee-shop resources so nothing keeps billing.
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

NETWORK_STACK="CoffeeShopNetworkData"
PIPELINE_STACK="CoffeeShopAppPipeline"
SAM_STACK="coffee-shop-app"
ECR_REPO="coffee-shop"

echo "==> coffee-shop destroy (region: ${AWS_REGION})"

# --- Confirmation prompt guarding all destructive steps ----------------------
cat <<WARN
WARNING: this will PERMANENTLY DELETE the coffee-shop resources in ${AWS_REGION}:
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
echo "==> [1/6] Deleting SAM stack ${SAM_STACK} (if it exists)"
if aws cloudformation describe-stacks --stack-name "${SAM_STACK}" >/dev/null 2>&1; then
  aws cloudformation delete-stack --stack-name "${SAM_STACK}"
  aws cloudformation wait stack-delete-complete --stack-name "${SAM_STACK}" || true
else
  echo "    ${SAM_STACK} not found; skipping."
fi

# --- 2. Empty the pipeline S3 buckets so CDK can delete them ------------------
# The source and artifact buckets are auto-named; resolve them from the stack.
echo "==> [2/6] Emptying pipeline S3 buckets"
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
echo "==> [3/6] Deleting images in ECR repo '${ECR_REPO}'"
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
# deployment group 'coffee-shop-prod' (prod blue/green) — are all declared
# in-stack, so `cdk destroy --all` removes them automatically.
#
# KNOWN ISSUE (blue/green): the prod CodeDeploy blue/green deployment group has
# two target groups (blue + green). During a cascading delete the ALB/listeners
# are torn down, but the green target group can momentarily report "currently in
# use by a listener or a rule" and fail the stack delete. Once the ALBs are gone
# the target group is orphaned and deletable, so we delete any orphaned
# Coffee-*/CoffeeShop* target group (one not attached to a load balancer) and
# retry the destroy.
delete_orphaned_target_groups() {
  # A target group is orphaned when its LoadBalancerArns list is empty. Delete
  # any such group whose name starts with 'Coffee' (the CDK-generated prefix).
  local tg_arns
  tg_arns="$(aws elbv2 describe-target-groups --region "${AWS_REGION}" \
    --query "TargetGroups[?length(LoadBalancerArns)==\`0\` && starts_with(TargetGroupName, 'Coffee')].TargetGroupArn" \
    --output text 2>/dev/null || true)"
  local tg
  for tg in ${tg_arns}; do
    [[ -z "${tg}" || "${tg}" == "None" ]] && continue
    echo "    Deleting orphaned target group: ${tg##*/}"
    aws elbv2 delete-target-group --target-group-arn "${tg}" --region "${AWS_REGION}" 2>/dev/null || true
  done
}

echo "==> [4/6] Destroying CDK stacks (${PIPELINE_STACK}, ${NETWORK_STACK})"
(
  cd "${ROOT}/infra"
  npm install
  # First attempt.
  if npx cdk destroy --all --force; then
    exit 0
  fi
  echo "    cdk destroy failed (often the blue/green green target group lingering)."
  echo "    Clearing orphaned target groups and retrying..."
  delete_orphaned_target_groups
  # A failed stack delete can leave the stack in DELETE_FAILED; delete-stack
  # retries just the resources that failed. Do that directly for both stacks,
  # then confirm.
  for s in "${PIPELINE_STACK}" "${NETWORK_STACK}"; do
    if aws cloudformation describe-stacks --stack-name "${s}" --region "${AWS_REGION}" >/dev/null 2>&1; then
      echo "    Retrying delete of ${s}..."
      aws cloudformation delete-stack --stack-name "${s}" --region "${AWS_REGION}"
      aws cloudformation wait stack-delete-complete --stack-name "${s}" --region "${AWS_REGION}" 2>/dev/null || true
    fi
  done
)

# --- 5. Sweep any leftover auto-named pipeline buckets -----------------------
# CDK's auto-delete can occasionally leave the pipeline source/artifact buckets
# behind if the stack delete failed mid-way. They are prefixed with the stack
# name; empty and remove any that remain.
echo "==> [5/6] Sweeping leftover pipeline S3 buckets"
LEFTOVER="$(aws s3api list-buckets \
  --query "Buckets[?starts_with(Name, 'coffeeshopapppipeline-')].Name" --output text 2>/dev/null || true)"
for b in ${LEFTOVER}; do
  [[ -z "${b}" || "${b}" == "None" ]] && continue
  echo "    Removing leftover bucket s3://${b}"
  aws s3 rm "s3://${b}" --recursive >/dev/null 2>&1 || true
  aws s3api delete-objects --bucket "${b}" --region "${AWS_REGION}" \
    --delete "$(aws s3api list-object-versions --bucket "${b}" --region "${AWS_REGION}" \
      --query '{Objects: Versions[].{Key:Key,VersionId:VersionId}}' --output json 2>/dev/null)" >/dev/null 2>&1 || true
  aws s3api delete-objects --bucket "${b}" --region "${AWS_REGION}" \
    --delete "$(aws s3api list-object-versions --bucket "${b}" --region "${AWS_REGION}" \
      --query '{Objects: DeleteMarkers[].{Key:Key,VersionId:VersionId}}' --output json 2>/dev/null)" >/dev/null 2>&1 || true
  aws s3api delete-bucket --bucket "${b}" --region "${AWS_REGION}" 2>/dev/null || true
done

# --- 6. Done -----------------------------------------------------------------
echo "==> [6/6] Teardown complete"
echo ""
echo "============================================================"
echo " coffee-shop app destroyed in ${AWS_REGION}."
echo " Verify in the AWS console that no CloudFormation stacks,"
echo " ALBs, Fargate tasks, target groups, or S3 buckets remain."
echo "============================================================"
