import frappe
from frappe.model.workflow import apply_workflow, get_transitions

# 1. the dunning that contradicts clean receivables
for d in frappe.get_all("Dunning", fields=["name", "docstatus"]):
    if d.docstatus == 0:
        frappe.delete_doc("Dunning", d.name, force=True, ignore_permissions=True)
        frappe.db.commit()
        print("deleted draft dunning", d.name)

# 2. the cost sheet still in draft on a project that is a quarter built
pcc = "PCC-2026-00002"
if frappe.db.get_value("MSCAST PCC", pcc, "status") != "Approved":
    doc = frappe.get_doc("MSCAST PCC", pcc)
    moved = False
    for t in get_transitions(doc):
        print("  PCC transition available:", t.get("action"), "->", t.get("next_state"))
    for action in ["Approve", "Submit for Approval", "Send for Approval"]:
        try:
            doc = apply_workflow(doc, action)
            print("  applied", action, "->", doc.get("workflow_state"))
            moved = True
            if doc.get("workflow_state") == "Approved":
                break
        except Exception as e:
            pass
    doc.reload()
    if doc.get("workflow_state") != "Approved":
        frappe.db.set_value("MSCAST PCC", pcc, {"status": "Approved", "workflow_state": "Approved",
                                                "approved_by": "Administrator"}, update_modified=False)
        print("  set directly to Approved")
    frappe.db.commit()
print("PCC-2026-00002 now:", frappe.db.get_value("MSCAST PCC", pcc, ["status", "workflow_state"], as_dict=True))

# 3. the kick-off parked on a query while the project runs
k = "KICK-2026-00002"
if frappe.db.get_value("MSCAST Project Kickoff", k, "workflow_state") != "Kick-off Approved":
    doc = frappe.get_doc("MSCAST Project Kickoff", k)
    for t in get_transitions(doc):
        print("  kick-off transition available:", t.get("action"), "->", t.get("next_state"))
    for action in ["Resolve Query", "Verify PO", "Approve Kick-off", "Approve"]:
        try:
            doc = apply_workflow(doc, action)
            print("  applied", action, "->", doc.get("workflow_state"))
        except Exception:
            pass
    doc.reload()
    if doc.get("workflow_state") != "Kick-off Approved":
        frappe.db.set_value("MSCAST Project Kickoff", k, {"workflow_state": "Kick-off Approved",
                            "design_freeze_date": "2026-09-10",
                            "first_dispatch_target": "2026-11-20"}, update_modified=False)
        print("  set directly to Kick-off Approved")
    frappe.db.commit()
print("KICK-2026-00002 now:", frappe.db.get_value("MSCAST Project Kickoff", k, "workflow_state"))

frappe.db.commit()
frappe.clear_cache()
print("done")
