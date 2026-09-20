#!/usr/bin/env bash
# Take a restorable snapshot of the POC site before a risky operation.
# Usage: snapshot.sh <label>
set -euo pipefail
LABEL="${1:-manual}"
C=mscast-poc-backend-1
STAMP=$(date +%Y%m%d-%H%M%S)
OUT=/mnt/d/MSCAST/erpnext-poc/backups
mkdir -p "$OUT"

echo "taking backup (database + files)..."
docker exec $C bench --site frontend backup --with-files 2>&1 | tail -6

echo
echo "copying out of the container..."
docker exec $C bash -lc 'ls -1t /home/frappe/frappe-bench/sites/frontend/private/backups/*.sql.gz | head -1' \
  | tr -d '\r' | while read -r f; do
      docker cp "$C:$f" "$OUT/${STAMP}-${LABEL}.sql.gz"
    done

ls -la --time-style=+%Y-%m-%d\ %H:%M "$OUT"
echo
echo "restore with:  scripts/restore.sh $OUT/${STAMP}-${LABEL}.sql.gz"
