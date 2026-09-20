# -*- coding: utf-8 -*-
"""B1 - move the BRM payment block out of a Server Script and into the app.

Three things happen here, and the order matters:

  1. The `mscast_brm_exempt` field is created on Supplier. The app control reads
     it, so it has to exist before the control starts refusing payments, or an
     electricity bill has no way out.
  2. The Server Script `MSCAST BRM payment block` is deleted. It guarded one
     door of four and cannot be unit tested; keeping it alongside the app
     control would mean two implementations of one rule, drifting apart.
  3. Caches are cleared, because Frappe holds the doc_events map and the
     Server Script list in memory.

The app control itself is in mscast_erp/controls/brm_payment.py and ships in
the image. This script only prepares the site around it.
"""
import frappe

EXEMPT_FIELD = "mscast_brm_exempt"
OLD_SCRIPT = "MSCAST BRM payment block"


def exemption_field():
    name = "Supplier-" + EXEMPT_FIELD
    if frappe.db.exists("Custom Field", name):
        print("   exemption field already present")
        return
    frappe.get_doc({
        "doctype": "Custom Field",
        "dt": "Supplier",
        "fieldname": EXEMPT_FIELD,
        "label": "Exempt from BRM certification",
        "fieldtype": "Check",
        "insert_after": "capability",
        "default": "0",
        "is_system_generated": 1,
        "description": (
            "Tick only for suppliers whose bills cannot be certified against a "
            "purchase order - electricity, water, rent, telephone, statutory "
            "payments. Every trade supplier must stay unticked: an unticked "
            "supplier cannot be paid without a certified BRM."),
    }).insert(ignore_permissions=True)
    print("   created Custom Field", name)


def retire_server_script():
    if not frappe.db.exists("Server Script", OLD_SCRIPT):
        print("   server script already retired")
        return
    frappe.delete_doc("Server Script", OLD_SCRIPT,
                      force=True, ignore_permissions=True)
    print("   deleted Server Script", OLD_SCRIPT,
          "- the control now lives in mscast_erp.controls.brm_payment")


def report():
    """State the door-by-door position, so the run is self-evidencing."""
    hooks = frappe.get_hooks("doc_events") or {}
    for dt in ("Payment Entry", "Journal Entry"):
        handlers = (hooks.get(dt) or {}).get("before_submit") or []
        handlers = [h for h in handlers if "brm_payment" in h]
        print("   %-16s before_submit -> %s" % (dt, handlers or "NOT WIRED"))
    n = frappe.db.count("Supplier", {EXEMPT_FIELD: 1})
    print("   suppliers marked BRM-exempt: %d of %d"
          % (n, frappe.db.count("Supplier")))


exemption_field()
retire_server_script()
frappe.db.commit()
frappe.clear_cache()
report()
print("187 done")
