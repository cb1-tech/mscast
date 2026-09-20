# -*- coding: utf-8 -*-
"""More of the business: customers, suppliers and items MSCAST would really have."""
import frappe

GST_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def gstin(state_code, pan):
    """Build a GSTIN with a valid check digit - India Compliance verifies it."""
    base = "%s%s1Z" % (state_code, pan)
    total = 0
    for i, ch in enumerate(base):
        value = GST_ALPHABET.index(ch)
        factor = 2 if i % 2 else 1
        product = value * factor
        total += product // 36 + product % 36
    return base + GST_ALPHABET[(36 - total % 36) % 36]


def first(dt, filters=None):
    r = frappe.get_all(dt, filters=filters or {}, fields=["name"], limit=1)
    return r[0].name if r else None

company = frappe.defaults.get_global_default("company")
abbr = frappe.db.get_value("Company", company, "abbr")

# ------------------------------------------------------------------ customers
CUSTOMERS = [
    # name, group-ish, state, gstin, city, terms
    ("Bhilai Rolling Mills Pvt Ltd", "Chhattisgarh", gstin("22", "AABCB4411C"), "Bhilai", "490001"),
    ("Godavari Ispat Ltd", "Telangana", gstin("36", "AACCG5522D"), "Peddapalli", "505172"),
    ("Nagpur Steel & Power Ltd", "Maharashtra", gstin("27", "AAECN6633E"), "Nagpur", "440016"),
    ("Surya Metallics Pvt Ltd", "Gujarat", gstin("24", "AAFCS7744F"), "Bhavnagar", "364001"),
    ("Kalinga Casting Works", "Odisha", gstin("21", "AAGCK8855G"), "Rourkela", "769001"),
    ("Vidarbha Alloys Pvt Ltd", "Maharashtra", gstin("27", "AAHCV9966H"), "Chandrapur", "442401"),
]

template_customer = first("Customer")
tmpl = frappe.get_doc("Customer", template_customer) if template_customer else None

made = []
for name, state, gstin_no, city, pin in CUSTOMERS:
    if frappe.db.exists("Customer", name):
        continue
    c = frappe.new_doc("Customer")
    c.customer_name = name
    c.customer_type = "Company"
    if tmpl:
        c.customer_group = tmpl.customer_group
        c.territory = tmpl.territory
    if frappe.get_meta("Customer").has_field("gst_category"):
        c.gst_category = "Registered Regular"
    c.flags.ignore_permissions = True
    c.insert()

    a = frappe.new_doc("Address")
    a.address_title = name
    a.address_type = "Billing"
    a.address_line1 = "Plot %d, Industrial Area" % (10 + len(made) * 7)
    a.city = city
    a.state = state
    a.country = "India"
    a.pincode = pin
    if frappe.get_meta("Address").has_field("gstin"):
        a.gstin = gstin_no
        a.gst_state = state
    a.append("links", {"link_doctype": "Customer", "link_name": name})
    a.flags.ignore_permissions = True
    a.insert()
    made.append(name)

print("customers added:", len(made))
for m in made:
    print("   ", m)

# ------------------------------------------------------------------ suppliers
SUPPLIERS = [
    ("Ashoka Heavy Fabricators (DEMO)", "Maharashtra", gstin("27", "AAICA1122J"), "Small", "UDYAM-MH-26-0071234", "Pune", "411026"),
    ("Sai Hydraulics & Systems (DEMO)", "Maharashtra", gstin("27", "AAJCS2233K"), "Micro", "UDYAM-MH-26-0082345", "Pune", "411019"),
    ("Deccan Roll Manufacturing (DEMO)", "Telangana", gstin("36", "AAKCD3344L"), "Small", "UDYAM-TG-26-0093456", "Hyderabad", "500055"),
    ("Elektra Drives India (DEMO)", "Karnataka", gstin("29", "AALCE4455M"), "Not registered", None, "Bengaluru", "560058"),
    ("Raipur Refractories Pvt Ltd (DEMO)", "Chhattisgarh", gstin("22", "AAMCR5566N"), "Small", "UDYAM-CT-26-0104567", "Raipur", "492001"),
]

made_s = []
for name, state, gstin_no, msme, udyam, city, pin in SUPPLIERS:
    if frappe.db.exists("Supplier", name):
        continue
    s = frappe.new_doc("Supplier")
    s.supplier_name = name
    t = first("Supplier")
    if t:
        tm = frappe.get_doc("Supplier", t)
        s.supplier_group = tm.supplier_group
        s.country = tm.country or "India"
    if frappe.get_meta("Supplier").has_field("gst_category"):
        s.gst_category = "Registered Regular" if msme != "Not registered" else "Registered Regular"
    if frappe.get_meta("Supplier").has_field("msme_type"):
        s.msme_type = msme
    if udyam and frappe.get_meta("Supplier").has_field("msme_udyam_no"):
        s.msme_udyam_no = udyam
    s.flags.ignore_permissions = True
    s.insert()

    a = frappe.new_doc("Address")
    a.address_title = name
    a.address_type = "Billing"
    a.address_line1 = "Unit %d, MIDC" % (4 + len(made_s) * 3)
    a.city = city
    a.state = state
    a.country = "India"
    a.pincode = pin
    if frappe.get_meta("Address").has_field("gstin"):
        a.gstin = gstin_no
        a.gst_state = state
    a.append("links", {"link_doctype": "Supplier", "link_name": name})
    a.flags.ignore_permissions = True
    a.insert()
    made_s.append(name)

print("suppliers added:", len(made_s))
for m in made_s:
    print("   ", m)

# ---------------------------------------------------------------------- items
tmpl_item = frappe.get_doc("Item", "CU-MOULD-130") if frappe.db.exists("Item", "CU-MOULD-130") else None
if not tmpl_item:
    tmpl_item = frappe.get_doc("Item", first("Item", {"is_stock_item": 1}))

ITEMS = [
    ("WSU-ROLL-130", "Withdrawal roll assembly 130 sq", "Bought-out", "Nos", "84559000", 1, 86000),
    ("GEARBOX-WSU", "WSU drive gearbox with motor", "Bought-out", "Nos", "84834000", 1, 264000),
    ("OSC-ASSY", "Mould oscillator assembly", "Bought-out", "Nos", "84543000", 1, 418000),
    ("TORCH-CUT-2S", "Oxy-fuel torch cutting machine, 2 strand", "Bought-out", "Set", "84561100", 1, 735000),
    ("DUMMY-BAR", "Dummy bar with head, 130 sq", "Bought-out", "Nos", "84543000", 1, 152000),
    ("HYD-POWERPACK", "Hydraulic power pack 45 kW", "Bought-out", "Nos", "84129090", 1, 512000),
    ("PLC-PANEL", "PLC and HMI control panel", "Bought-out", "Nos", "85371000", 1, 690000),
    ("MCC-PANEL", "Motor control centre with VFDs", "Bought-out", "Nos", "85371000", 1, 845000),
    ("COOL-TOWER", "Cooling tower 400 TR", "Bought-out", "Nos", "84195090", 1, 398000),
    ("TUNDISH-CAR", "Tundish car, motorised", "Bought-out", "Nos", "84543000", 1, 576000),
    ("SPRAY-NOZZLE", "Secondary cooling spray nozzle", "Spares", "Nos", "84248900", 1, 1850),
    ("REFRACTORY-TD", "Tundish refractory lining set", "Spares", "Set", "69022010", 1, 96000),
    ("MS-PLATE-20", "MS plate 20 mm IS2062 E250", "Raw material", "Kg", "72085190", 1, 68),
    ("SRV-COMMISSION", "Commissioning supervision at site", "Site Services", "Day", "998733", 0, 11500),
    ("SRV-REVAMP", "Caster revamp engineering and supervision", "Site Services", "Day", "998733", 0, 13500),
]

made_i = []
for code, name, group, uom, hsn, stock, rate in ITEMS:
    if frappe.db.exists("Item", code):
        continue
    it = frappe.new_doc("Item")
    it.item_code = code
    it.item_name = name
    it.description = name
    it.stock_uom = uom
    it.is_stock_item = stock
    it.include_item_in_manufacturing = 0
    it.item_group = group if frappe.db.exists("Item Group", group) else tmpl_item.item_group
    if frappe.get_meta("Item").has_field("gst_hsn_code"):
        if frappe.db.exists("GST HSN Code", hsn):
            it.gst_hsn_code = hsn
        elif tmpl_item:
            it.gst_hsn_code = tmpl_item.gst_hsn_code
    it.valuation_rate = rate
    it.flags.ignore_permissions = True
    it.insert()
    made_i.append((code, name))

print("items added:", len(made_i))
for code, name in made_i:
    print("   ", code, "-", name)

frappe.db.commit()
print()
print("totals now: customers %d | suppliers %d | items %d" % (
    frappe.db.count("Customer"), frappe.db.count("Supplier"), frappe.db.count("Item")))
