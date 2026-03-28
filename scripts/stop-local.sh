#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

stop_process() {
  local name="$1"
  local pid_file="$2"

  local pid
  pid="$(read_pid "$pid_file" || true)"

  if [[ -z "${pid:-}" ]]; then
    log "$name is not running"
    return
  fi

  if pid_is_running "$pid"; then
    kill "$pid"
    log "stopped $name pid $pid"
  else
    log "$name pid file exists but process is not running"
  fi

  rm -f "$pid_file"
}

stop_process frontend "$RUN_DIR/frontend.pid"
stop_process backend "$RUN_DIR/backend.pid"
