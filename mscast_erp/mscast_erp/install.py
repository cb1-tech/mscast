# -*- coding: utf-8 -*-
"""Post-install and post-migrate configuration that cannot travel as a fixture."""

import os

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
    sync_doctypes()
    # The documents were just created in this same request; without clearing the
    # cache the fixtures that hang off them still see the old, empty metadata.
    frappe.clear_cache()
    sync_our_fixtures()
    hide_stock_workspaces()
    set_landing_page()
    frappe.db.commit()


def sync_doctypes():
    """Import this app's document definitions explicitly.

    The framework's own sync does not reliably pick them up on a first install -
    the fixtures that depend on them are then skipped whole-file, which is how a
    clean build ends up missing its workflows, custom fields and workspaces.
    Importing them here makes install-app followed by migrate deterministic.
    """
    from frappe.modules.import_file import import_file_by_path

    base = frappe.get_app_path("mscast_erp", "mscast", "doctype")
    if not os.path.isdir(base):
        return

    created = []
    for folder in sorted(os.listdir(base)):
        path = os.path.join(base, folder, folder + ".json")
        if not os.path.isfile(path):
            continue
        try:
            import_file_by_path(path, force=False, reset_permissions=True)
            created.append(folder)
        except Exception:
            frappe.log_error(frappe.get_traceback(), "mscast_erp: could not import %s" % folder)

    frappe.db.commit()
    print("mscast_erp: %d document definitions synced" % len(created))


def sync_our_fixtures():
    """Import the fixtures row by row, now that the documents exist.

    The framework's own fixture sync abandons a whole file on the first bad row -
    one custom field pointing at a document that did not exist yet silently loses
    all seven hundred of them. This pass imports each record on its own and
    reports what did not land, so a gap is visible instead of silent.
    """
    import json

    base = frappe.get_app_path("mscast_erp", "fixtures")
    if not os.path.isdir(base):
        return

    # Order matters: a workflow needs its states, a custom field needs its document.
    order = [
        "workflow_state.json", "workflow_action_master.json", "role.json",
        "custom_field.json", "property_setter.json", "letter_head.json",
        "print_format.json", "report.json", "server_script.json",
        "client_script.json", "email_template.json", "notification.json",
        "custom_html_block.json", "dashboard_chart.json", "workflow.json",
        "workspace.json",
    ]
    files = order + sorted(f for f in os.listdir(base) if f.endswith(".json") and f not in order)

    total = failed = 0
    problems = []
    for filename in files:
        path = os.path.join(base, filename)
        if not os.path.isfile(path):
            continue
        try:
            records = json.load(open(path))
        except Exception:
            continue

        for record in records:
            doctype = record.get("doctype")
            name = record.get("name")
            if not doctype:
                continue
            try:
                if name and frappe.db.exists(doctype, name):
                    continue
                doc = frappe.get_doc(record)
                doc.flags.ignore_permissions = True
                doc.flags.ignore_mandatory = True
                doc.flags.ignore_links = True
                doc.insert()
                total += 1
            except Exception as e:
                try:
                    frappe.clear_cache(doctype=record.get("dt") or record.get("document_type") or doctype)
                    doc = frappe.get_doc(record)
                    doc.flags.ignore_permissions = True
                    doc.flags.ignore_mandatory = True
                    doc.flags.ignore_links = True
                    doc.insert()
                    total += 1
                except Exception as e2:
                    failed += 1
                    problems.append("%s %s: %s" % (doctype, name, str(e2)[:120]))

    frappe.db.commit()
    print("mscast_erp: %d configuration records imported, %d could not be" % (total, failed))
    if problems:
        frappe.log_error("\n".join(problems[:60]), "mscast_erp: fixtures that did not import")
        for p in problems[:10]:
            print("   could not import:", p)


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
