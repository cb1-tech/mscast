import frappe
rows = frappe.get_all("User", filters={"enabled":1}, fields=["name","email","full_name","unsubscribed","user_type"])
bad = [u for u in rows if u.email and not u.unsubscribed and u.email.split("@")[-1].lower() not in ("carobar.net","gmail.com","example.com") and u.name not in ("Administrator","Guest")]
for u in rows:
    print(" ", u.name, "| unsub", u.unsubscribed, "|", u.user_type)
print("would bounce:", [u.name for u in bad])
for u in bad:
    frappe.db.set_value("User", u.name, "unsubscribed", 1, update_modified=False)
    print("marked unsubscribed:", u.name)
frappe.db.commit()
