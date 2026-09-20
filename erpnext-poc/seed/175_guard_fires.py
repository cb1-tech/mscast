# -*- coding: utf-8 -*-
"""Prove the post-deploy guard actually fires and repairs.

Sets two transitions to the exact wrong values the stale deploy produced, then
calls the verification the way after_migrate calls it.
"""
import frappe
from mscast_erp.install import verify_controls

BREAK = [("MSCAST BRM Certification", "Certify", "Purchase Manager"),
         ("MSCAST PCC Approval", "Approve", "System Manager")]

for wf_name, action, wrong in BREAK:
    doc = frappe.get_doc("Workflow", wf_name)
    for t in doc.transitions:
        if t.action == action:
            t.allowed = wrong
    doc.flags.ignore_permissions = True
    doc.save()
    print("broke: %s / %s -> %s" % (wf_name, action, wrong))
frappe.db.commit()

print()
print("calling verify_controls() as after_migrate does:")
verify_controls()

print()
print("state now:")
for wf_name, action, _w in BREAK:
    got = [t.allowed for t in frappe.get_doc("Workflow", wf_name).transitions
           if t.action == action]
    print("   %-32s %-20s %s" % (wf_name, action, got))
