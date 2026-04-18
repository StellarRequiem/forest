#!/usr/bin/env bash
# Forest Status API — starts on port 7438
# Called by launchd (optional) or run manually.
set -euo pipefail

FOREST_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV="$FOREST_DIR/venv"

# Ensure fastapi + uvicorn are available
if ! "$VENV/bin/python" -c "import fastapi, uvicorn" 2>/dev/null; then
  echo "[forest-api] Installing fastapi + uvicorn into venv..."
  "$VENV/bin/pip" install --quiet "fastapi>=0.100" "uvicorn[standard]>=0.30" "httpx>=0.27"
fi

cd "$FOREST_DIR"
exec "$VENV/bin/uvicorn" api.status_api:app \
  --host 127.0.0.1 \
  --port 7438 \
  --log-level warning
