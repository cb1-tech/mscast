"""MSCAST POC - 28: QI parameters, template, inspections; asset items and assets (separate commits)."""
import frappe
from frappe.utils import add_days, add_months, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
TMPL = "Bought-out inspection - MSCAST"
CAT = "Plant & Machinery (Demo)"
log = lambda m: print("[seed-28] " + m, flush=True)
PARAMS = [("Overall length", "As per drawing"), ("Material grade / MTC", "Conforms to spec"),
          ("Surface finish", "No visible defects"), ("Hardness (HRC)", "50-58")]


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


def parameters():
    grp = frappe.db.get_value("Quality Inspection Parameter Group", {}, "name")
    if not grp:
        grp = ins({"doctype": "Quality Inspection Parameter Group",
                   "group_name": "MSCAST Mechanical"}).name
    made = 0
    for p, _v in PARAMS:
        if not frappe.db.exists("Quality Inspection Parameter", p):
            ins({"doctype": "Quality Inspection Parameter", "parameter": p, "parameter_group": grp})
            made += 1
    return "%d parameters (group %s)" % (made, grp)


def template():
    if not frappe.db.exists("Quality Inspection Template", TMPL):
        ins({"doctype": "Quality Inspection Template", "quality_inspection_template_name": TMPL,
             "item_quality_inspection_parameter": [
                 {"specification": p, "value": v} for p, v in PARAMS]})
    n = 0
    for code in ("BO-MOULD-TUBE", "BO-ROLL-SET", "ASM-WSU", "FAB-FRAME-WSU"):
        if frappe.db.exists("Item", code):
            frappe.db.set_value("Item", code, {"inspection_required_before_purchase": 1,
                                               "quality_inspection_template": TMPL})
            n += 1
    return "template applied to %d items" % n


def inspections():
    if frappe.db.count("Quality Inspection"):
        return "already exist"
    pr = frappe.db.get_value("Purchase Receipt", {"docstatus": 1}, "name")
    prd = frappe.get_doc("Purchase Receipt", pr)
    made = 0
    for it in prd.items:
        if it.item_code not in ("BO-MOULD-TUBE", "BO-ROLL-SET"):
            continue
        ins({"doctype": "Quality Inspection", "inspection_type": "Incoming",
             "reference_type": "Purchase Receipt", "reference_name": pr, "item_code": it.item_code,
             "quality_inspection_template": TMPL, "sample_size": 1, "inspected_by": "Administrator",
             "report_date": add_days(TODAY, -10), "status": "Accepted",
             "remarks": "Dimensions and material test certificate verified at supplier works.",
             "readings": [{"specification": p, "status": "Accepted", "reading_value": v}
                          for p, v in PARAMS[:3]]}, submit=True)
        made += 1
    return "%d incoming inspections" % made


def asset_items():
    made = []
    hsn = frappe.db.get_value("GST HSN Code", {"name": ("like", "8471%")}, "name") \
        or frappe.db.get_value("GST HSN Code", {}, "name")
    for code, name in [("FA-CAD-WS", "CAD workstation - engineering"),
                       ("FA-WELD-SET", "Welding & testing equipment")]:
        if frappe.db.exists("Item", code):
            continue
        ins({"doctype": "Item", "item_code": code, "item_name": name,
             "item_group": "All Item Groups", "stock_uom": "Nos", "is_fixed_asset": 1,
             "is_stock_item": 0, "asset_category": CAT, "gst_hsn_code": hsn,
             "item_defaults": [{"company": COMPANY}]})
        made.append(code)
    return "items: " + (", ".join(made) or "(existed)")


def assets():
    if frappe.db.count("Asset"):
        return "already exists"
    made = []
    for code, name, value, months_ago in [
        ("FA-CAD-WS", "CAD workstation - engineering", 185000, 14),
        ("FA-WELD-SET", "Welding & testing equipment", 420000, 26),
    ]:
        a = ins({
            "doctype": "Asset", "asset_name": name, "item_code": code, "asset_category": CAT,
            "company": COMPANY, "is_existing_asset": 1, "asset_quantity": 1,
            "purchase_date": add_months(TODAY, -months_ago),
            "available_for_use_date": add_months(TODAY, -months_ago),
            "gross_purchase_amount": value, "purchase_amount": value, "net_purchase_amount": value,
            "opening_accumulated_depreciation": 0, "calculate_depreciation": 1,
            "finance_books": [{"depreciation_method": "Straight Line",
                               "total_number_of_depreciations": 60, "frequency_of_depreciation": 1,
                               "depreciation_start_date": add_months(TODAY, -months_ago + 1)}],
        })
        try:
            a.submit()
            made.append(a.name + " submitted")
        except Exception as e:
            made.append(a.name + " draft (" + repr(e)[:90] + ")")
    return "; ".join(made)


def run():
    step("QI parameters", parameters)
    step("QI template", template)
    step("QI inspections", inspections)
    step("asset items", asset_items)
    step("assets", assets)
    log("DONE")


run()
