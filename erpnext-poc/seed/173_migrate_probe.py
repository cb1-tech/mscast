# -*- coding: utf-8 -*-
"""Controlled experiment: does a migrate overwrite live workflow rows?

Sets one transition to a deliberately wrong value and records it. Run
'bench migrate', then run 174 to see whether the migrate changed it back.

If migrate rewrites it, then fixtures are authoritative on every upgrade and
any business rule changed in the UI is lost the next time the app is deployed.
That is the risk to understand before the VPS.
"""
import frappe

WF, ACTION, PROBE = "MSCAST BRM Certification", "Certify", "Purchase Manager"

doc = frappe.get_doc("Workflow", WF)
for t in doc.transitions:
    if t.action == ACTION:
        print("before migrate: %s/%s = %s" % (WF, ACTION, t.allowed))
        t.allowed = PROBE
doc.flags.ignore_permissions = True
doc.save()
frappe.db.commit()
print("probe set      : %s/%s = %s" % (WF, ACTION, PROBE))
print()
print("now run:  docker exec mscast-poc-backend-1 bench --site frontend migrate")
print("then run: seed 174_migrate_verdict")
