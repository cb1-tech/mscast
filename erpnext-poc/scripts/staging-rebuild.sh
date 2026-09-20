#!/usr/bin/env bash
# Full clean build from scratch, with the custom documents as app doctypes.
C=mscast-poc-backend-1
SITE=staging.localhost
B=/home/frappe/frappe-bench
LOG=/mnt/d/MSCAST/erpnext-poc/staging-build.log
: > "$LOG"
run() { docker exec "$C" bash -c "cd $B && $1" 2>&1 | tail -"${2:-10}"; }
{
  echo "=============== refresh the app ==============="
  docker exec "$C" rm -rf $B/apps/mscast_erp
  docker cp /mnt/d/MSCAST/mscast_erp/. "$C":$B/apps/mscast_erp
  docker exec "$C" bash -c "cd $B && ./env/bin/pip install -q -e apps/mscast_erp && echo pip-installed"
  docker exec "$C" bash -c "grep -qx mscast_erp $B/sites/apps.txt || echo mscast_erp >> $B/sites/apps.txt"

  echo
  echo "=============== drop and recreate an empty site ==============="
  run "bench drop-site $SITE --db-root-password admin --force --no-backup" 4
  docker exec "$C" rm -rf $B/sites/$SITE
  PW=$(head -c 18 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 18)
  run "bench new-site $SITE --db-root-password admin --admin-password '$PW' --mariadb-user-host-login-scope='%'" 6
  unset PW

  for a in erpnext india_compliance hrms india_payroll mscast_erp; do
    echo
    echo "=============== install $a ==============="
    run "bench --site $SITE install-app $a" 14
  done

  echo
  echo "=============== migrate ==============="
  run "bench --site $SITE migrate" 10

  echo
  echo "=============== installed apps ==============="
  run "bench --site $SITE list-apps" 10
  echo "=============== REBUILD FINISHED ==============="
} >> "$LOG" 2>&1
