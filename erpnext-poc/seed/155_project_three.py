# -*- coding: utf-8 -*-
"""A third project, at the far end of its life.

PROJ-0001 is mid-build, PROJ-0002 has just started. Neither shows what closing a
job looks like: dispatched, invoiced, commissioned, certificate received,
retention released. This adds that, so the demo covers the whole arc.

It is the revamp MSCAST won from Ambika Steel - the same job that appears in the
bid history, which is the point: the records join up.
"""
import frappe

GST_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def gstin(state_code, pan):
    base = "%s%s1Z" % (state_code, pan)
    total = 0
    for i, ch in enumerate(base):
        v = GST_ALPHABET.index(ch)
        f = 2 if i % 2 else 1
        p = v * f
        total += p // 36 + p % 36
    return base + GST_ALPHABET[(36 - total % 36) % 36]


CUST = "Ambika Steel Rolling Mills"
PROJ = "PROJ-0003"
company = frappe.defaults.get_global_default("company")

# ------------------------------------------------------------------- customer
if not frappe.db.exists("Customer", CUST):
    t = frappe.get_all("Customer", fields=["customer_group", "territory"], limit=1)[0]
    c = frappe.new_doc("Customer")
    c.customer_name = CUST
    c.customer_type = "Company"
    c.customer_group = t.customer_group
    c.territory = t.territory
    if frappe.get_meta("Customer").has_field("gst_category"):
        c.gst_category = "Registered Regular"
    c.flags.ignore_permissions = True
    c.insert()

    a = frappe.new_doc("Address")
    a.address_title = CUST
    a.address_type = "Billing"
    a.address_line1 = "Plot 31, Waluj MIDC"
    a.city = "Chhatrapati Sambhajinagar"
    a.state = "Maharashtra"
    a.country = "India"
    a.pincode = "431136"
    if frappe.get_meta("Address").has_field("gstin"):
        a.gstin = gstin("27", "AANCA1234P")
        a.gst_state = "Maharashtra"
    a.append("links", {"link_doctype": "Customer", "link_name": CUST})
    a.flags.ignore_permissions = True
    a.insert()
    print("customer created:", CUST)

# -------------------------------------------------------------------- project
if not frappe.db.exists("Project", PROJ):
    p = frappe.new_doc("Project")
    p.project_name = "Caster revamp - Ambika Steel"
    p.customer = CUST
    p.status = "Open"
    p.expected_start_date = "2026-08-05"
    p.expected_end_date = "2026-09-12"
    p.percent_complete_method = "Manual"
    p.percent_complete = 100
    p.company = company
    p.flags.ignore_permissions = True
    p.insert()
    PROJ = p.name
    print("project created:", PROJ, "-", p.project_name)
else:
    print("project exists:", PROJ)

ITEMS = [("SRV-REVAMP", 250, 13500), ("SRV-COMMISSION", 40, 11500)]

# ---------------------------------------------------------------- sales order
so_name = frappe.db.get_value("Sales Order", {"project": PROJ, "docstatus": 1}, "name")
if not so_name:
    so = frappe.new_doc("Sales Order")
    so.customer = CUST
    so.company = company
    so.transaction_date = "2026-08-01"
    so.delivery_date = "2026-09-12"
    so.project = PROJ
    if frappe.get_meta("Sales Order").has_field("retention_percent"):
        so.retention_percent = 10
    for code, qty, rate in ITEMS:
        so.append("items", {"item_code": code, "qty": qty, "rate": rate,
                            "delivery_date": "2026-09-12", "project": PROJ})
    so.flags.ignore_permissions = True
    so.insert()
    so.submit()
    so_name = so.name
    print("sales order:", so_name, "value", so.grand_total)

# -------------------------------------------------------------- delivery note
if not frappe.db.exists("Delivery Note Item", {"against_sales_order": so_name, "docstatus": 1}):
    from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
    dn = make_delivery_note(so_name)
    dn.posting_date = "2026-09-10"
    dn.set_posting_time = 1
    dn.project = PROJ
    for it in dn.items:
        it.project = PROJ
    dn.flags.ignore_permissions = True
    dn.insert()
    dn.submit()
    print("delivered:", dn.name)

# --------------------------------------------------------------- sales invoice
si_name = frappe.db.get_value("Sales Invoice", {"project": PROJ, "docstatus": 1}, "name")
if not si_name:
    from erpnext.selling.doctype.sales_order.sales_order import make_sales_invoice
    si = make_sales_invoice(so_name)
    si.posting_date = "2026-09-12"
    si.set_posting_time = 1
    si.project = PROJ
    si.due_date = "2026-10-12"
    for it in si.items:
        it.project = PROJ
    si.flags.ignore_permissions = True
    si.insert()
    si.submit()
    si_name = si.name
    print("invoiced:", si_name, si.grand_total)

# ------------------------------------------------------------------- payment
si = frappe.get_doc("Sales Invoice", si_name)
if si.outstanding_amount > 1:
    from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
    pe = get_payment_entry("Sales Invoice", si_name)
    pe.posting_date = "2026-09-18"
    pe.reference_no = "NEFT/AMB/2026/0914"
    pe.reference_date = "2026-09-18"
    # they held back the 10% retention, as the contract allows
    keep_back = round(si.grand_total * 0.10, 2)
    pe.paid_amount = round(si.grand_total - keep_back, 2)
    pe.received_amount = pe.paid_amount
    for ref in pe.references:
        ref.allocated_amount = pe.paid_amount
    pe.flags.ignore_permissions = True
    pe.insert()
    pe.submit()
    print("paid:", pe.name, pe.paid_amount, "(retention of %s held back)" % keep_back)

# ------------------------------------------------- commissioning and handover
if not frappe.db.exists("MSCAST Commissioning Report", {"project": PROJ}):
    cr = frappe.new_doc("MSCAST Commissioning Report")
    cr.project = PROJ
    cr.customer = CUST
    cr.site_location = "Waluj works, Chhatrapati Sambhajinagar"
    cr.machine_description = "2-strand billet caster, mould and oscillator revamp"
    cr.machine_sn = "MS/CCM/2011/02-R1"
    cr.start_date = "2026-09-08"
    cr.end_date = "2026-09-11"
    cr.status = "Completed - provisional acceptance"
    cr.guarantee_start = "2026-09-11"
    cr.mscast_engineer = "Ganesh Pawar"
    cr.customer_representative = "A. Bhosale (Ambika)"
    cr.flags.ignore_permissions = True
    cr.insert()
    print("commissioned:", cr.name)

if not frappe.db.exists("MSCAST Spares Handover", {"project": PROJ}):
    sh = frappe.new_doc("MSCAST Spares Handover")
    sh.project = PROJ
    sh.customer = CUST
    sh.handover_date = "2026-09-11"
    sh.spares_type = "Commissioning spares"
    sh.received_by = "A. Bhosale (Ambika)"
    meta = frappe.get_meta("MSCAST Spares Handover")
    child = meta.get_field("items").options if meta.get_field("items") else None
    fields = {f.fieldname for f in frappe.get_meta(child).fields} if child else set()
    for code, desc, qty in [("SPRAY-NOZZLE", "Secondary cooling spray nozzles", 12),
                            ("REFRACTORY-TD", "Tundish refractory lining set", 1),
                            ("SPR-MOULD-TUBE", "Copper mould tube, spare", 2)]:
        row = {}
        if "item_code" in fields:
            row["item_code"] = code
        if "item" in fields:
            row["item"] = code
        for f in ("description", "item_name", "particulars"):
            if f in fields:
                row[f] = desc
        for f in ("qty", "quantity"):
            if f in fields:
                row[f] = qty
        for f in ("uom", "unit"):
            if f in fields:
                row[f] = "Nos"
        sh.append("items", row)
    sh.flags.ignore_permissions = True
    sh.insert()
    print("spares handed over:", sh.name)

# ------------------------------------------------------------- the certificate
if not frappe.db.exists("MSCAST Project Certificate", {"project": PROJ}):
    ct = frappe.new_doc("MSCAST Project Certificate")
    ct.project = PROJ
    ct.customer = CUST
    ct.certificate_type = "Commissioning"
    ct.issue_date = "2026-09-16"
    ct.status = "Received"
    ct.retention_release_due = "2027-09-11"
    ct.reference = "ASRM/COMM/2026/07"
    ct.flags.ignore_permissions = True
    ct.insert()
    print("certificate received:", ct.name)

frappe.db.commit()

proj = frappe.get_doc("Project", PROJ)
print()
print("PROJ-0003 summary")
print("  customer     ", proj.customer)
print("  complete     ", proj.percent_complete, "%")
print("  order        ", frappe.db.get_value("Sales Order", so_name, "grand_total"))
print("  billed       ", frappe.db.get_value("Sales Invoice", si_name, "grand_total"))
print("  outstanding  ", frappe.db.get_value("Sales Invoice", si_name, "outstanding_amount"), "(the retention)")
print()
print("open projects now:", frappe.db.count("Project", {"status": "Open"}))
