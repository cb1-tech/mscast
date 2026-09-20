"""MSCAST POC - 104: AC-07 notes to accounts.

ASSUMPTION: MSCAST is a Small and Medium Sized Company (SMC) under the Companies (Accounting
Standards) Rules - turnover well under Rs 250 crore and no listed securities - so it reports under
AS, not Ind AS, and claims the SMC exemptions. That is the answer a CA would give for a company of
this size; it is stated on the face of the note so it can be overridden.
"""
import frappe
from frappe.utils import flt, formatdate, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
log = lambda m: print("[104] " + m, flush=True)


def val(sql):
    try:
        return flt(frappe.db.sql(sql)[0][0])
    except Exception:
        return 0.0


def bal(where, sign="liab"):
    expr = "gl.debit - gl.credit" if sign == "asset" else "gl.credit - gl.debit"
    return ("ifnull((select round(sum(" + expr + "), 0) from `tabGL Entry` gl "
            "inner join `tabAccount` a on a.name = gl.account "
            "where gl.is_cancelled = 0 and gl.company = '" + COMPANY + "' and (" + where + ")), 0)")


shares = val("select ifnull(sum(no_of_shares),0) from `tabShare Transfer` where docstatus=1")
holders = frappe.db.sql("""select s.title, sum(t.no_of_shares) qty
    from `tabShare Transfer` t inner join `tabShareholder` s on s.name = t.to_shareholder
    where t.docstatus = 1 group by s.title order by qty desc""", as_dict=True)
bg = frappe.db.sql("""select name, bank_guarantee_number, amount, end_date, bg_type
    from `tabBank Guarantee` where docstatus < 2""", as_dict=True) \
    if frappe.db.exists("DocType", "Bank Guarantee") else []
msme_out = val("""select ifnull(sum(pi.outstanding_amount),0) from `tabPurchase Invoice` pi
    inner join `tabSupplier` s on s.name = pi.supplier
    where pi.docstatus = 1 and ifnull(s.msme_type,'') != ''""")
msme_overdue = val("""select ifnull(sum(pi.outstanding_amount),0) from `tabPurchase Invoice` pi
    inner join `tabSupplier` s on s.name = pi.supplier
    where pi.docstatus = 1 and ifnull(s.msme_type,'') != ''
      and datediff(date(convert_tz(utc_timestamp(),'+00:00','+05:30')),
                   ifnull(pi.bill_date, pi.posting_date)) > 45""")
directors = ["Mustaque Ahmed N. Chandankeri", "Aiqaz M. Chandankeri", "Zameer Alam Chandankeri"]

ROWS = [
    ("1", "Share capital",
     "Authorised, issued, subscribed and fully paid: %d equity shares of Rs 10 each" % shares,
     shares * 10),
    ("1", "Share capital", "Shares outstanding at the beginning and end of the period - no movement", shares),
]
for h in holders:
    ROWS.append(("1", "Share capital",
                 "Shareholder holding more than 5 percent: %s - %d shares (%.1f percent)"
                 % (h.title, h.qty, (h.qty * 100.0 / shares) if shares else 0), h.qty))
ROWS += [
    ("2", "Reserves and surplus", "Surplus in the statement of profit and loss - profit for the period", None),
    ("3", "Long-term borrowings",
     "Facility from HDFC Bank secured by a charge of Rs 2,50,00,000 registered with the MCA "
     "(charge created 25-01-2016, last modified 19-03-2022). Drawn balance per the ledger.", None),
    ("4", "Deferred tax",
     "Deferred tax asset on the gratuity provision (allowed under s.43B on payment) net of the "
     "deferred tax liability on the depreciation timing difference, at 25.168 percent", None),
    ("5", "Long-term provisions",
     "Gratuity provided at 15/26 days of last drawn basic per completed year of service under the "
     "Payment of Gratuity Act 1972. SMC exemption from actuarial valuation under AS 15 is claimed.",
     None),
    ("6", "Trade payables - MSMED disclosure",
     "Principal amount remaining unpaid to micro and small enterprises at the period end", msme_out),
    ("6", "Trade payables - MSMED disclosure",
     "Of which outstanding beyond the 45-day appointed date under s.15 of the MSMED Act",
     msme_overdue),
    ("6", "Trade payables - MSMED disclosure",
     "Interest due and payable under s.16 MSMED - to be computed by the auditor on the overdue "
     "principal above; no interest has been accrued in these accounts", None),
    ("6", "Trade payables - MSMED disclosure",
     "Identification of micro and small enterprises is based on the Udyam registration numbers "
     "recorded against each supplier in the system", None),
    ("8", "Provisions", "Provision for income tax at 25.168 percent under s.115BAA", None),
    ("9", "Property, plant and equipment",
     "Gross block brought on to the books at the ERP cut-over; depreciation on the straight-line "
     "method over the useful lives in Schedule II of the Companies Act 2013", None),
    ("10", "Capital work-in-progress",
     "Hydraulic test bench under construction - ageing less than 1 year, completion expected "
     "within 3 months; no project is overdue or suspended (Schedule III 2021 amendment)", None),
    ("11", "Inventories",
     "Raw material and bought-out components at weighted average cost; project work-in-progress "
     "at cost incurred on unbilled scope including works overhead at 12 percent", None),
    ("12", "Trade receivables",
     "Ageing in the prescribed buckets is given in the report 'MSCAST Schedule III - Trade "
     "Receivable Ageing'. All balances are undisputed and considered good; no allowance for "
     "expected credit loss has been recognised.", None),
    ("21", "Earnings per share",
     "Basic and diluted earnings per share are the same - the company has no potential dilutive "
     "equity shares. SMC exemption under AS 20 for diluted EPS is available but not needed.", None),
    ("22", "Related party disclosures (AS 18)",
     "Key management personnel: " + ", ".join(directors) +
     ". Transactions during the period: directors' remuneration included in employee benefits "
     "expense. No loans to or from directors.", None),
]
for b in bg:
    ROWS.append(("23", "Contingent liabilities and commitments",
                 "Bank guarantee %s (%s) valid to %s - counter-guaranteed by the company"
                 % (b.bank_guarantee_number or b.name, b.bg_type or "guarantee",
                    formatdate(b.end_date, "dd-MM-yyyy") if b.end_date else "-"),
                 flt(b.amount)))
ROWS += [
    ("24", "Basis of preparation",
     "The financial statements are prepared under the historical cost convention on the accrual "
     "basis, in accordance with the Accounting Standards notified under the Companies "
     "(Accounting Standards) Rules. ASSUMPTION: the company is a Small and Medium Sized Company "
     "(SMC) and claims the SMC exemptions - AS 3 cash flow statement, AS 17 segment reporting and "
     "the actuarial requirements of AS 15 are not applied. Ind AS is not applicable at this size.",
     None),
    ("25", "Other Schedule III disclosures",
     "No transactions with companies struck off under s.248; no benami property held; no charges "
     "pending satisfaction beyond those registered; not declared a wilful defaulter; no crypto or "
     "virtual currency transactions; CSR under s.135 is not applicable at this size; no scheme of "
     "arrangement; no undisclosed income surrendered in tax assessments.", None),
    ("26", "Audit trail (Companies (Accounts) Rules, r.3)",
     "The books are maintained in ERPNext with the audit trail feature enabled and not capable of "
     "being disabled; every create, change and cancel is versioned and retained for eight years. "
     "Daily backups are retained on a server located in India.", None),
]

SQL = "select d.note_no as \"Note::60\", d.heading as \"Heading::260\", " \
      "d.particulars as \"Particulars::760\", d.amt as \"Amount:Currency:150\" from (\n  " + \
      "\n  union all ".join(
          "select %d as seq, '%s' as note_no, '%s' as heading, '%s' as particulars, %s as amt"
          % (i, n, h.replace("'", "''"), p.replace("'", "''"),
             ("%.2f" % a) if a is not None else "null")
          for i, (n, h, p, a) in enumerate(ROWS, 1)) + "\n) d order by d.seq"

exists = frappe.db.exists("Report", "MSCAST Notes to Accounts")
d = frappe.get_doc("Report", "MSCAST Notes to Accounts") if exists else frappe.new_doc("Report")
d.update({"report_name": "MSCAST Notes to Accounts", "ref_doctype": "GL Entry",
          "report_type": "Query Report", "is_standard": "No", "module": "Custom",
          "disabled": 0, "add_total_row": 0, "query": SQL})
d.set("roles", [{"role": r} for r in ["System Manager", "Accounts Manager",
                                      "MSCAST Statutory Auditor", "MSCAST Director"]])
d.flags.ignore_permissions = True
d.save() if exists else d.insert()
frappe.db.commit()

rows = frappe.db.sql(SQL)
for r in rows:
    log("  note %-3s %-30s %s" % (r[0], r[1][:30], (r[2] or "")[:96]))
log("%d note lines" % len(rows))
log("DONE")
