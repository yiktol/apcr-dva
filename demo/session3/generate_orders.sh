#!/usr/bin/env bash
# =============================================================================
# BeanThere - random order generator
# Places random coffee orders as random superhero customers, to populate the
# orders table, CloudWatch metrics, and the dashboard.
#
#   ./generate_orders.sh [count] [delay_seconds]
#
#   count          how many orders to place   (default 20)
#   delay_seconds  pause between orders        (default 1)
#
# Occasionally emits a "failing" order so the SQS dead-letter queue fills too.
# Targets the deployed stack in ap-southeast-1 using current credentials.
# =============================================================================
set -euo pipefail
export AWS_PAGER=""

REGION="${REGION:-ap-southeast-1}"
STACK="${STACK:-beanthere}"
COUNT="${1:-20}"
DELAY="${2:-1}"

c_reset=$'\033[0m'; c_g=$'\033[32m'; c_b=$'\033[36m'; c_y=$'\033[33m'
say()  { printf "%s\n" "${c_b}==>${c_reset} $*"; }
ok()   { printf "%s\n" "${c_g}  +${c_reset} $*"; }

API="$(aws cloudformation describe-stacks --stack-name "$STACK" --region "$REGION" \
  --query "Stacks[0].Outputs[?OutputKey=='ApiUrl'].OutputValue" --output text 2>/dev/null)"
[ -n "$API" ] && [ "$API" != "None" ] || { echo "no ApiUrl - is the stack deployed?"; exit 1; }
API="${API%/}"

# Random superhero customers (nickname used as customerId so the orders table reads nicely).
CUSTOMERS=( superman batman spiderman ironman wonderwoman )
# Menu items and their prices (match the seeded menu).
declare -a MENU=( "esp:3.00:Espresso" "lat:4.50:Latte" "cap:4.00:Cappuccino" "moc:5.00:Mocha" "cbr:4.75:Cold Brew" )

# Make sure the menu is seeded so orders reference real items.
curl -s -X POST "$API/seed" >/dev/null || true

say "Placing $COUNT random orders against $API (delay ${DELAY}s)"

placed=0; failing=0
for i in $(seq 1 "$COUNT"); do
  cust="${CUSTOMERS[$((RANDOM % ${#CUSTOMERS[@]}))]}"

  # 1-3 distinct-ish line items, random quantities.
  n=$(( (RANDOM % 3) + 1 ))
  items="["; total=0
  for j in $(seq 1 "$n"); do
    entry="${MENU[$((RANDOM % ${#MENU[@]}))]}"
    id="${entry%%:*}"; rest="${entry#*:}"; price="${rest%%:*}"
    qty=$(( (RANDOM % 2) + 1 ))
    [ "$j" -gt 1 ] && items+=","
    items+="{\"id\":\"$id\",\"qty\":$qty}"
    # total += price*qty  (bc for float math)
    total=$(echo "$total + $price * $qty" | bc)
  done
  items+="]"

  # ~1 in 8 orders is a poison message -> exercises the dead-letter queue.
  fail=false
  if [ $(( RANDOM % 8 )) -eq 0 ]; then fail=true; failing=$((failing+1)); fi

  body="{\"customerId\":\"$cust\",\"items\":$items,\"total\":$total,\"simulateFailure\":$fail}"
  resp="$(curl -s -X POST "$API/orders" -H 'content-type: application/json' -d "$body")"
  oid="$(echo "$resp" | sed -n 's/.*"orderId":"\([^"]*\)".*/\1/p')"
  placed=$((placed+1))
  if $fail; then
    ok "$cust  \$${total}  ${oid}  ${c_y}(failing -> DLQ)${c_reset}"
  else
    ok "$cust  \$${total}  ${oid}"
  fi
  sleep "$DELAY"
done

echo
say "Done: $placed orders placed ($failing designed to fail into the DLQ)."
say "Watch them at the app's 'All orders' table and the CloudWatch dashboard."
