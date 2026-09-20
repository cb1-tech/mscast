# -*- coding: utf-8 -*-
"""Why did the workflow roles revert? Compare the database against the file."""
import frappe, json, os

path = "/home/frappe/frappe-bench/apps/mscast_erp/mscast_erp/fixtures/workflow.json"
print("app fixture file:", path, "exists:", os.path.exists(path))
if os.path.exists(path):
    for wf in json.load(open(path)):
        print("\n  FILE  %s   modified=%s" % (wf.get("name"), wf.get("modified")))
        for t in wf.get("transitions", []):
            print("        %-24s %s" % (t.get("action"), t.get("allowed")))

print()
print("=" * 70)
for name in ["MSCAST PCC Approval", "MSCAST BRM Certification"]:
    m = frappe.db.get_value("Workflow", name, "modified")
    print("  DB    %-30s modified=%s" % (name, m))

print()
print("versions recorded against these workflows (most recent first):")
for v in frappe.get_all("Version",
                        filters={"ref_doctype": "Workflow"},
                        fields=["docname", "owner", "creation"],
                        order_by="creation desc", limit=8):
    print("   %s  %-30s %s" % (v.creation, v.docname, v.owner))
