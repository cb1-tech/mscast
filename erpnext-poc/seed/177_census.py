# -*- coding: utf-8 -*-
"""One authoritative count of everything the documents quote numbers for."""
import frappe

print("doctypes (MSCAST module) :", frappe.db.count("DocType", {"module": "MSCAST"}))
print("  of which child tables  :", frappe.db.count("DocType", {"module": "MSCAST", "istable": 1}))
print("workflows                :", frappe.db.count("Workflow"))
for w in frappe.get_all("Workflow", fields=["name", "document_type", "is_active"]):
    print("     %-34s %-28s active=%s" % (w.name, w.document_type, w.is_active))
print("custom reports           :", frappe.db.count("Report", {"is_standard": "No"}))
print("print formats (custom)   :", frappe.db.count("Print Format", {"standard": "No"}))
print("server scripts           :", frappe.db.count("Server Script"))
print("notifications (enabled)  :", frappe.db.count("Notification", {"enabled": 1}))
print("email templates          :", frappe.db.count("Email Template"))
print("workspaces (MSCAST)      :", frappe.db.count("Workspace", {"name": ["like", "MSCAST%"]}))
print("dashboard charts         :", frappe.db.count("Dashboard Chart"))
print("roles (MSCAST-specific)  :", frappe.db.count("Role", {"name": ["like", "MSCAST%"]}))
print()
print("exception rules          : see 127_exception_engine (X01-X16)")
print("open exceptions now      :", frappe.db.count("MSCAST Exception",
                                                    {"status": ["in", ["Open", "Acknowledged"]]}))
print()
print("demo volume:")
for dt in ["Project", "Sales Order", "Sales Invoice", "Purchase Order", "Purchase Invoice",
           "Delivery Note", "Customer", "Supplier", "Item", "Employee",
           "MSCAST Installed Machine", "MSCAST Bid Outcome", "MSCAST Drawing",
           "MSCAST PCC", "MSCAST BRM"]:
    if frappe.db.exists("DocType", dt):
        print("   %-28s %d" % (dt, frappe.db.count(dt)))
print()
print("enabled staff logins     :", frappe.db.count(
    "User", {"enabled": 1, "user_type": "System User"}) - 1, "(excluding Administrator)")
print()
print("versions:")
for app in ["frappe", "erpnext", "india_compliance", "hrms", "india_payroll", "mscast_erp"]:
    try:
        print("   %-20s %s" % (app, frappe.get_attr(app + ".__version__")))
    except Exception:
        print("   %-20s ?" % app)
