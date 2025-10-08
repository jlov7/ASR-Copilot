#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
REPO_ROOT="$(cd "$ROOT_DIR/.." && pwd)"
PYTHON_BIN="${REPO_ROOT}/.venv/bin/python"
UVICORN_BIN="${REPO_ROOT}/.venv/bin/uvicorn"
CACHE_DIR="${REPO_ROOT}/.cache"
UVICORN_PID_FILE="${CACHE_DIR}/hosted_uvicorn.pid"
HTTP_PID_FILE="${CACHE_DIR}/hosted_http.pid"
API_PORT="${PORT:-9000}"
STATIC_PORT="${STATIC_PORT:-4173}"

ensure_python() {
  if [[ ! -x "$PYTHON_BIN" ]]; then
    echo "Python virtualenv not found at $PYTHON_BIN" >&2
    echo "Activate your venv or run 'python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt'" >&2
    exit 1
  fi
}

kill_pid_file() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid" 2>/dev/null || true
      sleep 0.2
      if kill -0 "$pid" 2>/dev/null; then
        kill -9 "$pid" 2>/dev/null || true
      fi
    fi
    rm -f "$pid_file"
  fi
}

kill_port() {
  local port="$1"
  local pids
  pids="$(lsof -ti ":${port}" 2>/dev/null || true)"
  for pid in $pids; do
    if [[ -n "$pid" ]]; then
      kill "$pid" 2>/dev/null || true
      sleep 0.2
      if kill -0 "$pid" 2>/dev/null; then
        kill -9 "$pid" 2>/dev/null || true
      fi
    fi
  done
}

start_uvicorn() {
  local env_vars=("ASR_SAFE_MODE=${ASR_SAFE_MODE:-true}" "ADAPTER_MODE=${ADAPTER_MODE:-mock}")
  nohup env "${env_vars[@]}" "$UVICORN_BIN" app.backend.main:app --host 127.0.0.1 --port "$API_PORT" \
    > "${CACHE_DIR}/hosted_uvicorn.log" 2>&1 &
  echo $! > "$UVICORN_PID_FILE"
}

start_http() {
  local dist_dir="$ROOT_DIR/frontend/dist"
  if [[ ! -f "$dist_dir/index.html" ]]; then
    echo "Frontend dist build not found. Run 'npm run build' in app/frontend first." >&2
    exit 1
  fi
  nohup "$PYTHON_BIN" -m http.server "$STATIC_PORT" --directory "$dist_dir" \
    > "${CACHE_DIR}/hosted_http.log" 2>&1 &
  echo $! > "$HTTP_PID_FILE"
}

ensure_dirs() {
  mkdir -p "$CACHE_DIR"
}

ensure_python
ensure_dirs
kill_pid_file "$UVICORN_PID_FILE"
kill_pid_file "$HTTP_PID_FILE"
kill_port "$API_PORT"
kill_port "$STATIC_PORT"

start_uvicorn
start_http

echo "Hosted demo running:"
echo "  API      → http://127.0.0.1:${API_PORT}"
echo "  Frontend → http://127.0.0.1:${STATIC_PORT}"
echo "PID files in $CACHE_DIR (hosted_uvicorn.pid, hosted_http.pid)"
