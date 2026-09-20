#!/usr/bin/env bash
C=mscast-poc-backend-1
docker exec "$C" bash -c 'cd /home/frappe/frappe-bench/sites && ../env/bin/python -c "
import frappe, traceback
frappe.init(site=\"staging.localhost\"); frappe.connect(); frappe.set_user(\"Administrator\")
dt = \"MSCAST PCC\"
print(\"table before:\", frappe.db.table_exists(\"tab\" + dt))
frappe.clear_cache()
try:
    from frappe.model.sync import sync_for
    sync_for(\"mscast_erp\", force=True, reset_permissions=True)
    frappe.db.commit()
    print(\"sync_for ok -> table:\", frappe.db.table_exists(\"tab\" + dt))
except Exception:
    traceback.print_exc()
try:
    from frappe.database.schema import DBTable
    meta = frappe.get_meta(dt)
    print(\"meta fields:\", len(meta.fields), \"issingle:\", meta.issingle, \"is_virtual:\", getattr(meta, \"is_virtual\", None), \"istable:\", meta.istable)
except Exception:
    traceback.print_exc()
print(\"tables with MSCAST:\", frappe.db.sql(\"show tables like '%MSCAST%'\"))
" 2>&1 | grep -v RuntimeWarning | tail -12'
