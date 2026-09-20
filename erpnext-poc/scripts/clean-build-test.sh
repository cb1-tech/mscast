#!/usr/bin/env bash
# Prove that an empty ERPNext site plus the mscast_erp app reproduces the system.
# The staging site is dropped at the end - it exists only for this test.
set -uo pipefail
C=mscast-poc-backend-1
SITE=staging.localhost
BENCH=/home/frappe/frappe-bench

step() { echo; echo "=============== $* ==============="; }

case "${1:-}" in

copy)
  step "copy the app into the bench"
  docker exec "$C" rm -rf $BENCH/apps/mscast_erp
  docker cp /mnt/d/MSCAST/mscast_erp/. "$C":$BENCH/apps/mscast_erp
  docker exec "$C" bash -c "cd $BENCH && ./env/bin/pip install -q -e apps/mscast_erp && echo installed"
  docker exec "$C" bash -c "ls $BENCH/apps/mscast_erp/mscast_erp/fixtures | head -20"
  ;;

newsite)
  step "create an empty site with ERPNext"
  docker exec "$C" bash -c "cd $BENCH && bench new-site $SITE \
      --db-root-password admin \
      --admin-password '$2' \
      --install-app erpnext \
      --no-mariadb-socket 2>&1 | tail -20"
  ;;

apps)
  step "install the other three apps"
  for a in india_compliance hrms india_payroll; do
    echo "--- $a ---"
    docker exec "$C" bash -c "cd $BENCH && bench --site $SITE install-app $a 2>&1 | tail -4"
  done
  ;;

mscast)
  step "install mscast_erp - this is the test"
  docker exec "$C" bash -c "cd $BENCH && bench --site $SITE install-app mscast_erp 2>&1 | tail -40"
  ;;

verify)
  step "what landed on the empty site"
  docker exec "$C" bash -c "cd $BENCH/sites && ../env/bin/python -c \"
import frappe
frappe.init(site='$SITE'); frappe.connect()
def n(dt, f=None):
    try: return frappe.db.count(dt, f or {})
    except Exception as e: return 'ERR'
print('custom doctypes      ', n('DocType', {'custom': 1}))
print('custom fields        ', n('Custom Field'))
print('property setters     ', n('Property Setter'))
print('custom reports       ', n('Report', {'is_standard': 'No'}))
print('print formats        ', n('Print Format', {'standard': 'No'}))
print('workflows            ', n('Workflow'))
print('server scripts       ', n('Server Script'))
print('notifications        ', n('Notification', {'is_standard': 0}))
print('custom html blocks   ', n('Custom HTML Block'))
print('MSCAST workspaces    ', n('Workspace', {'name': ('like', 'MSCAST%')}))
print('MSCAST roles         ', n('Role', {'name': ('like', 'MSCAST%')}))
print()
print('business data that should NOT be here:')
for dt in ['Sales Order','Purchase Order','Project','MSCAST PCC','Customer','Item','Employee']:
    print('   ', dt, n(dt))
print()
hidden = frappe.db.count('Workspace', {'public':1,'is_hidden':1})
print('hidden stock workspaces', hidden)
print('landing redirect       ', [ (r.source, r.target) for r in frappe.get_doc('Website Settings').get('route_redirects') or [] ])
\" 2>&1 | grep -v RuntimeWarning"
  ;;

drop)
  step "drop the staging site"
  docker exec "$C" bash -c "cd $BENCH && bench drop-site $SITE --db-root-password admin --force 2>&1 | tail -5"
  docker exec "$C" bash -c "ls $BENCH/sites"
  ;;

esac
