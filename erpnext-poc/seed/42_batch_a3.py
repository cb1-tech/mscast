"""MSCAST POC - 41: BATCH A fixes - bank entry references, TDS, dunning."""
import frappe
from frappe.utils import add_days, nowdate, flt

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[A3] " + m, flush=True)


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


def cc():
    return frappe.db.get_value("Cost Center", {"company": COMPANY, "is_group": 0}, "name")


def je(voucher_type, date, remark, rows, ref=None):
    d = {"doctype": "Journal Entry", "voucher_type": voucher_type, "company": COMPANY,
         "posting_date": date, "user_remark": remark, "accounts": rows}
    if voucher_type == "Bank Entry":
        d["cheque_no"] = ref or "NEFT/2026/0001"
        d["cheque_date"] = date
    return ins(d, submit=True)


def payments():
    if frappe.db.count("Journal Entry"):
        return "journal entries already exist"
    bank = acc(account_type="Bank"); petty = acc(account_name="Petty Cash")
    util = acc(account_name=("like", "%Electricity%")) or acc(account_name=("like", "%Utility%")) \
        or acc(account_name=("like", "%Miscellaneous Expenses%"))
    tel = acc(account_name=("like", "%Telephone%")) or util
    out = []
    out.append(je("Bank Entry", add_days(TODAY, -6), "MSEDCL electricity bill - office",
                  [{"account": util, "debit_in_account_currency": 18650, "cost_center": cc()},
                   {"account": bank, "credit_in_account_currency": 18650, "cost_center": cc()}],
                  "NEFT/MSEDCL/7741").name)
    out.append(je("Bank Entry", add_days(TODAY, -10), "Cash drawn for petty cash imprest",
                  [{"account": petty, "debit_in_account_currency": 25000, "cost_center": cc()},
                   {"account": bank, "credit_in_account_currency": 25000, "cost_center": cc()}],
                  "SELF/CHQ/000231").name)
    out.append(je("Cash Entry", add_days(TODAY, -4),
                  "Petty cash: courier to vendors, stationery, local conveyance",
                  [{"account": tel, "debit_in_account_currency": 4380, "cost_center": cc()},
                   {"account": petty, "credit_in_account_currency": 4380, "cost_center": cc()}]).name)
    out.append(je("Bank Entry", add_days(TODAY, -15),
                  "Foreign travel - Sharjah customer visit (Gulf Aluminium enquiry)",
                  [{"account": acc(account_name=("like", "%Travel%")) or util,
                    "debit_in_account_currency": 214500, "cost_center": cc()},
                   {"account": bank, "credit_in_account_currency": 214500, "cost_center": cc()}],
                  "CARD/HDFC/9921").name)
    out.append(je("Bank Entry", add_days(TODAY, -22),
                  "Marine + erection all-risk insurance premium for the CCM project",
                  [{"account": acc(account_name=("like", "%Insurance%")) or util,
                    "debit_in_account_currency": 96400, "cost_center": cc()},
                   {"account": bank, "credit_in_account_currency": 96400, "cost_center": cc()}],
                  "NEFT/INS/4410").name)
    out.append(je("Journal Entry", add_days(TODAY, -5),
                  "Cargo agency invoice - ODC movement Pune to Nagpur site",
                  [{"account": acc(account_name=("like", "%Freight%")) or util,
                    "debit_in_account_currency": 68000, "cost_center": cc()},
                   {"account": acc(account_type="Payable"), "credit_in_account_currency": 68000,
                    "party_type": "Supplier", "party": "Vidarbha Heavy Transport (DEMO)",
                    "cost_center": cc()}]).name)
    return ", ".join(out)


def tds():
    cat = "TDS - 194C - Contractor - 2%"
    if not frappe.db.exists("Tax Withholding Category", cat):
        tds_acc = acc(account_name=("like", "%TDS%"), root_type="Liability") or acc(account_type="Payable")
        ins({"doctype": "Tax Withholding Category", "name": cat, "category_name": cat,
             "rates": [{"from_date": "2026-04-01", "to_date": "2027-03-31", "tax_withholding_rate": 2,
                        "single_threshold": 30000, "cumulative_threshold": 100000}],
             "accounts": [{"company": COMPANY, "account": tds_acc}]})
    frappe.db.set_value("Supplier", "Pushkar Fabricators (DEMO)", "tax_withholding_category", cat)
    frappe.db.commit()
    if frappe.db.exists("Purchase Invoice", {"supplier": "Pushkar Fabricators (DEMO)", "docstatus": 1}):
        return "fabrication bill already booked"
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = "Pushkar Fabricators (DEMO)"
    pi.company = COMPANY
    pi.set_posting_time = 1
    pi.posting_date = add_days(TODAY, -2)
    pi.bill_no = "PF/INV/2026/231"
    pi.bill_date = add_days(TODAY, -2)
    pi.apply_tds = 1
    pi.tax_withholding_category = cat
    pi.company_address = frappe.db.get_value("Address", {"is_your_company_address": 1}, "name")
    pi.supplier_address = frappe.db.get_value("Address", {"address_title": "Pushkar Fabricators (DEMO)"}, "name")
    pi.append("items", {"item_code": "FAB-SPRAY-CHAMBER", "qty": 2, "rate": 258000,
                        "warehouse": "Vendor WIP - " + ABBR,
                        "project": frappe.db.get_value("Project", {"project_name": ("like", "CCM 2-Strand%")}, "name")})
    tmpl = "Input GST In-state - " + ABBR
    pi.taxes_and_charges = tmpl
    for t in frappe.get_doc("Purchase Taxes and Charges Template", tmpl).taxes:
        pi.append("taxes", {"charge_type": t.charge_type, "account_head": t.account_head,
                            "category": t.category, "add_deduct_tax": t.add_deduct_tax,
                            "description": t.description, "rate": t.rate, "cost_center": t.cost_center})
    pi.remarks = "Spray chamber fabrication - TDS 194C @ 2% deducted"
    pi.flags.ignore_permissions = True
    pi.insert()
    pi.submit()
    tds_amt = sum(t.tax_amount for t in pi.taxes if t.add_deduct_tax == "Deduct")
    return "%s grand total %s, TDS deducted %s" % (pi.name, pi.grand_total, tds_amt)


def dunning_type():
    existing = frappe.db.get_value("Dunning Type", {}, "name")
    if existing:
        return existing
    d = frappe.get_doc({
        "doctype": "Dunning Type", "dunning_type": "First reminder", "company": COMPANY,
        "is_default": 1, "dunning_fee": 0, "rate_of_interest": 12,
        "income_account": acc(root_type="Income"), "cost_center": cc(),
        "dunning_letter_text": [{"language": "en",
                                 "body_text": "Please find attached the outstanding invoice for your kind attention.",
                                 "closing_text": "We request settlement at the earliest."}],
    })
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    d.insert()
    return d.name


def dunning(dtype):
    if frappe.db.count("Dunning"):
        return "already exists"
    inv = frappe.db.get_value("Sales Invoice", {"docstatus": 1, "outstanding_amount": (">", 0),
                                               "is_return": 0}, "name", order_by="posting_date asc")
    if not inv:
        return "no outstanding invoice"
    si = frappe.get_doc("Sales Invoice", inv)
    d = frappe.new_doc("Dunning")
    d.company = COMPANY
    d.posting_date = TODAY
    d.customer = si.customer
    d.dunning_type = dtype
    d.rate_of_interest = 0
    d.dunning_fee = 0
    d.append("overdue_payments", {"sales_invoice": si.name, "due_date": si.due_date,
                                  "outstanding": si.outstanding_amount, "interest": 0,
                                  "overdue_days": 5, "payment_amount": si.grand_total,
                                  "paid_amount": 0})
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    d.insert()
    return "%s for %s (%s outstanding)" % (d.name, si.customer, si.outstanding_amount)


def payment_request():
    if frappe.db.count("Payment Request"):
        return "already exists"
    so = frappe.db.get_value("Sales Order", {"docstatus": 1, "customer": ("like", "Deccan%")}, "name")
    sod = frappe.get_doc("Sales Order", so)
    pr = frappe.new_doc("Payment Request")
    pr.payment_request_type = "Inward"
    pr.transaction_date = TODAY
    pr.reference_doctype = "Sales Order"
    pr.reference_name = so
    pr.party_type = "Customer"
    pr.party = sod.customer
    pr.grand_total = flt(sod.grand_total) * 0.3
    pr.currency = sod.currency
    pr.company = COMPANY
    pr.subject = "Advance (30 percent) against Sales Order " + so
    pr.flags.ignore_permissions = True
    pr.flags.ignore_mandatory = True
    pr.insert()
    return "%s (%s)" % (pr.name, pr.grand_total)


def run2():
    dt = step("dunning type", dunning_type)
    if isinstance(dt, str):
        step("payment reminder (dunning)", dunning, dt)
    step("advance payment request", payment_request)
    log("BATCH A3 DONE")


run2()
