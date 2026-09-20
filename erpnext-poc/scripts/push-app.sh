#!/usr/bin/env bash
# Copy the whole app from the repo into the running bench and clear bytecode,
# so a code change takes effect without a rebuild.
set -euo pipefail
SRC=/mnt/d/MSCAST/mscast_erp/mscast_erp
DEST=/home/frappe/frappe-bench/apps/mscast_erp/mscast_erp
for C in $(docker ps --format '{{.Names}}' | grep -E 'backend|worker|scheduler'); do
  if docker exec "$C" test -d "$DEST" 2>/dev/null; then
    docker cp "$SRC"/. "$C":"$DEST"/
    docker exec "$C" bash -c "find $DEST -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true"
    echo "  updated $C"
  fi
done
docker exec mscast-poc-backend-1 bench --site frontend clear-cache >/dev/null 2>&1 || true
echo "  cache cleared"
