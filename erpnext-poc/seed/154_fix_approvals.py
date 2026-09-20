# -*- coding: utf-8 -*-
"""Two fixes the user/role audit exposed.

1. Approving a cost sheet and approving a project kick-off both required
   'System Manager'. That is the IT account, not a business approver - it means
   the Managing Director cannot approve his own company's cost sheets, and
   whoever administers the system silently can. Both move to MSCAST Director.

2. The design engineer's login had inherited every role in the system.
"""
import frappe

MOVE = [
    ("MSCAST PCC Approval", "Approve", "System Manager", "MSCAST Director"),
    ("MSCAST Project Kick-off", "Approve Kick-off", "System Manager", "MSCAST Director"),
]

for wf_name, action, was, now in MOVE:
    if not frappe.db.exists("Workflow", wf_name):
        continue
    wf = frappe.get_doc("Workflow", wf_name)
    changed = False
    for t in wf.transitions:
        if t.action == action and t.allowed == was:
            t.allowed = now
            changed = True
    # the target state must also be reachable by that role
    for st in wf.states:
        if st.state in ("Approved", "Kick-off Approved") and st.allow_edit == was:
            st.allow_edit = now
            changed = True
    if changed:
        wf.flags.ignore_permissions = True
        wf.save()
        print("%s: '%s' now needs %s (was %s)" % (wf_name, action, now, was))

# the MSCAST Director role must be able to act, not just read
DIRECTOR_WRITES = ["MSCAST PCC", "MSCAST Project Kickoff", "MSCAST BRM",
                   "MSCAST Client Claim", "MSCAST Project Certificate"]
for dt in DIRECTOR_WRITES:
    if not frappe.db.exists("DocType", dt):
        continue
    for p in frappe.get_all("Custom DocPerm", filters={"parent": dt, "role": "MSCAST Director"},
                            fields=["name", "write", "submit"]):
        frappe.db.set_value("Custom DocPerm", p.name, {"write": 1, "submit": 1}, update_modified=False)
    for p in frappe.get_all("DocPerm", filters={"parent": dt, "role": "MSCAST Director"},
                            fields=["name", "write"]):
        frappe.db.set_value("DocPerm", p.name, "write", 1, update_modified=False)
print("MSCAST Director can now write to the documents it approves")

# trim the design engineer's login back to a design engineer's roles
KEEP = {"Projects User", "Item Manager", "Stock User", "System Manager",
        "Employee", "Blogger", "Report Manager"}
u = frappe.get_doc("User", "autoelectron.jp@gmail.com")
before = sorted({r.role for r in u.get("roles")})
u.set("roles", [{"role": r} for r in sorted(KEEP) if frappe.db.exists("Role", r)])
u.flags.ignore_permissions = True
u.save()
after = sorted({r.role for r in u.get("roles")})
print()
print("Rohit Kulkarni (design): %d roles -> %d" % (len(before), len(after)))
print("   removed:", ", ".join(r for r in before if r not in after))
print("   kept:   ", ", ".join(after))

frappe.db.commit()
frappe.clear_cache()

print()
print("=== approval chain, re-checked ===")
for wf in frappe.get_all("Workflow", filters={"is_active": 1}, fields=["name"]):
    doc = frappe.get_doc("Workflow", wf.name)
    print(" ", wf.name)
    for t in doc.transitions:
        holders = frappe.db.sql("""select u.name from `tabUser` u
            join `tabHas Role` r on r.parent = u.name
            where r.role = %s and u.enabled = 1 and u.name not in ('Administrator','Guest','admin@mscast.local')""",
            (t.allowed,), as_dict=True)
        who = ", ".join(sorted({h.name.split("@")[0] for h in holders})) or "NOBODY"
        print("     %-24s -> %-22s %-18s %s" % (t.action, t.next_state, t.allowed, who))
