#!/usr/bin/env bash
# The nightly safety net. Windows task "MSCAST nightly backup", 02:30 JST.
#
#   1. backup-nightly.sh - back up, copy off the volume, verify, prune
#   2. the build checks, against the live site
#   3. record both outcomes in site config, where the in-site watchdog
#      (mscast_erp.controls.watchdog, 09:00 IST) reads them
#   4. email mscast_alerts_to if either failed
#
# Before this, a failed backup wrote a line to a log nobody reads.
# SIMULATE_FAIL=1 forces an alert, to prove the path end to end.
set -uo pipefail
S=/mnt/d/MSCAST/erpnext-poc/scripts; C=mscast-poc-backend-1; SITE=${SITE:-frontend}
B=/home/frappe/frappe-bench; T=$(mktemp -d)
# Record a value in site config. Parsed as real JSON inside the container:
# `bench set-config --parse` uses Python syntax, so JSON's `true` made it fail -
# and with its output sent to /dev/null the backup record silently never landed
# (found on the first run, 21 Sep 2026: T9h reported no backup ever recorded).
# Errors are shown now, and a failure to record is itself reported.
setcfg() {  # key, json value
  printf '%s' "$2" > "$T/v.json"; docker cp "$T/v.json" "$C:/tmp/cfg-$1.json" >/dev/null
  docker exec "$C" bash -c "cd $B/sites && ../env/bin/python -c \"
import json, frappe
from frappe.installer import update_site_config
frappe.init(site='$SITE')
update_site_config('$1', json.load(open('/tmp/cfg-$1.json')))
\"" 2>&1 | grep -vE 'RuntimeWarning|sys.prefix|sys.exec_prefix|frozen site' || true
  docker exec "$C" grep -q "\"$1\"" "$B/sites/$SITE/site_config.json" \
    || echo "WARNING: could not record $1 in site config" | tee -a /mnt/d/MSCAST/backups/backup.log
}

bash $S/backup-nightly.sh > "$T/backup.txt" 2>&1; bk=$?
bline=$(tail -1 /mnt/d/MSCAST/backups/backup.log 2>/dev/null)
stamp=$(echo "$bline" | grep -oE '[0-9]{8}_[0-9]{6}' | head -1)
okjson=$([ $bk -eq 0 ] && echo true || echo false)
setcfg mscast_last_backup "{\"at\": $(date +%s), \"set\": \"${stamp:-none}\", \"ok\": $okjson, \"detail\": \"$(echo "$bline" | tr -d '"\\' | cut -c1-200)\"}"

bash $S/run-harness.sh "$SITE" > "$T/checks.txt" 2>&1
res=$(grep -E '^\[T\] RESULT' "$T/checks.txt" | tail -1)
p=$(echo "$res" | grep -oE '[0-9]+ PASS' | cut -d' ' -f1); w=$(echo "$res" | grep -oE '[0-9]+ WARN' | cut -d' ' -f1)
f=$(echo "$res" | grep -oE '[0-9]+ FAIL' | cut -d' ' -f1)
[ -n "$res" ] || f=1   # no result line at all is itself a failure
fails=$(grep -E '^\[T\] +FAIL ' "$T/checks.txt" | sed -E 's/^\[T\] +FAIL +//' | cut -c1-120 | tr -d '"\\' | paste -sd ';' -)
setcfg mscast_last_checks "{\"at\": $(date +%s), \"pass\": ${p:-0}, \"warn\": ${w:-0}, \"fail\": ${f:-0}, \"detail\": \"${fails:-}\"}"

if [ $bk -ne 0 ] || [ "${f:-0}" != "0" ] || [ -n "${SIMULATE_FAIL:-}" ]; then
  {
    [ -n "${SIMULATE_FAIL:-}" ] && echo "*** TEST ALERT - SIMULATE_FAIL was set. Nothing is actually wrong. ***" && echo
    echo "Nightly run on $(hostname), $(date '+%F %T %Z')"; echo
    echo "BACKUP: $([ $bk -eq 0 ] && echo OK || echo FAILED)"; echo "  $bline"; echo
    echo "BUILD CHECKS: ${res:-no result - the harness did not complete}"
    grep -E '^\[T\] +(FAIL|T[0-9a-z]+ +FAIL)' "$T/checks.txt" | sed 's/^/  /'
    echo; echo "What to do: bash /mnt/d/MSCAST/erpnext-poc/scripts/status.sh"
  } > "$T/alert.txt"
  docker cp "$T/alert.txt" "$C:/tmp/alert.txt" >/dev/null
  subj=$([ -n "${SIMULATE_FAIL:-}" ] && echo "TEST alert - nightly safety net" || echo "Nightly backup or build checks FAILED")
  docker exec "$C" bash -c "cd $B && bench --site $SITE execute mscast_erp.controls.watchdog.alert_from_file --kwargs \"{'subject': '$subj', 'path': '/tmp/alert.txt'}\"" 2>&1 | tail -2
fi
echo "$(date '+%F %T') nightly: backup rc=$bk, checks ${res#\[T\] }" | tee -a /mnt/d/MSCAST/backups/backup.log
rm -rf "$T"
