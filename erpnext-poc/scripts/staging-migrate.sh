#!/usr/bin/env bash
C=mscast-poc-backend-1
SITE=staging.localhost
B=/home/frappe/frappe-bench
LOG=/mnt/d/MSCAST/erpnext-poc/staging-build.log
{
  echo
  echo "=============== migrate again - fixtures that were skipped ==============="
  docker exec "$C" bash -c "cd $B && bench --site $SITE migrate" 2>&1 | grep -viE 'updating doctypes|\] +[0-9]+%' | tail -14
  echo "=============== MIGRATE 2 FINISHED ==============="
} >> "$LOG" 2>&1
