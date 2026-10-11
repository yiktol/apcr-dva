#!/usr/bin/env bash
# Serve the APCR-DVA content-review slide app over HTTP.
# The deck works by opening index.html / deck.html directly (file://) because
# the decks/m1.js bundle assigns window.DECK_DATA; serving over HTTP also
# enables the decks/m1.json fetch fallback.
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
