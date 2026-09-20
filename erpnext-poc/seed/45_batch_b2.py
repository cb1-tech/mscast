"""MSCAST POC - 45: BATCH B fixes - RFQ uom, intangible asset, CWIP via purchase invoice, share capital."""
import frappe
from frappe.utils import add_days, add_months, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[B2] " + m, flush=True)


def step(name, fn, *a, **kw):
    try:
        out = fn(*a, **kw)
        frappe.db.commit()
        log("OK   " + name + ((" -> " + str(out)) if out else ""))
        return out or True
    except Exception as e:
        frappe.db.rollback()
        log("FAIL " + name + " :: " + repr(e)[:320])
        return None


def ins(doc, submit=False):
    d = frappe.get_doc(doc)
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    d.insert(ignore_if_duplicate=True)
    if submit:
        d.submit()
    return d


def acc(**f):
    f.setdefault("company", COMPANY)
    f.setdefault("is_group", 0)
    return frappe.db.get_value("Account", f, "name")


# ------------------------------------------------------------------ P-02
def rfq():
    if frappe.db.count("Request for Quotation"):
        return "already exists"
    mr = frappe.db.get_value("Material Request", {"docstatus": 1}, "name")
    mrd = frappe.get_doc("Material Request", mr)
    r = frappe.new_doc("Request for Quotation")
    r.company = COMPANY
    r.transaction_date = add_days(TODAY, -55)
    r.schedule_date = add_days(TODAY, -35)
    r.message_for_supplier = ("Please quote your best techno-commercial offer as per the attached "
                              "drawings and specifications. Indicate delivery period, payment terms "
                              "and any deviation from the specification.")
    for sup in ["Suvarna Copper Moulds (DEMO)", "Kalyani Gears & Drives (DEMO)",
                "Shivneri Machining Works (DEMO)"]:
        if frappe.db.exists("Supplier", sup):
            r.append("suppliers", {"supplier": sup})
    for it in mrd.items:
        uom = frappe.db.get_value("Item", it.item_code, "stock_uom")
        r.append("items", {"item_code": it.item_code, "item_name": it.item_name,
                           "description": it.description, "qty": it.qty,
                           "uom": uom, "stock_uom": uom, "conversion_factor": 1,
                           "warehouse": it.warehouse, "schedule_date": add_days(TODAY, -35),
                           "material_request": mr, "material_request_item": it.name,
                           "project": it.project})
    r.flags.ignore_permissions = True
    r.insert()
    r.submit()
    return "%s to %d suppliers for %d items" % (r.name, len(r.suppliers), len(r.items))


# ------------------------------------------------------------------ AC-14 / AC-15 masters
def categories_and_items():
    made = []
    fa_soft = acc(account_name=("like", "%Software%")) or acc(account_name=("like", "%Plant and Machinery%"))
    acc_dep = acc(account_name=("like", "%Accumulated Depreciation%"))
    dep_exp = acc(account_name=("like", "%Depreciation%"), root_type="Expense")
    cwip_acc = acc(account_name=("like", "%Capital Work in Progress%")) or acc(account_name=("like", "%CWIP%"))
    if not cwip_acc:
        parent = frappe.db.get_value("Account", {"company": COMPANY, "is_group": 1,
                                                 "account_name": ("like", "%Fixed Asset%")}, "name")
        cwip_acc = ins({"doctype": "Account", "account_name": "Capital Work in Progress",
                        "parent_account": parent, "company": COMPANY, "root_type": "Asset",
                        "account_type": "Capital Work in Progress"}).name
        made.append("CWIP account")
    frappe.db.set_value("Company", COMPANY, "capital_work_in_progress_account", cwip_acc)

    cat = "Software (Intangible)"
    if not frappe.db.exists("Asset Category", cat):
        ins({"doctype": "Asset Category", "asset_category_name": cat, "enable_cwip_accounting": 0,
             "accounts": [{"company_name": COMPANY, "fixed_asset_account": fa_soft,
                           "accumulated_depreciation_account": acc_dep,
                           "depreciation_expense_account": dep_exp,
                           "capital_work_in_progress_account": cwip_acc}],
             "finance_books": [{"depreciation_method": "Straight Line",
                                "total_number_of_depreciations": 36, "frequency_of_depreciation": 1}]})
        made.append(cat)
    cat2 = "Plant under construction (CWIP)"
    if not frappe.db.exists("Asset Category", cat2):
        ins({"doctype": "Asset Category", "asset_category_name": cat2, "enable_cwip_accounting": 1,
             "accounts": [{"company_name": COMPANY,
                           "fixed_asset_account": acc(account_name=("like", "%Plant and Machinery%")) or fa_soft,
                           "accumulated_depreciation_account": acc_dep,
                           "depreciation_expense_account": dep_exp,
                           "capital_work_in_progress_account": cwip_acc}],
             "finance_books": [{"depreciation_method": "Straight Line",
                                "total_number_of_depreciations": 120, "frequency_of_depreciation": 1}]})
        made.append(cat2)

    hsn = frappe.db.get_value("GST HSN Code", {"name": ("like", "8523%")}, "name") \
        or frappe.db.get_value("GST HSN Code", {}, "name")
    for code, nm, cate in [("FA-ERP-SW", "ERP software licence (intangible)", cat),
                           ("FA-TEST-BENCH", "Hydraulic test bench under construction", cat2)]:
        if not frappe.db.exists("Item", code):
            ins({"doctype": "Item", "item_code": code, "item_name": nm,
                 "item_group": "All Item Groups", "stock_uom": "Nos", "is_fixed_asset": 1,
                 "is_stock_item": 0, "asset_category": cate, "gst_hsn_code": hsn,
                 "item_defaults": [{"company": COMPANY}]})
            made.append(code)
    return ", ".join(made) or "(already in place)"


def intangible_asset():
    if frappe.db.exists("Asset", {"item_code": "FA-ERP-SW"}):
        return "already exists"
    loc = frappe.db.get_value("Location", {}, "name")
    a = ins({"doctype": "Asset", "asset_name": "ERP software licence", "item_code": "FA-ERP-SW",
             "asset_category": "Software (Intangible)", "company": COMPANY, "is_existing_asset": 1,
             "asset_quantity": 1, "location": loc,
             "purchase_date": add_months(TODAY, -3), "available_for_use_date": add_months(TODAY, -3),
             "gross_purchase_amount": 240000, "purchase_amount": 240000,
             "net_purchase_amount": 240000, "opening_accumulated_depreciation": 0,
             "calculate_depreciation": 1,
             "finance_books": [{"depreciation_method": "Straight Line",
                                "total_number_of_depreciations": 36,
                                "frequency_of_depreciation": 1,
                                "depreciation_start_date": add_months(TODAY, -2)}]})
    a.submit()
    return "%s amortised over 36 months" % a.name


def cwip_asset_via_pi():
    if frappe.db.exists("Asset", {"item_code": "FA-TEST-BENCH"}):
        return "already exists"
    loc = frappe.db.get_value("Location", {}, "name")
    sup = "Shivneri Machining Works (DEMO)" if frappe.db.exists("Supplier", "Shivneri Machining Works (DEMO)") \
        else frappe.db.get_value("Supplier", {}, "name")
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = sup
    pi.company = COMPANY
    pi.set_posting_time = 1
    pi.posting_date = add_days(TODAY, -30)
    pi.bill_no = "SMW/CAP/2026/08"
    pi.bill_date = add_days(TODAY, -30)
    pi.update_stock = 0
    pi.append("items", {"item_code": "FA-TEST-BENCH", "qty": 1, "rate": 780000,
                        "asset_location": loc, "item_name": "Hydraulic test bench under construction",
                        "description": "Fabrication and assembly of 200 bar hydraulic test bench - stage 1"})
    pi.remarks = "Capital work in progress - hydraulic test bench, stage 1 billing"
    pi.flags.ignore_permissions = True
    pi.insert()
    pi.submit()
    frappe.db.commit()
    assets = frappe.get_all("Asset", filters={"purchase_invoice": pi.name}, pluck="name")
    for an in assets:
        try:
            a = frappe.get_doc("Asset", an)
            a.asset_name = "Hydraulic test bench (under construction)"
            a.location = loc
            a.available_for_use_date = add_months(TODAY, 3)
            a.calculate_depreciation = 0
            a.flags.ignore_permissions = True
            a.save()
        except Exception as e:
            log("  asset tidy skipped: " + repr(e)[:150])
    return "%s (Rs 7,80,000 to CWIP) -> asset %s" % (pi.name, assets or "none auto-created")


# ------------------------------------------------------------------ AC-08
def share_capital():
    made = []
    if not frappe.db.count("Shareholder"):
        for title, folk in [("Mustaque Ahmed N. Chandankeri", 7000),
                            ("Aiqaz M. Chandankeri", 2000),
                            ("Zameer Alam Chandankeri", 1000)]:
            ins({"doctype": "Shareholder", "title": title, "company": COMPANY,
                 "is_company": 0, "folio_no": "FOLIO-%04d" % folk})
        made.append("3 shareholders")
    if not frappe.db.exists("Share Type", "Equity"):
        ins({"doctype": "Share Type", "title": "Equity"})
    frappe.db.commit()
    if not frappe.db.count("Share Transfer"):
        eq = acc(root_type="Equity") or acc(account_name=("like", "%Capital%"), root_type="Equity")
        bank = acc(account_type="Bank")
        holders = frappe.get_all("Shareholder", pluck="name")
        start = 1
        for holder, qty in zip(holders, [7000, 2000, 1000]):
            ins({"doctype": "Share Transfer", "transfer_type": "Issue", "date": "2026-04-01",
                 "to_shareholder": holder, "share_type": "Equity",
                 "from_no": start, "to_no": start + qty - 1, "no_of_shares": qty,
                 "rate": 10, "amount": qty * 10, "company": COMPANY,
                 "equity_or_liability_account": eq, "asset_account": bank}, submit=True)
            start += qty
        made.append("10,000 equity shares of Rs 10 issued (paid-up Rs 1,00,000)")
    return "; ".join(made) or "(already exists)"


def run():
    step("request for quotation", rfq)
    step("asset categories + fixed-asset items", categories_and_items)
    step("intangible asset (software)", intangible_asset)
    step("CWIP asset via purchase invoice", cwip_asset_via_pi)
    step("share capital records", share_capital)
    frappe.clear_cache()
    log("BATCH B2 DONE")


run()
