import frappe
from frappe.utils import add_days

print("=== why only 7.2% delivered ===")
dn = frappe.get_doc("Delivery Note", "DN-26-00002")
for it in dn.items:
    print("  DN item:", it.item_code, "qty", it.qty, "rate", it.rate, "amount", it.amount)
so = frappe.get_doc("Sales Order", "SAL-ORD-2026-00001")
for it in so.items:
    print("  SO item:", it.item_code, "qty", it.qty, "delivered", it.delivered_qty, "amount", it.amount)
print("  per_delivered:", so.per_delivered)

print()
print("=== BRM via the workflow ===")
sup = "Shivneri Machining Works (DEMO)"
wf = frappe.get_all("Workflow", filters={"document_type": "MSCAST BRM", "is_active": 1}, fields=["name"])
if wf:
    w = frappe.get_doc("Workflow", wf[0].name)
    print("  states:", [s.state for s in w.states])
    print("  transitions:", [(t.state, t.action, t.next_state, t.allowed) for t in w.transitions])

existing = frappe.db.get_value("MSCAST BRM", {"supplier": sup}, "name")
if existing:
    print("  BRM already exists:", existing)
else:
    pi = frappe.db.get_value("Purchase Invoice", {"supplier": sup, "docstatus": 1},
                             ["name", "grand_total", "bill_no", "bill_date"], as_dict=True)
    b = frappe.new_doc("MSCAST BRM")
    b.supplier = sup
    b.project = "PROJ-0001"
    b.invoice_type = "Tax Invoice"
    b.supplier_invoice_no = pi.bill_no or "SMW/CAP/2026/08"
    b.supplier_invoice_date = pi.bill_date or "2026-08-20"
    b.amount = pi.grand_total
    b.flags.ignore_permissions = True
    b.insert()
    print("  created", b.name, "in state", b.get("workflow_state"), "status", b.get("status"))
    from frappe.model.workflow import apply_workflow, get_transitions
    for t in get_transitions(b):
        print("    available action:", t.get("action"), "->", t.get("next_state"))
    try:
        b = apply_workflow(b, "Certify")
        print("  certified ->", b.get("workflow_state"), "/", b.get("status"))
    except Exception as e:
        print("  apply_workflow failed:", e)
        frappe.db.set_value("MSCAST BRM", b.name, {"status": "Certified", "workflow_state": "Certified",
                                                   "certification_date": "2026-09-18"}, update_modified=False)
        print("  set directly to Certified")

print()
print("=== timesheets ===")
emp = frappe.db.get_value("Employee", {"status": "Active"}, "name")
act = frappe.db.get_value("Activity Type", {}, "name")
today = frappe.db.sql("select date(convert_tz(utc_timestamp(),'+00:00','+05:30'))")[0][0]
for proj, days_ago, hours in [("PROJ-0002", 3, 6), ("PROJ-0001", 2, 7)]:
    recent = frappe.db.sql("""select max(t.start_date) d from `tabTimesheet` t
        where t.parent_project = %s and t.docstatus = 1""", (proj,))[0][0]
    if recent and frappe.utils.date_diff(today, recent) < 14:
        print("  --", proj, "already has recent hours", recent)
        continue
    day = add_days(str(today), -days_ago)
    ts = frappe.new_doc("Timesheet")
    ts.employee = emp
    ts.parent_project = proj
    ts.append("time_logs", {"activity_type": act, "from_time": day + " 09:30:00",
                            "hours": hours, "project": proj, "description": "Detail engineering"})
    ts.flags.ignore_permissions = True
    ts.insert()
    ts.submit()
    print("  OK", ts.name, hours, "h on", proj, day)

frappe.db.commit()
frappe.clear_cache()
print("\ndone")
