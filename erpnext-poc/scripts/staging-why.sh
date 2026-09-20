#!/usr/bin/env bash
C=mscast-poc-backend-1
docker exec "$C" bash -c 'cd /home/frappe/frappe-bench/sites && ../env/bin/python -c "
import frappe, traceback
frappe.init(site=\"staging.localhost\"); frappe.connect(); frappe.set_user(\"Administrator\")
print(\"Module Defs for mscast_erp:\", frappe.get_all(\"Module Def\", filters={\"app_name\": \"mscast_erp\"}, pluck=\"name\"))
print(\"modules.txt says:\", open(\"/home/frappe/frappe-bench/apps/mscast_erp/mscast_erp/modules.txt\").read().strip())
try:
    print(\"get_module_list:\", frappe.get_module_list(\"mscast_erp\"))
except Exception as e:
    print(\"get_module_list failed:\", e)
p = \"/home/frappe/frappe-bench/apps/mscast_erp/mscast_erp/mscast/doctype/mscast_pcc/mscast_pcc.json\"
from frappe.modules.import_file import import_file_by_path
try:
    r = import_file_by_path(p, force=True, reset_permissions=True)
    print(\"import_file_by_path ->\", r)
except Exception:
    traceback.print_exc()
frappe.db.commit()
print(\"MSCAST PCC exists now:\", bool(frappe.db.exists(\"DocType\", \"MSCAST PCC\")))
" 2>&1 | grep -v RuntimeWarning | tail -30'
