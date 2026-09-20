#!/usr/bin/env bash
C=mscast-poc-backend-1
B=/home/frappe/frappe-bench
LOG=/mnt/d/MSCAST/erpnext-poc/staging-build.log
{
  echo
  echo "=============== refresh app, migrate, row-by-row fixtures ==============="
  docker cp /mnt/d/MSCAST/mscast_erp/mscast_erp/install.py "$C":$B/apps/mscast_erp/mscast_erp/install.py
  docker exec "$C" bash -c "cd $B && bench --site staging.localhost migrate" 2>&1 \
    | grep -viE 'updating doctypes|\] +[0-9]+%' | tail -22
  echo "=============== REMIGRATE FINISHED ==============="
} >> "$LOG" 2>&1
