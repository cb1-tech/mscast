#!/usr/bin/env bash
# Copy seed scripts into the ERPNext backend container and run them in order.
# usage: run-seed.sh 01_company_masters 02_custom_doctypes ...
set -uo pipefail
C=mscast-poc-backend-1
SRC=/mnt/d/MSCAST/erpnext-poc/seed
# The site is overridable so the harness can be pointed at a restored or a
# scratch site. It defaults to the live one, which is what every existing
# caller expects.
SITE=${SITE:-frontend}

docker exec "$C" bash -c "rm -rf /home/frappe/frappe-bench/seed && mkdir -p /home/frappe/frappe-bench/seed"
docker cp "$SRC/." "$C":/home/frappe/frappe-bench/seed >/dev/null
echo "seed scripts copied"

for f in "$@"; do
  echo "=================== $f ==================="
  docker exec "$C" bash -c "cd /home/frappe/frappe-bench/sites && ../env/bin/python -c \"
import frappe
frappe.init(site='$SITE')
frappe.connect()
frappe.set_user('Administrator')
exec(open('../seed/$f.py').read())
frappe.db.commit()
\"" 2>&1 | tr -d '\r' | grep -v -E 'Updating DocTypes|\] +[0-9]+%' | tail -60
done
echo "ALL DONE"
