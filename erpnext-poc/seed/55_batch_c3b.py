"""MSCAST POC - 55: BATCH C3 fixes - retention JE on the invoice's own debit-to account, gratuity provision."""
import frappe
from frappe.utils import flt, nowdate, date_diff

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
log = lambda m: print("[C3b] " + m, flush=True)


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


def retention():
    if frappe.db.exists("Journal Entry", {"user_remark": ("like", "Retention retained%")}):
        return "already booked"
    ret = acc(account_name=("like", "%Retention Receivable%"))
    si = frappe.db.get_value("Sales Invoice", {"docstatus": 1, "is_return": 0,
                                               "outstanding_amount": (">", 0)},
                             ["name", "customer", "grand_total", "debit_to"], as_dict=True,
                             order_by="grand_total desc")
    amt = round(flt(si.grand_total) * 0.10, 2)
    j = ins({"doctype": "Journal Entry", "voucher_type": "Journal Entry", "company": COMPANY,
             "posting_date": TODAY,
             "user_remark": "Retention retained by customer @ 10 percent on invoice %s - "
                            "reclassified from trade receivable to retention receivable, "
                            "releasable against the performance certificate." % si.name,
             "accounts": [
                 {"account": ret, "debit_in_account_currency": amt, "cost_center": cc(),
                  "party_type": "Customer", "party": si.customer},
                 {"account": si.debit_to, "credit_in_account_currency": amt, "cost_center": cc(),
                  "party_type": "Customer", "party": si.customer,
                  "reference_type": "Sales Invoice", "reference_name": si.name}]},
            submit=True)
    return "%s - retention %s held on %s" % (j.name, amt, si.name)


def gratuity():
    made = []
    parent = frappe.db.get_value("Account", {"company": COMPANY, "is_group": 1,
                                             "account_name": ("like", "%Current Liabilities%")}, "name") \
        or frappe.db.get_value("Account", {"company": COMPANY, "is_group": 1, "root_type": "Liability"}, "name")
    prov = acc(account_name="Provision for Gratuity")
    if not prov:
        prov = ins({"doctype": "Account", "account_name": "Provision for Gratuity",
                    "parent_account": parent, "company": COMPANY, "root_type": "Liability"}).name
        made.append("Provision for Gratuity account")
    exp = acc(account_name="Gratuity Expense")
    if not exp:
        exp_parent = frappe.db.get_value("Account", {"company": COMPANY, "is_group": 1,
                                                     "root_type": "Expense"}, "name")
        exp = ins({"doctype": "Account", "account_name": "Gratuity Expense",
                   "parent_account": exp_parent, "company": COMPANY, "root_type": "Expense"}).name
        made.append("Gratuity Expense account")

    if frappe.db.exists("DocType", "Gratuity Rule") and \
            not frappe.db.exists("Gratuity Rule", "Indian Payment of Gratuity Act 1972"):
        try:
            ins({"doctype": "Gratuity Rule", "name": "Indian Payment of Gratuity Act 1972",
                 "calculate_gratuity_amount_based_on": "Current Slab",
                 "total_working_days_per_year": 26, "minimum_year_for_gratuity": 5,
                 "work_experience_calculation_method": "Round off Work Experience",
                 "gratuity_rule_slabs": [{"from_year": 0, "to_year": 0,
                                          "fraction_of_applicable_earnings": 0.577}]})
            made.append("Gratuity Rule (15/26 days per completed year)")
        except Exception as e:
            log("  gratuity rule skipped: " + repr(e)[:200])

    if frappe.db.exists("Journal Entry", {"user_remark": ("like", "Provision for gratuity%")}):
        made.append("provision already booked")
        return "; ".join(made)

    emps = frappe.get_all("Employee", filters={"status": "Active", "company": COMPANY},
                          fields=["name", "employee_name", "date_of_joining"])
    total, detail = 0.0, []
    for e in emps:
        basic = frappe.db.sql("""select sd.amount from `tabSalary Detail` sd
            inner join `tabSalary Slip` ss on ss.name = sd.parent
            where ss.employee = %s and sd.parentfield = 'earnings'
              and sd.salary_component like 'Basic%%'
            order by ss.start_date desc limit 1""", e.name)
        basic = flt(basic[0][0]) if basic else 25000.0
        years = max(0.5, (date_diff(TODAY, e.date_of_joining) or 0) / 365.0)
        amt = round(basic * 15 / 26 * years, 0)
        total += amt
        detail.append("%s %.1f yr Rs %d" % (e.employee_name, years, int(amt)))
    total = round(total, 0)
    if not total:
        return "; ".join(made) + "; no employees"
    j = ins({"doctype": "Journal Entry", "voucher_type": "Journal Entry", "company": COMPANY,
             "posting_date": TODAY,
             "user_remark": "Provision for gratuity as at %s - estimate at 15/26 days of last drawn "
                            "basic per completed year of service (Payment of Gratuity Act 1972). "
                            "Employees: %s" % (TODAY, "; ".join(detail)),
             "accounts": [{"account": exp, "debit_in_account_currency": total, "cost_center": cc()},
                          {"account": prov, "credit_in_account_currency": total, "cost_center": cc()}]},
            submit=True)
    made.append("%s provision Rs %d for %d employees" % (j.name, int(total), len(emps)))
    return "; ".join(made)


def run():
    step("retention reclassification", retention)
    step("gratuity rule and provision", gratuity)
    log("BATCH C3b DONE")


run()
