import frappe
for it in ["CCM-2S-130", "SRV-DESIGN", "SRV-ERECTION", "SPR-MOULD-TUBE"]:
    d = frappe.db.get_value("Item", it, ["item_name","is_stock_item","is_fixed_asset","item_group","stock_uom"], as_dict=True)
    qty = frappe.db.sql("select ifnull(sum(actual_qty),0) q from `tabBin` where item_code=%s", (it,))[0][0]
    print("%-16s stock_item=%s group=%-22s on hand=%s | %s" % (it, d.is_stock_item if d else "?", d.item_group if d else "?", qty, d.item_name if d else "MISSING"))
print()
print("warehouses:", [w.name for w in frappe.get_all("Warehouse", filters={"is_group":0}, fields=["name"])])
print()
print("company abbr:", frappe.db.get_value("Company", frappe.defaults.get_global_default("company"), "abbr"))
