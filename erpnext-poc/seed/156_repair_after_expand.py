# -*- coding: utf-8 -*-
"""Repair what the data expansion and the user rework broke."""
import frappe

# ---------------------------------------------------- 1. dead notification recipients
NEW = {
    "MSCAST drawing awaiting customer approval": ["latookaushik@hotmail.com", "autoelectron.jp@gmail.com"],
    "MSCAST PO over PCC": ["uattech@carobar.net", "latookaushik@yahoo.com"],
    "MSCAST BG expiry alert": ["carobar.tradecars@gmail.com", "latookaushik@yahoo.com"],
}
print("1. notifications pointing at retired logins")
for name, recipients in NEW.items():
    if not frappe.db.exists("Notification", name):
        continue
    n = frappe.get_doc("Notification", name)
    n.set("recipients", [])
    for r in recipients:
        if frappe.db.exists("User", r):
            n.append("recipients", {"receiver_by_document_field": None, "email_by_document_field": None})
            n.recipients[-1].receiver_by_role = None
            n.recipients[-1].email_by_role = None
            n.recipients[-1].receiver_by_document_field = None
            # plain address
            if n.meta.get_field("recipients") and frappe.get_meta("Notification Recipient").has_field("email_id"):
                n.recipients[-1].email_id = r
    n.flags.ignore_permissions = True
    n.save()
    live = [x.get("email_id") for x in n.recipients]
    print("   %-44s -> %s" % (name, ", ".join([l for l in live if l])))

# ------------------------------------------------------- 2. ledger without a cost centre
print()
print("2. ledger entries with no cost centre")
rows = frappe.db.sql("""select name, voucher_type, voucher_no, account, debit, credit
    from `tabGL Entry` where is_cancelled = 0 and ifnull(cost_center,'') = ''""", as_dict=True)
default_cc = frappe.db.get_value("Company", frappe.defaults.get_global_default("company"), "cost_center")
for r in rows:
    print("   ", r.voucher_type, r.voucher_no, "|", r.account, "| dr", r.debit, "cr", r.credit)
    frappe.db.set_value("GL Entry", r.name, "cost_center", default_cc, update_modified=False)
if rows:
    print("   set cost centre %s on %d entr%s" % (default_cc, len(rows), "y" if len(rows) == 1 else "ies"))
else:
    print("   none")

# --------------------------------------- 3. keep the payment control demonstrable
# Certifying the Shivneri BRM left no uncertified supplier bill, so the block
# had nothing to refuse. A new bill from a new supplier restores the case.
print()
print("3. an uncertified supplier bill, so the payment block still has something to refuse")
sup = "Ashoka Heavy Fabricators (DEMO)"
if frappe.db.exists("Supplier", sup) and not frappe.db.exists("Purchase Invoice", {"supplier": sup, "docstatus": 1}):
    company = frappe.defaults.get_global_default("company")
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = sup
    pi.company = company
    pi.posting_date = "2026-09-16"
    pi.set_posting_time = 1
    pi.bill_no = "AHF/2026/0341"
    pi.bill_date = "2026-09-16"
    pi.due_date = "2026-10-31"
    pi.project = "PROJ-0002"
    pi.append("items", {
        "item_code": "MS-PLATE-20",
        "qty": 4200,
        "rate": 68,
        "project": "PROJ-0002",
    })
    pi.flags.ignore_permissions = True
    pi.insert()
    pi.submit()
    print("   %s from %s for %s - no BRM raised against it" % (pi.name, sup, pi.grand_total))
else:
    print("   already present")

frappe.db.commit()

# ------------------------------------------------------------------- verify
print()
print("=== after repair ===")
print("GL entries without a cost centre:", frappe.db.sql("""select count(*) from `tabGL Entry`
    where is_cancelled = 0 and ifnull(cost_center,'') = ''""")[0][0])
dead = []
for n in frappe.get_all("Notification", filters={"enabled": 1}, fields=["name"]):
    doc = frappe.get_doc("Notification", n.name)
    live = False
    for r in doc.recipients:
        addr = r.get("email_id")
        if addr and frappe.db.get_value("User", addr, "enabled"):
            live = True
        if r.get("receiver_by_role") or r.get("receiver_by_document_field"):
            live = True
    if not live:
        dead.append(n.name)
print("notifications with no live recipient:", dead or "none")
print("uncertified supplier bills:", frappe.db.sql("""select pi.name, pi.supplier, pi.outstanding_amount
    from `tabPurchase Invoice` pi where pi.docstatus=1 and pi.outstanding_amount>0
      and not exists (select 1 from `tabMSCAST BRM` b where b.supplier=pi.supplier
                      and b.status in ('Certified','Paid'))""", as_dict=True))
