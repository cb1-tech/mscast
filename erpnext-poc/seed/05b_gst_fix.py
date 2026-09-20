"""MSCAST ERPNext POC - 05b: fix demo GSTINs (valid check digit), HSN fallback, GST documents."""
import frappe
from frappe.utils import add_days, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[seed-05b] " + m, flush=True)
CHARS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def step(name, fn, *a, **kw):
    try:
        out = fn(*a, **kw)
        frappe.db.commit()
        log("OK   " + name + ((" -> " + str(out)) if out else ""))
        return out or True
    except Exception as e:
        frappe.db.rollback()
        log("FAIL " + name + " :: " + repr(e)[:300])
        return None


def gstin_check_digit(first14):
    total = 0
    for i, c in enumerate(first14):
        v = CHARS.index(c)
        f = 2 if (i % 2) else 1
        p = v * f
        total += p // 36 + p % 36
    return CHARS[(36 - total % 36) % 36]


def gstin(state_code, pan10, entity="1"):
    base = "%s%s%sZ" % (state_code, pan10, entity)
    return base + gstin_check_digit(base)


# party -> (address line, city, state, pin, country, state_code, pan)
PARTIES = {
    "Sahyadri Steels Ltd (DEMO)": ("Plot 14, MIDC Hingna", "Nagpur", "Maharashtra", "440016", "India", "27", "AAACS1111A"),
    "Konark Alloys Pvt Ltd (DEMO)": ("Industrial Estate, Kalunga", "Rourkela", "Odisha", "769014", "India", "21", "AAACK2222B"),
    "Deccan Extrusions Pvt Ltd (DEMO)": ("Survey 88, Jeedimetla", "Hyderabad", "Telangana", "500055", "India", "36", "AAACD3333C"),
    "Narmada Ispat Pvt Ltd (DEMO)": ("Sector C, Sanwer Road", "Indore", "Madhya Pradesh", "452015", "India", "23", "AAACN4444D"),
    "Gulf Aluminium Industries LLC (DEMO)": ("Industrial Area 12", "Sharjah", "", "", "United Arab Emirates", None, None),
    "Pushkar Fabricators (DEMO)": ("Gat 220, Shikrapur", "Pune", "Maharashtra", "412208", "India", "27", "AAAFP5555E"),
    "Shivneri Machining Works (DEMO)": ("Bhosari MIDC", "Pune", "Maharashtra", "411026", "India", "27", "AAAFS6666F"),
    "Kalyani Gears & Drives (DEMO)": ("Chakan MIDC Phase II", "Pune", "Maharashtra", "410501", "India", "27", "AAACK7777G"),
    "Hydropower Systems (DEMO)": ("Plot 7, Waluj MIDC", "Chhatrapati Sambhajinagar", "Maharashtra", "431136", "India", "27", "AAACH8888H"),
    "Suvarna Copper Moulds (DEMO)": ("GIDC Estate, Vatva", "Ahmedabad", "Gujarat", "382445", "India", "24", "AAACS9999I"),
    "Pune Electrical Panels (DEMO)": ("Bhosari MIDC", "Pune", "Maharashtra", "411026", "India", "27", "AAACP1010J"),
    "Bharat Steel Traders (DEMO)": ("Bhavani Peth", "Pune", "Maharashtra", "411042", "India", "27", "AAACB1111K"),
    "Vidarbha Heavy Transport (DEMO)": ("Transport Nagar", "Nagpur", "Maharashtra", "440027", "India", "27", "AAACV1212L"),
    "Precision Inspection Services (DEMO)": ("Kothrud", "Pune", "Maharashtra", "411038", "India", "27", "AAACP1313M"),
    "Sunrise Cooling Towers (DEMO)": ("Peenya Industrial Area", "Bengaluru", "Karnataka", "560058", "India", "29", "AAACS1414N"),
}


def parties():
    n = 0
    for party, (l1, city, state, pin, country, sc, pan) in PARTIES.items():
        gst = gstin(sc, pan) if sc else ""
        cat = "Registered Regular" if gst else "Overseas"
        for dt in ("Customer", "Supplier"):
            if not frappe.db.exists(dt, party):
                continue
            frappe.db.set_value(dt, party, "gst_category", cat)
            if gst:
                frappe.db.set_value(dt, party, "gstin", gst)
            if frappe.db.exists("Address", {"address_title": party, "address_type": "Billing"}):
                continue
            doc = {
                "doctype": "Address", "address_title": party, "address_type": "Billing",
                "address_line1": l1, "city": city, "pincode": pin, "country": country,
                "is_primary_address": 1, "is_shipping_address": 1, "gst_category": cat,
                "links": [{"link_doctype": dt, "link_name": party}],
            }
            if gst:
                doc["state"] = state
                doc["gstin"] = gst
            d = frappe.get_doc(doc)
            d.flags.ignore_permissions = True
            d.insert()
            n += 1
    log("addresses created: %d" % n)


def hsn_fallback():
    """Some 8-digit HSNs are not in the master; fall back to a code that exists."""
    fixes = {"CCM-2S-130": "8454", "ALBC-7": "8454", "ASM-HYD-POWERPACK": "8412"}
    tmpl = "GST 18% - " + ABBR
    for code, prefix in fixes.items():
        if not frappe.db.exists("Item", code):
            continue
        hsn = frappe.db.get_value("GST HSN Code", {"name": ("like", prefix + "%")}, "name",
                                  order_by="name asc")
        if not hsn:
            log("no HSN starting with %s" % prefix)
            continue
        it = frappe.get_doc("Item", code)
        it.gst_hsn_code = hsn
        if not it.taxes:
            it.append("taxes", {"item_tax_template": tmpl, "valid_from": "2026-04-01"})
        it.flags.ignore_permissions = True
        it.flags.ignore_mandatory = True
        it.save()
        log("%s -> HSN %s" % (code, hsn))


def company_address_name():
    return frappe.db.get_value("Address", {"address_title": ("like", "MSCAST%"),
                                           "is_your_company_address": 1}, "name")


def party_address(party):
    return frappe.db.get_value("Address", {"address_title": party, "address_type": "Billing"}, "name")


def sales_invoices():
    made = []
    cases = [
        ("Sahyadri Steels Ltd (DEMO)", "Output GST In-state - " + ABBR, "SPR-ROLL", 2, 64000,
         "Spare withdrawal rolls against AMC - intra-state supply (CGST + SGST)"),
        ("Konark Alloys Pvt Ltd (DEMO)", "Output GST Out-state - " + ABBR, "SPR-MOULD-TUBE", 8, 192000,
         "Spare copper mould tubes - inter-state supply (IGST)"),
    ]
    for customer, tax_template, item, qty, rate, remark in cases:
        if frappe.db.exists("Sales Invoice", {"customer": customer, "remarks": remark, "docstatus": 1}):
            continue
        si = frappe.new_doc("Sales Invoice")
        si.customer = customer
        si.company = COMPANY
        si.set_posting_time = 1
        si.posting_date = add_days(TODAY, -4)
        si.due_date = add_days(TODAY, 26)
        si.company_address = company_address_name()
        si.customer_address = party_address(customer)
        si.shipping_address_name = si.customer_address
        si.taxes_and_charges = tax_template
        si.remarks = remark
        si.append("items", {"item_code": item, "qty": qty, "rate": rate, "conversion_factor": 1})
        for t in frappe.get_doc("Sales Taxes and Charges Template", tax_template).taxes:
            si.append("taxes", {"charge_type": t.charge_type, "account_head": t.account_head,
                                "description": t.description, "rate": t.rate,
                                "cost_center": t.cost_center})
        si.flags.ignore_permissions = True
        si.insert()
        si.submit()
        made.append("%s: %s (%s)" % (si.name, si.grand_total, si.place_of_supply))
    return " | ".join(made)


def purchase_invoice():
    supplier = "Suvarna Copper Moulds (DEMO)"
    if frappe.db.exists("Purchase Invoice", {"supplier": supplier, "docstatus": 1}):
        return
    tax_template = "Input GST Out-state - " + ABBR
    pr = frappe.db.get_value("Purchase Receipt", {"supplier": supplier, "docstatus": 1}, "name")
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = supplier
    pi.company = COMPANY
    pi.set_posting_time = 1
    pi.posting_date = add_days(TODAY, -8)
    pi.bill_no = "SCM/26-27/0471"
    pi.bill_date = add_days(TODAY, -9)
    pi.company_address = company_address_name()
    pi.supplier_address = party_address(supplier)
    pi.taxes_and_charges = tax_template
    pi.remarks = "Copper mould tubes and withdrawal rolls - certified through BRM-2026-00001"
    if pr:
        prd = frappe.get_doc("Purchase Receipt", pr)
        for it in prd.items:
            pi.append("items", {"item_code": it.item_code, "qty": it.qty, "rate": it.rate,
                                "warehouse": it.warehouse, "project": it.project,
                                "purchase_receipt": prd.name, "pr_detail": it.name})
    else:
        pi.append("items", {"item_code": "BO-MOULD-TUBE", "qty": 4, "rate": 192000,
                            "warehouse": "Stores - " + ABBR})
    for t in frappe.get_doc("Purchase Taxes and Charges Template", tax_template).taxes:
        pi.append("taxes", {"charge_type": t.charge_type, "account_head": t.account_head,
                            "category": t.category, "add_deduct_tax": t.add_deduct_tax,
                            "description": t.description, "rate": t.rate,
                            "cost_center": t.cost_center})
    pi.flags.ignore_permissions = True
    pi.insert()
    pi.submit()
    # mark the BRM as paid-ready
    brm = frappe.db.get_value("MSCAST BRM", {"supplier": supplier}, "name")
    if brm:
        frappe.db.set_value("MSCAST BRM", brm, "status", "Paid")
    return "%s: %s (%s)" % (pi.name, pi.grand_total, pi.place_of_supply)


def run():
    step("party GSTIN + addresses", parties)
    step("HSN fallback", hsn_fallback)
    step("GST sales invoices", sales_invoices)
    step("GST purchase invoice", purchase_invoice)
    log("DONE")


run()
