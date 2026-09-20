# -*- coding: utf-8 -*-
"""Repair the contradictions the exception sweep found in the demo data."""
import frappe
from frappe.utils import add_days

def ok(msg): print("  OK  ", msg)
def skip(msg): print("  --  ", msg)
def fail(msg): print("  !!  ", msg)

# ---------------------------------------------------------------- 1. dispatch
# A caster was commissioned 10-15 Sep on a sales order showing nothing delivered.
# The machine is a non-stock ETO item, so the dispatch posts no stock movement.
print("1. dispatch the machine before it was commissioned")
so_name = "SAL-ORD-2026-00001"
already = frappe.db.sql("""select dni.parent from `tabDelivery Note Item` dni
    join `tabDelivery Note` dn on dn.name = dni.parent
    where dni.against_sales_order = %s and dn.docstatus = 1""", (so_name,), as_dict=True)
if already:
    skip("already dispatched on %s" % already[0].parent)
else:
    from erpnext.selling.doctype.sales_order.sales_order import make_delivery_note
    dn = make_delivery_note(so_name)
    dn.posting_date = "2026-09-05"
    dn.set_posting_time = 1
    dn.project = "PROJ-0001"
    keep = []
    for it in dn.items:
        if it.item_code in ("CCM-2S-130", "SRV-ERECTION"):
            it.project = "PROJ-0001"
            keep.append(it)
    dn.set("items", [])
    for it in keep:
        dn.append("items", it)
    for idx, it in enumerate(dn.items):
        it.idx = idx + 1
    dn.flags.ignore_permissions = True
    dn.insert()
    dn.submit()
    ok("delivery note %s submitted 5 Sep for %s" % (dn.name, ", ".join(i.item_code for i in dn.items)))
    frappe.db.commit()
    so = frappe.get_doc("Sales Order", so_name)
    print("      %s now %.1f%% delivered, status %s" % (so_name, so.per_delivered, so.status))

# ---------------------------------------------------------------- 2. dunning
print("2. the dunning that chases a customer with nothing overdue")
for d in frappe.get_all("Dunning", fields=["name", "docstatus"]):
    if d.docstatus == 0:
        frappe.delete_doc("Dunning", d.name, force=True, ignore_permissions=True)
        ok("deleted draft dunning %s - receivables are clean, nothing to chase" % d.name)
    else:
        skip("%s is submitted, left alone" % d.name)

# ------------------------------------------------------------------- 3. PCC
print("3. the cost sheet still in draft on a project that is 25% built")
pcc = "PCC-2026-00002"
if frappe.db.exists("MSCAST PCC", pcc):
    cur = frappe.db.get_value("MSCAST PCC", pcc, "status")
    if cur != "Approved":
        frappe.db.set_value("MSCAST PCC", pcc, {
            "status": "Approved", "workflow_state": "Approved",
            "approved_by": "Administrator"}, update_modified=False)
        ok("%s approved (was %s)" % (pcc, cur))
    else:
        skip("%s already approved" % pcc)

# --------------------------------------------------------------- 4. kick-off
print("4. the kick-off parked on a query while the project runs")
k = "KICK-2026-00002"
if frappe.db.exists("MSCAST Project Kickoff", k):
    cur = frappe.db.get_value("MSCAST Project Kickoff", k, "workflow_state")
    if cur != "Kick-off Approved":
        frappe.db.set_value("MSCAST Project Kickoff", k, {
            "workflow_state": "Kick-off Approved",
            "design_freeze_date": "2026-09-10",
            "first_dispatch_target": "2026-11-20"}, update_modified=False)
        ok("%s advanced from '%s' to 'Kick-off Approved'" % (k, cur))
    else:
        skip("%s already approved" % k)

# -------------------------------------------------------------------- 5. BRM
print("5. the supplier bill outstanding with no certified BRM")
sup = "Shivneri Machining Works (DEMO)"
pi = frappe.db.get_value("Purchase Invoice", {"supplier": sup, "docstatus": 1}, ["name", "grand_total", "bill_no", "bill_date"], as_dict=True)
if pi and not frappe.db.exists("MSCAST BRM", {"supplier": sup}):
    b = frappe.new_doc("MSCAST BRM")
    b.supplier = sup
    b.project = "PROJ-0001"
    b.invoice_type = "Tax Invoice"
    b.supplier_invoice_no = pi.bill_no or "SMW/CAP/2026/08"
    b.supplier_invoice_date = pi.bill_date or "2026-08-20"
    b.amount = pi.grand_total
    b.status = "Certified"
    b.certification_date = "2026-09-18"
    if frappe.get_meta("MSCAST BRM").has_field("workflow_state"):
        b.workflow_state = "Certified"
    b.flags.ignore_permissions = True
    b.insert()
    ok("BRM %s certified for %s (%s)" % (b.name, sup, pi.name))
else:
    skip("BRM already exists for %s, or no invoice found" % sup)

# ------------------------------------------------------------- 6. timesheets
print("6. open projects with no engineering hours booked")
emp = frappe.db.get_value("Employee", {"status": "Active"}, "name")
act = frappe.db.get_value("Activity Type", {}, "name")
if emp and act:
    for proj, days_ago, hours in [("PROJ-0002", 3, 6), ("PROJ-0001", 2, 7)]:
        recent = frappe.db.sql("""select max(t.start_date) d from `tabTimesheet` t
            where t.parent_project = %s and t.docstatus = 1""", (proj,))[0][0]
        today = frappe.db.sql("select date(convert_tz(utc_timestamp(),'+00:00','+05:30'))")[0][0]
        if recent and frappe.utils.date_diff(today, recent) < 14:
            skip("%s already has recent hours (%s)" % (proj, recent))
            continue
        day = add_days(str(today), -days_ago)
        ts = frappe.new_doc("Timesheet")
        ts.employee = emp
        ts.parent_project = proj
        ts.append("time_logs", {
            "activity_type": act,
            "from_time": day + " 09:30:00",
            "hours": hours,
            "project": proj,
            "description": "Detail engineering",
        })
        ts.flags.ignore_permissions = True
        ts.insert()
        ts.submit()
        ok("timesheet %s: %sh on %s, %s" % (ts.name, hours, proj, day))
else:
    fail("no active employee or activity type found - timesheets skipped")

frappe.db.commit()
frappe.clear_cache()
print("\ndone")
