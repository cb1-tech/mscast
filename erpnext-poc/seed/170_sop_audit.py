# -*- coding: utf-8 -*-
"""Audit the written SOPs against what the system actually enforces.

The SOPs were written on 19 Sep, before the user rework and the approval
changes. This checks the specific claims they make, so the documents can be
corrected from evidence rather than memory.
"""
import frappe

def holders(role):
    return sorted(u[0] for u in frappe.db.sql(
        """select distinct p.parent from `tabHas Role` p
           join `tabUser` u on u.name = p.parent
           where p.role = %s and u.enabled = 1 and u.user_type = 'System User'""", (role,)))

print("=" * 76)
print("CLAIM 1  'Purchase Order ... approved by the Purchase Manager'  (SOP-04, Part C)")
print("=" * 76)
for wf in ["MSCAST Purchase Order Approval", "MSCAST BRM Certification",
           "MSCAST PCC Approval", "MSCAST Project Kick-off"]:
    if not frappe.db.exists("Workflow", wf):
        continue
    doc = frappe.get_doc("Workflow", wf)
    print("\n  %s" % wf)
    for t in doc.transitions:
        print("     %-24s -> %-22s %s" % (t.action, t.next_state, t.allowed))

print()
print("=" * 76)
print("CLAIM 2  'the person who prepares a document never approves it'  (Part C)")
print("=" * 76)
PAIRS = [
    ("MSCAST PCC Approval", "Send for Approval", "Approve"),
    ("MSCAST Purchase Order Approval", "Send for Approval", "Approve"),
    ("MSCAST Project Kick-off", "Verify Customer PO", "Approve Kick-off"),
]
for wf, prep_action, appr_action in PAIRS:
    if not frappe.db.exists("Workflow", wf):
        continue
    doc = frappe.get_doc("Workflow", wf)
    prep = {t.allowed for t in doc.transitions if t.action == prep_action}
    appr = {t.allowed for t in doc.transitions if t.action == appr_action}
    p = set().union(*[set(holders(r)) for r in prep]) if prep else set()
    a = set().union(*[set(holders(r)) for r in appr]) if appr else set()
    both = sorted(p & a)
    print("\n  %s" % wf)
    print("     prepares (%s): %s" % (", ".join(prep) or "-", ", ".join(sorted(p)) or "-"))
    print("     approves (%s): %s" % (", ".join(appr) or "-", ", ".join(sorted(a)) or "-"))
    print("     BOTH        : %s" % (", ".join(both) if both
                                     else "nobody - separation holds"))

print()
print("=" * 76)
print("CLAIM 3  'attendance begins automatically' from biometric  (SOP-12, UC-7)")
print("=" * 76)
for s in frappe.get_all("Server Script", filters={"name": ["like", "%biometric%"]},
                        fields=["name", "disabled"]):
    print("  %-28s disabled=%s" % (s.name, s.disabled))

print()
print("=" * 76)
print("CLAIM 4  'Supplier payment ... Director above a threshold'  (Part C)")
print("=" * 76)
print("  any approval threshold configured?",
      bool(frappe.get_all("Authorization Rule", limit=1)) or "no Authorization Rule rows")

print()
print("=" * 76)
print("CLAIM 5  Drawing status control  (SOP-03)")
print("=" * 76)
print("  workflow on MSCAST Drawing:",
      frappe.db.get_value("Workflow", {"document_type": "MSCAST Drawing"}, "name")
      or "NONE - status is a plain field, nothing enforces the transitions")

print()
print("=" * 76)
print("NOT IN THE SOPs AT ALL - things the system now does daily")
print("=" * 76)
print("  06:00 exception sweep rules:",
      frappe.db.count("MSCAST Exception", {"status": ["in", ["Open", "Acknowledged"]]}),
      "open findings right now")
print("  08:35 AI briefing        :",
      frappe.db.get_value("Scheduled Job Type",
                          {"method": ["like", "%daily_briefing%"]}, "cron_format")
      or "not registered")
