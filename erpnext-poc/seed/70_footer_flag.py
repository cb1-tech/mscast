"""MSCAST POC - 70: turn the custom footer on (set_footer checkbox)."""
import frappe
log = lambda m: print("[mail7] " + m, flush=True)
frappe.db.set_value("Email Account", "mscast-test", "set_footer", 1)
frappe.db.commit()
v = frappe.db.get_value("Email Account", "mscast-test", ["set_footer", "footer"], as_dict=True)
log("set_footer=%s" % v.set_footer)
log("footer=%s" % (v.footer or "")[:160])
log("standard 'Sent via ERPNext' footer disabled: %s"
    % frappe.db.get_single_value("System Settings", "disable_standard_email_footer"))
log("DONE")
