# -*- coding: utf-8 -*-
"""Make the agent run by itself, and send to the right people.

164 found two things that would have stayed quiet:

  1. The 08:35 hook was declared in hooks.py but never registered as a
     Scheduled Job Type, so the scheduler had nothing to fire. The sweep at
     06:00 is a Server Script and had been running; the judgement half had
     only ever been run by hand.

  2. mscast_briefing_to was unset, so send() fell back to "the first enabled
     System User" - which after the user rework is meera.rane@mscast.co.in,
     a draughtsman on a domain that does not receive mail. The director's
     briefing would have been queued to a mailbox nobody reads.
"""
import frappe
from frappe.core.doctype.scheduled_job_type.scheduled_job_type import sync_jobs

print("1. registering the app's scheduled jobs")
if "mscast_erp" not in frappe.get_installed_apps():
    print("   mscast_erp is NOT installed on this site.")
    print("   The app directory exists and is listed in bench apps.txt, but the")
    print("   site has never had it installed, so:")
    print("     - frappe.get_hooks('scheduler_events') does not see its cron")
    print("     - the module is not importable (the test seeds add it to sys.path")
    print("       by hand, which is why running it manually has always worked)")
    print("   Everything else MSCAST works because the seeds wrote doctypes,")
    print("   workflows and Server Scripts straight into the database. Only the")
    print("   judgement half lives in app code, so only it is affected.")
    print()
    print("   Fix, when you want it:  bench --site <site> install-app mscast_erp")
else:
    sync_jobs()
    frappe.db.commit()
for j in frappe.get_all("Scheduled Job Type",
                        filters={"method": ["like", "%mscast_erp%"]},
                        fields=["method", "cron_format", "frequency", "stopped"]):
    print("   %-52s cron=%-12s stopped=%s" % (j.method, j.cron_format, j.stopped))

print()
print("2. pointing the briefing at the directors")
DIRECTORS = ["latookaushik@yahoo.com", "latookaushik@hotmail.com"]
live = []
for email in DIRECTORS:
    row = frappe.db.get_value("User", email, ["enabled", "full_name", "unsubscribed"],
                              as_dict=True)
    if not row:
        print("   %-28s NOT A USER - skipped" % email)
        continue
    if row.unsubscribed:
        # a briefing that lands in an unsubscribed mailbox is silently dropped
        frappe.db.set_value("User", email, "unsubscribed", 0)
        print("   %-28s %s (was unsubscribed - re-subscribed)" % (email, row.full_name))
    else:
        print("   %-28s %s" % (email, row.full_name))
    live.append(email)

if live:
    frappe.db.commit()
    print()
    print("   set this, outside the repo:")
    print("     bench --site <site> set-config mscast_briefing_to '%s'"
          % frappe.as_json(live))
else:
    print("   no director mailbox is live - leaving the fallback alone")
