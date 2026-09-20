"""MSCAST ERPNext POC - 00: run the ERPNext setup wizard headlessly.

Creates the company, Indian chart of accounts, fiscal year, warehouse types,
UOMs, item groups, territories and all the other ERPNext base fixtures.
"""
import frappe
from frappe.desk.page.setup_wizard.setup_wizard import setup_complete

log = lambda m: print("[seed-00] " + m, flush=True)

if frappe.is_setup_complete():
    log("setup already complete")
else:
    args = {
        "language": "English (United States)",
        "country": "India",
        "timezone": "Asia/Kolkata",
        "currency": "INR",
        "full_name": "MSCAST Admin",
        "email": "admin@mscast.local",
        "password": "admin",
        "company_name": "MSCAST Engineering Pvt Ltd",
        "company_abbr": "MSCAST",
        "company_tagline": "Continuous casting machines & equipment",
        "chart_of_accounts": "Standard with Numbers",
        "fy_start_date": "2026-04-01",
        "fy_end_date": "2027-03-31",
        "bank_account": "HDFC Bank",
        "domains": ["Manufacturing"],
        "setup_demo": 0,
    }
    out = setup_complete(args)
    log("setup_complete -> " + str(out))

frappe.db.commit()
log("company exists: %s" % frappe.db.exists("Company", "MSCAST Engineering Pvt Ltd"))
log("fiscal years: %s" % frappe.get_all("Fiscal Year", pluck="name"))
log("DONE")
