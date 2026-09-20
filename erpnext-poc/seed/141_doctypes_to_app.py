# -*- coding: utf-8 -*-
"""Convert the database-resident custom doctypes into real app doctypes.

A custom doctype lives only in the database. Shipped as a fixture it imports a
definition without creating its table, so a fresh site breaks on the first
migrate. An app doctype is a JSON file the framework owns: migrate creates the
table, upgrades keep it, and another Frappe partner can read it in the repo.
"""
import frappe, json, os, re

OUT = "/tmp/mscast_doctypes"
MODULE = "MSCAST"

os.makedirs(OUT, exist_ok=True)
os.system("rm -rf %s/*" % OUT)

STRIP_TOP = {"modified", "modified_by", "creation", "owner", "idx", "docstatus",
             "_user_tags", "_comments", "_assign", "_liked_by", "_user_edits"}
STRIP_ROW = STRIP_TOP | {"parent", "parentfield", "parenttype", "name"}


def snake(name):
    s = re.sub(r"[^a-zA-Z0-9]+", "_", name).strip("_").lower()
    return re.sub(r"_+", "_", s)


def camel(name):
    return "".join(w.capitalize() for w in re.split(r"[^a-zA-Z0-9]+", name) if w)


def clean_row(d):
    return {k: v for k, v in d.items() if k not in STRIP_ROW and v is not None and v != ""}


written = []
for row in frappe.get_all("DocType", filters={"custom": 1}, fields=["name"], order_by="name"):
    doc = frappe.get_doc("DocType", row.name)
    d = doc.as_dict(no_nulls=True)

    for k in list(d.keys()):
        if k in STRIP_TOP:
            d.pop(k, None)

    d["doctype"] = "DocType"
    d["name"] = row.name
    d["custom"] = 0
    d["module"] = MODULE
    d["app"] = "mscast_erp"
    d["is_virtual"] = d.get("is_virtual", 0)

    for table_field in ("fields", "permissions", "actions", "links", "states"):
        if d.get(table_field):
            d[table_field] = [clean_row(r) for r in d[table_field]]

    stem = snake(row.name)
    folder = os.path.join(OUT, stem)
    os.makedirs(folder, exist_ok=True)

    with open(os.path.join(folder, stem + ".json"), "w") as fh:
        json.dump(d, fh, indent=1, sort_keys=True, default=str)

    open(os.path.join(folder, "__init__.py"), "w").close()

    if not d.get("istable"):
        controller = (
            "# Copyright (c) 2026, MSCAST Engineering Pvt Ltd and contributors\n"
            "# For license information, please see license.txt\n\n"
            "from frappe.model.document import Document\n\n\n"
            "class %s(Document):\n\tpass\n" % camel(row.name)
        )
    else:
        controller = (
            "# Copyright (c) 2026, MSCAST Engineering Pvt Ltd and contributors\n"
            "# For license information, please see license.txt\n\n"
            "from frappe.model.document import Document\n\n\n"
            "class %s(Document):\n\tpass\n" % camel(row.name)
        )
    with open(os.path.join(folder, stem + ".py"), "w") as fh:
        fh.write(controller)

    written.append((row.name, stem, "child table" if d.get("istable") else "document",
                    len(d.get("fields") or []), len(d.get("permissions") or [])))

print("converted %d doctypes to app doctypes in module '%s'" % (len(written), MODULE))
for name, stem, kind, nf, np in written:
    print("  %-34s %-12s %2d fields %2d perms  -> mscast/doctype/%s/" % (name, kind, nf, np, stem))
