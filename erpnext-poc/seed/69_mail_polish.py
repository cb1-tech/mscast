"""MSCAST POC - 69: mail footer + host settings inspection/fix."""
import frappe
log = lambda m: print("[mail6] " + m, flush=True)

m = frappe.get_meta("System Settings")
flds = [f.fieldname for f in m.fields if f.fieldname and
        any(k in f.fieldname for k in ("footer", "mail", "email", "host", "url"))]
log("System Settings candidates: %s" % flds)
for fn in flds:
    log("  %-34s = %r" % (fn, frappe.db.get_single_value("System Settings", fn)))

ea = frappe.get_meta("Email Account")
log("Email Account footer fields: %s" % [f.fieldname for f in ea.fields
                                         if f.fieldname and "footer" in f.fieldname])
log("site host_name in conf: %r" % frappe.conf.get("host_name"))
log("frappe.utils.get_url() -> %s" % frappe.utils.get_url())

FOOTER = ('<div style="color:#7c7c7c;font-size:11px">MSCAST Engineering Pvt Ltd &middot; '
          'Pune, Maharashtra, India &middot; This message was sent from the MSCAST ERP system.</div>')

if ea.get_field("footer"):
    frappe.db.set_value("Email Account", "mscast-test", "footer", FOOTER)
    log("custom footer set on the email account")
for fn in ("disable_standard_email_footer", "email_footer_address"):
    if m.get_field(fn):
        frappe.db.set_single_value("System Settings", fn,
                                   1 if fn == "disable_standard_email_footer"
                                   else "MSCAST Engineering Pvt Ltd, Pune, India")
        log("System Settings.%s set" % fn)
frappe.db.commit()
log("DONE")
