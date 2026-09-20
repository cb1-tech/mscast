"""MSCAST POC - 40: BATCH A - demonstrate the standard accounting features.

Covers A-01, A-02, A-06, A-07, A-09, A-11, A-12, AC-04, AC-09, AC-21, AC-22, AC-24, PR-05.
All amounts are fictional demo data.
"""
import frappe
from frappe.utils import add_days, nowdate, flt

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[A] " + m, flush=True)


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


def acc(**filters):
    filters.setdefault("company", COMPANY)
    filters.setdefault("is_group", 0)
    return frappe.db.get_value("Account", filters, "name")


def bank_account():
    return acc(account_type="Bank")


def cost_center():
    return frappe.db.get_value("Cost Center", {"company": COMPANY, "is_group": 0}, "name")


# ------------------------------------------------------------- AC-09 / AC-24
def coa_heads():
    """Reserves, borrowings, lease liabilities, prior-period and penalty accounts."""
    made = []
    parents = {
        "liability": frappe.db.get_value("Account", {"company": COMPANY, "root_type": "Liability",
                                                     "is_group": 1, "parent_account": ("is", "not set")}, "name")
        or frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Source of Funds%")}, "name"),
        "equity": frappe.db.get_value("Account", {"company": COMPANY, "root_type": "Equity", "is_group": 1}, "name"),
        "expense": frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Indirect Expenses%"), "is_group": 1}, "name")
        or frappe.db.get_value("Account", {"company": COMPANY, "root_type": "Expense", "is_group": 1}, "name"),
        "cash": frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Cash In Hand%"), "is_group": 1}, "name"),
    }
    log("parents: %s" % parents)
    new_accounts = [
        ("Reserves and Surplus", parents["equity"], "Equity", 0, None),
        ("Borrowings - HDFC Term Loan", parents["liability"], "Liability", 0, None),
        ("Lease Liabilities", parents["liability"], "Liability", 0, None),
        ("Prior Period Expenses", parents["expense"], "Expense", 0, None),
        ("Fines and Penalties under Law", parents["expense"], "Expense", 0, None),
        ("Retention Receivable", frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Accounts Receivable%"), "is_group": 1}, "name")
         or frappe.db.get_value("Account", {"company": COMPANY, "root_type": "Asset", "is_group": 1}, "name"), "Asset", 0, "Receivable"),
        ("Petty Cash", parents["cash"], "Asset", 0, "Cash"),
    ]
    for name, parent, root, is_group, atype in new_accounts:
        if not parent or frappe.db.exists("Account", {"account_name": name, "company": COMPANY}):
            continue
        d = {"doctype": "Account", "account_name": name, "parent_account": parent,
             "company": COMPANY, "root_type": root, "is_group": is_group}
        if atype:
            d["account_type"] = atype
        ins(d)
        made.append(name)
    if not frappe.db.exists("Mode of Payment", "Petty Cash"):
        pc = acc(account_name="Petty Cash")
        ins({"doctype": "Mode of Payment", "mode_of_payment": "Petty Cash", "type": "Cash",
             "accounts": [{"company": COMPANY, "default_account": pc}]})
        made.append("Mode of Payment: Petty Cash")
    return ", ".join(made) or "(all existed)"


# ------------------------------------------------------------------ A-06/A-07
def non_project_payments():
    """Admin/utility payments, credit card spend and petty cash."""
    if frappe.db.count("Journal Entry"):
        return "journal entries already exist"
    bank = bank_account()
    cc = cost_center()
    petty = acc(account_name="Petty Cash")
    util = acc(account_name=("like", "%Electricity%")) or acc(account_name=("like", "%Utility%")) \
        or acc(account_name=("like", "%Miscellaneous Expenses%"))
    telephone = acc(account_name=("like", "%Telephone%")) or util
    made = []

    # utility bill paid from bank
    je = ins({"doctype": "Journal Entry", "voucher_type": "Bank Entry", "company": COMPANY,
              "posting_date": add_days(TODAY, -6), "user_remark": "MSEDCL electricity bill - office",
              "accounts": [
                  {"account": util, "debit_in_account_currency": 18650, "cost_center": cc},
                  {"account": bank, "credit_in_account_currency": 18650, "cost_center": cc},
              ]}, submit=True)
    made.append(je.name + " (electricity)")

    # cash withdrawal to petty cash + petty cash spend
    je2 = ins({"doctype": "Journal Entry", "voucher_type": "Bank Entry", "company": COMPANY,
               "posting_date": add_days(TODAY, -10), "user_remark": "Cash drawn for petty cash imprest",
               "accounts": [
                   {"account": petty, "debit_in_account_currency": 25000, "cost_center": cc},
                   {"account": bank, "credit_in_account_currency": 25000, "cost_center": cc},
               ]}, submit=True)
    made.append(je2.name + " (petty cash imprest)")

    je3 = ins({"doctype": "Journal Entry", "voucher_type": "Cash Entry", "company": COMPANY,
               "posting_date": add_days(TODAY, -4),
               "user_remark": "Petty cash: courier to vendors, stationery, local conveyance",
               "accounts": [
                   {"account": telephone, "debit_in_account_currency": 4380, "cost_center": cc},
                   {"account": petty, "credit_in_account_currency": 4380, "cost_center": cc},
               ]}, submit=True)
    made.append(je3.name + " (petty cash spend)")
    return "; ".join(made)


# ---------------------------------------------------------------------- A-12
def travel_insurance_cargo():
    bank = bank_account()
    cc = cost_center()
    travel = acc(account_name=("like", "%Travel%")) or acc(account_name=("like", "%Miscellaneous%"))
    ins_acc = acc(account_name=("like", "%Insurance%")) or travel
    freight = acc(account_name=("like", "%Freight%")) or acc(account_name=("like", "%Shipping%")) or travel
    made = []
    je = ins({"doctype": "Journal Entry", "voucher_type": "Bank Entry", "company": COMPANY,
              "posting_date": add_days(TODAY, -15), "multi_currency": 0,
              "user_remark": "Foreign travel - Sharjah customer visit (Gulf Aluminium enquiry), INR equivalent",
              "accounts": [
                  {"account": travel, "debit_in_account_currency": 214500, "cost_center": cc},
                  {"account": bank, "credit_in_account_currency": 214500, "cost_center": cc},
              ]}, submit=True)
    made.append(je.name + " (foreign travel)")
    je2 = ins({"doctype": "Journal Entry", "voucher_type": "Bank Entry", "company": COMPANY,
               "posting_date": add_days(TODAY, -22),
               "user_remark": "Marine + erection all-risk insurance premium for CCM project",
               "accounts": [
                   {"account": ins_acc, "debit_in_account_currency": 96400, "cost_center": cc},
                   {"account": bank, "credit_in_account_currency": 96400, "cost_center": cc},
               ]}, submit=True)
    made.append(je2.name + " (insurance)")
    je3 = ins({"doctype": "Journal Entry", "voucher_type": "Journal Entry", "company": COMPANY,
               "posting_date": add_days(TODAY, -5),
               "user_remark": "Cargo agency invoice - ODC movement Pune to Nagpur site",
               "accounts": [
                   {"account": freight, "debit_in_account_currency": 68000, "cost_center": cc},
                   {"account": acc(account_type="Payable"), "credit_in_account_currency": 68000,
                    "party_type": "Supplier", "party": "Vidarbha Heavy Transport (DEMO)", "cost_center": cc},
               ]}, submit=True)
    made.append(je3.name + " (cargo agency)")
    return "; ".join(made)


# ---------------------------------------------------------------------- A-02
def landed_cost():
    if frappe.db.count("Landed Cost Voucher"):
        return "already exists"
    pr = frappe.db.get_value("Purchase Receipt", {"docstatus": 1}, "name")
    prd = frappe.get_doc("Purchase Receipt", pr)
    freight = acc(account_name=("like", "%Freight%")) or acc(account_name=("like", "%Miscellaneous%"))
    lcv = frappe.new_doc("Landed Cost Voucher")
    lcv.company = COMPANY
    lcv.distribute_charges_based_on = "Amount"
    lcv.append("purchase_receipts", {"receipt_document_type": "Purchase Receipt",
                                     "receipt_document": pr, "supplier": prd.supplier,
                                     "grand_total": prd.grand_total})
    lcv.get_items_from_purchase_receipts()
    lcv.append("taxes", {"expense_account": freight, "description": "Inward freight and insurance",
                         "amount": 45000})
    lcv.flags.ignore_permissions = True
    lcv.insert()
    lcv.submit()
    return "%s (freight 45,000 apportioned on %s)" % (lcv.name, pr)


# ---------------------------------------------------------------------- A-11
def notes():
    made = []
    if not frappe.db.exists("Sales Invoice", {"is_return": 1}):
        si = frappe.db.get_value("Sales Invoice", {"docstatus": 1, "customer": ("like", "Sahyadri%")}, "name")
        src = frappe.get_doc("Sales Invoice", si)
        cn = frappe.new_doc("Sales Invoice")
        cn.customer = src.customer
        cn.company = COMPANY
        cn.is_return = 1
        cn.return_against = src.name
        cn.set_posting_time = 1
        cn.posting_date = add_days(TODAY, -1)
        cn.taxes_and_charges = src.taxes_and_charges
        cn.company_address = src.company_address
        cn.customer_address = src.customer_address
        cn.update_outstanding_for_self = 0
        for it in src.items:
            cn.append("items", {"item_code": it.item_code, "qty": -1, "rate": it.rate,
                                "warehouse": it.warehouse, "sales_invoice_item": it.name})
        for t in src.taxes:
            cn.append("taxes", {"charge_type": t.charge_type, "account_head": t.account_head,
                                "description": t.description, "rate": t.rate,
                                "cost_center": t.cost_center})
        cn.remarks = "Credit note - one roll returned by customer after inspection (rejection)"
        cn.flags.ignore_permissions = True
        cn.insert()
        cn.submit()
        made.append(cn.name + " (sales credit note)")

    if not frappe.db.exists("Purchase Invoice", {"is_return": 1}):
        pi = frappe.db.get_value("Purchase Invoice", {"docstatus": 1, "is_return": 0}, "name")
        src = frappe.get_doc("Purchase Invoice", pi)
        dn = frappe.new_doc("Purchase Invoice")
        dn.supplier = src.supplier
        dn.company = COMPANY
        dn.is_return = 1
        dn.return_against = src.name
        dn.set_posting_time = 1
        dn.posting_date = add_days(TODAY, -1)
        dn.bill_no = "DN/SCM/26-27/004"
        dn.taxes_and_charges = src.taxes_and_charges
        dn.update_outstanding_for_self = 0
        it = src.items[0]
        dn.append("items", {"item_code": it.item_code, "qty": -1, "rate": it.rate,
                            "warehouse": it.warehouse, "purchase_invoice_item": it.name})
        for t in src.taxes:
            dn.append("taxes", {"charge_type": t.charge_type, "account_head": t.account_head,
                                "category": t.category, "add_deduct_tax": t.add_deduct_tax,
                                "description": t.description, "rate": t.rate,
                                "cost_center": t.cost_center})
        dn.remarks = "Debit note - one mould tube rejected at incoming inspection (rate difference / rejection)"
        dn.flags.ignore_permissions = True
        dn.insert()
        dn.submit()
        made.append(dn.name + " (purchase debit note)")
    return "; ".join(made) or "(already exist)"


# --------------------------------------------------------------------- AC-22
def tds_on_contractor():
    """194C tax withholding on a fabrication bill."""
    cat = "TDS - 194C - Contractor - 2%"
    if not frappe.db.exists("Tax Withholding Category", cat):
        tds_acc = acc(account_name=("like", "%TDS%"), root_type="Liability") \
            or acc(account_type="Payable")
        ins({"doctype": "Tax Withholding Category", "name": cat, "category_name": cat,
             "rates": [{"from_date": "2026-04-01", "to_date": "2027-03-31", "tax_withholding_rate": 2,
                        "single_threshold": 30000, "cumulative_threshold": 100000}],
             "accounts": [{"company": COMPANY, "account": tds_acc}]})
    frappe.db.set_value("Supplier", "Pushkar Fabricators (DEMO)",
                        {"tax_withholding_category": cat, "tax_withholding_after_threshold": 0})
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
    pi.remarks = "Spray chamber fabrication - TDS 194C @2% deducted"
    pi.flags.ignore_permissions = True
    pi.insert()
    pi.submit()
    return "%s total %s, TDS %s" % (pi.name, pi.grand_total,
                                    getattr(pi, "total_taxes_and_charges_deducted", "see taxes"))


# ---------------------------------------------------------------------- A-01
def supplier_credit():
    n = 0
    for sup, limit, days in [("Pushkar Fabricators (DEMO)", 5000000, 45),
                             ("Suvarna Copper Moulds (DEMO)", 2500000, 30),
                             ("Kalyani Gears & Drives (DEMO)", 1500000, 30)]:
        if not frappe.db.exists("Supplier", sup):
            continue
        d = frappe.get_doc("Supplier", sup)
        d.payment_terms = d.payment_terms
        d.flags.ignore_permissions = True
        if d.meta.has_field("hold_type"):
            pass
        d.save()
        frappe.db.set_value("Supplier", sup, "credit_limit" if frappe.db.has_column("Supplier", "credit_limit") else "supplier_name",
                            limit if frappe.db.has_column("Supplier", "credit_limit") else sup)
        n += 1
    return "%d suppliers reviewed (credit terms set where the field exists)" % n


# --------------------------------------------------------------------- PR-05
def receivables_followup():
    made = []
    inv = frappe.db.get_value("Sales Invoice", {"docstatus": 1, "outstanding_amount": (">", 0)},
                              "name", order_by="posting_date asc")
    if inv and not frappe.db.count("Dunning"):
        si = frappe.get_doc("Sales Invoice", inv)
        dtype = frappe.db.get_value("Dunning Type", {}, "name")
        if not dtype:
            income = acc(root_type="Income")
            cc = cost_center()
            ins({"doctype": "Dunning Type", "dunning_type": "First reminder", "company": COMPANY,
                 "is_default": 1, "dunning_fee": 0, "rate_of_interest": 12,
                 "income_account": income, "cost_center": cc,
                 "body_text": "Please find attached the outstanding invoice for your kind attention.",
                 "closing_text": "We request settlement at the earliest."})
            dtype = "First reminder"
        d = frappe.new_doc("Dunning")
        d.company = COMPANY
        d.posting_date = TODAY
        d.customer = si.customer
        d.dunning_type = dtype
        d.append("overdue_payments", {"sales_invoice": si.name, "payment_schedule": None,
                                      "due_date": si.due_date, "outstanding": si.outstanding_amount,
                                      "interest": 0, "payment_term": None})
        d.flags.ignore_permissions = True
        d.insert()
        made.append(d.name + " (payment reminder)")
    if not frappe.db.count("Payment Request"):
        so = frappe.db.get_value("Sales Order", {"docstatus": 1, "customer": ("like", "Deccan%")}, "name")
        if so:
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
            pr.subject = "30% advance against Sales Order %s" % so
            pr.flags.ignore_permissions = True
            pr.insert()
            made.append(pr.name + " (advance request 30%)")
    return "; ".join(made) or "(already exist)"


# --------------------------------------------------------------------- AC-04
def email_templates():
    made = []
    for name, subject, body in [
        ("MSCAST - Dispatch intimation",
         "Dispatch intimation: {{ doc.name }}",
         "<p>Dear Sir,</p><p>Please find attached the dispatch documents for {{ doc.name }}. "
         "Material has been dispatched through {{ doc.transporter_name or 'our transporter' }} "
         "vide LR {{ doc.lr_no or '' }}.</p><p>Regards,<br>MSCAST Engineering Pvt. Ltd.</p>"),
        ("MSCAST - Purchase order to supplier",
         "Purchase Order {{ doc.name }} - MSCAST Engineering",
         "<p>Dear Supplier,</p><p>Please find attached our purchase order {{ doc.name }} dated "
         "{{ doc.transaction_date }}. Kindly acknowledge and confirm the delivery schedule.</p>"
         "<p>Regards,<br>Procurement, MSCAST Engineering Pvt. Ltd.</p>"),
        ("MSCAST - Payment reminder",
         "Outstanding invoice reminder - {{ doc.name }}",
         "<p>Dear Sir,</p><p>Our records show an amount outstanding against the enclosed invoice. "
         "We request you to arrange payment.</p><p>Regards,<br>Accounts, MSCAST Engineering Pvt. Ltd.</p>"),
    ]:
        if frappe.db.exists("Email Template", name):
            continue
        ins({"doctype": "Email Template", "name": name, "subject": subject, "response": body,
             "use_html": 1})
        made.append(name)
    return ", ".join(made) or "(all existed)"


# --------------------------------------------------------------------- AC-21
EXPENSE_REPORT_SQL = """
select
    a.name                          as "Account:Link/Account:260",
    a.account_number                as "Code::70",
    ifnull(cur.amt, 0)              as "This year (FY 26-27):Currency:150",
    ifnull(prev.amt, 0)             as "Last year:Currency:130",
    (ifnull(cur.amt,0) - ifnull(prev.amt,0)) as "Change:Currency:120",
    round(case when ifnull(prev.amt,0) = 0 then 0
          else (ifnull(cur.amt,0) - ifnull(prev.amt,0)) / prev.amt * 100 end, 1)
                                    as "Change %%:Float:90",
    round(case when (select sum(credit - debit) from `tabGL Entry` g2
                     inner join `tabAccount` a2 on a2.name = g2.account
                     where a2.root_type = 'Income' and g2.is_cancelled = 0
                       and g2.posting_date between '2026-04-01' and '2027-03-31') = 0 then 0
          else ifnull(cur.amt,0) /
               (select sum(credit - debit) from `tabGL Entry` g2
                inner join `tabAccount` a2 on a2.name = g2.account
                where a2.root_type = 'Income' and g2.is_cancelled = 0
                  and g2.posting_date between '2026-04-01' and '2027-03-31') * 100 end, 1)
                                    as "%% of sales:Float:100"
from `tabAccount` a
left join (select account, sum(debit - credit) amt from `tabGL Entry`
           where is_cancelled = 0 and posting_date between '2026-04-01' and '2027-03-31'
           group by account) cur on cur.account = a.name
left join (select account, sum(debit - credit) amt from `tabGL Entry`
           where is_cancelled = 0 and posting_date between '2025-04-01' and '2026-03-31'
           group by account) prev on prev.account = a.name
where a.root_type = 'Expense' and a.is_group = 0 and a.company = '""" + COMPANY + """'
  and (ifnull(cur.amt,0) <> 0 or ifnull(prev.amt,0) <> 0)
order by ifnull(cur.amt,0) desc
"""


def expense_analysis_report():
    name = "MSCAST Expense Analysis (vs last year, % of sales)"
    if frappe.db.exists("Report", name):
        frappe.db.set_value("Report", name, "query", EXPENSE_REPORT_SQL)
        return "updated"
    ins({"doctype": "Report", "report_name": name, "ref_doctype": "GL Entry",
         "report_type": "Query Report", "is_standard": "No", "module": "Custom",
         "query": EXPENSE_REPORT_SQL, "disabled": 0,
         "roles": [{"role": "System Manager"}, {"role": "Accounts User"}, {"role": "Accounts Manager"}]})
    return name


def run():
    step("COA heads (reserves, borrowings, lease, prior period, penalties, petty cash)", coa_heads)
    step("non-project payments + petty cash", non_project_payments)
    step("travel / insurance / cargo journal vouchers", travel_insurance_cargo)
    step("landed cost voucher", landed_cost)
    step("credit note + debit note", notes)
    step("TDS 194C on fabrication bill", tds_on_contractor)
    step("supplier credit terms", supplier_credit)
    step("receivables follow-up (dunning + payment request)", receivables_followup)
    step("email templates", email_templates)
    step("expense analysis report", expense_analysis_report)
    log("BATCH A DONE")


run()
