#!/usr/bin/env bash

set -euo pipefail

source "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/common.sh"

compose_cmd="$(docker_compose_cmd)"

cd "$ROOT_DIR"
$compose_cmd down
