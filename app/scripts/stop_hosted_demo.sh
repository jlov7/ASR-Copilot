#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
CACHE_DIR="${REPO_ROOT}/.cache"
UVICORN_PID_FILE="${CACHE_DIR}/hosted_uvicorn.pid"
HTTP_PID_FILE="${CACHE_DIR}/hosted_http.pid"

stop_pid_file() {
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

stop_pid_file "$UVICORN_PID_FILE"
stop_pid_file "$HTTP_PID_FILE"

echo "Hosted demo processes stopped (if they were running)."
