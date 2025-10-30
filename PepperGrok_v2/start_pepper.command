#!/bin/bash
# Launch script for PepperGrok v2 on macOS.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

if [ -d "venv" ]; then
  source "venv/bin/activate"
fi

export PYTHONPATH="$SCRIPT_DIR"

uvicorn app.server:app --host 0.0.0.0 --port 8000 &
UVICORN_PID=$!

cleanup() {
  kill "$UVICORN_PID" 2>/dev/null || true
}

trap cleanup EXIT

sleep 2
if command -v open >/dev/null 2>&1; then
  open "http://localhost:8000/ui" >/dev/null 2>&1 || true
fi

wait "$UVICORN_PID"
