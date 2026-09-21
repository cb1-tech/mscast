# -*- coding: utf-8 -*-
"""MSCAST's permission matrix and workflow guards - declared here, enforced on
every install and migrate.

This replaces the configuration half of seed script 183, and fixes a defect that
script introduced. Two lessons are built in:

1. A CUSTOM PERMISSION ROW REPLACES ALL THE STANDARD ONES.
   When a doctype has any `Custom DocPerm` rows, Frappe uses those and ignores the
   doctype's own `DocPerm` entirely. Seed 183 granted a role by inserting one
   custom row, without first copying the standard rows across. On five doctypes -
   Project Kick-off, Transmittal, MDF, Delivery Instruction, Commissioning Report -
   every other role silently lost all access. Found 21 Sep 2026: the managing
   director, named as the kick-off approver, could not open a single kick-off.
   So this module never adds a row to a doctype: it computes the WHOLE intended
   permission set (standard rows, plus any existing customisation, plus the
   matrix below) and writes that set as one unit.

2. CONFIGURATION IN A SEED SCRIPT DOES NOT SHIP.
   A fresh install from the app had a writable auditor, roles that could not do
   their jobs, and the kick-off checklist bypass - all fixed only in a seed
   script that a real install never runs. And fixtures are re-imported on every
   migrate, so the bypass would have returned on the first upgrade. This runs
   from `after_install` and `after_migrate`, after the fixtures, so the rule
   survives both.

Idempotent: a second run changes nothing and says so.
"""
import frappe

FLAGS = ("read", "write", "create", "delete", "submit", "cancel", "amend",
         "report", "export", "import", "share", "print", "email", "select")
WRITE_FLAGS = ("write", "create", "delete", "submit", "cancel", "amend", "import")

# ---------------------------------------------------------------- the matrix
# Taken from the Role Cards, which are the specification.

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

# Accounts enters invoices, prepares payments and journals. It does not
# originate engineering, stores or purchase documents.
REVOKE_CREATE = {
    "Accounts User": [
        "MSCAST BRM", "MSCAST PCC", "MSCAST Drawing", "MSCAST MDM",
        "MSCAST Delivery Instruction", "MSCAST Inspection Plan",
        "MSCAST Project Certificate", "MSCAST MDF", "MSCAST Transmittal",
    ],
}
# Accounts User prepares a payment; releasing it is not on its card.
REVOKE_SUBMIT = {"Accounts User": ["Payment Entry"]}

# The auditor reads. It changes nothing, anywhere - including the exception log.
AUDIT_READONLY = ("Auditor", "MSCAST Statutory Auditor")

# A workflow state that a condition guards must be guarded on EVERY route in.
KICKOFF_OK = ("doc.chk_price and doc.chk_scope and doc.chk_payment_terms "
              "and doc.chk_tax_gst")
GUARDED_STATES = {("MSCAST Project Kick-off", "PO Verified"): KICKOFF_OK}


# Whoever a workflow names as an approver can open, edit and - where their step
# submits or cancels the document - submit or cancel it. Derived from the live
# workflows, so a new workflow is covered without anyone remembering to add it.
# Found 21 Sep 2026: approval roles had never been given this, so a director
# could hold the approving role and still be unable to open the purchase order.


def _approver_rights():
    out = {}
    for w in frappe.get_all("Workflow", filters={"is_active": 1},
                            fields=["name", "document_type"]):
        wf = frappe.get_doc("Workflow", w.name)
        status = {s.state: int(s.doc_status or 0) for s in wf.states}
        for t in wf.transitions:
            if t.allowed in AUDIT_READONLY:
                continue
            f = out.setdefault(w.document_type, {}).setdefault(t.allowed, {"read", "write"})
            if status.get(t.next_state) == 1:
                f.add("submit")
            elif status.get(t.next_state) == 2:
                f.add("cancel")
    return out


# ---------------------------------------------------------------- mechanics
def _key(r):
    return (r["role"], int(r.get("permlevel") or 0), int(r.get("if_owner") or 0))


def _rows(table, doctype):
    return [dict(r) for r in frappe.get_all(
        table, filters={"parent": doctype},
        fields=["role", "permlevel", "if_owner"] + list(FLAGS))]


def _intended(doctype):
    """The whole permission set this doctype should have."""
    rows = {}
    for r in _rows("DocPerm", doctype):            # the doctype's own
        rows[_key(r)] = {f: int(r.get(f) or 0) for f in FLAGS}
    for r in _rows("Custom DocPerm", doctype):     # existing customisation wins
        rows[_key(r)] = {f: int(r.get(f) or 0) for f in FLAGS}

    for role, dts in GRANT.items():
        if doctype in dts and frappe.db.exists("Role", role):
            k = (role, 0, 0)
            p = rows.setdefault(k, {f: 0 for f in FLAGS})
            for f in ("read", "write", "create", "report", "export",
                      "print", "email", "share"):
                p[f] = 1

    for role, flags in _approver_rights().get(doctype, {}).items():
        if frappe.db.exists("Role", role):
            p = rows.setdefault((role, 0, 0), {f: 0 for f in FLAGS})
            for f in flags:
                p[f] = 1

    for role, dts in REVOKE_CREATE.items():
        if doctype in dts:
            for k, p in rows.items():
                if k[0] == role:
                    p["create"] = p["delete"] = 0
    for role, dts in REVOKE_SUBMIT.items():
        if doctype in dts:
            for k, p in rows.items():
                if k[0] == role:
                    p["submit"] = p["cancel"] = 0

    for k, p in rows.items():
        if k[0] in AUDIT_READONLY:
            for f in WRITE_FLAGS:
                p[f] = 0
            p["read"] = 1
    return rows


def _current(doctype):
    custom = _rows("Custom DocPerm", doctype)
    src = custom if custom else _rows("DocPerm", doctype)
    return {_key(r): {f: int(r.get(f) or 0) for f in FLAGS} for r in src}


def _write(doctype, rows):
    frappe.db.delete("Custom DocPerm", {"parent": doctype})
    for (role, level, owner), p in sorted(rows.items()):
        d = frappe.get_doc(dict(
            doctype="Custom DocPerm", parent=doctype, parenttype="DocType",
            parentfield="permissions", role=role, permlevel=level,
            if_owner=owner, **p))
        d.flags.ignore_permissions = True
        d.db_insert()
    frappe.clear_cache(doctype=doctype)


def _scope():
    dts = set()
    for group in (GRANT, REVOKE_CREATE, REVOKE_SUBMIT):
        for v in group.values():
            dts.update(v)
    dts.update(_approver_rights().keys())
    # every doctype on which an auditor role holds any write-type right
    for table in ("DocPerm", "Custom DocPerm"):
        for r in frappe.get_all(table, filters={"role": ["in", AUDIT_READONLY]},
                                fields=["parent"] + list(WRITE_FLAGS)):
            if any(r.get(f) for f in WRITE_FLAGS):
                dts.add(r.parent)
    return sorted(d for d in dts if frappe.db.exists("DocType", d))


# ---------------------------------------------------------------- entry points
def enforce_permissions():
    changed = []
    for dt in _scope():
        want = _intended(dt)
        if want != _current(dt):
            _write(dt, want)
            changed.append(dt)
    return changed


def enforce_workflow_guards():
    fixed = []
    for (wf_name, state), cond in GUARDED_STATES.items():
        if not frappe.db.exists("Workflow", wf_name):
            continue
        wf = frappe.get_doc("Workflow", wf_name)
        dirty = False
        for t in wf.transitions:
            if t.next_state == state and (t.condition or "").strip() != cond:
                t.condition = cond
                dirty = True
                fixed.append("%s: %s --%s--> %s" % (wf_name, t.state, t.action, state))
        if dirty:
            wf.flags.ignore_permissions = True
            wf.save()
    return fixed


def enforce():
    """Called from install.configure(). Repairs loudly, never quietly."""
    perms = enforce_permissions()
    guards = enforce_workflow_guards()
    frappe.db.commit()
    frappe.clear_cache()
    if perms:
        print("mscast_erp: permission matrix applied to %d doctype(s): %s"
              % (len(perms), ", ".join(perms)))
    else:
        print("mscast_erp: permission matrix verified, no change")
    if guards:
        print("mscast_erp: REPAIRED workflow guard(s) - the fixture and the rule "
              "disagree, reconcile before the next deploy:")
        for g in guards:
            print("    " + g)
    else:
        print("mscast_erp: workflow guards verified")
    return perms, guards
