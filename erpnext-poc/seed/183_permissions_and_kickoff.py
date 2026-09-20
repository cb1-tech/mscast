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

# ---------------------------------------------------------------- the matrix
# role -> doctypes it must be able to create and work on.
GRANT = {
    "Design User": [
        "MSCAST Drawing", "MSCAST Drawing Revision",
        "MSCAST Transmittal", "MSCAST Transmittal Item",
        "MSCAST MDF", "MSCAST MDF Item",
    ],
    "Projects User": [
        "MSCAST PCC", "MSCAST PCC Item", "MSCAST MDF", "MSCAST MDF Item",
        "MSCAST Project Kickoff", "MSCAST Client Claim",
        "MSCAST Project Certificate", "MSCAST Spares Handover",
        "MSCAST Spares Handover Item", "MSCAST Commissioning Report",
        "MSCAST Commissioning Parameter", "MSCAST Inspection Plan",
    ],
    "Stock User": [
        "MSCAST MDM", "MSCAST MDM Item", "MSCAST Delivery Instruction",
        "MSCAST Customer Asset",
    ],
    "Quality Manager": [
        "MSCAST Inspection Plan", "MSCAST Commissioning Report",
        "MSCAST Commissioning Parameter",
    ],
    "Purchase User": ["MSCAST BRM"],
    "Purchase Manager": ["MSCAST BRM"],
}

# Accounts should not be originating engineering, stores or purchase documents.
# Its role card says: enter invoices, prepare payments, journals.
REVOKE_CREATE = {
    "Accounts User": [
        "MSCAST BRM", "MSCAST PCC", "MSCAST Drawing", "MSCAST MDM",
        "MSCAST Delivery Instruction", "MSCAST Inspection Plan",
        "MSCAST Project Certificate", "MSCAST MDF", "MSCAST Transmittal",
    ],
}

# The auditor is read-only. No exceptions, including the exception log.
AUDIT_READONLY = ["Auditor", "MSCAST Statutory Auditor"]


def _perm_rows(doctype, role):
    out = []
    for tbl in ("Custom DocPerm", "DocPerm"):
        out += [(tbl, n) for n in frappe.get_all(
            tbl, filters={"parent": doctype, "role": role}, pluck="name")]
    return out


def grant(doctype, role):
    if not frappe.db.exists("DocType", doctype):
        return "no such doctype"
    rows = _perm_rows(doctype, role)
    if rows:
        for tbl, name in rows:
            d = frappe.get_doc(tbl, name)
            d.read = d.write = d.create = 1
            d.report = d.export = d.print = d.email = d.share = 1
            d.flags.ignore_permissions = True
            d.save()
        return "updated %d row(s)" % len(rows)
    d = frappe.get_doc({
        "doctype": "Custom DocPerm", "parent": doctype, "parenttype": "DocType",
        "parentfield": "permissions", "role": role, "permlevel": 0,
        "read": 1, "write": 1, "create": 1,
        "report": 1, "export": 1, "print": 1, "email": 1, "share": 1,
    })
    d.flags.ignore_permissions = True
    d.insert()
    return "created"


def revoke_create(doctype, role):
    rows = _perm_rows(doctype, role)
    if not rows:
        return "no rows"
    n = 0
    for tbl, name in rows:
        d = frappe.get_doc(tbl, name)
        if d.create or d.delete:
            d.create = 0
            d.delete = 0
            d.flags.ignore_permissions = True
            d.save()
            n += 1
    return "cleared create on %d row(s)" % n if n else "already clear"


def make_readonly(role):
    changed = []
    for tbl in ("Custom DocPerm", "DocPerm"):
        for r in frappe.get_all(tbl, filters={"role": role},
                                fields=["name", "parent", "write", "create",
                                        "delete", "submit", "cancel", "amend"]):
            if not (r.write or r.create or r.delete or r.submit or r.cancel or r.amend):
                continue
            d = frappe.get_doc(tbl, r.name)
            d.write = d.create = d.delete = d.submit = d.cancel = d.amend = 0
            d.read = 1
            d.flags.ignore_permissions = True
            d.save()
            changed.append(r.parent)
    return changed


def main():
    print("=" * 70)
    print("1. kick-off checklist condition on EVERY route into PO Verified")
    print("=" * 70)
    wf = frappe.get_doc("Workflow", "MSCAST Project Kick-off")
    COND = ("doc.chk_price and doc.chk_scope and doc.chk_payment_terms "
            "and doc.chk_tax_gst")
    fixed = 0
    for t in wf.transitions:
        if t.next_state == "PO Verified" and (t.condition or "").strip() != COND:
            print("   %-22s --%-20s--> %-14s  condition was %r"
                  % (t.state, t.action, t.next_state, t.condition or None))
            t.condition = COND
            fixed += 1
    if fixed:
        wf.flags.ignore_permissions = True
        wf.save()
        print("   %d transition(s) given the checklist condition" % fixed)
    else:
        print("   already correct on every route")

    print("")
    print("   records already approved with an unticked checklist:")
    bad = frappe.get_all(
        "MSCAST Project Kickoff",
        filters={"workflow_state": ["in", ["PO Verified", "Kick-off Approved"]]},
        fields=["name", "workflow_state", "chk_price", "chk_scope",
                "chk_payment_terms", "chk_tax_gst"])
    offenders = [k for k in bad if not (k.chk_price and k.chk_scope
                                        and k.chk_payment_terms and k.chk_tax_gst)]
    for k in offenders:
        print("      %s in %s (price=%s scope=%s terms=%s gst=%s)"
              % (k.name, k.workflow_state, k.chk_price, k.chk_scope,
                 k.chk_payment_terms, k.chk_tax_gst))
        # Put it back where the story says it is: querying the customer's terms.
        frappe.db.set_value("MSCAST Project Kickoff", k.name,
                            "workflow_state", "PO Query Raised")
        print("         -> moved back to PO Query Raised, which is what the "
              "unticked box means")
    if not offenders:
        print("      none")

    print("")
    print("=" * 70)
    print("2. give each role the permissions its role card describes")
    print("=" * 70)
    for role, doctypes in GRANT.items():
        if not frappe.db.exists("Role", role):
            print("   %-18s ROLE DOES NOT EXIST" % role)
            continue
        for dt in doctypes:
            print("   %-18s %-34s %s" % (role, dt, grant(dt, role)))

    print("")
    print("   narrowing Accounts User to what its card claims:")
    for role, doctypes in REVOKE_CREATE.items():
        for dt in doctypes:
            print("   %-18s %-34s %s" % (role, dt, revoke_create(dt, role)))

    for tbl in ("Custom DocPerm", "DocPerm"):
        for r in frappe.get_all(tbl, filters={"parent": "Payment Entry",
                                              "role": "Accounts User"},
                                fields=["name", "submit", "cancel"]):
            if r.submit or r.cancel:
                d = frappe.get_doc(tbl, r.name)
                d.submit = d.cancel = 0
                d.flags.ignore_permissions = True
                d.save()
                print("   Accounts User      Payment Entry   submit/cancel removed "
                      "- the card says it cannot release a payment")

    print("")
    print("=" * 70)
    print("3. the auditor is read-only")
    print("=" * 70)
    for role in AUDIT_READONLY:
        if not frappe.db.exists("Role", role):
            print("   %-26s role does not exist" % role)
            continue
        changed = make_readonly(role)
        if changed:
            for dt in sorted(set(changed)):
                print("   %-26s stripped write/create/delete on %s" % (role, dt))
        else:
            print("   %-26s already read-only everywhere" % role)

    frappe.db.commit()

    # Permission changes are cached per user. Without this, a logged-in session
    # keeps the old answer and `frappe.has_permission` lies to you - which it did
    # while this script was being verified, reporting the auditor as still
    # writable after it had been fixed.
    frappe.clear_cache()
    print("")
    print("permission cache cleared")
    print("done")


main()
