"""MSCAST POC - 31: asset location + submit the draft assets."""
import frappe

log = lambda m: print("[seed-31] " + m, flush=True)
LOC = "MSCAST Pune Office"

if not frappe.db.exists("Location", LOC):
    d = frappe.get_doc({"doctype": "Location", "location_name": LOC, "is_group": 0})
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    d.insert()
    log("location created")
frappe.db.commit()

for name in frappe.get_all("Asset", filters={"docstatus": 0}, pluck="name"):
    try:
        a = frappe.get_doc("Asset", name)
        a.location = LOC
        a.custodian = None
        a.flags.ignore_permissions = True
        a.save()
        a.submit()
        log("%s submitted; depreciation rows=%d" % (
            name, frappe.db.count("Asset Depreciation Schedule", {"asset": name})))
    except Exception as e:
        frappe.db.rollback()
        log("%s: %s" % (name, repr(e)[:250]))
frappe.db.commit()

for a in frappe.get_all("Asset", fields=["name", "asset_name", "gross_purchase_amount",
                                         "value_after_depreciation", "docstatus"]):
    log("  %s | %s | gross %s | book %s | docstatus %s" % (
        a.name, a.asset_name, a.gross_purchase_amount, a.value_after_depreciation, a.docstatus))
log("DONE")
