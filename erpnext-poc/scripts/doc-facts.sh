#!/usr/bin/env bash
# Facts the documents assert, printed from the running system.
set -euo pipefail
C=mscast-poc-backend-1

docker exec -i $C bash -c 'cd /home/frappe/frappe-bench && bench --site frontend console' <<'PY' 2>/dev/null
import frappe

print("### who is who, and what they hold")
for u in frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"},
                        fields=["name", "full_name"], order_by="creation"):
    roles = sorted(frappe.get_all("Has Role",
                   filters={"parent": u.name, "parenttype": "User"}, pluck="role"))
    print("  %-32s %-22s %d" % (u.name, u.full_name or "-", len(roles)))
    print("      %s" % ", ".join(roles))

print()
print("### System Manager, users only")
rows = frappe.db.sql("""select h.parent, u.full_name, u.enabled
                        from `tabHas Role` h join `tabUser` u on u.name = h.parent
                        where h.role = 'System Manager'""", as_dict=True)
for r in rows:
    print("   %-32s %-22s enabled=%s" % (r.parent, r.full_name or "-", r.enabled))

print()
print("### total roles defined in this system")
print("   %d" % frappe.db.count("Role"))
print("   Administrator holds %d" % frappe.db.count("Has Role",
        {"parent": "Administrator", "parenttype": "User"}))

print()
print("### disabled users")
for u in frappe.get_all("User", filters={"enabled": 0, "user_type": "System User"}, pluck="name"):
    print("   ", u)

print()
print("### document counts")
for dt in ["Item", "Customer", "Supplier", "Employee", "Project", "MSCAST Exception",
           "MSCAST PCC", "MSCAST BRM", "MSCAST Drawing", "MSCAST Project Kickoff"]:
    try:
        print("   %-26s %5d" % (dt, frappe.db.count(dt)))
    except Exception as e:
        print("   %-26s n/a" % dt)
PY
