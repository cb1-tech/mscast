#!/usr/bin/env bash
# Count what is actually in a site. Used to prove a restore brought the business
# back, not merely that the command exited 0.
set -uo pipefail
SITE=${1:?usage: verify-site.sh <site>}
C=mscast-poc-backend-1
cat > /tmp/_verify_site.py <<'PY'
import frappe
from frappe.utils import flt
def n(dt, f=None):
    try: return frappe.db.count(dt, f or {})
    except Exception as e: return "ERR " + str(e)[:50]
rows = [
 ("apps installed",    ", ".join(frappe.get_installed_apps())),
 ("GL entries",        n("GL Entry", {"is_cancelled": 0})),
 ("sales invoices",    n("Sales Invoice", {"docstatus": 1})),
 ("purchase invoices", n("Purchase Invoice", {"docstatus": 1})),
 ("MSCAST BRMs",       n("MSCAST BRM")),
 ("MSCAST PCCs",       n("MSCAST PCC")),
 ("projects",          n("Project")),
 ("custom reports",    n("Report", {"is_standard": "No"})),
 ("print formats",     n("Print Format", {"standard": "No"})),
 ("workflows",         n("Workflow")),
 ("custom fields",     n("Custom Field")),
 ("enabled users",     n("User", {"enabled": 1})),
 ("employees",         n("Employee")),
 ("salary slips",      n("Salary Slip", {"docstatus": 1})),
 ("attendance",        n("Attendance")),
]
for k, v in rows:
    print("  %-20s %s" % (k, v))
d = flt(frappe.db.sql("select sum(debit)-sum(credit) from `tabGL Entry` where is_cancelled=0")[0][0])
print("  %-20s %s" % ("trial balance", d))
print("  %-20s %s" % ("VERDICT", "OK" if d == 0 else "TRIAL BALANCE DOES NOT NET"))
PY
docker cp /tmp/_verify_site.py "$C":/tmp/_verify_site.py >/dev/null
docker exec "$C" bash -c "cd /home/frappe/frappe-bench/sites && ../env/bin/python -c \"
import frappe
frappe.init(site='$SITE'); frappe.connect(); frappe.set_user('Administrator')
exec(open('/tmp/_verify_site.py').read())
\"" 2>&1 | grep -v -E 'RuntimeWarning|sys.prefix|sys.exec_prefix|frozen site'
