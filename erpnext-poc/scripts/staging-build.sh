#!/usr/bin/env bash
# Full clean-build proof, start to finish. Logs to staging-build.log.
# The staging site is throwaway: its admin password is random and never recorded.
C=mscast-poc-backend-1
SITE=staging.localhost
B=/home/frappe/frappe-bench
LOG=/mnt/d/MSCAST/erpnext-poc/staging-build.log
: > "$LOG"

run() { docker exec "$C" bash -c "cd $B && $1" 2>&1 | tail -"${2:-12}"; }

{
  echo "=============== drop any previous staging site ==============="
  run "bench drop-site $SITE --db-root-password admin --force --no-backup" 6
  docker exec "$C" rm -rf $B/sites/$SITE

  echo
  echo "=============== create an empty site ==============="
  PW=$(head -c 18 /dev/urandom | base64 | tr -dc 'a-zA-Z0-9' | head -c 18)
  run "bench new-site $SITE --db-root-password admin --admin-password '$PW' --no-mariadb-socket" 10
  unset PW

  for a in erpnext india_compliance hrms india_payroll mscast_erp; do
    echo
    echo "=============== install $a ==============="
    run "bench --site $SITE install-app $a" 14
  done

  echo
  echo "=============== installed apps ==============="
  run "bench --site $SITE list-apps" 12

  echo
  echo "=============== ALL DONE ==============="
} >> "$LOG" 2>&1
