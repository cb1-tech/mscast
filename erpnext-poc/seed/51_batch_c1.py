"""MSCAST POC - 51: BATCH C part 1 - auditor/director roles, MSME 45-day report,
SO-PO-invoice tracker, project closure report."""
import frappe
from frappe.permissions import add_permission, update_permission_property

COMPANY = "MSCAST Engineering Pvt Ltd"
log = lambda m: print("[C1] " + m, flush=True)


def step(name, fn, *a, **kw):
    try:
        out = fn(*a, **kw)
        frappe.db.commit()
        log("OK   " + name + ((" -> " + str(out)) if out else ""))
        return out or True
    except Exception as e:
        frappe.db.rollback()
        log("FAIL " + name + " :: " + repr(e)[:320])
        return None


def ins(doc, submit=False):
    d = frappe.get_doc(doc)
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    d.insert(ignore_if_duplicate=True)
    if submit:
        d.submit()
    return d


def qreport(name, ref_dt, sql, roles=("System Manager", "Accounts Manager"), total=False):
    exists = frappe.db.exists("Report", name)
    d = frappe.get_doc("Report", name) if exists else frappe.new_doc("Report")
    d.update({"report_name": name, "ref_doctype": ref_dt, "report_type": "Query Report",
              "is_standard": "No", "module": "Custom", "disabled": 0,
              "add_total_row": 1 if total else 0, "query": sql})
    d.set("roles", [{"role": r} for r in roles])
    d.flags.ignore_permissions = True
    d.save() if exists else d.insert()
    return name


# ---------------------------------------------------------------- AC-20 roles
AUDITOR_READ = ["GL Entry", "Journal Entry", "Sales Invoice", "Purchase Invoice", "Payment Entry",
                "Asset", "Stock Ledger Entry", "Account", "Cost Center", "Fiscal Year",
                "Sales Order", "Purchase Order", "Delivery Note", "Purchase Receipt",
                "Version", "Activity Log", "Company", "Supplier", "Customer", "Item",
                "MSCAST BRM", "MSCAST PCC", "MSCAST Project Certificate"]

DIRECTOR_READ = AUDITOR_READ + ["Project", "Employee", "Salary Slip", "MSCAST Client Claim",
                                "MSCAST MDM", "MSCAST Drawing", "MSCAST Inspection Plan"]


def roles():
    made = []
    for rn, desk in [("MSCAST Statutory Auditor", 1), ("MSCAST Director", 1)]:
        if not frappe.db.exists("Role", rn):
            ins({"doctype": "Role", "role_name": rn, "desk_access": desk,
                 "disabled": 0, "is_custom": 1})
            made.append(rn)
    frappe.db.commit()

    def grant(role, doctypes, write=0):
        for dt in doctypes:
            if not frappe.db.exists("DocType", dt):
                continue
            try:
                if not frappe.db.exists("Custom DocPerm", {"parent": dt, "role": role}):
                    add_permission(dt, role, 0)
                for prop, val in [("read", 1), ("report", 1), ("export", 1), ("print", 1),
                                  ("write", write), ("create", 0), ("delete", 0),
                                  ("submit", 0), ("cancel", 0), ("amend", 0)]:
                    update_permission_property(dt, role, 0, prop, val)
            except Exception as e:
                log("  perm %s/%s skipped: %s" % (role, dt, repr(e)[:100]))

    grant("MSCAST Statutory Auditor", AUDITOR_READ)
    grant("MSCAST Director", DIRECTOR_READ)
    made.append("read-only permissions on %d / %d doctypes" % (len(AUDITOR_READ), len(DIRECTOR_READ)))

    for email, fname, lname, rns in [
            ("auditor@mscast.demo", "Statutory", "Auditor (DEMO)",
             ["MSCAST Statutory Auditor", "Auditor"]),
            ("director@mscast.demo", "Managing", "Director (DEMO)",
             ["MSCAST Director", "Projects Manager", "Accounts Manager"])]:
        if not frappe.db.exists("User", email):
            u = frappe.get_doc({"doctype": "User", "email": email, "first_name": fname,
                                "last_name": lname, "send_welcome_email": 0, "user_type": "System User",
                                "roles": [{"role": r} for r in rns if frappe.db.exists("Role", r)]})
            u.flags.ignore_permissions = True
            u.insert()
            made.append(email)
    return "; ".join(made) or "(already in place)"


# ---------------------------------------------------------------- AC-11 MSME
def msme_flags():
    data = [("Pushkar Fabricators (DEMO)", "Micro", "UDYAM-MH-26-0041872"),
            ("Shivneri Machining Works (DEMO)", "Small", "UDYAM-MH-26-0117430"),
            ("Suvarna Copper Moulds (DEMO)", "Small", "UDYAM-MH-26-0093118"),
            ("Pune Electrical Panels (DEMO)", "Micro", "UDYAM-MH-26-0155902")]
    n = 0
    for sup, typ, udyam in data:
        if frappe.db.exists("Supplier", sup):
            frappe.db.set_value("Supplier", sup, {"msme_type": typ, "msme_udyam_no": udyam})
            n += 1
    return "%d suppliers flagged as MSME" % n


MSME_SQL = """
select
  pi.supplier                                             as "Supplier:Link/Supplier:200",
  s.msme_type                                             as "MSME Class::90",
  s.msme_udyam_no                                         as "Udyam Registration::170",
  pi.name                                                 as "Purchase Invoice:Link/Purchase Invoice:150",
  pi.bill_no                                              as "Supplier Bill No::130",
  ifnull(pi.bill_date, pi.posting_date)                   as "Bill Date:Date:90",
  date_add(ifnull(pi.bill_date, pi.posting_date), interval 45 day)
                                                          as "Sec 15 Due (45 d):Date:110",
  pi.grand_total                                          as "Invoice Amount:Currency:130",
  pi.outstanding_amount                                   as "Outstanding:Currency:130",
  datediff(curdate(), ifnull(pi.bill_date, pi.posting_date))
                                                          as "Age (days):Int:90",
  greatest(0, datediff(curdate(), date_add(ifnull(pi.bill_date, pi.posting_date), interval 45 day)))
                                                          as "Days Beyond 45:Int:110",
  case
    when pi.outstanding_amount <= 0 then 'Paid'
    when datediff(curdate(), ifnull(pi.bill_date, pi.posting_date)) > 45
      then 'BEYOND 45 DAYS - s.43B(h) disallowance + MSME Form I'
    when datediff(curdate(), ifnull(pi.bill_date, pi.posting_date)) > 30
      then 'Due within 15 days'
    else 'Within 45 days'
  end                                                     as "MSMED Status::300"
from `tabPurchase Invoice` pi
inner join `tabSupplier` s on s.name = pi.supplier
where pi.docstatus = 1 and ifnull(s.msme_type, '') != ''
order by pi.outstanding_amount desc, pi.bill_date
"""

TRACKER_SQL = """
select
  so.project                                              as "Project:Link/Project:110",
  so.name                                                 as "Sales Order:Link/Sales Order:150",
  so.customer                                             as "Customer:Link/Customer:210",
  so.transaction_date                                     as "SO Date:Date:90",
  so.grand_total                                          as "SO Value:Currency:130",
  (select ifnull(sum(sii.amount), 0) from `tabSales Invoice Item` sii
     inner join `tabSales Invoice` si on si.name = sii.parent
     where si.docstatus = 1 and si.is_return = 0 and sii.sales_order = so.name)
                                                          as "Billed to Client:Currency:140",
  (select ifnull(sum(si.grand_total - si.outstanding_amount), 0) from `tabSales Invoice` si
     inner join `tabSales Invoice Item` sii on sii.parent = si.name
     where si.docstatus = 1 and si.is_return = 0 and sii.sales_order = so.name)
                                                          as "Collected:Currency:130",
  (select ifnull(sum(poi.amount), 0) from `tabPurchase Order Item` poi
     inner join `tabPurchase Order` po on po.name = poi.parent
     where po.docstatus = 1 and poi.project = so.project)
                                                          as "PO Committed:Currency:140",
  (select ifnull(sum(pii.amount), 0) from `tabPurchase Invoice Item` pii
     inner join `tabPurchase Invoice` pi on pi.name = pii.parent
     where pi.docstatus = 1 and pii.project = so.project)
                                                          as "Supplier Billed:Currency:140",
  (select count(*) from `tabPurchase Order` po2
     inner join `tabPurchase Order Item` poi2 on poi2.parent = po2.name
     where po2.docstatus = 1 and poi2.project = so.project)
                                                          as "PO Lines:Int:80",
  so.per_delivered                                        as "% Delivered:Percent:100",
  so.per_billed                                           as "% Billed:Percent:95",
  so.status                                               as "SO Status::110"
from `tabSales Order` so
where so.docstatus = 1 and so.company = '""" + COMPANY + """'
order by so.transaction_date desc
"""

CLOSURE_SQL = """
select
  p.name                                                  as "Project:Link/Project:110",
  p.project_name                                          as "Description::260",
  p.status                                                as "Status::90",
  p.expected_start_date                                   as "Start:Date:90",
  p.expected_end_date                                     as "Contract End:Date:100",
  (select ifnull(sum(so.grand_total), 0) from `tabSales Order` so
     where so.docstatus = 1 and so.project = p.name)      as "Contract Value:Currency:140",
  (select ifnull(max(pcc.total_estimated_cost), 0) from `tabMSCAST PCC` pcc
     where pcc.project = p.name)                          as "PCC Est. Cost:Currency:140",
  (select ifnull(sum(pii.amount), 0) from `tabPurchase Invoice Item` pii
     inner join `tabPurchase Invoice` pi on pi.name = pii.parent
     where pi.docstatus = 1 and pii.project = p.name)     as "Actual Bought-out:Currency:150",
  (select ifnull(sum(sii.amount), 0) from `tabSales Invoice Item` sii
     inner join `tabSales Invoice` si on si.name = sii.parent
     where si.docstatus = 1 and si.is_return = 0 and sii.project = p.name)
                                                          as "Billed:Currency:130",
  (select ifnull(sum(si.outstanding_amount), 0) from `tabSales Invoice` si
     where si.docstatus = 1 and si.is_return = 0 and si.project = p.name)
                                                          as "Receivable:Currency:130",
  (select count(*) from `tabMSCAST Project Certificate` c
     where c.project = p.name)                            as "Certificates:Int:100",
  (select count(*) from `tabMSCAST Client Claim` cl
     where cl.project = p.name and cl.status not in ('Settled', 'Rejected'))
                                                          as "Open Claims:Int:95",
  (select count(*) from `tabMSCAST Drawing` d
     where d.project = p.name and d.status != 'Approved')  as "Drawings not approved:Int:150",
  (select count(*) from `tabMSCAST Inspection Plan` ip
     where ip.project = p.name and ifnull(ip.result, '') != 'Accepted')
                                                          as "Inspections open:Int:130",
  case
    when p.status = 'Completed' then 'Closed'
    when (select count(*) from `tabMSCAST Client Claim` cl2
            where cl2.project = p.name and cl2.status not in ('Settled', 'Rejected')) > 0
      then 'Cannot close - claims open'
    when (select ifnull(sum(si2.outstanding_amount), 0) from `tabSales Invoice` si2
            where si2.docstatus = 1 and si2.is_return = 0 and si2.project = p.name) > 0
      then 'Cannot close - money outstanding'
    else 'Ready for closure'
  end                                                     as "Closure Verdict::220"
from `tabProject` p
where p.company = '""" + COMPANY + """'
order by p.name
"""


def reports():
    made = [qreport("MSCAST MSME 45-Day Dues (MSMED s.15, s.43B(h))", "Purchase Invoice",
                    MSME_SQL, ("System Manager", "Accounts Manager", "Accounts User",
                               "MSCAST Statutory Auditor", "MSCAST Director"), total=True),
            qreport("MSCAST SO - PO - Invoice Tracker", "Sales Order", TRACKER_SQL,
                    ("System Manager", "Accounts Manager", "Projects Manager", "Sales User",
                     "MSCAST Director"), total=True),
            qreport("MSCAST Project Closure Report", "Project", CLOSURE_SQL,
                    ("System Manager", "Accounts Manager", "Projects Manager",
                     "MSCAST Director", "MSCAST Statutory Auditor"))]
    return "; ".join(made)


def smoke():
    out = []
    for r in ["MSCAST MSME 45-Day Dues (MSMED s.15, s.43B(h))",
              "MSCAST SO - PO - Invoice Tracker", "MSCAST Project Closure Report"]:
        try:
            q = frappe.db.get_value("Report", r, "query")
            rows = frappe.db.sql(q, as_dict=False)
            out.append("%s -> %d rows" % (r, len(rows)))
        except Exception as e:
            out.append("%s -> ERROR %s" % (r, repr(e)[:200]))
    return " | ".join(out)


def run():
    step("auditor + director roles and demo users", roles)
    step("MSME supplier flags", msme_flags)
    step("query reports", reports)
    step("report smoke test", smoke)
    frappe.clear_cache()
    log("BATCH C1 DONE")


run()
