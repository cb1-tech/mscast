# -*- coding: utf-8 -*-
"""MSCAST Exception Sweep — the deterministic half of the discrepancy agent.

Rules look ACROSS documents for states that cannot both be true. Standard ERPNext
reports answer "what is the number"; these answer "this number disagrees with that one".
Findings land in the MSCAST Exception doctype, which the agentic layer then reads.
"""
import frappe

DT = "MSCAST Exception"

FIELDS = [
    {"fieldname": "rule_code", "label": "Rule", "fieldtype": "Data", "in_list_view": 1, "reqd": 1, "in_standard_filter": 1},
    {"fieldname": "title", "label": "Finding", "fieldtype": "Data", "in_list_view": 1, "reqd": 1},
    {"fieldname": "severity", "label": "Severity", "fieldtype": "Select", "options": "High\nMedium\nLow",
     "in_list_view": 1, "in_standard_filter": 1, "default": "Medium"},
    {"fieldname": "owner_area", "label": "Whose job", "fieldtype": "Select",
     "options": "Sales\nProjects\nDesign\nPurchase\nStores\nQuality\nAccounts\nHR\nDirector",
     "in_list_view": 1, "in_standard_filter": 1},
    {"fieldname": "col1", "fieldtype": "Column Break"},
    {"fieldname": "status", "label": "Status", "fieldtype": "Select",
     "options": "Open\nAcknowledged\nResolved\nIgnored", "default": "Open",
     "in_list_view": 1, "in_standard_filter": 1},
    {"fieldname": "ref_doctype", "label": "Document Type", "fieldtype": "Link", "options": "DocType"},
    {"fieldname": "ref_name", "label": "Document", "fieldtype": "Dynamic Link", "options": "ref_doctype"},
    {"fieldname": "amount", "label": "Amount at stake", "fieldtype": "Currency"},
    {"fieldname": "sec1", "fieldtype": "Section Break"},
    {"fieldname": "details", "label": "What is inconsistent", "fieldtype": "Small Text"},
    {"fieldname": "suggested_action", "label": "Suggested action", "fieldtype": "Small Text"},
    {"fieldname": "sec2", "fieldtype": "Section Break"},
    {"fieldname": "first_seen", "label": "First seen", "fieldtype": "Date", "read_only": 1},
    {"fieldname": "last_seen", "label": "Last seen", "fieldtype": "Date", "read_only": 1},
    {"fieldname": "col2", "fieldtype": "Column Break"},
    {"fieldname": "times_seen", "label": "Days running", "fieldtype": "Int", "read_only": 1},
    {"fieldname": "resolved_on", "label": "Cleared on", "fieldtype": "Date", "read_only": 1},
]

PERMS = [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1},
    {"role": "MSCAST Director", "read": 1, "write": 1, "report": 1, "export": 1},
    {"role": "Accounts Manager", "read": 1, "write": 1, "report": 1},
    {"role": "Projects User", "read": 1, "write": 1, "report": 1},
    {"role": "Purchase User", "read": 1, "write": 1, "report": 1},
    {"role": "MSCAST Statutory Auditor", "read": 1, "report": 1, "export": 1},
]

if frappe.db.exists("DocType", DT):
    doc = frappe.get_doc("DocType", DT)
    doc.set("fields", [])
    doc.set("permissions", [])
else:
    doc = frappe.new_doc("DocType")
    doc.name = DT
    doc.custom = 1
    doc.module = "Custom"
    doc.naming_rule = "Expression (old style)"
    doc.autoname = "hash"
doc.custom = 1
doc.module = "Custom"
doc.track_changes = 1
doc.title_field = "title"
doc.sort_field = "modified"
doc.sort_order = "DESC"
for f in FIELDS:
    doc.append("fields", f)
for p in PERMS:
    if frappe.db.exists("Role", p["role"]):
        doc.append("permissions", p)
doc.save(ignore_permissions=True)
frappe.db.commit()
print("doctype ready:", DT, "fields:", len(doc.fields))

# ---------------------------------------------------------------- the sweep
SWEEP = r'''
today = frappe.db.sql("select date(convert_tz(utc_timestamp(),'+00:00','+05:30'))")[0][0]
found = []

def add(code, title, sev, area, dt, dn, details, action, amount=0, bucket=found):
    bucket.append({"rule_code": code, "title": title, "severity": sev, "owner_area": area,
                  "ref_doctype": dt, "ref_name": dn, "details": details,
               "suggested_action": action, "amount": amount or 0})

# --- X01 a machine commissioned on a project that has dispatched nothing ------
for r in frappe.db.sql("""
    select c.name, c.project, c.status, so.name so, so.per_delivered
    from `tabMSCAST Commissioning Report` c
    join `tabSales Order` so on so.project = c.project and so.docstatus = 1
    where ifnull(so.per_delivered, 0) = 0""", as_dict=True):
    add("X01", "Commissioning recorded on a project with nothing dispatched", "High", "Projects",
        "MSCAST Commissioning Report", r.name,
        "%s reports commissioning complete on %s, but %s shows 0%% delivered." % (r.name, r.project, r.so),
        "Either the dispatch was never recorded against the sales order, or the commissioning report belongs to a different project.")

# --- X02 acceptance certificate awaited with nothing dispatched ---------------
for r in frappe.db.sql("""
    select ct.name, ct.project, so.name so
    from `tabMSCAST Project Certificate` ct
    join `tabSales Order` so on so.project = ct.project and so.docstatus = 1
    where ct.status = 'Awaited' and ifnull(so.per_delivered, 0) = 0""", as_dict=True):
    add("X02", "Acceptance certificate awaited before any dispatch", "High", "Projects",
        "MSCAST Project Certificate", r.name,
        "%s is awaiting the customer's certificate for %s, but nothing has been delivered on %s." % (r.name, r.project, r.so),
        "Check the dispatch records; a certificate cannot be due before handover.")

# --- X03 dispatch not linked to a project ------------------------------------
for r in frappe.db.sql("""
    select distinct dn.name, dn.posting_date, dn.grand_total
    from `tabDelivery Note` dn
    join `tabDelivery Note Item` dni on dni.parent = dn.name
    join `tabSales Order` so on so.name = dni.against_sales_order
    where dn.docstatus = 1 and ifnull(dn.project, '') = '' and ifnull(so.project, '') <> ''""", as_dict=True):
    add("X03", "Dispatch not linked to a project", "Medium", "Stores",
        "Delivery Note", r.name,
        "%s was dispatched on %s with no project set, so its cost and revenue miss the project MIS." % (r.name, r.posting_date),
        "Set the project on the delivery note.", r.grand_total)

# --- X04 dunning raised while nothing is overdue ------------------------------
overdue = frappe.db.sql("""select count(*) c from `tabSales Invoice`
    where docstatus = 1 and outstanding_amount > 0 and due_date < %s""", (today,))[0][0]
if not overdue:
    for r in frappe.db.sql("""select name, docstatus, grand_total from `tabDunning`
        where ifnull(status,'') not in ('Resolved')""", as_dict=True):
        add("X04", "Customer being chased while no invoice is overdue", "Medium", "Accounts",
            "Dunning", r.name,
            "%s is open for %s but no sales invoice is past its due date." % (r.name, r.grand_total),
            "Close the dunning, or check whether an invoice due date is wrong.", r.grand_total)

# --- X05 a draft document that has been sitting unsubmitted -------------------
for dt, days, area in [("Dunning", 3, "Accounts"), ("Sales Invoice", 3, "Accounts"),
                       ("Purchase Invoice", 5, "Accounts"), ("Delivery Note", 3, "Stores")]:
    for r in frappe.db.sql("""select name, modified from `tab%s`
        where docstatus = 0 and datediff(%%s, date(modified)) >= %%s""" % dt, (today, days), as_dict=True):
        add("X05", "Draft %s left unsubmitted" % dt.lower(), "Low", area, dt, r.name,
            "%s has been a draft since %s. Drafts do not post to the ledger." % (r.name, r.modified),
            "Submit it or delete it.")

# --- X06 retention held against a party with no live order --------------------
for r in frappe.db.sql("""
    select je.name, jea.party, jea.debit
    from `tabJournal Entry` je join `tabJournal Entry Account` jea on jea.parent = je.name
    where je.docstatus = 1 and jea.account like '%%Retention%%' and jea.debit > 0
      and ifnull(jea.party, '') <> ''
      and jea.party not in (select distinct customer from `tabSales Order` where docstatus = 1)
      and jea.party not in (select distinct customer from `tabSales Invoice` where docstatus = 1)""", as_dict=True):
    add("X06", "Retention held against a party with nothing on file", "High", "Accounts",
        "Journal Entry", r.name,
        "%s holds retention of %s from %s, who has neither a sales order nor an invoice on file." % (r.name, r.debit, r.party),
        "Check which contract this retention belongs to; the retention report reads it from the sales order.", r.debit)

# --- X07 project underway while its cost sheet is still a draft ---------------
for r in frappe.db.sql("""
    select p.name, p.percent_complete, pc.name pcc, pc.status
    from `tabProject` p join `tabMSCAST PCC` pc on pc.project = p.name
    where p.status = 'Open' and pc.status <> 'Approved' and ifnull(p.percent_complete, 0) > 10""", as_dict=True):
    add("X07", "Work under way with no approved cost sheet", "High", "Sales",
        "MSCAST PCC", r.pcc,
        "%s is %s%% complete but its PCC %s is still %s, so there is no approved cost baseline to measure against." % (r.name, r.percent_complete, r.pcc, r.status),
        "Approve the PCC or stop booking cost to the project.")

# --- X08 kick-off not approved while the project runs -------------------------
for r in frappe.db.sql("""
    select k.name, k.project, k.workflow_state, p.percent_complete
    from `tabMSCAST Project Kickoff` k join `tabProject` p on p.name = k.project
    where ifnull(k.workflow_state, '') <> 'Kick-off Approved' and ifnull(p.percent_complete, 0) > 0""", as_dict=True):
    add("X08", "Project running before kick-off was approved", "Medium", "Projects",
        "MSCAST Project Kickoff", r.name,
        "%s is at %s while %s is %s%% complete." % (r.name, r.workflow_state, r.project, r.percent_complete),
        "Clear the kick-off query, or record why work started early.")

# --- X09 supplier bill paid or payable with no certified BRM ------------------
for r in frappe.db.sql("""
    select pi.name, pi.supplier, pi.outstanding_amount, pi.grand_total
    from `tabPurchase Invoice` pi
    where pi.docstatus = 1 and pi.outstanding_amount > 0
      and not exists (select 1 from `tabMSCAST BRM` b
                      where b.supplier = pi.supplier and b.status in ('Certified', 'Paid'))""", as_dict=True):
    add("X09", "Supplier bill outstanding with no certified BRM", "High", "Purchase",
        "Purchase Invoice", r.name,
        "%s from %s is outstanding at %s with no Billing Routing Memo certified for that supplier." % (r.name, r.supplier, r.outstanding_amount),
        "Raise and certify a BRM before Accounts release payment.", r.outstanding_amount)

# --- X10 MSME bill approaching the statutory limit ---------------------------
for r in frappe.db.sql("""
    select pi.name, pi.supplier, pi.outstanding_amount, pi.bill_date,
           datediff(%s, pi.bill_date) age
    from `tabPurchase Invoice` pi join `tabSupplier` s on s.name = pi.supplier
    where pi.docstatus = 1 and pi.outstanding_amount > 0
      and ifnull(s.msme_type, 'Not registered') in ('Micro', 'Small')
      and datediff(%s, pi.bill_date) >= 30""", (today, today), as_dict=True):
    sev = "High" if r.age >= 45 else "Medium"
    add("X10", "MSME bill nearing the 45-day limit", sev, "Accounts",
        "Purchase Invoice", r.name,
        "%s from %s is %s days old and %s is outstanding. Beyond 45 days the deduction is disallowed under s.43B(h) and interest accrues under MSMED s.16." % (r.name, r.supplier, r.age, r.outstanding_amount),
        "Release payment before day 45.", r.outstanding_amount)

# --- X11 drawing sitting with the customer too long --------------------------
for r in frappe.db.sql("""
    select name, drawing_no, title, project, modified, datediff(%s, date(modified)) age
    from `tabMSCAST Drawing`
    where status = 'For Customer Approval' and datediff(%s, date(modified)) >= 14""", (today, today), as_dict=True):
    add("X11", "Drawing with the customer beyond two weeks", "Medium", "Design",
        "MSCAST Drawing", r.name,
        "%s (%s) has been with the customer for %s days. Engineering downstream of it is blocked." % (r.drawing_no, r.project, r.age),
        "Chase the approval in writing and record the delay against the contract delivery date.")

# --- X12 inspection stage past its planned date ------------------------------
for r in frappe.db.sql("""
    select name, item_or_assembly, supplier, planned_date, datediff(%s, planned_date) late
    from `tabMSCAST Inspection Plan`
    where result = 'Pending' and planned_date < %s""", (today, today), as_dict=True):
    add("X12", "Inspection stage past its planned date", "Medium", "Quality",
        "MSCAST Inspection Plan", r.name,
        "%s at %s was planned for %s, %s days ago, and is still pending." % (r.item_or_assembly, r.supplier, r.planned_date, r.late),
        "Confirm the inspection date with the supplier or re-plan it.")

# --- X13 bank guarantee running out ------------------------------------------
for r in frappe.db.sql("""
    select name, bg_type, amount, end_date, datediff(end_date, %s) days_left
    from `tabBank Guarantee`
    where end_date is not null and datediff(end_date, %s) between 0 and 60""", (today, today), as_dict=True):
    add("X13", "Bank guarantee expiring", "High", "Accounts",
        "Bank Guarantee", r.name,
        "%s (%s, %s) expires on %s — %s days away." % (r.name, r.bg_type, r.amount, r.end_date, r.days_left),
        "Extend it or get it released; an expired PBG can block retention recovery.", r.amount)

# --- X14 active project with no hours booked ---------------------------------
for r in frappe.db.sql("""
    select p.name, p.project_name,
           (select max(t.start_date) from `tabTimesheet` t where t.parent_project = p.name and t.docstatus = 1) last_ts
    from `tabProject` p where p.status = 'Open'""", as_dict=True):
    if not r.last_ts:
        add("X14", "Open project with no time ever booked", "Medium", "Projects", "Project", r.name,
            "%s is open but no timesheet has ever been submitted against it, so engineering cost and WIP are understated." % r.name,
            "Book engineering hours weekly, or the project MIS will show a margin that is not real.")
    elif frappe.utils.date_diff(today, r.last_ts) >= 14:
        add("X14", "Open project with no time booked for a fortnight", "Low", "Projects", "Project", r.name,
            "%s last had hours booked on %s." % (r.name, r.last_ts),
            "Book engineering hours weekly.")

# --- X15 free issue sitting with a vendor too long ---------------------------
for r in frappe.db.sql("""
    select sle.item_code, sle.warehouse, sum(sle.actual_qty) qty, min(sle.posting_date) since,
           datediff(%s, min(sle.posting_date)) age
    from `tabStock Ledger Entry` sle
    where sle.is_cancelled = 0 and sle.warehouse like '%%Free Issue%%'
    group by sle.item_code, sle.warehouse having qty > 0""", (today,), as_dict=True):
    if r.age and r.age >= 180:
        add("X15", "Free-issue material with a vendor beyond six months", "Medium", "Stores",
            "Item", r.item_code,
            "%s qty %s has been at %s since %s (%s days). Job-work goods must return within a year, and ITC-04 reporting depends on it." % (r.item_code, r.qty, r.warehouse, r.since, r.age),
            "Confirm the balance with the vendor and plan the return.")

# --- X16 purchase order committed beyond the approved cost sheet -------------
for r in frappe.db.sql("""
    select po.name, po.project, sum(po.grand_total) committed, pc.total_estimated_cost, pc.name pcc
    from `tabPurchase Order` po join `tabMSCAST PCC` pc on pc.project = po.project and pc.status = 'Approved'
    where po.docstatus = 1 group by po.name, po.project, pc.total_estimated_cost, pc.name
    having committed > pc.total_estimated_cost""", as_dict=True):
    add("X16", "Purchase commitment above the approved cost sheet", "High", "Purchase",
        "Purchase Order", r.name,
        "%s commits %s on %s against an approved PCC of %s." % (r.name, r.committed, r.project, r.total_estimated_cost),
        "Revise the PCC or reduce the order; the project margin is already gone.", r.committed)

# ---------------------------------------------------------------- upsert
seen_keys = []
for f in found:
    key = f["rule_code"] + "|" + (f["ref_name"] or "")
    seen_keys.append(key)
    existing = frappe.db.get_value("MSCAST Exception",
        {"rule_code": f["rule_code"], "ref_name": f["ref_name"], "status": ["in", ["Open", "Acknowledged"]]},
        ["name", "times_seen"], as_dict=True)
    if existing:
        frappe.db.set_value("MSCAST Exception", existing.name, {
            "last_seen": today,
            "times_seen": (existing.times_seen or 1) + 1,
            "details": f["details"], "amount": f["amount"]}, update_modified=False)
    else:
        d = frappe.new_doc("MSCAST Exception")
        d.update(f)
        d.status = "Open"
        d.first_seen = today
        d.last_seen = today
        d.times_seen = 1
        d.insert(ignore_permissions=True)

# anything open that the sweep no longer finds has been fixed
for e in frappe.get_all("MSCAST Exception", filters={"status": ["in", ["Open", "Acknowledged"]]},
                        fields=["name", "rule_code", "ref_name"]):
    if (e.rule_code + "|" + (e.ref_name or "")) not in seen_keys:
        frappe.db.set_value("MSCAST Exception", e.name,
                            {"status": "Resolved", "resolved_on": today}, update_modified=False)

frappe.db.commit()
'''

name = "MSCAST Exception Sweep"
if frappe.db.exists("Server Script", name):
    s = frappe.get_doc("Server Script", name)
else:
    s = frappe.new_doc("Server Script")
    s.name = name
s.script_type = "Scheduler Event"
s.event_frequency = "Cron"
s.cron_format = "0 6 * * *"
s.module = "Custom"
s.disabled = 0
s.script = SWEEP
s.save(ignore_permissions=True)
frappe.db.commit()
print("server script saved:", s.name, "cron", s.cron_format)

# run it once now
from frappe.utils.safe_exec import safe_exec
frappe.local.response = frappe._dict({"_init": 1})
safe_exec(SWEEP, None, {})
frappe.db.commit()

rows = frappe.db.sql("""select rule_code, severity, owner_area, title, ref_doctype, ref_name, amount
    from `tabMSCAST Exception` where status = 'Open'
    order by field(severity,'High','Medium','Low'), rule_code""", as_dict=True)
print()
print("=== EXCEPTIONS RAISED: %d ===" % len(rows))
for r in rows:
    print("  [%s] %-4s %-9s %-40s %s %s" % (r.severity[0], r.rule_code, r.owner_area, r.title[:40], r.ref_doctype, r.ref_name))
