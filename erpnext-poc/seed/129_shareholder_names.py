import frappe

RENAME = {
    "Mustaque Ahmed N. Chandankeri": "Promoter A (DEMO)",
    "Aiqaz M. Chandankeri": "Promoter B (DEMO)",
    "Zameer Alam Chandankeri": "Promoter C (DEMO)",
}

print("before:")
for s in frappe.get_all("Shareholder", fields=["name", "title", "folio_no"]):
    print("   ", s.name, "|", s.title, "|", s.folio_no)

for s in frappe.get_all("Shareholder", fields=["name", "title"]):
    new = RENAME.get((s.title or "").strip())
    if new:
        frappe.db.set_value("Shareholder", s.name, "title", new, update_modified=False)
        print("retitled", s.name, ":", s.title, "->", new)

# the contact/party name may also carry it
for dt, field in [("Shareholder", "title")]:
    pass

frappe.db.commit()
frappe.clear_cache()
print()
print("after:")
for s in frappe.get_all("Shareholder", fields=["name", "title"]):
    bal = frappe.get_all("Share Balance", filters={"parent": s.name}, fields=["no_of_shares", "amount"])
    print("   ", s.name, "|", s.title, "|", bal)

# the demo watermark does not belong on the stock 1099 form
css = frappe.db.get_value("Print Format", "IRS 1099 Form", "css") or ""
if "demo watermark" in css:
    frappe.db.set_value("Print Format", "IRS 1099 Form", "css",
                        css.split("\n/* demo watermark")[0], update_modified=False)
    print("\nreverted watermark on IRS 1099 Form (not an MSCAST format)")
frappe.db.commit()
