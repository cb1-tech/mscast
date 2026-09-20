"""MSCAST POC - 17: make PF/ESI/PT actually compute, re-run August payroll."""
import frappe
from frappe.utils import add_months, nowdate, get_first_day, get_last_day

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
STRUCTURE = "MSCAST Staff 2026-27"
log = lambda m: print("[seed-17] " + m, flush=True)

FORMULAS = {
    "Provident Fund": "min(B, 15000) * 0.12",
    "Employee State Insurance": "gross_pay * 0.0075 if gross_pay <= 21000 else 0",
    "Professional Tax": "200 if gross_pay > 10000 else (175 if gross_pay > 7500 else 0)",
}


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


def masters():
    for comp, formula in FORMULAS.items():
        if not frappe.db.exists("Salary Component", comp):
            continue
        frappe.db.set_value("Salary Component", comp, {
            "amount_based_on_formula": 1, "formula": formula,
            "depends_on_payment_days": 0, "remove_if_zero_valued": 1,
        })
    return ", ".join(FORMULAS)


def structure_rows():
    n = 0
    for row in frappe.get_all("Salary Detail", filters={"parent": STRUCTURE, "parentfield": "deductions"},
                              fields=["name", "salary_component"]):
        f = FORMULAS.get(row.salary_component)
        if not f:
            continue
        frappe.db.set_value("Salary Detail", row.name, {
            "amount_based_on_formula": 1, "formula": f, "depends_on_payment_days": 0,
        }, update_modified=False)
        n += 1
    return "%d deduction rows updated" % n


def employee_ids():
    ids = {
        "HR-EMP-00001": ("100100100101", "PN/PUN/0012345/001", "3112345601"),
        "HR-EMP-00002": ("100100100102", "PN/PUN/0012345/002", "3112345602"),
        "HR-EMP-00003": ("100100100103", "PN/PUN/0012345/003", "3112345603"),
        "HR-EMP-00004": ("100100100104", "PN/PUN/0012345/004", "3112345604"),
        "HR-EMP-00005": ("100100100105", "PN/PUN/0012345/005", "3112345605"),
        "HR-EMP-00006": ("100100100106", "PN/PUN/0012345/006", "3112345606"),
    }
    for emp, (uan, pf, esic) in ids.items():
        if frappe.db.exists("Employee", emp):
            frappe.db.set_value("Employee", emp, {"uan_number": uan, "pf_name": pf,
                                                  "esic_card_no": esic})
    if not frappe.db.exists("India Payroll Company Setting", {"company": COMPANY}):
        d = frappe.get_doc({
            "doctype": "India Payroll Company Setting", "company": COMPANY,
            "esic_registration_number": "34000123450000999",
            "epf_establishment_code": "PN/PUN/0012345",
            "professional_tax_registration_number": "27999888777P",
            "lwf_registration_number": "MH/LWF/00123",
        })
        d.flags.ignore_permissions = True
        d.insert()
    return "statutory ids set for %d employees + company registrations" % len(ids)


def rerun_payroll():
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
            log("slip %s: %s" % (s, repr(e)[:200]))
    rows = frappe.db.sql("""select employee_name, gross_pay, total_deduction, net_pay
                            from `tabSalary Slip` where start_date=%s and docstatus=1
                            order by net_pay desc""", (start,), as_dict=True)
    for r in rows:
        log("  %-24s gross %9.0f  ded %7.0f  net %9.0f" % (r.employee_name, r.gross_pay,
                                                           r.total_deduction, r.net_pay))
    slip = frappe.get_all("Salary Slip", filters={"start_date": start, "docstatus": 1}, limit=1, pluck="name")
    if slip:
        d = frappe.get_doc("Salary Slip", slip[0])
        log("  sample deductions: %s" % [(x.salary_component, x.amount) for x in d.deductions])
    return "%s, %d slips submitted" % (pe.name, done)


def run():
    step("component masters", masters)
    step("structure rows", structure_rows)
    step("employee statutory ids", employee_ids)
    step("re-run payroll", rerun_payroll)
    log("DONE")


run()
