"""MSCAST POC - 06b: fix salary components, leave, expense claim; run payroll."""
import frappe
from frappe.utils import add_days, add_months, nowdate, get_first_day, get_last_day

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[seed-06b] " + m, flush=True)


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


EMPS = lambda: [(e.name, e.base) for e in frappe.db.sql(
    """select e.name, ifnull(a.base, 0) base from `tabEmployee` e
       left join `tabSalary Structure Assignment` a on a.employee = e.name and a.docstatus = 1
       where e.status = 'Active'""", as_dict=True)]

BASE = {"HR-EMP-00001": 150000, "HR-EMP-00002": 85000, "HR-EMP-00003": 62000,
        "HR-EMP-00004": 48000, "HR-EMP-00005": 42000, "HR-EMP-00006": 38000}


def fix_components():
    """Formula-based components cannot also depend on payment days."""
    n = 0
    for c in frappe.get_all("Salary Component", filters={"amount_based_on_formula": 1},
                            fields=["name", "depends_on_payment_days"]):
        if c.depends_on_payment_days:
            frappe.db.set_value("Salary Component", c.name, "depends_on_payment_days", 0)
            n += 1
    return "%d components fixed" % n


def salary_structure():
    name = "MSCAST Staff 2026-27"
    comp = {c.salary_component_abbr: c.name for c in frappe.get_all(
        "Salary Component", fields=["name", "salary_component_abbr"])}
    log("components: %s" % sorted(comp.items())[:12])
    if not frappe.db.exists("Salary Structure", name):
        ss = frappe.get_doc({
            "doctype": "Salary Structure", "name": name, "company": COMPANY,
            "is_active": "Yes", "payroll_frequency": "Monthly", "currency": "INR",
            "payment_account": frappe.db.get_value(
                "Account", {"company": COMPANY, "account_type": "Bank", "is_group": 0}, "name"),
            "earnings": [
                {"salary_component": "Basic", "amount_based_on_formula": 1,
                 "formula": "base * 0.5", "depends_on_payment_days": 0},
                {"salary_component": "House Rent Allowance", "amount_based_on_formula": 1,
                 "formula": "B * 0.4", "depends_on_payment_days": 0},
                {"salary_component": "Conveyance Allowance", "amount": 1600,
                 "depends_on_payment_days": 0},
                {"salary_component": "Special Allowance", "amount_based_on_formula": 1,
                 "formula": "base - (B + HRA + CA)", "depends_on_payment_days": 0},
            ],
            "deductions": [
                {"salary_component": "Provident Fund", "amount_based_on_formula": 1,
                 "formula": "min(B, 15000) * 0.12", "depends_on_payment_days": 0},
                {"salary_component": "ESI", "amount_based_on_formula": 1,
                 "formula": "gross_pay * 0.0075 if gross_pay <= 21000 else 0",
                 "depends_on_payment_days": 0},
                {"salary_component": "Professional Tax", "amount_based_on_formula": 1,
                 "formula": "200 if gross_pay > 10000 else (175 if gross_pay > 7500 else 0)",
                 "depends_on_payment_days": 0},
            ],
        })
        ss.flags.ignore_permissions = True
        ss.insert()
        ss.submit()
    for emp, base in BASE.items():
        if not frappe.db.exists("Employee", emp):
            continue
        if frappe.db.exists("Salary Structure Assignment", {"employee": emp, "docstatus": 1}):
            continue
        ins({"doctype": "Salary Structure Assignment", "employee": emp, "salary_structure": name,
             "from_date": "2026-04-01", "base": base, "company": COMPANY}, submit=True)
    return name


def leaves():
    lt = "Casual Leave"
    if not frappe.db.exists("Leave Type", lt):
        ins({"doctype": "Leave Type", "leave_type_name": lt, "max_leaves_allowed": 12})
    for emp in BASE:
        if not frappe.db.exists("Employee", emp):
            continue
        if frappe.db.exists("Leave Allocation", {"employee": emp, "leave_type": lt, "docstatus": 1}):
            continue
        ins({"doctype": "Leave Allocation", "employee": emp, "leave_type": lt,
             "from_date": "2026-04-01", "to_date": "2027-03-31", "new_leaves_allocated": 12,
             "company": COMPANY}, submit=True)
    emp0 = "HR-EMP-00006"
    if not frappe.db.exists("Leave Application", {"employee": emp0}):
        d = add_days(TODAY, -25)
        ins({"doctype": "Leave Application", "employee": emp0, "leave_type": lt,
             "from_date": d, "to_date": d, "company": COMPANY, "status": "Approved",
             "leave_approver": "Administrator", "description": "Personal work"}, submit=True)
    return "allocations + 1 application"


def expense_claim_type():
    for name in ("Travel", "Food", "Medical"):
        if not frappe.db.exists("Expense Claim Type", name):
            continue
        d = frappe.get_doc("Expense Claim Type", name)
        if not any(a.company == COMPANY for a in d.accounts):
            acc = (frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Travel%"), "is_group": 0}, "name")
                   or frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Miscellaneous Expenses%"), "is_group": 0}, "name")
                   or frappe.db.get_value("Account", {"company": COMPANY, "root_type": "Expense", "is_group": 0}, "name"))
            d.append("accounts", {"company": COMPANY, "default_account": acc})
            d.flags.ignore_permissions = True
            d.save()
    return "expense claim types mapped"


def expense_claim():
    if frappe.db.count("Expense Claim"):
        return "already exists"
    proj = frappe.db.get_value("Project", {"project_name": ("like", "CCM 2-Strand%")}, "name")
    ins({
        "doctype": "Expense Claim", "employee": "HR-EMP-00006", "company": COMPANY,
        "posting_date": add_days(TODAY, -6), "project": proj, "approval_status": "Approved",
        "payable_account": frappe.db.get_value(
            "Account", {"company": COMPANY, "account_type": "Payable", "is_group": 0}, "name"),
        "expenses": [{"expense_date": add_days(TODAY, -8), "expense_type": "Travel",
                      "description": "Site visit to Nagpur - travel and lodging (erection supervision)",
                      "amount": 18400, "sanctioned_amount": 18400}],
    }, submit=True)
    return "site travel claim booked to " + str(proj)


def payroll_run():
    start = get_first_day(add_months(TODAY, -1))
    end = get_last_day(add_months(TODAY, -1))
    if frappe.db.exists("Payroll Entry", {"start_date": start, "docstatus": ("<", 2)}):
        return "payroll entry already exists"
    payable = (frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Payroll Payable%")}, "name")
               or frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Payable", "is_group": 0}, "name"))
    pe = frappe.get_doc({
        "doctype": "Payroll Entry", "company": COMPANY, "posting_date": end,
        "payroll_frequency": "Monthly", "start_date": start, "end_date": end,
        "currency": "INR", "exchange_rate": 1, "payroll_payable_account": payable,
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
    n = frappe.db.count("Salary Slip", {"start_date": start})
    return "%s  slips=%d  period %s..%s" % (pe.name, n, start, end)


def submit_slips():
    start = get_first_day(add_months(TODAY, -1))
    slips = frappe.get_all("Salary Slip", filters={"start_date": start, "docstatus": 0}, pluck="name")
    done = 0
    for s in slips:
        try:
            d = frappe.get_doc("Salary Slip", s)
            d.flags.ignore_permissions = True
            d.submit()
            done += 1
        except Exception as e:
            log("slip %s: %s" % (s, repr(e)[:150]))
    total = frappe.db.sql("""select sum(gross_pay), sum(total_deduction), sum(net_pay)
                             from `tabSalary Slip` where start_date = %s and docstatus = 1""", (start,))
    return "submitted %d slips; gross/ded/net = %s" % (done, total and total[0])


def run():
    step("fix salary components", fix_components)
    step("salary structure", salary_structure)
    step("leaves", leaves)
    step("expense claim types", expense_claim_type)
    step("expense claim", expense_claim)
    step("payroll run", payroll_run)
    step("submit salary slips", submit_slips)
    log("DONE")


run()
