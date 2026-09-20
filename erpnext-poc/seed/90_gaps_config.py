"""MSCAST POC - 90: PC-02 billing & dispatch schedule, A-09 receipt print, AC-05 chat webhook.

Mock data is grounded in the MSCAST knowledge base: payment milestones 30/60/10, HSN 8454/8412,
GSTIN 27AAGCM8444B1ZI, IEC 3112018541, HDFC banker.
"""
import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.utils import add_days, flt, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
log = lambda m: print("[90] " + m, flush=True)

CSS = """
.print-format { font-family: Arial, Helvetica, sans-serif; font-size: 10.5px; color:#222; }
.ms-title { font-size:15px; font-weight:700; text-align:center; letter-spacing:1px;
            border:1px solid #1f3864; background:#eef2f9; color:#1f3864; padding:5px; margin-bottom:10px; }
table.ms { width:100%; border-collapse:collapse; margin-bottom:10px; }
table.ms th { background:#1f3864; color:#fff; font-size:10px; padding:4px 5px; border:1px solid #1f3864; text-align:left; }
table.ms td { border:1px solid #c6cbd4; padding:3px 5px; vertical-align:top; }
table.meta { width:100%; border-collapse:collapse; margin-bottom:10px; }
table.meta td { border:1px solid #c6cbd4; padding:3px 6px; font-size:10px; }
table.meta td.k { background:#f2f4f8; font-weight:600; width:20%; }
.num { text-align:right; }
.ms-note { font-size:9.5px; color:#444; margin-top:6px; }
.sign { margin-top:26px; width:100%; }
.sign td { border:none; font-size:10px; padding-top:22px; border-top:1px solid #888; width:33%; text-align:center; }
.big { font-size:13px; font-weight:700; }
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


P1 = lambda: frappe.db.get_value("Project", {"project_name": ("like", "CCM 2-Strand%")}, "name")
P2 = lambda: frappe.db.get_value("Project", {"project_name": ("like", "Aluminium Billet%")}, "name")


# ------------------------------------------------------------------ PC-02
def billing_schedule():
    doctype("MSCAST Project Schedule Line", [
        f("milestone", "Milestone", "Data", reqd=1, in_list_view=1, columns=3),
        f("scope", "Scope / assembly", "Data", in_list_view=1, columns=2),
        f("planned_dispatch_date", "Planned Dispatch", "Date", in_list_view=1, columns=1),
        f("billing_percent", "Billing %", "Percent", in_list_view=1, columns=1),
        f("billing_amount", "Billing Value", "Currency", in_list_view=1, columns=2),
        f("status", "Status", "Select",
          options="Planned\nMaterial ordered\nReady for dispatch\nDispatched\nBilled\nCollected",
          default="Planned", in_list_view=1, columns=1),
        f("sales_invoice", "Invoice", "Link", options="Sales Invoice"),
        f("procurement_note", "Note for procurement", "Small Text"),
    ], istable=1)

    create_custom_fields({"Project": [
        {"fieldname": "mscast_schedule_sb", "label": "Billing and Dispatch Schedule",
         "fieldtype": "Section Break", "insert_after": "notes", "collapsible": 1},
        {"fieldname": "mscast_schedule", "label": "Billing / Dispatch Schedule", "fieldtype": "Table",
         "options": "MSCAST Project Schedule Line", "insert_after": "mscast_schedule_sb",
         "description": "Milestone-wise dispatch and billing plan derived from the PCC and the "
                        "customer PO payment terms. Visible to procurement."},
    ]}, ignore_validate=True)

    rows1 = [
        ("M1 - Advance against PBG", "Order booking", -78, 30, 6079500, "Collected",
         "Release long-lead bought-outs: copper mould tubes, hydraulic power pack."),
        ("M2 - Design and drawing approval", "Engineering", -60, 10, 2026500, "Billed",
         "Drawings frozen; MDF released to procurement."),
        ("M3 - Dispatch of WSU and mould assembly", "Withdrawal + mould", -20, 30, 6079500,
         "Dispatched", "Fabrication with Pushkar; free-issue plate already at vendor."),
        ("M4 - Dispatch of balance scope", "Spray chamber, run-out, hydraulics", 25, 20, 4053000,
         "Ready for dispatch", "Pending third-party inspection on the hydraulic power pack."),
        ("M5 - Commissioning and acceptance", "Site", 45, 10, 2026500, "Planned",
         "Retention 10 percent releases against the performance certificate."),
    ]
    rows2 = [
        ("M1 - Advance", "Order booking", -26, 20, 2840000, "Collected", "Awaiting payment-terms deviation closure."),
        ("M2 - Design approval", "Engineering", 10, 15, 2130000, "Planned", "Design release blocked on the PO query."),
        ("M3 - Dispatch of caster", "Billet caster 7 inch", 90, 50, 7100000, "Planned",
         "Die inserts and thermocouples to be ordered 60 days ahead."),
        ("M4 - Commissioning", "Site", 120, 15, 2130000, "Planned", "Mandatory spares handed over separately."),
    ]
    made = []
    for proj, rows in ((P1(), rows1), (P2(), rows2)):
        if not proj:
            continue
        d = frappe.get_doc("Project", proj)
        if d.get("mscast_schedule"):
            made.append("%s already has a schedule" % proj)
            continue
        for m, sc, off, pct, amt, st, note in rows:
            d.append("mscast_schedule", {
                "milestone": m, "scope": sc, "planned_dispatch_date": add_days(TODAY, off),
                "billing_percent": pct, "billing_amount": amt, "status": st,
                "procurement_note": note})
        d.flags.ignore_permissions = True
        d.flags.ignore_mandatory = True
        d.save()
        made.append("%s: %d milestones" % (proj, len(rows)))

    qreport("MSCAST Billing and Dispatch Schedule", "Project", """
select
  s.parent                                        as "Project:Link/Project:110",
  p.project_name                                  as "Description::230",
  s.milestone                                     as "Milestone::260",
  s.scope                                         as "Scope::200",
  s.planned_dispatch_date                         as "Planned Dispatch:Date:110",
  s.billing_percent                               as "Bill %:Percent:70",
  s.billing_amount                                as "Billing Value:Currency:130",
  s.status                                        as "Status::130",
  datediff(s.planned_dispatch_date,
           date(convert_tz(utc_timestamp(),'+00:00','+05:30')))
                                                  as "Days to go:Int:90",
  s.procurement_note                              as "Action for procurement::340"
from `tabMSCAST Project Schedule Line` s
inner join `tabProject` p on p.name = s.parent
order by s.planned_dispatch_date
""", ("System Manager", "Accounts Manager", "Projects Manager", "Purchase Manager",
      "Purchase User", "MSCAST Director"), total=True)
    return "; ".join(made) + " + procurement report"


# ------------------------------------------------------------------ A-09
RECEIPT_HTML = """
<div class="ms-title">RECEIPT</div>
<table class="meta">
  <tr><td class="k">Receipt No.</td><td>{{ doc.name }}</td>
      <td class="k">Date</td><td>{{ frappe.utils.formatdate(doc.posting_date, "dd-MM-yyyy") }}</td></tr>
  <tr><td class="k">Received from</td><td colspan="3"><b>{{ doc.party_name or doc.party }}</b></td></tr>
  <tr><td class="k">Amount</td><td colspan="3" class="big">
      {{ frappe.utils.fmt_money(doc.paid_amount, currency=doc.paid_from_account_currency) }}
      ({{ frappe.utils.money_in_words(doc.paid_amount, doc.paid_from_account_currency) }})</td></tr>
  <tr><td class="k">Received by</td><td>{{ doc.paid_to }}</td>
      <td class="k">Mode / Ref.</td>
      <td>{{ doc.mode_of_payment or "-" }} {{ doc.reference_no or "" }}
          {% if doc.reference_date %} dated {{ frappe.utils.formatdate(doc.reference_date, "dd-MM-yyyy") }}{% endif %}</td></tr>
</table>
{% if doc.references %}
<table class="ms">
  <thead><tr><th style="width:6%">#</th><th>Against</th><th style="width:18%" class="num">Document Total</th>
    <th style="width:18%" class="num">Allocated</th></tr></thead>
  <tbody>
  {% for r in doc.references %}
    <tr><td>{{ loop.index }}</td><td>{{ r.reference_doctype }} {{ r.reference_name }}</td>
      <td class="num">{{ frappe.utils.fmt_money(r.total_amount) }}</td>
      <td class="num">{{ frappe.utils.fmt_money(r.allocated_amount) }}</td></tr>
  {% endfor %}
  </tbody>
</table>
{% endif %}
{% if doc.remarks %}<div class="ms-note">{{ doc.remarks }}</div>{% endif %}
<div class="ms-note">Subject to realisation of the instrument. This receipt is computer generated
from the MSCAST ERP system.</div>
<table class="sign"><tr><td>Prepared by</td><td>Accounts</td>
  <td>For MSCAST Engineering Pvt Ltd</td></tr></table>
"""


def receipt_print():
    pf("MSCAST Payment Receipt", "Payment Entry", RECEIPT_HTML)
    pe = frappe.db.get_value("Payment Entry", {"payment_type": "Receive", "docstatus": 1}, "name")
    if not pe:
        return "print format created; no receive payment to render"
    html = frappe.get_print("Payment Entry", pe, print_format="MSCAST Payment Receipt")
    return "print format + rendered %s (%d chars)" % (pe, len(html))


# ------------------------------------------------------------------ AC-05
CHAT_CARD = """{
  "text": "*MSCAST ERP* - {{ doc.doctype }} *{{ doc.name }}* submitted\\n{{ doc.company }}\\nValue: Rs {{ doc.get('grand_total') or doc.get('paid_amount') or 0 }}\\nParty: {{ doc.get('customer') or doc.get('supplier') or doc.get('party') or '-' }}\\n{{ frappe.utils.get_url() }}/app/{{ doc.doctype | lower | replace(' ', '-') }}/{{ doc.name }}"
}"""


def chat_webhooks():
    meta = frappe.get_meta("Webhook")
    have = {fl.fieldname for fl in meta.fields if fl.fieldname}
    log("  webhook fields: %s" % sorted(have & {"request_structure", "webhook_json", "condition",
                                                "enabled", "request_url", "webhook_docevent",
                                                "webhook_doctype", "request_method"}))
    made = []
    PLACEHOLDER = "https://chat.googleapis.com/v1/spaces/REPLACE_SPACE/messages?key=REPLACE&token=REPLACE"
    for dt, event, cond in [
            ("Sales Invoice", "on_submit", "doc.grand_total > 500000"),
            ("Purchase Order", "on_submit", "doc.grand_total > 500000"),
            ("Payment Entry", "on_submit", "doc.paid_amount > 500000")]:
        if frappe.db.exists("Webhook", {"webhook_doctype": dt, "webhook_docevent": event}):
            continue
        d = {"doctype": "Webhook", "webhook_doctype": dt, "webhook_docevent": event,
             "request_url": PLACEHOLDER, "request_method": "POST", "condition": cond,
             "enabled": 0}
        if "request_structure" in have:
            d["request_structure"] = "JSON"
        if "webhook_json" in have:
            d["webhook_json"] = CHAT_CARD
        ins(d)
        made.append("%s %s" % (dt, event))
    return ("%s (disabled - paste the Google Chat space webhook URL and enable)" % ", ".join(made)
            if made else "webhooks already exist")


def run():
    step("PC-02 billing and dispatch schedule on the project", billing_schedule)
    step("A-09 payment receipt print", receipt_print)
    step("AC-05 Google Chat webhooks for major-value transactions", chat_webhooks)
    frappe.clear_cache()
    log("SCRIPT 90 DONE")


run()
