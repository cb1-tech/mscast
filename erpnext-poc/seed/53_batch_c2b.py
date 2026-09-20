"""MSCAST POC - 53: BATCH C part 2 - transmittal register, commissioning report,
spares handover, kick-off / customer-PO-check workflow."""
import frappe
from frappe.utils import add_days, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
log = lambda m: print("[C2b] " + m, flush=True)

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
"""

PERMS = [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1,
     "export": 1, "share": 1, "print": 1, "email": 1},
    {"role": "Projects Manager", "read": 1, "write": 1, "create": 1, "report": 1, "print": 1,
     "email": 1},
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


P1 = lambda: frappe.db.get_value("Project", {"project_name": ("like", "CCM 2-Strand%")}, "name")
P2 = lambda: frappe.db.get_value("Project", {"project_name": ("like", "Aluminium Billet%")}, "name")


# ------------------------------------------------------------ PC-12 transmittal
TRANSMITTAL_HTML = """
<div class="ms-title">DOCUMENT / DRAWING TRANSMITTAL NOTE</div>
<table class="meta">
  <tr><td class="k">Transmittal No.</td><td>{{ doc.name }}</td>
      <td class="k">Date</td><td>{{ frappe.utils.formatdate(doc.transmittal_date, "dd-MM-yyyy") }}</td></tr>
  <tr><td class="k">Project</td><td>{{ doc.project or "-" }}</td>
      <td class="k">Issued To</td><td>{{ doc.customer or doc.supplier or "-" }}</td></tr>
  <tr><td class="k">Attention</td><td>{{ doc.attention or "-" }}</td>
      <td class="k">Mode</td><td>{{ doc.mode_of_transmission or "-" }}</td></tr>
  <tr><td class="k">Purpose</td><td colspan="3"><span class="badge">{{ doc.purpose }}</span></td></tr>
</table>
<table class="ms">
  <thead><tr><th style="width:5%">#</th><th style="width:20%">Drawing / Doc No.</th>
    <th>Title</th><th style="width:9%">Rev.</th><th style="width:8%" class="num">Sheets</th>
    <th style="width:10%" class="num">Copies</th></tr></thead>
  <tbody>
  {% for r in doc.items %}
    <tr><td>{{ loop.index }}</td><td>{{ r.document_no }}</td><td>{{ r.title }}</td>
      <td>{{ r.revision }}</td><td class="num">{{ r.sheets or 1 }}</td>
      <td class="num">{{ r.copies or 1 }}</td></tr>
  {% endfor %}
  </tbody>
</table>
{% if doc.remarks %}<div class="ms-note"><b>Remarks:</b> {{ doc.remarks }}</div>{% endif %}
<div class="ms-note">Please acknowledge receipt by signing and returning one copy of this transmittal.
Documents are issued for the stated purpose only and remain the property of MSCAST Engineering Pvt Ltd.</div>
<table class="sign"><tr><td>Issued by (MSCAST)</td><td>Checked by</td><td>Received by / Date</td></tr></table>
"""


def transmittal():
    doctype("MSCAST Transmittal Item", [
        f("document_no", "Drawing / Document No.", "Data", reqd=1, in_list_view=1, columns=2),
        f("title", "Title", "Data", in_list_view=1, columns=4),
        f("revision", "Rev.", "Data", in_list_view=1, columns=1),
        f("sheets", "Sheets", "Int", in_list_view=1, columns=1, default="1"),
        f("copies", "Copies", "Int", in_list_view=1, columns=1, default="1"),
        f("drawing", "Drawing", "Link", options="MSCAST Drawing"),
    ], istable=1)
    created = doctype("MSCAST Transmittal", [
        f("naming_series", "Series", "Select", options="TRN-.YYYY.-", default="TRN-.YYYY.-", reqd=1),
        f("transmittal_date", "Date", "Date", reqd=1, default="Today", in_list_view=1),
        f("project", "Project", "Link", options="Project", in_standard_filter=1, in_list_view=1),
        f("issued_to", "Issued To", "Select", options="Customer\nSupplier\nInspection Agency",
          default="Customer", reqd=1, in_standard_filter=1),
        f("customer", "Customer", "Link", options="Customer", depends_on="eval:doc.issued_to=='Customer'",
          in_list_view=1),
        f("supplier", "Supplier", "Link", options="Supplier",
          depends_on="eval:doc.issued_to!='Customer'"),
        f("attention", "Kind Attention", "Data"),
        f("cb0", "", "Column Break"),
        f("purpose", "Purpose", "Select",
          options="For approval\nFor construction / manufacture\nFor information\nAs-built / final records\nFor quotation",
          default="For approval", reqd=1, in_standard_filter=1),
        f("mode_of_transmission", "Mode", "Select", options="Email\nCourier\nBy hand\nCloud link",
          default="Email"),
        f("reference", "Their Reference", "Data"),
        f("ack_received", "Acknowledgement Received", "Check", default="0", in_list_view=1),
        f("ack_date", "Acknowledged On", "Date", depends_on="ack_received"),
        f("sb0", "Documents Transmitted", "Section Break"),
        f("items", "Documents", "Table", options="MSCAST Transmittal Item", reqd=1),
        f("sb1", "Remarks", "Section Break"),
        f("remarks", "Remarks", "Small Text"),
    ], title_field="project", search_fields="project,customer,purpose")

    if not frappe.db.count("MSCAST Transmittal"):
        drg = frappe.get_all("MSCAST Drawing", filters={"project": P1()},
                             fields=["name", "drawing_no", "title", "current_revision"], limit=4)
        ins({"doctype": "MSCAST Transmittal", "transmittal_date": add_days(TODAY, -34),
             "project": P1(), "issued_to": "Customer", "customer": "Sahyadri Steels Ltd (DEMO)",
             "attention": "Mr. R. Kulkarni - Projects", "purpose": "For approval",
             "mode_of_transmission": "Email", "reference": "SSL/CCM/2026/ENG-07",
             "ack_received": 1, "ack_date": add_days(TODAY, -31),
             "items": [{"document_no": d.drawing_no, "title": d.title, "revision": d.current_revision,
                        "sheets": 1, "copies": 1, "drawing": d.name} for d in drg] or
                      [{"document_no": "MS-CCM-GA-001", "title": "General arrangement", "revision": "R1"}],
             "remarks": "General arrangement and layout set issued for customer approval. "
                        "Approval requested within 7 days to protect the delivery schedule."})
        ins({"doctype": "MSCAST Transmittal", "transmittal_date": add_days(TODAY, -12),
             "project": P1(), "issued_to": "Supplier", "supplier": "Pushkar Fabricators (DEMO)",
             "attention": "Works Manager", "purpose": "For construction / manufacture",
             "mode_of_transmission": "Cloud link", "reference": "PF/WO/2026/118",
             "items": [{"document_no": "MS-CCM-FAB-221", "title": "Spray chamber weldment", "revision": "R2",
                        "sheets": 3, "copies": 1},
                       {"document_no": "MS-CCM-FAB-222", "title": "Spray chamber - nozzle bracket detail",
                        "revision": "R0", "sheets": 1, "copies": 1}],
             "remarks": "Issued for fabrication. Any deviation to be raised before cutting material."})
    pf("MSCAST Transmittal Note", "MSCAST Transmittal", TRANSMITTAL_HTML)
    return "register + print + %d transmittals" % frappe.db.count("MSCAST Transmittal")


# ------------------------------------------------------------ PC-19 commissioning
COMM_HTML = """
<div class="ms-title">COMMISSIONING &amp; PERFORMANCE TRIAL REPORT</div>
<table class="meta">
  <tr><td class="k">Report No.</td><td>{{ doc.name }}</td>
      <td class="k">Project</td><td>{{ doc.project or "-" }}</td></tr>
  <tr><td class="k">Customer</td><td>{{ doc.customer or "-" }}</td>
      <td class="k">Site</td><td>{{ doc.site_location or "-" }}</td></tr>
  <tr><td class="k">Machine / Serial</td><td>{{ doc.machine_description or "-" }} {{ doc.machine_sn or "" }}</td>
      <td class="k">Period</td><td>{{ frappe.utils.formatdate(doc.start_date, "dd-MM-yyyy") }} to
        {{ frappe.utils.formatdate(doc.end_date, "dd-MM-yyyy") }}</td></tr>
  <tr><td class="k">Trial heats / runs</td><td>{{ doc.trial_runs or 0 }}</td>
      <td class="k">Status</td><td><span class="badge">{{ doc.status }}</span></td></tr>
</table>
<table class="ms">
  <thead><tr><th style="width:5%">#</th><th>Parameter</th><th style="width:20%">Contractual / Specified</th>
    <th style="width:20%">Achieved on trial</th><th style="width:10%">Result</th></tr></thead>
  <tbody>
  {% for r in doc.parameters %}
    <tr><td>{{ loop.index }}</td><td>{{ r.parameter }}</td><td>{{ r.specified }}</td>
      <td>{{ r.achieved }}</td><td>{{ r.result }}</td></tr>
  {% endfor %}
  </tbody>
</table>
{% if doc.punch_points %}
<div class="ms-note"><b>Punch list / pending points:</b><div style="white-space:pre-line">{{ doc.punch_points }}</div></div>
{% endif %}
{% if doc.observations %}<div class="ms-note"><b>Observations:</b> {{ doc.observations }}</div>{% endif %}
<div class="ms-note">The machine has been commissioned and the above performance parameters demonstrated in the
presence of the customer's representative. Guarantee period commences from the date of provisional acceptance
as per the contract.</div>
<table class="sign"><tr><td>MSCAST Commissioning Engineer<br>{{ doc.mscast_engineer or "" }}</td>
  <td>MSCAST Project Manager</td>
  <td>For {{ doc.customer or "Customer" }}<br>{{ doc.customer_representative or "" }}</td></tr></table>
"""


def commissioning():
    doctype("MSCAST Commissioning Parameter", [
        f("parameter", "Parameter", "Data", reqd=1, in_list_view=1, columns=3),
        f("specified", "Specified", "Data", in_list_view=1, columns=3),
        f("achieved", "Achieved", "Data", in_list_view=1, columns=3),
        f("result", "Result", "Select", options="Met\nNot met\nDeviation accepted",
          default="Met", in_list_view=1, columns=2),
        f("remarks", "Remarks", "Data"),
    ], istable=1)
    doctype("MSCAST Commissioning Report", [
        f("naming_series", "Series", "Select", options="COMM-.YYYY.-", default="COMM-.YYYY.-", reqd=1),
        f("project", "Project", "Link", options="Project", reqd=1, in_list_view=1, in_standard_filter=1),
        f("customer", "Customer", "Link", options="Customer", in_list_view=1),
        f("site_location", "Site", "Data"),
        f("machine_description", "Machine", "Data"),
        f("machine_sn", "Serial No.", "Data"),
        f("cb0", "", "Column Break"),
        f("start_date", "Commissioning Start", "Date", in_list_view=1),
        f("end_date", "Commissioning End", "Date"),
        f("trial_runs", "Trial Heats / Runs", "Int"),
        f("status", "Status", "Select",
          options="In progress\nCompleted - provisional acceptance\nCompleted - final acceptance\nHeld up at site",
          default="In progress", in_list_view=1, in_standard_filter=1),
        f("guarantee_start", "Guarantee Period Starts", "Date"),
        f("sb0", "Performance Parameters", "Section Break"),
        f("parameters", "Parameters", "Table", options="MSCAST Commissioning Parameter"),
        f("sb1", "Punch List and Observations", "Section Break"),
        f("punch_points", "Punch List", "Small Text"),
        f("observations", "Observations", "Small Text"),
        f("cb1", "", "Column Break"),
        f("mscast_engineer", "MSCAST Engineer", "Data"),
        f("customer_representative", "Customer Representative", "Data"),
    ], title_field="project", search_fields="project,customer,status")

    if not frappe.db.count("MSCAST Commissioning Report"):
        ins({"doctype": "MSCAST Commissioning Report", "project": P1(),
             "customer": "Sahyadri Steels Ltd (DEMO)", "site_location": "Jalna works, Maharashtra",
             "machine_description": "2-strand billet caster 130 sq", "machine_sn": "MS/CCM/2026/07",
             "start_date": add_days(TODAY, -9), "end_date": add_days(TODAY, -4), "trial_runs": 6,
             "status": "Completed - provisional acceptance", "guarantee_start": add_days(TODAY, -4),
             "mscast_engineer": "S. Pawar", "customer_representative": "R. Kulkarni (SSL)",
             "parameters": [
                 {"parameter": "Casting speed (130 sq)", "specified": "2.2 - 2.8 m/min",
                  "achieved": "2.6 m/min sustained", "result": "Met"},
                 {"parameter": "Billet surface quality", "specified": "Free of cracks / laps",
                  "achieved": "Accepted on 6 heats", "result": "Met"},
                 {"parameter": "Mould oscillation frequency", "specified": "100 - 220 cpm",
                  "achieved": "80 - 220 cpm", "result": "Met"},
                 {"parameter": "Water circuit pressure", "specified": "8 bar min",
                  "achieved": "7.6 bar (customer pump limitation)", "result": "Deviation accepted"},
                 {"parameter": "Cut length tolerance", "specified": "+/- 50 mm",
                  "achieved": "+/- 30 mm", "result": "Met"}],
             "punch_points": "1. Customer to upgrade cooling pump to reach 8 bar.\n"
                             "2. Two spare nozzles to be replenished by MSCAST within 30 days.\n"
                             "3. Operator training - second batch pending.",
             "observations": "Machine handed over for regular production. Guarantee period of 12 months "
                             "commences from the date of provisional acceptance."})
    pf("MSCAST Commissioning Report Print", "MSCAST Commissioning Report", COMM_HTML)
    return "doctype + print + demo report"


# ------------------------------------------------------------ PC-20 spares handover
SPARES_HTML = """
<div class="ms-title">MANDATORY / COMMISSIONING SPARES HANDOVER NOTE</div>
<table class="meta">
  <tr><td class="k">Handover No.</td><td>{{ doc.name }}</td>
      <td class="k">Date</td><td>{{ frappe.utils.formatdate(doc.handover_date, "dd-MM-yyyy") }}</td></tr>
  <tr><td class="k">Project</td><td>{{ doc.project or "-" }}</td>
      <td class="k">Customer</td><td>{{ doc.customer or "-" }}</td></tr>
  <tr><td class="k">Category</td><td>{{ doc.spares_type }}</td>
      <td class="k">Delivery Note</td><td>{{ doc.delivery_note or "-" }}</td></tr>
</table>
<table class="ms">
  <thead><tr><th style="width:5%">#</th><th style="width:18%">Part No.</th><th>Description</th>
    <th style="width:9%" class="num">Qty</th><th style="width:8%">UOM</th>
    <th style="width:22%">Recommended use</th></tr></thead>
  <tbody>
  {% for r in doc.items %}
    <tr><td>{{ loop.index }}</td><td>{{ r.part_no or r.item_code }}</td><td>{{ r.description }}</td>
      <td class="num">{{ "{:,.2f}".format(r.qty) }}</td><td>{{ r.uom }}</td>
      <td>{{ r.recommended_use or "" }}</td></tr>
  {% endfor %}
  </tbody>
</table>
{% if doc.remarks %}<div class="ms-note"><b>Remarks:</b> {{ doc.remarks }}</div>{% endif %}
<div class="ms-note">The above spares form part of the contract scope and are handed over in sound condition.
Consumption of commissioning spares during trials is to the customer's account unless stated otherwise.</div>
<table class="sign"><tr><td>Handed over by (MSCAST)</td><td>Stores</td>
  <td>Received by {{ doc.received_by or "" }}</td></tr></table>
"""


def spares():
    doctype("MSCAST Spares Item", [
        f("item_code", "Item", "Link", options="Item", in_list_view=1, columns=2),
        f("part_no", "Part No.", "Data", in_list_view=1, columns=2),
        f("description", "Description", "Data", in_list_view=1, columns=3),
        f("qty", "Qty", "Float", in_list_view=1, columns=1, default="1"),
        f("uom", "UOM", "Link", options="UOM", in_list_view=1, columns=1),
        f("recommended_use", "Recommended Use", "Data", in_list_view=1, columns=2),
    ], istable=1)
    doctype("MSCAST Spares Handover", [
        f("naming_series", "Series", "Select", options="SPH-.YYYY.-", default="SPH-.YYYY.-", reqd=1),
        f("project", "Project", "Link", options="Project", reqd=1, in_list_view=1, in_standard_filter=1),
        f("customer", "Customer", "Link", options="Customer", in_list_view=1),
        f("handover_date", "Handover Date", "Date", default="Today", in_list_view=1),
        f("cb0", "", "Column Break"),
        f("spares_type", "Category", "Select",
          options="Commissioning spares\nMandatory spares (2 years)\nRecommended spares\nWarranty replacement",
          default="Commissioning spares", in_standard_filter=1, in_list_view=1),
        f("delivery_note", "Delivery Note", "Link", options="Delivery Note"),
        f("received_by", "Received By", "Data"),
        f("sb0", "Spares", "Section Break"),
        f("items", "Spares", "Table", options="MSCAST Spares Item", reqd=1),
        f("sb1", "Remarks", "Section Break"),
        f("remarks", "Remarks", "Small Text"),
    ], title_field="project", search_fields="project,customer,spares_type")

    if not frappe.db.count("MSCAST Spares Handover"):
        ins({"doctype": "MSCAST Spares Handover", "project": P1(),
             "customer": "Sahyadri Steels Ltd (DEMO)", "handover_date": add_days(TODAY, -4),
             "spares_type": "Commissioning spares", "received_by": "R. Kulkarni (SSL)",
             "items": [
                 {"part_no": "MS-NZ-3.5", "description": "Spray nozzle 3.5 mm brass", "qty": 12,
                  "uom": "Nos", "recommended_use": "Segment 1 and 2 cooling"},
                 {"part_no": "MS-MT-130", "description": "Copper mould tube 130 sq", "qty": 1,
                  "uom": "Nos", "recommended_use": "Standby for first campaign"},
                 {"part_no": "MS-SEAL-K1", "description": "Hydraulic cylinder seal kit", "qty": 2,
                  "uom": "Set", "recommended_use": "Withdrawal unit"},
                 {"part_no": "MS-BRG-6210", "description": "Roller bearing 6210 2RS", "qty": 8,
                  "uom": "Nos", "recommended_use": "Withdrawal / straightener rollers"}],
             "remarks": "Commissioning spares handed over at site along with the machine. "
                        "Mandatory 2-year spares list quoted separately under offer MS/SP/2026/14."})
        ins({"doctype": "MSCAST Spares Handover", "project": P2(),
             "customer": "Deccan Extrusions Pvt Ltd (DEMO)", "handover_date": add_days(TODAY, -2),
             "spares_type": "Mandatory spares (2 years)",
             "items": [{"part_no": "AL-DIE-7", "description": "Billet die insert 7 inch", "qty": 2,
                        "uom": "Nos", "recommended_use": "Planned changeover"},
                       {"part_no": "AL-THERMO-K", "description": "K-type thermocouple assembly", "qty": 6,
                        "uom": "Nos", "recommended_use": "Melt and mould temperature"}],
             "remarks": "Against clause 9 of the purchase order - two-year mandatory spares."})
    pf("MSCAST Spares Handover Note", "MSCAST Spares Handover", SPARES_HTML)
    return "doctype + print + %d handovers" % frappe.db.count("MSCAST Spares Handover")


# ------------------------------------------------------------ PC-01 kick-off + PO check
def kickoff():
    doctype("MSCAST Project Kickoff", [
        f("naming_series", "Series", "Select", options="KICK-.YYYY.-", default="KICK-.YYYY.-", reqd=1),
        f("project", "Project", "Link", options="Project", reqd=1, in_list_view=1, in_standard_filter=1),
        f("customer", "Customer", "Link", options="Customer", in_list_view=1),
        f("sales_order", "Sales Order", "Link", options="Sales Order"),
        f("quotation_ref", "Our Offer / Quotation Ref.", "Data"),
        f("cb0", "", "Column Break"),
        f("customer_po_no", "Customer PO No.", "Data", reqd=1, in_list_view=1),
        f("customer_po_date", "Customer PO Date", "Date"),
        f("po_value", "PO Value", "Currency", in_list_view=1),
        f("contract_delivery_date", "Contract Delivery Date", "Date"),
        f("sb0", "Customer PO verification checklist", "Section Break"),
        f("chk_price", "Price matches our offer", "Check", default="0"),
        f("chk_scope", "Scope and technical specification match", "Check", default="0"),
        f("chk_payment_terms", "Payment terms accepted", "Check", default="0"),
        f("chk_delivery", "Delivery period acceptable", "Check", default="0"),
        f("cb1", "", "Column Break"),
        f("chk_ld_clause", "LD / penalty clause reviewed", "Check", default="0"),
        f("chk_tax_gst", "GST rate, HSN and place of supply verified", "Check", default="0"),
        f("chk_bg_required", "BG / PBG requirement identified", "Check", default="0"),
        f("chk_advance", "Advance received", "Check", default="0"),
        f("po_deviations", "Deviations found in customer PO", "Small Text"),
        f("sb1", "Kick-off meeting", "Section Break"),
        f("kickoff_date", "Kick-off Meeting Date", "Date", in_list_view=1),
        f("attendees", "Attendees", "Small Text"),
        f("cb2", "", "Column Break"),
        f("design_freeze_date", "Design Freeze Target", "Date"),
        f("first_dispatch_target", "First Dispatch Target", "Date"),
        f("sb2", "Agreed actions", "Section Break"),
        f("agreed_actions", "Agreed Actions", "Small Text"),
        f("open_points", "Open Points", "Small Text"),
    ], title_field="project", search_fields="project,customer,customer_po_no")

    # workflow states / actions
    for st, style in [("Draft", ""), ("PO Verified", "Warning"), ("Kick-off Approved", "Success"),
                      ("PO Query Raised", "Danger")]:
        if not frappe.db.exists("Workflow State", st):
            ins({"doctype": "Workflow State", "workflow_state_name": st, "style": style})
    for act in ["Verify Customer PO", "Raise Query to Customer", "Approve Kick-off", "Reopen"]:
        if not frappe.db.exists("Workflow Action Master", act):
            ins({"doctype": "Workflow Action Master", "workflow_action_name": act})
    frappe.db.commit()

    wf_name = "MSCAST Project Kick-off"
    if not frappe.db.exists("Workflow", wf_name):
        ins({"doctype": "Workflow", "workflow_name": wf_name,
             "document_type": "MSCAST Project Kickoff", "is_active": 1,
             "workflow_state_field": "workflow_state", "send_email_alert": 0,
             "states": [
                 {"state": "Draft", "doc_status": "0", "allow_edit": "Projects Manager"},
                 {"state": "PO Query Raised", "doc_status": "0", "allow_edit": "Projects Manager"},
                 {"state": "PO Verified", "doc_status": "0", "allow_edit": "Accounts Manager"},
                 {"state": "Kick-off Approved", "doc_status": "0", "allow_edit": "System Manager"},
             ],
             "transitions": [
                 {"state": "Draft", "action": "Verify Customer PO", "next_state": "PO Verified",
                  "allowed": "Accounts Manager",
                  "condition": "doc.chk_price and doc.chk_scope and doc.chk_payment_terms and doc.chk_tax_gst"},
                 {"state": "Draft", "action": "Raise Query to Customer", "next_state": "PO Query Raised",
                  "allowed": "Projects Manager"},
                 {"state": "PO Query Raised", "action": "Verify Customer PO", "next_state": "PO Verified",
                  "allowed": "Accounts Manager"},
                 {"state": "PO Verified", "action": "Approve Kick-off", "next_state": "Kick-off Approved",
                  "allowed": "System Manager"},
                 {"state": "PO Verified", "action": "Reopen", "next_state": "Draft",
                  "allowed": "Projects Manager"},
             ]})
    frappe.db.commit()

    if not frappe.db.count("MSCAST Project Kickoff"):
        so1 = frappe.db.get_value("Sales Order", {"customer": ("like", "Sahyadri%"), "docstatus": 1}, "name")
        so2 = frappe.db.get_value("Sales Order", {"customer": ("like", "Deccan%"), "docstatus": 1}, "name")
        k1 = ins({"doctype": "MSCAST Project Kickoff", "project": P1(),
                  "customer": "Sahyadri Steels Ltd (DEMO)", "sales_order": so1,
                  "quotation_ref": "MS/OFR/2026/031 R2", "customer_po_no": "SSL/PO/2026/0417",
                  "customer_po_date": add_days(TODAY, -78), "po_value": 20265000,
                  "contract_delivery_date": add_days(TODAY, 40),
                  "chk_price": 1, "chk_scope": 1, "chk_payment_terms": 1, "chk_delivery": 1,
                  "chk_ld_clause": 1, "chk_tax_gst": 1, "chk_bg_required": 1, "chk_advance": 1,
                  "po_deviations": "PO asks for LD at 0.5% per week capped at 5%; our offer said 0.5% "
                                   "per week capped at 5% - matches. Payment milestone 3 reworded, accepted.",
                  "kickoff_date": add_days(TODAY, -74),
                  "attendees": "MSCAST: Managing Director, Design head, Projects, Accounts. "
                               "SSL: Projects head, Works manager.",
                  "design_freeze_date": add_days(TODAY, -60),
                  "first_dispatch_target": add_days(TODAY, -20),
                  "agreed_actions": "1. GA drawing for approval within 10 days.\n"
                                    "2. Advance 30% against PBG - released.\n"
                                    "3. Civil foundation drawing to customer by week 3.",
                  "open_points": "Customer to confirm water pump capacity at site."})
        frappe.db.set_value("MSCAST Project Kickoff", k1.name, "workflow_state", "Kick-off Approved")
        k2 = ins({"doctype": "MSCAST Project Kickoff", "project": P2(),
                  "customer": "Deccan Extrusions Pvt Ltd (DEMO)", "sales_order": so2,
                  "quotation_ref": "MS/OFR/2026/044", "customer_po_no": "DEPL/PO/26-27/112",
                  "customer_po_date": add_days(TODAY, -26), "po_value": 14200000,
                  "contract_delivery_date": add_days(TODAY, 120),
                  "chk_price": 1, "chk_scope": 1, "chk_payment_terms": 0, "chk_delivery": 1,
                  "chk_ld_clause": 1, "chk_tax_gst": 1, "chk_bg_required": 0, "chk_advance": 0,
                  "po_deviations": "PO states 100% payment against delivery; our offer was 30 percent "
                                   "advance / 60 percent against dispatch / 10 percent after commissioning. "
                                   "Query raised with the customer - kick-off held until resolved.",
                  "kickoff_date": add_days(TODAY, -20),
                  "attendees": "MSCAST: Projects, Accounts. DEPL: Purchase head.",
                  "open_points": "Payment terms deviation to be closed before design release."})
        frappe.db.set_value("MSCAST Project Kickoff", k2.name, "workflow_state", "PO Query Raised")
        frappe.db.commit()
    return "doctype + workflow (%s) + 2 kick-off records" % wf_name


def run():
    step("document / drawing transmittal register", transmittal)
    step("commissioning report", commissioning)
    step("spares handover note", spares)
    step("kick-off and customer-PO-check workflow", kickoff)
    frappe.clear_cache()
    log("BATCH C2b DONE")


run()
