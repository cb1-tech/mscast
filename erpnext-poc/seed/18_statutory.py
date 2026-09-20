"""MSCAST POC - 18: configure india_payroll statutory settings on Salary Structure Assignments,
let the app compute PF / ESI / PT / LWF, then re-run August payroll."""
import frappe
from frappe.utils import add_months, nowdate, get_first_day, get_last_day

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
STRUCTURE = "MSCAST Staff 2026-27"
STAT = ["Provident Fund", "Employee State Insurance", "Professional Tax"]
log = lambda m: print("[seed-18] " + m, flush=True)


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


def ssa_fields():
    names = [f.fieldname for f in frappe.get_meta("Salary Structure Assignment").fields
             if f.fieldname and any(k in f.fieldname for k in
                                    ("epf", "esi", "lwf", "pf", "professional", "state", "regime", "tax", "disab"))]
    log("SSA india_payroll fields: %s" % names)
    return ", ".join(names)


def configure_ssa():
    fields = {f.fieldname: f for f in frappe.get_meta("Salary Structure Assignment").fields}
    updates = {}
    if "employment_state" in fields:
        updates["employment_state"] = "Maharashtra"
    for f in ("epf_applicable", "esi_applicable", "pt_applicable", "professional_tax_applicable"):
        if f in fields:
            updates[f] = 1
    if "lwf_exempted" in fields:
        updates["lwf_exempted"] = 0
    for f in ("tax_regime", "income_tax_regime"):
        if f in fields:
            opts = (fields[f].options or "").split("\n")
            new = next((o for o in opts if "New" in o), None)
            if new:
                updates[f] = new
    n = 0
    for ssa in frappe.get_all("Salary Structure Assignment", filters={"docstatus": 1}, pluck="name"):
        frappe.db.set_value("Salary Structure Assignment", ssa, updates, update_modified=False)
        n += 1
    return "%d assignments updated with %s" % (n, updates)


def revert_formulas():
    for c in STAT:
        if frappe.db.exists("Salary Component", c):
            frappe.db.set_value("Salary Component", c, {"amount_based_on_formula": 0, "formula": ""})
    for row in frappe.get_all("Salary Detail", filters={"parent": STRUCTURE, "parentfield": "deductions"},
                              fields=["name", "salary_component"]):
        if row.salary_component in STAT:
            frappe.db.set_value("Salary Detail", row.name,
                                {"amount_based_on_formula": 0, "formula": ""}, update_modified=False)
    return "statutory components handed back to india_payroll"


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
    slip = frappe.get_all("Salary Slip", filters={"start_date": start, "docstatus": 1}, limit=1, pluck="name")
    if slip:
        d = frappe.get_doc("Salary Slip", slip[0])
        log("  sample earnings:   %s" % [(x.salary_component, x.amount) for x in d.earnings])
        log("  sample deductions: %s" % [(x.salary_component, x.amount) for x in d.deductions])
    return "%s, %d slips" % (pe.name, done)


def run():
    step("SSA fields", ssa_fields)
    step("configure SSA", configure_ssa)
    step("revert formulas", revert_formulas)
    step("re-run payroll", rerun)
    log("DONE")


run()
