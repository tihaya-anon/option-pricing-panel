#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

print_status() {
  local name="$1"
  local pid_file="$2"
  local url="$3"
  local pid

  pid="$(read_pid "$pid_file" || true)"

  if [[ -n "${pid:-}" ]] && pid_is_running "$pid"; then
    printf '%s: running (pid %s) %s\n' "$name" "$pid" "$url"
    return
  fi

  printf '%s: stopped\n' "$name"
}

print_status backend "$RUN_DIR/backend.pid" "http://127.0.0.1:8000"
print_status frontend "$RUN_DIR/frontend.pid" "http://127.0.0.1:5173"
