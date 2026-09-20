# -*- coding: utf-8 -*-
"""Who holds which MSCAST role in the POC, for the role cards."""
import frappe

ROLES = ["MSCAST Director", "Projects Manager", "Accounts Manager", "Accounts User",
         "Purchase Manager", "Purchase User", "Sales Manager", "Sales User",
         "Stock User", "Item Manager", "Quality Manager", "Projects User",
         "Design User", "HR Manager", "HR User", "Auditor"]

for r in ROLES:
    rows = frappe.db.sql("""select u.full_name, u.name, u.enabled
                            from `tabHas Role` h join `tabUser` u on u.name = h.parent
                            where h.role = %s and u.user_type = 'System User'
                              and u.name not in ('Administrator','Guest')
                            order by u.full_name""", (r,), as_dict=True)
    who = ", ".join("%s" % x.full_name for x in rows if x.enabled) or "-"
    print("%-20s %s" % (r, who))

print()
print("all enabled staff and everything they hold:")
for u in frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"},
                        fields=["name", "full_name"], order_by="full_name"):
    if u.name in ("Administrator", "Guest"):
        continue
    roles = sorted(x[0] for x in frappe.db.sql(
        "select role from `tabHas Role` where parent = %s", (u.name,)))
    keep = [r for r in roles if r in ROLES]
    print("  %-24s %-30s %s" % (u.full_name, u.name, ", ".join(keep) or "(none of ours)"))
