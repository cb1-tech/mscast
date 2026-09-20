"""MSCAST POC - 12: HSN fallback (6/8 digit) + input-GST purchase invoice with diagnostics."""
import frappe
from frappe.utils import add_days, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[seed-12] " + m, flush=True)


def pick_hsn(prefix):
    rows = frappe.db.sql(
        """select name from `tabGST HSN Code`
           where name like %s and char_length(name) in (6, 8) order by char_length(name), name""",
        (prefix + "%",), as_dict=True)
    return rows[0].name if rows else None


def hsn_fallback():
    tmpl = "GST 18% - " + ABBR
    for code, prefix in {"CCM-2S-130": "8454", "ALBC-7": "8454", "ASM-HYD-POWERPACK": "8412"}.items():
        if not frappe.db.exists("Item", code):
            continue
        hsn = pick_hsn(prefix)
        if not hsn:
            log("no 6/8-digit HSN for prefix " + prefix)
            continue
        it = frappe.get_doc("Item", code)
        it.gst_hsn_code = hsn
        if not it.taxes:
            it.append("taxes", {"item_tax_template": tmpl, "valid_from": "2026-04-01"})
        it.flags.ignore_permissions = True
        it.flags.ignore_mandatory = True
        it.save()
        log("%s -> HSN %s" % (code, hsn))
    frappe.db.commit()


def purchase_invoice():
    supplier = "Suvarna Copper Moulds (DEMO)"
    if frappe.db.exists("Purchase Invoice", {"supplier": supplier, "docstatus": 1}):
        log("purchase invoice already exists")
        return
    comp_addr = frappe.db.get_value("Address", {"is_your_company_address": 1}, "name")
    sup_addr = frappe.db.get_value("Address", {"address_title": supplier, "address_type": "Billing"}, "name")
    log("company address=%s (%s) supplier address=%s (%s)" % (
        comp_addr, frappe.db.get_value("Address", comp_addr, "gstin"),
        sup_addr, frappe.db.get_value("Address", sup_addr, "gstin")))

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
    if pr:
        prd = frappe.get_doc("Purchase Receipt", pr)
        for it in prd.items:
            pi.append("items", {"item_code": it.item_code, "qty": it.qty, "rate": it.rate,
                                "warehouse": it.warehouse, "project": it.project,
                                "purchase_receipt": prd.name, "pr_detail": it.name})
    else:
        pi.append("items", {"item_code": "BO-MOULD-TUBE", "qty": 4, "rate": 192000,
                            "warehouse": "Stores - " + ABBR})
    pi.run_method("set_missing_values")
    log("after set_missing_values: supplier_gstin=%s company_gstin=%s place_of_supply=%s tax_category=%s" % (
        pi.get("supplier_gstin"), pi.get("company_gstin"), pi.get("place_of_supply"), pi.get("tax_category")))

    template = ("Input GST Out-state - " + ABBR) if (pi.get("tax_category") or "").startswith("Out") \
        else ("Input GST In-state - " + ABBR)
    pi.taxes_and_charges = template
    pi.set("taxes", [])
    for t in frappe.get_doc("Purchase Taxes and Charges Template", template).taxes:
        pi.append("taxes", {"charge_type": t.charge_type, "account_head": t.account_head,
                            "category": t.category, "add_deduct_tax": t.add_deduct_tax,
                            "description": t.description, "rate": t.rate,
                            "cost_center": t.cost_center})
    pi.remarks = "Copper mould tubes and withdrawal rolls - certified through BRM"
    pi.flags.ignore_permissions = True
    pi.insert()
    pi.submit()
    log("purchase invoice %s total=%s template=%s" % (pi.name, pi.grand_total, template))
    brm = frappe.db.get_value("MSCAST BRM", {"supplier": supplier}, "name")
    if brm:
        frappe.db.set_value("MSCAST BRM", brm, "status", "Paid")
    frappe.db.commit()


try:
    hsn_fallback()
except Exception as e:
    log("hsn fallback failed: " + repr(e)[:200])
try:
    purchase_invoice()
except Exception as e:
    frappe.db.rollback()
    log("purchase invoice failed: " + repr(e)[:400])
log("DONE")
