#!/usr/bin/env bash
C=mscast-poc-backend-1
SITE=staging.localhost
B=/home/frappe/frappe-bench
LOG=/mnt/d/MSCAST/erpnext-poc/staging-build.log

run() { docker exec "$C" bash -c "cd $B && $1" 2>&1 | tail -"${2:-12}"; }

{
  echo
  echo "=============== refresh the app copy and register it with the bench ==============="
  docker exec "$C" rm -rf $B/apps/mscast_erp
  docker cp /mnt/d/MSCAST/mscast_erp/. "$C":$B/apps/mscast_erp
  docker exec "$C" bash -c "cd $B && ./env/bin/pip install -q -e apps/mscast_erp && echo pip-installed"
  docker exec "$C" bash -c "grep -qx mscast_erp $B/sites/apps.txt || echo mscast_erp >> $B/sites/apps.txt; cat $B/sites/apps.txt"

  echo
  echo "=============== install mscast_erp on the empty site ==============="
  run "bench --site $SITE install-app mscast_erp" 25

  echo
  echo "=============== build the app assets ==============="
  run "bench build --app mscast_erp" 8

  echo
  echo "=============== MSCAST INSTALL FINISHED ==============="
} >> "$LOG" 2>&1
