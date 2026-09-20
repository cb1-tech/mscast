"""MSCAST POC - 06e: create missing components, Holiday List Assignment (v16), structure, payroll."""
import frappe
from frappe.utils import add_days, add_months, nowdate, get_first_day, get_last_day

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
HL = "MSCAST 2026-27"
log = lambda m: print("[seed-06e] " + m, flush=True)
BASE = {"HR-EMP-00001": 150000, "HR-EMP-00002": 85000, "HR-EMP-00003": 62000,
        "HR-EMP-00004": 48000, "HR-EMP-00005": 42000, "HR-EMP-00006": 38000}


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
    for name, abbr, formula, amount in [
        ("Conveyance Allowance", "CA", None, 1600),
        ("Special Allowance", "SA", "base - (B + HRA + CA)", None),
    ]:
        if frappe.db.exists("Salary Component", name):
            frappe.db.set_value("Salary Component", name, "depends_on_payment_days", 0)
            continue
        ins({"doctype": "Salary Component", "salary_component": name, "salary_component_abbr": abbr,
             "type": "Earning", "is_tax_applicable": 1, "depends_on_payment_days": 0,
             "amount_based_on_formula": 1 if formula else 0, "formula": formula or "",
             "amount": amount or 0})
        made.append(name)
    return "created: " + (", ".join(made) or "none (already present)")


def holiday_assignment():
    if not frappe.db.exists("DocType", "Holiday List Assignment"):
        return "doctype not present in this version"
    meta = frappe.get_meta("Holiday List Assignment")
    fields = [f.fieldname for f in meta.fields]
    log("Holiday List Assignment fields: %s" % fields)
    if frappe.db.exists("Holiday List Assignment", {"holiday_list": HL}):
        return "assignment already exists"
    doc = {"doctype": "Holiday List Assignment", "holiday_list": HL}
    if "company" in fields:
        doc["company"] = COMPANY
    if "applicable_for" in fields:
        doc["applicable_for"] = "Company"
    if "from_date" in fields:
        doc["from_date"] = "2026-04-01"
    if "to_date" in fields:
        doc["to_date"] = "2027-03-31"
    if "effective_from" in fields:
        doc["effective_from"] = "2026-04-01"
    d = ins(doc)
    if d.meta.is_submittable:
        d.submit()
    return "created %s" % d.name


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
        try:
            ins({"doctype": "Leave Allocation", "employee": emp, "leave_type": lt,
                 "from_date": "2026-04-01", "to_date": "2027-03-31", "new_leaves_allocated": 12,
                 "company": COMPANY}, submit=True)
            made += 1
        except Exception as e:
            log("alloc %s: %s" % (emp, repr(e)[:150]))
    if not frappe.db.exists("Leave Application", {"employee": "HR-EMP-00006"}):
        try:
            d = add_days(TODAY, -25)
            ins({"doctype": "Leave Application", "employee": "HR-EMP-00006", "leave_type": lt,
                 "from_date": d, "to_date": d, "company": COMPANY, "status": "Approved",
                 "leave_approver": "Administrator", "description": "Personal work"}, submit=True)
        except Exception as e:
            log("leave application: %s" % repr(e)[:200])
    return "%d allocations" % made


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
        log("create_salary_slips: " + repr(e)[:250])
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
    step("salary components", components)
    step("holiday list assignment", holiday_assignment)
    s = step("salary structure", salary_structure)
    if isinstance(s, str):
        step("assignments", assignments, s)
    step("leaves", leaves)
    step("payroll run", payroll_run)
    step("submit slips", submit_slips)
    log("DONE")


run()
