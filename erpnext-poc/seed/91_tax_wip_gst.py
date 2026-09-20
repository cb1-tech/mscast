"""MSCAST POC - 91: AC-11 tax provisions, AC-17 project WIP valuation, AC-18 GST on closing
inventory, plus the AC-05 webhook fix.

ASSUMPTIONS (no CA input available - stated on the vouchers themselves):
  * Income tax at 25.168% (domestic company under s.115BAA incl. surcharge and cess).
  * Deferred tax on two timing differences: gratuity provision (allowed on payment - DTA) and
    depreciation (IT WDV faster than book SLM - DTL).
  * WIP valued at cost incurred on unbilled scope: bought-out billed by suppliers + material
    issued + engineering hours at Rs 450/hr + 12% works overhead, less cost of the billed portion.
"""
import frappe
from frappe.utils import add_days, flt, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
TAX_RATE = 25.168
LABOUR_RATE = 450.0
OVERHEAD_PCT = 12.0
log = lambda m: print("[91] " + m, flush=True)


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


def ensure_account(name, root_type, parent_like=None, account_type=None):
    existing = acc(account_name=name)
    if existing:
        return existing
    parent = None
    if parent_like:
        parent = frappe.db.get_value("Account", {"company": COMPANY, "is_group": 1,
                                                 "account_name": ("like", parent_like)}, "name")
    parent = parent or frappe.db.get_value("Account", {"company": COMPANY, "is_group": 1,
                                                       "root_type": root_type}, "name")
    d = {"doctype": "Account", "account_name": name, "parent_account": parent,
         "company": COMPANY, "root_type": root_type}
    if account_type:
        d["account_type"] = account_type
    return ins(d).name


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


# ------------------------------------------------------------------ AC-05 fix
CHAT_CARD = ('{"text": "*MSCAST ERP* - {{ doc.doctype }} {{ doc.name }} submitted. '
             'Value Rs {{ doc.get(\'grand_total\') or doc.get(\'paid_amount\') or 0 }}. '
             'Party {{ doc.get(\'customer\') or doc.get(\'supplier\') or doc.get(\'party\') or \'-\' }}."}')
PLACEHOLDER = "https://chat.googleapis.com/v1/spaces/REPLACE_SPACE/messages?key=REPLACE&token=REPLACE"


def chat_webhooks():
    made = []
    for dt, event, cond in [("Sales Invoice", "on_submit", "doc.grand_total > 500000"),
                            ("Purchase Order", "on_submit", "doc.grand_total > 500000"),
                            ("Payment Entry", "on_submit", "doc.paid_amount > 500000")]:
        nm = "MSCAST chat alert - %s" % dt
        if frappe.db.exists("Webhook", nm):
            continue
        ins({"doctype": "Webhook", "name": nm, "webhook_doctype": dt, "webhook_docevent": event,
             "request_url": PLACEHOLDER, "request_method": "POST", "request_structure": "JSON",
             "webhook_json": CHAT_CARD, "condition": cond, "enabled": 0})
        made.append(dt)
    return ("%s (disabled - paste the Google Chat space URL and enable)" % ", ".join(made)
            if made else "already exist")


# ------------------------------------------------------------------ AC-11
def tax_provisions():
    if frappe.db.exists("Journal Entry", {"user_remark": ("like", "Provision for income tax%")}):
        return "already booked"
    prov_it = ensure_account("Provision for Income Tax", "Liability", "%Current Liabilities%")
    tax_exp = ensure_account("Income Tax Expense", "Expense")
    dta = ensure_account("Deferred Tax Asset", "Asset", "%Current Assets%")
    dtl = ensure_account("Deferred Tax Liability", "Liability", "%Current Liabilities%")
    dt_exp = ensure_account("Deferred Tax Expense / (Income)", "Expense")

    pl = frappe.db.sql("""
        select
          sum(case when a.root_type = 'Income'  then gl.credit - gl.debit else 0 end) as income,
          sum(case when a.root_type = 'Expense' then gl.debit - gl.credit else 0 end) as expense
        from `tabGL Entry` gl inner join `tabAccount` a on a.name = gl.account
        where gl.is_cancelled = 0 and gl.company = %s""", COMPANY, as_dict=True)[0]
    pbt = flt(pl.income) - flt(pl.expense)
    current_tax = round(max(0.0, pbt) * TAX_RATE / 100, 0)
    log("  income %s, expense %s, PBT %s -> current tax %s" % (pl.income, pl.expense, pbt, current_tax))

    out = []
    if current_tax:
        j = ins({"doctype": "Journal Entry", "voucher_type": "Journal Entry", "company": COMPANY,
                 "posting_date": TODAY,
                 "user_remark": "Provision for income tax at %.3f percent (s.115BAA concessional "
                                "rate including surcharge and cess) on profit before tax of "
                                "Rs %s computed from the books to date. ASSUMPTION: the company "
                                "has opted for s.115BAA; to be confirmed with the auditor."
                                % (TAX_RATE, int(pbt)),
                 "accounts": [{"account": tax_exp, "debit_in_account_currency": current_tax,
                               "cost_center": cc()},
                              {"account": prov_it, "credit_in_account_currency": current_tax,
                               "cost_center": cc()}]}, submit=True)
        out.append("%s current tax Rs %d" % (j.name, current_tax))

    gratuity_prov = flt(frappe.db.sql("""select sum(gl.credit - gl.debit) from `tabGL Entry` gl
        where gl.is_cancelled = 0 and gl.account like '%%Provision for Gratuity%%'""")[0][0])
    dta_amt = round(gratuity_prov * TAX_RATE / 100, 0)
    dep_diff = 320000.0                      # mock: IT WDV depreciation ahead of book SLM
    dtl_amt = round(dep_diff * TAX_RATE / 100, 0)
    net = dta_amt - dtl_amt
    rows = []
    if dta_amt:
        rows.append({"account": dta, "debit_in_account_currency": dta_amt, "cost_center": cc()})
    if dtl_amt:
        rows.append({"account": dtl, "credit_in_account_currency": dtl_amt, "cost_center": cc()})
    if net > 0:
        rows.append({"account": dt_exp, "credit_in_account_currency": net, "cost_center": cc()})
    elif net < 0:
        rows.append({"account": dt_exp, "debit_in_account_currency": -net, "cost_center": cc()})
    if rows:
        j2 = ins({"doctype": "Journal Entry", "voucher_type": "Journal Entry", "company": COMPANY,
                  "posting_date": TODAY,
                  "user_remark": "Deferred tax on timing differences at %.3f percent: DTA on the "
                                 "gratuity provision of Rs %d (allowed on payment under s.43B) and "
                                 "DTL on depreciation of Rs %d (IT WDV ahead of book SLM). "
                                 "ASSUMPTION: depreciation difference is an estimate pending the "
                                 "tax depreciation schedule."
                                 % (TAX_RATE, int(gratuity_prov), int(dep_diff)),
                  "accounts": rows}, submit=True)
        out.append("%s deferred tax DTA %d / DTL %d" % (j2.name, dta_amt, dtl_amt))
    return "; ".join(out)


# ------------------------------------------------------------------ AC-17
WIP_SQL = """
select
  p.name                                                  as "Project:Link/Project:110",
  p.project_name                                          as "Description::240",
  round(ifnull((select sum(pii.amount) from `tabPurchase Invoice Item` pii
     inner join `tabPurchase Invoice` pi on pi.name = pii.parent
     where pi.docstatus = 1 and pii.project = p.name), 0), 0)
                                                          as "Bought-out billed:Currency:140",
  round(ifnull((select sum(sle.actual_qty * sle.valuation_rate) * -1 from `tabStock Ledger Entry` sle
     where sle.is_cancelled = 0 and sle.project = p.name and sle.actual_qty < 0), 0), 0)
                                                          as "Material issued:Currency:130",
  round(ifnull((select sum(td.hours) from `tabTimesheet Detail` td
     inner join `tabTimesheet` t on t.name = td.parent
     where t.docstatus = 1 and td.project = p.name), 0) * {rate}, 0)
                                                          as "Engineering cost:Currency:140",
  round((
    ifnull((select sum(pii.amount) from `tabPurchase Invoice Item` pii
       inner join `tabPurchase Invoice` pi on pi.name = pii.parent
       where pi.docstatus = 1 and pii.project = p.name), 0)
  + ifnull((select sum(sle.actual_qty * sle.valuation_rate) * -1 from `tabStock Ledger Entry` sle
       where sle.is_cancelled = 0 and sle.project = p.name and sle.actual_qty < 0), 0)
  + ifnull((select sum(td.hours) from `tabTimesheet Detail` td
       inner join `tabTimesheet` t on t.name = td.parent
       where t.docstatus = 1 and td.project = p.name), 0) * {rate}
  ) * {ovh}, 0)                                           as "Cost incurred incl. {ovhp}% overhead:Currency:190",
  round(ifnull((select sum(sii.amount) from `tabSales Invoice Item` sii
     inner join `tabSales Invoice` si on si.name = sii.parent
     where si.docstatus = 1 and si.is_return = 0 and sii.project = p.name), 0), 0)
                                                          as "Billed to customer:Currency:140",
  round(ifnull((select sum(so.grand_total) from `tabSales Order` so
     where so.docstatus = 1 and so.project = p.name), 0), 0)
                                                          as "Contract value:Currency:140",
  round(
    ifnull((select sum(so2.grand_total) from `tabSales Order` so2
       where so2.docstatus = 1 and so2.project = p.name), 0) = 0, 0)
                                                          as "_hidden:Int:1",
  round(greatest(0, (
    ifnull((select sum(pii.amount) from `tabPurchase Invoice Item` pii
       inner join `tabPurchase Invoice` pi on pi.name = pii.parent
       where pi.docstatus = 1 and pii.project = p.name), 0)
  + ifnull((select sum(sle.actual_qty * sle.valuation_rate) * -1 from `tabStock Ledger Entry` sle
       where sle.is_cancelled = 0 and sle.project = p.name and sle.actual_qty < 0), 0)
  + ifnull((select sum(td.hours) from `tabTimesheet Detail` td
       inner join `tabTimesheet` t on t.name = td.parent
       where t.docstatus = 1 and td.project = p.name), 0) * {rate}
  ) * {ovh} * (1 - least(1, ifnull((select sum(sii2.amount) from `tabSales Invoice Item` sii2
       inner join `tabSales Invoice` si2 on si2.name = sii2.parent
       where si2.docstatus = 1 and si2.is_return = 0 and sii2.project = p.name), 0)
     / nullif((select sum(so3.grand_total) from `tabSales Order` so3
       where so3.docstatus = 1 and so3.project = p.name), 0)))), 0)
                                                          as "WIP to carry:Currency:150"
from `tabProject` p
where p.company = '{company}'
order by p.name
"""


def wip_valuation():
    sql = (WIP_SQL.replace("{rate}", str(LABOUR_RATE))
           .replace("{ovh}", str(1 + OVERHEAD_PCT / 100))
           .replace("{ovhp}", str(int(OVERHEAD_PCT)))
           .replace("{company}", COMPANY))
    sql = "\n".join(l for l in sql.split("\n") if "_hidden" not in l)
    # drop the leftover expression line that fed the hidden column
    sql = sql.replace("""  round(
    ifnull((select sum(so2.grand_total) from `tabSales Order` so2
       where so2.docstatus = 1 and so2.project = p.name), 0) = 0, 0)
""", "")
    name = qreport("MSCAST Project WIP Valuation", "Project", sql,
                   ("System Manager", "Accounts Manager", "Projects Manager",
                    "MSCAST Statutory Auditor", "MSCAST Director"), total=True)
    rows = frappe.db.sql(sql, as_dict=True)
    for r in rows:
        log("  %s" % dict(r))
    wip_total = sum(flt(list(r.values())[-1]) for r in rows)

    wip_acc = ensure_account("Work in Progress - Projects", "Asset", "%Current Assets%")
    chg = ensure_account("Change in Work in Progress", "Income")
    if frappe.db.exists("Journal Entry", {"user_remark": ("like", "Work in progress carried%")}):
        return "%s (JV already booked)" % name
    if wip_total > 0:
        j = ins({"doctype": "Journal Entry", "voucher_type": "Journal Entry", "company": COMPANY,
                 "posting_date": TODAY,
                 "user_remark": "Work in progress carried at cost on unbilled scope as at %s - "
                                "bought-out billed by suppliers plus material issued plus "
                                "engineering hours at Rs %d/hr plus %d percent works overhead, "
                                "less the cost of the billed portion. ASSUMPTION: percentage of "
                                "completion measured by billing against contract value; method to "
                                "be confirmed with the auditor (decision D6)."
                                % (TODAY, int(LABOUR_RATE), int(OVERHEAD_PCT)),
                 "accounts": [{"account": wip_acc, "debit_in_account_currency": round(wip_total, 0),
                               "cost_center": cc()},
                              {"account": chg, "credit_in_account_currency": round(wip_total, 0),
                               "cost_center": cc()}]}, submit=True)
        return "%s + %s WIP Rs %d" % (name, j.name, int(wip_total))
    return "%s (no WIP to carry)" % name


# ------------------------------------------------------------------ AC-18
GST_STOCK_SQL = """
select
  b.warehouse                                             as "Warehouse:Link/Warehouse:200",
  b.item_code                                             as "Item:Link/Item:180",
  i.item_name                                             as "Description::240",
  i.gst_hsn_code                                          as "HSN::100",
  b.actual_qty                                            as "Qty:Float:90",
  i.stock_uom                                             as "UOM::70",
  round(b.stock_value, 0)                                 as "Stock Value (ex-GST):Currency:150",
  18                                                      as "GST Rate %:Int:90",
  round(b.stock_value * 0.18, 0)                          as "ITC embedded in the stock:Currency:180",
  case when b.warehouse like '%%Vendor%%' or b.warehouse like '%%Free Issue%%'
       then 'At job worker - ITC-04 return, return within 1 year (3 years for capital goods)'
       else 'Own premises - ITC already availed, no reversal while it stays taxable output' end
                                                          as "GST treatment::420"
from `tabBin` b
inner join `tabItem` i on i.name = b.item_code
where b.actual_qty != 0
order by b.warehouse, b.item_code
"""


def gst_on_stock():
    name = qreport("MSCAST GST on Closing Inventory (ITC and ITC-04)", "Bin", GST_STOCK_SQL,
                   ("System Manager", "Accounts Manager", "Stock Manager",
                    "MSCAST Statutory Auditor"), total=True)
    rows = frappe.db.sql(GST_STOCK_SQL)
    return "%s -> %d stock lines" % (name, len(rows))


def run():
    step("AC-05 chat webhooks", chat_webhooks)
    step("AC-11 income tax and deferred tax provisions", tax_provisions)
    step("AC-17 project WIP valuation", wip_valuation)
    step("AC-18 GST on closing inventory", gst_on_stock)
    frappe.clear_cache()
    log("SCRIPT 91 DONE")


run()
