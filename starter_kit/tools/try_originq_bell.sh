#!/usr/bin/env bash
# One-shot OriginQ Wukong Bell evidence attempt (120s wall clock).
# Secrets stay in starter_kit/.env (gitignored). Does not open a Final Issue.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if command -v python3 >/dev/null 2>&1; then
  PY=python3
else
  PY=python
fi
# Prefer a venv that already has pyqpanda when available.
for candidate in \
  "$ROOT/../LoomQ-2026-Jessica/.venv/bin/python" \
  "$ROOT/.venv/bin/python"; do
  if [ -x "$candidate" ] && "$candidate" -c "import pyqpanda" 2>/dev/null; then
    PY="$candidate"
    break
  fi
done

export LOOMQ_ORIGINQ_MODE="${LOOMQ_ORIGINQ_MODE:-wukong}"
# Official Q&A allows WK_C180; backends.py maps it to pyqpanda chip_id=72.
export LOOMQ_ORIGINQ_CHIP="${LOOMQ_ORIGINQ_CHIP:-WK_C180}"
export LOOMQ_ORIGINQ_TIMEOUT_SEC="${LOOMQ_ORIGINQ_TIMEOUT_SEC:-120}"
export LOOMQ_ORIGINQ_POLL_SEC="${LOOMQ_ORIGINQ_POLL_SEC:-2}"
export PYTHONPATH="$ROOT"

SHOTS="${1:-256}"
echo "OriginQ Bell attempt: mode=$LOOMQ_ORIGINQ_MODE chip=$LOOMQ_ORIGINQ_CHIP timeout=${LOOMQ_ORIGINQ_TIMEOUT_SEC}s shots=$SHOTS"
echo "python: $PY"
exec "$PY" "$ROOT/tools/run_bell_evidence.py" --platform originq --shots "$SHOTS"
