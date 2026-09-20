"""MSCAST POC - 48: check capital PI posting, submit remaining draft assets."""
import frappe
log = lambda m: print("[48] " + m, flush=True)

for r in frappe.db.sql("""select account, debit, credit from `tabGL Entry`
        where voucher_no='PINV-26-00004' and is_cancelled=0""", as_dict=True):
    log("  PINV-26-00004 GL: %s Dr %s Cr %s" % (r.account, r.debit, r.credit))

cw = frappe.db.get_value("Account", {"account_name": ("like", "%Capital Work in Progress%")}, "name")
log("CWIP account in COA: %s" % cw)

for name in frappe.get_all("Asset", filters={"docstatus": 0}, pluck="name"):
    try:
        a = frappe.get_doc("Asset", name)
        if not a.location:
            a.location = frappe.db.get_value("Location", {}, "name")
        a.flags.ignore_permissions = True
        a.save()
        a.submit()
        frappe.db.commit()
        log("submitted %s" % name)
    except Exception as e:
        frappe.db.rollback()
        log("%s still draft: %s" % (name, repr(e)[:260]))

log("assets: %s" % frappe.db.count("Asset", {"docstatus": 1}))
log("DONE")
