"""MSCAST POC - 06f: payable account type, holiday-list assignment per employee, payroll run."""
import frappe
from frappe.utils import add_days, add_months, nowdate, get_first_day, get_last_day

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
HL = "MSCAST 2026-27"
log = lambda m: print("[seed-06f] " + m, flush=True)


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


def payable_account():
    acc = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Payroll Payable%")}, "name")
    if not acc:
        return "no payroll payable account"
    frappe.db.set_value("Account", acc, "account_type", "Payable")
    return "%s set to Payable" % acc


def hla_per_employee():
    if not frappe.db.exists("DocType", "Holiday List Assignment"):
        return "not applicable"
    made = 0
    for e in frappe.get_all("Employee", fields=["name", "employee_name"]):
        if frappe.db.exists("Holiday List Assignment", {"assigned_to": e.name, "docstatus": ("<", 2)}):
            continue
        try:
            d = ins({"doctype": "Holiday List Assignment", "applicable_for": "Employee",
                     "assigned_to": e.name, "holiday_list": HL, "from_date": "2026-04-01"})
            if d.meta.is_submittable and d.docstatus == 0:
                d.submit()
            made += 1
        except Exception as ex:
            log("hla %s: %s" % (e.name, repr(ex)[:180]))
    return "%d employee assignments" % made


def leave_application():
    if frappe.db.exists("Leave Application", {"employee": "HR-EMP-00006"}):
        return "exists"
    d = add_days(TODAY, -25)
    ins({"doctype": "Leave Application", "employee": "HR-EMP-00006", "leave_type": "Casual Leave",
         "from_date": d, "to_date": d, "company": COMPANY, "status": "Approved",
         "leave_approver": "Administrator", "description": "Personal work"}, submit=True)
    return "one day CL approved on %s" % d


def payroll_run():
    start = get_first_day(add_months(TODAY, -1))
    end = get_last_day(add_months(TODAY, -1))
    existing = frappe.db.get_value("Payroll Entry", {"start_date": start, "docstatus": ("<", 2)}, "name")
    if existing:
        pe = frappe.get_doc("Payroll Entry", existing)
    else:
        payable = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Payroll Payable%")}, "name")
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
            log("slip %s: %s" % (s, repr(e)[:250]))
    rows = frappe.db.sql("""select employee_name, gross_pay, total_deduction, net_pay
                            from `tabSalary Slip` where start_date=%s and docstatus=1
                            order by net_pay desc""", (start,), as_dict=True)
    for r in rows:
        log("  %-24s gross %10.0f  ded %8.0f  net %10.0f" % (
            r.employee_name, r.gross_pay, r.total_deduction, r.net_pay))
    return "submitted %d slips" % done


def run():
    step("payroll payable account", payable_account)
    step("holiday list assignment per employee", hla_per_employee)
    step("leave application", leave_application)
    step("payroll run", payroll_run)
    step("submit slips", submit_slips)
    log("DONE")


run()
