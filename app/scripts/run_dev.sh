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

uvicorn app.backend.main:app --reload --host 127.0.0.1 --port 8000 &
BACKEND_PID=$!

echo "FastAPI running at http://127.0.0.1:8000"

cd "$ROOT_DIR/frontend"

if [ ! -d "node_modules" ]; then
  echo "Installing frontend dependencies..."
  npm install
fi

npm run dev -- --host 127.0.0.1 --port 5173 &
FRONTEND_PID=$!

echo "Frontend running at http://127.0.0.1:5173"

echo "Press Ctrl+C to stop both services."

trap 'kill $BACKEND_PID $FRONTEND_PID' EXIT
wait
