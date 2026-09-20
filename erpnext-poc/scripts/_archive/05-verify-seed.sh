#!/usr/bin/env bash
echo "--- host file ---"
grep -c "ensure_project" /mnt/d/MSCAST/erpnext-poc/seed/03_transactions.py
md5sum /mnt/d/MSCAST/erpnext-poc/seed/03_transactions.py
echo "--- container file ---"
docker exec mscast-poc-backend-1 bash -c "grep -c ensure_project /home/frappe/frappe-bench/seed/03_transactions.py; md5sum /home/frappe/frappe-bench/seed/03_transactions.py"
