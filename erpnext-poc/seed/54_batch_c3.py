"""MSCAST POC - 54: BATCH C part 3 - retention flow, supplementary invoice, gratuity provision,
Schedule III balance sheet and statement of profit and loss."""
import frappe
from frappe.utils import add_days, flt, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[C3] " + m, flush=True)


def step(name, fn, *a, **kw):
    try:
        out = fn(*a, **kw)
        frappe.db.commit()
        log("OK   " + name + ((" -> " + str(out)) if out else ""))
        return out or True
    except Exception as e:
        frappe.db.rollback()
        log("FAIL " + name + " :: " + repr(e)[:400])
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


def qreport(name, ref_dt, sql, roles=("System Manager", "Accounts Manager"), total=False):
    exists = frappe.db.exists("Report", name)
    d = frappe.get_doc("Report", name) if exists else frappe.new_doc("Report")
    d.update({"report_name": name, "ref_doctype": ref_dt, "report_type": "Query Report",
              "is_standard": "No", "module": "Custom", "disabled": 0,
              "add_total_row": 1 if total else 0, "query": sql})
    d.set("roles", [{"role": r} for r in roles])
    d.flags.ignore_permissions = True
    d.save() if exists else d.insert()
    return name


# ------------------------------------------------------------ AC-09 retention
def retention():
    ret = acc(account_name=("like", "%Retention Receivable%"))
    if not ret:
        return "retention account missing"
    si = frappe.db.get_value("Sales Invoice", {"docstatus": 1, "is_return": 0,
                                               "outstanding_amount": (">", 0)},
                             ["name", "customer", "grand_total", "outstanding_amount"], as_dict=True,
                             order_by="grand_total desc")
    if not si:
        return "no open invoice"
    if frappe.db.exists("Journal Entry", {"user_remark": ("like", "Retention retained%")}):
        return "already booked"
    amt = round(flt(si.grand_total) * 0.10, 2)
    deb = acc(account_type="Receivable")
    j = ins({"doctype": "Journal Entry", "voucher_type": "Journal Entry", "company": COMPANY,
             "posting_date": TODAY,
             "user_remark": "Retention retained by customer @ 10 percent on invoice %s - "
                            "reclassified from trade receivable to retention receivable, "
                            "releasable against the performance certificate." % si.name,
             "accounts": [
                 {"account": ret, "debit_in_account_currency": amt, "cost_center": cc(),
                  "party_type": "Customer", "party": si.customer},
                 {"account": deb, "credit_in_account_currency": amt, "cost_center": cc(),
                  "party_type": "Customer", "party": si.customer,
                  "reference_type": "Sales Invoice", "reference_name": si.name}]},
            submit=True)
    return "%s - retention %s on %s" % (j.name, amt, si.name)


# ------------------------------------------------------------ PC-18 supplementary invoice
def supplementary_invoice():
    claim = frappe.db.get_value("MSCAST Client Claim",
                                {"status": ("not in", ["Settled", "Rejected"])},
                                ["name", "project", "customer", "claim_amount", "settled_amount"],
                                as_dict=True)
    if not claim:
        return "no open claim"
    if frappe.db.exists("Sales Invoice", {"remarks": ("like", "Supplementary invoice%"), "docstatus": 1}):
        return "already raised"
    amt = flt(claim.settled_amount) or flt(claim.claim_amount)
    item = frappe.db.get_value("Sales Invoice Item", {"docstatus": 1}, "item_code")
    si = frappe.new_doc("Sales Invoice")
    si.customer = claim.customer
    si.company = COMPANY
    si.set_posting_time = 1
    si.posting_date = TODAY
    si.due_date = add_days(TODAY, 30)
    si.project = claim.project
    si.append("items", {"item_code": item, "qty": 1, "rate": amt,
                        "item_name": "Supplementary billing - agreed scope variation",
                        "description": "Supplementary invoice against agreed claim %s - "
                                       "additional scope / price variation as per customer's "
                                       "amendment to the purchase order." % claim.name,
                        "project": claim.project})
    tmpl = "Output GST In-state - " + ABBR
    if frappe.db.exists("Sales Taxes and Charges Template", tmpl):
        si.taxes_and_charges = tmpl
        for t in frappe.get_doc("Sales Taxes and Charges Template", tmpl).taxes:
            si.append("taxes", {"charge_type": t.charge_type, "account_head": t.account_head,
                                "description": t.description, "rate": t.rate,
                                "cost_center": t.cost_center})
    si.remarks = ("Supplementary invoice against client claim %s - agreed scope variation. "
                  "Original contract value unchanged; this bill covers the approved extra." % claim.name)
    si.flags.ignore_permissions = True
    si.flags.ignore_mandatory = True
    si.insert()
    si.submit()
    frappe.db.set_value("MSCAST Client Claim", claim.name,
                        {"status": "Settled", "sales_invoice": si.name, "settlement_date": TODAY,
                         "settled_amount": amt})
    return "%s for %s against claim %s" % (si.name, si.grand_total, claim.name)


# ------------------------------------------------------------ HR-12 gratuity
def gratuity():
    made = []
    parent = frappe.db.get_value("Account", {"company": COMPANY, "is_group": 1,
                                             "account_name": ("like", "%Current Liabilities%")}, "name") \
        or frappe.db.get_value("Account", {"company": COMPANY, "is_group": 1, "root_type": "Liability"}, "name")
    prov = acc(account_name="Provision for Gratuity")
    if not prov:
        prov = ins({"doctype": "Account", "account_name": "Provision for Gratuity",
                    "parent_account": parent, "company": COMPANY, "root_type": "Liability",
                    "account_type": "Payable" if False else None}).name
        made.append("Provision for Gratuity account")
    exp_parent = frappe.db.get_value("Account", {"company": COMPANY, "is_group": 1,
                                                 "root_type": "Expense"}, "name")
    exp = acc(account_name="Gratuity Expense")
    if not exp:
        exp = ins({"doctype": "Account", "account_name": "Gratuity Expense",
                   "parent_account": exp_parent, "company": COMPANY, "root_type": "Expense"}).name
        made.append("Gratuity Expense account")

    if frappe.db.exists("DocType", "Gratuity Rule") and not frappe.db.exists("Gratuity Rule", "Indian Payment of Gratuity Act 1972"):
        try:
            ins({"doctype": "Gratuity Rule", "name": "Indian Payment of Gratuity Act 1972",
                 "calculate_gratuity_amount_based_on": "Current Slab",
                 "total_working_days_per_year": 26, "minimum_year_for_gratuity": 5,
                 "work_experience_calculation_function": "Round off Work Experience",
                 "applicable_earnings_component": [],
                 "gratuity_rule_slabs": [{"from_year": 0, "to_year": 0, "fraction_of_applicable_earnings": 0.577}]})
            made.append("Gratuity Rule (15/26 days per completed year)")
        except Exception as e:
            log("  gratuity rule skipped: " + repr(e)[:160])

    if frappe.db.exists("Journal Entry", {"user_remark": ("like", "Provision for gratuity%")}):
        made.append("provision already booked")
    else:
        rows = frappe.db.sql("""
            select e.name, e.employee_name, e.date_of_joining,
                   ifnull((select sum(sd.amount) from `tabSalary Detail` sd
                           inner join `tabSalary Slip` ss on ss.name = sd.parent
                           where ss.employee = e.name and sd.parent_field = 'earnings'
                             and sd.salary_component in ('Basic', 'Basic Salary')
                           order by ss.start_date desc limit 1), 0) as basic
            from `tabEmployee` e where e.status = 'Active' and e.company = %s""", COMPANY, as_dict=True)
        total = 0.0
        detail = []
        for r in rows:
            years = max(0.5, (frappe.utils.date_diff(TODAY, r.date_of_joining) or 0) / 365.0)
            basic = flt(r.basic) or 25000
            amt = round(basic * 15 / 26 * years, 0)
            total += amt
            detail.append("%s %.1f yr Rs %s" % (r.employee_name, years, int(amt)))
        total = round(total, 0)
        if total:
            j = ins({"doctype": "Journal Entry", "voucher_type": "Journal Entry", "company": COMPANY,
                     "posting_date": TODAY,
                     "user_remark": "Provision for gratuity as at %s - actuarial-style estimate at "
                                    "15/26 days of last drawn basic per completed year of service "
                                    "(Payment of Gratuity Act 1972). Employees: %s"
                                    % (TODAY, "; ".join(detail)),
                     "accounts": [{"account": exp, "debit_in_account_currency": total, "cost_center": cc()},
                                  {"account": prov, "credit_in_account_currency": total, "cost_center": cc()}]},
                    submit=True)
            made.append("%s provision Rs %s for %d employees" % (j.name, int(total), len(rows)))
    return "; ".join(made) or "(already in place)"


# ------------------------------------------------------------ AC-17 Schedule III
BS_SQL = """
select
  case
    when a.root_type = 'Equity' then '1. EQUITY AND LIABILITIES - Shareholders funds'
    when a.root_type = 'Liability' and (a.account_name like '%%Term Loan%%' or a.account_name like '%%Borrowing%%'
         or a.account_name like '%%Lease Liabilit%%') then '2. Non-current liabilities'
    when a.root_type = 'Liability' then '3. Current liabilities'
    when a.root_type = 'Asset' and (a.account_type in ('Fixed Asset','Capital Work in Progress','Accumulated Depreciation')
         or a.account_name like '%%Fixed Asset%%' or a.account_name like '%%CWIP%%'
         or a.account_name like '%%Software%%') then '4. ASSETS - Non-current assets'
    else '5. Current assets'
  end                                                       as "Schedule III Head::330",
  case
    when a.account_name like '%%Share Capital%%' or a.account_name like '%%Capital Stock%%' then 'Share capital'
    when a.root_type = 'Equity' then 'Reserves and surplus'
    when a.account_name like '%%Term Loan%%' or a.account_name like '%%Borrowing%%' then 'Long-term borrowings'
    when a.account_name like '%%Lease Liabilit%%' then 'Lease liabilities'
    when a.account_type = 'Payable' then 'Trade payables'
    when a.account_name like '%%GST%%' or a.account_name like '%%TDS%%' or a.account_name like '%%Duties and Taxes%%'
         or a.account_name like '%%Professional Tax%%' or a.account_name like '%%PF%%' or a.account_name like '%%ESIC%%'
      then 'Other current liabilities - statutory dues'
    when a.account_name like '%%Provision%%' then 'Provisions'
    when a.account_type = 'Capital Work in Progress' or a.account_name like '%%CWIP%%'
      then 'Capital work-in-progress'
    when a.account_name like '%%Software%%' then 'Intangible assets'
    when a.account_type in ('Fixed Asset','Accumulated Depreciation') or a.account_name like '%%Fixed Asset%%'
      then 'Property, plant and equipment'
    when a.account_type = 'Stock' or a.account_name like '%%Stock%%' or a.account_name like '%%Inventor%%'
      then 'Inventories'
    when a.account_type = 'Receivable' then 'Trade receivables'
    when a.account_name like '%%Retention%%' then 'Other current assets - retention receivable'
    when a.account_type in ('Bank','Cash') then 'Cash and cash equivalents'
    else 'Other current assets'
  end                                                       as "Line Item::300",
  a.name                                                    as "Account:Link/Account:260",
  round(sum(case when a.root_type = 'Asset' then gl.debit - gl.credit
                 else gl.credit - gl.debit end), 2)         as "Amount (Rs):Currency:150"
from `tabGL Entry` gl
inner join `tabAccount` a on a.name = gl.account
where gl.is_cancelled = 0 and gl.company = '""" + COMPANY + """'
  and a.root_type in ('Asset', 'Liability', 'Equity')
group by a.name
having abs(round(sum(case when a.root_type = 'Asset' then gl.debit - gl.credit
                          else gl.credit - gl.debit end), 2)) > 0.5
order by 1, 2, 3
"""

PL_SQL = """
select
  case
    when a.root_type = 'Income' and a.account_name not like '%%Other Income%%' then 'I. Revenue from operations'
    when a.root_type = 'Income' then 'II. Other income'
    when a.account_name like '%%Cost of Goods%%' or a.account_name like '%%Material%%'
         or a.account_name like '%%Purchase%%' or a.account_name like '%%Stock Expenses%%'
      then 'IV. (a) Cost of materials consumed'
    when a.account_name like '%%Salar%%' or a.account_name like '%%Wage%%' or a.account_name like '%%Gratuity%%'
         or a.account_name like '%%Staff%%' or a.account_name like '%%PF%%' or a.account_name like '%%Bonus%%'
      then 'IV. (c) Employee benefits expense'
    when a.account_name like '%%Interest%%' or a.account_name like '%%Bank Charge%%'
         or a.account_name like '%%Finance%%' then 'IV. (d) Finance costs'
    when a.account_name like '%%Depreciat%%' or a.account_name like '%%Amortis%%'
      then 'IV. (e) Depreciation and amortisation expense'
    when a.account_name like '%%Tax%%' and a.root_type = 'Expense' then 'VII. Tax expense'
    else 'IV. (f) Other expenses'
  end                                                       as "Schedule III Head::330",
  a.name                                                    as "Account:Link/Account:280",
  round(sum(case when a.root_type = 'Income' then gl.credit - gl.debit
                 else gl.debit - gl.credit end), 2)         as "Amount (Rs):Currency:160"
from `tabGL Entry` gl
inner join `tabAccount` a on a.name = gl.account
inner join `tabFiscal Year` fy on gl.fiscal_year = fy.name
where gl.is_cancelled = 0 and gl.company = '""" + COMPANY + """'
  and a.root_type in ('Income', 'Expense')
group by a.name
having abs(round(sum(case when a.root_type = 'Income' then gl.credit - gl.debit
                          else gl.debit - gl.credit end), 2)) > 0.5
order by 1, 2
"""


def schedule_iii():
    r1 = qreport("MSCAST Balance Sheet (Schedule III grouping)", "GL Entry", BS_SQL,
                 ("System Manager", "Accounts Manager", "MSCAST Statutory Auditor", "MSCAST Director"),
                 total=True)
    r2 = qreport("MSCAST Statement of Profit and Loss (Schedule III grouping)", "GL Entry", PL_SQL,
                 ("System Manager", "Accounts Manager", "MSCAST Statutory Auditor", "MSCAST Director"),
                 total=True)
    out = []
    for r in (r1, r2):
        try:
            rows = frappe.db.sql(frappe.db.get_value("Report", r, "query"))
            out.append("%s -> %d rows" % (r, len(rows)))
        except Exception as e:
            out.append("%s -> ERROR %s" % (r, repr(e)[:200]))
    return " | ".join(out)


def run():
    step("retention reclassification", retention)
    step("supplementary invoice against agreed claim", supplementary_invoice)
    step("gratuity rule and provision", gratuity)
    step("Schedule III statements", schedule_iii)
    frappe.clear_cache()
    log("BATCH C3 DONE")


run()
