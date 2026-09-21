#!/usr/bin/env bash
# Nightly: back up the live site, copy the set OUT of the Docker volume onto D:,
# prove it is readable, prune old sets. Scheduled by Windows Task Scheduler
# (task "MSCAST nightly backup") - see the POC README.
#
# Why off the volume: `docker compose down -v` - which reset-poc.sh runs - deletes
# the `sites` volume, and Frappe keeps its backups inside it.
#
# What this does NOT protect against: losing this PC. D: is the same machine.
# For production, Companies (Accounts) Rules r.3(5) requires a daily backup on
# servers physically in India, so the real deployment needs an India-hosted
# off-site copy. This is the POC's safety net, not that.
#
# Retention: the 14 newest sets, plus the first set of each month for a year.
set -uo pipefail
SITE=${SITE:-frontend}
C=mscast-poc-backend-1
ROOT=/mnt/d/MSCAST/backups
LOG=$ROOT/backup.log
SCRIPTS=/mnt/d/MSCAST/erpnext-poc/scripts
mkdir -p "$ROOT"
say() { echo "$(date '+%F %T') $*" | tee -a "$LOG"; }

if ! docker ps --format '{{.Names}}' | grep -qx "$C"; then
  say "FAIL stack not running - no backup taken"; exit 1
fi

# Refuse to bless a backup the site cannot itself read. On 21 Sep 2026 a set was
# taken while the site's encryption_key did not match its data; it verified as a
# perfectly good archive and would have restored a site with an unreadable mail
# password. An archive can be intact and still wrong.
cat > /tmp/_decrypt_check.py <<'PY2'
import frappe
from frappe.utils.password import get_decrypted_password
bad = 0
for r in frappe.db.sql("select doctype, name, fieldname from `__Auth` where encrypted=1", as_dict=True):
    try: get_decrypted_password(r.doctype, r.name, r.fieldname, raise_exception=True)
    except Exception: bad += 1
print("UNDECRYPTABLE=%d" % bad)
PY2
docker cp /tmp/_decrypt_check.py "$C":/tmp/_decrypt_check.py >/dev/null
bad=$(docker exec "$C" bash -c "cd /home/frappe/frappe-bench/sites && ../env/bin/python -c \"
import frappe; frappe.init(site='$SITE'); frappe.connect()
exec(open('/tmp/_decrypt_check.py').read())\"" 2>/dev/null | grep -oE 'UNDECRYPTABLE=[0-9]+' | cut -d= -f2)
if [ "${bad:-x}" != "0" ]; then
  say "FAIL site cannot decrypt ${bad:-?} of its own secrets - encryption_key mismatch; backup NOT taken. See restore-key.sh"
  exit 1
fi

out=$(docker exec "$C" bash -c "cd /home/frappe/frappe-bench && bench --site $SITE backup --with-files" 2>&1)
stamp=$(echo "$out" | grep -oE '[0-9]{8}_[0-9]{6}' | head -1)
[ -n "$stamp" ] || { say "FAIL bench backup produced no set: $(echo "$out" | tail -2)"; exit 1; }

if ! bash "$SCRIPTS/backup-out.sh" "$stamp" > "$ROOT/.last-verify.txt" 2>&1; then
  say "FAIL $stamp copied but did not verify - see $ROOT/.last-verify.txt"; exit 1
fi
size=$(du -sh "$ROOT/$stamp" | cut -f1)
say "OK   $stamp  $size  verified (gzip + tar)"

# Prune on D: - only directories that look like backup sets.
mapfile -t sets < <(ls -1 "$ROOT" | grep -E '^[0-9]{8}_[0-9]{6}$' | sort -r)
keep_month=""
cutoff=$(date -d '365 days ago' +%Y%m%d)
for i in "${!sets[@]}"; do
  s=${sets[$i]}; day=${s:0:8}; month=${s:0:6}
  if [ "$i" -lt 14 ]; then continue; fi
  # oldest set of each month is kept for a year (sets are sorted newest-first,
  # so remember the month and keep the last one we see for it)
  if [ "$day" -ge "$cutoff" ] && ! ls -1 "$ROOT" | grep -E "^${month}" | sort | head -1 | grep -qx "$s"; then
    rm -rf "${ROOT:?}/$s" && say "     pruned $s"
  elif [ "$day" -lt "$cutoff" ]; then
    rm -rf "${ROOT:?}/$s" && say "     pruned $s (older than a year)"
  fi
done

# Inside the volume, keep only the newest 3 sets - the copies on D: are the record.
docker exec "$C" bash -c "cd /home/frappe/frappe-bench/sites/$SITE/private/backups && \
  ls -1 | grep -oE '^[0-9]{8}_[0-9]{6}' | sort -u -r | tail -n +4 | \
  while read s; do rm -f \${s}-*; done" 2>/dev/null
exit 0
