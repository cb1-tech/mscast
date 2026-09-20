import frappe
m = frappe.get_meta("User")
flds = [f.fieldname for f in m.fields if "workspace" in (f.fieldname or "").lower() or "default_app" in (f.fieldname or "")]
print("User fields about workspaces/app:", flds)
print("desktop:home_page default =", frappe.db.get_default("desktop:home_page"))

if "default_workspace" in flds:
    for u in frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"}, fields=["name"]):
        frappe.db.set_value("User", u.name, "default_workspace", "MSCAST", update_modified=False)
        print("  default workspace set for", u.name)

if "default_app" in flds:
    for u in frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"}, fields=["name"]):
        frappe.db.set_value("User", u.name, "default_app", "frappe", update_modified=False)

frappe.db.set_default("desktop:home_page", "workspace")
print("desktop:home_page now =", frappe.db.get_default("desktop:home_page"))
frappe.db.commit()
frappe.clear_cache()
print("caches cleared")
