"""MSCAST POC - 06c: use india_payroll's own salary components, fix holiday list,
cost centre on expense claim, then run payroll."""
import frappe
from frappe.utils import add_days, add_months, nowdate, get_first_day, get_last_day

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
HL = "MSCAST 2026-27"
log = lambda m: print("[seed-06c] " + m, flush=True)
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


def diagnostics():
    comps = frappe.get_all("Salary Component", fields=["name", "salary_component_abbr", "type"],
                           order_by="type, name")
    for c in comps:
        log("  component: %-38s %-6s %s" % (c.name, c.salary_component_abbr, c.type))
    log("company holiday list: %s" % frappe.db.get_value("Company", COMPANY, "default_holiday_list"))
    for e in frappe.get_all("Employee", fields=["name", "employee_name", "holiday_list", "department"]):
        log("  employee: %s %s hl=%s" % (e.name, e.employee_name, e.holiday_list))
    log("cost centers: %s" % frappe.get_all("Cost Center", filters={"company": COMPANY, "is_group": 0}, pluck="name"))
    return "listed"


def find(*names):
    for n in names:
        if frappe.db.exists("Salary Component", n):
            return n
    return None


def ensure(name, ctype, formula=None, amount=None):
    if frappe.db.exists("Salary Component", name):
        return name
    ins({"doctype": "Salary Component", "salary_component": name, "type": ctype,
         "salary_component_abbr": "".join(w[0] for w in name.split())[:5].upper(),
         "depends_on_payment_days": 0,
         "is_tax_applicable": 1 if ctype == "Earning" else 0,
         "amount_based_on_formula": 1 if formula else 0,
         "formula": formula or "", "amount": amount or 0})
    return name


def holiday_lists():
    frappe.db.set_value("Company", COMPANY, "default_holiday_list", HL)
    n = 0
    for e in frappe.get_all("Employee", pluck="name"):
        if not frappe.db.get_value("Employee", e, "holiday_list"):
            frappe.db.set_value("Employee", e, "holiday_list", HL)
            n += 1
    return "company + %d employees set to %s" % (n, HL)


def salary_structure():
    basic = find("Basic") or ensure("Basic", "Earning", formula="base * 0.5")
    hra = find("House Rent Allowance", "HRA") or ensure("House Rent Allowance", "Earning", formula="B * 0.4")
    conv = ensure("Conveyance Allowance", "Earning", amount=1600)
    special = ensure("Special Allowance", "Earning", formula="base - (B + HRA + CA)")
    pf = find("Provident Fund", "Employee Provident Fund", "EPF Employee", "PF") or \
        ensure("Provident Fund", "Deduction", formula="min(B, 15000) * 0.12")
    esi = find("Employee State Insurance", "ESI") or \
        ensure("ESI", "Deduction", formula="gross_pay * 0.0075 if gross_pay <= 21000 else 0")
    pt = find("Professional Tax", "PT") or \
        ensure("Professional Tax", "Deduction",
               formula="200 if gross_pay > 10000 else (175 if gross_pay > 7500 else 0)")
    log("using components: %s / %s / %s / %s | %s / %s / %s" % (basic, hra, conv, special, pf, esi, pt))

    # india_payroll components may be statutory-driven; make ours formula-driven where we created them
    name = "MSCAST Staff 2026-27"
    if frappe.db.exists("Salary Structure", name):
        return name
    earnings = [
        {"salary_component": basic, "amount_based_on_formula": 1, "formula": "base * 0.5",
         "depends_on_payment_days": 0},
        {"salary_component": hra, "amount_based_on_formula": 1, "formula": "B * 0.4",
         "depends_on_payment_days": 0},
        {"salary_component": conv, "amount": 1600, "depends_on_payment_days": 0},
        {"salary_component": special, "amount_based_on_formula": 1,
         "formula": "base - (B + HRA + CA)", "depends_on_payment_days": 0},
    ]
    deductions = [
        {"salary_component": pf, "amount_based_on_formula": 1,
         "formula": "min(B, 15000) * 0.12", "depends_on_payment_days": 0},
        {"salary_component": esi, "amount_based_on_formula": 1,
         "formula": "gross_pay * 0.0075 if gross_pay <= 21000 else 0", "depends_on_payment_days": 0},
        {"salary_component": pt, "amount_based_on_formula": 1,
         "formula": "200 if gross_pay > 10000 else (175 if gross_pay > 7500 else 0)",
         "depends_on_payment_days": 0},
    ]
    ss = frappe.get_doc({
        "doctype": "Salary Structure", "name": name, "company": COMPANY, "is_active": "Yes",
        "payroll_frequency": "Monthly", "currency": "INR",
        "payment_account": frappe.db.get_value(
            "Account", {"company": COMPANY, "account_type": "Bank", "is_group": 0}, "name"),
        "earnings": earnings, "deductions": deductions,
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
        ins({"doctype": "Salary Structure Assignment", "employee": emp,
             "salary_structure": structure, "from_date": "2026-04-01", "base": base,
             "company": COMPANY}, submit=True)
        n += 1
    return "%d assignments" % n


def leaves():
    lt = "Casual Leave"
    for emp in BASE:
        if not frappe.db.exists("Employee", emp):
            continue
        if frappe.db.exists("Leave Allocation", {"employee": emp, "leave_type": lt, "docstatus": 1}):
            continue
        ins({"doctype": "Leave Allocation", "employee": emp, "leave_type": lt,
             "from_date": "2026-04-01", "to_date": "2027-03-31", "new_leaves_allocated": 12,
             "company": COMPANY}, submit=True)
    if not frappe.db.exists("Leave Application", {"employee": "HR-EMP-00006"}):
        d = add_days(TODAY, -25)
        ins({"doctype": "Leave Application", "employee": "HR-EMP-00006", "leave_type": lt,
             "from_date": d, "to_date": d, "company": COMPANY, "status": "Approved",
             "leave_approver": "Administrator", "description": "Personal work"}, submit=True)
    return "ok"


def expense_claim():
    if frappe.db.count("Expense Claim"):
        return "already exists"
    cc = frappe.db.get_value("Cost Center", {"company": COMPANY, "is_group": 0,
                                             "cost_center_name": ("not like", "%Main%")}, "name") \
        or frappe.db.get_value("Cost Center", {"company": COMPANY, "is_group": 0}, "name")
    proj = frappe.db.get_value("Project", {"project_name": ("like", "CCM 2-Strand%")}, "name")
    ins({
        "doctype": "Expense Claim", "employee": "HR-EMP-00006", "company": COMPANY,
        "posting_date": add_days(TODAY, -6), "project": proj, "cost_center": cc,
        "approval_status": "Approved",
        "payable_account": frappe.db.get_value(
            "Account", {"company": COMPANY, "account_type": "Payable", "is_group": 0}, "name"),
        "expenses": [{"expense_date": add_days(TODAY, -8), "expense_type": "Travel",
                      "description": "Site visit to Nagpur - travel and lodging (erection supervision)",
                      "amount": 18400, "sanctioned_amount": 18400, "cost_center": cc}],
    }, submit=True)
    return "claim booked to %s / %s" % (proj, cc)


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
        log("employees picked up: %d" % len(pe.employees))
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
    return "submitted %d; totals(count, gross, ded, net)=%s" % (done, tot and tot[0])


def run():
    step("diagnostics", diagnostics)
    step("holiday lists", holiday_lists)
    s = step("salary structure", salary_structure)
    if isinstance(s, str):
        step("assignments", assignments, s)
    step("leaves", leaves)
    step("expense claim", expense_claim)
    step("payroll run", payroll_run)
    step("submit slips", submit_slips)
    log("DONE")


run()
