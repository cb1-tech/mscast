"""MSCAST ERPNext POC - 07: letterhead + MSCAST print formats.

Creates a Letter Head and Jinja print formats for PCC, MDF, MDM,
Delivery Instruction (with Annexure-I), BRM, Inspection Plan and Project Certificate.
"""
import frappe

log = lambda m: print("[seed-07] " + m, flush=True)
COMPANY = "MSCAST Engineering Pvt Ltd"

HEADER = """
<div style="border-bottom:2px solid #1f3864;padding-bottom:6px;margin-bottom:10px;">
  <table style="width:100%;border:none;">
    <tr>
      <td style="border:none;vertical-align:middle;">
        <div style="font-size:20px;font-weight:700;color:#1f3864;letter-spacing:0.5px;">MSCAST ENGINEERING PVT. LTD.</div>
        <div style="font-size:10px;color:#444;line-height:1.4;">
          Prithvi Park, Row House No. 7, N.I.B.M Road, Kondhwa, Pune 411 048, Maharashtra, INDIA<br>
          Tel: +91 20 41322865 &nbsp;|&nbsp; sales@mcast.co.in &nbsp;|&nbsp; www.mcast.co.in
        </div>
      </td>
      <td style="border:none;text-align:right;vertical-align:middle;font-size:9px;color:#444;">
        CIN: U74900PN2010PTC137644<br>GSTIN: 27AAGCM8444B1ZI<br>IEC: 3112018541
      </td>
    </tr>
  </table>
</div>
"""

FOOTER = """
<div style="border-top:1px solid #bbb;padding-top:4px;font-size:8px;color:#666;text-align:center;">
  Continuous Casting Machines &middot; Aluminium Billet Casting Machines &middot; Design, Consultancy &amp; Spares
</div>
"""

CSS = """
.print-format { font-family: Arial, Helvetica, sans-serif; font-size: 10.5px; color:#222; }
.ms-title { font-size:15px; font-weight:700; text-align:center; letter-spacing:1px;
            border:1px solid #1f3864; background:#eef2f9; color:#1f3864; padding:5px; margin-bottom:10px; }
table.ms { width:100%; border-collapse:collapse; margin-bottom:10px; }
table.ms th { background:#1f3864; color:#fff; font-weight:600; font-size:10px; padding:4px 5px; border:1px solid #1f3864; text-align:left; }
table.ms td { border:1px solid #c6cbd4; padding:3px 5px; vertical-align:top; }
table.meta { width:100%; border-collapse:collapse; margin-bottom:10px; }
table.meta td { border:1px solid #c6cbd4; padding:3px 6px; font-size:10px; }
table.meta td.k { background:#f2f4f8; font-weight:600; width:18%; }
.num { text-align:right; }
.ms-note { font-size:9.5px; color:#444; margin-top:6px; }
.sign { margin-top:26px; width:100%; }
.sign td { border:none; font-size:10px; padding-top:22px; border-top:1px solid #888; width:33%; text-align:center; }
.badge { display:inline-block; padding:1px 7px; border-radius:9px; font-size:9px; border:1px solid #1f3864; color:#1f3864; }
"""


def letter_head():
    if frappe.db.exists("Letter Head", "MSCAST"):
        lh = frappe.get_doc("Letter Head", "MSCAST")
    else:
        lh = frappe.new_doc("Letter Head")
        lh.letter_head_name = "MSCAST"
    lh.content = HEADER
    lh.footer = FOOTER
    lh.is_default = 1
    lh.disabled = 0
    lh.source = "HTML"
    lh.footer_source = "HTML"
    lh.flags.ignore_permissions = True
    lh.save()
    log("letter head ready")


def pf(name, doctype, html):
    d = frappe.db.exists("Print Format", name)
    doc = frappe.get_doc("Print Format", name) if d else frappe.new_doc("Print Format")
    doc.update({
        "name": name, "doc_type": doctype, "module": "Custom", "standard": "No",
        "custom_format": 1, "print_format_type": "Jinja", "disabled": 0,
        "font_size": 0, "margin_top": 12, "margin_bottom": 12,
        "default_print_language": "en", "letter_head": "MSCAST",
        "css": CSS, "html": html,
    })
    doc.flags.ignore_permissions = True
    doc.save() if d else doc.insert()
    log(("updated " if d else "created ") + name)


# ------------------------------------------------------------------ PCC
PCC_HTML = """
<div class="ms-title">PURCHASE COST CALCULATION (PCC)</div>
<table class="meta">
  <tr><td class="k">PCC No.</td><td>{{ doc.name }}</td>
      <td class="k">Revision</td><td>{{ doc.revision or "" }}</td>
      <td class="k">Status</td><td><span class="badge">{{ doc.status }}</span></td></tr>
  <tr><td class="k">Project</td><td>{{ doc.project or "" }}</td>
      <td class="k">Sales Order</td><td>{{ doc.sales_order or "" }}</td>
      <td class="k">Date</td><td>{{ frappe.utils.formatdate(doc.modified, "dd-MM-yyyy") }}</td></tr>
  <tr><td class="k">Customer</td><td colspan="5">{{ doc.customer or "" }}</td></tr>
</table>

<table class="ms">
  <thead><tr>
    <th style="width:4%">#</th><th style="width:14%">Item</th><th>Description</th>
    <th style="width:12%">Assembly</th><th style="width:11%">Category</th>
    <th style="width:7%" class="num">Qty</th><th style="width:6%">UOM</th>
    <th style="width:11%" class="num">Est. Rate</th><th style="width:12%" class="num">Est. Amount</th>
    <th style="width:8%" class="num">Lead (d)</th>
  </tr></thead>
  <tbody>
  {% for r in doc.items %}
    <tr>
      <td>{{ loop.index }}</td>
      <td>{{ r.item_code or "" }}</td>
      <td>{{ r.description or "" }}{% if r.approved_make %}<br><span style="font-size:9px;color:#666">Make: {{ r.approved_make }}</span>{% endif %}</td>
      <td>{{ r.assembly or "" }}</td>
      <td>{{ r.category or "" }}</td>
      <td class="num">{{ "{:,.2f}".format(r.qty or 0) }}</td>
      <td>{{ r.uom or "" }}</td>
      <td class="num">{{ frappe.utils.fmt_money(r.est_rate or 0, currency="INR") }}</td>
      <td class="num">{{ frappe.utils.fmt_money(r.est_amount or 0, currency="INR") }}</td>
      <td class="num">{{ r.lead_time_days or "" }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>

<table class="meta">
  <tr><td class="k">Total Estimated Cost</td><td class="num">{{ frappe.utils.fmt_money(doc.total_estimated_cost or 0, currency="INR") }}</td>
      <td class="k">Contract Value</td><td class="num">{{ frappe.utils.fmt_money(doc.contract_value or 0, currency="INR") }}</td>
      <td class="k">Target Margin</td><td class="num">{{ doc.target_margin_pct or 0 }} %</td></tr>
</table>

{% if doc.remarks %}<div class="ms-note"><b>Remarks:</b> {{ doc.remarks }}</div>{% endif %}

<table class="sign">
  <tr><td>Prepared by<br>{{ doc.prepared_by or "" }}</td>
      <td>Checked by (Projects)</td>
      <td>Approved by<br>{{ doc.approved_by or "" }}</td></tr>
</table>
"""

# ------------------------------------------------------------------ MDF
MDF_HTML = """
<div class="ms-title">MATERIAL DATA FILE (MDF)</div>
<table class="meta">
  <tr><td class="k">MDF No.</td><td>{{ doc.name }}</td>
      <td class="k">Assembly</td><td>{{ doc.assembly or "" }}</td>
      <td class="k">Status</td><td><span class="badge">{{ doc.status }}</span></td></tr>
  <tr><td class="k">Project</td><td>{{ doc.project or "" }}</td>
      <td class="k">Drawing</td><td>{{ frappe.db.get_value("MSCAST Drawing", doc.drawing, "drawing_no") or doc.drawing or "" }}</td>
      <td class="k">Released on</td><td>{{ frappe.utils.formatdate(doc.released_on, "dd-MM-yyyy") if doc.released_on else "-" }}</td></tr>
</table>

<table class="ms">
  <thead><tr>
    <th style="width:4%">#</th><th style="width:15%">Item</th><th>Description</th>
    <th style="width:15%">Drawing No.</th><th style="width:14%">Material Spec</th>
    <th style="width:8%" class="num">Qty</th><th style="width:6%">UOM</th>
    <th style="width:9%" class="num">Wt (kg)</th><th style="width:11%">Category</th>
  </tr></thead>
  <tbody>
  {% for r in doc.items %}
    <tr>
      <td>{{ loop.index }}</td><td>{{ r.item_code or "" }}</td><td>{{ r.description or "" }}</td>
      <td>{{ r.drawing_no or "" }}</td><td>{{ r.material_spec or "" }}</td>
      <td class="num">{{ "{:,.2f}".format(r.qty or 0) }}</td><td>{{ r.uom or "" }}</td>
      <td class="num">{{ "{:,.1f}".format(r.weight_kg or 0) }}</td><td>{{ r.category or "" }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>

{% if doc.remarks %}<div class="ms-note"><b>Remarks:</b> {{ doc.remarks }}</div>{% endif %}
<table class="sign">
  <tr><td>Prepared by (Engineering)<br>{{ doc.prepared_by or "" }}</td>
      <td>Released to Procurement</td>
      <td>Received by (Procurement)</td></tr>
</table>
"""

# ------------------------------------------------------------------ MDM
MDM_HTML = """
<div class="ms-title">MATERIAL DISPATCH MEMO (MDM)</div>
<table class="meta">
  <tr><td class="k">MDM No.</td><td>{{ doc.name }}</td>
      <td class="k">Dispatch Lot</td><td>{{ doc.lot_no or "" }}</td>
      <td class="k">Status</td><td><span class="badge">{{ doc.status }}</span></td></tr>
  <tr><td class="k">Project</td><td>{{ doc.project or "" }}</td>
      <td class="k">Supplier</td><td>{{ doc.supplier or "" }}</td>
      <td class="k">Scheduled</td><td>{{ frappe.utils.formatdate(doc.scheduled_date, "dd-MM-yyyy") if doc.scheduled_date else "-" }}</td></tr>
  <tr><td class="k">Purchase Order</td><td colspan="5">{{ doc.purchase_order or "" }}</td></tr>
</table>

<table class="ms">
  <thead><tr>
    <th style="width:5%">#</th><th style="width:18%">Item</th><th>Description</th>
    <th style="width:10%" class="num">Qty</th><th style="width:8%">UOM</th>
    <th style="width:12%">Free Issue</th><th style="width:18%">Remarks</th>
  </tr></thead>
  <tbody>
  {% for r in doc.items %}
    <tr>
      <td>{{ loop.index }}</td><td>{{ r.item_code or "" }}</td><td>{{ r.description or "" }}</td>
      <td class="num">{{ "{:,.2f}".format(r.qty or 0) }}</td><td>{{ r.uom or "" }}</td>
      <td>{{ "YES (Annexure-I)" if r.is_free_issue else "-" }}</td><td>{{ r.remarks or "" }}</td>
    </tr>
  {% endfor %}
  </tbody>
</table>

{% if doc.remarks %}<div class="ms-note"><b>Remarks:</b> {{ doc.remarks }}</div>{% endif %}
<div class="ms-note">Material to be dispatched only after clearance of pre-dispatch inspection and issue of Delivery Instruction.</div>
<table class="sign">
  <tr><td>Prepared by (Procurement)</td><td>Checked by (Projects)</td><td>Approved by</td></tr>
</table>
"""

# ------------------------------------------------- Delivery Instruction
DI_HTML = """
<div class="ms-title">DELIVERY INSTRUCTION</div>
<table class="meta">
  <tr><td class="k">DI No.</td><td>{{ doc.name }}</td>
      <td class="k">Date</td><td>{{ frappe.utils.formatdate(doc.dispatch_date, "dd-MM-yyyy") if doc.dispatch_date else "-" }}</td>
      <td class="k">Status</td><td><span class="badge">{{ doc.status }}</span></td></tr>
  <tr><td class="k">To (Supplier)</td><td>{{ doc.supplier or "" }}</td>
      <td class="k">MDM Ref.</td><td>{{ doc.mdm or "" }}</td>
      <td class="k">Project</td><td>{{ doc.project or "" }}</td></tr>
  <tr><td class="k">Consignee</td><td colspan="5">{{ doc.consignee or "" }}</td></tr>
  <tr><td class="k">Transporter</td><td>{{ doc.transporter or "" }}</td>
      <td class="k">Vehicle</td><td>{{ doc.vehicle_type or "" }}</td>
      <td class="k">LR No.</td><td>{{ doc.lr_no or "" }}</td></tr>
</table>

<div style="font-weight:600;margin:8px 0 4px;">Material to be dispatched</div>
<table class="ms">
  <thead><tr><th style="width:5%">#</th><th style="width:20%">Item</th><th>Description</th>
    <th style="width:10%" class="num">Qty</th><th style="width:8%">UOM</th><th style="width:12%">Free Issue</th></tr></thead>
  <tbody>
  {% set rows = frappe.get_all("MSCAST MDM Item", filters={"parent": doc.mdm},
        fields=["item_code","description","qty","uom","is_free_issue"], order_by="idx") %}
  {% for r in rows %}
    <tr><td>{{ loop.index }}</td><td>{{ r.item_code or "" }}</td><td>{{ r.description or "" }}</td>
        <td class="num">{{ "{:,.2f}".format(r.qty or 0) }}</td><td>{{ r.uom or "" }}</td>
        <td>{{ "YES" if r.is_free_issue else "-" }}</td></tr>
  {% endfor %}
  {% if not rows %}<tr><td colspan="6" style="text-align:center;color:#888">No MDM linked</td></tr>{% endif %}
  </tbody>
</table>

{% if doc.instructions %}
<div style="font-weight:600;margin:8px 0 4px;">Instructions</div>
<div style="border:1px solid #c6cbd4;padding:6px;">{{ doc.instructions }}</div>
{% endif %}

{% if doc.free_issue_annexure %}
<div style="font-weight:600;margin:10px 0 4px;">ANNEXURE-I &mdash; Free Issue Material</div>
<div style="border:1px solid #c6cbd4;padding:6px;">{{ doc.free_issue_annexure }}</div>
{% endif %}

<div class="ms-note">
  1. Dispatch documents: invoice, packing list, test certificates and e-way bill to accompany the consignment.<br>
  2. Intimate dispatch details (LR no., vehicle no., date) to MSCAST Projects on the day of dispatch.<br>
  3. Any deviation from this instruction requires written approval from MSCAST.
</div>

<table class="sign">
  <tr><td>Issued by (Procurement)</td><td>Approved by (Projects)</td><td>Acknowledged by Supplier</td></tr>
</table>
"""

# ------------------------------------------------------------------ BRM
BRM_HTML = """
<div class="ms-title">BILLING ROUTING MEMO (BRM)</div>
<table class="meta">
  <tr><td class="k">BRM No.</td><td>{{ doc.name }}</td>
      <td class="k">Status</td><td><span class="badge">{{ doc.status }}</span></td>
      <td class="k">Invoice Type</td><td>{{ doc.invoice_type or "" }}</td></tr>
  <tr><td class="k">Supplier</td><td>{{ doc.supplier or "" }}</td>
      <td class="k">Purchase Order</td><td>{{ doc.purchase_order or "" }}</td>
      <td class="k">Project</td><td>{{ doc.project or "" }}</td></tr>
  <tr><td class="k">Supplier Invoice</td><td>{{ doc.supplier_invoice_no or "" }}</td>
      <td class="k">Invoice Date</td><td>{{ frappe.utils.formatdate(doc.supplier_invoice_date, "dd-MM-yyyy") if doc.supplier_invoice_date else "-" }}</td>
      <td class="k">Amount</td><td class="num">{{ frappe.utils.fmt_money(doc.amount or 0, currency="INR") }}</td></tr>
</table>

<div style="font-weight:600;margin:8px 0 4px;">Certification by Procurement</div>
<table class="ms">
  <thead><tr><th style="width:70%">Check</th><th style="width:30%">Status</th></tr></thead>
  <tbody>
    <tr><td>Quantity as per Purchase Order</td><td>{{ "Verified" if doc.qty_check else "Not verified" }}</td></tr>
    <tr><td>Rate and commercial terms as per Purchase Order</td><td>{{ "Verified" if doc.rate_check else "Not verified" }}</td></tr>
    <tr><td>Inspection cleared</td><td>{{ "Cleared" if doc.inspection_check else "Pending" }}</td></tr>
    <tr><td>Material delivered as per Delivery Instruction</td><td>{{ "Confirmed" if doc.delivery_check else "Pending" }}</td></tr>
  </tbody>
</table>

{% if doc.remarks %}<div class="ms-note"><b>Remarks:</b> {{ doc.remarks }}</div>{% endif %}
<div class="ms-note">Payment to be released by Accounts only against a certified BRM.</div>

<table class="sign">
  <tr><td>Certified by<br>{{ doc.certified_by or "" }}{% if doc.certification_date %}<br>{{ frappe.utils.formatdate(doc.certification_date, "dd-MM-yyyy") }}{% endif %}</td>
      <td>Projects</td><td>Accounts / Director</td></tr>
</table>
"""

# ------------------------------------------------------ Inspection Plan
INSP_HTML = """
<div class="ms-title">INSPECTION CALL / REPORT</div>
<table class="meta">
  <tr><td class="k">Ref. No.</td><td>{{ doc.name }}</td>
      <td class="k">Stage</td><td>{{ doc.stage or "" }}</td>
      <td class="k">Result</td><td><span class="badge">{{ doc.result }}</span></td></tr>
  <tr><td class="k">Project</td><td>{{ doc.project or "" }}</td>
      <td class="k">Supplier</td><td>{{ doc.supplier or "" }}</td>
      <td class="k">Purchase Order</td><td>{{ doc.purchase_order or "" }}</td></tr>
  <tr><td class="k">Item / Assembly</td><td>{{ doc.item_or_assembly or "" }}</td>
      <td class="k">Planned</td><td>{{ frappe.utils.formatdate(doc.planned_date, "dd-MM-yyyy") if doc.planned_date else "-" }}</td>
      <td class="k">Actual</td><td>{{ frappe.utils.formatdate(doc.actual_date, "dd-MM-yyyy") if doc.actual_date else "-" }}</td></tr>
  <tr><td class="k">Inspector</td><td colspan="5">{{ doc.inspector or "" }}</td></tr>
</table>
<div style="font-weight:600;margin:8px 0 4px;">Observations</div>
<div style="border:1px solid #c6cbd4;padding:6px;min-height:60px;">{{ doc.observations or "" }}</div>
<table class="sign">
  <tr><td>MSCAST QC</td><td>Supplier Representative</td><td>Customer / TPI</td></tr>
</table>
"""

# --------------------------------------------------- Project Certificate
CERT_HTML = """
<div class="ms-title">{{ (doc.certificate_type or "PROJECT") | upper }} CERTIFICATE</div>
<table class="meta">
  <tr><td class="k">Certificate No.</td><td>{{ doc.name }}</td>
      <td class="k">Type</td><td>{{ doc.certificate_type or "" }}</td>
      <td class="k">Status</td><td><span class="badge">{{ doc.status }}</span></td></tr>
  <tr><td class="k">Project</td><td>{{ doc.project or "" }}</td>
      <td class="k">Customer</td><td>{{ doc.customer or "" }}</td>
      <td class="k">Issue Date</td><td>{{ frappe.utils.formatdate(doc.issue_date, "dd-MM-yyyy") if doc.issue_date else "-" }}</td></tr>
  <tr><td class="k">Customer Ref.</td><td>{{ doc.reference or "" }}</td>
      <td class="k">Retention Release Due</td><td colspan="3">{{ frappe.utils.formatdate(doc.retention_release_due, "dd-MM-yyyy") if doc.retention_release_due else "-" }}</td></tr>
</table>
<div style="border:1px solid #c6cbd4;padding:8px;min-height:70px;">{{ doc.notes or "" }}</div>
<table class="sign">
  <tr><td>For MSCAST Engineering Pvt. Ltd.</td><td>Site In-charge</td><td>For {{ doc.customer or "Customer" }}</td></tr>
</table>
"""


def run():
    letter_head()
    pf("MSCAST PCC Sheet", "MSCAST PCC", PCC_HTML)
    pf("MSCAST MDF Sheet", "MSCAST MDF", MDF_HTML)
    pf("MSCAST Material Dispatch Memo", "MSCAST MDM", MDM_HTML)
    pf("MSCAST Delivery Instruction Print", "MSCAST Delivery Instruction", DI_HTML)
    pf("MSCAST Billing Routing Memo", "MSCAST BRM", BRM_HTML)
    pf("MSCAST Inspection Report", "MSCAST Inspection Plan", INSP_HTML)
    pf("MSCAST Project Certificate Print", "MSCAST Project Certificate", CERT_HTML)

    # make them the default format for each doctype
    for dt, name in [
        ("MSCAST PCC", "MSCAST PCC Sheet"),
        ("MSCAST MDF", "MSCAST MDF Sheet"),
        ("MSCAST MDM", "MSCAST Material Dispatch Memo"),
        ("MSCAST Delivery Instruction", "MSCAST Delivery Instruction Print"),
        ("MSCAST BRM", "MSCAST Billing Routing Memo"),
        ("MSCAST Inspection Plan", "MSCAST Inspection Report"),
        ("MSCAST Project Certificate", "MSCAST Project Certificate Print"),
    ]:
        frappe.db.set_value("DocType", dt, "default_print_format", name)

    frappe.db.commit()
    frappe.clear_cache()
    log("DONE")


run()
