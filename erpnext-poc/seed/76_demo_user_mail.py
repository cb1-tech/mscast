"""MSCAST POC - 76: stop system mail going to the fictional demo addresses.
mscast.demo does not resolve - every notification to those users would hard-bounce and
hurt the sending reputation of carobar.net."""
import frappe
log = lambda m: print("[nobounce] " + m, flush=True)

DEMO = ["director@mscast.demo", "auditor@mscast.demo"]
m = frappe.get_meta("User")
have = {f.fieldname for f in m.fields if f.fieldname}
log("user mail-control fields: %s"
    % sorted(have & {"unsubscribed", "thread_notify", "send_me_a_copy", "document_follow_notify",
                     "allowed_in_mentions", "enabled", "mute_sounds"}))

for email in DEMO:
    if not frappe.db.exists("User", email):
        log("%s: absent" % email)
        continue
    vals = {}
    for fn, v in (("unsubscribed", 1), ("thread_notify", 0), ("send_me_a_copy", 0),
                  ("document_follow_notify", 0)):
        if fn in have:
            vals[fn] = v
    frappe.db.set_value("User", email, vals)
    log("%s -> %s (login still works, no outbound mail)" % (email, vals))

frappe.db.commit()

# who would actually receive role-based notifications now?
roles = ["Accounts Manager", "Projects Manager", "Purchase Manager", "Stock Manager"]
for r in roles:
    users = frappe.get_all("Has Role", filters={"role": r, "parenttype": "User"}, pluck="parent")
    live = [u for u in users if frappe.db.get_value("User", u, "enabled")
            and not frappe.db.get_value("User", u, "unsubscribed")]
    log("role %-18s -> %s" % (r, live))
log("DONE")
