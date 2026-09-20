"""MSCAST POC - 29: asset category, asset items, fixed assets with depreciation."""
import frappe
from frappe.utils import add_months, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
CAT = "Plant & Machinery (Demo)"
TODAY = nowdate()
log = lambda m: print("[seed-29] " + m, flush=True)


def step(name, fn, *a, **kw):
    try:
        out = fn(*a, **kw)
        frappe.db.commit()
        log("OK   " + name + ((" -> " + str(out)) if out else ""))
        return out or True
    except Exception as e:
        frappe.db.rollback()
        log("FAIL " + name + " :: " + repr(e)[:350])
        return None


def ins(doc, submit=False):
    d = frappe.get_doc(doc)
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    d.insert(ignore_if_duplicate=True)
    if submit:
        d.submit()
    return d


def category():
    if frappe.db.exists("Asset Category", CAT):
        return "exists"
    fa = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Plant and Machinery%"), "is_group": 0}, "name") \
        or frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Fixed Asset", "is_group": 0}, "name")
    acc = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Accumulated Depreciation%"), "is_group": 0}, "name")
    exp = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Depreciation%"), "is_group": 0, "root_type": "Expense"}, "name")
    log("accounts: fixed=%s accum=%s expense=%s" % (fa, acc, exp))
    ins({"doctype": "Asset Category", "asset_category_name": CAT, "enable_cwip_accounting": 0,
         "accounts": [{"company_name": COMPANY, "fixed_asset_account": fa,
                       "accumulated_depreciation_account": acc, "depreciation_expense_account": exp}],
         "finance_books": [{"depreciation_method": "Straight Line",
                            "total_number_of_depreciations": 60, "frequency_of_depreciation": 1}]})
    return "category created"


def items():
    hsn = frappe.db.get_value("GST HSN Code", {"name": ("like", "8471%")}, "name") \
        or frappe.db.get_value("GST HSN Code", {}, "name")
    made = []
    for code, name in [("FA-CAD-WS", "CAD workstation - engineering"),
                       ("FA-WELD-SET", "Welding & testing equipment")]:
        if frappe.db.exists("Item", code):
            continue
        ins({"doctype": "Item", "item_code": code, "item_name": name, "item_group": "All Item Groups",
             "stock_uom": "Nos", "is_fixed_asset": 1, "is_stock_item": 0, "asset_category": CAT,
             "gst_hsn_code": hsn, "item_defaults": [{"company": COMPANY}]})
        made.append(code)
    return ", ".join(made) or "(existed)"


def assets():
    if frappe.db.count("Asset"):
        return "already exists"
    out = []
    for code, name, value, months_ago in [
        ("FA-CAD-WS", "CAD workstation - engineering", 185000, 14),
        ("FA-WELD-SET", "Welding & testing equipment", 420000, 26),
    ]:
        a = ins({"doctype": "Asset", "asset_name": name, "item_code": code, "asset_category": CAT,
                 "company": COMPANY, "is_existing_asset": 1, "asset_quantity": 1,
                 "purchase_date": add_months(TODAY, -months_ago),
                 "available_for_use_date": add_months(TODAY, -months_ago),
                 "gross_purchase_amount": value, "purchase_amount": value, "net_purchase_amount": value,
                 "opening_accumulated_depreciation": 0, "calculate_depreciation": 1,
                 "finance_books": [{"depreciation_method": "Straight Line",
                                    "total_number_of_depreciations": 60,
                                    "frequency_of_depreciation": 1,
                                    "depreciation_start_date": add_months(TODAY, -months_ago + 1)}]})
        try:
            a.submit()
            out.append(a.name + " submitted")
        except Exception as e:
            out.append(a.name + " draft: " + repr(e)[:120])
    return "; ".join(out)


def run():
    step("asset category", category)
    step("asset items", items)
    step("assets", assets)
    log("DONE")


run()
