#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/mscast-poc"
cp -f frappe_docker/pwd.yml compose.yaml
nohup docker compose -p mscast-poc -f compose.yaml up -d > up.log 2>&1 &
disown
sleep 2
echo "launched; log at $HOME/mscast-poc/up.log"
