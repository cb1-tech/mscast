"""MSCAST POC - 78: make sure every MSCAST notification has a live recipient."""
import frappe
log = lambda m: print("[notify] " + m, flush=True)
ME = "autoelectron.jp@gmail.com"

WANT = ["Purchase Manager", "Stock Manager", "Sales Manager", "HR Manager", "Purchase User",
        "Item Manager", "Quality Manager", "Employee"]
u = frappe.get_doc("User", ME)
have = {r.role for r in u.roles}
added = []
for r in WANT:
    if frappe.db.exists("Role", r) and r not in have:
        u.append("roles", {"role": r})
        added.append(r)
if added:
    u.flags.ignore_permissions = True
    u.save()
    frappe.db.commit()
log("roles added to %s: %s" % (ME, added or "(none needed)"))

log("--- MSCAST notifications and who they reach ---")
for n in frappe.get_all("Notification", filters={"name": ("like", "MSCAST%")},
                        fields=["name", "document_type", "event", "enabled", "channel"]):
    recips = frappe.get_all("Notification Recipient", filters={"parent": n.name},
                            fields=["receiver_by_role", "receiver_by_document_field"])
    live = []
    for r in recips:
        if r.receiver_by_role:
            users = frappe.get_all("Has Role", filters={"role": r.receiver_by_role,
                                                        "parenttype": "User"}, pluck="parent")
            live += [x for x in users if frappe.db.get_value("User", x, "enabled")
                     and not frappe.db.get_value("User", x, "unsubscribed")]
        if r.receiver_by_document_field:
            live.append("field:" + r.receiver_by_document_field)
    log("%-46s enabled=%s event=%s -> %s" % (n.name, n.enabled, n.event,
                                             sorted(set(live)) or "NOBODY"))
log("DONE")
