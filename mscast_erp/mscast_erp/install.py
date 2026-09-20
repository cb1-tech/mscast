# -*- coding: utf-8 -*-
"""Post-install and post-migrate configuration that cannot travel as a fixture."""

import frappe

# Every stock workspace MSCAST does not use. Hidden, never deleted - each form
# and report behind them still opens from search or a direct link.
HIDE = [
    "Welcome Workspace", "Home", "Build", "CRM", "Selling", "Buying", "Stock",
    "Manufacturing", "Subcontracting", "Quality", "Projects", "Assets", "Support",
    "Invoicing", "Financial Reports", "GST India", "Income Tax India", "HR Setup",
    "Tenure", "Recruitment", "Shift & Attendance", "Leaves", "Expenses",
    "Performance", "Payroll", "India Payroll", "Tax & Benefits", "Users",
    "Website", "Integrations", "ERPNext Settings",
]

LANDING = "MSCAST"


def after_install():
    configure()


def after_migrate():
    configure()


def configure():
    """Idempotent. Safe to run on every migrate."""
    hide_stock_workspaces()
    set_landing_page()
    frappe.db.commit()


def hide_stock_workspaces():
    for name in HIDE:
        if frappe.db.exists("Workspace", name):
            frappe.db.set_value("Workspace", name, "is_hidden", 1, update_modified=False)


def set_landing_page():
    """The desk's empty route falls back to a legacy page, so point users and
    the site root at the MSCAST home workspace explicitly."""
    if not frappe.db.exists("Workspace", LANDING):
        return

    for user in frappe.get_all(
        "User", filters={"enabled": 1, "user_type": "System User"}, pluck="name"
    ):
        frappe.db.set_value("User", user, "default_workspace", LANDING, update_modified=False)

    target = "/desk/" + frappe.utils.slug(LANDING)
    ws = frappe.get_doc("Website Settings")
    keep = [
        (r.source, r.target)
        for r in (ws.get("route_redirects") or [])
        if r.source not in ("/", "/desk", "/app")
    ]
    ws.set("route_redirects", [])
    for source, tgt in keep:
        ws.append("route_redirects", {"source": source, "target": tgt})
    for source in ["/", "/desk", "/app"]:
        ws.append("route_redirects", {"source": source, "target": target})
    ws.flags.ignore_mandatory = True
    ws.save(ignore_permissions=True)
