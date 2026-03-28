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
    local pgid
    pgid="$(process_group_id "$pid" || true)"

    if [[ -n "${pgid:-}" ]]; then
      kill -"${pgid}" 2>/dev/null || true
      sleep 1

      if kill -0 -"${pgid}" 2>/dev/null; then
        kill -TERM -"${pgid}" 2>/dev/null || true
        sleep 1
      fi

      if kill -0 -"${pgid}" 2>/dev/null; then
        kill -KILL -"${pgid}" 2>/dev/null || true
      fi

      log "stopped $name process group $pgid"
    else
      kill "$pid"
      log "stopped $name pid $pid"
    fi
  else
    log "$name pid file exists but process is not running"
  fi

  rm -f "$pid_file"
}

stop_process frontend "$RUN_DIR/frontend.pid"
stop_process backend "$RUN_DIR/backend.pid"
