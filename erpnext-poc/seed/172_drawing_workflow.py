# -*- coding: utf-8 -*-
"""Put a real workflow on MSCAST Drawing.

SOP-03 says "nothing is manufactured against a drawing that is not Released for
Manufacture" and calls it a control. It was not one: status was a plain Select
field, so anyone could set any value in any order, including straight from Draft
to Released without the customer ever seeing it.

The states and their order come from the field's own options, so the drawings
already in the system stay valid. Nothing is renamed and no record moves.

Who may do what follows the same rule as the rest of the system: preparing is
the drawing office's job, and anything the customer sees or that authorises
metal to be cut is the Projects Manager's.
"""
import frappe

DOCTYPE = "MSCAST Drawing"
NAME = "MSCAST Drawing Release"

STATES = [
    # state,                      doc_status, allow_edit,        style
    ("Draft",                    0, "Design User",      ""),
    ("For Customer Approval",    0, "Projects Manager", "Warning"),
    ("Approved by Customer",     0, "Projects Manager", "Info"),
    ("Released for Manufacture", 0, "Projects Manager", "Success"),
    ("Superseded",               0, "Projects Manager", "Danger"),
]

TRANSITIONS = [
    # from,                     action,                  to,                        allowed
    ("Draft", "Issue for Customer Approval", "For Customer Approval", "Design User"),
    ("For Customer Approval", "Record Customer Approval", "Approved by Customer", "Projects Manager"),
    ("For Customer Approval", "Return for Rework", "Draft", "Projects Manager"),
    ("Approved by Customer", "Release for Manufacture", "Released for Manufacture", "Projects Manager"),
    ("Released for Manufacture", "Supersede", "Superseded", "Projects Manager"),
    ("Approved by Customer", "Supersede", "Superseded", "Projects Manager"),
]

# The drawing office needs a role of its own. Meera Rane prepares drawings and
# must be able to issue them for approval, but must not be able to release one
# for manufacture - that is the whole point of the control.
if not frappe.db.exists("Role", "Design User"):
    frappe.get_doc({"doctype": "Role", "role_name": "Design User",
                    "desk_access": 1}).insert(ignore_permissions=True)
    print("role created: Design User")

for email in ["meera.rane@mscast.co.in"]:
    if frappe.db.exists("User", email):
        u = frappe.get_doc("User", email)
        if "Design User" not in {r.role for r in u.get("roles")}:
            u.append("roles", {"role": "Design User"})
            u.flags.ignore_permissions = True
            u.save()
            print("Design User granted to %s" % u.full_name)

for state, docstatus, _edit, style in STATES:
    if not frappe.db.exists("Workflow State", state):
        frappe.get_doc({"doctype": "Workflow State", "workflow_state_name": state,
                        "style": style}).insert(ignore_permissions=True)
for _f, action, _t, _a in TRANSITIONS:
    if not frappe.db.exists("Workflow Action Master", action):
        frappe.get_doc({"doctype": "Workflow Action Master",
                        "workflow_action_name": action}).insert(ignore_permissions=True)

doc = (frappe.get_doc("Workflow", NAME) if frappe.db.exists("Workflow", NAME)
       else frappe.new_doc("Workflow"))
doc.workflow_name = NAME
doc.document_type = DOCTYPE
doc.workflow_state_field = "status"
doc.is_active = 1
doc.send_email_alert = 0
doc.set("states", [])
doc.set("transitions", [])
for state, docstatus, edit, _s in STATES:
    doc.append("states", {"state": state, "doc_status": str(docstatus),
                          "allow_edit": edit})
for frm, action, to, allowed in TRANSITIONS:
    doc.append("transitions", {"state": frm, "action": action, "next_state": to,
                               "allowed": allowed, "allow_self_approval": 1})
doc.flags.ignore_permissions = True
doc.save()
frappe.db.commit()

print()
print("workflow saved:", NAME)
for t in doc.transitions:
    print("   %-26s %-26s -> %-26s %s"
          % (t.state, t.action, t.next_state, t.allowed))
print()
print("drawings by status (unchanged):")
for r in frappe.db.sql("""select status, count(*) n from `tabMSCAST Drawing`
                          group by status""", as_dict=True):
    print("   %-28s %d" % (r.status, r.n))
print()
print("the control SOP-03 claims is now real: Released for Manufacture can only")
print("be reached from Approved by Customer, and only by a Projects Manager.")
