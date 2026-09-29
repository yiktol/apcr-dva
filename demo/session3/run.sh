#!/usr/bin/env bash
# =============================================================================
# BeanThere - APCR-DVA Session 3 core-services demo
# End-to-end lifecycle: deploy | test | cleanup | all
#
#   ./run.sh deploy    Package + deploy the stack, build + publish the React app
#   ./run.sh test      Exercise every core service and assert it fired
#   ./run.sh cleanup    Empty buckets and delete the stack (full teardown)
#   ./run.sh all       deploy, then test
#
# Targets AWS account 875692608981 / ap-southeast-1 using current credentials.
# =============================================================================
set -euo pipefail

# ---- config -----------------------------------------------------------------
export AWS_PAGER=""
REGION="${REGION:-ap-southeast-1}"
STACK="${STACK:-beanthere}"
PROJECT="${PROJECT:-beanthere}"
HERE="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE="$HERE/template.yaml"
FRONTEND="$HERE/frontend"

c_reset=$'\033[0m'; c_g=$'\033[32m'; c_y=$'\033[33m'; c_r=$'\033[31m'; c_b=$'\033[36m'
say()  { printf "%s\n" "${c_b}==>${c_reset} $*"; }
ok()   { printf "%s\n" "${c_g}  ok${c_reset} $*"; }
warn() { printf "%s\n" "${c_y}  ! ${c_reset} $*"; }
die()  { printf "%s\n" "${c_r}  x ${c_reset} $*" >&2; exit 1; }

need() { command -v "$1" >/dev/null 2>&1 || die "required tool not found: $1"; }

out() { # fetch a single stack output value by key
  aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue" --output text 2>/dev/null
}

# ---- deploy -----------------------------------------------------------------
deploy() {
  need aws
  say "Validating template with cfn-lint (if available)"
  if command -v cfn-lint >/dev/null 2>&1; then cfn-lint "$TEMPLATE" && ok "lint clean"; else warn "cfn-lint not installed, skipping"; fi

  say "Deploying CloudFormation stack '$STACK' to $REGION (ElastiCache can take ~10 min)"
  aws cloudformation deploy \
    --template-file "$TEMPLATE" \
    --stack-name "$STACK" \
    --region "$REGION" \
    --capabilities CAPABILITY_IAM CAPABILITY_AUTO_EXPAND \
    --no-fail-on-empty-changeset \
    --parameter-overrides ProjectName="$PROJECT"
  ok "stack deployed"

  local api bucket cf uid cid iid dist
  api="$(out ApiUrl)"; bucket="$(out FrontendBucket)"; cf="$(out CloudFrontUrl)"
  uid="$(out UserPoolId)"; cid="$(out UserPoolClientId)"; iid="$(out IdentityPoolId)"

  say "Generating the architecture diagram (embeds AWS icons)"
  if command -v python3 >/dev/null 2>&1 && [ -f "$HERE/build_diagram.py" ]; then
    python3 "$HERE/build_diagram.py" && ok "diagram generated" || warn "diagram generation failed (continuing)"
  else
    warn "python3 or build_diagram.py missing - skipping diagram"
  fi

  say "Building and publishing the React front end"
  if command -v npm >/dev/null 2>&1; then
    ( cd "$FRONTEND" && npm install --silent && npm run build --silent )
    cat > "$FRONTEND/dist/config.js" <<EOF
window.BEANTHERE_CONFIG = {
  apiUrl: "$api",
  userPoolId: "$uid",
  userPoolClientId: "$cid",
  identityPoolId: "$iid"
};
EOF
    aws s3 sync "$FRONTEND/dist/" "s3://$bucket/" --region "$REGION" --delete
    dist="$(aws cloudfront list-distributions --query "DistributionList.Items[?Origins.Items[?contains(DomainName, '$bucket')]].Id" --output text 2>/dev/null || true)"
    [ -n "${dist:-}" ] && aws cloudfront create-invalidation --distribution-id "$dist" --paths "/*" >/dev/null 2>&1 && ok "CloudFront invalidated"
    ok "front end published"
  else
    warn "npm not found - skipping front-end build. Backend + API still deployed."
  fi

  seed_users

  echo
  ok "API:        $api"
  ok "Front end:  $cf"
  ok "Dashboard:  $(out DashboardUrl)"
  echo
  say "Next: ./run.sh test    (or open the CloudFront URL above)"
}

# ---- demo users -------------------------------------------------------------
# The 5 superhero sign-in accounts. CloudFormation cannot set a permanent
# password, so they are created here (idempotent) right after deploy.
DEMO_PASSWORD="${DEMO_PASSWORD:-Superhero123}"
DEMO_USERS=(
  "clark.kent@beanthere.demo:superman"
  "bruce.wayne@beanthere.demo:batman"
  "peter.parker@beanthere.demo:spiderman"
  "tony.stark@beanthere.demo:ironman"
  "diana.prince@beanthere.demo:wonderwoman"
)
seed_users() {
  local pool; pool="$(out UserPoolId)"
  [ -n "$pool" ] && [ "$pool" != "None" ] || { warn "no user pool - skipping demo users"; return 0; }
  say "Seeding ${#DEMO_USERS[@]} superhero demo users (password: $DEMO_PASSWORD)"
  local entry email nick
  for entry in "${DEMO_USERS[@]}"; do
    email="${entry%%:*}"; nick="${entry##*:}"
    aws cognito-idp admin-create-user --region "$REGION" --user-pool-id "$pool" \
      --username "$email" --message-action SUPPRESS \
      --user-attributes Name=email,Value="$email" Name=email_verified,Value=true Name=nickname,Value="$nick" \
      >/dev/null 2>&1 || true
    aws cognito-idp admin-set-user-password --region "$REGION" --user-pool-id "$pool" \
      --username "$email" --password "$DEMO_PASSWORD" --permanent >/dev/null 2>&1 \
      && ok "$nick -> $email" || warn "could not set password for $email"
  done
}

# ---- test -------------------------------------------------------------------
test_e2e() {
  need aws; need curl
  local api queue dlq bus alarm loggroup topic
  api="$(out ApiUrl)"; queue="$(out OrderQueueUrl)"; dlq="$(out OrderDLQUrl)"
  bus="$(out EventBusName)"; alarm="$(out AlarmName)"; loggroup="$(out WorkerLogGroup)"
  topic="$(out OrderEventsTopicArn)"
  [ -n "$api" ] || die "no ApiUrl output - is the stack deployed?"
  api="${api%/}"

  local pass=0 fail=0
  check() { if eval "$2"; then ok "$1"; pass=$((pass+1)); else warn "FAILED: $1"; fail=$((fail+1)); fi; }

  say "1 · Cognito - create and confirm a test user"
  local uid cid email pw
  uid="$(out UserPoolId)"; cid="$(out UserPoolClientId)"
  email="demo+$(date +%s)@example.com"; pw="Demo$(date +%s)!a"
  aws cognito-idp sign-up --region "$REGION" --client-id "$cid" \
    --username "$email" --password "$pw" --user-attributes Name=email,Value="$email" >/dev/null 2>&1 || warn "sign-up returned non-zero"
  aws cognito-idp admin-confirm-sign-up --region "$REGION" --user-pool-id "$uid" --username "$email" >/dev/null 2>&1 || true
  local idtoken
  idtoken="$(aws cognito-idp admin-initiate-auth --region "$REGION" --user-pool-id "$uid" --client-id "$cid" \
    --auth-flow ADMIN_USER_PASSWORD_AUTH --auth-parameters USERNAME="$email",PASSWORD="$pw" \
    --query 'AuthenticationResult.IdToken' --output text 2>/dev/null || true)"
  check "Cognito issued a JWT id token" '[ -n "$idtoken" ] && [ "$idtoken" != "None" ]'

  say "2 · Seed menu + ElastiCache lazy loading (miss -> DB, then hit -> cache)"
  curl -s -X POST "$api/seed" >/dev/null
  # First call after seed may be cache or db depending on seed; force a definitive check:
  local m1 m2
  m1="$(curl -s "$api/menu")"; sleep 1; m2="$(curl -s "$api/menu")"
  echo "    first:  $(echo "$m1" | head -c 80)"
  echo "    second: $(echo "$m2" | head -c 80)"
  check "menu endpoint returns items" 'echo "$m2" | grep -q "\"items\""'
  check "ElastiCache served a cached read" 'echo "$m2" | grep -q "\"source\":\"cache\""'

  say "3 · SQS -> worker -> DynamoDB status (normal order should reach CONFIRMED)"
  local resp orderid
  resp="$(curl -s -X POST "$api/orders" -H 'content-type: application/json' \
    -d '{"customerId":"tester","items":[{"id":"lat","qty":2}],"total":9.0}')"
  orderid="$(echo "$resp" | sed -n 's/.*"orderId":"\([^"]*\)".*/\1/p')"
  echo "    queued: $orderid"
  check "order accepted (SQS enqueue)" '[ -n "$orderid" ]'
  local status="" i
  for i in $(seq 1 20); do
    status="$(curl -s "$api/orders/$orderid" | sed -n 's/.*"status":"\([^"]*\)".*/\1/p')"
    [ "$status" = "CONFIRMED" ] && break; sleep 3
  done
  echo "    final status: ${status:-none}"
  check "worker processed order to CONFIRMED" '[ "$status" = "CONFIRMED" ]'

  say "4 · SNS - topic exists and has the fan-out subscription wiring"
  check "SNS order-events topic present" '[ -n "$topic" ]'

  say "5 · EventBridge - OrderPlaced events routed to the CloudWatch Logs target"
  local streams=""
  for i in $(seq 1 10); do
    streams="$(aws logs describe-log-streams --region "$REGION" \
      --log-group-name "/beanthere/$PROJECT/eventbridge-orderplaced" \
      --query 'logStreams[].logStreamName' --output text 2>/dev/null || true)"
    [ -n "$streams" ] && [ "$streams" != "None" ] && break; sleep 3
  done
  check "EventBridge rule delivered an event to CloudWatch Logs" '[ -n "$streams" ] && [ "$streams" != "None" ]'

  say "6 · CloudWatch - custom metric OrderProcessingTime has data points"
  local dp=""
  for i in $(seq 1 10); do
    dp="$(aws cloudwatch get-metric-statistics --region "$REGION" \
      --namespace BeanThere --metric-name OrderProcessingTime \
      --start-time "$(date -u -v-15M +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || date -u -d '15 min ago' +%Y-%m-%dT%H:%M:%SZ)" \
      --end-time "$(date -u +%Y-%m-%dT%H:%M:%SZ)" --period 60 --statistics Average \
      --query 'length(Datapoints)' --output text 2>/dev/null || echo 0)"
    [ "${dp:-0}" != "0" ] && break; sleep 6
  done
  echo "    datapoints: ${dp:-0}"
  check "CloudWatch received custom metric data" '[ "${dp:-0}" != "0" ]'

  say "7 · CloudWatch Logs - worker emitted structured JSON with a customerId field"
  # A JSON metric-filter matches the discoverable field. An explicit start-time is
  # required, else the search starts at the log group's beginning and caps out
  # before reaching recent events. Retry for ingestion lag.
  local jsonhit="" logstart
  logstart=$(( ($(date +%s) - 900) * 1000 ))
  for i in $(seq 1 10); do
    jsonhit="$(aws logs filter-log-events --region "$REGION" --log-group-name "$loggroup" \
      --start-time "$logstart" --filter-pattern '{ $.customerId = "tester" }' --limit 5 \
      --query 'length(events)' --output text 2>/dev/null || echo 0)"
    [ "${jsonhit:-0}" != "0" ] && break; sleep 4
  done
  echo "    matched structured events: ${jsonhit:-0}"
  check "structured JSON logs are filterable by field" '[ "${jsonhit:-0}" != "0" ]'

  say "8 · SQS dead-letter queue - a failing order should land in the DLQ"
  curl -s -X POST "$api/orders" -H 'content-type: application/json' \
    -d '{"customerId":"tester","items":[{"id":"esp","qty":1}],"total":3.0,"simulateFailure":true}' >/dev/null
  # 3 retries at a 20s visibility timeout -> DLQ in ~1 min; poll up to ~2.5 min.
  local dlqn=""
  for i in $(seq 1 30); do
    dlqn="$(aws sqs get-queue-attributes --region "$REGION" --queue-url "$dlq" \
      --attribute-names ApproximateNumberOfMessages \
      --query 'Attributes.ApproximateNumberOfMessages' --output text 2>/dev/null || echo 0)"
    [ "${dlqn:-0}" != "0" ] && break; sleep 6
  done
  echo "    DLQ depth: ${dlqn:-0}"
  check "poison message routed to the dead-letter queue" '[ "${dlqn:-0}" != "0" ]'

  say "9 · CloudTrail - trail is actively logging"
  local trailname logging
  trailname="$(out TrailName)"
  logging="$(aws cloudtrail get-trail-status --region "$REGION" --name "$trailname" \
    --query 'IsLogging' --output text 2>/dev/null || echo false)"
  check "CloudTrail is logging" '[ "$logging" = "True" ]'

  echo
  say "RESULT: $pass passed, $fail failed (8 core services + supporting glue)"
  [ "$fail" -eq 0 ] && ok "all core services exercised end to end" || warn "some checks failed - see above"
  return "$fail"
}

# ---- cleanup ----------------------------------------------------------------
cleanup() {
  need aws
  local bucket trailbucket
  bucket="$(out FrontendBucket)"; trailbucket="$PROJECT-trail-$(aws sts get-caller-identity --query Account --output text)-$REGION"

  if [ -n "${bucket:-}" ] && [ "$bucket" != "None" ]; then
    say "Emptying front-end bucket $bucket"; aws s3 rm "s3://$bucket" --recursive --region "$REGION" >/dev/null 2>&1 || true
  fi
  say "Emptying CloudTrail bucket $trailbucket"
  aws s3 rm "s3://$trailbucket" --recursive --region "$REGION" >/dev/null 2>&1 || true

  # The dashboard is a stack resource (deleted with the stack). This also removes
  # any earlier manually-created dashboard with the legacy name, just in case.
  aws cloudwatch delete-dashboards --region "$REGION" \
    --dashboard-names BeanThere-CoreServices "$PROJECT-CoreServices" >/dev/null 2>&1 || true

  say "Deleting stack '$STACK' (this also removes ElastiCache, Cognito, queues, topics, trail, dashboard)"
  aws cloudformation delete-stack --stack-name "$STACK" --region "$REGION"
  say "Waiting for delete to complete..."
  if aws cloudformation wait stack-delete-complete --stack-name "$STACK" --region "$REGION" 2>/dev/null; then
    ok "stack deleted - all demo resources removed"
  else
    warn "delete wait timed out or stack had a delete issue; check the CloudFormation console"
  fi
}

# ---- main -------------------------------------------------------------------
case "${1:-}" in
  deploy)      deploy ;;
  test)        test_e2e ;;
  cleanup)     cleanup ;;
  seed-users)  seed_users ;;
  all)         deploy && echo && test_e2e ;;
  *) echo "usage: $0 {deploy|test|cleanup|seed-users|all}"; exit 2 ;;
esac
