# -*- coding: utf-8 -*-
"""Three audit findings, fixed at the root.

1. THE KICK-OFF CHECKLIST DID NOT HOLD.
   The condition requiring price, scope, payment terms and GST to be ticked sat
   on exactly one transition, Draft -> PO Verified. The other route into the same
   state, PO Query Raised -> PO Verified, had no condition at all - so the way to
   get an unchecked kick-off approved was to raise a query first. KICK-2026-00002
   is sitting in Kick-off Approved right now with chk_payment_terms = 0, which is
   the exact scenario UC-2 uses to show the control working.

2. FOUR ROLES COULD NOT DO THEIR JOB.
   `Design User` had ZERO permission rows anywhere in the system. Stores, Quality
   and the Purchase Executive had none on the MSCAST doctypes their role cards
   tell them to use. The Draft -> For Customer Approval transition was executable
   by nobody at all. Meanwhile `Accounts User` could create every MSCAST document
   and submit and cancel Payment Entries, which its role card explicitly denies.

3. THE AUDITOR COULD WRITE.
   Four documents say the CA's login cannot change anything. `Auditor` had write
   and create on GSTR-1 and GST Return Log; `MSCAST Statutory Auditor` had write,
   create and DELETE on MSCAST Exception - the ability to erase the output of the
   overnight control sweep.

The permission matrix below is taken from the Role Cards, which are the spec.
"""
import frappe

# The configuration half of this script now lives in the app, as
# mscast_erp.controls.permissions, and runs on every install and migrate.
#
# It moved because it was wrong here, and because here it did not ship:
#   - inserting one Custom DocPerm row replaces ALL of a doctype's standard
#     permissions; on five doctypes every other role lost access, including the
#     director named as the kick-off approver (found 21 Sep 2026);
#   - a fresh install from the app never runs seed scripts, so it shipped with a
#     writable auditor and the kick-off bypass; and the bypass was also in the
#     workflow fixture, so the first migrate would have brought it back.
# What stays here is the one-off DATA repair, which is not configuration.
from mscast_erp.controls.permissions import enforce

enforce()

print("")
print("records already approved with an unticked checklist:")
bad = frappe.get_all(
    "MSCAST Project Kickoff",
    filters={"workflow_state": ["in", ["PO Verified", "Kick-off Approved"]]},
    fields=["name", "workflow_state", "chk_price", "chk_scope",
            "chk_payment_terms", "chk_tax_gst"])
offenders = [k for k in bad if not (k.chk_price and k.chk_scope
                                    and k.chk_payment_terms and k.chk_tax_gst)]
for k in offenders:
    frappe.db.set_value("MSCAST Project Kickoff", k.name, "workflow_state",
                        "PO Query Raised")
    print("   %s moved back to PO Query Raised - an unticked box means the "
          "customer's terms are still being queried" % k.name)
if not offenders:
    print("   none")
frappe.db.commit()
frappe.clear_cache()
print("done")
