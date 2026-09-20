import frappe, json
q = frappe.db.get_value("Report", "MSCAST Daily Management Summary", "query")
for seg in q.split("union all"):
    if "Orders in hand" in seg or "Retention held" in seg:
        print("---- SEGMENT ----")
        print(seg.strip()[:700])
        print()
print("=== DN-26-00001 ===")
dn = frappe.get_doc("Delivery Note", "DN-26-00001")
print(" customer:", dn.customer, "| total:", dn.grand_total, "| posting:", dn.posting_date)
for it in dn.items:
    print("   item:", it.item_code, it.qty, it.rate, "| against SO:", it.against_sales_order, "| project:", it.project)
print()
print("=== SO-1 items ===")
so = frappe.get_doc("Sales Order", "SAL-ORD-2026-00001")
print(" customer:", so.customer, "| total:", so.grand_total)
for it in so.items:
    print("   ", it.item_code, "qty", it.qty, "rate", it.rate, "delivered", it.delivered_qty)
print()
print("=== Konark invoice ===")
print(frappe.db.sql("""select name, customer, grand_total, outstanding_amount, posting_date
    from `tabSales Invoice` where customer like 'Konark%%'""", as_dict=True))
print()
print("=== retention fields on SO ===")
print([f.fieldname for f in frappe.get_meta("Sales Order").fields if "retention" in (f.fieldname or "").lower() or "pbg" in (f.fieldname or "").lower()])
print(" SO-1:", frappe.db.get_value("Sales Order","SAL-ORD-2026-00001", ["custom_retention_percent","custom_pbg_percent"], as_dict=True) if frappe.db.has_column("Sales Order","custom_retention_percent") else "n/a")
