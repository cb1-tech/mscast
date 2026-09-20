# -*- coding: utf-8 -*-
"""Notifications go to a role, not to a named mailbox.

Hardcoding an address means the alert dies the day that person leaves. A role
survives the people in it - which is the whole reason the roles exist.
"""
import frappe

BY_ROLE = {
    "MSCAST drawing awaiting customer approval": "Projects User",
    "MSCAST PO over PCC": "Purchase Manager",
    "MSCAST BG expiry alert": "Accounts Manager",
}

for name, role in BY_ROLE.items():
    if not frappe.db.exists("Notification", name):
        continue
    n = frappe.get_doc("Notification", name)
    n.set("recipients", [{"receiver_by_role": role}])
    n.flags.ignore_permissions = True
    n.save()
    holders = frappe.db.sql("""select u.name from `tabUser` u join `tabHas Role` r on r.parent = u.name
        where r.role = %s and u.enabled = 1 and u.name not in ('Administrator','Guest')""", (role,), as_dict=True)
    print("%-44s -> role %-18s (%s)" % (name, role, ", ".join(h.name.split("@")[0] for h in holders)))

# anything still without a cost centre, including rows created after the last pass
cc = frappe.db.get_value("Company", frappe.defaults.get_global_default("company"), "cost_center")
rows = frappe.db.sql("""select name, voucher_type, voucher_no from `tabGL Entry`
    where is_cancelled = 0 and ifnull(cost_center,'') = ''""", as_dict=True)
for r in rows:
    frappe.db.set_value("GL Entry", r.name, "cost_center", cc, update_modified=False)
print()
print("cost centre set on %d further entr%s" % (len(rows), "y" if len(rows) == 1 else "ies"))

frappe.db.commit()
frappe.clear_cache()
print("remaining without a cost centre:",
      frappe.db.sql("select count(*) from `tabGL Entry` where is_cancelled=0 and ifnull(cost_center,'')=''")[0][0])
