#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/start-backend-local.sh"
"$SCRIPT_DIR/start-frontend-local.sh"

printf 'backend:  http://127.0.0.1:8000\n'
printf 'frontend: http://127.0.0.1:5173\n'
