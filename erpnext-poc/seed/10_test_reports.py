"""MSCAST ERPNext POC - 10: smoke-test the query reports and key links."""
import frappe
from frappe.desk.query_report import run as run_report

log = lambda m: print("[test]", m, flush=True)

REPORTS = [
    "MSCAST PO vs PCC Variance", "MSCAST Project MIS", "MSCAST Free Issue at Vendor",
    "MSCAST Drawing Register", "MSCAST Dispatch Schedule", "MSCAST Retention and Certificates",
    "MSCAST BRM Register", "MSCAST Inspection Status",
]

for r in REPORTS:
    try:
        res = run_report(r, filters=None, ignore_prepared_report=True)
        rows = res.get("result") or []
        log("OK   %-40s rows=%d" % (r, len(rows)))
        if rows:
            first = rows[0]
            if isinstance(first, dict):
                vals = list(first.values())[:4]
            else:
                vals = list(first)[:4]
            log("     sample: %s" % (vals,))
    except Exception as e:
        log("FAIL %-40s %s" % (r, repr(e)[:200]))

# standard reports that matter for the demo
for r, filters in [
    ("Stock Balance", {"company": "MSCAST Engineering Pvt Ltd", "from_date": "2026-04-01", "to_date": "2027-03-31"}),
    ("Project Profitability", {"company": "MSCAST Engineering Pvt Ltd", "start_date": "2026-04-01", "end_date": "2027-03-31"}),
]:
    try:
        res = run_report(r, filters=filters, ignore_prepared_report=True)
        log("OK   %-40s rows=%d" % (r, len(res.get("result") or [])))
    except Exception as e:
        log("FAIL %-40s %s" % (r, repr(e)[:160]))

ws = frappe.get_doc("Workspace", "MSCAST")
log("workspace shortcuts=%d links=%d" % (len(ws.shortcuts), len(ws.links)))
log("custom doctypes: %s" % frappe.get_all("DocType", filters={"name": ("like", "MSCAST%")}, pluck="name"))
log("DONE")
