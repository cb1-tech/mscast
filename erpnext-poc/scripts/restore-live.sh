#!/usr/bin/env bash
# Restore a backup OVER the live site. Destructive and deliberate.
#
# Unlike restore-test.sh this does not create a site - it restores into the one
# that is there, so the Administrator password and site config are whatever the
# backup carried, not a test value.
#
# usage: restore-live.sh /mnt/d/MSCAST/backups/<stamp> [site]
set -euo pipefail
DIR=${1:?usage: restore-live.sh <backup dir> [site]}
SITE=${2:-frontend}
C=mscast-poc-backend-1
BENCH=/home/frappe/frappe-bench

DB=$(ls "$DIR"/*database.sql.gz)
PUB=$(ls "$DIR"/*-files.tar | grep -v private || true)
PRIV=$(ls "$DIR"/*private-files.tar || true)
ROOTPW=${DB_ROOT_PASSWORD:-$(grep -m1 -E '^\s*MYSQL_ROOT_PASSWORD:' "$HOME/mscast-poc/compose.yaml" \
                            | sed -E 's/.*:[[:space:]]*//' | tr -d '"'"'"'\r')}

echo "restoring $(basename "$DB") OVER site '$SITE'"
docker exec "$C" bash -c "rm -rf $BENCH/restore && mkdir -p $BENCH/restore"
for f in "$DB" "$PUB" "$PRIV"; do
  [ -n "$f" ] && docker cp "$f" "$C:$BENCH/restore/$(basename "$f")"
done

docker exec "$C" bash -c "cd $BENCH && bench --site $SITE --force restore \
  restore/$(basename "$DB") \
  ${PUB:+--with-public-files restore/$(basename "$PUB")} \
  ${PRIV:+--with-private-files restore/$(basename "$PRIV")} \
  --db-root-password '$ROOTPW'" 2>&1 | tail -8

echo
# Without this every stored secret in the restored data is undecryptable.
bash /mnt/d/MSCAST/erpnext-poc/scripts/restore-key.sh "$DIR" "$SITE"

echo
echo "restarting so nothing serves stale state..."
cd "$HOME/mscast-poc"
docker compose restart backend queue-short queue-long scheduler websocket >/dev/null
docker compose restart frontend >/dev/null
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://localhost:8080/login || echo 000)
  [ "$code" = "200" ] && { echo "  site answering (HTTP 200 after $i attempt(s))"; exit 0; }
  sleep 5
done
echo "  SITE DID NOT COME BACK (last HTTP $code)" >&2; exit 1
