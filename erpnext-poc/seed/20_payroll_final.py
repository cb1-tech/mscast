"""MSCAST POC - 20: payroll with explicit PF / ESIC / PT / TDS deduction components.

india_payroll's statutory engine needs company-level statutory config that is out of scope for
this POC, so the demo structure computes the same deductions with explicit formulas.
india_payroll stays installed for its registers (EPF/ESIC/PT), Form 16 and 24Q features.
"""
import frappe
from frappe.utils import add_months, nowdate, get_first_day, get_last_day

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
STRUCTURE = "MSCAST Staff 2026-27 (Demo)"
log = lambda m: print("[seed-20] " + m, flush=True)
BASE = {"HR-EMP-00001": 150000, "HR-EMP-00002": 85000, "HR-EMP-00003": 62000,
        "HR-EMP-00004": 48000, "HR-EMP-00005": 42000, "HR-EMP-00006": 38000}

DEDUCTIONS = [
    ("PF Employee 12%", "PFE", "min(B, 15000) * 0.12"),
    ("ESIC Employee 0.75%", "ESIE", "gross_pay * 0.0075 if gross_pay <= 21000 else 0"),
    ("Professional Tax MH", "PTMH", "200 if gross_pay > 10000 else (175 if gross_pay > 7500 else 0)"),
    ("TDS on Salary", "TDSS", "max(0, (gross_pay * 12 - 1200000)) * 0.15 / 12"),
]


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


def components():
    made = []
    for name, abbr, formula in DEDUCTIONS:
        if frappe.db.exists("Salary Component", name):
            frappe.db.set_value("Salary Component", name, {
                "amount_based_on_formula": 1, "formula": formula, "depends_on_payment_days": 0})
            continue
        ins({"doctype": "Salary Component", "salary_component": name, "salary_component_abbr": abbr,
             "type": "Deduction", "amount_based_on_formula": 1, "formula": formula,
             "depends_on_payment_days": 0, "remove_if_zero_valued": 1})
        made.append(name)
    return "created " + (", ".join(made) if made else "(all existed)")


def structure():
    if frappe.db.exists("Salary Structure", STRUCTURE):
        return STRUCTURE
    ss = frappe.get_doc({
        "doctype": "Salary Structure", "name": STRUCTURE, "company": COMPANY, "is_active": "Yes",
        "payroll_frequency": "Monthly", "currency": "INR",
        "payment_account": frappe.db.get_value(
            "Account", {"company": COMPANY, "account_type": "Bank", "is_group": 0}, "name"),
        "earnings": [
            {"salary_component": "Basic", "amount_based_on_formula": 1, "formula": "base * 0.5"},
            {"salary_component": "House Rent Allowance", "amount_based_on_formula": 1,
             "formula": "B * 0.4", "depends_on_payment_days": 0},
            {"salary_component": "Conveyance Allowance", "amount": 1600, "depends_on_payment_days": 0},
            {"salary_component": "Special Allowance", "amount_based_on_formula": 1,
             "formula": "base - (B + HRA + CA)", "depends_on_payment_days": 0},
        ],
        "deductions": [
            {"salary_component": n, "amount_based_on_formula": 1, "formula": f,
             "depends_on_payment_days": 0} for n, _a, f in DEDUCTIONS
        ],
    })
    ss.flags.ignore_permissions = True
    ss.insert()
    ss.submit()
    return STRUCTURE


def assignments():
    start = get_first_day(add_months(TODAY, -1))
    n = 0
    for emp, base in BASE.items():
        if not frappe.db.exists("Employee", emp):
            continue
        if frappe.db.exists("Salary Structure Assignment",
                            {"employee": emp, "salary_structure": STRUCTURE, "docstatus": 1}):
            continue
        d = ins({"doctype": "Salary Structure Assignment", "employee": emp,
                 "salary_structure": STRUCTURE, "from_date": start, "base": base,
                 "company": COMPANY, "employment_state": "Maharashtra"}, submit=True)
        n += 1
    return "%d assignments from %s" % (n, start)


def rerun():
    start = get_first_day(add_months(TODAY, -1))
    end = get_last_day(add_months(TODAY, -1))
    for s in frappe.get_all("Salary Slip", filters={"start_date": start}, fields=["name", "docstatus"]):
        d = frappe.get_doc("Salary Slip", s.name)
        d.flags.ignore_permissions = True
        if d.docstatus == 1:
            d.cancel()
        frappe.delete_doc("Salary Slip", s.name, force=1, ignore_permissions=True)
    for p in frappe.get_all("Payroll Entry", filters={"start_date": start}, fields=["name", "docstatus"]):
        d = frappe.get_doc("Payroll Entry", p.name)
        d.flags.ignore_permissions = True
        if d.docstatus == 1:
            d.cancel()
        frappe.delete_doc("Payroll Entry", p.name, force=1, ignore_permissions=True)
    frappe.db.commit()

    pe = frappe.get_doc({
        "doctype": "Payroll Entry", "company": COMPANY, "posting_date": end,
        "payroll_frequency": "Monthly", "start_date": start, "end_date": end,
        "currency": "INR", "exchange_rate": 1,
        "payroll_payable_account": frappe.db.get_value(
            "Account", {"company": COMPANY, "account_name": ("like", "%Payroll Payable%")}, "name"),
        "payment_account": frappe.db.get_value(
            "Account", {"company": COMPANY, "account_type": "Bank", "is_group": 0}, "name"),
    })
    pe.flags.ignore_permissions = True
    pe.insert()
    pe.fill_employee_details()
    pe.save()
    pe.submit()
    try:
        pe.create_salary_slips()
    except Exception as e:
        log("create_salary_slips: " + repr(e)[:200])
    frappe.db.commit()
    done = 0
    for s in frappe.get_all("Salary Slip", filters={"start_date": start, "docstatus": 0}, pluck="name"):
        try:
            d = frappe.get_doc("Salary Slip", s)
            d.flags.ignore_permissions = True
            d.submit()
            done += 1
        except Exception as e:
            log("slip %s: %s" % (s, repr(e)[:250]))
    for r in frappe.db.sql("""select employee_name, gross_pay, total_deduction, net_pay
                              from `tabSalary Slip` where start_date=%s and docstatus=1
                              order by net_pay desc""", (start,), as_dict=True):
        log("  %-24s gross %9.0f  ded %7.0f  net %9.0f" % (r.employee_name, r.gross_pay,
                                                           r.total_deduction, r.net_pay))
    slip = frappe.get_all("Salary Slip", filters={"start_date": start, "docstatus": 1},
                          order_by="net_pay asc", limit=1, pluck="name")
    if slip:
        d = frappe.get_doc("Salary Slip", slip[0])
        log("  %s deductions: %s" % (d.employee_name, [(x.salary_component, x.amount) for x in d.deductions]))
    return "%s, %d slips" % (pe.name, done)


def run():
    step("deduction components", components)
    step("demo salary structure", structure)
    step("assignments", assignments)
    step("re-run payroll", rerun)
    log("DONE")


run()
