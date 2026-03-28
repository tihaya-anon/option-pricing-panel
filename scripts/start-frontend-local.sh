#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_command pnpm

PID_FILE="$RUN_DIR/frontend.pid"
LOG_FILE="$RUN_DIR/frontend.log"

existing_pid="$(read_pid "$PID_FILE" || true)"
if [[ -n "${existing_pid:-}" ]] && pid_is_running "$existing_pid"; then
  log "frontend already running with pid $existing_pid"
  exit 0
fi

log "starting frontend on http://127.0.0.1:5173"
nohup setsid bash -lc \
  "cd \"$ROOT_DIR/frontend\" && exec env VITE_ENABLE_API_MOCK=false VITE_API_PROXY_TARGET=http://127.0.0.1:8000 pnpm dev -- --host 0.0.0.0 --port 5173" \
  >"$LOG_FILE" 2>&1 &
echo $! >"$PID_FILE"

sleep 2

started_pid="$(read_pid "$PID_FILE")"
if ! pid_is_running "$started_pid"; then
  log "frontend failed to start, see $LOG_FILE"
  exit 1
fi

log "frontend started with pid $started_pid"
