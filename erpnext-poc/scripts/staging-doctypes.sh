#!/usr/bin/env bash
C=mscast-poc-backend-1
docker exec "$C" bash -c 'cd /home/frappe/frappe-bench/sites && ../env/bin/python -c "
import frappe, os, json
frappe.init(site=\"staging.localhost\"); frappe.connect()
base = \"/home/frappe/frappe-bench/apps/mscast_erp/mscast_erp/mscast/doctype\"
missing = []
for folder in sorted(os.listdir(base)):
    p = os.path.join(base, folder, folder + \".json\")
    if not os.path.isfile(p):
        continue
    name = json.load(open(p))[\"name\"]
    exists = frappe.db.exists(\"DocType\", name)
    table = frappe.db.table_exists(name) if exists else False
    if not exists or not table:
        missing.append((name, bool(exists), bool(table)))
print(\"doctype folders:\", len([f for f in os.listdir(base) if os.path.isdir(os.path.join(base,f))]))
print(\"missing or table-less:\", len(missing))
for m in missing:
    print(\"   \", m[0], \"| doctype row:\", m[1], \"| table:\", m[2])
print()
print(\"on site, module MSCAST:\", frappe.db.count(\"DocType\", {\"module\": \"MSCAST\"}))
" 2>&1 | grep -v RuntimeWarning'
