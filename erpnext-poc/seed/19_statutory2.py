"""MSCAST POC - 19: enable EPF/ESI/PT/LWF via Payroll Settings company registrations, re-run payroll."""
import frappe
from frappe.utils import add_months, nowdate, get_first_day, get_last_day

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
log = lambda m: print("[seed-19] " + m, flush=True)


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


def company_settings():
    meta = frappe.get_meta("Payroll Settings")
    field = next((f.fieldname for f in meta.fields
                  if f.fieldtype == "Table" and f.options == "India Payroll Company Setting"), None)
    log("Payroll Settings child table field: %s" % field)
    if not field:
        return "child table not found"
    ps = frappe.get_single("Payroll Settings")
    rows = ps.get(field) or []
    if not any(r.company == COMPANY for r in rows):
        ps.append(field, {
            "company": COMPANY,
            "epf_establishment_code": "PN/PUN/0012345",
            "esic_registration_number": "34000123450000999",
            "professional_tax_registration_number": "27999888777P",
            "lwf_registration_number": "MH/LWF/00123",
        })
    ps.flags.ignore_permissions = True
    ps.save()
    try:
        from india_payroll.india_payroll.company_settings import is_statutory_enabled
        log("statutory enabled: epf=%s esi=%s pt=%s lwf=%s" % (
            is_statutory_enabled("epf", COMPANY), is_statutory_enabled("esi", COMPANY),
            is_statutory_enabled("pt", COMPANY), is_statutory_enabled("lwf", COMPANY)))
    except Exception as e:
        log("is_statutory_enabled check: " + repr(e)[:200])
    return "company registrations saved"


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
        log("  lowest-paid slip deductions: %s" % [(x.salary_component, x.amount) for x in d.deductions])
    return "%s, %d slips" % (pe.name, done)


def run():
    step("payroll company settings", company_settings)
    step("re-run payroll", rerun)
    log("DONE")


run()
