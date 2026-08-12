#!/usr/bin/env bash
# One-command L2 web launcher (keeps running until Ctrl+C).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
elif command -v python >/dev/null 2>&1; then
  PY=python
else
  echo "No python3/python found. Install Python 3.10+." >&2
  exit 1
fi

PORT="${LOOMQ_WEB_PORT:-8765}"
export PYTHONPATH="$ROOT"

echo "Starting LoomQ L2 web on http://127.0.0.1:${PORT}/"
echo "Directory: $ROOT"
echo "Press Ctrl+C to stop."
exec "$PY" web/server.py --host 127.0.0.1 --port "$PORT"
