#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if [ ! -d "../.venv" ]; then
  echo "Python venv not found. Run 'python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt' first." >&2
  exit 1
fi

source ../.venv/bin/activate
export PYTHONPATH="$ROOT_DIR/..:$PYTHONPATH"

python -m app.scripts.seed_data >/tmp/asr_seed.log

echo "Launching ASR Copilot demo (Safe Mode ON)."

uvicorn app.backend.main:app --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

sleep 2

echo "Backend ready at http://127.0.0.1:8000"

cd "$ROOT_DIR/frontend"
if [ ! -d "node_modules" ]; then
  npm install
fi
npm run dev -- --host 127.0.0.1 --port 5173 &
FRONTEND_PID=$!

sleep 2

echo "Frontend ready at http://127.0.0.1:5173"
python - <<'PY'
import webbrowser
webbrowser.open("http://127.0.0.1:5173")
PY

echo "Status Pack exports will appear in ../out/"

echo "Press Ctrl+C to exit demo."

trap 'kill $BACKEND_PID $FRONTEND_PID' EXIT
wait
