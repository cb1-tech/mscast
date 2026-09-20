"""MSCAST POC - 57: BATCH C4 fix - project status print (dict aggregate syntax), BRM certified sample."""
import frappe

log = lambda m: print("[C4b] " + m, flush=True)

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
{% set billed = frappe.db.get_value("Sales Invoice", {"project": doc.name, "docstatus": 1, "is_return": 0}, {"SUM": "grand_total"}) or 0 %}
{% set outst = frappe.db.get_value("Sales Invoice", {"project": doc.name, "docstatus": 1, "is_return": 0}, {"SUM": "outstanding_amount"}) or 0 %}
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
      <td class="num">{{ frappe.utils.fmt_money(frappe.db.get_value("Purchase Invoice Item", {"project": doc.name, "docstatus": 1}, {"SUM": "amount"}) or 0) }}</td>
      <td>Dispatch memos raised</td>
      <td>{{ frappe.get_all("MSCAST MDM", filters={"project": doc.name}) | length }}</td></tr>
    <tr><td>Open client claims</td>
      <td class="num">{{ frappe.utils.fmt_money(frappe.db.get_value("MSCAST Client Claim", {"project": doc.name, "status": ["not in", ["Settled","Rejected"]]}, {"SUM": "claim_amount"}) or 0) }}</td>
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


def pf(name, doctype_name, html):
    exists = frappe.db.exists("Print Format", name)
    doc = frappe.get_doc("Print Format", name) if exists else frappe.new_doc("Print Format")
    doc.update({"name": name, "doc_type": doctype_name, "module": "Custom", "standard": "No",
                "custom_format": 1, "print_format_type": "Jinja", "disabled": 0,
                "margin_top": 12, "margin_bottom": 12, "letter_head": "MSCAST",
                "css": CSS, "html": html})
    doc.flags.ignore_permissions = True
    doc.save() if exists else doc.insert()


pf("MSCAST Project Status Report", "Project", STATUS_HTML)
frappe.db.commit()
frappe.clear_cache()
for p in frappe.get_all("Project", pluck="name"):
    try:
        h = frappe.get_print("Project", p, print_format="MSCAST Project Status Report")
        log("status report %s rendered (%d chars)" % (p, len(h)))
    except Exception as e:
        log("status report %s RENDER ERROR %s" % (p, repr(e)[:260]))

brm = frappe.db.get_value("MSCAST BRM", {"status": "Pending"}, "name")
if brm:
    frappe.db.set_value("MSCAST BRM", brm, {"status": "Certified",
                                            "qty_check": 1, "rate_check": 1,
                                            "inspection_check": 1, "delivery_check": 1,
                                            "certification_date": frappe.utils.nowdate()})
    frappe.db.commit()
    log("certified %s so one supplier bill is payable; the other stays pending to demo the block" % brm)
for b in frappe.get_all("MSCAST BRM", fields=["name", "supplier", "supplier_invoice_no", "status", "amount"]):
    log("  %s | %s | %s | %s | %s" % (b.name, b.supplier, b.supplier_invoice_no, b.status, b.amount))
log("DONE")
