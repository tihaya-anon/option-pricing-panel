#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

require_command uv

PID_FILE="$RUN_DIR/backend.pid"
LOG_FILE="$RUN_DIR/backend.log"

existing_pid="$(read_pid "$PID_FILE" || true)"
if [[ -n "${existing_pid:-}" ]] && pid_is_running "$existing_pid"; then
  log "backend already running with pid $existing_pid"
  exit 0
fi

log "starting backend on http://127.0.0.1:8000"
nohup bash -lc "cd \"$ROOT_DIR/backend\" && exec uv run option-pricing-lab" \
  >"$LOG_FILE" 2>&1 &
echo $! >"$PID_FILE"

sleep 2

started_pid="$(read_pid "$PID_FILE")"
if ! pid_is_running "$started_pid"; then
  log "backend failed to start, see $LOG_FILE"
  exit 1
fi

log "backend started with pid $started_pid"
