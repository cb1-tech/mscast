#!/usr/bin/env bash
# Build the DEV instance (mscastdev.carobar.net) as a SEPARATE compose project.
# Own database, Redis, workers and volumes; the live project 'mscast-poc' is
# never touched. Same image as live, so dev always matches the live code.
#
# usage: dev-create.sh [backup dir]      (first-time build; refuses if dev exists)
set -euo pipefail
SEED=${1:-/mnt/d/MSCAST/backups-dev-seed/20260921_125913}
P=mscast-dev
C=$P-backend-1
DIR=$HOME/$P
BENCH=/home/frappe/frappe-bench
say(){ echo "[$(date +%H:%M:%S)] $*"; }

docker ps -a --format '{{.Names}}' | grep -q "^$C$" && { echo "dev already exists - use start-dev.sh"; exit 1; }

say "1/7 compose file (live compose, port 8081)"
mkdir -p "$DIR"
sed 's/"8080:8080"/"8081:8080"/' "$HOME/mscast-poc/compose.yaml" > "$DIR/compose.yaml"
grep -q '"8081:8080"' "$DIR/compose.yaml" || { echo "port rewrite failed"; exit 1; }

say "2/7 start the stack (creates an empty site 'frontend')"
docker compose -p $P -f "$DIR/compose.yaml" up -d 2>&1 | tail -3
docker wait $P-create-site-1 >/dev/null
docker logs --tail 3 $P-create-site-1

say "3/7 restore $(basename "$SEED")"
DB=$(ls "$SEED"/*database.sql.gz); PUB=$(ls "$SEED"/*-files.tar | grep -v private); PRIV=$(ls "$SEED"/*private-files.tar)
docker exec $C bash -c "rm -rf $BENCH/restore && mkdir -p $BENCH/restore"
for f in "$DB" "$PUB" "$PRIV"; do docker cp "$f" "$C:$BENCH/restore/$(basename "$f")"; done
docker exec $C bash -c "cd $BENCH && bench --site frontend --force restore restore/$(basename "$DB") \
  --with-public-files restore/$(basename "$PUB") --with-private-files restore/$(basename "$PRIV") \
  --db-root-password admin" 2>&1 | tail -4

say "4/7 encryption key + mscast_* settings from the backup"
C=$C bash /mnt/d/MSCAST/erpnext-poc/scripts/restore-key.sh "$SEED" frontend

say "5/7 host_name, server scripts, migrate"
# Bench-wide (common_site_config), so a restore does NOT carry it. Without it every
# MSCAST server script (home page, BRM rules, morning batch) is silently off.
docker exec $C bash -c "cd $BENCH && bench set-config -g server_script_enabled true"
docker exec $C bash -c "cd $BENCH && bench --site frontend set-config host_name https://mscastdev.carobar.net"
docker exec $C bash -c "cd $BENCH && bench --site frontend migrate" 2>&1 | grep -v -E 'Updating DocTypes|\] +[0-9]+%' | tail -12

say "6/7 DEV marker + scheduler on + no backup alerts"
# Dev is not backed up (it is rebuilt from its seed), so the 09:00 watchdog would
# email "backup overdue" daily and look like a live problem. The watchdog sends
# nothing when mscast_alerts_to is unset - by design, for scratch copies.
docker exec $C bash -c "cd $BENCH/sites && python3 -c \"
import json; p='frontend/site_config.json'; c=json.load(open(p))
for k in ('mscast_alerts_to', 'mscast_last_backup', 'mscast_last_checks'): c.pop(k, None)
c['mscast_dev_copy'] = 1
json.dump(c, open(p, 'w'), indent=1)\""
docker exec $C bash -c "cd $BENCH && bench --site frontend enable-scheduler"
C=$C TAIL=40 bash /mnt/d/MSCAST/erpnext-poc/scripts/run-seed.sh 193_dev_marker
docker restart $P-backend-1 $P-frontend-1 $P-websocket-1 >/dev/null

say "7/7 verify"
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8081/api/method/ping || true)
  [ "$code" = "200" ] && break; sleep 5
done
echo "  dev ping      $code"
echo "  live ping     $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/api/method/ping)"
say "DEV BUILD DONE"
