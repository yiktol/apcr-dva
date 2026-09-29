#!/usr/bin/env bash
# =============================================================================
# BeanThere - full teardown
# Removes EVERYTHING this demo created in AWS:
#   - empties the front-end and CloudTrail S3 buckets (so the stack can delete)
#   - deletes the CloudFormation stack  (ElastiCache, Cognito, SQS+DLQ, SNS,
#     EventBridge, CloudWatch alarm + dashboard, CloudTrail, Lambdas, API GW,
#     DynamoDB, CloudFront, S3 buckets)
#   - removes out-of-band resources run.sh's own cleanup doesn't:
#       * the scoped Logs-Insights inline policy added to the public-dashboard
#         sharing role (Option B grant)
#       * any leftover CloudWatch dashboards with the demo names
#
#   ./cleanup.sh          # prompts before deleting
#   ./cleanup.sh --yes    # no prompt (for scripts/CI)
#
# Targets account 875692608981 / ap-southeast-1 using current credentials.
# Leaves the shared VPC and any other stacks untouched.
# =============================================================================
set -euo pipefail
export AWS_PAGER=""

REGION="${REGION:-ap-southeast-1}"
STACK="${STACK:-beanthere}"
PROJECT="${PROJECT:-beanthere}"
ASSUME_YES="false"
case "${1:-}" in
  --yes|-y) ASSUME_YES="true" ;;
  "") ;;
  *) echo "usage: $0 [--yes|-y]"; exit 2 ;;
esac

c_reset=$'\033[0m'; c_g=$'\033[32m'; c_y=$'\033[33m'; c_r=$'\033[31m'; c_b=$'\033[36m'
say()  { printf "%s\n" "${c_b}==>${c_reset} $*"; }
ok()   { printf "%s\n" "${c_g}  +${c_reset} $*"; }
warn() { printf "%s\n" "${c_y}  ! ${c_reset} $*"; }
die()  { printf "%s\n" "${c_r}  x ${c_reset} $*" >&2; exit 1; }

command -v aws >/dev/null 2>&1 || die "aws CLI not found"

ACCOUNT="$(aws sts get-caller-identity --query Account --output text 2>/dev/null || true)"
if [ -z "$ACCOUNT" ] || [ "$ACCOUNT" = "None" ]; then
  die "AWS credentials are not valid (SSO token may have expired). Run your login (e.g. 'aws sso login') and retry."
fi

out() {
  aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text 2>/dev/null
}

stack_exists() {
  aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" >/dev/null 2>&1
}

# ---- what will be removed ---------------------------------------------------
FRONT_BUCKET="$(out FrontendBucket 2>/dev/null || true)"
[ -z "$FRONT_BUCKET" ] || [ "$FRONT_BUCKET" = "None" ] && FRONT_BUCKET="$PROJECT-web-$ACCOUNT-$REGION"
TRAIL_BUCKET="$PROJECT-trail-$ACCOUNT-$REGION"

say "This will permanently delete the BeanThere demo in account $ACCOUNT / $REGION:"
echo "    - CloudFormation stack:   $STACK  (all its resources)"
echo "    - S3 front-end bucket:    $FRONT_BUCKET"
echo "    - S3 CloudTrail bucket:   $TRAIL_BUCKET"
echo "    - CloudWatch dashboards:  $PROJECT-CoreServices, BeanThere-CoreServices"
echo "    - Sharing-role log grant: inline policy 'beanthere-logs-insights-worker' (if present)"
echo "    (the shared VPC and other stacks are left untouched)"
echo

if [ "$ASSUME_YES" != "true" ]; then
  printf "Type 'delete' to proceed: "
  read -r ans
  [ "$ans" = "delete" ] || die "aborted - nothing deleted"
fi

# ---- 1. empty S3 buckets (stack delete fails on non-empty buckets) ----------
for b in "$FRONT_BUCKET" "$TRAIL_BUCKET"; do
  if aws s3api head-bucket --bucket "$b" >/dev/null 2>&1; then
    say "Emptying s3://$b"
    aws s3 rm "s3://$b" --recursive --region "$REGION" >/dev/null 2>&1 || true
    # also purge any versioned objects / delete markers, if versioning was on
    aws s3api list-object-versions --bucket "$b" --output json 2>/dev/null \
      | python3 -c "
import sys,json
try: d=json.load(sys.stdin)
except Exception: sys.exit(0)
items=(d.get('Versions',[]) or [])+(d.get('DeleteMarkers',[]) or [])
import subprocess
for it in items:
    subprocess.run(['aws','s3api','delete-object','--bucket','$b',
        '--key',it['Key'],'--version-id',it['VersionId'],'--region','$REGION'],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
" 2>/dev/null || true
    ok "emptied $b"
  else
    warn "bucket $b not found (already gone)"
  fi
done

# ---- 2. remove the Option B log-query grant on the sharing role -------------
# Find any CWDBSharing role whose attached policy scopes to our dashboard, and
# drop the inline policy we added. This is out-of-band (CloudWatch-managed role).
say "Removing the public-dashboard Logs-Insights grant (if present)"
found_role=""
for R in $(aws iam list-roles --query "Roles[?starts_with(RoleName,'CWDBSharing-PublicReadOnlyAccess')].RoleName" --output text 2>/dev/null | tr '\t' '\n'); do
  # our inline policy name is fixed; just try to delete it from each role
  if aws iam get-role-policy --role-name "$R" --policy-name beanthere-logs-insights-worker >/dev/null 2>&1; then
    aws iam delete-role-policy --role-name "$R" --policy-name beanthere-logs-insights-worker >/dev/null 2>&1 \
      && { ok "removed grant from $R"; found_role="$R"; }
  fi
done
[ -n "$found_role" ] || warn "no log-query grant found (nothing to remove)"

# ---- 3. delete CloudWatch dashboards (also stack-managed, belt & suspenders) -
aws cloudwatch delete-dashboards --region "$REGION" \
  --dashboard-names "$PROJECT-CoreServices" "BeanThere-CoreServices" >/dev/null 2>&1 \
  && ok "deleted CloudWatch dashboards" || warn "no dashboards to delete"

# ---- 4. delete the stack ----------------------------------------------------
if stack_exists; then
  say "Deleting CloudFormation stack '$STACK' (ElastiCache teardown can take a few minutes)"
  aws cloudformation delete-stack --stack-name "$STACK" --region "$REGION"
  say "Waiting for stack-delete-complete..."
  if aws cloudformation wait stack-delete-complete --stack-name "$STACK" --region "$REGION" 2>/dev/null; then
    ok "stack deleted"
  else
    warn "delete wait timed out or failed - check the CloudFormation console for '$STACK'"
    warn "a common cause is a bucket that still has objects; re-run this script."
  fi
else
  warn "stack '$STACK' not found (already deleted)"
fi

# ---- 5. sweep any orphaned buckets the stack didn't own ---------------------
for b in "$FRONT_BUCKET" "$TRAIL_BUCKET"; do
  if aws s3api head-bucket --bucket "$b" >/dev/null 2>&1; then
    warn "bucket $b still exists after stack delete - removing it directly"
    aws s3 rb "s3://$b" --force --region "$REGION" >/dev/null 2>&1 \
      && ok "removed $b" || warn "could not remove $b (check manually)"
  fi
done

echo
ok "Cleanup complete. The BeanThere demo has been torn down."
say "Note: the 5 superhero Cognito users were deleted with the user pool."
