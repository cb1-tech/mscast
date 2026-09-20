"""MSCAST POC - 103: fix the two harness failures."""
import frappe
log = lambda m: print("[103] " + m, flush=True)

# T4 - the US 1099 print format ships with ERPNext and needs a fiscal_year argument.
# An Indian private company will never file a 1099; disable it rather than carry a format that
# throws when someone clicks Print.
if frappe.db.exists("Print Format", "IRS 1099 Form"):
    frappe.db.set_value("Print Format", "IRS 1099 Form", "disabled", 1)
    log("disabled the IRS 1099 Form print format (US-only, throws on render)")

# T5d - find the ledger entry with no cost centre
rows = frappe.db.sql("""select gl.name, gl.voucher_type, gl.voucher_no, gl.account, gl.debit,
                               gl.credit, gl.party_type, gl.party, a.account_type
    from `tabGL Entry` gl inner join `tabAccount` a on a.name = gl.account
    where gl.is_cancelled = 0 and ifnull(gl.cost_center,'') = ''""", as_dict=True)
for r in rows:
    log("  %s | %s %s | %s (%s) | Dr %s Cr %s | party %s"
        % (r.name, r.voucher_type, r.voucher_no, r.account, r.account_type, r.debit, r.credit,
           r.party or "-"))

cc = frappe.db.get_value("Cost Center", {"company": "MSCAST Engineering Pvt Ltd",
                                         "is_group": 0}, "name")
fixed = 0
for r in rows:
    # receivable/payable control lines legitimately carry no cost centre in ERPNext; everything
    # else should have one for project and department reporting
    if r.account_type in ("Receivable", "Payable"):
        continue
    frappe.db.set_value("GL Entry", r.name, "cost_center", cc, update_modified=False)
    fixed += 1
frappe.db.commit()
log("set the cost centre on %d entries (party control lines left alone by design)" % fixed)

left = frappe.db.sql("""select count(*) from `tabGL Entry` gl
    inner join `tabAccount` a on a.name = gl.account
    where gl.is_cancelled = 0 and ifnull(gl.cost_center,'') = ''
      and a.account_type not in ('Receivable','Payable')""")[0][0]
log("remaining non-party entries without a cost centre: %d" % left)
log("DONE")
