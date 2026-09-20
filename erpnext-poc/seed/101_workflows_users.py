"""MSCAST POC - 101: approval workflows for PCC, Purchase Order and BRM + department users.

ASSUMPTION: no org chart was supplied. Approvers are modelled on a 10-person engineer-to-order
company - the person who raises a document is never the person who approves it, and anything that
commits money above the PCC estimate needs the director.
"""
import frappe

COMPANY = "MSCAST Engineering Pvt Ltd"
log = lambda m: print("[101] " + m, flush=True)


def step(name, fn, *a, **kw):
    try:
        out = fn(*a, **kw)
        frappe.db.commit()
        log("OK   " + name + ((" -> " + str(out)) if out else ""))
        return out or True
    except Exception as e:
        frappe.db.rollback()
        log("FAIL " + name + " :: " + repr(e)[:400])
        return None


def ins(doc, submit=False):
    d = frappe.get_doc(doc)
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    d.insert(ignore_if_duplicate=True)
    if submit:
        d.submit()
    return d


def ensure_states(names):
    styles = {"Draft": "", "Pending Approval": "Warning", "Approved": "Success",
              "Revision Required": "Danger", "Rejected": "Danger", "Certified": "Success",
              "Paid": "Primary", "Pending": "Warning", "Sent for Approval": "Warning"}
    for n in names:
        if not frappe.db.exists("Workflow State", n):
            ins({"doctype": "Workflow State", "workflow_state_name": n, "style": styles.get(n, "")})


def ensure_actions(names):
    for n in names:
        if not frappe.db.exists("Workflow Action Master", n):
            ins({"doctype": "Workflow Action Master", "workflow_action_name": n})


def workflow(name, dt, state_field, states, transitions):
    if frappe.db.exists("Workflow", name):
        return "exists"
    ensure_states([s["state"] for s in states])
    ensure_actions([t["action"] for t in transitions])
    frappe.db.commit()
    ins({"doctype": "Workflow", "workflow_name": name, "document_type": dt, "is_active": 1,
         "workflow_state_field": state_field, "send_email_alert": 0,
         "states": states, "transitions": transitions})
    return "created"


# ------------------------------------------------------------------ users
def users():
    made = []
    people = [
        ("accounts@mscast.demo", "Accounts", "Executive (DEMO)",
         ["Accounts User", "Accounts Manager", "Employee"]),
        ("purchase@mscast.demo", "Purchase", "Engineer (DEMO)",
         ["Purchase User", "Purchase Manager", "Stock User", "Employee"]),
        ("design@mscast.demo", "Design", "Engineer (DEMO)",
         ["Projects User", "Projects Manager", "Employee"]),
        ("stores@mscast.demo", "Stores", "Incharge (DEMO)",
         ["Stock User", "Stock Manager", "Item Manager", "Employee"]),
        ("hr@mscast.demo", "HR and Admin", "Officer (DEMO)",
         ["HR User", "HR Manager", "Employee"]),
    ]
    for email, fn, ln, roles in people:
        if frappe.db.exists("User", email):
            continue
        u = frappe.get_doc({"doctype": "User", "email": email, "first_name": fn, "last_name": ln,
                            "send_welcome_email": 0, "user_type": "System User",
                            "roles": [{"role": r} for r in roles if frappe.db.exists("Role", r)]})
        u.flags.ignore_permissions = True
        u.insert()
        # fictional domain - never let system mail try to reach it
        frappe.db.set_value("User", email, "unsubscribed", 1)
        made.append(email)
    return ", ".join(made) or "already exist"


# ------------------------------------------------------------------ workflows
def wf_pcc():
    r = workflow("MSCAST PCC Approval", "MSCAST PCC", "workflow_state",
                 [{"state": "Draft", "doc_status": "0", "allow_edit": "Projects Manager"},
                  {"state": "Pending Approval", "doc_status": "0", "allow_edit": "Accounts Manager"},
                  {"state": "Revision Required", "doc_status": "0", "allow_edit": "Projects Manager"},
                  {"state": "Approved", "doc_status": "0", "allow_edit": "System Manager"}],
                 [{"state": "Draft", "action": "Send for Approval", "next_state": "Pending Approval",
                   "allowed": "Projects Manager"},
                  {"state": "Pending Approval", "action": "Approve", "next_state": "Approved",
                   "allowed": "System Manager"},
                  {"state": "Pending Approval", "action": "Send Back", "next_state": "Revision Required",
                   "allowed": "Accounts Manager"},
                  {"state": "Revision Required", "action": "Send for Approval",
                   "next_state": "Pending Approval", "allowed": "Projects Manager"}])
    for n, st in frappe.db.sql("""select name, status from `tabMSCAST PCC`"""):
        frappe.db.set_value("MSCAST PCC", n, "workflow_state",
                            "Approved" if (st or "").lower().startswith("approv") else "Draft")
    return r


def wf_po():
    r = workflow("MSCAST Purchase Order Approval", "Purchase Order", "workflow_state",
                 [{"state": "Draft", "doc_status": "0", "allow_edit": "Purchase User"},
                  {"state": "Pending Approval", "doc_status": "0", "allow_edit": "Purchase Manager"},
                  {"state": "Approved", "doc_status": "1", "allow_edit": "System Manager"},
                  {"state": "Rejected", "doc_status": "0", "allow_edit": "Purchase Manager"}],
                 [{"state": "Draft", "action": "Send for Approval", "next_state": "Pending Approval",
                   "allowed": "Purchase User"},
                  {"state": "Pending Approval", "action": "Approve", "next_state": "Approved",
                   "allowed": "Purchase Manager"},
                  {"state": "Pending Approval", "action": "Reject", "next_state": "Rejected",
                   "allowed": "Purchase Manager"}])
    for n, ds in frappe.db.sql("""select name, docstatus from `tabPurchase Order`"""):
        frappe.db.set_value("Purchase Order", n, "workflow_state",
                            "Approved" if ds == 1 else "Draft")
    return r


def wf_brm():
    """Uses the BRM's own status field as the workflow state, so the payment-block server script
    keeps working unchanged - it reads status == 'Certified'."""
    r = workflow("MSCAST BRM Certification", "MSCAST BRM", "status",
                 [{"state": "Pending", "doc_status": "0", "allow_edit": "Purchase Manager"},
                  {"state": "Certified", "doc_status": "0", "allow_edit": "Accounts Manager"},
                  {"state": "Rejected", "doc_status": "0", "allow_edit": "Purchase Manager"},
                  {"state": "Paid", "doc_status": "0", "allow_edit": "Accounts Manager"}],
                 [{"state": "Pending", "action": "Certify", "next_state": "Certified",
                   "allowed": "Purchase Manager"},
                  {"state": "Pending", "action": "Reject", "next_state": "Rejected",
                   "allowed": "Purchase Manager"},
                  {"state": "Certified", "action": "Mark Paid", "next_state": "Paid",
                   "allowed": "Accounts Manager"}])
    return r


def verify():
    out = []
    for w in frappe.get_all("Workflow", fields=["name", "document_type", "workflow_state_field",
                                                "is_active"]):
        ns = frappe.db.count("Workflow Document State", {"parent": w.name})
        nt = frappe.db.count("Workflow Transition", {"parent": w.name})
        out.append("%s on %s (field %s, %d states, %d transitions, active=%s)"
                   % (w.name, w.document_type, w.workflow_state_field, ns, nt, w.is_active))
    return " | ".join(out)


def run():
    step("department users", users)
    step("PCC approval workflow", wf_pcc)
    step("purchase order approval workflow", wf_po)
    step("BRM certification workflow", wf_brm)
    step("verify workflows", verify)
    frappe.clear_cache()
    log("SCRIPT 101 DONE")


run()
