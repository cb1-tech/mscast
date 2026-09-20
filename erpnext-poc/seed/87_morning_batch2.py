"""MSCAST POC - 87: move the daily auto email reports from 00:00 to 08:30 IST.

Approach: leave every Auto Email Report enabled (send() refuses on a disabled one), stop Frappe's
built-in midnight 'send_daily' job, and drive the identical logic from a cron script at 08:30
site time. Behaviour is unchanged apart from the hour.
"""
import frappe
log = lambda m: print("[morning2] " + m, flush=True)

SCRIPT_NAME = "MSCAST morning report batch"
BUILTIN = "frappe.email.doctype.auto_email_report.auto_email_report.send_daily"

BATCH = """
for r in frappe.get_all("Auto Email Report",
                        filters={"enabled": 1, "frequency": ["in", ["Daily", "Daily Long"]]},
                        pluck="name"):
    try:
        frappe.get_doc("Auto Email Report", r).send()
    except Exception:
        frappe.log_error(title="MSCAST morning report failed: " + r)
"""

job = frappe.db.get_value("Scheduled Job Type", {"method": BUILTIN}, "name")
log("built-in daily job: %s" % job)
if job:
    frappe.db.set_value("Scheduled Job Type", job, "stopped", 1)
    frappe.db.commit()
    log("stopped the midnight batch (reversible: set stopped=0 on %s)" % job)

if frappe.db.exists("Server Script", SCRIPT_NAME):
    s = frappe.get_doc("Server Script", SCRIPT_NAME)
    s.script = BATCH
    s.cron_format = "30 8 * * *"
    s.disabled = 0
else:
    s = frappe.get_doc({"doctype": "Server Script", "name": SCRIPT_NAME,
                        "script_type": "Scheduler Event", "event_frequency": "Cron",
                        "cron_format": "30 8 * * *", "disabled": 0, "module": "Custom",
                        "script": BATCH})
s.flags.ignore_permissions = True
s.save() if s.get("name") and frappe.db.exists("Server Script", SCRIPT_NAME) else s.insert()
frappe.db.commit()
log("cron server script '%s' set to 30 8 * * *" % SCRIPT_NAME)

rows = frappe.get_all("Scheduled Job Type", filters={"server_script": SCRIPT_NAME},
                      fields=["name", "frequency", "cron_format", "stopped"])
log("scheduled job rows for the script: %s" % rows)
for r in rows:
    try:
        log("  next execution (site time / IST): %s"
            % frappe.get_doc("Scheduled Job Type", r.name).get_next_execution())
    except Exception as e:
        log("  next execution: n/a %s" % repr(e)[:150])

log("--- sanity: what fires daily now ---")
for j in frappe.get_all("Scheduled Job Type",
                        filters={"method": ("like", "%%auto_email_report%%")},
                        fields=["name", "method", "frequency", "stopped"]):
    log("  %s | %s | stopped=%s" % (j.method, j.frequency, j.stopped))
for r in frappe.get_all("Auto Email Report", fields=["name", "enabled", "frequency"]):
    log("  AER %-34s enabled=%s frequency=%s" % (r.name, r.enabled, r.frequency))
log("DONE")
