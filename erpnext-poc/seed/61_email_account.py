"""MSCAST POC - 61: outgoing email account (Purelymail) + repoint scheduled mail to a real inbox.
Password is NOT set here - it is typed into the form by the user."""
import frappe

ACCOUNT = "mscast-test"
EMAIL = "uattech@carobar.net"
HOST = "smtp.purelymail.com"
PORT = 465
REAL_INBOX = "autoelectron.jp@gmail.com"
log = lambda m: print("[mail] " + m, flush=True)

meta = frappe.get_meta("Email Account")
flds = [f.fieldname for f in meta.fields if f.fieldname and
        any(k in f.fieldname for k in ("ssl", "tls", "smtp", "sender", "outgoing", "password", "login"))]
log("relevant fields: %s" % flds)

vals = {
    "doctype": "Email Account",
    "email_account_name": ACCOUNT,
    "email_id": EMAIL,
    "domain": None,
    "service": "",
    "enable_outgoing": 1,
    "default_outgoing": 1,
    "enable_incoming": 0,
    "smtp_server": HOST,
    "smtp_port": PORT,
    "always_use_account_email_id_as_sender": 1,
    "always_use_account_name_as_sender_name": 1,
    "send_unsubscribe_message": 0,
    "no_smtp_authentication": 0,
}
if meta.get_field("use_ssl_for_outgoing"):
    vals["use_ssl_for_outgoing"] = 1
    vals["use_tls"] = 0
elif meta.get_field("use_tls"):
    vals["use_tls"] = 0 if PORT == 465 else 1

if frappe.db.exists("Email Account", ACCOUNT):
    d = frappe.get_doc("Email Account", ACCOUNT)
    d.update({k: v for k, v in vals.items() if k != "doctype"})
    log("updating existing account")
else:
    d = frappe.get_doc(vals)
    log("creating account")
d.flags.ignore_permissions = True
d.flags.ignore_validate = True
d.flags.ignore_mandatory = True
d.save(ignore_permissions=True) if d.name else d.insert()
frappe.db.commit()
log("Email Account '%s' saved: %s:%s as %s (outgoing default)" % (d.name, HOST, PORT, EMAIL))
log("PASSWORD IS BLANK - open http://localhost:8080/app/email-account/%s and enter it, then Save"
    % d.name.replace(" ", "%20"))

# ---- repoint scheduled mail to a real inbox (demo users keep their fictional addresses)
for aer in frappe.get_all("Auto Email Report", pluck="name"):
    frappe.db.set_value("Auto Email Report", aer, {"email_to": REAL_INBOX, "enabled": 1})
    log("auto email report '%s' -> %s" % (aer, REAL_INBOX))

for dg in frappe.get_all("Email Digest", pluck="name"):
    d2 = frappe.get_doc("Email Digest", dg)
    d2.enabled = 1
    d2.set("recipients", [{"recipient": REAL_INBOX}])
    d2.flags.ignore_permissions = True
    d2.flags.ignore_mandatory = True
    d2.save()
    log("email digest '%s' enabled -> %s" % (dg, REAL_INBOX))

frappe.db.commit()
log("email queue rows: %d" % frappe.db.count("Email Queue"))
log("DONE")
