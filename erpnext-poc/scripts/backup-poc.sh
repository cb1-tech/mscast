#!/usr/bin/env bash
set -euo pipefail
OUT=/mnt/d/MSCAST/erpnext-poc/backups
mkdir -p "$OUT"
docker exec mscast-poc-backend-1 bash -c "cd /home/frappe/frappe-bench && bench --site frontend backup --with-files" 
docker cp mscast-poc-backend-1:/home/frappe/frappe-bench/sites/frontend/private/backups "$OUT/$(date +%Y%m%d-%H%M%S)"
echo "backup copied to $OUT"
