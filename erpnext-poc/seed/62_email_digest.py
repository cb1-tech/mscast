"""MSCAST POC - 62: real user for the digest recipient (Email Digest links to User), enable digest."""
import frappe

REAL = "autoelectron.jp@gmail.com"
log = lambda m: print("[mail2] " + m, flush=True)

if not frappe.db.exists("User", REAL):
    u = frappe.get_doc({"doctype": "User", "email": REAL, "first_name": "Sanjay",
                        "send_welcome_email": 0, "user_type": "System User",
                        "roles": [{"role": r} for r in
                                  ["System Manager", "MSCAST Director", "Accounts Manager",
                                   "Projects Manager"] if frappe.db.exists("Role", r)]})
    u.flags.ignore_permissions = True
    u.insert()
    frappe.db.commit()
    log("created user %s (System Manager + MSCAST Director)" % REAL)
else:
    log("user %s already exists" % REAL)

for dg in frappe.get_all("Email Digest", pluck="name"):
    d = frappe.get_doc("Email Digest", dg)
    d.enabled = 1
    d.frequency = "Daily"
    d.set("recipients", [{"recipient": REAL}])
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    d.save()
    log("digest '%s' enabled, daily, -> %s" % (dg, REAL))

frappe.db.commit()
acc = frappe.db.get_value("Email Account", "mscast-test",
                          ["email_id", "smtp_server", "smtp_port", "use_ssl_for_outgoing",
                           "default_outgoing", "enable_outgoing"], as_dict=True)
log("outgoing account: %s" % acc)
log("password set? %s" % bool(frappe.db.get_value("Email Account", "mscast-test", "password")))
log("DONE")
