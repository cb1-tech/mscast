# -*- coding: utf-8 -*-
"""Take System Manager off the operational staff accounts.

T6f found an ordinary staff account - Item Manager, Projects User, Stock User -
also holding System Manager. That bypasses every control in the system: the BRM
payment block, the purchase order approval, the drawing release sequence, the
approval matrix, all of it. And it was invisible to T6e, which excludes System
Manager holders by design.

Nobody who does day-to-day work in the system should carry it. Administration
is admin@mscast.local and the built-in Administrator; that is the whole list.

This costs nothing for demonstrating: the roles are what show a visitor the
difference between what a buyer can do and what a director can do, and that
difference only exists if the buyer is not secretly an administrator.
"""
import frappe

ADMIN_ACCOUNTS = {"Administrator", "admin@mscast.local"}
ROLE = "System Manager"

holders = {u[0] for u in frappe.db.sql(
    """select h.parent from `tabHas Role` h join `tabUser` u on u.name = h.parent
       where h.role = %s and u.enabled = 1 and u.user_type = 'System User'""", (ROLE,))}

print("System Manager holders before:")
for h in sorted(holders):
    print("   ", h)

for name in sorted(holders - ADMIN_ACCOUNTS):
    doc = frappe.get_doc("User", name)
    kept = [r.role for r in doc.get("roles") if r.role != ROLE]
    doc.set("roles", [{"role": r} for r in sorted(set(kept))])
    doc.flags.ignore_permissions = True
    doc.save()
    print()
    print("removed %s from %s (%s)" % (ROLE, doc.full_name, name))
    print("   keeps:", ", ".join(sorted(set(kept))) or "(nothing)")

frappe.db.commit()

print()
print("System Manager holders after:")
for u in frappe.db.sql(
        """select h.parent from `tabHas Role` h join `tabUser` u on u.name = h.parent
           where h.role = %s and u.enabled = 1""", (ROLE,), as_dict=True):
    print("   ", u.parent)
print("    Administrator (built in)")
