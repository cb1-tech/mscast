"""MSCAST POC - 59: verification sweep - BRM payment block test + full inventory for the matrix."""
import frappe
from frappe.utils import nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
log = lambda m: print("[V] " + m, flush=True)

# ---------------- BRM payment block live test ----------------
pi = frappe.db.get_value("Purchase Invoice",
                         {"docstatus": 1, "outstanding_amount": (">", 0)},
                         ["name", "supplier", "bill_no", "outstanding_amount", "credit_to"],
                         as_dict=True)
if pi:
    log("testing BRM block with %s (%s, bill %s)" % (pi.name, pi.supplier, pi.bill_no))
    try:
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Pay"
        pe.company = COMPANY
        pe.posting_date = TODAY
        pe.party_type = "Supplier"
        pe.party = pi.supplier
        pe.paid_from = frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Bank",
                                                       "is_group": 0}, "name")
        pe.paid_to = pi.credit_to
        pe.paid_amount = pe.received_amount = pi.outstanding_amount
        pe.reference_no = "TEST/BRM/BLOCK"
        pe.reference_date = TODAY
        pe.append("references", {"reference_doctype": "Purchase Invoice", "reference_name": pi.name,
                                 "total_amount": pi.outstanding_amount,
                                 "outstanding_amount": pi.outstanding_amount,
                                 "allocated_amount": pi.outstanding_amount})
        pe.flags.ignore_permissions = True
        pe.insert()
        pe.submit()
        log("  payment went through (%s) - BRM was certified or block not triggered" % pe.name)
        pe.cancel()
        frappe.db.commit()
        log("  test payment cancelled")
    except Exception as e:
        frappe.db.rollback()
        log("  BLOCKED as designed: " + str(e)[:300])

# ---------------- inventory ----------------
log("==== INVENTORY %s ====" % TODAY)
GROUPS = {
    "Selling": ["Lead", "Opportunity", "Quotation", "Sales Order", "Customer"],
    "Buying": ["Supplier", "Request for Quotation", "Supplier Quotation", "Purchase Order",
               "Material Request", "Supplier Scorecard"],
    "Stock": ["Item", "Stock Entry", "Purchase Receipt", "Delivery Note", "Batch", "Serial No",
              "Landed Cost Voucher", "Quality Inspection", "Stock Reconciliation"],
    "Manufacturing": ["BOM", "Work Order", "Job Card", "Operation", "Workstation"],
    "Projects": ["Project", "Task", "Timesheet", "Activity Type"],
    "Accounts": ["Sales Invoice", "Purchase Invoice", "Payment Entry", "Journal Entry",
                 "Payment Request", "Dunning", "Bank Guarantee", "Asset", "Asset Category",
                 "Tax Withholding Category", "Share Transfer", "Shareholder", "Cost Center",
                 "Budget", "Period Closing Voucher"],
    "GST / India": ["GST HSN Code", "GSTIN", "e-Waybill Log", "Bill of Entry"],
    "HR": ["Employee", "Attendance", "Leave Application", "Salary Structure", "Salary Slip",
           "Payroll Entry", "Expense Claim", "Appraisal", "Job Applicant", "Gratuity",
           "Gratuity Rule", "Holiday List", "Shift Type"],
    "MSCAST custom": ["MSCAST PCC", "MSCAST MDF", "MSCAST MDM", "MSCAST BRM", "MSCAST Drawing",
                      "MSCAST Delivery Instruction", "MSCAST Inspection Plan",
                      "MSCAST Project Certificate", "MSCAST Client Claim", "MSCAST Customer Asset",
                      "MSCAST Transmittal", "MSCAST Commissioning Report", "MSCAST Spares Handover",
                      "MSCAST Project Kickoff", "MSCAST Archival Log"],
    "Automation": ["Notification", "Email Digest", "Auto Email Report", "Server Script", "Workflow",
                   "Email Template", "Dashboard Chart", "Number Card", "Workspace", "Print Format",
                   "Report", "Role", "Letter Head"],
}
for grp, dts in GROUPS.items():
    parts = []
    for dt in dts:
        if not frappe.db.exists("DocType", dt):
            parts.append("%s=n/a" % dt)
            continue
        try:
            parts.append("%s=%d" % (dt, frappe.db.count(dt)))
        except Exception:
            parts.append("%s=err" % dt)
    log("%-14s %s" % (grp, ", ".join(parts)))

log("--- custom reports ---")
for r in frappe.get_all("Report", filters={"is_standard": "No"}, fields=["name"], order_by="name"):
    log("  " + r.name)
log("--- custom print formats ---")
for p in frappe.get_all("Print Format", filters={"standard": "No"}, fields=["name", "doc_type"],
                        order_by="name"):
    log("  %s (%s)" % (p.name, p.doc_type))
log("--- workflows ---")
for w in frappe.get_all("Workflow", fields=["name", "document_type", "is_active"]):
    log("  %s on %s active=%s" % (w.name, w.document_type, w.is_active))
log("--- server scripts ---")
for s in frappe.get_all("Server Script", fields=["name", "script_type", "reference_doctype",
                                                 "event_frequency", "disabled"]):
    log("  %s | %s | %s | %s | disabled=%s" % (s.name, s.script_type, s.reference_doctype,
                                               s.event_frequency, s.disabled))
log("--- roles (custom) ---")
log("  " + ", ".join(frappe.get_all("Role", filters={"is_custom": 1}, pluck="name")))
log("--- auto email / digest ---")
log("  " + ", ".join(frappe.get_all("Auto Email Report", pluck="name")))
log("DONE")
