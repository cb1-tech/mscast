"""MSCAST ERPNext POC - 06: HR, attendance, leave and Indian payroll demo.

Adaptive: reuses salary components created by india_payroll / hrms when present,
otherwise creates simple equivalents. All people are fictional.
"""
import frappe
from frappe.utils import add_days, add_months, getdate, nowdate, get_first_day, get_last_day, flt

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[seed-06] " + m, flush=True)


def step(name, fn, *a, **kw):
    try:
        out = fn(*a, **kw)
        frappe.db.commit()
        log("OK   " + name + ((" -> " + str(out)) if out else ""))
        return out or True
    except Exception as e:
        frappe.db.rollback()
        log("FAIL " + name + " :: " + repr(e)[:300])
        return None


def ins(doc, submit=False):
    d = frappe.get_doc(doc)
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    d.insert(ignore_if_duplicate=True)
    if submit:
        d.submit()
    return d


DEPTS = ["Engineering", "Projects", "Procurement", "Accounts", "Quality & Site"]
DESIGS = ["Managing Director", "Design Engineer", "Project Engineer",
          "Purchase Executive", "Accounts Executive", "Site Supervisor"]

# (first name, last name, designation, department, joining offset months, monthly CTC base)
PEOPLE = [
    ("Mustaque", "Chandankeri", "Managing Director", "Engineering", -180, 150000),
    ("Aiqaz", "Chandankeri", "Project Engineer", "Projects", -84, 85000),
    ("Rohit", "Kulkarni", "Design Engineer", "Engineering", -36, 62000),
    ("Sameer", "Lokhande", "Purchase Executive", "Procurement", -60, 48000),
    ("Anita", "Deshpande", "Accounts Executive", "Accounts", -30, 42000),
    ("Ganesh", "Pawar", "Site Supervisor", "Quality & Site", -18, 38000),
]

HOLIDAYS = [
    ("2026-04-14", "Dr. Ambedkar Jayanti"), ("2026-05-01", "Maharashtra Day"),
    ("2026-08-15", "Independence Day"), ("2026-09-14", "Ganesh Chaturthi"),
    ("2026-10-02", "Gandhi Jayanti"), ("2026-11-08", "Diwali"),
    ("2027-01-26", "Republic Day"), ("2027-03-03", "Holi"),
]


def org_structure():
    for d in DEPTS:
        name = d + " - " + ABBR
        if not frappe.db.exists("Department", name):
            ins({"doctype": "Department", "department_name": d, "company": COMPANY,
                 "parent_department": "All Departments"})
    for d in DESIGS:
        if not frappe.db.exists("Designation", d):
            ins({"doctype": "Designation", "designation_name": d})

    if not frappe.db.exists("Holiday List", "MSCAST 2026-27"):
        hl = frappe.new_doc("Holiday List")
        hl.holiday_list_name = "MSCAST 2026-27"
        hl.from_date = "2026-04-01"
        hl.to_date = "2027-03-31"
        hl.weekly_off = "Sunday"
        hl.flags.ignore_permissions = True
        hl.insert()
        hl.get_weekly_off_dates()
        for d, desc in HOLIDAYS:
            hl.append("holidays", {"holiday_date": d, "description": desc})
        hl.save()
    frappe.db.set_value("Company", COMPANY, "default_holiday_list", "MSCAST 2026-27")


def employees():
    made = []
    for first, last, desig, dept, joff, base in PEOPLE:
        existing = frappe.db.get_value("Employee", {"employee_name": first + " " + last}, "name")
        if existing:
            made.append((existing, base))
            continue
        e = ins({
            "doctype": "Employee", "first_name": first, "last_name": last,
            "company": COMPANY, "status": "Active", "gender": "Female" if first == "Anita" else "Male",
            "date_of_birth": add_months(TODAY, -12 * 34), "date_of_joining": add_months(TODAY, joff),
            "department": dept + " - " + ABBR, "designation": desig,
            "holiday_list": "MSCAST 2026-27", "employment_type": "Full-time",
            "salary_mode": "Bank", "salary_currency": "INR",
        })
        made.append((e.name, base))
    log("employees: %d" % len(made))
    return made


def attendance(emps):
    """Mark the last 12 working days."""
    if frappe.db.count("Attendance") > 10:
        return
    hol = set(frappe.get_all("Holiday", filters={"parent": "MSCAST 2026-27"}, pluck="holiday_date"))
    made = 0
    for emp, _base in emps:
        d, n = getdate(TODAY), 0
        while n < 12:
            d = add_days(d, -1)
            if getdate(d) in hol or getdate(d).weekday() == 6:
                continue
            status = "On Leave" if (n == 3 and emp.endswith("4")) else "Present"
            try:
                ins({"doctype": "Attendance", "employee": emp, "attendance_date": d,
                     "status": status, "company": COMPANY}, submit=True)
                made += 1
            except Exception:
                pass
            n += 1
    log("attendance rows: %d" % made)


def leaves(emps):
    lt = "Casual Leave" if frappe.db.exists("Leave Type", "Casual Leave") else None
    if not lt:
        ins({"doctype": "Leave Type", "leave_type_name": "Casual Leave", "max_leaves_allowed": 12,
             "is_earned_leave": 0, "include_holiday": 0})
        lt = "Casual Leave"
    if not frappe.db.exists("Leave Period", "MSCAST 2026-27"):
        ins({"doctype": "Leave Period", "from_date": "2026-04-01", "to_date": "2027-03-31",
             "company": COMPANY, "is_active": 1, "name": "MSCAST 2026-27"})
    for emp, _b in emps:
        if frappe.db.exists("Leave Allocation", {"employee": emp, "leave_type": lt, "docstatus": 1}):
            continue
        ins({"doctype": "Leave Allocation", "employee": emp, "leave_type": lt,
             "from_date": "2026-04-01", "to_date": "2027-03-31", "new_leaves_allocated": 12,
             "company": COMPANY}, submit=True)
    emp0 = emps[-1][0]
    if not frappe.db.exists("Leave Application", {"employee": emp0}):
        ins({"doctype": "Leave Application", "employee": emp0, "leave_type": lt,
             "from_date": add_days(TODAY, -9), "to_date": add_days(TODAY, -9),
             "company": COMPANY, "status": "Approved", "leave_approver": "Administrator",
             "description": "Personal work"}, submit=True)


# ---------------------------------------------------------------- payroll
def find_component(patterns, ctype):
    for p in patterns:
        n = frappe.db.get_value("Salary Component", {"name": ("like", p), "type": ctype}, "name")
        if n:
            return n
    return None


def ensure_component(name, ctype, formula=None, amount=None, **kw):
    if frappe.db.exists("Salary Component", name):
        return name
    d = {
        "doctype": "Salary Component", "salary_component": name, "type": ctype,
        "salary_component_abbr": "".join(w[0] for w in name.split())[:5].upper(),
        "depends_on_payment_days": 1, "is_tax_applicable": 1 if ctype == "Earning" else 0,
    }
    if formula:
        d.update({"amount_based_on_formula": 1, "formula": formula})
    elif amount is not None:
        d["amount"] = amount
    d.update(kw)
    ins(d)
    return name


def salary_structure(emps):
    basic = ensure_component("Basic", "Earning", formula="base * 0.5")
    hra = ensure_component("House Rent Allowance", "Earning", formula="B * 0.4")
    conv = ensure_component("Conveyance Allowance", "Earning", amount=1600)
    special = ensure_component("Special Allowance", "Earning", formula="base - (B + HRA + CA)")

    pf = find_component(["%Provident Fund%", "%PF%"], "Deduction") or \
        ensure_component("Provident Fund", "Deduction", formula="min(B, 15000) * 0.12")
    esi = find_component(["%ESI%", "%Employee State Insurance%"], "Deduction") or \
        ensure_component("ESI", "Deduction", formula="gross_pay * 0.0075 if gross_pay <= 21000 else 0")
    pt = find_component(["%Professional Tax%", "%PT%"], "Deduction") or \
        ensure_component("Professional Tax", "Deduction",
                         formula="200 if gross_pay > 10000 else (175 if gross_pay > 7500 else 0)")

    name = "MSCAST Staff 2026-27"
    if not frappe.db.exists("Salary Structure", name):
        ss = frappe.get_doc({
            "doctype": "Salary Structure", "name": name, "company": COMPANY,
            "is_active": "Yes", "payroll_frequency": "Monthly", "currency": "INR",
            "salary_slip_based_on_timesheet": 0,
            "payment_account": frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Bank", "is_group": 0}, "name"),
            "earnings": [
                {"salary_component": basic, "amount_based_on_formula": 1, "formula": "base * 0.5"},
                {"salary_component": hra, "amount_based_on_formula": 1, "formula": "B * 0.4"},
                {"salary_component": conv, "amount": 1600},
                {"salary_component": special, "amount_based_on_formula": 1, "formula": "base - (B + HRA + CA)"},
            ],
            "deductions": [
                {"salary_component": pf, "amount_based_on_formula": 1, "formula": "min(B, 15000) * 0.12"},
                {"salary_component": esi, "amount_based_on_formula": 1,
                 "formula": "gross_pay * 0.0075 if gross_pay <= 21000 else 0"},
                {"salary_component": pt, "amount_based_on_formula": 1,
                 "formula": "200 if gross_pay > 10000 else (175 if gross_pay > 7500 else 0)"},
            ],
        })
        ss.flags.ignore_permissions = True
        ss.insert()
        ss.submit()
    for emp, base in emps:
        if frappe.db.exists("Salary Structure Assignment", {"employee": emp, "docstatus": 1}):
            continue
        ins({"doctype": "Salary Structure Assignment", "employee": emp, "salary_structure": name,
             "from_date": "2026-04-01", "base": base, "company": COMPANY,
             "income_tax_slab": frappe.db.get_value("Income Tax Slab", {"company": COMPANY}, "name")},
            submit=True)
    return name


def payroll_run(structure):
    start = get_first_day(add_months(TODAY, -1))
    end = get_last_day(add_months(TODAY, -1))
    if frappe.db.exists("Payroll Entry", {"start_date": start, "docstatus": ("<", 2)}):
        return
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
    pe.create_salary_slips()
    log("payroll entry: %s (%s to %s), slips: %d" % (
        pe.name, start, end, frappe.db.count("Salary Slip", {"start_date": start})))


def expense_claim(emps):
    if frappe.db.count("Expense Claim"):
        return
    emp = emps[-1][0]
    etype = frappe.db.get_value("Expense Claim Type", {"name": ("like", "Travel%")}) or \
        frappe.db.get_value("Expense Claim Type", {}, "name")
    proj = frappe.db.get_value("Project", {"project_name": ("like", "CCM 2-Strand%")}, "name")
    ins({
        "doctype": "Expense Claim", "employee": emp, "company": COMPANY,
        "posting_date": add_days(TODAY, -6), "project": proj,
        "approval_status": "Approved",
        "payable_account": frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Payable", "is_group": 0}, "name"),
        "expenses": [{
            "expense_date": add_days(TODAY, -8), "expense_type": etype,
            "description": "Site visit to Nagpur - travel and lodging (erection supervision)",
            "amount": 18400, "sanctioned_amount": 18400,
        }],
    })
    log("expense claim created for project " + str(proj))


def run():
    step("org structure", org_structure)
    emps = step("employees", employees)
    if isinstance(emps, list):
        step("attendance", attendance, emps)
        step("leaves", leaves, emps)
        s = step("salary structure", salary_structure, emps)
        if isinstance(s, str):
            step("payroll run", payroll_run, s)
        step("expense claim", expense_claim, emps)
    log("DONE")


run()
