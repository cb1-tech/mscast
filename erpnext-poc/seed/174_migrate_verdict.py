# -*- coding: utf-8 -*-
"""Read the verdict of the migrate experiment started by 173."""
import frappe

WF, ACTION, PROBE, FIXTURE_VALUE = (
    "MSCAST BRM Certification", "Certify", "Purchase Manager", "MSCAST Director")

got = [t.allowed for t in frappe.get_doc("Workflow", WF).transitions
       if t.action == ACTION]
now = got[0] if got else "(missing)"
print("after migrate  : %s/%s = %s" % (WF, ACTION, now))
print()
if now == FIXTURE_VALUE:
    print("VERDICT: migrate OVERWROTE the live row from the fixture file.")
    print("         Fixtures are authoritative on every upgrade. Anything")
    print("         changed in the UI is silently reverted on the next deploy,")
    print("         and a stale checkout reverts it to whatever that checkout")
    print("         happened to contain.")
elif now == PROBE:
    print("VERDICT: migrate LEFT the live row alone.")
    print("         Fixtures did not overwrite it, so the earlier revert came")
    print("         from install-app specifically, not from migrate.")
else:
    print("VERDICT: unexpected value - investigate before drawing a conclusion.")
