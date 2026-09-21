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

# role -> reports its card says it uses. Each listed role is added to the report
# and given read + report on the report's document type, because the report runner
# needs both, per user. Found 21 Sep 2026 building the screenshot manual: Stores
# could not open "Free Issue at Vendor" (its card's monthly job) and Accounts could
# not open "Retention and Certificates" - neither was on the report, or had the
# report right on its document. The Drawing Register had the same fault earlier.
REPORT_USERS = {
    "MSCAST Free Issue at Vendor": ["Stock User", "Purchase User"],
    "MSCAST Dispatch Schedule": ["Stock User"],
    "MSCAST Retention and Certificates": ["Accounts User"],
    "MSCAST MSME 45-Day Dues (MSMED s.15, s.43B(h))": ["Accounts User"],
    "MSCAST BRM Register": ["Accounts User", "Purchase User"],
    "MSCAST PO vs PCC Variance": ["Purchase Manager"],
    "MSCAST Inspection Status": ["Quality Manager"],
    "MSCAST Drawing Register": ["Design User"],
}

# role -> settings documents its forms read when they open. Without read access
# the form opens with a "No permission for ..." message: Stores opening a Stock
# Entry got "No permission for Stock Settings" (standard ERPNext gives Stock
# Settings to Stock Manager and Sales User only).
FORM_NEEDS = {
    "Stock User": ["Stock Settings"],
}


def _report_needs():
    """doctype -> {role: flags} derived from REPORT_USERS."""
    out = {}
    for rep, roles in REPORT_USERS.items():
        ref = frappe.db.get_value("Report", rep, "ref_doctype")
        if not ref:
            continue
        for role in roles:
            out.setdefault(ref, {}).setdefault(role, set()).update({"read", "report"})
    for role, dts in FORM_NEEDS.items():
        for dt in dts:
            out.setdefault(dt, {}).setdefault(role, set()).add("read")
    return out


# The oversight roles' rights, exactly: what the directors and the statutory
# auditor can see and do on every document. Kept as data (oversight.json) because
# it is a specification, not logic - read it as a table.
#
# Most of it was granted on live by setup scripts and never packaged, so a fresh
# install gave the CA a login that could not open a ledger and the directors no
# view of the books. Found 21 Sep 2026 by comparing a fresh install with live,
# row by row. The auditor rule below still strips any write-type right from the
# statutory auditor, whatever this file says.
import json as _json
import os as _os
OVERSIGHT = _json.load(open(_os.path.join(_os.path.dirname(__file__), "oversight.json")))

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
# A BRM certifies that quantity, rate, inspection and delivery were checked -
# that is what releases the money. Until 21 Sep 2026 a director could certify one
# with all four boxes unticked; the demo screenshot of a certified BRM showed
# exactly that. Same rule as the kick-off: the checklist gates the state.
BRM_OK = "doc.qty_check and doc.rate_check and doc.inspection_check and doc.delivery_check"
GUARDED_STATES = {("MSCAST Project Kick-off", "PO Verified"): KICKOFF_OK,
                  ("MSCAST BRM Certification", "Certified"): BRM_OK}


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

    for role, per_doctype in OVERSIGHT.items():
        if doctype in per_doctype and frappe.db.exists("Role", role):
            p = rows.setdefault((role, 0, 0), {f: 0 for f in FLAGS})
            for f in per_doctype[doctype]:
                p[f] = 1

    for role, flags in _report_needs().get(doctype, {}).items():
        if frappe.db.exists("Role", role):
            p = rows.setdefault((role, 0, 0), {f: 0 for f in FLAGS})
            for f in flags:
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
    for per_doctype in OVERSIGHT.values():
        dts.update(per_doctype)
    dts.update(_approver_rights().keys())
    dts.update(_report_needs().keys())
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


def enforce_report_roles():
    """A register of a document is open to everyone who can report on that document.

    Add-only, on reports about MSCAST's own documents. The report runner checks
    two things per USER across all their roles - a role listed on the report, and
    the 'report' right on its document type - and they need not come from the same
    role. So a listed role that looks useless on its own may still be what lets a
    particular user in; removing it can take away access that works. An earlier
    version of this rule did remove such roles, on 21 Sep 2026, and was reverted
    the same hour. Adding can only grant.

    Found by the demo screenshot run: the Drawing Register was closed to the
    drawing office.
    """
    changed = []
    for r in frappe.get_all("Report", filters={"is_standard": "No"}, fields=["name", "ref_doctype"]):
        can = set(REPORT_USERS.get(r.name, []))
        if r.ref_doctype and frappe.db.get_value("DocType", r.ref_doctype, "module") == "MSCAST":
            can |= {p.role for p in frappe.get_meta(r.ref_doctype).permissions
                    if p.report and not p.permlevel} - {"All", "Guest", "Desk User"}
        if not can:
            continue
        doc = frappe.get_doc("Report", r.name)
        add = sorted(c for c in can - {x.role for x in doc.roles} if frappe.db.exists("Role", c))
        if add:
            for role in add:
                doc.append("roles", {"role": role})
            doc.flags.ignore_permissions = True
            doc.save()
            changed.append("%s (+%s)" % (r.name, ", ".join(add)))
    return changed


def enforce():
    """Called from install.configure(). Repairs loudly, never quietly."""
    perms = enforce_permissions()
    guards = enforce_workflow_guards()
    reports = enforce_report_roles()
    frappe.db.commit()
    frappe.clear_cache()
    if perms:
        print("mscast_erp: permission matrix applied to %d doctype(s): %s"
              % (len(perms), ", ".join(perms)))
    else:
        print("mscast_erp: permission matrix verified, no change")
    if reports:
        print("mscast_erp: report access corrected: " + "; ".join(reports))
    else:
        print("mscast_erp: report access verified")
    if guards:
        print("mscast_erp: REPAIRED workflow guard(s) - the fixture and the rule "
              "disagree, reconcile before the next deploy:")
        for g in guards:
            print("    " + g)
    else:
        print("mscast_erp: workflow guards verified")
    return perms, guards
