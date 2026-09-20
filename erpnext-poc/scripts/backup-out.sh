#!/usr/bin/env bash
# Copy a backup set out of the Docker volume onto D:, and prove it is readable.
#
# This matters more than it looks. `reset-poc.sh` runs `docker compose down -v`,
# which deletes the `sites` volume - and the backups live inside it. A backup
# that only exists in the volume you are about to destroy is not a backup.
set -euo pipefail
STAMP=${1:?usage: backup-out.sh YYYYMMDD_HHMMSS}
C=mscast-poc-backend-1
SRC=/home/frappe/frappe-bench/sites/frontend/private/backups
DEST=/mnt/d/MSCAST/backups/$STAMP

mkdir -p "$DEST"
for f in $(docker exec "$C" bash -c "ls $SRC | grep $STAMP"); do
  docker cp "$C:$SRC/$f" "$DEST/$f"
done

echo "=== copied out of the volume onto D: ==="
ls -la "$DEST"

echo
echo "=== integrity ==="
gzip -t "$DEST"/*database.sql.gz && echo "  gzip integrity OK"
zcat "$DEST"/*database.sql.gz | wc -c | awk '{printf "  uncompressed      %.1f MB\n", $1/1048576}'
zcat "$DEST"/*database.sql.gz | grep -c 'CREATE TABLE' | awk '{print "  CREATE TABLE      " $1}'
zcat "$DEST"/*database.sql.gz | grep -oE 'tabMSCAST [A-Za-z ]+' | sort -u | wc -l \
  | awk '{print "  MSCAST doctypes   " $1}'
for t in *files.tar; do :; done
for f in "$DEST"/*.tar; do
  tar -tf "$f" >/dev/null && echo "  tar OK            $(basename "$f")"
done
echo
echo "kept at: $DEST"
