#!/usr/bin/env bash
# ---------------------------------------------------------------------------
# Kiro CLI headless usage samples
#
# "Headless" = run the agent non-interactively (no TUI, no human to approve
# tool calls). This is the pattern behind running an AI dev agent as a
# pipeline stage that gates promotion on its result.
#
# Install (Ubuntu/Linux, x86_64 or arm64):
#   curl -fsSL https://cli.kiro.dev/install | bash
#   # binary lands in ~/.local/bin/kiro-cli ; ensure that dir is on PATH
#
# First run triggers a browser auth flow. In CI you must authenticate the
# host/runner ahead of time.
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# 1. Basic headless prompt
#    Pass the prompt as the INPUT argument + --no-interactive.
# ---------------------------------------------------------------------------
kiro-cli chat --no-interactive "your prompt here"

# ---------------------------------------------------------------------------
# 2. Tool trust
#    In --no-interactive mode there is no human to approve tool calls
#    (running commands, reading/writing files). Pre-authorize what the run
#    needs, otherwise tool use stalls or is skipped.
# ---------------------------------------------------------------------------

# trust everything (simplest, least safe)
kiro-cli chat --no-interactive --trust-all-tools "run the validation checks and report pass/fail"

# trust only specific tools (safer)
kiro-cli chat --no-interactive --trust-tools=fs_read "summarize the errors in ./deploy.log"

# trust no tools (pure text answer, no side effects)
kiro-cli chat --no-interactive --trust-tools= "explain what a non-zero exit code means"

# ---------------------------------------------------------------------------
# 3. Machine-readable output
#    JSON Lines stream for parsing in a script (implies --no-interactive).
# ---------------------------------------------------------------------------
kiro-cli chat --output-format stream-json "your prompt" > events.jsonl

# ---------------------------------------------------------------------------
# 4. Feed a prompt from a file or stdin (handy for long validation prompts)
# ---------------------------------------------------------------------------
kiro-cli chat --no-interactive "$(cat prompt.txt)"
# or
echo "check these logs: $(cat deploy.log)" | xargs -0 kiro-cli chat --no-interactive

# ---------------------------------------------------------------------------
# 5. Pipeline-gating wrapper
#    The CLI exits 0 when the RUN succeeds, regardless of the model's verdict,
#    so a "FAIL" verdict will NOT by itself produce a non-zero exit. To gate a
#    pipeline, make the model emit a sentinel and translate it to an exit code.
#
#    Two sample logs are provided to demo both paths:
#      deploy.pass.log  -> 7/7 checks pass  -> agent prints PASS -> exit 0 (promote)
#      deploy.fail.log  -> payment-callback 500 -> agent prints FAIL -> exit 1 (stop)
# ---------------------------------------------------------------------------

# The gate logic lives in a standalone, executable script: gate.sh
# It takes a log file, runs the agent headless, and exits 0 (pass) or 1 (fail).

# Demo the passing path (exits 0, pipeline would promote):
./gate.sh ./deploy.pass.log
echo "exit=$?"

# Demo the failing path (exits non-zero, pipeline would halt):
./gate.sh ./deploy.fail.log
echo "exit=$?"
