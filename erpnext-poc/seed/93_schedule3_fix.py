"""MSCAST POC - 93: fix the Schedule III balance sheet / P&L generator and guard the ratios
against immaterial denominators (a thin demo ledger otherwise produces 100% ROE and a
4.4-million DSCR, which is worse than showing nothing)."""
import frappe
from frappe.utils import flt, formatdate, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
ASAT = "As at " + formatdate(TODAY, "dd MMM yyyy")
log = lambda m: print("[93] " + m, flush=True)


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
                                      "MSCAST Statutory Auditor", "MSCAST Director")):
    exists = frappe.db.exists("Report", name)
    d = frappe.get_doc("Report", name) if exists else frappe.new_doc("Report")
    d.update({"report_name": name, "ref_doctype": ref_dt, "report_type": "Query Report",
              "is_standard": "No", "module": "Custom", "disabled": 0, "add_total_row": 0,
              "query": sql})
    d.set("roles", [{"role": r} for r in roles])
    d.flags.ignore_permissions = True
    d.save() if exists else d.insert()
    return name


def bal(where, sign="liab"):
    expr = "gl.debit - gl.credit" if sign == "asset" else "gl.credit - gl.debit"
    return ("ifnull((select round(sum(" + expr + "), 0) from `tabGL Entry` gl "
            "inner join `tabAccount` a on a.name = gl.account "
            "where gl.is_cancelled = 0 and gl.company = '" + COMPANY + "' and (" + where + ")), 0)")


def payables(msme=True):
    op = "!=" if msme else "="
    return ("ifnull((select round(sum(pi.outstanding_amount), 0) from `tabPurchase Invoice` pi "
            "inner join `tabSupplier` s on s.name = pi.supplier "
            "where pi.docstatus = 1 and ifnull(s.msme_type,'') " + op + " '' ), 0)")


SURPLUS = "(" + bal("a.root_type = 'Income'") + " - " + bal("a.root_type = 'Expense'", "asset") + ")"


def union(rows, value_label):
    parts = []
    for seq, note, label, val in rows:
        parts.append("select %d as seq, '%s' as note, '%s' as particulars, %s as amt"
                     % (seq, note, label.replace("'", "''"), val if val else "null"))
    return ('select\n'
            '  d.note as "Note::55",\n'
            '  d.particulars as "Particulars::430",\n'
            '  d.amt as "' + value_label + ':Currency:175",\n'
            '  null as "Previous year:Currency:150"\n'
            'from (\n  ' + "\n  union all ".join(parts) + '\n) d order by d.seq')


def balance_sheet():
    ppe = bal("(a.account_type in ('Fixed Asset','Accumulated Depreciation') "
              "or a.account_name like '%%Plant and Machinery%%' or a.account_name like '%%Furniture%%' "
              "or a.account_name like '%%Office Equipment%%' or a.account_name like '%%Computer%%') "
              "and a.account_name not like '%%Software%%'", "asset")
    rows = [
        (10, "", "I. EQUITY AND LIABILITIES", None),
        (20, "", "1. Shareholders' funds", None),
        (30, "1", "        (a) Share capital",
         bal("a.account_name like '%%Share Capital%%' or a.account_name like '%%Capital Stock%%'")),
        (40, "2", "        (b) Reserves and surplus",
         bal("a.root_type = 'Equity' and a.account_name not like '%%Share Capital%%' "
             "and a.account_name not like '%%Capital Stock%%'") + " + " + SURPLUS),
        (50, "", "2. Non-current liabilities", None),
        (60, "3", "        (a) Long-term borrowings",
         bal("a.account_name like '%%Term Loan%%' or a.account_name like '%%Borrowing%%'")),
        (70, "4", "        (b) Deferred tax liabilities (net)",
         bal("a.account_name like '%%Deferred Tax Liability%%'")),
        (80, "5", "        (c) Long-term provisions - gratuity",
         bal("a.account_name like '%%Provision for Gratuity%%'")),
        (90, "", "3. Current liabilities", None),
        (100, "6", "        (a) Trade payables - micro and small enterprises", payables(True)),
        (110, "6", "        (b) Trade payables - other than micro and small", payables(False)),
        (120, "7", "        (c) Other current liabilities - statutory dues",
         bal("a.account_name like '%%Duties and Taxes%%' or a.account_name like '%%GST%%' "
             "or a.account_name like '%%TDS%%' or a.account_name like '%%Professional Tax%%' "
             "or a.account_name like '%%Payroll Payable%%' or a.account_name like '%%Lease Liabilit%%'")),
        (130, "8", "        (d) Short-term provisions - income tax",
         bal("a.account_name like '%%Provision for Income Tax%%'")),
        (140, "", "TOTAL",
         "(" + bal("a.root_type in ('Equity','Liability') and a.account_type != 'Payable'")
         + " + " + payables(True) + " + " + payables(False) + " + " + SURPLUS + ")"),
        (150, "", " ", None),
        (160, "", "II. ASSETS", None),
        (170, "", "1. Non-current assets", None),
        (180, "9", "        (a) Property, plant and equipment", ppe),
        (190, "9", "        (b) Intangible assets - software",
         bal("a.account_name like '%%Software%%'", "asset")),
        (200, "10", "        (c) Capital work-in-progress",
         bal("a.account_type = 'Capital Work in Progress' or a.account_name like '%%CWIP%%'", "asset")),
        (210, "4", "        (d) Deferred tax assets (net)",
         bal("a.account_name like '%%Deferred Tax Asset%%'", "asset")),
        (220, "", "2. Current assets", None),
        (230, "11", "        (a) Inventories including project work-in-progress",
         bal("a.account_type = 'Stock' or a.account_name like '%%Stock%%' "
             "or a.account_name like '%%Work in Progress - Projects%%'", "asset")),
        (240, "12", "        (b) Trade receivables", bal("a.account_type = 'Receivable'", "asset")),
        (250, "13", "        (c) Cash and cash equivalents",
         bal("a.account_type in ('Bank','Cash')", "asset")),
        (260, "14", "        (d) Other current assets - retention receivable",
         bal("a.account_name like '%%Retention%%'", "asset")),
        (270, "", "TOTAL", bal("a.root_type = 'Asset'", "asset")),
        (280, "", " ", None),
        (290, "", "Comparatives: first year on ERPNext - previous-year column fills once the Tally "
                  "opening balances are migrated.", None),
    ]
    sql = union(rows, ASAT)
    name = qreport("MSCAST Balance Sheet (Schedule III)", "GL Entry", sql)
    res = frappe.db.sql(sql)
    tot = [r for r in res if r[1].strip() == "TOTAL"]
    log("  equities+liabilities = %s | assets = %s" % (tot[0][2], tot[1][2]))
    diff = flt(tot[1][2]) - flt(tot[0][2])
    return "%s | difference %s" % (name, "0 (balances)" if abs(diff) < 1 else round(diff, 2))


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
        (10, "15", "I.    Revenue from operations", rev),
        (20, "16", "II.   Other income", oth),
        (30, "", "III.  Total income", tot_inc),
        (40, "", "IV.   Expenses", None),
        (50, "17", "           Cost of materials consumed and bought-out", mat),
        (60, "18", "           Employee benefits expense", emp),
        (70, "19", "           Finance costs", fin),
        (80, "9", "           Depreciation and amortisation expense", dep),
        (90, "20", "           Other expenses", other),
        (100, "", "           Total expenses", tot_exp),
        (110, "", "V.    Profit before tax", pbt),
        (120, "", "VI.   Tax expense", None),
        (130, "8", "           (a) Current tax", tax_c),
        (140, "4", "           (b) Deferred tax", tax_d),
        (150, "", "VII.  Profit for the period", pat),
        (160, "21", "VIII. Earnings per equity share - basic and diluted (Rs)",
         "round(" + pat + " / nullif(" + shares + ", 0), 2)"),
    ]
    sql = union(rows, "Period to " + formatdate(TODAY, "dd MMM yyyy"))
    name = qreport("MSCAST Statement of Profit and Loss (Schedule III)", "GL Entry", sql)
    for r in frappe.db.sql(sql):
        if r[2] is not None:
            log("  %-60s %12s" % (r[1][:60], r[2]))
    return name


def ratios():
    ca = bal("a.root_type = 'Asset' and (a.account_type in ('Bank','Cash','Receivable','Stock') "
             "or a.account_name like '%%Stock%%' or a.account_name like '%%Retention%%' "
             "or a.account_name like '%%Work in Progress%%' or a.account_name like '%%Deferred Tax Asset%%')",
             "asset")
    cl = ("(" + bal("a.root_type = 'Liability' and a.account_name not like '%%Term Loan%%' "
                    "and a.account_name not like '%%Borrowing%%' and a.account_type != 'Payable'")
          + " + " + payables(True) + " + " + payables(False) + ")")
    inv = bal("a.account_type = 'Stock' or a.account_name like '%%Stock%%'", "asset")
    debt = bal("a.account_name like '%%Term Loan%%' or a.account_name like '%%Borrowing%%'")
    eq = "(" + bal("a.root_type = 'Equity'") + " + " + SURPLUS + ")"
    rev = bal("a.root_type = 'Income'")
    pat = SURPLUS
    cogs = bal("a.account_name like '%%Cost of Goods%%' or a.account_name like '%%Material%%' "
               "or a.account_name like '%%Purchase%%'", "asset")
    ar = bal("a.account_type = 'Receivable'", "asset")
    ap = "(" + payables(True) + " + " + payables(False) + ")"
    fin = bal("a.account_name like '%%Interest%%'", "asset")
    ce = "(" + eq + " + " + debt + ")"

    def r(num, den, pct=False, floor=10000):
        """Ratio guarded: null when the denominator is immaterial, so no 100% ROE artefacts."""
        return ("case when abs(%s) < %d then null else round(%s %s / %s, 2) end"
                % (den, floor, num, "* 100" if pct else "", den))

    rows = [
        (10, "a", "Current ratio (times)", r(ca, cl)),
        (20, "b", "Debt-equity ratio (times)", r(debt, eq)),
        (30, "c", "Debt service coverage ratio (times)", r("(%s + %s)" % (pat, fin), fin)),
        (40, "d", "Return on equity (%)", r(pat, eq, True)),
        (50, "e", "Inventory turnover (times)", r(cogs, inv)),
        (60, "f", "Trade receivables turnover (times)", r(rev, ar)),
        (70, "g", "Trade payables turnover (times)", r(cogs, ap)),
        (80, "h", "Net capital turnover (times)", r(rev, "(%s - %s)" % (ca, cl))),
        (90, "i", "Net profit ratio (%)", r(pat, rev, True)),
        (100, "j", "Return on capital employed (%)", r("(%s + %s)" % (pat, fin), ce, True)),
        (110, "k", "Return on investment (%)", r("(%s + %s)" % (pat, fin), ce, True)),
    ]
    parts = []
    for seq, cl_, label, val in rows:
        parts.append("select %d as seq, '%s' as cl, '%s' as particulars, %s as val"
                     % (seq, cl_, label.replace("'", "''"), val))
    sql = ('select d.cl as "Ref::50",\n'
           '       d.particulars as "Ratio (Schedule III, 2021 amendment)::400",\n'
           '       d.val as "Current period:Float:130",\n'
           '       null as "Previous period:Float:130",\n'
           '       case when d.val is null then '
           '\'Denominator immaterial in the demo ledger - not meaningful\' '
           'else \'Explain a variance above 25 percent in the notes\' end as "Remark::400"\n'
           'from (\n  ' + "\n  union all ".join(parts) + '\n) d order by d.seq')
    name = qreport("MSCAST Schedule III - Ratios", "GL Entry", sql)
    shown = 0
    for row in frappe.db.sql(sql):
        log("  %-58s %s" % (row[1][:58], row[2] if row[2] is not None else "n/a"))
        shown += 1 if row[2] is not None else 0
    return "%s (%d of 11 meaningful on the demo ledger)" % (name, shown)


def run():
    step("Schedule III balance sheet", balance_sheet)
    step("Schedule III statement of profit and loss", profit_and_loss)
    step("Schedule III ratios (guarded)", ratios)
    frappe.clear_cache()
    log("SCRIPT 93 DONE")


run()
