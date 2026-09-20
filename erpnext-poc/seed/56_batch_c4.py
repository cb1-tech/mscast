"""MSCAST POC - 56: BATCH C part 4 - client schedule / status prints, daily management summary,
archival job, BRM payment block."""
import frappe
from frappe.utils import nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
log = lambda m: print("[C4] " + m, flush=True)

CSS = """
.print-format { font-family: Arial, Helvetica, sans-serif; font-size: 10.5px; color:#222; }
.ms-title { font-size:15px; font-weight:700; text-align:center; letter-spacing:1px;
            border:1px solid #1f3864; background:#eef2f9; color:#1f3864; padding:5px; margin-bottom:10px; }
table.ms { width:100%; border-collapse:collapse; margin-bottom:10px; }
table.ms th { background:#1f3864; color:#fff; font-size:10px; padding:4px 5px; border:1px solid #1f3864; text-align:left; }
table.ms td { border:1px solid #c6cbd4; padding:3px 5px; vertical-align:top; }
table.meta { width:100%; border-collapse:collapse; margin-bottom:10px; }
table.meta td { border:1px solid #c6cbd4; padding:3px 6px; font-size:10px; }
table.meta td.k { background:#f2f4f8; font-weight:600; width:18%; }
.num { text-align:right; }
.ms-note { font-size:9.5px; color:#444; margin-top:6px; }
.sign { margin-top:26px; width:100%; }
.sign td { border:none; font-size:10px; padding-top:22px; border-top:1px solid #888; width:33%; text-align:center; }
.badge { display:inline-block; padding:1px 7px; border-radius:9px; font-size:9px; border:1px solid #1f3864; color:#1f3864; }
.bar { background:#e6eaf2; height:9px; width:100%; }
.bar > div { background:#1f3864; height:9px; }
"""

PERMS = [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1,
     "export": 1, "share": 1, "print": 1, "email": 1},
    {"role": "Projects Manager", "read": 1, "write": 1, "create": 1, "report": 1, "print": 1},
    {"role": "Accounts User", "read": 1, "report": 1, "print": 1},
]


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


def f(fieldname, label, fieldtype, **kw):
    d = {"fieldname": fieldname, "label": label, "fieldtype": fieldtype}
    d.update(kw)
    return d


def doctype(name, fields, istable=0, title_field=None, search_fields=None):
    if frappe.db.exists("DocType", name):
        return False
    d = frappe.get_doc({"doctype": "DocType", "name": name, "module": "Custom", "custom": 1,
                        "istable": istable, "editable_grid": 1 if istable else 0,
                        "track_changes": 0 if istable else 1, "allow_rename": 1,
                        "title_field": title_field, "search_fields": search_fields,
                        "sort_field": "modified", "sort_order": "DESC", "fields": fields,
                        "permissions": [] if istable else PERMS})
    d.flags.ignore_permissions = True
    d.insert()
    return True


def pf(name, doctype_name, html):
    exists = frappe.db.exists("Print Format", name)
    doc = frappe.get_doc("Print Format", name) if exists else frappe.new_doc("Print Format")
    doc.update({"name": name, "doc_type": doctype_name, "module": "Custom", "standard": "No",
                "custom_format": 1, "print_format_type": "Jinja", "disabled": 0,
                "margin_top": 12, "margin_bottom": 12, "letter_head": "MSCAST",
                "css": CSS, "html": html})
    doc.flags.ignore_permissions = True
    doc.save() if exists else doc.insert()


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


# ------------------------------------------------------------ PC-15 client schedule
SCHEDULE_HTML = """
<div class="ms-title">PROJECT EXECUTION SCHEDULE - CLIENT COPY</div>
{% set k = frappe.get_all("MSCAST Project Kickoff", filters={"project": doc.name},
       fields=["name","customer_po_no","customer_po_date","contract_delivery_date",
               "design_freeze_date","first_dispatch_target","kickoff_date"], limit=1) %}
{% set kk = k[0] if k else None %}
<table class="meta">
  <tr><td class="k">Project</td><td>{{ doc.name }} - {{ doc.project_name }}</td>
      <td class="k">Customer</td><td>{{ doc.customer or "-" }}</td></tr>
  <tr><td class="k">Customer PO</td><td>{{ kk.customer_po_no if kk else "-" }}
        {% if kk and kk.customer_po_date %} dated {{ frappe.utils.formatdate(kk.customer_po_date, "dd-MM-yyyy") }}{% endif %}</td>
      <td class="k">Contract delivery</td>
      <td>{{ frappe.utils.formatdate(kk.contract_delivery_date, "dd-MM-yyyy") if kk and kk.contract_delivery_date
              else (frappe.utils.formatdate(doc.expected_end_date, "dd-MM-yyyy") if doc.expected_end_date else "-") }}</td></tr>
  <tr><td class="k">Issued on</td><td>{{ frappe.utils.formatdate(frappe.utils.nowdate(), "dd-MM-yyyy") }}</td>
      <td class="k">Overall progress</td><td>{{ "%.0f"|format(doc.percent_complete or 0) }}%</td></tr>
</table>

<table class="ms">
  <thead><tr><th style="width:5%">#</th><th>Contractual milestone</th>
    <th style="width:18%">Planned</th><th style="width:18%">Status</th></tr></thead>
  <tbody>
    <tr><td>1</td><td>Kick-off meeting and design inputs frozen</td>
      <td>{{ frappe.utils.formatdate(kk.kickoff_date, "dd-MM-yyyy") if kk and kk.kickoff_date else "-" }}</td>
      <td>{{ "Completed" if kk and kk.kickoff_date else "Planned" }}</td></tr>
    <tr><td>2</td><td>General arrangement and detail drawings for approval</td>
      <td>{{ frappe.utils.formatdate(kk.design_freeze_date, "dd-MM-yyyy") if kk and kk.design_freeze_date else "-" }}</td>
      <td>{% set dr = frappe.get_all("MSCAST Drawing", filters={"project": doc.name}, fields=["status"]) %}
          {{ dr | selectattr("status","equalto","Approved") | list | length }} of {{ dr | length }} approved</td></tr>
    <tr><td>3</td><td>Bought-out ordering and vendor inspection</td>
      <td>-</td>
      <td>{% set ip = frappe.get_all("MSCAST Inspection Plan", filters={"project": doc.name}, fields=["result"]) %}
          {{ ip | selectattr("result","equalto","Accepted") | list | length }} of {{ ip | length }} stages cleared</td></tr>
    <tr><td>4</td><td>Manufacture, assembly and dispatch</td>
      <td>{{ frappe.utils.formatdate(kk.first_dispatch_target, "dd-MM-yyyy") if kk and kk.first_dispatch_target else "-" }}</td>
      <td>{% set md = frappe.get_all("MSCAST MDM", filters={"project": doc.name}, fields=["status"]) %}
          {{ md | length }} dispatch memo(s) raised</td></tr>
    <tr><td>5</td><td>Erection, commissioning and performance trial</td>
      <td>{{ frappe.utils.formatdate(kk.contract_delivery_date, "dd-MM-yyyy") if kk and kk.contract_delivery_date else "-" }}</td>
      <td>{% set cr = frappe.get_all("MSCAST Commissioning Report", filters={"project": doc.name}, fields=["status"]) %}
          {{ cr[0].status if cr else "Not started" }}</td></tr>
    <tr><td>6</td><td>Provisional / final acceptance and retention release</td>
      <td>-</td>
      <td>{% set ce = frappe.get_all("MSCAST Project Certificate", filters={"project": doc.name},
             fields=["certificate_type","status"]) %}
          {% if ce %}{% for c in ce %}{{ c.certificate_type }} - {{ c.status }}{% if not loop.last %}; {% endif %}{% endfor %}
          {% else %}Pending{% endif %}</td></tr>
  </tbody>
</table>

{% set tasks = frappe.get_all("Task", filters={"project": doc.name},
      fields=["subject","exp_start_date","exp_end_date","status","progress"], order_by="exp_start_date asc") %}
{% if tasks %}
<table class="ms">
  <thead><tr><th style="width:5%">#</th><th>Activity</th><th style="width:13%">Start</th>
    <th style="width:13%">Finish</th><th style="width:12%">Status</th><th style="width:12%" class="num">Progress</th></tr></thead>
  <tbody>
  {% for t in tasks %}
    <tr><td>{{ loop.index }}</td><td>{{ t.subject }}</td>
      <td>{{ frappe.utils.formatdate(t.exp_start_date, "dd-MM-yyyy") if t.exp_start_date else "-" }}</td>
      <td>{{ frappe.utils.formatdate(t.exp_end_date, "dd-MM-yyyy") if t.exp_end_date else "-" }}</td>
      <td>{{ t.status }}</td><td class="num">{{ "%.0f"|format(t.progress or 0) }}%</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endif %}
<div class="ms-note">Dates are indicative and subject to timely drawing approvals, free-issue material and
site readiness by the customer. Any hold at site or delayed approval shifts the downstream milestones.</div>
<table class="sign"><tr><td>Prepared by - MSCAST Projects</td><td>Approved by</td><td>Customer acknowledgement</td></tr></table>
"""

STATUS_HTML = """
<div class="ms-title">PROJECT STATUS REPORT</div>
<table class="meta">
  <tr><td class="k">Project</td><td>{{ doc.name }} - {{ doc.project_name }}</td>
      <td class="k">Customer</td><td>{{ doc.customer or "-" }}</td></tr>
  <tr><td class="k">Report date</td><td>{{ frappe.utils.formatdate(frappe.utils.nowdate(), "dd-MM-yyyy") }}</td>
      <td class="k">Status</td><td><span class="badge">{{ doc.status }}</span></td></tr>
</table>
<div class="bar"><div style="width:{{ doc.percent_complete or 0 }}%"></div></div>
<div class="ms-note">Overall completion {{ "%.0f"|format(doc.percent_complete or 0) }}%</div>

{% set so = frappe.get_all("Sales Order", filters={"project": doc.name, "docstatus": 1},
      fields=["name","grand_total","per_billed","per_delivered"]) %}
{% set contract = so | sum(attribute="grand_total") %}
{% set billed = frappe.db.get_value("Sales Invoice", {"project": doc.name, "docstatus": 1, "is_return": 0}, "sum(grand_total)") or 0 %}
{% set outst = frappe.db.get_value("Sales Invoice", {"project": doc.name, "docstatus": 1, "is_return": 0}, "sum(outstanding_amount)") or 0 %}
<table class="ms">
  <thead><tr><th>Commercial</th><th class="num" style="width:22%">Amount (Rs)</th>
    <th>Engineering and execution</th><th style="width:22%">Position</th></tr></thead>
  <tbody>
    <tr><td>Contract value (orders booked)</td><td class="num">{{ frappe.utils.fmt_money(contract) }}</td>
      <td>Drawings released / approved</td>
      <td>{% set dr = frappe.get_all("MSCAST Drawing", filters={"project": doc.name}, fields=["status"]) %}
          {{ dr | selectattr("status","equalto","Approved") | list | length }} of {{ dr | length }}</td></tr>
    <tr><td>Billed to date</td><td class="num">{{ frappe.utils.fmt_money(billed) }}</td>
      <td>Material data files released</td>
      <td>{{ frappe.get_all("MSCAST MDF", filters={"project": doc.name}) | length }}</td></tr>
    <tr><td>Outstanding from customer</td><td class="num">{{ frappe.utils.fmt_money(outst) }}</td>
      <td>Vendor inspections cleared</td>
      <td>{% set ip = frappe.get_all("MSCAST Inspection Plan", filters={"project": doc.name}, fields=["result"]) %}
          {{ ip | selectattr("result","equalto","Accepted") | list | length }} of {{ ip | length }}</td></tr>
    <tr><td>Bought-out billed by suppliers</td>
      <td class="num">{{ frappe.utils.fmt_money(frappe.db.get_value("Purchase Invoice Item", {"project": doc.name, "docstatus": 1}, "sum(amount)") or 0) }}</td>
      <td>Dispatch memos raised</td>
      <td>{{ frappe.get_all("MSCAST MDM", filters={"project": doc.name}) | length }}</td></tr>
    <tr><td>Open client claims</td>
      <td class="num">{{ frappe.utils.fmt_money(frappe.db.get_value("MSCAST Client Claim", {"project": doc.name, "status": ["not in", ["Settled","Rejected"]]}, "sum(claim_amount)") or 0) }}</td>
      <td>Commissioning</td>
      <td>{% set cr = frappe.get_all("MSCAST Commissioning Report", filters={"project": doc.name}, fields=["status"]) %}
          {{ cr[0].status if cr else "Not started" }}</td></tr>
  </tbody>
</table>

{% set punch = frappe.get_all("MSCAST Commissioning Report", filters={"project": doc.name}, fields=["punch_points"]) %}
{% if punch and punch[0].punch_points %}
<div class="ms-note"><b>Open punch points:</b><div style="white-space:pre-line">{{ punch[0].punch_points }}</div></div>
{% endif %}
{% set kk = frappe.get_all("MSCAST Project Kickoff", filters={"project": doc.name}, fields=["open_points"], limit=1) %}
{% if kk and kk[0].open_points %}
<div class="ms-note"><b>Open points with the customer:</b> {{ kk[0].open_points }}</div>
{% endif %}
<table class="sign"><tr><td>MSCAST Project Manager</td><td>MSCAST Management</td><td>Customer</td></tr></table>
"""


def project_prints():
    pf("MSCAST Project Schedule (Client)", "Project", SCHEDULE_HTML)
    pf("MSCAST Project Status Report", "Project", STATUS_HTML)
    out = []
    for fmt in ["MSCAST Project Schedule (Client)", "MSCAST Project Status Report"]:
        for p in frappe.get_all("Project", pluck="name"):
            try:
                html = frappe.get_print("Project", p, print_format=fmt)
                out.append("%s/%s ok (%d chars)" % (fmt.split("(")[0].strip(), p, len(html)))
            except Exception as e:
                out.append("%s/%s RENDER ERROR %s" % (fmt, p, repr(e)[:220]))
    return " | ".join(out)


# ------------------------------------------------------------ MG-03 daily summary
DAILY_SQL = """
select 'Cash' as "Area::110", 'Cash and bank balance' as "Indicator::330",
  format(ifnull((select sum(gl.debit - gl.credit) from `tabGL Entry` gl
     inner join `tabAccount` a on a.name = gl.account
     where gl.is_cancelled = 0 and a.account_type in ('Bank','Cash')), 0), 0) as "Value::170"
union all select 'Receivables', 'Outstanding from customers',
  format(ifnull((select sum(outstanding_amount) from `tabSales Invoice`
     where docstatus = 1 and is_return = 0), 0), 0)
union all select 'Receivables', 'Overdue beyond due date',
  format(ifnull((select sum(outstanding_amount) from `tabSales Invoice`
     where docstatus = 1 and is_return = 0 and due_date < curdate()), 0), 0)
union all select 'Receivables', 'Retention held by customers',
  format(ifnull((select sum(gl.debit - gl.credit) from `tabGL Entry` gl
     where gl.is_cancelled = 0 and gl.account like '%%Retention%%'), 0), 0)
union all select 'Payables', 'Outstanding to suppliers',
  format(ifnull((select sum(outstanding_amount) from `tabPurchase Invoice` where docstatus = 1), 0), 0)
union all select 'Payables', 'MSME dues beyond 45 days (s.43B(h) risk)',
  format(ifnull((select sum(pi.outstanding_amount) from `tabPurchase Invoice` pi
     inner join `tabSupplier` s on s.name = pi.supplier
     where pi.docstatus = 1 and ifnull(s.msme_type,'') != '' and pi.outstanding_amount > 0
       and datediff(curdate(), ifnull(pi.bill_date, pi.posting_date)) > 45), 0), 0)
union all select 'Order book', 'Orders in hand (booked less billed)',
  format(ifnull((select sum(so.grand_total * (100 - ifnull(so.per_billed,0)) / 100)
     from `tabSales Order` so where so.docstatus = 1 and so.status != 'Closed'), 0), 0)
union all select 'Order book', 'Billed this month',
  format(ifnull((select sum(grand_total) from `tabSales Invoice`
     where docstatus = 1 and is_return = 0 and month(posting_date) = month(curdate())
       and year(posting_date) = year(curdate())), 0), 0)
union all select 'Projects', 'Open projects',
  cast((select count(*) from `tabProject` where status = 'Open') as char)
union all select 'Engineering', 'Drawings awaiting customer approval',
  cast((select count(*) from `tabMSCAST Drawing` where status != 'Approved') as char)
union all select 'Quality', 'Inspection stages not yet accepted',
  cast((select count(*) from `tabMSCAST Inspection Plan` where ifnull(result,'') != 'Accepted') as char)
union all select 'Purchase', 'Purchase orders not fully received',
  cast((select count(*) from `tabPurchase Order`
     where docstatus = 1 and ifnull(per_received,0) < 100) as char)
union all select 'Billing control', 'BRMs pending certification',
  cast((select count(*) from `tabMSCAST BRM` where status != 'Certified') as char)
union all select 'Claims', 'Client claims open',
  cast((select count(*) from `tabMSCAST Client Claim`
     where status not in ('Settled','Rejected')) as char)
union all select 'Contracts', 'Certificates / guarantees due in 30 days',
  cast((select count(*) from `tabMSCAST Project Certificate`
     where retention_release_due between curdate() and date_add(curdate(), interval 30 day)) as char)
"""


def daily_summary():
    name = qreport("MSCAST Daily Management Summary", "Project", DAILY_SQL,
                   ("System Manager", "Accounts Manager", "Projects Manager", "MSCAST Director"))
    rows = frappe.db.sql(frappe.db.get_value("Report", name, "query"))
    if not frappe.db.exists("Auto Email Report", "MSCAST Daily Management Summary"):
        ins({"doctype": "Auto Email Report", "report": name, "report_type": "Query Report",
             "user": "Administrator", "enabled": 1, "frequency": "Daily",
             "email_to": "director@mscast.demo\nauditor@mscast.demo",
             "format": "HTML", "day_of_week": "Monday",
             "subject": "MSCAST - daily management summary",
             "description": "One-page daily position: cash, receivables, payables, MSME exposure, "
                            "order book, engineering and quality status."})
    return "%s (%d indicators) + daily auto email" % (name, len(rows))


# ------------------------------------------------------------ AC-19 archival
ARCHIVE_SCRIPT = """
cutoff = frappe.utils.add_years(frappe.utils.nowdate(), -1)
counts = []
total = 0
for dt in ("Sales Invoice", "Purchase Invoice", "Journal Entry", "Stock Ledger Entry"):
    try:
        n = frappe.db.count(dt, {"docstatus": 1})
    except Exception:
        n = 0
    total = total + n
    counts.append(dt + ": " + str(n))
doc = frappe.get_doc({
    "doctype": "MSCAST Archival Log",
    "run_date": frappe.utils.nowdate(),
    "period_covered": "Up to " + cutoff,
    "documents_in_scope": total,
    "archive_location": "Off-site encrypted copy - monthly full backup (database + files)",
    "retention_note": "Books of account and vouchers retained for 8 financial years "
                      "(Companies Act 2013 s.128(5)); audit trail retained for 8 years "
                      "(Companies (Accounts) Rules r.3). India copy of daily backup retained "
                      "as required by r.3(5).",
    "verified": 0,
    "notes": "; ".join(counts),
})
doc.flags.ignore_permissions = True
doc.insert()
"""


def archival():
    doctype("MSCAST Archival Log", [
        f("run_date", "Run Date", "Date", reqd=1, in_list_view=1, default="Today"),
        f("period_covered", "Period Covered", "Data", in_list_view=1),
        f("documents_in_scope", "Documents in Scope", "Int", in_list_view=1),
        f("archive_location", "Archive Location", "Data"),
        f("cb0", "", "Column Break"),
        f("verified", "Restore Verified", "Check", default="0", in_list_view=1),
        f("verified_by", "Verified By", "Link", options="User"),
        f("verified_on", "Verified On", "Date"),
        f("sb0", "Retention", "Section Break"),
        f("retention_note", "Statutory Retention", "Small Text"),
        f("notes", "Notes", "Small Text"),
    ], title_field="period_covered", search_fields="run_date,period_covered")

    made = []
    if not frappe.db.exists("Server Script", "MSCAST monthly archival job"):
        ins({"doctype": "Server Script", "name": "MSCAST monthly archival job",
             "script_type": "Scheduler Event", "event_frequency": "Monthly",
             "disabled": 0, "script": ARCHIVE_SCRIPT,
             "module": "Custom"})
        made.append("scheduled server script (monthly)")
    # run it once so the demo has a log row
    if not frappe.db.count("MSCAST Archival Log"):
        cutoff = frappe.utils.add_years(TODAY, -1)
        counts = []
        total = 0
        for dt in ("Sales Invoice", "Purchase Invoice", "Journal Entry", "Stock Ledger Entry"):
            n = frappe.db.count(dt, {"docstatus": 1}) if frappe.db.exists("DocType", dt) else 0
            total += n
            counts.append("%s: %d" % (dt, n))
        ins({"doctype": "MSCAST Archival Log", "run_date": TODAY,
             "period_covered": "Up to " + cutoff,
             "documents_in_scope": total,
             "archive_location": "Off-site encrypted copy - monthly full backup (database + files)",
             "retention_note": "Books of account and vouchers retained for 8 financial years "
                               "(Companies Act 2013 s.128(5)); audit trail retained for 8 years "
                               "(Companies (Accounts) Rules r.3). Daily backup copy kept on a server "
                               "physically in India as required by r.3(5).",
             "notes": "; ".join(counts)})
        made.append("first archival log")
    try:
        frappe.db.set_value("System Settings", "System Settings", "backup_limit", 12)
        made.append("backup retention set to 12 rolling backups")
    except Exception as e:
        log("  backup limit skipped: " + repr(e)[:120])
    return "; ".join(made) or "(already in place)"


# ------------------------------------------------------------ PC-11 BRM payment block
BRM_BLOCK = """
if doc.payment_type == "Pay" and doc.party_type == "Supplier":
    for ref in (doc.references or []):
        if ref.reference_doctype == "Purchase Invoice":
            bill = frappe.db.get_value("Purchase Invoice", ref.reference_name, "bill_no")
            brm = frappe.db.get_value("MSCAST BRM",
                {"supplier": doc.party, "supplier_invoice_no": bill},
                ["name", "status"], as_dict=True)
            if not brm:
                frappe.throw("Payment blocked: no Billing Routing Memo (BRM) has been raised for "
                             "supplier bill " + str(bill) + " of " + str(doc.party) +
                             ". Raise and certify a BRM before releasing payment.")
            if brm.status != "Certified":
                frappe.throw("Payment blocked: BRM " + brm.name + " for supplier bill " + str(bill) +
                             " is in status '" + str(brm.status) + "'. Only a certified BRM "
                             "(quantity, rate, inspection and delivery checked) can be paid.")
"""


def brm_block():
    made = []
    if not frappe.db.exists("Server Script", "MSCAST BRM payment block"):
        ins({"doctype": "Server Script", "name": "MSCAST BRM payment block",
             "script_type": "DocType Event", "reference_doctype": "Payment Entry",
             "doctype_event": "Before Submit", "disabled": 0, "module": "Custom",
             "script": BRM_BLOCK})
        made.append("server script on Payment Entry (Before Submit)")
    opts = (frappe.get_meta("MSCAST BRM").get_field("status").options or "").split("\n")
    made.append("BRM statuses: " + "/".join([o for o in opts if o]))
    brm = frappe.db.get_value("MSCAST BRM", {}, ["name", "status", "supplier", "supplier_invoice_no"],
                              as_dict=True)
    if brm:
        made.append("sample BRM %s (%s) for %s bill %s" % (brm.name, brm.status, brm.supplier,
                                                           brm.supplier_invoice_no))
    return "; ".join(made)


def run():
    step("client schedule and status prints", project_prints)
    step("daily management summary + auto email", daily_summary)
    step("archival job and retention log", archival)
    step("BRM payment block", brm_block)
    frappe.clear_cache()
    log("BATCH C4 DONE")


run()
