# -*- coding: utf-8 -*-
"""Three corrections, in the order their effects cascade.

ORDER MATTERS. PF changes payroll expense; B8 changes the stock adjustment;
both change profit before tax. So the tax provision is recomputed LAST, once
the other two have settled, or it is provided on a number that no longer exists.

1. PF OFF (MSCAST, 20 Sep 2026)
   EPF is mandatory only at 20+ employees under s.1(3) of the EPF & MP Act.
   MSCAST is under that, no employee carries a UAN, and MSCAST confirms the
   establishment is not registered. PF comes out of the salary structure and
   the slips are rebuilt without it.

   THE EXCEPTION, RECORDED DELIBERATELY: under s.1(5) an establishment that has
   ONCE been covered stays covered even if headcount later falls below 20. If
   MSCAST has ever held an EPF code, removing PF is non-compliance rather than
   correction, and s.14B damages and s.7Q interest follow. This is the one line
   the CA should confirm.

2. B8  Two opening-stock Stock Entries credited 24,74,400 to 5119 Stock
   Adjustment, an EXPENSE account, so the figure inflates profit. Opening stock
   belongs against 1910 Temporary Opening.

3. A5  The retention journal entry is internally correct but sits on the wrong
   contract: Konark Alloys is a spares customer with no project and no retention
   clause. It moves to a project invoice whose sales order actually carries one.
"""
import frappe
from frappe.utils import flt, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TAX_RATE = 0.25168          # s.115BAA, 22% + 10% surcharge + 4% cess
STOCK_ADJ = "5119 - Stock Adjustment - MSCAST"
TEMP_OPEN = "1910 - Temporary Opening - MSCAST"


def cost_centre():
    return frappe.db.get_value("Company", COMPANY, "cost_center") or \
        frappe.db.get_value("Cost Center", {"company": COMPANY, "is_group": 0}, "name")


def jv(lines, remark, posting_date=None):
    d = frappe.get_doc({
        "doctype": "Journal Entry", "voucher_type": "Journal Entry",
        "company": COMPANY, "posting_date": posting_date or nowdate(),
        "user_remark": remark, "accounts": lines,
    })
    d.flags.ignore_permissions = True
    d.insert()
    d.submit()
    return d.name


def pbt():
    """Profit before tax: income less expense, with the tax accounts taken out."""
    inc = flt(frappe.db.sql("""select sum(gl.credit-gl.debit) from `tabGL Entry` gl
        join `tabAccount` a on a.name=gl.account
        where a.root_type='Income' and gl.is_cancelled=0""")[0][0])
    exp = flt(frappe.db.sql("""select sum(gl.debit-gl.credit) from `tabGL Entry` gl
        join `tabAccount` a on a.name=gl.account
        where a.root_type='Expense' and gl.is_cancelled=0
          and a.name not like '%%Income Tax Expense%%'
          and a.name not like '%%Deferred Tax Expense%%'""")[0][0])
    return inc, exp, inc - exp


# ------------------------------------------------------------------ 1. PF off
PF_NAMES = ("Provident Fund", "PF Employee 12%", "Employer Provident Fund",
            "EPF Admin Charges", "Voluntary Provident Fund")


def pf_off():
    print("=" * 70)
    print("1. PF OFF - MSCAST is under the 20-employee threshold and unregistered")
    print("=" * 70)

    with_uan = frappe.db.sql("""select count(*) from `tabEmployee`
        where ifnull(provident_fund_account,'') <> ''""")[0][0]
    total = frappe.db.count("Employee")
    print("   evidence: %d of %d employees carry a UAN" % (with_uan, total))
    if with_uan:
        print("   *** SOME EMPLOYEES HAVE A UAN - the establishment may be registered.")
        print("   *** Under s.1(5) coverage then continues regardless of headcount.")
        print("   *** Stopping. Confirm with the CA before removing PF.")
        return False

    still_there = frappe.db.sql("""select count(*) from `tabSalary Detail` sd
        join `tabSalary Structure` ss on ss.name = sd.parent
        where sd.parenttype = 'Salary Structure'
          and sd.salary_component in %s""", (PF_NAMES,))[0][0]
    in_payroll = flt(frappe.db.sql("""select sum(sd.amount) from `tabSalary Detail` sd
        join `tabSalary Slip` s on s.name = sd.parent
        where s.docstatus = 1 and sd.salary_component in %s""", (PF_NAMES,))[0][0])
    if not still_there and abs(in_payroll) < 0.01:
        print("   PF is already out of the structures and out of submitted payroll")
        return True

    slips = frappe.get_all("Salary Slip", filters={"docstatus": 1},
                           fields=["name", "employee", "start_date", "end_date",
                                   "salary_structure"])
    print("   %d submitted salary slips to rebuild" % len(slips))

    pf_before = flt(frappe.db.sql("""select sum(sd.amount) from `tabSalary Detail` sd
        join `tabSalary Slip` ss on ss.name = sd.parent
        where ss.docstatus = 1 and sd.salary_component in %s""",
        (PF_NAMES,))[0][0])
    print("   PF currently inside submitted payroll: Rs %.2f" % pf_before)

    for s in slips:
        d = frappe.get_doc("Salary Slip", s.name)
        d.flags.ignore_permissions = True
        d.cancel()
    frappe.db.commit()
    print("   cancelled %d slips" % len(slips))

    structures = {s.salary_structure for s in slips if s.salary_structure}
    structures |= set(frappe.get_all("Salary Structure", filters={"docstatus": 1},
                                     pluck="name"))
    for name in structures:
        st = frappe.get_doc("Salary Structure", name)
        removed = []
        for table in ("earnings", "deductions"):
            keep = []
            for row in st.get(table) or []:
                if row.salary_component in PF_NAMES:
                    removed.append(row.salary_component)
                else:
                    keep.append(row)
            st.set(table, keep)
        if removed:
            was_submitted = st.docstatus == 1
            if was_submitted:
                st.flags.ignore_validate_update_after_submit = True
            st.flags.ignore_permissions = True
            st.save()
            print("   %s: removed %s" % (name, ", ".join(sorted(set(removed)))))
        else:
            print("   %s: no PF components present" % name)

    rebuilt = 0
    for s in slips:
        try:
            d = frappe.get_doc({
                "doctype": "Salary Slip", "employee": s.employee,
                "start_date": s.start_date, "end_date": s.end_date,
                "company": COMPANY,
            })
            d.flags.ignore_permissions = True
            d.insert()
            d.submit()
            rebuilt += 1
        except Exception as e:
            print("   could not rebuild a slip for %s: %s" % (s.employee, e))
    frappe.db.commit()
    print("   rebuilt and submitted %d slips, now without PF" % rebuilt)

    pf_after = flt(frappe.db.sql("""select sum(sd.amount) from `tabSalary Detail` sd
        join `tabSalary Slip` ss on ss.name = sd.parent
        where ss.docstatus = 1 and sd.salary_component in %s""",
        (PF_NAMES,))[0][0])
    print("   PF inside submitted payroll now: Rs %.2f" % pf_after)
    return True


# --------------------------------------------------------- 2. B8 stock adjustment
def b8():
    print("")
    print("=" * 70)
    print("2. B8 - opening stock out of the P&L")
    print("=" * 70)
    bal = flt(frappe.db.sql("""select sum(debit-credit) from `tabGL Entry`
        where account=%s and is_cancelled=0""", (STOCK_ADJ,))[0][0])
    print("   %s balance: %.2f" % (STOCK_ADJ, bal))
    if abs(bal) < 0.01:
        print("   already clear")
        return
    if not frappe.db.exists("Account", TEMP_OPEN):
        print("   %s does not exist - stopping" % TEMP_OPEN)
        return
    amt = abs(bal)
    cc = cost_centre()
    # bal is negative (a credit sitting in an expense account), so debit it back
    # out and park the counterpart against the opening-balance account where
    # opening stock belongs.
    name = jv([
        {"account": STOCK_ADJ, "debit_in_account_currency": amt,
         "credit_in_account_currency": 0, "cost_center": cc},
        {"account": TEMP_OPEN, "debit_in_account_currency": 0,
         "credit_in_account_currency": amt, "cost_center": cc},
    ], "B8: opening stock received via Stock Entry was credited to Stock "
       "Adjustment, an expense account, which inflated profit by this amount. "
       "Reclassified to Temporary Opening, where opening balances belong. "
       "Review finding B8, 20 Sep 2026.")
    print("   %s posted: DR %s %.2f / CR %s %.2f" % (name, STOCK_ADJ, amt, TEMP_OPEN, amt))
    after = flt(frappe.db.sql("""select sum(debit-credit) from `tabGL Entry`
        where account=%s and is_cancelled=0""", (STOCK_ADJ,))[0][0])
    print("   %s balance now: %.2f" % (STOCK_ADJ, after))


# ------------------------------------------------------------------ 3. A5 retention
def a5():
    print("")
    print("=" * 70)
    print("3. A5 - retention onto a contract that actually has a retention clause")
    print("=" * 70)
    ret_acc = frappe.db.get_value("Account", {"name": ["like", "%Retention Receivable%"]})
    if not ret_acc:
        print("   no Retention Receivable account")
        return
    rows = frappe.db.sql("""select gl.voucher_no, gl.party, sum(gl.debit-gl.credit) amt
        from `tabGL Entry` gl where gl.account=%s and gl.is_cancelled=0
        group by gl.voucher_no, gl.party""", (ret_acc,), as_dict=True)
    cc = cost_centre()
    debtors = frappe.db.get_value("Company", COMPANY, "default_receivable_account") or \
        frappe.db.get_value("Account", {"name": ["like", "%Debtors%"], "company": COMPANY})

    # Which invoices sit on an order that actually carries retention?
    eligible = frappe.db.sql("""
        select si.name, si.customer, si.project, si.base_grand_total,
               so.name so_name, so.retention_percent
        from `tabSales Invoice` si
        join `tabSales Order` so on so.project = si.project and so.docstatus = 1
        where si.docstatus = 1 and ifnull(si.project,'') <> ''
          and ifnull(so.retention_percent,0) > 0
        order by si.base_grand_total desc""", as_dict=True)
    print("   invoices on a contract with a retention clause:")
    for e in eligible:
        print("      %-16s %-34s %s %5.1f%%  Rs %12.2f"
              % (e.name, e.customer, e.so_name, e.retention_percent, e.base_grand_total))
    if not eligible:
        print("   none - leaving the ledger alone")
        return
    target = eligible[0]
    correct = round(target.base_grand_total * target.retention_percent / 100.0, 2)

    for r in rows:
        if abs(r.amt) < 0.01:
            continue
        on_contract = any(e.customer == r.party for e in eligible)
        print("   existing: %s  %s  Rs %.2f  %s"
              % (r.voucher_no, r.party, r.amt,
                 "on a retention contract" if on_contract else
                 "<- NO retention clause for this customer"))
        if on_contract:
            continue
        jv([
            {"account": ret_acc, "party_type": "Customer", "party": r.party,
             "debit_in_account_currency": 0,
             "credit_in_account_currency": abs(r.amt), "cost_center": cc},
            {"account": debtors, "party_type": "Customer", "party": r.party,
             "debit_in_account_currency": abs(r.amt),
             "credit_in_account_currency": 0, "cost_center": cc},
        ], "A5: reverses retention reclassified against %s, a customer with no "
           "project and no retention clause. Review finding A5." % r.party)
        print("      reversed")

    existing_on_target = flt(frappe.db.sql("""select sum(gl.debit-gl.credit)
        from `tabGL Entry` gl where gl.account=%s and gl.party=%s
        and gl.is_cancelled=0""", (ret_acc, target.customer))[0][0])
    if abs(existing_on_target - correct) < 0.01:
        print("   retention already correctly posted against %s" % target.customer)
        return

    # ERPNext validates a referenced row against the invoice's own receivable
    # account, so the reference belongs on the Debtors line only. The retention
    # line is the reclassification and carries no reference.
    inv_debit_to = frappe.db.get_value("Sales Invoice", target.name, "debit_to") or debtors
    name = jv([
        {"account": ret_acc, "party_type": "Customer", "party": target.customer,
         "debit_in_account_currency": correct, "credit_in_account_currency": 0,
         "cost_center": cc},
        {"account": inv_debit_to, "party_type": "Customer", "party": target.customer,
         "debit_in_account_currency": 0, "credit_in_account_currency": correct,
         "cost_center": cc, "reference_type": "Sales Invoice",
         "reference_name": target.name},
    ], "A5: retention of %.1f%% on %s per %s, reclassified from trade "
       "receivables. Not collectable until the performance certificate."
       % (target.retention_percent, target.name, target.so_name))
    print("   %s posted: %.1f%% of %s = Rs %.2f against %s"
          % (name, target.retention_percent, target.name, correct, target.customer))


# ------------------------------------------------------- 4. tax, computed last
def reprovision_tax():
    print("")
    print("=" * 70)
    print("4. tax provision, recomputed on the profit that now exists")
    print("=" * 70)
    inc, exp, profit = pbt()
    print("   income                     : %14.2f" % inc)
    print("   expense excl. tax           : %14.2f" % exp)
    print("   profit before tax           : %14.2f" % profit)

    cur_exp = "Income Tax Expense - MSCAST"
    cur_prov = "Provision for Income Tax - MSCAST"
    for a in (cur_exp, cur_prov):
        if not frappe.db.exists("Account", a):
            print("   %s missing - leaving tax alone" % a)
            return
    old = flt(frappe.db.sql("""select sum(debit-credit) from `tabGL Entry`
        where account=%s and is_cancelled=0""", (cur_exp,))[0][0])
    want = round(max(profit, 0) * TAX_RATE, 2)
    print("   provision currently posted  : %14.2f" % old)
    print("   at %.3f%% of the new profit : %14.2f" % (TAX_RATE * 100, want))

    delta = round(want - old, 2)
    if abs(delta) < 0.01:
        print("   no adjustment needed")
        return
    cc = cost_centre()
    if delta > 0:
        lines = [
            {"account": cur_exp, "debit_in_account_currency": delta,
             "credit_in_account_currency": 0, "cost_center": cc},
            {"account": cur_prov, "debit_in_account_currency": 0,
             "credit_in_account_currency": delta, "cost_center": cc},
        ]
    else:
        lines = [
            {"account": cur_prov, "debit_in_account_currency": -delta,
             "credit_in_account_currency": 0, "cost_center": cc},
            {"account": cur_exp, "debit_in_account_currency": 0,
             "credit_in_account_currency": -delta, "cost_center": cc},
        ]
    name = jv(lines,
              "Current tax reprovisioned at %.3f%% (s.115BAA) on profit before "
              "tax of %.2f, after removing PF and after reclassifying opening "
              "stock out of the P&L. ASSUMPTION: the rate and the s.115BAA "
              "election still require the CA's confirmation."
              % (TAX_RATE * 100, profit))
    print("   %s posted, adjustment of %.2f" % (name, delta))
    now = flt(frappe.db.sql("""select sum(debit-credit) from `tabGL Entry`
        where account=%s and is_cancelled=0""", (cur_exp,))[0][0])
    print("   income tax expense now      : %14.2f" % now)


def main():
    ok = pf_off()
    if not ok:
        print("")
        print("PF step stopped - not touching the ledger further.")
        return
    b8()
    a5()
    reprovision_tax()
    frappe.db.commit()

    print("")
    print("=" * 70)
    inc, exp, profit = pbt()
    tax = flt(frappe.db.sql("""select sum(debit-credit) from `tabGL Entry`
        where account like '%%Income Tax Expense%%' and is_cancelled=0""")[0][0])
    print("   profit before tax : %14.2f" % profit)
    print("   current tax       : %14.2f" % tax)
    print("   profit after tax  : %14.2f" % (profit - tax))
    diff = flt(frappe.db.sql("""select sum(debit)-sum(credit) from `tabGL Entry`
        where is_cancelled=0""")[0][0])
    print("   trial balance     : %14.2f  %s"
          % (diff, "nets to zero" if abs(diff) < 0.01 else "*** DOES NOT BALANCE ***"))
    print("done")


main()
