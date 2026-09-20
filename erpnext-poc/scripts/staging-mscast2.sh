#!/usr/bin/env bash
C=mscast-poc-backend-1
SITE=staging.localhost
B=/home/frappe/frappe-bench
LOG=/mnt/d/MSCAST/erpnext-poc/staging-build.log
run() { docker exec "$C" bash -c "cd $B && $1" 2>&1 | tail -"${2:-10}"; }
{
  echo
  echo "=============== migrate, then sync fixtures again ==============="
  run "bench --site $SITE migrate" 12
  echo "--- second pass at the app ---"
  run "bench --site $SITE install-app mscast_erp" 12
  echo "--- migrate again ---"
  run "bench --site $SITE migrate" 8
  echo
  echo "=============== PASS TWO FINISHED ==============="
} >> "$LOG" 2>&1
