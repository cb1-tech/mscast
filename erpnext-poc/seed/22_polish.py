"""MSCAST POC - 22: final polish (HR settings, default workspace, session defaults)."""
import frappe

log = lambda m: print("[seed-22] " + m, flush=True)

try:
    hr = frappe.get_single("HR Settings")
    if hr.meta.has_field("standard_working_hours"):
        hr.standard_working_hours = 8
    hr.flags.ignore_permissions = True
    hr.save()
    log("HR Settings: standard working hours = 8")
except Exception as e:
    log("HR settings: " + repr(e)[:200])

try:
    n = 0
    for u in frappe.get_all("User", filters={"enabled": 1}, pluck="name"):
        if frappe.db.has_column("User", "default_workspace"):
            frappe.db.set_value("User", u, "default_workspace", "MSCAST")
            n += 1
    log("default workspace set for %d users" % n)
except Exception as e:
    log("default workspace: " + repr(e)[:200])

frappe.db.commit()
frappe.clear_cache()
log("DONE")
