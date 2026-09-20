"""MSCAST POC - 25: close gaps found in the inventory check.

MSME supplier data, bank guarantees, quality inspections, delivery note + packing slip,
cheque print template, fixed assets with depreciation, alerts (notification / auto email / digest),
supplier scorecard, warranty claim.
"""
import json
import frappe
from frappe.utils import add_days, add_months, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[seed-25] " + m, flush=True)


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


MSME = {
    "Pushkar Fabricators (DEMO)": ("UDYAM-MH-26-0011234", "Small"),
    "Shivneri Machining Works (DEMO)": ("UDYAM-MH-26-0022345", "Micro"),
    "Hydropower Systems (DEMO)": ("UDYAM-MH-26-0033456", "Small"),
    "Pune Electrical Panels (DEMO)": ("UDYAM-MH-26-0044567", "Micro"),
    "Vidarbha Heavy Transport (DEMO)": ("UDYAM-MH-26-0055678", "Small"),
    "Precision Inspection Services (DEMO)": ("UDYAM-MH-26-0066789", "Micro"),
}


def msme():
    n = 0
    for sup, (udyam, mtype) in MSME.items():
        if frappe.db.exists("Supplier", sup):
            frappe.db.set_value("Supplier", sup, {"msme_udyam_no": udyam, "msme_type": mtype})
            n += 1
    for sup in frappe.get_all("Supplier", filters={"msme_type": ("in", ["", None])}, pluck="name"):
        frappe.db.set_value("Supplier", sup, "msme_type", "Not registered")
    return "%d MSME suppliers tagged" % n


def bank_guarantees():
    if frappe.db.count("Bank Guarantee"):
        return "already exists"
    so = frappe.db.get_value("Sales Order", {"customer": ("like", "Sahyadri%"), "docstatus": 1}, "name")
    bank = frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Bank", "is_group": 0}, "name")
    ins({"doctype": "Bank Guarantee", "bg_type": "Providing", "reference_doctype": "Sales Order",
         "reference_docname": so, "customer": "Sahyadri Steels Ltd (DEMO)", "project": "PROJ-0001",
         "amount": 2026500, "start_date": add_days(TODAY, -110), "validity": 400,
         "bank": "HDFC Bank", "bank_account_no": "50200012345678", "iban": "",
         "bank_guarantee_number": "HDFC/ABG/2026/0841", "name_of_beneficiary": "Sahyadri Steels Ltd (DEMO)",
         "margin_money": 202650, "charges": 24318, "company": COMPANY, "account": bank},
        submit=True)
    ins({"doctype": "Bank Guarantee", "bg_type": "Providing", "reference_doctype": "Sales Order",
         "reference_docname": so, "customer": "Sahyadri Steels Ltd (DEMO)", "project": "PROJ-0001",
         "amount": 2026500, "start_date": add_days(TODAY, -20), "validity": 550,
         "bank": "HDFC Bank", "bank_account_no": "50200012345678",
         "bank_guarantee_number": "HDFC/PBG/2026/0992", "name_of_beneficiary": "Sahyadri Steels Ltd (DEMO)",
         "margin_money": 202650, "charges": 26344, "company": COMPANY, "account": bank},
        submit=True)
    return "ABG + PBG registered with expiry dates"


def quality_inspections():
    if frappe.db.count("Quality Inspection"):
        return "already exists"
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
                {"specification": "Overall length", "status": "Accepted", "reading_value": "as per drawing"},
                {"specification": "Material grade / MTC", "status": "Accepted", "reading_value": "conforms"},
            ],
        }, submit=True)
        made += 1
    return "%d incoming inspections" % made


def spares_stock_and_dispatch():
    """Receive spares, then deliver them with a packing slip (dispatch lot demo)."""
    if frappe.db.count("Delivery Note"):
        return "delivery note already exists"
    if not frappe.db.exists("Stock Entry", {"remarks": ("like", "Spares stock%"), "docstatus": 1}):
        ins({"doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": COMPANY,
             "posting_date": add_days(TODAY, -12), "set_posting_time": 1,
             "remarks": "Spares stock received from vendor for Konark order",
             "items": [
                 {"item_code": "SPR-MOULD-TUBE", "qty": 8, "t_warehouse": "Stores - " + ABBR,
                  "basic_rate": 168000},
                 {"item_code": "SPR-ROLL", "qty": 2, "t_warehouse": "Stores - " + ABBR,
                  "basic_rate": 56000},
             ]}, submit=True)

    dn = frappe.new_doc("Delivery Note")
    dn.customer = "Konark Alloys Pvt Ltd (DEMO)"
    dn.company = COMPANY
    dn.set_posting_time = 1
    dn.posting_date = add_days(TODAY, -3)
    dn.customer_address = frappe.db.get_value(
        "Address", {"address_title": "Konark Alloys Pvt Ltd (DEMO)"}, "name")
    dn.shipping_address_name = dn.customer_address
    dn.company_address = frappe.db.get_value("Address", {"is_your_company_address": 1}, "name")
    dn.mode_of_transport = "Road"
    dn.gst_transporter_id = frappe.db.get_value("Supplier", "Vidarbha Heavy Transport (DEMO)", "gstin")
    dn.transporter_name = "Vidarbha Heavy Transport (DEMO)"
    dn.lr_no = "VHT/2026/9013"
    dn.lr_date = add_days(TODAY, -3)
    dn.vehicle_no = "MH12AB1234"
    dn.append("items", {"item_code": "SPR-MOULD-TUBE", "qty": 8, "rate": 192000,
                        "warehouse": "Stores - " + ABBR})
    dn.flags.ignore_permissions = True
    dn.insert()
    dn.submit()

    ps = frappe.new_doc("Packing Slip")
    ps.delivery_note = dn.name
    ps.from_case_no = 1
    ps.to_case_no = 2
    ps.flags.ignore_permissions = True
    try:
        ps.insert()
        ps.submit()
        packing = ps.name
    except Exception as e:
        packing = "packing slip skipped: " + repr(e)[:120]
    return "%s (spares dispatch with transporter details) + %s" % (dn.name, packing)


def cheque_template():
    if frappe.db.count("Cheque Print Template"):
        return "already exists"
    ins({"doctype": "Cheque Print Template", "bank_name": "HDFC Bank", "cheque_size": "Regular",
         "starting_position_from_top_edge": 0, "cheque_width": 20, "cheque_height": 9,
         "scanned_cheque": "", "is_account_payable": 1,
         "acc_pay_dist_from_top_edge": 1, "acc_pay_dist_from_left_edge": 9,
         "message_to_show": "Account Pay Only",
         "date_dist_from_top_edge": 1, "date_dist_from_left_edge": 15,
         "payer_name_from_top_edge": 2.5, "payer_name_from_left_edge": 3,
         "amt_in_words_from_top_edge": 3.5, "amt_in_words_from_left_edge": 4,
         "amt_in_word_width": 15, "amt_in_words_line_spacing": 0.5,
         "amt_in_figures_from_top_edge": 3.5, "amt_in_figures_from_left_edge": 16,
         "signatory_from_top_edge": 6, "signatory_from_left_edge": 15})
    return "HDFC cheque layout"


def fixed_assets():
    if frappe.db.count("Asset"):
        return "already exists"
    fa_acc = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Plant and Machinery%"), "is_group": 0}, "name") \
        or frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Fixed Asset", "is_group": 0}, "name")
    acc_dep = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Accumulated Depreciation%"), "is_group": 0}, "name")
    dep_exp = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Depreciation%"), "is_group": 0, "root_type": "Expense"}, "name")
    if not (fa_acc and acc_dep and dep_exp):
        return "asset accounts missing (fa=%s acc=%s exp=%s)" % (fa_acc, acc_dep, dep_exp)

    cat = "Plant & Machinery (Demo)"
    if not frappe.db.exists("Asset Category", cat):
        ins({"doctype": "Asset Category", "asset_category_name": cat,
             "enable_cwip_accounting": 0,
             "accounts": [{"company_name": COMPANY, "fixed_asset_account": fa_acc,
                           "accumulated_depreciation_account": acc_dep,
                           "depreciation_expense_account": dep_exp}],
             "finance_books": [{"depreciation_method": "Straight Line",
                                "total_number_of_depreciations": 60, "frequency_of_depreciation": 1}]})
    made = []
    for code, name, value, months_ago in [
        ("FA-CAD-WS", "CAD workstation - engineering", 185000, 14),
        ("FA-WELD-SET", "Welding & testing equipment", 420000, 26),
    ]:
        if not frappe.db.exists("Item", code):
            ins({"doctype": "Item", "item_code": code, "item_name": name, "item_group": "All Item Groups",
                 "stock_uom": "Nos", "is_fixed_asset": 1, "is_stock_item": 0, "asset_category": cat,
                 "item_defaults": [{"company": COMPANY}]})
        a = ins({
            "doctype": "Asset", "asset_name": name, "item_code": code, "asset_category": cat,
            "company": COMPANY, "is_existing_asset": 1, "asset_quantity": 1,
            "purchase_date": add_months(TODAY, -months_ago),
            "available_for_use_date": add_months(TODAY, -months_ago),
            "gross_purchase_amount": value, "opening_accumulated_depreciation": 0,
            "calculate_depreciation": 1,
            "finance_books": [{"depreciation_method": "Straight Line",
                               "total_number_of_depreciations": 60,
                               "frequency_of_depreciation": 1,
                               "depreciation_start_date": add_months(TODAY, -months_ago + 1)}],
        })
        try:
            a.submit()
        except Exception as e:
            log("asset submit %s: %s" % (a.name, repr(e)[:150]))
        made.append(a.name)
    return "assets: " + ", ".join(made)


def alerts():
    made = []
    if not frappe.db.exists("Notification", "MSCAST BG expiry alert"):
        ins({"doctype": "Notification", "name": "MSCAST BG expiry alert", "subject":
             "Bank guarantee {{ doc.bank_guarantee_number }} expires in 30 days",
             "document_type": "Bank Guarantee", "event": "Days Before", "date_changed": "end_date",
             "days_in_advance": 30, "enabled": 1, "channel": "Email",
             "message": "Bank guarantee {{ doc.bank_guarantee_number }} for {{ doc.customer }} "
                        "({{ doc.amount }}) expires on {{ doc.end_date }}. Arrange extension or release.",
             "recipients": [{"receiver_by_role": "Accounts Manager"}]})
        made.append("BG expiry notification")
    if not frappe.db.exists("Notification", "MSCAST PO over PCC"):
        ins({"doctype": "Notification", "name": "MSCAST PO over PCC", "subject":
             "Purchase Order {{ doc.name }} exceeds the PCC budget",
             "document_type": "Purchase Order", "event": "Submit", "enabled": 1, "channel": "Email",
             "condition": "doc.pcc_budget_amount and doc.grand_total > doc.pcc_budget_amount",
             "message": "PO {{ doc.name }} to {{ doc.supplier }} is {{ doc.grand_total }} against a "
                        "PCC budget of {{ doc.pcc_budget_amount }}. Justification: {{ doc.pcc_variance_note }}",
             "recipients": [{"receiver_by_role": "Purchase Manager"}]})
        made.append("PO vs PCC notification")

    if not frappe.db.exists("Auto Email Report", "MSCAST Project MIS - weekly"):
        ins({"doctype": "Auto Email Report", "name": "MSCAST Project MIS - weekly",
             "report": "MSCAST Project MIS", "user": "Administrator", "report_type": "Query Report",
             "email_to": "director@mcast.co.in", "format": "HTML", "frequency": "Weekly",
             "day_of_week": "Monday", "enabled": 0, "no_of_rows": 100,
             "description": "Weekly project MIS to management (disabled in the POC - no mail server)"})
        made.append("Auto Email Report (weekly MIS)")
    if not frappe.db.exists("Auto Email Report", "MSCAST Dispatch schedule - weekly"):
        ins({"doctype": "Auto Email Report", "name": "MSCAST Dispatch schedule - weekly",
             "report": "MSCAST Dispatch Schedule", "user": "Administrator", "report_type": "Query Report",
             "email_to": "projects@mcast.co.in", "format": "XLSX", "frequency": "Weekly",
             "day_of_week": "Monday", "enabled": 0, "no_of_rows": 100,
             "description": "Weekly dispatch schedule vs contract (disabled in the POC)"})
        made.append("Auto Email Report (dispatch)")

    if not frappe.db.exists("Email Digest", "MSCAST daily digest"):
        ins({"doctype": "Email Digest", "name": "MSCAST daily digest", "company": COMPANY,
             "frequency": "Daily", "enabled": 0,
             "recipients": [{"recipient": "director@mcast.co.in"}],
             "income": 1, "expenses_booked": 1, "bank_balance": 1, "credit_balance": 1,
             "invoiced_amount": 1, "payables": 1, "new_quotations": 1, "pending_quotations": 1,
             "sales_orders_to_bill": 1, "sales_orders_to_deliver": 1, "purchase_orders_to_receive": 1,
             "open_tickets": 0, "open_todos": 1, "add_quote": 0})
        made.append("Email Digest (daily COO/CFO summary)")
    return ", ".join(made) or "(all existed)"


def scorecard():
    if frappe.db.count("Supplier Scorecard"):
        return "already exists"
    ins({
        "doctype": "Supplier Scorecard", "supplier": "Pushkar Fabricators (DEMO)",
        "period": "Per Month", "weighting_function": "{total_score} * max( 0, min ( 1 , (12 - {period_number}) / 12) )",
        "criteria": [{"criteria_name": "Delivery", "weight": 60},
                     {"criteria_name": "Quality", "weight": 40}]
        if frappe.db.exists("Supplier Scorecard Criteria", "Delivery") else [],
        "standings": [{"standing_name": "Excellent", "min_grade": 80, "max_grade": 100,
                       "warn_rfqs": 0, "warn_pos": 0, "prevent_rfqs": 0, "prevent_pos": 0,
                       "notify_supplier": 0, "notify_employee": 0, "employee_link": None},
                      {"standing_name": "Average", "min_grade": 50, "max_grade": 80},
                      {"standing_name": "Poor", "min_grade": 0, "max_grade": 50, "warn_pos": 1}],
    })
    return "scorecard for Pushkar Fabricators"


def warranty():
    if frappe.db.count("Warranty Claim"):
        return "already exists"
    ins({"doctype": "Warranty Claim", "customer": "Sahyadri Steels Ltd (DEMO)",
         "company": COMPANY, "complaint_date": add_days(TODAY, -2), "status": "Open",
         "item_code": "SPR-ROLL", "complaint": "Withdrawal roll bearing noise reported after 400 heats; "
                                               "site visit planned with spare bearing set.",
         "customer_address": frappe.db.get_value("Address", {"address_title": "Sahyadri Steels Ltd (DEMO)"}, "name")})
    return "one open warranty claim"


def run():
    step("MSME supplier data", msme)
    step("bank guarantees", bank_guarantees)
    step("quality inspections", quality_inspections)
    step("spares dispatch (DN + packing slip)", spares_stock_and_dispatch)
    step("cheque print template", cheque_template)
    step("fixed assets", fixed_assets)
    step("alerts & scheduled reports", alerts)
    step("supplier scorecard", scorecard)
    step("warranty claim", warranty)
    log("DONE")


run()
