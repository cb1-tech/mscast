# -*- coding: utf-8 -*-
"""Make MSCAST Exception an app doctype on this site, as it is in the package.

127_exception_engine creates it with frappe.get_doc({...custom: 1...}) because
that was the quickest way to get the exception sweep working. The app then also
ships it as a real doctype under mscast/doctype/mscast_exception/. Two sources
for one form, and this site was running the custom one.

That matters beyond tidiness. A doctype with custom=1 never has its controller
imported - frappe returns a plain Document and stops. That is precisely what
hid the wrong controller class names on all 26 doctypes until the app was
installed and the flag flipped. Leaving one doctype on the custom path means
one doctype whose controller is never exercised, on a site that is supposed to
match what a clean build produces.

Aligning it means the POC and a clean build agree.
"""
import frappe

NAME = "MSCAST Exception"
row = frappe.db.get_value("DocType", NAME, ["module", "custom"], as_dict=True)
print("before: module=%s custom=%s" % (row.module, row.custom))

if row.module != "MSCAST" or row.custom:
    frappe.db.set_value("DocType", NAME, {"module": "MSCAST", "custom": 0},
                        update_modified=False)
    frappe.db.commit()
    frappe.clear_cache(doctype=NAME)
    after = frappe.db.get_value("DocType", NAME, ["module", "custom"], as_dict=True)
    print("after : module=%s custom=%s" % (after.module, after.custom))
else:
    print("already aligned")

print()
print("controller now resolves to:")
from frappe.model.base_document import get_controller
print("  ", get_controller(NAME))

print()
print("rows still readable:", frappe.db.count(NAME))
print("open right now     :", frappe.db.count(NAME, {"status": ["in", ["Open", "Acknowledged"]]}))
