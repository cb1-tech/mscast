# -*- coding: utf-8 -*-
"""The app ships 26 doctype folders but only 25 sit in the MSCAST module. Which?"""
import frappe, os

root = "/home/frappe/frappe-bench/apps/mscast_erp/mscast_erp/mscast/doctype"
folders = {d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d))}
print("folders shipped:", len(folders))

in_module = {frappe.scrub(n) for n in
             frappe.get_all("DocType", filters={"module": "MSCAST"}, pluck="name")}
print("in MSCAST module:", len(in_module))

for stem in sorted(folders - in_module):
    name = frappe.db.get_value("DocType", {"name": ["like", "%"]}, "name")  # placeholder
    row = frappe.db.sql("""select name, module, custom from `tabDocType`
                           where replace(lower(name),' ','_') = %s""", (stem,), as_dict=True)
    print("  shipped but not in module: %-32s -> %s" % (stem, row or "NOT IN DATABASE AT ALL"))
for stem in sorted(in_module - folders):
    print("  in module but not shipped: %s" % stem)
