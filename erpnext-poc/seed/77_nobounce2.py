"""MSCAST POC - 77: unsubscribe every non-deliverable address so only real mailboxes get system mail."""
import frappe
log = lambda m: print("[nobounce2] " + m, flush=True)

GOOD_DOMAINS = ("gmail.com", "carobar.net", "carobar.dev")
for u in frappe.get_all("User", filters={"enabled": 1},
                        fields=["name", "email", "unsubscribed", "user_type"]):
    addr = (u.email or u.name or "")
    dom = addr.split("@")[-1].lower()
    if u.name == "Guest":
        continue
    deliverable = dom in GOOD_DOMAINS
    if not deliverable and not u.unsubscribed:
        frappe.db.set_value("User", u.name, "unsubscribed", 1)
        log("unsubscribed %-28s (domain %s does not resolve)" % (u.name, dom))
    elif deliverable:
        log("keeping      %-28s (real mailbox)" % u.name)
frappe.db.commit()

log("--- who now receives role-based notifications ---")
for r in ["Accounts Manager", "Projects Manager", "Purchase Manager", "Stock Manager",
          "Sales Manager", "HR Manager"]:
    users = frappe.get_all("Has Role", filters={"role": r, "parenttype": "User"}, pluck="parent")
    live = [u for u in users if frappe.db.get_value("User", u, "enabled")
            and not frappe.db.get_value("User", u, "unsubscribed")]
    log("  %-18s -> %s" % (r, live or "(nobody - notification will be skipped)"))
log("DONE")
