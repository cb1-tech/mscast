# DEV instance marker - run ONLY on the dev site (mscastdev.carobar.net).
# Makes it impossible to confuse dev with the live POC: browser tab / login
# title and a banner across the top of every desk page.
host = frappe.conf.get("host_name") or ""
assert "mscastdev" in host, "refusing: this is not the dev site (host_name=%r)" % host

ss = frappe.get_single("System Settings")
if ss.meta.has_field("app_name"):
    frappe.db.set_single_value("System Settings", "app_name", "MSCAST ERP - DEV")
    print("app_name -> MSCAST ERP - DEV")

ns = frappe.get_meta("Navbar Settings")
if ns.has_field("announcement_widget"):
    frappe.db.set_single_value("Navbar Settings", "announcement_widget",
        '<div style="background:#b45309;color:#fff;padding:6px 12px;font-weight:bold;text-align:center">'
        'DEV INSTANCE - mscastdev.carobar.net - for testing only, not the live POC</div>')
    print("desk banner set")
else:
    print("Navbar Settings has no announcement_widget in this version - banner skipped")
frappe.clear_cache()
