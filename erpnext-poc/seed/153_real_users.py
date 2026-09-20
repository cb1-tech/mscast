# -*- coding: utf-8 -*-
"""Real people on real mailboxes, each wearing several hats - which is how a
company of six actually runs. The (DEMO) logins are retired."""
import frappe

# employee, full name, email, designation, roles, what they may approve
PEOPLE = [
    ("HR-EMP-00001", "Mustaque", "Chandankeri", "latookaushik@yahoo.com",
     "Managing Director",
     ["MSCAST Director", "Sales Manager", "Sales User", "Accounts Manager",
      "Projects Manager", "Purchase Manager", "Item Manager"],
     "Cost sheets, quotations, purchase orders, kick-off, claims, project closure, payroll"),

    ("HR-EMP-00002", "Aiqaz", "Chandankeri", "latookaushik@hotmail.com",
     "Director - Projects & Engineering",
     ["Projects Manager", "Projects User", "Quality Manager", "Sales User",
      "Stock User", "Item Manager"],
     "Kick-off, drawings released for manufacture, inspection sign-off"),

    ("HR-EMP-00004", "Sameer", "Lokhande", "uattech@carobar.net",
     "Purchase & Stores",
     ["Purchase Manager", "Purchase User", "Stock Manager", "Stock User", "Item Manager"],
     "Billing Routing Memos - certifies a supplier bill before Accounts may pay"),

    ("HR-EMP-00005", "Anita", "Deshpande", "carobar.tradecars@gmail.com",
     "Accounts & HR",
     ["Accounts Manager", "Accounts User", "HR Manager", "HR User"],
     "Payments, invoices, payroll entry"),

    ("HR-EMP-00003", "Rohit", "Kulkarni", "autoelectron.jp@gmail.com",
     "Design Engineer",
     ["Projects User", "Item Manager", "Stock User", "System Manager"],
     "Drawing revisions, MDF release to procurement"),

    ("HR-EMP-00006", "Ganesh", "Pawar", "autoelectron.jp+site@gmail.com",
     "Site Supervisor",
     ["Projects User", "Quality Manager", "Stock User", "Employee"],
     "Inspection results, commissioning reports, site expense claims"),
]

EXTERNAL = [
    ("autoelectron.jp+ca@gmail.com", "S. Joshi", "Joshi & Associates, Chartered Accountants",
     ["MSCAST Statutory Auditor", "Auditor"]),
]

RETIRE = ["hr@mscast.demo", "stores@mscast.demo", "design@mscast.demo",
          "purchase@mscast.demo", "accounts@mscast.demo", "director@mscast.demo",
          "auditor@mscast.demo", "mustaque@mcast.co.in"]


def upsert_user(email, first, last, roles, designation=None):
    if frappe.db.exists("User", email):
        u = frappe.get_doc("User", email)
    else:
        u = frappe.new_doc("User")
        u.email = email
        u.send_welcome_email = 0
    u.first_name = first
    u.last_name = last
    u.full_name = ("%s %s" % (first, last)).strip()
    u.enabled = 1
    u.user_type = "System User"
    # nothing here should ever send mail to a real inbox by accident
    u.unsubscribed = 1
    if designation:
        u.designation = designation
    existing = {r.role for r in (u.get("roles") or [])}
    for r in roles:
        if frappe.db.exists("Role", r) and r not in existing:
            u.append("roles", {"role": r})
    u.flags.ignore_permissions = True
    u.save()
    return u


print("=== staff ===")
for emp_id, first, last, email, designation, roles, approves in PEOPLE:
    u = upsert_user(email, first, last, roles, designation)
    have = sorted({r.role for r in u.get("roles")})
    if frappe.db.exists("Employee", emp_id):
        frappe.db.set_value("Employee", emp_id, {
            "user_id": email,
            "company_email": email,
            "prefered_email": "Company Email" if frappe.get_meta("Employee").has_field("prefered_email") else None,
        }, update_modified=False)
    print("  %-26s %-34s %s" % (u.full_name, email, designation))
    print("       roles: %s" % ", ".join(have))
    print("       approves: %s" % approves)

print()
print("=== external ===")
for email, name, firm, roles in EXTERNAL:
    parts = name.split(" ", 1)
    u = upsert_user(email, parts[0], parts[1] if len(parts) > 1 else "", roles)
    print("  %-26s %-34s %s" % (u.full_name, email, firm))
    print("       roles: %s" % ", ".join(sorted({r.role for r in u.get("roles")})))

print()
print("=== retired ===")
for email in RETIRE:
    if frappe.db.exists("User", email):
        frappe.db.set_value("User", email, {"enabled": 0, "unsubscribed": 1}, update_modified=False)
        print("  disabled", email)

frappe.db.commit()
frappe.clear_cache()

print()
print("=== can the approval chain actually run? ===")
for wf in frappe.get_all("Workflow", filters={"is_active": 1}, fields=["name", "document_type"]):
    doc = frappe.get_doc("Workflow", wf.name)
    print(" ", wf.name)
    for t in doc.transitions:
        holders = frappe.db.sql("""select u.name from `tabUser` u
            join `tabHas Role` r on r.parent = u.name
            where r.role = %s and u.enabled = 1 and u.name not in ('Administrator','Guest')""",
            (t.allowed,), as_dict=True)
        who = ", ".join(h.name.split("@")[0] for h in holders) or "NOBODY"
        flag = "" if holders else "   <-- no live user holds this role"
        print("     %-22s %-18s -> %-22s needs %-18s %s%s" % (
            t.state, t.action, t.next_state, t.allowed, who, flag))

print()
print("active logins:", frappe.db.count("User", {"enabled": 1, "user_type": "System User"}))
