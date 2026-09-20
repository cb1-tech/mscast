"""MSCAST POC - 97: Schedule III statements, final pass + the missing share-capital entry.

Totals are now taken from the ledger itself (assets = Dr-Cr over root Asset; equity and
liabilities = Cr-Dr over root Liability/Equity plus the surplus), which must balance because the
trial balance nets to zero. Individual lines are presentation only, and whatever they fail to
classify shows up on an explicit 'unclassified' line rather than breaking the totals.
"""
import frappe
from frappe.utils import flt, formatdate, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
ASAT = "As at " + formatdate(TODAY, "dd MMM yyyy")
log = lambda m: print("[97] " + m, flush=True)


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


A = lambda w: bal("a.root_type = 'Asset' and (" + w + ")", "asset")
L = lambda w: bal("a.root_type = 'Liability' and (" + w + ")")
E = lambda w: bal("a.root_type = 'Expense' and (" + w + ")", "asset")


def add(*x):
    return "(" + " + ".join(x) + ")"


def sub(a, b):
    return "(" + a + " - " + b + ")"


def party_side(account_type, want):
    """Gross party balances: Schedule III shows debit-balance parties as receivables and
    credit-balance parties as advances, never the netted control account."""
    sign = "x.net" if want == "dr" else "-1 * x.net"
    return ("ifnull((select round(sum(greatest(0, " + sign + ")), 0) from ("
            "select gl.party, sum(gl.debit - gl.credit) net from `tabGL Entry` gl "
            "inner join `tabAccount` a on a.name = gl.account "
            "where gl.is_cancelled = 0 and gl.company = '" + COMPANY + "' "
            "and a.account_type = '" + account_type + "' and ifnull(gl.party,'') != '' "
            "and a.account_name not like '%%Retention%%' "
            "group by gl.party) x), 0)")


AR_CTRL = A("a.account_type = 'Receivable' and a.account_name not like '%%Retention%%'")
AP_CTRL = L("a.account_type = 'Payable'")
AR_GROSS = party_side("Receivable", "dr")
ADV_CUST = party_side("Receivable", "cr")
AP_GROSS = party_side("Payable", "cr")
ADV_SUPP = party_side("Payable", "dr")
AP_MSME = ("ifnull((select round(sum(pi.outstanding_amount),0) from `tabPurchase Invoice` pi "
           "inner join `tabSupplier` s on s.name = pi.supplier "
           "where pi.docstatus = 1 and ifnull(s.msme_type,'') != ''), 0)")
AP_OTHERS = sub(AP_GROSS, AP_MSME)

INCOME = bal("a.root_type = 'Income'")
EXPENSE = bal("a.root_type = 'Expense'", "asset")
SURPLUS = sub(INCOME, EXPENSE)
ASSET_TOTAL = add(bal("a.root_type = 'Asset'", "asset"), ADV_CUST, ADV_SUPP)
LIAB_TOTAL = add(bal("a.root_type in ('Liability','Equity')"), SURPLUS, ADV_CUST, ADV_SUPP)


def union(rows, value_label):
    parts = []
    for seq, note, label, val in rows:
        parts.append("select %d as seq, '%s' as note, '%s' as particulars, %s as amt"
                     % (seq, note, label.replace("'", "''"), val if val else "null"))
    return ('select\n'
            '  d.note as "Note::55",\n'
            '  d.particulars as "Particulars::450",\n'
            '  d.amt as "' + value_label + ':Currency:175",\n'
            '  null as "Previous year:Currency:150"\n'
            'from (\n  ' + "\n  union all ".join(parts) + '\n) d order by d.seq')


# ------------------------------------------------------------- share capital entry
def share_capital_entry():
    if frappe.db.exists("Journal Entry", {"user_remark": ("like", "Issue of 10,000 equity shares%")}):
        return "already booked"
    eq_parent = frappe.db.get_value("Account", {"company": COMPANY, "is_group": 1,
                                                "root_type": "Equity"}, "name")
    cap = acc(account_name="Share Capital") or ins({
        "doctype": "Account", "account_name": "Share Capital", "parent_account": eq_parent,
        "company": COMPANY, "root_type": "Equity", "account_type": "Equity"}).name
    bank = acc(account_type="Bank")
    n_shares = flt(frappe.db.sql("""select sum(no_of_shares) from `tabShare Transfer`
                                    where docstatus = 1""")[0][0])
    amt = n_shares * 10
    if not amt:
        return "no share transfers to book"
    j = ins({"doctype": "Journal Entry", "voucher_type": "Journal Entry", "company": COMPANY,
             "posting_date": "2026-04-01",
             "user_remark": "Issue of 10,000 equity shares of Rs 10 each, fully paid - subscribed "
                            "capital brought on to the books to match the share register "
                            "(authorised and paid-up capital Rs 1,00,000 per the MCA filing). "
                            "MOCK opening entry for the POC.",
             "accounts": [{"account": bank, "debit_in_account_currency": amt, "cost_center": cc()},
                          {"account": cap, "credit_in_account_currency": amt, "cost_center": cc()}]},
            submit=True)
    return "%s - share capital Rs %d now in the ledger" % (j.name, int(amt))


def balance_sheet():
    share = bal("a.root_type = 'Equity' and (a.account_name like '%%Share Capital%%' "
                "or a.account_name like '%%Capital Stock%%')")
    reserves = add(bal("a.root_type = 'Equity' and a.account_name not like '%%Share Capital%%' "
                       "and a.account_name not like '%%Capital Stock%%'"), SURPLUS)
    borrow = L("a.account_name like '%%Term Loan%%' or a.account_name like '%%Borrowing%%'")
    dtl = L("a.account_name like '%%Deferred Tax Liability%%'")
    gratuity = L("a.account_name like '%%Provision for Gratuity%%'")
    statutory = L("a.account_type != 'Payable' and (a.account_name like '%%Duties and Taxes%%' "
                  "or a.account_name like '%%GST%%' or a.account_name like '%%TDS%%' "
                  "or a.account_name like '%%Output Tax%%' or a.account_name like '%%Professional Tax%%' "
                  "or a.account_name like '%%Payroll Payable%%' or a.account_name like '%%Lease Liabilit%%')")
    srbnb = L("a.account_type = 'Stock Received But Not Billed' "
              "or a.account_name like '%%Received But Not Billed%%'")
    prov_it = L("a.account_name like '%%Provision for Income Tax%%'")
    liab_listed = add(share, reserves, borrow, dtl, gratuity, AP_MSME, AP_OTHERS, ADV_CUST,
                      statutory, srbnb, prov_it)
    liab_unmapped = sub(LIAB_TOTAL, liab_listed)

    ppe = A("(a.account_type in ('Fixed Asset','Accumulated Depreciation') "
            "or a.account_name like '%%Plant and Machinery%%' or a.account_name like '%%Furniture%%' "
            "or a.account_name like '%%Office Equipment%%' or a.account_name like '%%Computer%%') "
            "and a.account_name not like '%%Software%%'")
    intang = A("a.account_name like '%%Software%%'")
    cwip = A("a.account_type = 'Capital Work in Progress' or a.account_name like '%%CWIP%%'")
    dta = A("a.account_name like '%%Deferred Tax Asset%%'")
    stock = A("a.account_type = 'Stock' or a.account_name like '%%Stock In Hand%%' "
              "or a.account_name like '%%Work in Progress - Projects%%'")
    cash = A("a.account_type in ('Bank','Cash')")
    itc = A("a.account_type = 'Tax' or a.account_name like '%%Input Tax%%'")
    reten = A("a.account_name like '%%Retention%%'")
    asset_listed = add(ppe, intang, cwip, dta, stock, AR_GROSS, cash, itc, ADV_SUPP, reten)
    asset_unmapped = sub(ASSET_TOTAL, asset_listed)

    rows = [
        (10, "", "I. EQUITY AND LIABILITIES", None),
        (20, "", "1. Shareholders' funds", None),
        (30, "1", "        (a) Share capital", share),
        (40, "2", "        (b) Reserves and surplus", reserves),
        (50, "", "2. Non-current liabilities", None),
        (60, "3", "        (a) Long-term borrowings", borrow),
        (70, "4", "        (b) Deferred tax liabilities (net)", dtl),
        (80, "5", "        (c) Long-term provisions - gratuity", gratuity),
        (90, "", "3. Current liabilities", None),
        (100, "6", "        (a) Trade payables - micro and small enterprises", AP_MSME),
        (110, "6", "        (b) Trade payables - other than micro and small", AP_OTHERS),
        (120, "7", "        (c) Advances from customers", ADV_CUST),
        (130, "7", "        (d) Statutory dues - GST, TDS, PT, payroll", statutory),
        (140, "7", "        (e) Goods received but not billed", srbnb),
        (150, "8", "        (f) Short-term provisions - income tax", prov_it),
        (160, "", "        (g) Unclassified - to map into Schedule III", liab_unmapped),
        (170, "", "TOTAL", LIAB_TOTAL),
        (180, "", " ", None),
        (190, "", "II. ASSETS", None),
        (200, "", "1. Non-current assets", None),
        (210, "9", "        (a) Property, plant and equipment", ppe),
        (220, "9", "        (b) Intangible assets - software", intang),
        (230, "10", "        (c) Capital work-in-progress", cwip),
        (240, "4", "        (d) Deferred tax assets (net)", dta),
        (250, "", "2. Current assets", None),
        (260, "11", "        (a) Inventories including project work-in-progress", stock),
        (270, "12", "        (b) Trade receivables - gross", AR_GROSS),
        (280, "13", "        (c) Cash and cash equivalents", cash),
        (290, "14", "        (d) Input GST credit (ITC)", itc),
        (300, "14", "        (e) Advances to suppliers", ADV_SUPP),
        (310, "14", "        (f) Retention receivable", reten),
        (320, "", "        (g) Unclassified - to map into Schedule III", asset_unmapped),
        (330, "", "TOTAL", ASSET_TOTAL),
        (340, "", " ", None),
        (350, "", "Comparatives: first year on ERPNext - the previous-year column fills once the "
                  "Tally opening balances are migrated.", None),
    ]
    sql = union(rows, ASAT)
    name = qreport("MSCAST Balance Sheet (Schedule III)", "GL Entry", sql)
    res = frappe.db.sql(sql)
    for r in res:
        if r[2] is not None:
            log("  %-58s %14s" % (r[1][:58], r[2]))
    tot = [flt(r[2]) for r in res if r[1].strip() == "TOTAL"]
    diff = tot[1] - tot[0]
    return "%s | difference %s" % (name, "0 - balances" if abs(diff) < 1 else diff)


def profit_and_loss():
    rev = bal("a.root_type = 'Income' and a.account_name not like '%%Other Income%%' "
              "and a.account_name not like '%%Change in Work in Progress%%'")
    oth = bal("a.root_type = 'Income' and a.account_name like '%%Other Income%%'")
    wip_change = bal("a.root_type = 'Income' and a.account_name like '%%Change in Work in Progress%%'")
    stock_adj = E("a.account_type = 'Stock Adjustment' or a.account_name like '%%Stock Adjustment%%'")
    mat = E("a.account_type = 'Cost of Goods Sold' or a.account_name like '%%Cost of Goods%%' "
            "or a.account_name like '%%Freight%%'")
    emp = E("a.account_name like '%%Salar%%' or a.account_name like '%%Wage%%' "
            "or a.account_name like '%%Gratuity Expense%%' or a.account_name like '%%Staff%%' "
            "or a.account_name like '%%Bonus%%'")
    fin = E("a.account_name like '%%Interest%%' or a.account_name like '%%Bank Charge%%'")
    dep = E("a.account_name like '%%Depreciat%%' or a.account_name like '%%Amortis%%'")
    tax_c = E("a.account_name like '%%Income Tax Expense%%'")
    tax_d = E("a.account_name like '%%Deferred Tax Expense%%'")
    chg = sub(stock_adj, wip_change)     # stock adjustment + increase in project WIP
    other = sub(EXPENSE, add(mat, emp, fin, dep, tax_c, tax_d, stock_adj))
    tot_inc = add(rev, oth)
    tot_exp = add(mat, chg, emp, fin, dep, other)
    pbt = sub(tot_inc, tot_exp)
    pat = sub(pbt, add(tax_c, tax_d))
    shares = "(select ifnull(sum(no_of_shares),0) from `tabShare Transfer` where docstatus = 1)"
    rows = [
        (10, "15", "I.    Revenue from operations", rev),
        (20, "16", "II.   Other income", oth),
        (30, "", "III.  Total income", tot_inc),
        (40, "", "IV.   Expenses", None),
        (50, "17", "           Cost of materials consumed and bought-out", mat),
        (60, "11", "           Changes in inventories and work-in-progress", chg),
        (70, "18", "           Employee benefits expense", emp),
        (80, "19", "           Finance costs", fin),
        (90, "9", "           Depreciation and amortisation expense", dep),
        (100, "20", "           Other expenses", other),
        (110, "", "           Total expenses", tot_exp),
        (120, "", "V.    Profit before tax", pbt),
        (130, "", "VI.   Tax expense", None),
        (140, "8", "           (a) Current tax", tax_c),
        (150, "4", "           (b) Deferred tax", tax_d),
        (160, "", "VII.  Profit for the period", pat),
        (170, "21", "VIII. Earnings per equity share - basic and diluted (Rs)",
         "round(" + pat + " / nullif(" + shares + ", 0), 2)"),
    ]
    sql = union(rows, "Period to " + formatdate(TODAY, "dd MMM yyyy"))
    name = qreport("MSCAST Statement of Profit and Loss (Schedule III)", "GL Entry", sql)
    res = frappe.db.sql(sql)
    for r in res:
        if r[2] is not None:
            log("  %-58s %14s" % (r[1][:58], r[2]))
    pat_val = [flt(r[2]) for r in res if "Profit for the period" in r[1]][0]
    surplus = flt(frappe.db.sql("select " + SURPLUS)[0][0])
    log("  P&L profit %s vs ledger surplus %s -> %s" % (pat_val, surplus,
                                                        "tie" if abs(pat_val - surplus) < 1 else "DIFF"))
    return "%s | profit ties to the ledger: %s" % (name, abs(pat_val - surplus) < 1)


def ppe_opening():
    """The asset register holds 4 assets but two were created as existing assets with no
    accounting entry, so PPE showed nil on the balance sheet."""
    if frappe.db.exists("Journal Entry", {"user_remark": ("like", "Opening balances of property%")}):
        return "already booked"
    rows = frappe.db.sql("""select a.name, a.asset_name, a.asset_category, a.purchase_amount,
                                   ac.fixed_asset_account
        from `tabAsset` a
        left join `tabAsset Category Account` ac on ac.parent = a.asset_category
        where a.docstatus = 1 and ifnull(a.purchase_invoice,'') = ''
              and ifnull(a.purchase_receipt,'') = ''""", as_dict=True)
    if not rows:
        return "no unbooked assets"
    lines, total, names = [], 0.0, []
    for r in rows:
        target = r.fixed_asset_account or acc(account_name=("like", "%Plant and Machinery%"))
        if not target:
            continue
        lines.append({"account": target, "debit_in_account_currency": flt(r.purchase_amount),
                      "cost_center": cc()})
        total += flt(r.purchase_amount)
        names.append("%s %s" % (r.asset_name, int(flt(r.purchase_amount))))
    if not lines:
        return "no fixed asset accounts mapped"
    reserves = acc(account_name=("like", "%Reserves%")) or acc(root_type="Equity")
    lines.append({"account": reserves, "credit_in_account_currency": total, "cost_center": cc()})
    j = ins({"doctype": "Journal Entry", "voucher_type": "Journal Entry", "company": COMPANY,
             "posting_date": "2026-04-01",
             "user_remark": "Opening balances of property, plant and equipment already owned "
                            "before the ERP cut-over, brought on to the books against reserves: "
                            + "; ".join(names) + ". MOCK opening entry for the POC.",
             "accounts": lines}, submit=True)
    return "%s - PPE Rs %d capitalised (%d assets)" % (j.name, int(total), len(names))


def run():
    step("share capital brought on to the books", share_capital_entry)
    step("PPE opening balances", ppe_opening)
    step("Schedule III balance sheet (final)", balance_sheet)
    step("Schedule III statement of profit and loss (final)", profit_and_loss)
    frappe.clear_cache()
    log("SCRIPT 97 DONE")


run()
