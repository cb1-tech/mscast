"""MSCAST POC - 98: reverse the bad PPE opening entry and post it correctly.

The first attempt took the fixed-asset account from whichever Asset Category Account row the
join returned (so everything landed in Software) and included the test bench, whose cost is
already in CWIP from PINV-26-00004 - a double count.
"""
import frappe
from frappe.utils import flt

COMPANY = "MSCAST Engineering Pvt Ltd"
log = lambda m: print("[98] " + m, flush=True)


def acc(**f):
    f.setdefault("company", COMPANY)
    f.setdefault("is_group", 0)
    return frappe.db.get_value("Account", f, "name")


def cc():
    return frappe.db.get_value("Cost Center", {"company": COMPANY, "is_group": 0}, "name")


bad = frappe.db.get_value("Journal Entry", {"user_remark": ("like", "Opening balances of property%"),
                                            "docstatus": 1}, "name")
if bad:
    d = frappe.get_doc("Journal Entry", bad)
    d.flags.ignore_permissions = True
    d.cancel()
    frappe.db.commit()
    log("cancelled %s" % bad)

log("--- assets and where their cost already sits ---")
assets = frappe.db.sql("""select name, asset_name, asset_category, purchase_amount,
                                 ifnull(purchase_invoice,'') pi, ifnull(purchase_receipt,'') pr
                          from `tabAsset` where docstatus = 1""", as_dict=True)
cwip_assets = set()
for a in assets:
    in_books = bool(a.pi or a.pr)
    if "CWIP" in (a.asset_category or ""):
        in_books = True          # cost already routed to the CWIP account by the capital invoice
        cwip_assets.add(a.name)
    log("  %-26s %-32s Rs %-10s already in books: %s"
        % (a.name, a.asset_name[:32], int(flt(a.purchase_amount)), in_books))

pm = acc(account_name=("like", "%Plant and Machinery%")) or acc(account_type="Fixed Asset")
sw = acc(account_name=("like", "%Software%"))
log("plant and machinery account: %s" % pm)
log("software account          : %s" % sw)

lines, names, total = [], [], 0.0
for a in assets:
    if a.pi or a.pr or a.name in cwip_assets:
        continue
    target = sw if "Software" in (a.asset_category or "") else pm
    if not target:
        continue
    lines.append({"account": target, "debit_in_account_currency": flt(a.purchase_amount),
                  "cost_center": cc()})
    names.append("%s Rs %d to %s" % (a.asset_name, int(flt(a.purchase_amount)),
                                     target.split(" - ")[0]))
    total += flt(a.purchase_amount)

if lines:
    reserves = acc(account_name=("like", "%Reserves%")) or acc(root_type="Equity")
    lines.append({"account": reserves, "credit_in_account_currency": total, "cost_center": cc()})
    j = frappe.get_doc({"doctype": "Journal Entry", "voucher_type": "Journal Entry",
                        "company": COMPANY, "posting_date": "2026-04-01",
                        "user_remark": "Opening balances of property, plant and equipment and "
                                       "intangibles owned before the ERP cut-over, brought on to "
                                       "the books against reserves: " + "; ".join(names)
                                       + ". The hydraulic test bench is excluded - its cost is "
                                         "already in CWIP from the capital purchase invoice. "
                                         "MOCK opening entry for the POC.",
                        "accounts": lines})
    j.flags.ignore_permissions = True
    j.insert()
    j.submit()
    frappe.db.commit()
    log("posted %s - Rs %d across %d assets" % (j.name, int(total), len(names)))
else:
    log("nothing to capitalise")

for r in frappe.db.sql("""select a.name, round(sum(gl.debit - gl.credit),0) net
    from `tabGL Entry` gl inner join `tabAccount` a on a.name = gl.account
    where gl.is_cancelled = 0 and (a.account_type in ('Fixed Asset','Capital Work in Progress')
       or a.account_name like '%%Software%%' or a.account_name like '%%Plant and Machinery%%')
    group by a.name having abs(net) > 0.5""", as_dict=True):
    log("  fixed asset ledger: %-44s %s" % (r.name[:44], r.net))
log("DONE")
