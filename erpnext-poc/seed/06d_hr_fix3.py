"""MSCAST POC - 06d: fix component masters + holiday list, then structure, assignments, payroll."""
import frappe
from frappe.utils import add_days, add_months, nowdate, getdate, get_first_day, get_last_day

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
HL = "MSCAST 2026-27"
log = lambda m: print("[seed-06d] " + m, flush=True)
BASE = {"HR-EMP-00001": 150000, "HR-EMP-00002": 85000, "HR-EMP-00003": 62000,
        "HR-EMP-00004": 48000, "HR-EMP-00005": 42000, "HR-EMP-00006": 38000}
HOLIDAYS = [("2026-04-14", "Dr. Ambedkar Jayanti"), ("2026-05-01", "Maharashtra Day"),
            ("2026-08-15", "Independence Day"), ("2026-09-14", "Ganesh Chaturthi"),
            ("2026-10-02", "Gandhi Jayanti"), ("2026-11-08", "Diwali"),
            ("2027-01-26", "Republic Day"), ("2027-03-03", "Holi")]


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


def fix_masters():
    names = ["House Rent Allowance", "Conveyance Allowance", "Special Allowance",
             "Provident Fund", "Employee State Insurance", "Professional Tax"]
    out = []
    for n in names:
        if frappe.db.exists("Salary Component", n):
            frappe.db.set_value("Salary Component", n, "depends_on_payment_days", 0)
            out.append(n)
    return "depends_on_payment_days=0 for: " + ", ".join(out)


def holiday_list():
    if frappe.db.exists("Holiday List", HL):
        d = frappe.get_doc("Holiday List", HL)
        log("existing HL %s..%s holidays=%d" % (d.from_date, d.to_date, len(d.holidays)))
        if d.from_date and getdate(d.from_date) <= getdate("2026-09-18") <= getdate(d.to_date) and d.holidays:
            return "holiday list ok"
        frappe.delete_doc("Holiday List", HL, force=1, ignore_permissions=True)
    d = frappe.new_doc("Holiday List")
    d.holiday_list_name = HL
    d.from_date = "2026-04-01"
    d.to_date = "2027-03-31"
    d.weekly_off = "Sunday"
    # weekly offs
    cur = getdate("2026-04-01")
    end = getdate("2027-03-31")
    while cur <= end:
        if cur.weekday() == 6:
            d.append("holidays", {"holiday_date": cur, "description": "Sunday", "weekly_off": 1})
        cur = add_days(cur, 1)
        cur = getdate(cur)
    for dt, desc in HOLIDAYS:
        d.append("holidays", {"holiday_date": dt, "description": desc})
    d.flags.ignore_permissions = True
    d.insert()
    frappe.db.set_value("Company", COMPANY, "default_holiday_list", HL)
    for e in frappe.get_all("Employee", pluck="name"):
        frappe.db.set_value("Employee", e, "holiday_list", HL)
    return "%s created with %d holidays" % (HL, len(d.holidays))


def salary_structure():
    name = "MSCAST Staff 2026-27"
    if frappe.db.exists("Salary Structure", name):
        return name
    ss = frappe.get_doc({
        "doctype": "Salary Structure", "name": name, "company": COMPANY, "is_active": "Yes",
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
            {"salary_component": "Provident Fund", "amount_based_on_formula": 1,
             "formula": "min(B, 15000) * 0.12", "depends_on_payment_days": 0},
            {"salary_component": "Employee State Insurance", "amount_based_on_formula": 1,
             "formula": "gross_pay * 0.0075 if gross_pay <= 21000 else 0", "depends_on_payment_days": 0},
            {"salary_component": "Professional Tax", "amount_based_on_formula": 1,
             "formula": "200 if gross_pay > 10000 else (175 if gross_pay > 7500 else 0)",
             "depends_on_payment_days": 0},
        ],
    })
    ss.flags.ignore_permissions = True
    ss.insert()
    ss.submit()
    return name


def assignments(structure):
    n = 0
    for emp, base in BASE.items():
        if not frappe.db.exists("Employee", emp):
            continue
        if frappe.db.exists("Salary Structure Assignment", {"employee": emp, "docstatus": 1}):
            continue
        ins({"doctype": "Salary Structure Assignment", "employee": emp, "salary_structure": structure,
             "from_date": "2026-04-01", "base": base, "company": COMPANY}, submit=True)
        n += 1
    return "%d assignments" % n


def leaves():
    lt = "Casual Leave"
    made = 0
    for emp in BASE:
        if not frappe.db.exists("Employee", emp):
            continue
        if frappe.db.exists("Leave Allocation", {"employee": emp, "leave_type": lt, "docstatus": 1}):
            continue
        ins({"doctype": "Leave Allocation", "employee": emp, "leave_type": lt,
             "from_date": "2026-04-01", "to_date": "2027-03-31", "new_leaves_allocated": 12,
             "company": COMPANY}, submit=True)
        made += 1
    if not frappe.db.exists("Leave Application", {"employee": "HR-EMP-00006"}):
        d = add_days(TODAY, -25)
        ins({"doctype": "Leave Application", "employee": "HR-EMP-00006", "leave_type": lt,
             "from_date": d, "to_date": d, "company": COMPANY, "status": "Approved",
             "leave_approver": "Administrator", "description": "Personal work"}, submit=True)
    return "%d allocations + application" % made


def payroll_run():
    start = get_first_day(add_months(TODAY, -1))
    end = get_last_day(add_months(TODAY, -1))
    existing = frappe.db.get_value("Payroll Entry", {"start_date": start, "docstatus": ("<", 2)}, "name")
    if existing:
        pe = frappe.get_doc("Payroll Entry", existing)
    else:
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
        log("employees picked: %d" % len(pe.employees))
        pe.submit()
    try:
        pe.create_salary_slips()
    except Exception as e:
        log("create_salary_slips: " + repr(e)[:200])
    return "%s slips=%d" % (pe.name, frappe.db.count("Salary Slip", {"start_date": start}))


def submit_slips():
    start = get_first_day(add_months(TODAY, -1))
    done = 0
    for s in frappe.get_all("Salary Slip", filters={"start_date": start, "docstatus": 0}, pluck="name"):
        try:
            d = frappe.get_doc("Salary Slip", s)
            d.flags.ignore_permissions = True
            d.submit()
            done += 1
        except Exception as e:
            log("slip %s: %s" % (s, repr(e)[:200]))
    tot = frappe.db.sql("""select count(*), sum(gross_pay), sum(total_deduction), sum(net_pay)
                           from `tabSalary Slip` where start_date=%s and docstatus=1""", (start,))
    return "submitted %d; (count, gross, deductions, net)=%s" % (done, tot and tot[0])


def run():
    step("fix component masters", fix_masters)
    step("holiday list", holiday_list)
    s = step("salary structure", salary_structure)
    if isinstance(s, str):
        step("assignments", assignments, s)
    step("leaves", leaves)
    step("payroll run", payroll_run)
    step("submit slips", submit_slips)
    log("DONE")


run()
