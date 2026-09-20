# -*- coding: utf-8 -*-
"""Directors approve; everyone else prepares.

Anything that leaves the company - a cost sheet that becomes a quotation, a
purchase order to a supplier, a drawing sent to a customer, a commitment made at
kick-off - is approved by Mustaque or Aiqaz. Staff raise the document; they do
not sign it off.

That needs more people than six, so the preparers below are invented. They are
on @mscast.co.in and marked unsubscribed: they can log in for a demo, and no
mail is ever attempted to an address that does not exist.
"""
import frappe

DIRECTORS = ["latookaushik@yahoo.com", "latookaushik@hotmail.com"]  # Mustaque, Aiqaz

# --------------------------------------------------------------- new preparers
STAFF = [
    ("nikhil.sawant@mscast.co.in", "Nikhil", "Sawant", "Purchase Executive",
     ["Purchase User", "Stock User", "Item Manager"],
     "Raises material requests, RFQs and purchase orders. Cannot approve them."),
    ("kavita.joshi@mscast.co.in", "Kavita", "Joshi", "Accounts Executive",
     ["Accounts User"],
     "Enters invoices and prepares payments. Cannot release them."),
    ("prashant.more@mscast.co.in", "Prashant", "More", "Stores Officer",
     ["Stock User", "Item Manager"],
     "Receipts, issues and dispatch paperwork."),
    ("vinod.shelke@mscast.co.in", "Vinod", "Shelke", "QA Inspector",
     ["Projects User", "Stock User"],
     "Records inspection results. Sign-off is Aiqaz's."),
    ("meera.rane@mscast.co.in", "Meera", "Rane", "Design Draughtsman",
     ["Projects User", "Item Manager"],
     "Prepares drawings and MDFs. Release to a customer is Aiqaz's."),
]

print("1. preparers")
for email, first, last, designation, roles, note in STAFF:
    if frappe.db.exists("User", email):
        u = frappe.get_doc("User", email)
    else:
        u = frappe.new_doc("User")
        u.email = email
        u.send_welcome_email = 0
    u.first_name, u.last_name = first, last
    u.full_name = "%s %s" % (first, last)
    u.enabled = 1
    u.user_type = "System User"
    u.unsubscribed = 1          # invented address - never attempt delivery
    u.designation = designation
    have = {r.role for r in (u.get("roles") or [])}
    for r in roles:
        if frappe.db.exists("Role", r) and r not in have:
            u.append("roles", {"role": r})
    u.flags.ignore_permissions = True
    u.save()
    print("   %-24s %-28s %s" % (u.full_name, designation, ", ".join(sorted(roles))))
    print("      %s" % note)

# ------------------------------------------------- both directors can approve
print()
print("2. approval authority")
for email in DIRECTORS:
    u = frappe.get_doc("User", email)
    have = {r.role for r in u.get("roles")}
    for r in ["MSCAST Director", "Projects Manager", "Accounts Manager", "Sales Manager"]:
        if r not in have and frappe.db.exists("Role", r):
            u.append("roles", {"role": r})
    u.flags.ignore_permissions = True
    u.save()
    print("   %-24s %s" % (u.full_name, ", ".join(sorted({r.role for r in u.get("roles")}))))

# ------------------------------------- an external decision needs a director
# The whole matrix lives here, not spread across 154 and 161, because relying on
# two scripts running in the right order is how it came back as System Manager
# after an app install. Re-running this alone restores the intended state.
MOVE = [
    ("MSCAST PCC Approval", "Approve", "MSCAST Director",
     "a cost sheet is what the price is built on"),
    ("MSCAST Project Kick-off", "Approve Kick-off", "MSCAST Director",
     "accepting a customer order is the director's commitment"),
    ("MSCAST Purchase Order Approval", "Approve", "MSCAST Director",
     "a purchase order commits money to an outside supplier"),
    ("MSCAST PCC Approval", "Send Back", "MSCAST Director",
     "sending a cost sheet back is the director's call, not Accounts'"),
    ("MSCAST BRM Certification", "Certify", "MSCAST Director",
     "certifying a bill releases money to an outside supplier, and the buyer "
     "must not certify what he himself ordered"),
]
print()
print("3. transitions moved to the directors")
for wf_name, action, role, why in MOVE:
    if not frappe.db.exists("Workflow", wf_name):
        continue
    wf = frappe.get_doc("Workflow", wf_name)
    changed = False
    for t in wf.transitions:
        if t.action == action and t.allowed != role:
            print("   %-34s %-18s %s -> %s" % (wf_name, action, t.allowed, role))
            print("      %s" % why)
            t.allowed = role
            changed = True
    for st in wf.states:
        if st.state in ("Approved",) and st.allow_edit != role:
            st.allow_edit = role
            changed = True
    if changed:
        wf.flags.ignore_permissions = True
        wf.save()

frappe.db.commit()
frappe.clear_cache()

# ------------------------------------------------------- the resulting matrix
print()
print("=== who may do what ===")
for wf in frappe.get_all("Workflow", filters={"is_active": 1}, fields=["name", "document_type"]):
    doc = frappe.get_doc("Workflow", wf.name)
    print()
    print(" ", wf.name, "(%s)" % wf.document_type)
    for t in doc.transitions:
        holders = frappe.db.sql("""select u.full_name from `tabUser` u
            join `tabHas Role` r on r.parent = u.name
            where r.role = %s and u.enabled = 1
              and u.name not in ('Administrator','Guest','admin@mscast.local')""",
            (t.allowed,), as_dict=True)
        who = ", ".join(sorted({h.full_name for h in holders})) or "NOBODY"
        print("     %-24s -> %-22s %-18s %s" % (t.action, t.next_state, t.allowed, who))

print()
print("=== can anyone both raise and approve the same purchase order? ===")
clash = frappe.db.sql("""
    select u.full_name from `tabUser` u
    where u.enabled = 1 and u.name not in ('Administrator','Guest','admin@mscast.local')
      and exists (select 1 from `tabHas Role` r where r.parent = u.name and r.role = 'Purchase User')
      and exists (select 1 from `tabHas Role` r where r.parent = u.name and r.role = 'MSCAST Director')
""", as_dict=True)
print("  ", ", ".join(c.full_name for c in clash) if clash else "no - raising and approving are now separate")
