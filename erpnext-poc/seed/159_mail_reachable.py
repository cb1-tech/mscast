# -*- coding: utf-8 -*-
"""Let the real mailboxes actually receive.

153_real_users marked every new account unsubscribed, to avoid surprising a real
inbox. That made every notification undeliverable - the harness caught it. These
five mailboxes were supplied precisely so the demo can send to them, so they are
subscribed; the two +tag addresses stay muted because they are the same inbox
again and would only duplicate.
"""
import frappe

RECEIVE = [
    "latookaushik@yahoo.com",
    "latookaushik@hotmail.com",
    "uattech@carobar.net",
    "carobar.tradecars@gmail.com",
    "autoelectron.jp@gmail.com",
]
MUTE = ["autoelectron.jp+site@gmail.com", "autoelectron.jp+ca@gmail.com"]

for email in RECEIVE:
    if frappe.db.exists("User", email):
        frappe.db.set_value("User", email, "unsubscribed", 0, update_modified=False)
        print("will receive:", email)
for email in MUTE:
    if frappe.db.exists("User", email):
        frappe.db.set_value("User", email, "unsubscribed", 1, update_modified=False)
        print("muted       :", email, "(same inbox as the main gmail)")

frappe.db.commit()
frappe.clear_cache()

print()
print("=== notification reach ===")
for n in frappe.get_all("Notification", filters={"name": ("like", "MSCAST%"), "enabled": 1}, pluck="name"):
    live = []
    for r in frappe.get_all("Notification Recipient", filters={"parent": n},
                            fields=["receiver_by_role", "receiver_by_document_field"]):
        if r.receiver_by_document_field:
            live.append("field:" + r.receiver_by_document_field)
        if r.receiver_by_role:
            us = frappe.get_all("Has Role", filters={"role": r.receiver_by_role, "parenttype": "User"}, pluck="parent")
            for u in us:
                if frappe.db.get_value("User", u, "enabled") and not frappe.db.get_value("User", u, "unsubscribed"):
                    live.append(u.split("@")[0])
    print("  %-44s %s" % (n, ", ".join(sorted(set(live))) or "NOBODY"))
