#!/usr/bin/env bash
#
# deploy.sh — stand up the session5 secure coffee-shop AI assistant.
#
# This creates REAL, BILLABLE AWS resources (CloudFront + API Gateway + WAF +
# Lambda + Bedrock Guardrail + VPC interface endpoints + DynamoDB + KMS + S3 +
# Secrets Manager + SSM). Run it in a throwaway sandbox account and tear it down
# with ./destroy.sh when you are done.
#
# Region is pinned to ap-southeast-1 everywhere (regional WAF => single region).
#
# ONE-TIME PREREQUISITES (not automated here):
#   * Amazon Bedrock model access for Nova Micro (apac.amazon.nova-micro-v1:0)
#     must be enabled in ap-southeast-1 for this account.
#   * The VPC vpc-01857e627d800ca7a and its six subnets must already exist.
#   * `cdk bootstrap` runs below (idempotent) but needs account admin the first
#     time.
set -euo pipefail

# --- Configuration ----------------------------------------------------------
export AWS_REGION="ap-southeast-1"
export AWS_DEFAULT_REGION="ap-southeast-1"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

SECURITY_STACK="SecureAssistantSecurityData"
APP_STACK="SecureAssistantAppEdgeAI"

echo "==> secure-assistant deploy (region: ${AWS_REGION})"

# --- Preflight ---------------------------------------------------------------
echo "==> [0/6] Checking prerequisites"
for bin in aws docker node npm python3 zip rsvg-convert; do
  if ! command -v "$bin" >/dev/null 2>&1; then
    echo "ERROR: required tool '$bin' not found on PATH." >&2
    exit 1
  fi
done

ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
echo "    Using AWS account ${ACCOUNT_ID} in ${AWS_REGION}"

# --- 1. CDK bootstrap --------------------------------------------------------
echo "==> [1/6] Bootstrapping CDK environment (idempotent)"
(
  cd "${ROOT}/infra"
  npm install
  npx cdk bootstrap "aws://${ACCOUNT_ID}/${AWS_REGION}"
)

# --- 2. Regenerate the architecture diagram ---------------------------------
echo "==> [2/6] Regenerating the architecture diagram"
(
  cd "${ROOT}/diagram"
  python3 build_diagram.py
  rsvg-convert -o architecture.png architecture.svg
)

# --- 3. Deploy the SecurityData stack FIRST ---------------------------------
# ORDERING MATTERS: the Guardrail + its published version, the CMK, the tables,
# the secret, the SSM config, and the Bedrock invocation-logging config all live
# here and are referenced by the AppEdgeAI stack (which passes the guardrail
# id/version into the assistant Lambda env). The container image build happens
# at this step via cdk-assets (NOT at synth).
echo "==> [3/6] Deploying ${SECURITY_STACK} (CMK, tables, guardrail, logging)"
(
  cd "${ROOT}/infra"
  CDK_DEFAULT_ACCOUNT="${ACCOUNT_ID}" CDK_DEFAULT_REGION="${AWS_REGION}" \
    npx cdk deploy "${SECURITY_STACK}" --require-approval never
)

# --- 3b. Build + push the assistant image to a dedicated ECR repo -----------
# The assistant Lambda is a container image. We build + push it OURSELVES (not
# via a CDK image asset) because the local buildx/colima toolchain emits an OCI
# image index with provenance attestations that AWS Lambda rejects. buildx with
# --provenance=false --sbom=false produces a single Docker-schema2 manifest that
# Lambda accepts. The AppEdgeAI stack imports this repo by name and references
# the :latest tag.
echo "==> [3b/6] Building + pushing the assistant image (Lambda-compatible)"
ASSISTANT_REPO="session5-secure-assistant"
ASSISTANT_ECR_URI="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ASSISTANT_REPO}"
aws ecr describe-repositories --repository-names "${ASSISTANT_REPO}" --region "${AWS_REGION}" >/dev/null 2>&1 \
  || aws ecr create-repository --repository-name "${ASSISTANT_REPO}" --region "${AWS_REGION}" >/dev/null
aws ecr get-login-password --region "${AWS_REGION}" \
  | docker login --username AWS --password-stdin "${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
# BUILDX_NO_DEFAULT_ATTESTATIONS + --provenance=false --sbom=false => no OCI
# index / attestation manifests; --platform linux/amd64 matches Lambda x86_64.
BUILDX_NO_DEFAULT_ATTESTATIONS=1 docker buildx build \
  --platform linux/amd64 --provenance=false --sbom=false \
  -t "${ASSISTANT_ECR_URI}:latest" --push "${ROOT}/app"
echo "    Pushed ${ASSISTANT_ECR_URI}:latest"

# --- 4. Deploy the AppEdgeAI stack ------------------------------------------
# Stands up CloudFront, WAF, API Gateway, the Lambdas (the assistant references
# the ECR image pushed above), and the Bedrock interface endpoints.
echo "==> [4/6] Deploying ${APP_STACK} (edge + compute + observability)"
(
  cd "${ROOT}/infra"
  CDK_DEFAULT_ACCOUNT="${ACCOUNT_ID}" CDK_DEFAULT_REGION="${AWS_REGION}" \
    npx cdk deploy "${APP_STACK}" --require-approval never
)

# --- 5. Seed demo data ------------------------------------------------------
echo "==> [5/6] Seeding demo data (orders + a sample receipt)"
ORDERS_TABLE="$(aws cloudformation describe-stack-resources \
  --stack-name "${SECURITY_STACK}" \
  --query "StackResources[?ResourceType=='AWS::DynamoDB::Table' && contains(LogicalResourceId, 'Orders')].PhysicalResourceId | [0]" \
  --output text)"
RECEIPTS_BUCKET="$(aws cloudformation describe-stacks \
  --stack-name "${APP_STACK}" \
  --query "Stacks[0].Outputs[?OutputKey=='ReceiptsBucketName'].OutputValue | [0]" \
  --output text)"

if [[ -n "${ORDERS_TABLE}" && "${ORDERS_TABLE}" != "None" ]]; then
  aws dynamodb put-item --table-name "${ORDERS_TABLE}" --region "${AWS_REGION}" \
    --item '{"orderId":{"S":"ORD-000123"},"summary":{"S":"1x Flat White, 1x Croissant"},"total":{"N":"12.50"}}' || true
  aws dynamodb put-item --table-name "${ORDERS_TABLE}" --region "${AWS_REGION}" \
    --item '{"orderId":{"S":"ORD-000456"},"summary":{"S":"2x Latte"},"total":{"N":"9.00"}}' || true
fi

if [[ -n "${RECEIPTS_BUCKET}" && "${RECEIPTS_BUCKET}" != "None" ]]; then
  TMP_PDF="$(mktemp -t receipt.XXXXXX).pdf"
  printf '%%PDF-1.4\n%% session5 demo receipt for ORD-000123\n' > "${TMP_PDF}"
  aws s3 cp "${TMP_PDF}" "s3://${RECEIPTS_BUCKET}/receipts/ORD-000123.pdf" || true
  rm -f "${TMP_PDF}"
fi

# --- 6. Resolve the CloudFront URL ------------------------------------------
echo "==> [6/6] Resolving the CloudFront URL"
CLOUDFRONT_URL="$(aws cloudformation describe-stacks \
  --stack-name "${APP_STACK}" \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontUrl'].OutputValue | [0]" \
  --output text 2>/dev/null || true)"

echo ""
echo "============================================================"
echo " secure-assistant deployed in ${AWS_REGION}"
echo "------------------------------------------------------------"
if [[ -n "${CLOUDFRONT_URL}" && "${CLOUDFRONT_URL}" != "None" ]]; then
  echo " CloudFront URL : ${CLOUDFRONT_URL}  (the single entry point)"
else
  echo " CloudFront URL : (not available yet — distribution may still deploy)"
fi
echo "------------------------------------------------------------"
echo " Try: open the SPA, ask the assistant about ORD-000123, request a"
echo " refund (it returns PENDING), click Confirm, then Download receipt."
echo " Remember to run ./destroy.sh when finished — this costs money."
echo "============================================================"
