# -*- coding: utf-8 -*-
"""Export every MSCAST customisation as app fixtures.

Configuration only - no demo data. What comes out of here plus an empty ERPNext
site must reproduce the system.
"""
import frappe, json, os

OUT = "/tmp/mscast_fixtures"
os.makedirs(OUT, exist_ok=True)
for f in os.listdir(OUT):
    os.remove(os.path.join(OUT, f))

STRIP = {"modified", "modified_by", "creation", "owner", "idx", "docstatus",
         "_user_tags", "_comments", "_assign", "_liked_by", "doctype"}

def clean(d):
    if isinstance(d, dict):
        out = {}
        for k, v in d.items():
            if k in STRIP and k != "doctype":
                continue
            if k == "name" or not k.startswith("_"):
                out[k] = clean(v)
        return out
    if isinstance(d, list):
        return [clean(x) for x in d]
    return d

def dump(label, doctype, filters=None, order="name"):
    names = [r.name for r in frappe.get_all(doctype, filters=filters or {}, fields=["name"], order_by=order)]
    rows = []
    for n in names:
        doc = frappe.get_doc(doctype, n)
        d = doc.as_dict(no_nulls=False)
        d["doctype"] = doctype
        rows.append(clean(d))
    path = os.path.join(OUT, "%s.json" % label)
    with open(path, "w") as fh:
        json.dump(rows, fh, indent=1, default=str, sort_keys=True)
    print("  %-26s %3d records" % (label, len(rows)))
    return len(rows)

print("exporting configuration fixtures")
total = 0
total += dump("custom_doctype", "DocType", {"custom": 1})
total += dump("custom_field", "Custom Field", {})
total += dump("property_setter", "Property Setter", {})
total += dump("report", "Report", {"is_standard": "No"})
total += dump("print_format", "Print Format", {"standard": "No"})
total += dump("workflow", "Workflow", {})
total += dump("workflow_state", "Workflow State", {})
total += dump("workflow_action_master", "Workflow Action Master", {})
total += dump("server_script", "Server Script", {})
total += dump("client_script", "Client Script", {})
total += dump("notification", "Notification", {"is_standard": 0})
total += dump("email_template", "Email Template", {})
total += dump("custom_html_block", "Custom HTML Block", {})
total += dump("workspace", "Workspace", {"name": ["like", "MSCAST%"]})
total += dump("role", "Role", {"name": ["like", "MSCAST%"]})
total += dump("letter_head", "Letter Head", {"name": ["like", "MSCAST%"]})
if frappe.db.exists("DocType", "Dashboard Chart"):
    total += dump("dashboard_chart", "Dashboard Chart", {"is_standard": 0})
print("  total:", total, "records")

# the hidden stock workspaces are a configuration decision too
hidden = [w.name for w in frappe.get_all("Workspace", filters={"public": 1, "is_hidden": 1}, fields=["name"])]
with open(os.path.join(OUT, "_hidden_workspaces.json"), "w") as fh:
    json.dump(hidden, fh, indent=1)
print("  hidden workspaces recorded:", len(hidden))
print("\nwritten to", OUT)
