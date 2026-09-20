#!/usr/bin/env bash
# Copy the agent module from the repo into the running bench and restart the
# workers, so a change to briefing.py takes effect without a full rebuild.
set -euo pipefail

SRC=/mnt/d/MSCAST/mscast_erp/mscast_erp/agents
DEST=/home/frappe/frappe-bench/apps/mscast_erp/mscast_erp/agents

for C in $(docker ps --format '{{.Names}}' | grep -E 'backend|worker|scheduler'); do
  if docker exec "$C" test -d "$DEST" 2>/dev/null; then
    docker cp "$SRC"/. "$C":"$DEST"/
    docker exec "$C" bash -c "find $DEST -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true"
    echo "  updated $C"
  fi
done
