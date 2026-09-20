#!/usr/bin/env bash
C=mscast-poc-backend-1
docker exec "$C" bash -c 'cd /home/frappe/frappe-bench/sites && ../env/bin/python -c "
import frappe, json, os, traceback
frappe.init(site=\"staging.localhost\"); frappe.connect(); frappe.set_user(\"Administrator\")
frappe.flags.in_import = True
base = \"/home/frappe/frappe-bench/apps/mscast_erp/mscast_erp/fixtures\"
for f in [\"workspace.json\", \"workflow.json\", \"notification.json\"]:
    rows = json.load(open(os.path.join(base, f)))
    print()
    print(\"====\", f, len(rows), \"records\")
    ok = err = 0
    first = None
    for r in rows:
        try:
            if frappe.db.exists(r[\"doctype\"], r.get(\"name\")):
                ok += 1; continue
            d = frappe.get_doc(r)
            d.flags.ignore_permissions = True
            d.flags.ignore_mandatory = True
            d.flags.ignore_links = True
            d.insert()
            ok += 1
        except Exception as e:
            err += 1
            if first is None:
                first = (r.get(\"name\"), type(e).__name__, str(e)[:260])
    print(\"   imported/exists:\", ok, \"  failed:\", err)
    if first:
        print(\"   first failure:\", first[0], \"|\", first[1], \"|\", first[2])
frappe.db.commit()
print()
print(\"workspaces now:\", frappe.db.count(\"Workspace\", {\"name\": (\"like\", \"MSCAST%\")}))
print(\"workflows now:\", frappe.db.count(\"Workflow\"))
print(\"notifications now:\", frappe.db.count(\"Notification\", {\"is_standard\": 0}))
" 2>&1 | grep -v RuntimeWarning'
