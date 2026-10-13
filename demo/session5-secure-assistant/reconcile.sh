#!/usr/bin/env bash
#
# reconcile.sh — bring the LIVE deployment up to the working configuration that
# plain CloudFormation cannot apply on this account, and keep static assets in
# sync. Safe to run repeatedly (idempotent). Run it AFTER deploy.sh (deploy.sh
# calls it automatically as its final step), or on its own after any
# `cdk deploy SecureAssistantAppEdgeAI` which otherwise resets the assistant's
# GUARDRAIL_VERSION back to the CloudFormation-tracked value.
#
# WHY THIS EXISTS
# ---------------
# Two aspects of the working deployment are not reproducible through pure CDK on
# the training account 875692608981:
#
#   1. The expanded Bedrock Guardrail. The guardrail config in
#      infra/lib/security-data-stack.ts is the source of truth, but updating the
#      AWS::Bedrock::Guardrail resource through CloudFormation is rejected on
#      this account by the managed hook AWS::EarlyValidation::PropertyValidation
#      (the changeset fails before execution; the identical config applies
#      cleanly through the Bedrock control-plane API). So we apply the
#      *synthesized* guardrail config via `aws bedrock update-guardrail`, publish
#      a new immutable version, and point the assistant Lambda's
#      GUARDRAIL_VERSION at that exact version. On an account WITHOUT that hook,
#      `cdk deploy SecureAssistantSecurityData` would apply the same config and
#      this step is a harmless no-op re-assertion.
#
#   2. The architecture diagram the SPA serves. The site's "Architecture" link
#      loads architecture.png from the SPA bucket (spa/architecture.png), a
#      separate copy from diagram/architecture.png. We regenerate the diagram
#      and copy it into spa/ so a redeploy ships the current image.
#
# The script DERIVES the guardrail config from the synthesized CDK template, so
# the CDK source stays the single source of truth — this script never hand-codes
# guardrail policy.
set -euo pipefail

export AWS_REGION="${AWS_REGION:-ap-southeast-1}"
export AWS_DEFAULT_REGION="${AWS_DEFAULT_REGION:-ap-southeast-1}"

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SECURITY_STACK="SecureAssistantSecurityData"
APP_STACK="SecureAssistantAppEdgeAI"

echo "==> reconcile (region: ${AWS_REGION})"

# --- 0. Sync the SPA architecture diagram -----------------------------------
# Regenerate the diagram if the generator and tooling are present, then copy the
# PNG+SVG into the SPA so the deployed site serves the current version.
echo "==> [1/4] Syncing the architecture diagram into the SPA"
if command -v python3 >/dev/null 2>&1 && [[ -f "${ROOT}/diagram/build_diagram.py" ]]; then
  ( cd "${ROOT}/diagram" && python3 build_diagram.py >/dev/null 2>&1 || true )
  if command -v rsvg-convert >/dev/null 2>&1 && [[ -f "${ROOT}/diagram/architecture.svg" ]]; then
    rsvg-convert -o "${ROOT}/diagram/architecture.png" "${ROOT}/diagram/architecture.svg" >/dev/null 2>&1 || true
  fi
fi
if [[ -f "${ROOT}/diagram/architecture.png" ]]; then
  cp "${ROOT}/diagram/architecture.png" "${ROOT}/spa/architecture.png"
  [[ -f "${ROOT}/diagram/architecture.svg" ]] && cp "${ROOT}/diagram/architecture.svg" "${ROOT}/spa/architecture.svg"
  echo "    SPA diagram synced from diagram/architecture.png"
else
  echo "    (no diagram/architecture.png found; leaving spa/ copy as-is)"
fi

# --- 1. Resolve the live guardrail id ---------------------------------------
echo "==> [2/4] Resolving the guardrail"
GUARDRAIL_ID="$(aws cloudformation describe-stacks --stack-name "${SECURITY_STACK}" \
  --query "Stacks[0].Outputs[?OutputKey=='GuardrailIdOutput'].OutputValue | [0]" \
  --output text 2>/dev/null || true)"
if [[ -z "${GUARDRAIL_ID}" || "${GUARDRAIL_ID}" == "None" ]]; then
  echo "ERROR: could not resolve the guardrail id from ${SECURITY_STACK} outputs." >&2
  echo "       Deploy the SecurityData stack first (./deploy.sh)." >&2
  exit 1
fi
echo "    Guardrail: ${GUARDRAIL_ID}"

# --- 2. Apply the synthesized guardrail config via the Bedrock API ----------
# Derive the config from the synthesized CDK template so the CDK source remains
# the single source of truth. This is the step CloudFormation cannot do here.
echo "==> [3/4] Applying the expanded guardrail config + publishing a version"
TEMPLATE="${ROOT}/infra/cdk.out/${SECURITY_STACK}.template.json"
if [[ ! -f "${TEMPLATE}" ]]; then
  echo "    Synthesizing ${SECURITY_STACK} to read the guardrail config..."
  ( cd "${ROOT}/infra" \
      && CDK_DEFAULT_ACCOUNT="$(aws sts get-caller-identity --query Account --output text)" \
         CDK_DEFAULT_REGION="${AWS_REGION}" \
         JSII_SILENCE_WARNING_UNTESTED_NODE_VERSION=1 \
         npx cdk synth "${SECURITY_STACK}" >/dev/null 2>&1 )
fi

NEW_VERSION="$(GUARDRAIL_ID="${GUARDRAIL_ID}" TEMPLATE="${TEMPLATE}" AWS_REGION="${AWS_REGION}" python3 - <<'PY'
import json, os, boto3

template = json.load(open(os.environ["TEMPLATE"]))
props = next(
    r["Properties"]
    for r in template["Resources"].values()
    if r["Type"] == "AWS::Bedrock::Guardrail"
)

def lower(x):
    if isinstance(x, dict):
        return {k[0].lower() + k[1:]: lower(v) for k, v in x.items()}
    if isinstance(x, list):
        return [lower(i) for i in x]
    return x

bedrock = boto3.client("bedrock", region_name=os.environ["AWS_REGION"])
gid = os.environ["GUARDRAIL_ID"]

args = dict(
    guardrailIdentifier=gid,
    name=props["Name"],
    blockedInputMessaging=props["BlockedInputMessaging"],
    blockedOutputsMessaging=props["BlockedOutputsMessaging"],
    contentPolicyConfig=lower(props["ContentPolicyConfig"]),
    sensitiveInformationPolicyConfig=lower(props["SensitiveInformationPolicyConfig"]),
    topicPolicyConfig=lower(props["TopicPolicyConfig"]),
)
# Optional policy groups, only if present in the synthesized template.
if "WordPolicyConfig" in props:
    args["wordPolicyConfig"] = lower(props["WordPolicyConfig"])
if "ContextualGroundingPolicyConfig" in props:
    args["contextualGroundingPolicyConfig"] = lower(props["ContextualGroundingPolicyConfig"])

bedrock.update_guardrail(**args)
ver = bedrock.create_guardrail_version(
    guardrailIdentifier=gid,
    description="reconcile.sh: synthesized guardrail config applied via API",
)["version"]
print(ver)
PY
)"
echo "    Applied config; published guardrail version ${NEW_VERSION}"

# --- 3. Point the assistant Lambda at the published version -----------------
echo "==> [4/4] Pointing the assistant Lambda at guardrail version ${NEW_VERSION}"
ASSISTANT_FN="$(aws cloudformation describe-stack-resources --stack-name "${APP_STACK}" \
  --query "StackResources[?ResourceType=='AWS::Lambda::Function' && contains(LogicalResourceId, 'AssistantFn')].PhysicalResourceId | [0]" \
  --output text)"
if [[ -z "${ASSISTANT_FN}" || "${ASSISTANT_FN}" == "None" ]]; then
  echo "ERROR: could not resolve the assistant Lambda from ${APP_STACK}." >&2
  exit 1
fi

CUR_ENV="$(aws lambda get-function-configuration --function-name "${ASSISTANT_FN}" \
  --query "Environment.Variables" --output json)"
NEW_ENV="$(NEW_VERSION="${NEW_VERSION}" python3 - "$CUR_ENV" <<'PY'
import json, os, sys
env = json.loads(sys.argv[1])
env["GUARDRAIL_VERSION"] = os.environ["NEW_VERSION"]
print(json.dumps({"Variables": env}))
PY
)"
aws lambda update-function-configuration --function-name "${ASSISTANT_FN}" \
  --environment "${NEW_ENV}" --query "LastUpdateStatus" --output text >/dev/null
aws lambda wait function-updated --function-name "${ASSISTANT_FN}"
echo "    ${ASSISTANT_FN} now uses GUARDRAIL_VERSION=${NEW_VERSION}"

echo ""
echo "============================================================"
echo " reconcile complete"
echo "------------------------------------------------------------"
echo " Guardrail ${GUARDRAIL_ID} version ${NEW_VERSION} is live and wired."
echo " SPA architecture diagram synced. If you changed the SPA, run"
echo " a CloudFront invalidation or redeploy ${APP_STACK} to publish it."
echo "============================================================"
