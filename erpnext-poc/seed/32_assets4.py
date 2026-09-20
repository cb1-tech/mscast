"""MSCAST POC - 32: inspect Asset fields, set location, submit."""
import frappe

log = lambda m: print("[seed-32] " + m, flush=True)
LOC = "MSCAST Pune Office"

fields = [f.fieldname for f in frappe.get_meta("Asset").fields
          if f.fieldname and any(k in f.fieldname for k in ("amount", "value", "location", "custodian"))]
log("asset fields: %s" % fields)
log("assets: %s" % frappe.get_all("Asset", fields=["name", "asset_name", "docstatus"]))

for name in frappe.get_all("Asset", filters={"docstatus": 0}, pluck="name"):
    try:
        a = frappe.get_doc("Asset", name)
        a.location = LOC
        a.flags.ignore_permissions = True
        a.save()
        a.submit()
        frappe.db.commit()
        log("%s submitted" % name)
    except Exception as e:
        frappe.db.rollback()
        log("%s failed: %s" % (name, repr(e)[:250]))

for a in frappe.get_all("Asset", fields=["name", "asset_name", "docstatus", "status"]):
    log("  %s | %s | docstatus=%s | status=%s" % (a.name, a.asset_name, a.docstatus, a.status))
log("depreciation schedules: %d" % frappe.db.count("Asset Depreciation Schedule"))
log("DONE")
