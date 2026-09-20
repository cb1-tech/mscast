#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/mscast-poc"
docker compose -p mscast-poc -f compose.yaml stop
echo "stopped (data volumes kept)"
