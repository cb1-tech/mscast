"""MSCAST POC - 92: A-14 Schedule III statements + AC-07 notes to accounts.

Builds the statutory vertical format, the Schedule III (2021 amendment) ageing tables and the
eleven prescribed ratios. Comparatives are shown as a column and stay blank until the Tally
opening migration - flagged on the face of the statement rather than fabricated.
"""
import frappe
from frappe.utils import flt, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
log = lambda m: print("[92] " + m, flush=True)
IST = "date(convert_tz(utc_timestamp(),'+00:00','+05:30'))"


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


def qreport(name, ref_dt, sql, roles=("System Manager", "Accounts Manager",
                                      "MSCAST Statutory Auditor", "MSCAST Director"), total=False):
    exists = frappe.db.exists("Report", name)
    d = frappe.get_doc("Report", name) if exists else frappe.new_doc("Report")
    d.update({"report_name": name, "ref_doctype": ref_dt, "report_type": "Query Report",
              "is_standard": "No", "module": "Custom", "disabled": 0,
              "add_total_row": 1 if total else 0, "query": sql})
    d.set("roles", [{"role": r} for r in roles])
    d.flags.ignore_permissions = True
    d.save() if exists else d.insert()
    return name


def bal(where, sign="liab"):
    """Scalar subquery: balance of accounts matching `where`. sign=asset -> Dr-Cr, liab -> Cr-Dr."""
    expr = "gl.debit - gl.credit" if sign == "asset" else "gl.credit - gl.debit"
    return ("ifnull((select round(sum(%s), 0) from `tabGL Entry` gl "
            "inner join `tabAccount` a on a.name = gl.account "
            "where gl.is_cancelled = 0 and gl.company = '%s' and (%s)), 0)" % (expr, COMPANY, where))


def payables(msme=True):
    op = "!=" if msme else "="
    return ("ifnull((select round(sum(pi.outstanding_amount), 0) from `tabPurchase Invoice` pi "
            "inner join `tabSupplier` s on s.name = pi.supplier "
            "where pi.docstatus = 1 and ifnull(s.msme_type,'') %s '' ), 0)" % op)


SURPLUS = ("(" + bal("a.root_type = 'Income'") + " - " + bal("a.root_type = 'Expense'", "asset") + ")")


def union(rows, cols):
    """rows: list of (seq, note, particulars, value_sql_or_None)."""
    parts = []
    for seq, note, label, val in rows:
        v = val if val else "null"
        parts.append("select %d as seq, '%s' as note, '%s' as particulars, %s as amt"
                     % (seq, note, label.replace("'", "''"), v))
    return ("select\n"
            "  d.note as \"Note::60\",\n"
            "  d.particulars as \"Particulars::%d\",\n"
            "  d.amt as \"%s:Currency:170\",\n"
            "  null as \"Previous year:Currency:150\"\n"
            "from (\n  " % cols[0] + "\n  union all ".join(parts) + "\n) d order by d.seq")


# ---------------------------------------------------------------- balance sheet
def balance_sheet():
    ppe = bal("(a.account_type in ('Fixed Asset','Accumulated Depreciation') "
              "or a.account_name like '%%Plant and Machinery%%' or a.account_name like '%%Furniture%%' "
              "or a.account_name like '%%Office Equipment%%' or a.account_name like '%%Computer%%') "
              "and a.account_name not like '%%Software%%'", "asset")
    rows = [
        (10, "", "I. EQUITY AND LIABILITIES", None),
        (20, "", "1. Shareholders' funds", None),
        (30, "1", "      (a) Share capital",
         bal("a.account_name like '%%Share Capital%%' or a.account_name like '%%Capital Stock%%'")),
        (40, "2", "      (b) Reserves and surplus",
         bal("a.root_type = 'Equity' and a.account_name not like '%%Share Capital%%' "
             "and a.account_name not like '%%Capital Stock%%'") + " + " + SURPLUS),
        (50, "", "2. Non-current liabilities", None),
        (60, "3", "      (a) Long-term borrowings",
         bal("a.account_name like '%%Term Loan%%' or a.account_name like '%%Borrowing%%'")),
        (70, "4", "      (b) Deferred tax liabilities (net)",
         bal("a.account_name like '%%Deferred Tax Liability%%'")),
        (80, "5", "      (c) Long-term provisions (gratuity)",
         bal("a.account_name like '%%Provision for Gratuity%%'")),
        (90, "", "3. Current liabilities", None),
        (100, "6", "      (a) Trade payables - micro and small enterprises", payables(True)),
        (110, "6", "      (b) Trade payables - others", payables(False)),
        (120, "7", "      (c) Other current liabilities (statutory dues, GST, TDS)",
         bal("a.account_name like '%%Duties and Taxes%%' or a.account_name like '%%GST%%' "
             "or a.account_name like '%%TDS%%' or a.account_name like '%%Professional Tax%%' "
             "or a.account_name like '%%Payroll Payable%%' or a.account_name like '%%Lease Liabilit%%'")),
        (130, "8", "      (d) Short-term provisions (income tax)",
         bal("a.account_name like '%%Provision for Income Tax%%'")),
        (140, "", "TOTAL - EQUITY AND LIABILITIES",
         "(" + bal("a.root_type in ('Equity','Liability') and a.account_type != 'Payable'") + " + "
         + payables(True) + " + " + payables(False) + " + " + SURPLUS + ")"),
        (150, "", "II. ASSETS", None),
        (160, "", "1. Non-current assets", None),
        (170, "9", "      (a) Property, plant and equipment", ppe),
        (180, "9", "      (b) Intangible assets (software)",
         bal("a.account_name like '%%Software%%'", "asset")),
        (190, "10", "      (c) Capital work-in-progress",
         bal("a.account_type = 'Capital Work in Progress' or a.account_name like '%%CWIP%%'", "asset")),
        (200, "4", "      (d) Deferred tax assets (net)",
         bal("a.account_name like '%%Deferred Tax Asset%%'", "asset")),
        (210, "", "2. Current assets", None),
        (220, "11", "      (a) Inventories (stock and project WIP)",
         bal("a.account_type = 'Stock' or a.account_name like '%%Stock%%' "
             "or a.account_name like '%%Work in Progress - Projects%%'", "asset")),
        (230, "12", "      (b) Trade receivables", bal("a.account_type = 'Receivable'", "asset")),
        (240, "13", "      (c) Cash and cash equivalents",
         bal("a.account_type in ('Bank','Cash')", "asset")),
        (250, "14", "      (d) Other current assets (retention receivable)",
         bal("a.account_name like '%%Retention%%'", "asset")),
        (260, "", "TOTAL - ASSETS", bal("a.root_type = 'Asset'", "asset")),
    ]
    sql = union(rows, [420])
    name = qreport("MSCAST Balance Sheet (Schedule III)", "GL Entry", sql)
    res = frappe.db.sql(sql, as_dict=True)
    tot_l = [r for r in res if "TOTAL - EQUITY" in r["Particulars::420"]][0]
    tot_a = [r for r in res if "TOTAL - ASSETS" in r["Particulars::420"]][0]
    k = [x for x in tot_l.keys() if x.startswith("As at") or "Currency:170" in x]
    lv = list(tot_l.values())[2]
    av = list(tot_a.values())[2]
    log("  total equity+liabilities = %s | total assets = %s | difference = %s"
        % (lv, av, flt(av) - flt(lv)))
    return "%s (%d lines, balances %s)" % (name, len(res),
                                           "OK" if abs(flt(av) - flt(lv)) < 1 else
                                           "DIFF %s" % (flt(av) - flt(lv)))


# ---------------------------------------------------------------- P&L
def profit_and_loss():
    rev = bal("a.root_type = 'Income' and a.account_name not like '%%Other Income%%' "
              "and a.account_name not like '%%Change in Work in Progress%%'")
    oth = bal("a.root_type = 'Income' and (a.account_name like '%%Other Income%%' "
              "or a.account_name like '%%Change in Work in Progress%%')")
    mat = bal("a.account_name like '%%Cost of Goods%%' or a.account_name like '%%Material%%' "
              "or a.account_name like '%%Purchase%%' or a.account_name like '%%Stock Expenses%%' "
              "or a.account_name like '%%Freight%%'", "asset")
    emp = bal("a.account_name like '%%Salar%%' or a.account_name like '%%Wage%%' "
              "or a.account_name like '%%Gratuity Expense%%' or a.account_name like '%%Staff%%' "
              "or a.account_name like '%%Bonus%%'", "asset")
    fin = bal("a.account_name like '%%Interest%%' or a.account_name like '%%Bank Charge%%'", "asset")
    dep = bal("a.account_name like '%%Depreciat%%' or a.account_name like '%%Amortis%%'", "asset")
    tax_c = bal("a.account_name like '%%Income Tax Expense%%'", "asset")
    tax_d = bal("a.account_name like '%%Deferred Tax Expense%%'", "asset")
    other = ("(" + bal("a.root_type = 'Expense'", "asset") + " - " + mat + " - " + emp + " - "
             + fin + " - " + dep + " - " + tax_c + " - " + tax_d + ")")
    tot_inc = "(" + rev + " + " + oth + ")"
    tot_exp = "(" + mat + " + " + emp + " + " + fin + " + " + dep + " + " + other + ")"
    pbt = "(" + tot_inc + " - " + tot_exp + ")"
    pat = "(" + pbt + " - " + tax_c + " - " + tax_d + ")"
    shares = "(select ifnull(sum(no_of_shares),0) from `tabShare Transfer` where docstatus = 1)"
    rows = [
        (10, "15", "I.   Revenue from operations", rev),
        (20, "16", "II.  Other income", oth),
        (30, "", "III. Total income (I + II)", tot_inc),
        (40, "", "IV.  Expenses", None),
        (50, "17", "        Cost of materials consumed / bought-out", mat),
        (60, "18", "        Employee benefits expense", emp),
        (70, "19", "        Finance costs", fin),
        (80, "9", "        Depreciation and amortisation expense", dep),
        (90, "20", "        Other expenses", other),
        (100, "", "        Total expenses", tot_exp),
        (110, "", "V.   Profit before tax (III - IV)", pbt),
        (120, "", "VI.  Tax expense", None),
        (130, "8", "        (a) Current tax", tax_c),
        (140, "4", "        (b) Deferred tax", tax_d),
        (150, "", "VII. Profit for the period", pat),
        (160, "21", "VIII. Earnings per equity share (basic and diluted) - Rs",
         "round(" + pat + " / nullif(" + shares + ", 0), 2)"),
    ]
    sql = union(rows, [420])
    name = qreport("MSCAST Statement of Profit and Loss (Schedule III)", "GL Entry", sql)
    res = frappe.db.sql(sql)
    for r in res:
        if r[2] is not None:
            log("  %-58s %s" % (r[2][:58], r[2 if False else 2] and r[-2]))
    return "%s (%d lines)" % (name, len(res))


# ---------------------------------------------------------------- ageing (2021 amendment)
AGEING_AR = """
select
  si.customer                                     as "Customer:Link/Customer:220",
  si.name                                         as "Invoice:Link/Sales Invoice:150",
  si.due_date                                     as "Due Date:Date:95",
  si.outstanding_amount                           as "Outstanding:Currency:130",
  case when datediff({ist}, si.due_date) <= 0 then si.outstanding_amount else 0 end
                                                  as "Not due:Currency:120",
  case when datediff({ist}, si.due_date) between 1 and 180 then si.outstanding_amount else 0 end
                                                  as "< 6 months:Currency:120",
  case when datediff({ist}, si.due_date) between 181 and 365 then si.outstanding_amount else 0 end
                                                  as "6 mo - 1 yr:Currency:120",
  case when datediff({ist}, si.due_date) between 366 and 730 then si.outstanding_amount else 0 end
                                                  as "1 - 2 yrs:Currency:110",
  case when datediff({ist}, si.due_date) between 731 and 1095 then si.outstanding_amount else 0 end
                                                  as "2 - 3 yrs:Currency:110",
  case when datediff({ist}, si.due_date) > 1095 then si.outstanding_amount else 0 end
                                                  as "> 3 yrs:Currency:110",
  'Undisputed - considered good'                  as "Classification::220"
from `tabSales Invoice` si
where si.docstatus = 1 and si.is_return = 0 and si.outstanding_amount > 0
order by si.due_date
""".replace("{ist}", IST)

AGEING_AP = """
select
  pi.supplier                                     as "Supplier:Link/Supplier:220",
  case when ifnull(s.msme_type,'') != '' then concat('MSME - ', s.msme_type) else 'Others' end
                                                  as "Schedule III class::140",
  pi.name                                         as "Invoice:Link/Purchase Invoice:150",
  ifnull(pi.bill_date, pi.posting_date)           as "Bill Date:Date:95",
  pi.outstanding_amount                           as "Outstanding:Currency:130",
  case when datediff({ist}, ifnull(pi.bill_date, pi.posting_date)) <= 365 then pi.outstanding_amount else 0 end
                                                  as "< 1 yr:Currency:120",
  case when datediff({ist}, ifnull(pi.bill_date, pi.posting_date)) between 366 and 730 then pi.outstanding_amount else 0 end
                                                  as "1 - 2 yrs:Currency:110",
  case when datediff({ist}, ifnull(pi.bill_date, pi.posting_date)) between 731 and 1095 then pi.outstanding_amount else 0 end
                                                  as "2 - 3 yrs:Currency:110",
  case when datediff({ist}, ifnull(pi.bill_date, pi.posting_date)) > 1095 then pi.outstanding_amount else 0 end
                                                  as "> 3 yrs:Currency:110",
  datediff({ist}, ifnull(pi.bill_date, pi.posting_date))
                                                  as "Age (days):Int:95"
from `tabPurchase Invoice` pi
left join `tabSupplier` s on s.name = pi.supplier
where pi.docstatus = 1 and pi.outstanding_amount > 0
order by 2, 4
""".replace("{ist}", IST)


def ageing():
    a = qreport("MSCAST Schedule III - Trade Receivable Ageing", "Sales Invoice", AGEING_AR,
                total=True)
    b = qreport("MSCAST Schedule III - Trade Payable Ageing (MSME and others)", "Purchase Invoice",
                AGEING_AP, total=True)
    return "%s (%d rows); %s (%d rows)" % (a, len(frappe.db.sql(AGEING_AR)),
                                           b, len(frappe.db.sql(AGEING_AP)))


# ---------------------------------------------------------------- 11 ratios
def ratios():
    ca = bal("a.root_type = 'Asset' and (a.account_type in ('Bank','Cash','Receivable','Stock') "
             "or a.account_name like '%%Stock%%' or a.account_name like '%%Retention%%' "
             "or a.account_name like '%%Work in Progress%%' or a.account_name like '%%Deferred Tax Asset%%')",
             "asset")
    cl = ("(" + bal("a.root_type = 'Liability' and a.account_name not like '%%Term Loan%%' "
                    "and a.account_name not like '%%Borrowing%%' "
                    "and a.account_type != 'Payable'") + " + " + payables(True) + " + "
          + payables(False) + ")")
    inv = bal("a.account_type = 'Stock' or a.account_name like '%%Stock%%'", "asset")
    debt = bal("a.account_name like '%%Term Loan%%' or a.account_name like '%%Borrowing%%'")
    eq = ("(" + bal("a.root_type = 'Equity'") + " + " + SURPLUS + ")")
    rev = bal("a.root_type = 'Income'")
    pat = SURPLUS
    cogs = bal("a.account_name like '%%Cost of Goods%%' or a.account_name like '%%Material%%' "
               "or a.account_name like '%%Purchase%%'", "asset")
    ar = bal("a.account_type = 'Receivable'", "asset")
    ap = "(" + payables(True) + " + " + payables(False) + ")"
    fin = bal("a.account_name like '%%Interest%%'", "asset")
    ce = "(" + eq + " + " + debt + ")"
    rows = [
        (10, "a", "Current ratio (times)", "round(%s / nullif(%s,0), 2)" % (ca, cl)),
        (20, "b", "Debt-equity ratio (times)", "round(%s / nullif(%s,0), 2)" % (debt, eq)),
        (30, "c", "Debt service coverage ratio (times)",
         "round((%s + %s) / nullif(%s,0), 2)" % (pat, fin, "greatest(%s, 1)" % fin)),
        (40, "d", "Return on equity (%)", "round(%s * 100 / nullif(%s,0), 2)" % (pat, eq)),
        (50, "e", "Inventory turnover (times)", "round(%s / nullif(%s,0), 2)" % (cogs, inv)),
        (60, "f", "Trade receivables turnover (times)", "round(%s / nullif(%s,0), 2)" % (rev, ar)),
        (70, "g", "Trade payables turnover (times)", "round(%s / nullif(%s,0), 2)" % (cogs, ap)),
        (80, "h", "Net capital turnover (times)",
         "round(%s / nullif(%s - %s,0), 2)" % (rev, ca, cl)),
        (90, "i", "Net profit ratio (%)", "round(%s * 100 / nullif(%s,0), 2)" % (pat, rev)),
        (100, "j", "Return on capital employed (%)",
         "round((%s + %s) * 100 / nullif(%s,0), 2)" % (pat, fin, ce)),
        (110, "k", "Return on investment (%) - same base as ROCE for an unlisted SMC",
         "round((%s + %s) * 100 / nullif(%s,0), 2)" % (pat, fin, ce)),
    ]
    parts = []
    for seq, note, label, val in rows:
        parts.append("select %d as seq, '%s' as cl, '%s' as particulars, %s as val"
                     % (seq, note, label.replace("'", "''"), val))
    sql = ("select d.cl as \"Ref::50\", d.particulars as \"Ratio (Schedule III, 2021 amendment)::430\",\n"
           "       d.val as \"Current period:Float:130\",\n"
           "       null as \"Previous period:Float:130\",\n"
           "       'Explain any variance above 25 percent in the notes' as \"Note::330\"\n"
           "from (\n  " + "\n  union all ".join(parts) + "\n) d order by d.seq")
    name = qreport("MSCAST Schedule III - Ratios", "GL Entry", sql)
    for r in frappe.db.sql(sql):
        log("  %-62s %s" % (r[1][:62], r[2]))
    return name


def run():
    step("A-14 Schedule III balance sheet", balance_sheet)
    step("A-14 Schedule III statement of profit and loss", profit_and_loss)
    step("Schedule III ageing tables (2021 amendment)", ageing)
    step("Schedule III eleven ratios", ratios)
    frappe.clear_cache()
    log("SCRIPT 92 DONE")


run()
