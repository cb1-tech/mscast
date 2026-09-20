"""MSCAST ERPNext POC - 05: India Compliance / GST configuration + GST demo documents.

Sets company and party GST registrations and addresses, HSN/SAC and GST rates on items,
creates in-state (CGST+SGST) and out-of-state (IGST) sales invoices and a purchase invoice
with input GST, and switches on the MCA audit trail.
"""
import frappe
from frappe.utils import add_days, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[seed-05] " + m, flush=True)


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


def ins(doc, submit=False):
    d = frappe.get_doc(doc)
    d.flags.ignore_permissions = True
    d.insert(ignore_if_duplicate=True)
    if submit:
        d.submit()
    return d


def address(title, line1, city, state, pincode, country, gstin, gst_category, link_dt, link_name,
            is_company=0):
    name = title + "-" + ("Billing" if not is_company else "Office")
    if frappe.db.exists("Address", {"address_title": title, "address_type": "Billing"}):
        return
    doc = {
        "doctype": "Address", "address_title": title, "address_type": "Billing",
        "address_line1": line1, "city": city, "pincode": pincode, "country": country,
        "is_primary_address": 1, "is_shipping_address": 1,
        "links": [{"link_doctype": link_dt, "link_name": link_name}],
    }
    if country == "India":
        doc["state"] = state
        doc["gstin"] = gstin
        doc["gst_category"] = gst_category
    else:
        doc["state"] = state or ""
        doc["gst_category"] = "Overseas"
    if is_company:
        doc["is_your_company_address"] = 1
    ins(doc)


# ---------------------------------------------------------------- company
def company_gst():
    frappe.db.set_value("Company", COMPANY, "gst_category", "Registered Regular")
    address("MSCAST Pune Office", "Prithvi Park, Row House No. 7, N.I.B.M Road, Kondhwa",
            "Pune", "Maharashtra", "411048", "India", "27AAGCM8444B1ZI",
            "Registered Regular", "Company", COMPANY, is_company=1)


PARTY_GST = {
    # customer/supplier: (line1, city, state, pincode, country, gstin, category)
    "Sahyadri Steels Ltd (DEMO)": ("Plot 14, MIDC Hingna", "Nagpur", "Maharashtra", "440016",
                                   "India", "27AAACS1111A1Z5", "Registered Regular"),
    "Konark Alloys Pvt Ltd (DEMO)": ("Industrial Estate, Kalunga", "Rourkela", "Odisha", "769014",
                                     "India", "21AAACK2222B1Z3", "Registered Regular"),
    "Deccan Extrusions Pvt Ltd (DEMO)": ("Survey 88, Jeedimetla", "Hyderabad", "Telangana", "500055",
                                         "India", "36AAACD3333C1Z1", "Registered Regular"),
    "Narmada Ispat Pvt Ltd (DEMO)": ("Sector C, Sanwer Road", "Indore", "Madhya Pradesh", "452015",
                                     "India", "23AAACN4444D1Z9", "Registered Regular"),
    "Gulf Aluminium Industries LLC (DEMO)": ("Industrial Area 12", "Sharjah", "", "",
                                             "United Arab Emirates", "", "Overseas"),
    "Pushkar Fabricators (DEMO)": ("Gat 220, Shikrapur", "Pune", "Maharashtra", "412208",
                                   "India", "27AAAFP5555E1Z2", "Registered Regular"),
    "Shivneri Machining Works (DEMO)": ("Bhosari MIDC", "Pune", "Maharashtra", "411026",
                                        "India", "27AAAFS6666F1Z8", "Registered Regular"),
    "Kalyani Gears & Drives (DEMO)": ("Chakan MIDC Phase II", "Pune", "Maharashtra", "410501",
                                      "India", "27AAACK7777G1Z6", "Registered Regular"),
    "Hydropower Systems (DEMO)": ("Plot 7, Waluj MIDC", "Chhatrapati Sambhajinagar", "Maharashtra",
                                  "431136", "India", "27AAACH8888H1Z4", "Registered Regular"),
    "Suvarna Copper Moulds (DEMO)": ("GIDC Estate, Vatva", "Ahmedabad", "Gujarat", "382445",
                                     "India", "24AAACS9999I1Z2", "Registered Regular"),
    "Pune Electrical Panels (DEMO)": ("Bhosari MIDC", "Pune", "Maharashtra", "411026",
                                      "India", "27AAACP1010J1Z0", "Registered Regular"),
    "Bharat Steel Traders (DEMO)": ("Bhavani Peth", "Pune", "Maharashtra", "411042",
                                    "India", "27AAACB1111K1Z8", "Registered Regular"),
    "Vidarbha Heavy Transport (DEMO)": ("Transport Nagar", "Nagpur", "Maharashtra", "440027",
                                        "India", "27AAACV1212L1Z6", "Registered Regular"),
    "Precision Inspection Services (DEMO)": ("Kothrud", "Pune", "Maharashtra", "411038",
                                             "India", "27AAACP1313M1Z4", "Registered Regular"),
    "Sunrise Cooling Towers (DEMO)": ("Peenya Industrial Area", "Bengaluru", "Karnataka", "560058",
                                      "India", "29AAACS1414N1Z2", "Registered Regular"),
}

MSME = {
    "Pushkar Fabricators (DEMO)": ("UDYAM-MH-26-0011234", "Small"),
    "Shivneri Machining Works (DEMO)": ("UDYAM-MH-26-0022345", "Micro"),
    "Hydropower Systems (DEMO)": ("UDYAM-MH-26-0033456", "Small"),
    "Pune Electrical Panels (DEMO)": ("UDYAM-MH-26-0044567", "Micro"),
    "Vidarbha Heavy Transport (DEMO)": ("UDYAM-MH-26-0055678", "Small"),
    "Precision Inspection Services (DEMO)": ("UDYAM-MH-26-0066789", "Micro"),
}


def party_gst():
    for party, (l1, city, state, pin, country, gstin, cat) in PARTY_GST.items():
        for dt in ("Customer", "Supplier"):
            if frappe.db.exists(dt, party):
                frappe.db.set_value(dt, party, "gst_category", cat)
                if gstin:
                    frappe.db.set_value(dt, party, "gstin", gstin)
                address(party, l1, city, state, pin, country, gstin, cat, dt, party)
    for sup, (udyam, mtype) in MSME.items():
        if frappe.db.exists("Supplier", sup):
            frappe.db.set_value("Supplier", sup, {"msme_udyam_no": udyam, "msme_type": mtype})
    log("party GST + MSME data set for %d parties" % len(PARTY_GST))


# ------------------------------------------------------------------ items
HSN = {
    "CCM-2S-130": "84543000", "ALBC-7": "84543000",
    "ASM-LADLE-TURRET": "84549000", "ASM-TUNDISH-CAR": "84549000", "ASM-MOULD": "84549000",
    "ASM-WSU": "84549000", "ASM-DUMMY-BAR": "84549000", "ASM-RUNOUT": "84283900",
    "ASM-COOLING-BED": "84283900", "ASM-HYD-POWERPACK": "84122900", "ASM-WATER-SYS": "84139190",
    "ASM-MCC-PLC": "85371000",
    "FAB-FRAME-WSU": "84549000", "FAB-SPRAY-CHAMBER": "84549000", "FAB-TUNDISH-SHELL": "84549000",
    "FAB-PLATFORM": "73089090",
    "BO-GEARMOTOR-5": "85015220", "BO-GEARBOX-HEL": "84834000", "BO-BEARING-SET": "84829900",
    "BO-COUPLING": "84836090", "BO-CYL-100": "84122100", "BO-VALVE-PROP": "84819090",
    "BO-ACCUMULATOR": "84819090", "BO-HOSE-KIT": "40093100", "BO-VFD-22": "85044090",
    "BO-PLC-CPU": "85371000", "BO-HMI-15": "85371000", "BO-PYROMETER": "90251190",
    "BO-CABLE-LOT": "85444999", "BO-MOULD-TUBE": "74112900", "BO-MOULD-JACKET": "84549000",
    "BO-SPRAY-NOZZLE": "84248990", "BO-ROLL-SET": "84549000", "BO-GRAPHITE-RING": "68151090",
    "BO-PUMP-CENT": "84137010", "BO-PHE": "84195090",
    "RM-PLATE-20": "72085190", "RM-PLATE-40": "72085190", "RM-SECTION-ISMB": "72165000",
    "RM-PIPE-SEAMLESS": "73044900",
    "SPR-MOULD-TUBE": "74112900", "SPR-ROLL": "84549000",
    "SRV-DESIGN": "998336", "SRV-ERECTION": "998873",
}


def items_gst():
    tmpl = "GST 18% - " + ABBR
    n = 0
    for code, hsn in HSN.items():
        if not frappe.db.exists("Item", code):
            continue
        if not frappe.db.exists("GST HSN Code", hsn):
            log("missing HSN master %s for %s (skipped)" % (hsn, code))
            continue
        it = frappe.get_doc("Item", code)
        it.gst_hsn_code = hsn
        if not it.taxes:
            it.append("taxes", {"item_tax_template": tmpl, "valid_from": "2026-04-01"})
        it.flags.ignore_permissions = True
        it.flags.ignore_mandatory = True
        it.save()
        n += 1
    log("HSN/SAC + GST 18%% template set on %d items" % n)


# --------------------------------------------------------------- invoices
def sales_invoices():
    """In-state CGST+SGST and out-of-state IGST spares invoices."""
    made = []
    cases = [
        ("Sahyadri Steels Ltd (DEMO)", "Output GST In-state - " + ABBR, "SPR-ROLL", 2, 64000,
         "Spare withdrawal rolls against AMC - in-state supply (CGST+SGST)"),
        ("Konark Alloys Pvt Ltd (DEMO)", "Output GST Out-state - " + ABBR, "SPR-MOULD-TUBE", 8, 192000,
         "Spare copper mould tubes - inter-state supply (IGST)"),
    ]
    for customer, tax_template, item, qty, rate, remark in cases:
        if frappe.db.exists("Sales Invoice", {"customer": customer, "docstatus": 1,
                                              "remarks": remark}):
            continue
        si = frappe.new_doc("Sales Invoice")
        si.customer = customer
        si.company = COMPANY
        si.set_posting_time = 1
        si.posting_date = add_days(TODAY, -4)
        si.due_date = add_days(TODAY, 26)
        si.taxes_and_charges = tax_template
        si.remarks = remark
        si.append("items", {"item_code": item, "qty": qty, "rate": rate, "conversion_factor": 1})
        for t in frappe.get_doc("Sales Taxes and Charges Template", tax_template).taxes:
            si.append("taxes", {
                "charge_type": t.charge_type, "account_head": t.account_head,
                "description": t.description, "rate": t.rate, "cost_center": t.cost_center,
            })
        si.flags.ignore_permissions = True
        si.insert()
        si.submit()
        made.append("%s %s" % (si.name, si.grand_total))
    return ", ".join(made)


def purchase_invoice():
    """Input GST on the mould tube purchase (Gujarat supplier -> IGST)."""
    supplier = "Suvarna Copper Moulds (DEMO)"
    if frappe.db.exists("Purchase Invoice", {"supplier": supplier, "docstatus": 1}):
        return
    pr = frappe.db.get_value("Purchase Receipt", {"supplier": supplier, "docstatus": 1}, "name")
    tax_template = "Input GST Out-state - " + ABBR
    pi = frappe.new_doc("Purchase Invoice")
    pi.supplier = supplier
    pi.company = COMPANY
    pi.set_posting_time = 1
    pi.posting_date = add_days(TODAY, -8)
    pi.bill_no = "SCM/26-27/0471"
    pi.bill_date = add_days(TODAY, -9)
    pi.taxes_and_charges = tax_template
    pi.remarks = "Copper mould tubes and rolls - certified through BRM"
    if pr:
        prd = frappe.get_doc("Purchase Receipt", pr)
        for it in prd.items:
            pi.append("items", {
                "item_code": it.item_code, "qty": it.qty, "rate": it.rate,
                "warehouse": it.warehouse, "project": it.project,
                "purchase_receipt": prd.name, "pr_detail": it.name,
            })
    else:
        pi.append("items", {"item_code": "BO-MOULD-TUBE", "qty": 4, "rate": 192000,
                            "warehouse": "Stores - " + ABBR})
    for t in frappe.get_doc("Purchase Taxes and Charges Template", tax_template).taxes:
        pi.append("taxes", {
            "charge_type": t.charge_type, "account_head": t.account_head, "category": t.category,
            "add_deduct_tax": t.add_deduct_tax, "description": t.description, "rate": t.rate,
            "cost_center": t.cost_center,
        })
    pi.flags.ignore_permissions = True
    pi.insert()
    pi.submit()
    return "%s %s" % (pi.name, pi.grand_total)


def audit_trail():
    s = frappe.get_single("Accounts Settings")
    if not s.get("enable_audit_trail"):
        s.enable_audit_trail = 1
        s.flags.ignore_permissions = True
        s.save()
    return "audit trail enabled=%s" % frappe.db.get_single_value("Accounts Settings", "enable_audit_trail")


def gst_settings():
    s = frappe.get_single("GST Settings")
    s.enable_e_invoice = 0
    s.enable_e_waybill = 1
    s.flags.ignore_permissions = True
    s.save()
    return "e-invoice off (no API credentials), e-way bill forms available"


def run():
    step("company GST + address", company_gst)
    step("party GST + MSME", party_gst)
    step("item HSN/SAC + GST rate", items_gst)
    step("GST sales invoices", sales_invoices)
    step("GST purchase invoice", purchase_invoice)
    step("audit trail", audit_trail)
    step("GST settings", gst_settings)
    log("DONE")


run()
