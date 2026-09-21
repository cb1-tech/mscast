#!/usr/bin/env bash
# Test an upgrade on a completely separate stack, then tear it down.
#
# A copy of the live data is restored into its own compose project (its own
# database, volumes and network, frontend on :8090), onto the NEW image, and
# `bench migrate` is run - which is exactly what upgrading the live site would
# do. Then all the build checks run against the result. The live stack is never
# touched, and nothing on the test stack can send mail.
#
# usage: upgrade-test.sh <new app image> <backup dir> [--keep]
set -euo pipefail
NEW=${1:?usage: upgrade-test.sh <new app image> <backup dir> [--keep]}
BK=${2:?usage: upgrade-test.sh <new app image> <backup dir> [--keep]}
KEEP=${3:-}
P=mscast-upg; DIR=$HOME/mscast-upg; PORT=8090
OLD=$(grep -m1 -oE 'mscast/erpnext:[A-Za-z0-9._-]+' "$HOME/mscast-poc/compose.yaml")
C=$P-backend-1; BENCH=/home/frappe/frappe-bench
S=/mnt/d/MSCAST/erpnext-poc/scripts
b() { docker exec "$C" bash -c "cd $BENCH && $*"; }

echo "=== versions: live image $OLD -> candidate $NEW ==="
paste <(bash $S/app-versions.sh "$OLD") <(bash $S/app-versions.sh "$NEW" | awk '{print $2}') \
  | awk '{printf "  %-18s %-10s -> %s%s\n", $1, $2, $3, ($2!=$3 ? "   CHANGED" : "")}'

echo
echo "=== 1/6  separate stack '$P' on :$PORT ==="
mkdir -p "$DIR"
sed -e "s#$OLD#$NEW#g" -e "s#\"8080:8080\"#\"$PORT:8080\"#" "$HOME/mscast-poc/compose.yaml" > "$DIR/compose.yaml"
docker compose -p $P -f "$DIR/compose.yaml" up -d 2>&1 | grep -cE 'Started|Running' | sed 's/^/  containers up: /'
for i in $(seq 1 60); do
  s=$(docker inspect -f '{{.State.Status}}:{{.State.ExitCode}}' $P-create-site-1 2>/dev/null || echo none)
  case "$s" in exited:0) break;; exited:*) echo "site creation failed: $s" >&2; exit 1;; esac
  sleep 10
done
echo "  empty site created"

echo
echo "=== 2/6  restore the live backup into it, and mute it ==="
ROOTPW=$(grep -m1 -E '^\s*MYSQL_ROOT_PASSWORD:' "$DIR/compose.yaml" | sed -E 's/.*:[[:space:]]*//')
b "rm -rf restore && mkdir restore"
for f in "$BK"/*database.sql.gz "$BK"/*-files.tar; do docker cp "$f" "$C:$BENCH/restore/"; done
DB=$(basename "$BK"/*database.sql.gz); PUB=$(basename "$(ls "$BK"/*-files.tar | grep -v private)")
PRIV=$(basename "$BK"/*private-files.tar)
b "bench --site frontend --force restore restore/$DB --with-public-files restore/$PUB \
   --with-private-files restore/$PRIV --db-root-password '$ROOTPW'" 2>&1 | tail -2 | sed 's/^/  /'
C=$C bash $S/restore-key.sh "$BK" frontend
b "bench --site frontend set-config mute_emails 1 && bench --site frontend disable-scheduler \
   && bench set-config -g server_script_enabled true" >/dev/null
echo "  mail muted, scheduler disabled"

echo
echo "=== 3/6  THE UPGRADE: bench migrate on the new code ==="
b "bench --site frontend migrate" > "$DIR/migrate.log" 2>&1 && rc=0 || rc=$?
grep -iE 'mscast_erp|error|traceback|failed' "$DIR/migrate.log" | tail -12 | sed 's/^/  /'
echo "  migrate exit code: $rc   (full log: $DIR/migrate.log)"
[ $rc -eq 0 ] || { echo "UPGRADE FAILED at migrate" >&2; exit 1; }

echo
echo "=== 4/6  restart onto the migrated site ==="
docker compose -p $P -f "$DIR/compose.yaml" restart backend queue-short queue-long scheduler websocket frontend >/dev/null
sleep 15
printf '  :%s/login  %s\n' $PORT "$(curl -s -o /dev/null -w '%{http_code}' http://localhost:$PORT/login)"

echo
echo "=== 5/6  the build checks, against the upgraded copy ==="
C=$C SITE=frontend bash $S/run-harness.sh frontend | tee "$DIR/harness.txt" | grep -E '^\[T\] (T|RESULT)'
echo
echo "  demonstration watermark after migrate:"
b "cd sites && ../env/bin/python -c \"
import frappe; frappe.init(site='frontend'); frappe.connect()
pf = frappe.get_all('Print Format', {'standard': 'No', 'disabled': 0}, pluck='name')
n = sum(1 for p in pf if 'mscast-demo-watermark' in (frappe.db.get_value('Print Format', p, 'html') or ''))
print('    %d of %d enabled MSCAST print formats still carry it' % (n, len(pf)))\"" 2>/dev/null | grep -v Warning

echo
if [ "$KEEP" = "--keep" ]; then
  echo "=== 6/6  kept running on :$PORT - tear down with: docker compose -p $P -f $DIR/compose.yaml down -v"
else
  echo "=== 6/6  tear down the test stack ==="
  docker compose -p $P -f "$DIR/compose.yaml" down -v 2>&1 | tail -1 | sed 's/^/  /'
fi
