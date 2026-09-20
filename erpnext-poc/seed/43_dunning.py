"""MSCAST POC - 43: payment reminder (dunning) - zero interest, explicit fields."""
import frappe
from frappe.utils import nowdate, date_diff

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
log = lambda m: print("[A4] " + m, flush=True)

dt = frappe.db.get_value("Dunning Type", {}, "name")
frappe.db.set_value("Dunning Type", dt, {"rate_of_interest": 0, "dunning_fee": 0})
frappe.db.commit()
log("dunning type %s set to zero interest/fee" % dt)

if frappe.db.count("Dunning"):
    log("dunning already exists")
else:
    inv = frappe.db.get_value("Sales Invoice",
                              {"docstatus": 1, "outstanding_amount": (">", 0), "is_return": 0},
                              "name", order_by="posting_date asc")
    si = frappe.get_doc("Sales Invoice", inv)
    d = frappe.new_doc("Dunning")
    d.company = COMPANY
    d.posting_date = TODAY
    d.customer = si.customer
    d.dunning_type = dt
    d.rate_of_interest = 0
    d.dunning_fee = 0
    d.currency = si.currency
    d.conversion_rate = 1
    d.append("overdue_payments", {
        "sales_invoice": si.name, "due_date": si.due_date,
        "overdue_days": max(0, date_diff(TODAY, si.due_date)),
        "outstanding": si.outstanding_amount, "payment_amount": si.grand_total,
        "paid_amount": si.grand_total - si.outstanding_amount, "interest": 0,
    })
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    try:
        d.insert()
        log("created %s for %s (outstanding %s, %s days overdue)" % (
            d.name, si.customer, si.outstanding_amount, d.overdue_payments[0].overdue_days))
    except Exception as e:
        frappe.db.rollback()
        log("dunning failed: " + repr(e)[:300])
        log("fallback: creating a Notification for overdue invoices instead")
        if not frappe.db.exists("Notification", "MSCAST overdue invoice reminder"):
            n = frappe.get_doc({
                "doctype": "Notification", "name": "MSCAST overdue invoice reminder",
                "subject": "Invoice {{ doc.name }} is overdue", "document_type": "Sales Invoice",
                "event": "Days After", "date_changed": "due_date", "days_in_advance": 7,
                "enabled": 1, "channel": "Email",
                "condition": "doc.outstanding_amount > 0",
                "message": "Invoice {{ doc.name }} for {{ doc.customer }} ({{ doc.outstanding_amount }}) "
                           "is overdue. Please follow up.",
                "recipients": [{"receiver_by_role": "Accounts Manager"}],
            })
            n.flags.ignore_permissions = True
            n.insert()
            log("created overdue-invoice notification")
frappe.db.commit()
log("DONE")
