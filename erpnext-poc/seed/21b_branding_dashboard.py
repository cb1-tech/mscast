"""MSCAST POC - 21: branding (logo, app name, favicon, login page), dark theme,
KPI number cards and dashboard charts wired into the MSCAST workspace."""
import json
import frappe

COMPANY = "MSCAST Engineering Pvt Ltd"
log = lambda m: print("[seed-21] " + m, flush=True)

LOGO_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">
  <defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
    <stop offset="0%" stop-color="#2563eb"/><stop offset="100%" stop-color="#0ea5e9"/>
  </linearGradient></defs>
  <rect width="48" height="48" rx="11" fill="url(#g)"/>
  <path d="M11 34V15h5.2l7.8 11.4L31.8 15H37v19h-4.9V22.8l-7 10.2h-2.2l-7-10.2V34z" fill="#fff"/>
</svg>"""

BANNER_SVG = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 120" width="520" height="120">
  <defs><linearGradient id="b" x1="0" y1="0" x2="1" y2="0">
    <stop offset="0%" stop-color="#1e3a8a"/><stop offset="100%" stop-color="#0ea5e9"/>
  </linearGradient></defs>
  <rect width="520" height="120" rx="14" fill="url(#b)"/>
  <text x="34" y="58" font-family="Helvetica,Arial" font-size="30" font-weight="700" fill="#fff">MSCAST ERP</text>
  <text x="34" y="86" font-family="Helvetica,Arial" font-size="14" fill="#cfe4ff">
    Continuous casting machines - engineering, projects, procurement</text>
</svg>"""


def step(name, fn, *a, **kw):
    try:
        out = fn(*a, **kw)
        frappe.db.commit()
        log("OK   " + name + ((" -> " + str(out)) if out else ""))
        return out or True
    except Exception as e:
        frappe.db.rollback()
        log("FAIL " + name + " :: " + repr(e)[:300])
        return None


def upload(filename, content):
    existing = frappe.db.get_value("File", {"file_name": filename}, "file_url")
    if existing:
        return existing
    f = frappe.get_doc({"doctype": "File", "file_name": filename, "is_private": 0,
                        "content": content})
    f.flags.ignore_permissions = True
    f.insert()
    return f.file_url


def branding():
    logo = upload("mscast-logo.svg", LOGO_SVG)
    banner = upload("mscast-banner.svg", BANNER_SVG)

    ws = frappe.get_single("Website Settings")
    for field, value in [("app_name", "MSCAST ERP"), ("app_logo", logo), ("favicon", logo),
                         ("banner_image", logo), ("splash_image", logo),
                         ("website_theme", ws.website_theme), ("disable_signup", 1),
                         ("hide_footer_signup", 1)]:
        if ws.meta.has_field(field) and value is not None:
            ws.set(field, value)
    if ws.meta.has_field("brand_html"):
        ws.brand_html = ('<span style="display:inline-flex;align-items:center;gap:8px">'
                         '<img src="%s" style="height:22px;width:22px;border-radius:6px">'
                         '<b>MSCAST ERP</b></span>' % logo)
    ws.flags.ignore_permissions = True
    ws.save()

    if frappe.db.exists("DocType", "Navbar Settings"):
        nb = frappe.get_single("Navbar Settings")
        for field in ("app_logo", "logo"):
            if nb.meta.has_field(field):
                nb.set(field, logo)
        nb.flags.ignore_permissions = True
        nb.save()

    ss = frappe.get_single("System Settings")
    for field, value in [("app_name", "MSCAST ERP"), ("banner_image", logo)]:
        if ss.meta.has_field(field):
            ss.set(field, value)
    ss.flags.ignore_permissions = True
    ss.save()
    return "logo %s, banner %s" % (logo, banner)


def dark_theme():
    n = 0
    for u in frappe.get_all("User", filters={"enabled": 1}, pluck="name"):
        if frappe.db.has_column("User", "desk_theme"):
            frappe.db.set_value("User", u, "desk_theme", "Dark")
            n += 1
    return "%d users set to dark desk theme" % n


CARDS = [
    ("Open Projects", "Project", "Count", None, {"status": "Open"}, "#7c3aed"),
    ("Order Book (submitted SO)", "Sales Order", "Sum", "grand_total", {"docstatus": 1}, "#2563eb"),
    ("PO Committed", "Purchase Order", "Sum", "grand_total", {"docstatus": 1}, "#0ea5e9"),
    ("Drawings pending approval", "MSCAST Drawing", "Count", None,
     {"status": "For Customer Approval"}, "#f59e0b"),
    ("BRMs pending certification", "MSCAST BRM", "Count", None, {"status": "Pending"}, "#ef4444"),
    ("Inspections due", "MSCAST Inspection Plan", "Count", None, {"result": "Pending"}, "#10b981"),
]


def number_cards():
    made = []
    for label, dt, fn, field, filters, color in CARDS:
        if frappe.db.exists("Number Card", label):
            continue
        doc = {
            "doctype": "Number Card", "name": label, "label": label, "document_type": dt,
            "function": fn, "is_public": 1, "show_percentage_stats": 1,
            "stats_time_interval": "Monthly", "color": color,
            "filters_json": json.dumps([[dt, k, "=", v, False] for k, v in filters.items()]),
        }
        if field:
            doc["aggregate_function_based_on"] = field
        d = frappe.get_doc(doc)
        d.flags.ignore_permissions = True
        d.insert()
        made.append(label)
    return ", ".join(made) or "(all existed)"


CHARTS = [
    dict(name="Order Book by Customer", document_type="Sales Order", chart_type="Group By",
         group_by_type="Sum", group_by_based_on="customer", aggregate_function_based_on="grand_total",
         type="Donut", color="#2563eb", filters=[["Sales Order", "docstatus", "=", 1, False]]),
    dict(name="Drawings by Status", document_type="MSCAST Drawing", chart_type="Group By",
         group_by_type="Count", group_by_based_on="status", type="Bar", color="#0ea5e9", filters=[]),
    dict(name="Purchase Commitment by Supplier", document_type="Purchase Order", chart_type="Group By",
         group_by_type="Sum", group_by_based_on="supplier", aggregate_function_based_on="grand_total",
         type="Bar", color="#7c3aed", filters=[["Purchase Order", "docstatus", "=", 1, False]]),
    dict(name="Inspection Results", document_type="MSCAST Inspection Plan", chart_type="Group By",
         group_by_type="Count", group_by_based_on="result", type="Pie", color="#10b981", filters=[]),
    dict(name="Engineering Hours by Activity", document_type="Timesheet Detail",
         parent_document_type="Timesheet", chart_type="Group By",
         group_by_type="Sum", group_by_based_on="activity_type", aggregate_function_based_on="hours",
         type="Bar", color="#f59e0b", filters=[]),
]


def charts():
    made = []
    for c in CHARTS:
        if frappe.db.exists("Dashboard Chart", c["name"]):
            continue
        doc = {
            "doctype": "Dashboard Chart", "name": c["name"], "chart_name": c["name"],
            "chart_type": c["chart_type"], "document_type": c["document_type"],
            "group_by_type": c.get("group_by_type"), "group_by_based_on": c.get("group_by_based_on"),
            "aggregate_function_based_on": c.get("aggregate_function_based_on"),
            "type": c["type"], "color": c.get("color"), "is_public": 1, "timeseries": 0,
            "filters_json": json.dumps(c.get("filters") or []), "number_of_groups": 0,
        }
        if c.get("parent_document_type"):
            doc["parent_document_type"] = c["parent_document_type"]
        d = frappe.get_doc(doc)
        d.flags.ignore_permissions = True
        d.insert()
        made.append(c["name"])
    return ", ".join(made) or "(all existed)"


SHORTCUTS = [
    ("MSCAST PCC", "DocType", "Blue"), ("MSCAST Drawing", "DocType", "Green"),
    ("MSCAST MDF", "DocType", "Orange"), ("MSCAST BRM", "DocType", "Red"),
    ("MSCAST MDM", "DocType", "Purple"), ("MSCAST Delivery Instruction", "DocType", "Cyan"),
    ("Project", "DocType", "Grey"), ("MSCAST Project MIS", "Report", "Yellow"),
]

CARDS_LINKS = [
    ("Engineering", [("MSCAST Drawing", "DocType"), ("MSCAST MDF", "DocType"),
                     ("Timesheet", "DocType"), ("MSCAST Drawing Register", "Report")]),
    ("Sales & Projects", [("Opportunity", "DocType"), ("Quotation", "DocType"),
                          ("Sales Order", "DocType"), ("Project", "DocType"),
                          ("MSCAST PCC", "DocType"), ("MSCAST Project Certificate", "DocType"),
                          ("MSCAST Project MIS", "Report")]),
    ("Procurement", [("Material Request", "DocType"), ("Request for Quotation", "DocType"),
                     ("Supplier Quotation", "DocType"), ("Purchase Order", "DocType"),
                     ("MSCAST BRM", "DocType"), ("MSCAST Inspection Plan", "DocType"),
                     ("MSCAST PO vs PCC Variance", "Report")]),
    ("Dispatch & Stock", [("MSCAST MDM", "DocType"), ("MSCAST Delivery Instruction", "DocType"),
                          ("Delivery Note", "DocType"), ("Stock Entry", "DocType"),
                          ("MSCAST Free Issue at Vendor", "Report"),
                          ("MSCAST Dispatch Schedule", "Report")]),
    ("Accounts & GST", [("Sales Invoice", "DocType"), ("Purchase Invoice", "DocType"),
                        ("Payment Entry", "DocType"), ("GSTR-1", "DocType"),
                        ("Purchase Reconciliation Tool", "DocType"),
                        ("MSCAST Retention and Certificates", "Report"),
                        ("MSCAST BRM Register", "Report")]),
    ("HR & Payroll", [("Employee", "DocType"), ("Attendance", "DocType"),
                      ("Leave Application", "DocType"), ("Salary Slip", "DocType"),
                      ("Expense Claim", "DocType")]),
]


def workspace():
    if frappe.db.exists("Workspace", "MSCAST"):
        frappe.delete_doc("Workspace", "MSCAST", force=1, ignore_permissions=True)
    content = [
        {"id": "hdr", "type": "header",
         "data": {"text": '<span class="h4"><b>MSCAST ERP</b></span>', "col": 12}},
    ]
    for label, _dt, _fn, _f, _flt, _c in CARDS:
        content.append({"id": "nc-" + label[:12].replace(" ", ""), "type": "number_card",
                        "data": {"number_card_name": label, "col": 4}})
    content.append({"id": "sp1", "type": "spacer", "data": {"col": 12}})
    content.append({"id": "ch1", "type": "chart",
                    "data": {"chart_name": "Order Book by Customer", "col": 6}})
    content.append({"id": "ch2", "type": "chart",
                    "data": {"chart_name": "Purchase Commitment by Supplier", "col": 6}})
    content.append({"id": "ch3", "type": "chart",
                    "data": {"chart_name": "Drawings by Status", "col": 4}})
    content.append({"id": "ch4", "type": "chart",
                    "data": {"chart_name": "Inspection Results", "col": 4}})
    content.append({"id": "ch5", "type": "chart",
                    "data": {"chart_name": "Engineering Hours by Activity", "col": 4}})
    content.append({"id": "sp2", "type": "spacer", "data": {"col": 12}})
    for label, _t, _c in SHORTCUTS:
        content.append({"id": "sc-" + label[:14].replace(" ", ""), "type": "shortcut",
                        "data": {"shortcut_name": label, "col": 3}})
    content.append({"id": "sp3", "type": "spacer", "data": {"col": 12}})
    for card, _links in CARDS_LINKS:
        content.append({"id": "cd-" + card[:12].replace(" ", "").replace("&", ""),
                        "type": "card", "data": {"card_name": card, "col": 4}})

    ws = frappe.get_doc({
        "doctype": "Workspace", "name": "MSCAST", "label": "MSCAST", "title": "MSCAST",
        "module": "Custom", "public": 1, "icon": "tool", "sequence_id": 0.5,
        "content": json.dumps(content),
        "shortcuts": [{"type": t, "link_to": n, "label": n, "color": c} for n, t, c in SHORTCUTS],
        "number_cards": [{"number_card_name": lbl, "label": lbl} for lbl, *_ in CARDS],
        "charts": [{"chart_name": c["name"], "label": c["name"]} for c in CHARTS],
        "links": [],
    })
    for card, links in CARDS_LINKS:
        ws.append("links", {"type": "Card Break", "label": card, "link_count": len(links)})
        for name, ltype in links:
            if ltype == "DocType" and not frappe.db.exists("DocType", name):
                continue
            ws.append("links", {"type": "Link", "label": name, "link_type": ltype,
                                "link_to": name, "is_query_report": 1 if ltype == "Report" else 0})
    ws.flags.ignore_permissions = True
    ws.insert()
    return "workspace rebuilt with %d cards and %d charts" % (len(CARDS), len(CHARTS))


def run():
    step("branding", branding)
    step("dark theme", dark_theme)
    step("number cards", number_cards)
    step("dashboard charts", charts)
    step("workspace", workspace)
    frappe.clear_cache()
    log("DONE")


run()
