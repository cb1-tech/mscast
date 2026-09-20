#!/usr/bin/env bash
# Segregation-of-duties audit that does NOT rely on workflow transitions alone.
# T6e only compares transition roles; document CREATION is a permission, not a
# transition, so a user can hold create rights on a document and the approval
# role for it without T6e ever noticing. This asks the fuller question.
set -euo pipefail
C=mscast-poc-backend-1

docker exec -i $C bash -c 'cd /home/frappe/frappe-bench && bench --site frontend console' <<'PY' 2>/dev/null
import frappe

USERS = frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"},
                       fields=["name", "full_name"])

def roles_of(u):
    return set(frappe.get_all("Has Role", filters={"parent": u, "parenttype": "User"},
                              pluck="role"))

def can_create(roles, dt):
    rows = frappe.get_all("Custom DocPerm", filters={"parent": dt}, fields=["role", "create"]) \
         + frappe.get_all("DocPerm", filters={"parent": dt}, fields=["role", "create"])
    return sorted({r.role for r in rows if r.create and r.role in roles})

CHECKS = [
    # (document, what creating it means, the approval role that must be someone else)
    ("MSCAST BRM",   "prepare a supplier-bill certificate", "MSCAST Director",  "certify"),
    ("MSCAST BRM",   "prepare a supplier-bill certificate", "Accounts Manager", "mark paid"),
    ("Purchase Order", "raise a purchase order",            "MSCAST Director",  "approve"),
    ("MSCAST PCC",   "prepare a cost sheet",                "MSCAST Director",  "approve"),
]

print("### can one person carry a document end to end?")
print()
for dt, prep_desc, appr_role, appr_desc in CHECKS:
    print("--- %s : create + %s (%s)" % (dt, appr_desc, appr_role))
    hit = False
    for u in USERS:
        rs = roles_of(u.name)
        if appr_role not in rs:
            continue
        if "System Manager" in rs:
            print("    %-22s [System Manager - can do anything anyway]" % (u.full_name or u.name))
            continue
        via = can_create(rs, dt)
        if via:
            hit = True
            print("    ** %-20s can CREATE via %s AND %s"
                  % (u.full_name or u.name, ", ".join(via), appr_desc))
    if not hit:
        print("    none")
    print()

print("### certify AND mark paid - same person?")
for u in USERS:
    rs = roles_of(u.name)
    if "System Manager" in rs:
        continue
    if "MSCAST Director" in rs and "Accounts Manager" in rs:
        print("    ** %s holds both MSCAST Director (certify) and Accounts Manager (mark paid)"
              % (u.full_name or u.name))

print()
print("### exactly what each director holds")
for u in USERS:
    rs = roles_of(u.name)
    if "MSCAST Director" in rs:
        print("    %-22s %s" % (u.full_name or u.name, ", ".join(sorted(rs))))
PY
