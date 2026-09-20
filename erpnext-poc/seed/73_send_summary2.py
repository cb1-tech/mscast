"""MSCAST POC - 73: tune the scheduled reports to sane defaults and send the daily
management summary for real."""
import frappe
from frappe.utils import nowdate

log = lambda m: print("[send2] " + m, flush=True)
SUMMARY = "MSCAST Daily Management Summary"
INBOX = "autoelectron.jp@gmail.com"

# ---- context: what time zone does "daily" mean here?
tz = frappe.db.get_single_value("System Settings", "time_zone")
log("site time zone: %s   (daily jobs fire early morning in this zone)" % tz)
try:
    from frappe.utils.scheduler import is_scheduler_inactive
    log("scheduler inactive? %s (site config pause_scheduler=%r, disable_scheduler=%r)"
        % (is_scheduler_inactive(), frappe.conf.get("pause_scheduler"),
           frappe.conf.get("disable_scheduler")))
except Exception as e:
    log("scheduler check skipped: " + repr(e)[:150])

meta = frappe.get_meta("Auto Email Report")
have = {f.fieldname for f in meta.fields if f.fieldname}
log("auto email report fields present: %s"
    % sorted(have & {"format", "send_if_data", "no_of_rows", "sender", "subject", "description",
                     "dynamic_date_period", "day_of_week", "frequency", "email_to", "enabled",
                     "reference_report", "from_date_field", "to_date_field"}))

# ---- best-practice defaults per report
PLAN = {
    SUMMARY: dict(fmt="HTML", send_if_data=0, rows=100,
                  subject="MSCAST daily position - cash, receivables, MSME exposure, order book"),
    "MSCAST Dispatch Schedule": dict(fmt="XLSX", send_if_data=1, rows=500,
                                     subject="MSCAST dispatch schedule - ordered, delivered, pending"),
    "MSCAST Project MIS": dict(fmt="XLSX", send_if_data=1, rows=500,
                               subject="MSCAST project MIS - contract vs PCC vs committed vs billed"),
}
for name, cfg in PLAN.items():
    if not frappe.db.exists("Auto Email Report", name):
        log("missing: %s" % name)
        continue
    d = frappe.get_doc("Auto Email Report", name)
    d.enabled = 1
    d.frequency = "Daily"
    d.email_to = INBOX
    if "format" in have:
        d.format = cfg["fmt"]
    if "send_if_data" in have:
        d.send_if_data = cfg["send_if_data"]
    if "no_of_rows" in have:
        d.no_of_rows = cfg["rows"]
    if "subject" in have:
        d.subject = cfg["subject"]
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    d.save()
    log("%-34s -> %s, send_if_data=%s, rows=%s" % (name, cfg["fmt"], cfg["send_if_data"], cfg["rows"]))
frappe.db.commit()

# ---- send the summary now
log("sending '%s' to %s ..." % (SUMMARY, INBOX))
try:
    frappe.get_doc("Auto Email Report", SUMMARY).send()
    log("send() returned without error")
except Exception as e:
    frappe.db.rollback()
    log("send() FAILED: " + repr(e)[:400])
frappe.db.commit()

try:
    frappe.email.queue.flush()
    frappe.db.commit()
except Exception as e:
    log("flush: " + repr(e)[:200])

for q in frappe.get_all("Email Queue", fields=["name", "status", "error", "creation"],
                        order_by="creation desc", limit=3):
    log("  queue %s | %s | %s" % (q.name, q.status, (q.error or "")[:250]))
log("DONE")
