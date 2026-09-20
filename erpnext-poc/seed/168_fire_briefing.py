# -*- coding: utf-8 -*-
"""Run the 08:35 job exactly as the scheduler will, and show what was sent."""
import frappe, traceback
from mscast_erp.agents import briefing

conf = frappe.conf.get("mscast_briefing_to")
print("mscast_briefing_to  :", repr(conf), "type:", type(conf).__name__)

data = briefing.collect()
print("exceptions on hand  :", len(data["exceptions"]))

before = frappe.db.sql("select ifnull(max(creation),'2000-01-01') from `tabEmail Queue`")[0][0]
print()
print("calling daily_briefing() ...")
try:
    briefing.daily_briefing()
    frappe.db.commit()
except Exception:
    traceback.print_exc()

rows = frappe.db.sql("""select q.status, q.creation, r.recipient
                        from `tabEmail Queue` q
                        left join `tabEmail Queue Recipient` r on r.parent = q.name
                        where q.creation > %s order by q.creation desc""",
                     (before,), as_dict=True)
print()
print("queued by this run:")
for e in rows or []:
    print("   %s  %-30s %s" % (e.creation, e.recipient or "?", e.status))
if not rows:
    print("   nothing queued")
    print()
    print("recent errors logged:")
    for l in frappe.get_all("Error Log", fields=["method", "creation"],
                            order_by="creation desc", limit=5):
        print("   %s  %s" % (l.creation, (l.method or "")[:70]))
