#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# gate.sh - headless post-deployment validation gate
#
# Runs Kiro CLI in headless mode to review a deployment log and decide whether
# the build may be promoted. Exits 0 if validation PASSED, non-zero if FAILED.
# A CI/CD pipeline stage reads this exit code to stop promotion automatically.
#
# Usage:
#   ./gate.sh <path-to-deploy-log>
#
# Examples:
#   ./gate.sh deploy.pass.log   # -> prints PASS, exit 0  (pipeline promotes)
#   ./gate.sh deploy.fail.log   # -> prints FAIL, exit 1  (pipeline halts)
# ---------------------------------------------------------------------------
set -euo pipefail

log="${1:-}"
if [[ -z "$log" ]]; then
  echo "usage: $0 <path-to-deploy-log>" >&2
  exit 2
fi
if [[ ! -f "$log" ]]; then
  echo "error: log file not found: $log" >&2
  exit 2
fi

# Ask the agent for a single-word verdict. --trust-tools=fs_read lets it read
# the log without prompting; --no-interactive runs with no human in the loop.
out=$(kiro-cli chat --no-interactive --trust-tools=fs_read \
  "Review the file $log. It contains post-deployment validation checks. \
If every check passed, print exactly PASS. If any check failed, print exactly FAIL.")

echo "$out"

# Translate the model's verdict into a pipeline-usable exit code.
if grep -q '\bPASS\b' <<<"$out"; then
  echo ">> validation passed - promoting build to production"
  exit 0
else
  echo ">> validation failed - stopping promotion" >&2
  exit 1
fi
