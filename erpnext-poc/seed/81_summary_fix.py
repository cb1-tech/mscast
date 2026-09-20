"""MSCAST POC - 81: %-free date expression in the summary, then send the corrected report."""
import frappe
log = lambda m: print("[sum3] " + m, flush=True)
NAME = "MSCAST Daily Management Summary"
INBOX = "autoelectron.jp@gmail.com"

d = frappe.get_doc("Report", NAME)
old = "date_format(curdate(), '%%d %%b %%Y') as txt"
new = ("concat(lpad(day(curdate()),2,'0'), ' ', left(monthname(curdate()),3), ' ', "
       "year(curdate())) as txt")
if old in d.query:
    d.query = d.query.replace(old, new)
    d.flags.ignore_permissions = True
    d.save()
    frappe.db.commit()
    log("date expression replaced")
else:
    log("pattern not found - query already fixed?")

rows = frappe.db.sql(d.query)
log("row 1 now: %s" % (rows[0],))
alerts = [r for r in rows if r[3] and r[3].startswith(("ACT", "WATCH"))]
log("%d rows, %d flagged (%d ACT)" % (len(rows), len(alerts),
                                      len([r for r in alerts if r[3].startswith("ACT")])))

frappe.get_doc("Auto Email Report", NAME).send()
frappe.db.commit()
log("corrected summary enqueued to %s" % INBOX)
log("DONE")
