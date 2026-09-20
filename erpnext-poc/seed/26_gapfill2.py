"""MSCAST POC - 26: second pass on the gap list (bank, QI parameters, assets, alerts, scorecard)."""
import frappe
from frappe.utils import add_days, add_months, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[seed-26] " + m, flush=True)


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


def pick_hsn(*prefixes):
    for p in prefixes:
        rows = frappe.db.sql("""select name from `tabGST HSN Code` where name like %s
                                and char_length(name) in (6, 8) order by char_length(name), name""",
                             (p + "%",), as_dict=True)
        if rows:
            return rows[0].name
    return frappe.db.get_value("GST HSN Code", {}, "name")


def bank_guarantees():
    if frappe.db.count("Bank Guarantee"):
        return "already exists"
    if not frappe.db.exists("Bank", "HDFC Bank"):
        ins({"doctype": "Bank", "bank_name": "HDFC Bank"})
    so = frappe.db.get_value("Sales Order", {"customer": ("like", "Sahyadri%"), "docstatus": 1}, "name")
    bank_acc = frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Bank", "is_group": 0}, "name")
    for num, days_ago, validity, label in [
        ("HDFC/ABG/2026/0841", 110, 400, "Advance bank guarantee (30% advance)"),
        ("HDFC/PBG/2026/0992", 20, 550, "Performance bank guarantee (10% of order)"),
    ]:
        ins({"doctype": "Bank Guarantee", "bg_type": "Providing", "reference_doctype": "Sales Order",
             "reference_docname": so, "customer": "Sahyadri Steels Ltd (DEMO)", "project": "PROJ-0001",
             "amount": 2026500, "start_date": add_days(TODAY, -days_ago), "validity": validity,
             "bank": "HDFC Bank", "bank_account_no": "50200012345678",
             "bank_guarantee_number": num, "name_of_beneficiary": "Sahyadri Steels Ltd (DEMO)",
             "margin_money": 202650, "charges": 24318, "company": COMPANY, "account": bank_acc,
             "more_information": label}, submit=True)
    return "ABG + PBG registered"


QI_PARAMS = ["Overall length", "Material grade / MTC", "Surface finish", "Hardness (HRC)"]


def quality_inspections():
    for p in QI_PARAMS:
        if not frappe.db.exists("Quality Inspection Parameter", p):
            ins({"doctype": "Quality Inspection Parameter", "parameter": p,
                 "parameter_group": frappe.db.get_value("Quality Inspection Parameter Group", {}, "name")})
    if frappe.db.count("Quality Inspection"):
        return "inspections already exist"
    pr = frappe.db.get_value("Purchase Receipt", {"docstatus": 1}, "name")
    prd = frappe.get_doc("Purchase Receipt", pr)
    made = 0
    for it in prd.items[:2]:
        ins({
            "doctype": "Quality Inspection", "inspection_type": "Incoming",
            "reference_type": "Purchase Receipt", "reference_name": pr, "item_code": it.item_code,
            "sample_size": 1, "inspected_by": "Administrator", "report_date": add_days(TODAY, -10),
            "status": "Accepted", "remarks": "Dimensions and material test certificate verified.",
            "readings": [
                {"specification": "Overall length", "status": "Accepted", "reading_value": "As per drawing"},
                {"specification": "Material grade / MTC", "status": "Accepted", "reading_value": "Conforms"},
            ],
        }, submit=True)
        made += 1
    return "%d incoming inspections" % made


def fixed_assets():
    if frappe.db.count("Asset"):
        return "already exists"
    fa_acc = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Plant and Machinery%"), "is_group": 0}, "name") \
        or frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Fixed Asset", "is_group": 0}, "name")
    acc_dep = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Accumulated Depreciation%"), "is_group": 0}, "name")
    dep_exp = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Depreciation%"), "is_group": 0, "root_type": "Expense"}, "name")
    cat = "Plant & Machinery (Demo)"
    if not frappe.db.exists("Asset Category", cat):
        ins({"doctype": "Asset Category", "asset_category_name": cat, "enable_cwip_accounting": 0,
             "accounts": [{"company_name": COMPANY, "fixed_asset_account": fa_acc,
                           "accumulated_depreciation_account": acc_dep,
                           "depreciation_expense_account": dep_exp}],
             "finance_books": [{"depreciation_method": "Straight Line",
                                "total_number_of_depreciations": 60, "frequency_of_depreciation": 1}]})
    made = []
    for code, name, value, months_ago, hsn_prefix in [
        ("FA-CAD-WS", "CAD workstation - engineering", 185000, 14, "847130"),
        ("FA-WELD-SET", "Welding & testing equipment", 420000, 26, "851590"),
    ]:
        if not frappe.db.exists("Item", code):
            ins({"doctype": "Item", "item_code": code, "item_name": name,
                 "item_group": "All Item Groups", "stock_uom": "Nos", "is_fixed_asset": 1,
                 "is_stock_item": 0, "asset_category": cat, "gst_hsn_code": pick_hsn(hsn_prefix, hsn_prefix[:4]),
                 "item_defaults": [{"company": COMPANY}]})
        a = ins({
            "doctype": "Asset", "asset_name": name, "item_code": code, "asset_category": cat,
            "company": COMPANY, "is_existing_asset": 1, "asset_quantity": 1,
            "purchase_date": add_months(TODAY, -months_ago),
            "available_for_use_date": add_months(TODAY, -months_ago),
            "gross_purchase_amount": value, "opening_accumulated_depreciation": 0,
            "calculate_depreciation": 1,
            "finance_books": [{"depreciation_method": "Straight Line",
                               "total_number_of_depreciations": 60, "frequency_of_depreciation": 1,
                               "depreciation_start_date": add_months(TODAY, -months_ago + 1)}],
        })
        try:
            a.submit()
        except Exception as e:
            log("asset submit %s: %s" % (a.name, repr(e)[:180]))
        made.append(a.name)
    return "assets: " + ", ".join(made)


def alerts():
    user = frappe.db.get_value("User", {"name": ("like", "admin@%")}, "name") or "Administrator"
    made = []
    if not frappe.db.exists("Notification", "MSCAST BG expiry alert"):
        ins({"doctype": "Notification", "name": "MSCAST BG expiry alert",
             "subject": "Bank guarantee {{ doc.bank_guarantee_number }} expires in 30 days",
             "document_type": "Bank Guarantee", "event": "Days Before", "date_changed": "end_date",
             "days_in_advance": 30, "enabled": 1, "channel": "Email",
             "message": "Bank guarantee {{ doc.bank_guarantee_number }} for {{ doc.customer }} "
                        "expires on {{ doc.end_date }}. Arrange extension or release.",
             "recipients": [{"receiver_by_role": "Accounts Manager"}]})
        made.append("BG expiry")
    if not frappe.db.exists("Notification", "MSCAST PO over PCC"):
        ins({"doctype": "Notification", "name": "MSCAST PO over PCC",
             "subject": "Purchase Order {{ doc.name }} exceeds the PCC budget",
             "document_type": "Purchase Order", "event": "Submit", "enabled": 1, "channel": "Email",
             "condition": "doc.pcc_budget_amount and doc.grand_total > doc.pcc_budget_amount",
             "message": "PO {{ doc.name }} to {{ doc.supplier }} is {{ doc.grand_total }} against a PCC "
                        "budget of {{ doc.pcc_budget_amount }}. Justification: {{ doc.pcc_variance_note }}",
             "recipients": [{"receiver_by_role": "Purchase Manager"}]})
        made.append("PO vs PCC")
    if not frappe.db.exists("Notification", "MSCAST drawing awaiting customer approval"):
        ins({"doctype": "Notification", "name": "MSCAST drawing awaiting customer approval",
             "subject": "Drawing {{ doc.drawing_no }} is waiting for customer approval",
             "document_type": "MSCAST Drawing", "event": "Value Change", "value_changed": "status",
             "enabled": 1, "channel": "Email",
             "condition": "doc.status == 'For Customer Approval'",
             "message": "Drawing {{ doc.drawing_no }} ({{ doc.title }}) on project {{ doc.project }} "
                        "is with the customer for approval.",
             "recipients": [{"receiver_by_role": "Projects Manager"}]})
        made.append("drawing approval")

    for nm, report, fmt in [("MSCAST Project MIS - weekly", "MSCAST Project MIS", "HTML"),
                            ("MSCAST Dispatch schedule - weekly", "MSCAST Dispatch Schedule", "XLSX")]:
        if frappe.db.exists("Auto Email Report", nm):
            continue
        ins({"doctype": "Auto Email Report", "name": nm, "report": report, "user": "Administrator",
             "report_type": "Query Report", "email_to": "director@mcast.co.in", "format": fmt,
             "frequency": "Weekly", "day_of_week": "Monday", "enabled": 0, "no_of_rows": 100,
             "description": "Scheduled management report (disabled in the POC - no mail server configured)"})
        made.append(nm)

    if not frappe.db.exists("Email Digest", "MSCAST daily digest"):
        ins({"doctype": "Email Digest", "name": "MSCAST daily digest", "company": COMPANY,
             "frequency": "Daily", "enabled": 0, "recipients": [{"recipient": user}],
             "income": 1, "expenses_booked": 1, "bank_balance": 1, "credit_balance": 1,
             "invoiced_amount": 1, "payables": 1, "new_quotations": 1, "pending_quotations": 1,
             "sales_orders_to_bill": 1, "sales_orders_to_deliver": 1, "purchase_orders_to_receive": 1,
             "open_todos": 1})
        made.append("daily digest")
    return ", ".join(made) or "(all existed)"


def scorecard():
    if frappe.db.count("Supplier Scorecard"):
        return "already exists"
    for crit, formula in [("On-time delivery", "100 * (1 - {rejected_qty} / {received_qty})"),
                          ("Quality acceptance", "100 * (1 - {rejected_qty} / {received_qty})")]:
        if not frappe.db.exists("Supplier Scorecard Criteria", crit):
            ins({"doctype": "Supplier Scorecard Criteria", "criteria_name": crit,
                 "max_score": 100, "formula": formula,
                 "weight": 0})
    ins({
        "doctype": "Supplier Scorecard", "supplier": "Pushkar Fabricators (DEMO)",
        "period": "Per Month",
        "weighting_function": "{total_score} * max( 0, min ( 1 , (12 - {period_number}) / 12) )",
        "criteria": [{"criteria_name": "On-time delivery", "weight": 60},
                     {"criteria_name": "Quality acceptance", "weight": 40}],
        "standings": [
            {"standing_name": "Excellent", "min_grade": 80, "max_grade": 100},
            {"standing_name": "Average", "min_grade": 50, "max_grade": 80},
            {"standing_name": "Poor", "min_grade": 0, "max_grade": 50, "warn_pos": 1},
        ],
    })
    return "scorecard for Pushkar Fabricators"


def run():
    step("bank guarantees", bank_guarantees)
    step("quality inspections", quality_inspections)
    step("fixed assets", fixed_assets)
    step("alerts & scheduled reports", alerts)
    step("supplier scorecard", scorecard)
    log("DONE")


run()
