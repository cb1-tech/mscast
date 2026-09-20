#!/usr/bin/env bash
C=mscast-poc-backend-1
docker exec "$C" bash -c 'cd /home/frappe/frappe-bench/sites && ../env/bin/python -c "
import frappe
frappe.init(site=\"staging.localhost\"); frappe.connect()
rows = frappe.db.sql(\"show tables like %s\", (\"tabMSCAST%%\",))
print(\"MSCAST tables on the empty site:\", len(rows))
missing = []
for d in frappe.get_all(\"DocType\", filters={\"module\": \"MSCAST\"}, pluck=\"name\"):
    if not frappe.db.table_exists(d):
        missing.append(d)
print(\"doctypes in module MSCAST:\", frappe.db.count(\"DocType\", {\"module\": \"MSCAST\"}))
print(\"without a table:\", missing or \"none\")
print()
for dt, f in [(\"Custom Field\", None), (\"Workflow\", None), (\"Notification\", {\"is_standard\": 0}),
              (\"Report\", {\"is_standard\": \"No\"}), (\"Print Format\", {\"standard\": \"No\"}),
              (\"Workspace\", {\"name\": (\"like\", \"MSCAST%%\")}), (\"Server Script\", None),
              (\"Custom HTML Block\", None), (\"Role\", {\"name\": (\"like\", \"MSCAST%%\")})]:
    print(\"   %-20s %s\" % (dt, frappe.db.count(dt, f or {})))
" 2>&1 | grep -v RuntimeWarning'
