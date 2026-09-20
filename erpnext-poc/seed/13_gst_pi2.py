"""MSCAST POC - 13: correct HSN for casting machines + input-GST purchase invoice (state-aware)."""
import frappe
from frappe.utils import add_days, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[seed-13] " + m, flush=True)


def pick_hsn(*prefixes):
    for p in prefixes:
        rows = frappe.db.sql(
            """select name from `tabGST HSN Code`
               where name like %s and char_length(name) in (6, 8)
               order by char_length(name), name""", (p + "%",), as_dict=True)
        if rows:
            return rows[0].name
    return None


def fix_hsn():
    m = pick_hsn("845430", "8454")
    for code in ("CCM-2S-130", "ALBC-7"):
        if frappe.db.exists("Item", code) and m:
            it = frappe.get_doc("Item", code)
            it.gst_hsn_code = m
            it.flags.ignore_permissions = True
            it.flags.ignore_mandatory = True
            it.save()
    log("casting machine HSN -> %s" % m)
    frappe.db.commit()


def purchase_invoice():
    supplier = "Suvarna Copper Moulds (DEMO)"
    if frappe.db.exists("Purchase Invoice", {"supplier": supplier, "docstatus": 1}):
        log("already exists")
        return
    comp_addr = frappe.db.get_value("Address", {"is_your_company_address": 1}, "name")
    sup_addr = frappe.db.get_value("Address", {"address_title": supplier, "address_type": "Billing"}, "name")
    comp_gstin = frappe.db.get_value("Address", comp_addr, "gstin") or ""
    sup_gstin = frappe.db.get_value("Address", sup_addr, "gstin") or ""
    inter_state = comp_gstin[:2] != sup_gstin[:2]
    template = ("Input GST Out-state - " if inter_state else "Input GST In-state - ") + ABBR
    log("supplier %s vs company %s -> %s" % (sup_gstin[:2], comp_gstin[:2], template))

    pr = frappe.db.get_value("Purchase Receipt", {"supplier": supplier, "docstatus": 1}, "name")
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = supplier
    pi.company = COMPANY
    pi.set_posting_time = 1
    pi.posting_date = add_days(TODAY, -8)
    pi.bill_no = "SCM/26-27/0471"
    pi.bill_date = add_days(TODAY, -9)
    pi.billing_address = comp_addr
    pi.shipping_address = comp_addr
    pi.supplier_address = sup_addr
    pi.tax_category = "Out-State" if inter_state else "In-State"
    if pr:
        prd = frappe.get_doc("Purchase Receipt", pr)
        for it in prd.items:
            pi.append("items", {"item_code": it.item_code, "qty": it.qty, "rate": it.rate,
                                "warehouse": it.warehouse, "project": it.project,
                                "purchase_receipt": prd.name, "pr_detail": it.name})
    else:
        pi.append("items", {"item_code": "BO-MOULD-TUBE", "qty": 4, "rate": 192000,
                            "warehouse": "Stores - " + ABBR})
    pi.taxes_and_charges = template
    for t in frappe.get_doc("Purchase Taxes and Charges Template", template).taxes:
        pi.append("taxes", {"charge_type": t.charge_type, "account_head": t.account_head,
                            "category": t.category, "add_deduct_tax": t.add_deduct_tax,
                            "description": t.description, "rate": t.rate,
                            "cost_center": t.cost_center})
    pi.remarks = "Copper mould tubes and withdrawal rolls - certified through BRM"
    pi.flags.ignore_permissions = True
    pi.insert()
    pi.submit()
    log("purchase invoice %s total=%s place_of_supply=%s" % (pi.name, pi.grand_total, pi.place_of_supply))
    brm = frappe.db.get_value("MSCAST BRM", {"supplier": supplier}, "name")
    if brm:
        frappe.db.set_value("MSCAST BRM", brm, "status", "Paid")
    frappe.db.commit()


try:
    fix_hsn()
except Exception as e:
    log("hsn fix failed: " + repr(e)[:200])
try:
    purchase_invoice()
except Exception as e:
    frappe.db.rollback()
    log("PI failed: " + repr(e)[:400])
log("DONE")
