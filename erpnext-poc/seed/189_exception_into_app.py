"""MSCAST Exception: hand the live definition over to the app.

On the live site MSCAST Exception was still a database-defined custom doctype
(module Custom, custom=1) - left from before the documents moved into the app.
The app defines it too, but a custom doctype of the same name is never
overwritten by the app's, so any change to it in the package would never have
reached live. Found 21 Sep 2026 because a check counted 26 MSCAST doctypes on a
fresh install and 25 on live.

Checked first: identical 18 fields, types, options and naming, so no data moves.
Idempotent.
"""
import frappe
dt = "MSCAST Exception"
cur = frappe.db.get_value("DocType", dt, ["module", "custom"], as_dict=True)
print("[189] before: module=%s custom=%s records=%d" % (cur.module, cur.custom, frappe.db.count(dt)))
if cur.module != "MSCAST" or cur.custom:
    frappe.db.set_value("DocType", dt, {"module": "MSCAST", "custom": 0}, update_modified=False)
    frappe.db.commit()
    frappe.reload_doc("mscast", "doctype", "mscast_exception", force=True)
    frappe.db.commit()
    frappe.clear_cache(doctype=dt)
cur = frappe.db.get_value("DocType", dt, ["module", "custom"], as_dict=True)
print("[189] after:  module=%s custom=%s records=%d" % (cur.module, cur.custom, frappe.db.count(dt)))
