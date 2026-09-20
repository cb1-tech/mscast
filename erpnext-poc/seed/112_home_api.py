import frappe

SCRIPT = r'''
rep = "MSCAST Daily Management Summary"
q = frappe.db.get_value("Report", rep, "query")
rows = frappe.db.sql(q, as_dict=True)

summary = []
for r in rows:
    vals = list(r.values())
    summary.append({
        "area": vals[0],
        "indicator": vals[1],
        "value": vals[2],
        "attention": vals[3] if len(vals) > 3 else "",
    })

def fmt_money(v):
    try:
        v = float(v)
    except Exception:
        return v
    if abs(v) >= 10000000:
        return "Rs %.2f Cr" % (v / 10000000.0)
    if abs(v) >= 100000:
        return "Rs %.2f L" % (v / 100000.0)
    return "Rs %d" % int(round(v))

ind = {}
for s in summary:
    ind[s["indicator"]] = {"value": s["value"], "attention": s["attention"] or ""}

today = frappe.db.sql("select date(convert_tz(utc_timestamp(),'+00:00','+05:30'))")[0][0]

projects = []
for p in frappe.get_all("Project",
        filters={"status": "Open"},
        fields=["name", "project_name", "customer", "percent_complete", "expected_end_date", "total_billed_amount"],
        order_by="expected_end_date asc"):
    so = frappe.get_all("Sales Order", filters={"project": p.name, "docstatus": 1},
                        fields=["name", "grand_total"], limit=1)
    pcc = frappe.get_all("MSCAST PCC", filters={"project": p.name, "status": "Approved"},
                         fields=["name", "total_estimated_cost", "revision"], limit=1)
    pcc_any = pcc or frappe.get_all("MSCAST PCC", filters={"project": p.name},
                                    fields=["name", "total_estimated_cost", "revision", "status"], limit=1)
    contract = so[0].grand_total if so else 0
    cost = pcc_any[0].total_estimated_cost if pcc_any else 0
    days = None
    if p.expected_end_date:
        days = frappe.utils.date_diff(p.expected_end_date, today)
    projects.append({
        "name": p.name,
        "title": p.project_name,
        "customer": (p.customer or "").replace(" (DEMO)", ""),
        "percent": p.percent_complete or 0,
        "due": frappe.utils.formatdate(p.expected_end_date, "d MMM yyyy") if p.expected_end_date else "",
        "days_left": days,
        "contract": fmt_money(contract),
        "cost": fmt_money(cost),
        "margin": round((contract - cost) * 100.0 / contract, 1) if contract else None,
        "billed": fmt_money(p.total_billed_amount or 0),
        "pcc": pcc_any[0].name if pcc_any else None,
        "pcc_state": (pcc_any[0].get("status") if pcc_any else None) or ("Approved" if pcc else None),
    })

def cnt(dt, filters=None):
    try:
        return frappe.db.count(dt, filters or {})
    except Exception:
        return 0

counts = {
    "opportunity_open": cnt("Opportunity", {"status": "Open"}),
    "quotation": cnt("Quotation", {"docstatus": 1}),
    "so_open": cnt("Sales Order", {"docstatus": 1, "status": ["not in", ["Closed", "Completed"]]}),
    "drawing_customer": cnt("MSCAST Drawing", {"status": "For Customer Approval"}),
    "drawing_draft": cnt("MSCAST Drawing", {"status": "Draft"}),
    "drawing_total": cnt("MSCAST Drawing"),
    "mdf_draft": cnt("MSCAST MDF", {"status": "Draft"}),
    "transmittal": cnt("MSCAST Transmittal"),
    "mr_pending": cnt("Material Request", {"docstatus": 1, "status": "Pending"}),
    "rfq": cnt("Request for Quotation", {"docstatus": 1}),
    "po_open": cnt("Purchase Order", {"docstatus": 1, "status": ["in", ["To Receive and Bill", "To Receive", "To Bill"]]}),
    "brm_pending": cnt("MSCAST BRM", {"status": "Pending Certification"}),
    "brm_certified": cnt("MSCAST BRM", {"status": "Certified"}),
    "insp_pending": cnt("MSCAST Inspection Plan", {"result": "Pending"}),
    "insp_plans": cnt("MSCAST Inspection Plan"),
    "qi": cnt("Quality Inspection", {"docstatus": 1}),
    "spares": cnt("MSCAST Spares Handover"),
    "cert_awaited": cnt("MSCAST Project Certificate", {"status": "Awaited"}),
    "bg": cnt("Bank Guarantee"),
    "items": cnt("Item", {"disabled": 0}),
    "employees": cnt("Employee", {"status": "Active"}),
    "leave_pending": cnt("Leave Application", {"docstatus": 0}),
    "expense_claims": cnt("Expense Claim", {"docstatus": 1}),
    "claims_open": cnt("MSCAST Client Claim", {"status": ["in", ["Open", "Agreed", "Submitted"]]}),
    "mdm": cnt("MSCAST MDM"),
    "di": cnt("MSCAST Delivery Instruction"),
    "kickoff_open": cnt("MSCAST Project Kickoff", {"workflow_state": ["!=", "Kick-off Approved"]}),
}

bg_next = frappe.get_all("Bank Guarantee", fields=["name", "end_date"], order_by="end_date asc", limit=1)

user = frappe.session.user
fullname = frappe.db.get_value("User", user, "full_name") or ""

frappe.response["message"] = {
    "as_at": frappe.utils.formatdate(str(today), "EEEE, d MMMM yyyy"),
    "indicators": ind,
    "summary": summary,
    "projects": projects,
    "counts": counts,
    "bg_next": frappe.utils.formatdate(bg_next[0].end_date, "d MMM yyyy") if bg_next else "",
    "user": {"name": user, "full_name": fullname, "initials": "".join([w[0] for w in fullname.split()[:2]]).upper()},
}
'''

name = "MSCAST Home Data"
if frappe.db.exists("Server Script", name):
    doc = frappe.get_doc("Server Script", name)
else:
    doc = frappe.new_doc("Server Script")
    doc.name = name
doc.script_type = "API"
doc.api_method = "mscast_home_data"
doc.allow_guest = 0
doc.disabled = 0
doc.module = "Custom"
doc.script = SCRIPT
doc.save(ignore_permissions=True)
frappe.db.commit()
print("server script saved:", doc.name, "->", doc.api_method)

# smoke test
frappe.local.response = frappe._dict({"_init": 1})
from frappe.utils.safe_exec import safe_exec
try:
    safe_exec(SCRIPT, None, {})
    m = frappe.response.get("message")
    print("OK as_at:", m["as_at"])
    print("indicators:", len(m["indicators"]))
    for k in ["Cash and bank balance", "Outstanding from customers", "Billed this month", "Orders in hand (booked less billed)", "Retention held by customers", "MSME dues due within the next 15 days"]:
        print("   ", k, "=>", m["indicators"].get(k))
    for p in m["projects"]:
        print("   PROJ", p["name"], p["title"][:34], p["percent"], p["due"], p["days_left"], p["contract"], p["cost"], p["margin"], p["billed"])
    print("counts:", m["counts"])
except Exception as e:
    import traceback; traceback.print_exc()
