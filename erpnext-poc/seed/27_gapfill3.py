"""MSCAST POC - 27: quality inspection template + inspections, assets, supplier scorecard."""
import frappe
from frappe.utils import add_days, add_months, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
log = lambda m: print("[seed-27] " + m, flush=True)


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


def quality():
    tmpl = "Bought-out inspection - MSCAST"
    if not frappe.db.exists("Quality Inspection Template", tmpl):
        ins({"doctype": "Quality Inspection Template", "quality_inspection_template_name": tmpl,
             "item_quality_inspection_parameter": [
                 {"specification": "Overall length", "acceptance_formula_based": 0, "value": "As per drawing"},
                 {"specification": "Material grade / MTC", "value": "Conforms to spec"},
                 {"specification": "Surface finish", "value": "No visible defects"},
                 {"specification": "Hardness (HRC)", "min_value": 50, "max_value": 58,
                  "numeric": 1},
             ]})
    n = 0
    for code in ("BO-MOULD-TUBE", "BO-ROLL-SET", "ASM-WSU", "FAB-FRAME-WSU"):
        if frappe.db.exists("Item", code):
            frappe.db.set_value("Item", code, {"inspection_required_before_purchase": 1,
                                               "quality_inspection_template": tmpl})
            n += 1
    frappe.db.commit()

    if frappe.db.count("Quality Inspection"):
        return "template on %d items; inspections already exist" % n
    pr = frappe.db.get_value("Purchase Receipt", {"docstatus": 1}, "name")
    prd = frappe.get_doc("Purchase Receipt", pr)
    made = 0
    for it in prd.items:
        if it.item_code not in ("BO-MOULD-TUBE", "BO-ROLL-SET"):
            continue
        ins({
            "doctype": "Quality Inspection", "inspection_type": "Incoming",
            "reference_type": "Purchase Receipt", "reference_name": pr, "item_code": it.item_code,
            "quality_inspection_template": tmpl, "sample_size": 1, "inspected_by": "Administrator",
            "report_date": add_days(TODAY, -10), "status": "Accepted",
            "remarks": "Dimensions and material test certificate verified at supplier works.",
            "readings": [
                {"specification": "Overall length", "status": "Accepted", "reading_value": "As per drawing"},
                {"specification": "Material grade / MTC", "status": "Accepted", "reading_value": "Conforms"},
                {"specification": "Surface finish", "status": "Accepted", "reading_value": "OK"},
            ],
        }, submit=True)
        made += 1
    return "template on %d items, %d inspections" % (n, made)


def assets():
    if frappe.db.count("Asset"):
        return "already exists"
    cat = "Plant & Machinery (Demo)"
    made = []
    for code, name, value, months_ago in [
        ("FA-CAD-WS", "CAD workstation - engineering", 185000, 14),
        ("FA-WELD-SET", "Welding & testing equipment", 420000, 26),
    ]:
        doc = {
            "doctype": "Asset", "asset_name": name, "item_code": code, "asset_category": cat,
            "company": COMPANY, "is_existing_asset": 1, "asset_quantity": 1,
            "purchase_date": add_months(TODAY, -months_ago),
            "available_for_use_date": add_months(TODAY, -months_ago),
            "gross_purchase_amount": value, "purchase_amount": value,
            "net_purchase_amount": value, "opening_accumulated_depreciation": 0,
            "calculate_depreciation": 1,
            "finance_books": [{"depreciation_method": "Straight Line",
                               "total_number_of_depreciations": 60, "frequency_of_depreciation": 1,
                               "depreciation_start_date": add_months(TODAY, -months_ago + 1)}],
        }
        a = ins(doc)
        try:
            a.submit()
        except Exception as e:
            log("asset submit %s: %s" % (a.name, repr(e)[:200]))
        made.append("%s (%s)" % (a.name, a.docstatus))
    return "assets: " + ", ".join(made)


def scorecard():
    if frappe.db.count("Supplier Scorecard"):
        return "already exists"
    variables = frappe.get_all("Supplier Scorecard Variable", fields=["name", "param_name"])
    log("available scorecard variables: %s" % [v.param_name for v in variables][:20])
    names = {v.param_name for v in variables}
    if {"total_accepted_items", "total_received_items"} <= names:
        quality_formula = "100 * {total_accepted_items} / {total_received_items}"
    elif {"rejected_items", "received_items"} <= names:
        quality_formula = "100 * (1 - {rejected_items} / {received_items})"
    else:
        quality_formula = "100"
    if {"on_time_shipment_num", "total_shipments"} <= names:
        delivery_formula = "100 * {on_time_shipment_num} / {total_shipments}"
    elif "shipments_on_time" in names:
        delivery_formula = "100 * {shipments_on_time} / {total_shipments}"
    else:
        delivery_formula = "100"
    log("formulas: delivery=%s quality=%s" % (delivery_formula, quality_formula))

    for crit, formula in [("MSCAST On-time delivery", delivery_formula),
                          ("MSCAST Quality acceptance", quality_formula)]:
        if not frappe.db.exists("Supplier Scorecard Criteria", crit):
            ins({"doctype": "Supplier Scorecard Criteria", "criteria_name": crit,
                 "max_score": 100, "formula": formula})
    ins({
        "doctype": "Supplier Scorecard", "supplier": "Pushkar Fabricators (DEMO)",
        "period": "Per Month",
        "weighting_function": "{total_score} * max( 0, min ( 1 , (12 - {period_number}) / 12) )",
        "criteria": [{"criteria_name": "MSCAST On-time delivery", "weight": 60},
                     {"criteria_name": "MSCAST Quality acceptance", "weight": 40}],
        "standings": [
            {"standing_name": "Excellent", "min_grade": 80, "max_grade": 100},
            {"standing_name": "Average", "min_grade": 50, "max_grade": 80},
            {"standing_name": "Poor", "min_grade": 0, "max_grade": 50, "warn_pos": 1},
        ],
    })
    return "scorecard created for Pushkar Fabricators"


def run():
    step("quality inspection template + inspections", quality)
    step("fixed assets", assets)
    step("supplier scorecard", scorecard)
    log("DONE")


run()
