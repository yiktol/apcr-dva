#!/usr/bin/env bash
# Serve the APCR-DVA content-review slide app over HTTP.
# The deck works by opening index.html / deck.html directly (file://) because
# the decks/m1.js bundle assigns window.DECK_DATA; serving over HTTP also
# enables the decks/m1.json fetch fallback.
#
# Two serve modes:
#   serve.sh              -- static only. No /judge backend, so the
#                             Knowledge Check's AI judge call fails fast and
#                             falls back to local explanations.
#   serve_with_judge.py   -- static + a real /judge endpoint backed by
#                             Amazon Bedrock, which fetches live AWS docs and
#                             grades each question against them.
#
# Usage:  ./serve.sh [PORT]     (default 8030)
set -euo pipefail
PORT="${1:-8030}"
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if lsof -tiTCP:"$PORT" -sTCP:LISTEN >/dev/null 2>&1; then
  echo "Port $PORT busy; freeing it."
  lsof -tiTCP:"$PORT" -sTCP:LISTEN | xargs kill -9 2>/dev/null || true
  sleep 1
fi
echo "Serving $DIR at http://localhost:$PORT/"
echo "Open:  http://localhost:$PORT/index.html   (Ctrl-C to stop)"
exec python3 -m http.server "$PORT" --bind 127.0.0.1 --directory "$DIR"
