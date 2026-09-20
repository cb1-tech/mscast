"""MSCAST POC - 47: CWIP asset record (ledger CWIP already posted by PINV-26-00004)."""
import frappe
from frappe.utils import add_days, add_months, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
CAT = "Plant under construction (CWIP)"
log = lambda m: print("[47] " + m, flush=True)

meta = frappe.get_meta("Asset")
amt_fields = [f.fieldname for f in meta.fields if f.fieldname and
              any(k in f.fieldname for k in ("amount", "value", "existing", "composite"))]
log("asset amount/flag fields: %s" % amt_fields)

cwip_bal = frappe.db.sql("""select sum(debit-credit) from `tabGL Entry`
    where account like '%%Capital Work in Progress%%' and is_cancelled=0""")[0][0]
log("CWIP ledger balance: %s" % cwip_bal)

if frappe.db.exists("Asset", {"item_code": "FA-TEST-BENCH"}):
    log("CWIP asset already exists")
else:
    frappe.db.set_value("Asset Category", CAT, "enable_cwip_accounting", 0)
    frappe.db.commit()
    frappe.clear_cache()
    loc = frappe.db.get_value("Location", {}, "name")
    d = {"doctype": "Asset", "asset_name": "Hydraulic test bench (under construction)",
         "item_code": "FA-TEST-BENCH", "asset_category": CAT, "company": COMPANY,
         "is_existing_asset": 1, "asset_quantity": 1, "location": loc,
         "purchase_date": add_days(TODAY, -30), "available_for_use_date": add_months(TODAY, 3),
         "calculate_depreciation": 0,
         "asset_owner": "Company"}
    for fn in ("gross_purchase_amount", "purchase_amount", "net_purchase_amount",
               "total_asset_cost", "purchase_receipt_amount", "asset_value"):
        if meta.get_field(fn):
            d[fn] = 780000
    a = frappe.get_doc(d)
    a.flags.ignore_permissions = True
    a.flags.ignore_mandatory = True
    try:
        a.insert()
        log("created %s" % a.name)
        try:
            a.submit()
            log("submitted %s" % a.name)
        except Exception as e:
            log("left in draft: " + repr(e)[:220])
        frappe.db.commit()
    except Exception as e:
        frappe.db.rollback()
        log("FAIL " + repr(e)[:320])
    frappe.db.set_value("Asset Category", CAT, "enable_cwip_accounting", 1)
    frappe.db.commit()

fields = ["name", "asset_name", "asset_category", "docstatus", "status"]
fields += [f for f in ("gross_purchase_amount", "total_asset_cost", "purchase_amount") if meta.get_field(f)]
for a in frappe.get_all("Asset", fields=fields):
    log("  " + " | ".join(str(a.get(k)) for k in fields))
log("DONE")
