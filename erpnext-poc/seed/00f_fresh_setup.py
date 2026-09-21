"""Fresh MSCAST system - complete the ERPNext setup wizard with no demo data.

Used by new-mscast-site.sh. Unlike 00_setup_wizard.py it creates no login: the
demo seed made a user 'admin@mscast.local' with password 'admin', which is fine
for a demonstration and wrong for anything real. On a fresh system the only
account is Administrator, whose password new-mscast-site.sh sets and prints once.

Company, chart of accounts, fiscal year and currency are MSCAST's real ones.
"""
import frappe
from frappe.desk.page.setup_wizard.setup_wizard import setup_complete
from frappe.utils import getdate, nowdate

log = lambda m: print("[fresh-00] " + m, flush=True)

# Indian financial year containing today.
t = getdate(nowdate())
fy_start = "%d-04-01" % (t.year if t.month >= 4 else t.year - 1)
fy_end = "%d-03-31" % (int(fy_start[:4]) + 1)

if frappe.is_setup_complete():
    log("setup already complete")
else:
    setup_complete({
        "language": "English (United States)",
        "country": "India",
        "timezone": "Asia/Kolkata",
        "currency": "INR",
        "full_name": "Administrator",
        "company_name": "MSCAST Engineering Pvt Ltd",
        "company_abbr": "MSCAST",
        "company_tagline": "Continuous casting machines & equipment",
        "chart_of_accounts": "Standard with Numbers",
        "fy_start_date": fy_start,
        "fy_end_date": fy_end,
        "domains": ["Manufacturing"],
        "setup_demo": 0,
    })
frappe.db.commit()
log("company: %s" % frappe.db.exists("Company", "MSCAST Engineering Pvt Ltd"))
log("fiscal year: %s to %s" % (fy_start, fy_end))
log("DONE")
