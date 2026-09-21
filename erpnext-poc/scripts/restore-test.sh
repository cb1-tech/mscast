#!/usr/bin/env bash
# Prove a backup actually restores, by restoring it into a SEPARATE site and
# counting what came back. The live site is never touched.
#
# "We take backups" is a claim about the past. "We restored one" is a claim
# about the future, and it is the only one that matters. Companies (Accounts)
# Rules r.3(5) requires the books to be kept in India and recoverable; an
# untested backup does not satisfy that in any meaningful sense.
#
# usage: restore-test.sh /mnt/d/MSCAST/backups/<stamp>  [testsite]
set -euo pipefail
DIR=${1:?usage: restore-test.sh <backup dir> [site]}
SITE=${2:-restoretest}
C=mscast-poc-backend-1
BENCH=/home/frappe/frappe-bench

DB=$(ls "$DIR"/*database.sql.gz)
PUB=$(ls "$DIR"/*-files.tar | grep -v private || true)
PRIV=$(ls "$DIR"/*private-files.tar || true)
# The db root password is not in common_site_config.json - it is only in the
# compose file, as MYSQL_ROOT_PASSWORD on the db service. Read it from there
# rather than guessing, so this keeps working if it is ever changed.
ROOTPW=${DB_ROOT_PASSWORD:-$(grep -m1 -E '^\s*MYSQL_ROOT_PASSWORD:' "$HOME/mscast-poc/compose.yaml" \
                            | sed -E 's/.*:[[:space:]]*//' | tr -d '"'"'"'\r')}
[ -n "$ROOTPW" ] || { echo "could not determine the db root password" >&2; exit 1; }
echo "restoring $(basename "$DB") into site '$SITE'"

docker exec "$C" bash -c "rm -rf $BENCH/restore && mkdir -p $BENCH/restore"
for f in "$DB" "$PUB" "$PRIV"; do
  [ -n "$f" ] && docker cp "$f" "$C:$BENCH/restore/$(basename "$f")"
done

echo "=== 1/3  create the empty site ==="
# --force so a previous half-finished attempt does not block the test, and
# --mariadb-user-host-login-scope='%' because the bench and the db are separate
# containers (the old --no-mariadb-socket spelling is deprecated).
docker exec "$C" bash -c "cd $BENCH && bench new-site $SITE --force \
  --db-root-password '$ROOTPW' --admin-password restoretest \
  --mariadb-user-host-login-scope='%'" 2>&1 | tail -4

echo
echo "=== 2/3  restore into it ==="
docker exec "$C" bash -c "cd $BENCH && bench --site $SITE --force restore \
  restore/$(basename "$DB") \
  ${PUB:+--with-public-files restore/$(basename "$PUB")} \
  ${PRIV:+--with-private-files restore/$(basename "$PRIV")} \
  --db-root-password '$ROOTPW'" 2>&1 | tail -8

echo
bash /mnt/d/MSCAST/erpnext-poc/scripts/restore-key.sh "$DIR" "$SITE"
# A restored copy carries the live mail account and an enabled scheduler, so
# left alone it sends the morning report and the digest to real people. Mute it.
docker exec "$C" bash -c "cd $BENCH && bench --site $SITE set-config mute_emails 1 \
  && bench --site $SITE disable-scheduler" >/dev/null
echo "  mail muted, scheduler disabled on the test copy"

echo
echo "=== 3/3  count what actually came back ==="
docker exec "$C" bash -c "cd $BENCH/sites && ../env/bin/python -c \"
import frappe
frappe.init(site='$SITE'); frappe.connect()
def n(dt, f=None): 
    try: return frappe.db.count(dt, f or {})
    except Exception as e: return 'ERR ' + str(e)[:40]
rows = [
 ('apps installed',    ', '.join(frappe.get_installed_apps())),
 ('GL entries',        n('GL Entry', {'is_cancelled': 0})),
 ('sales invoices',    n('Sales Invoice', {'docstatus': 1})),
 ('purchase invoices', n('Purchase Invoice', {'docstatus': 1})),
 ('MSCAST BRMs',       n('MSCAST BRM')),
 ('custom reports',    n('Report', {'is_standard': 'No'})),
 ('print formats',     n('Print Format', {'standard': 'No'})),
 ('workflows',         n('Workflow')),
 ('users',             n('User', {'enabled': 1})),
 ('employees',         n('Employee')),
 ('salary slips',      n('Salary Slip', {'docstatus': 1})),
]
for k, v in rows: print('  %-20s %s' % (k, v))
from frappe.utils import flt
d = flt(frappe.db.sql('select sum(debit)-sum(credit) from \\\`tabGL Entry\\\` where is_cancelled=0')[0][0])
print('  %-20s %s' % ('trial balance', d))
print('  %-20s %s' % ('VERDICT', 'RESTORE OK' if d == 0 else 'TRIAL BALANCE DOES NOT NET - INVESTIGATE'))
\"" 2>&1 | grep -v RuntimeWarning
