# -*- coding: utf-8 -*-
"""Is the agent actually wired to run by itself, or only by hand?

Checks every link in the chain between 06:00 and the director's inbox, and
says which ones are live on this site right now.
"""
import frappe

print("=" * 70)
print("1. IS THE SCHEDULER RUNNING AT ALL")
print("=" * 70)
from frappe.utils.scheduler import is_scheduler_inactive
inactive = is_scheduler_inactive(verbose=False)
print("  site_config pause_scheduler  :", frappe.conf.get("pause_scheduler"))
print("  site_config maintenance_mode :", frappe.conf.get("maintenance_mode"))
print("  -> scheduler is", "INACTIVE - nothing fires on its own" if inactive else "ACTIVE")

print()
print("=" * 70)
print("2. STEP ONE - THE RULES SWEEP (Server Script, 06:00, no model)")
print("=" * 70)
for s in frappe.get_all("Server Script",
                        filters={"script_type": "Scheduler Event"},
                        fields=["name", "disabled", "cron_format", "event_frequency"]):
    print("  %-28s disabled=%s  cron=%s %s"
          % (s.name, s.disabled, s.cron_format or "-", s.event_frequency or ""))

print()
print("=" * 70)
print("3. STEP TWO - THE JUDGEMENT (app hook, 08:35, calls the model)")
print("=" * 70)
try:
    hooks = frappe.get_hooks("scheduler_events", app_name="mscast_erp")
    print(" ", hooks)
except Exception as exc:
    print("  could not read hooks:", exc)
jobs = frappe.get_all("Scheduled Job Type",
                      filters={"method": ["like", "%mscast_erp%"]},
                      fields=["name", "method", "frequency", "cron_format", "stopped"])
print("  registered Scheduled Job Types:")
for j in jobs or []:
    print("    %-60s cron=%s stopped=%s" % (j.method, j.cron_format, j.stopped))
if not jobs:
    print("    NONE - the hook has not been registered into Scheduled Job Type")

print()
print("=" * 70)
print("4. WHO RECEIVES IT")
print("=" * 70)
to = frappe.conf.get("mscast_briefing_to")
print("  mscast_briefing_to :", to or "NOT SET - falls back to the first enabled user")
if not to:
    first = frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"},
                           fields=["email"], limit=1)
    print("  would go to        :", first[0].email if first else "(nobody)")
print("  outgoing account   :", frappe.db.get_value(
    "Email Account", {"default_outgoing": 1}, "name") or "none")

print()
print("=" * 70)
print("5. WHAT YOU CAN OPEN IN THE DESK")
print("=" * 70)
print("  MSCAST Exception rows by status:")
for row in frappe.db.sql("""select status, count(*) n from `tabMSCAST Exception`
                            group by status""", as_dict=True):
    print("    %-14s %d" % (row.status, row.n))
sent = frappe.db.sql("""select q.name, q.status, q.creation, r.recipient
                        from `tabEmail Queue` q
                        left join `tabEmail Queue Recipient` r on r.parent = q.name
                        where q.message like '%%Written by the overnight checks%%'
                        order by q.creation desc limit 5""", as_dict=True)
print("  briefing emails actually sent from this site:")
for e in sent or []:
    print("    %s  %-30s %s" % (e.creation, e.recipient or "?", e.status))
if not sent:
    print("    none - the 08:35 job has never sent one here")
