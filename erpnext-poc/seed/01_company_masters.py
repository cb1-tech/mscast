"""MSCAST ERPNext POC - 01: company, masters, users.

Run inside the backend container:
    cd /home/frappe/frappe-bench && python -c "import frappe;frappe.init(site='frontend');frappe.connect();exec(open('/workspace/seed/01_company_masters.py').read());frappe.db.commit()"

All data is FICTIONAL demo data for a proof of concept.
"""
import frappe
from frappe.utils import add_days, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"


def log(msg):
    print("[seed-01] " + msg, flush=True)


def exists(dt, name):
    return frappe.db.exists(dt, name)


def make(doc, ignore_links=False):
    d = frappe.get_doc(doc)
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    if ignore_links:
        d.flags.ignore_links = True
    d.insert(ignore_if_duplicate=True)
    return d


# ---------------------------------------------------------------- company
def setup_company():
    if not exists("Company", COMPANY):
        make({
            "doctype": "Company",
            "company_name": COMPANY,
            "abbr": ABBR,
            "default_currency": "INR",
            "country": "India",
            "create_chart_of_accounts_based_on": "Standard Template",
            "chart_of_accounts": "Standard with Numbers",
        })
        log("company created")
    else:
        log("company exists")

    c = frappe.get_doc("Company", COMPANY)
    c.tax_id = "27AAGCM8444B1ZI"  # public GSTIN, demo use
    c.domain = "Manufacturing"
    c.save(ignore_permissions=True)

    # global defaults
    gd = frappe.get_single("Global Defaults")
    gd.default_company = COMPANY
    gd.country = "India"
    gd.save(ignore_permissions=True)
    frappe.db.set_default("company", COMPANY)
    frappe.db.set_default("currency", "INR")

    # delete the auto "Wind Power" style demo company if any other exists
    for other in frappe.get_all("Company", filters={"name": ("!=", COMPANY)}, pluck="name"):
        log("note: other company present: " + other)


# ---------------------------------------------------------------- basics
def setup_basics():
    for uom in ["Manhour", "Manday", "Set", "Lot", "Metre Run"]:
        if not exists("UOM", uom):
            make({"doctype": "UOM", "uom_name": uom, "must_be_whole_number": 0})

    groups = [
        ("Machines (ETO)", "All Item Groups"),
        ("Assemblies", "All Item Groups"),
        ("Fabricated Parts", "All Item Groups"),
        ("Bought-out - Mechanical", "All Item Groups"),
        ("Bought-out - Hydraulics", "All Item Groups"),
        ("Bought-out - Electrical", "All Item Groups"),
        ("Bought-out - Casting", "All Item Groups"),
        ("Raw Material - Steel", "All Item Groups"),
        ("Spares", "All Item Groups"),
        ("Engineering Services", "All Item Groups"),
        ("Site Services", "All Item Groups"),
    ]
    for g, parent in groups:
        if not exists("Item Group", g):
            make({
                "doctype": "Item Group",
                "item_group_name": g,
                "parent_item_group": parent,
                "is_group": 0,
            })

    for wh, is_group in [("Vendor WIP", 0), ("Site Stores", 0), ("Free Issue at Vendor", 0)]:
        name = wh + " - " + ABBR
        if not exists("Warehouse", name):
            make({
                "doctype": "Warehouse",
                "warehouse_name": wh,
                "company": COMPANY,
                "is_group": is_group,
                "parent_warehouse": "All Warehouses - " + ABBR,
            })

    activities = [
        ("Layout & GA Drawing", 950),
        ("Detail Design", 850),
        ("Hydraulic Circuit", 900),
        ("P&ID / Cooling", 900),
        ("Vendor Visit", 700),
        ("Site Supervision", 1200),
        ("Project Management", 1100),
    ]
    for act, rate in activities:
        if not exists("Activity Type", act):
            make({"doctype": "Activity Type", "activity_type": act})
        if not frappe.db.exists("Activity Cost", {"activity_type": act}):
            make({
                "doctype": "Activity Cost",
                "activity_type": act,
                "billing_rate": rate,
                "costing_rate": rate * 0.6,
                "employee": None,
            })
    log("basics done")


# ---------------------------------------------------------------- parties
CUSTOMERS = [
    ("Sahyadri Steels Ltd (DEMO)", "Maharashtra", "27AAACS1111A1Z5", "Nagpur"),
    ("Konark Alloys Pvt Ltd (DEMO)", "Odisha", "21AAACK2222B1Z3", "Rourkela"),
    ("Deccan Extrusions Pvt Ltd (DEMO)", "Telangana", "36AAACD3333C1Z1", "Hyderabad"),
    ("Gulf Aluminium Industries LLC (DEMO)", None, None, "Sharjah"),
    ("Narmada Ispat Pvt Ltd (DEMO)", "Madhya Pradesh", "23AAACN4444D1Z9", "Indore"),
]

SUPPLIERS = [
    ("Pushkar Fabricators (DEMO)", "Fabrication", "27AAAFP5555E1Z2", 1, "Small"),
    ("Shivneri Machining Works (DEMO)", "Machining", "27AAAFS6666F1Z8", 1, "Micro"),
    ("Kalyani Gears & Drives (DEMO)", "Mechanical", "27AAACK7777G1Z6", 0, None),
    ("Hydropower Systems (DEMO)", "Hydraulics", "27AAACH8888H1Z4", 1, "Small"),
    ("Suvarna Copper Moulds (DEMO)", "Casting", "24AAACS9999I1Z2", 0, None),
    ("Pune Electrical Panels (DEMO)", "Electrical", "27AAACP1010J1Z0", 1, "Micro"),
    ("Bharat Steel Traders (DEMO)", "Raw Material", "27AAACB1111K1Z8", 0, None),
    ("Vidarbha Heavy Transport (DEMO)", "Logistics", "27AAACV1212L1Z6", 1, "Small"),
    ("Precision Inspection Services (DEMO)", "Inspection", "27AAACP1313M1Z4", 1, "Micro"),
    ("Sunrise Cooling Towers (DEMO)", "Utilities", "29AAACS1414N1Z2", 0, None),
]


def setup_parties():
    if not exists("Supplier Group", "Sub-contractor"):
        make({"doctype": "Supplier Group", "supplier_group_name": "Sub-contractor"})
    for name, sgroup, gstin, is_msme, msme_type in SUPPLIERS:
        if not exists("Supplier", name):
            make({
                "doctype": "Supplier",
                "supplier_name": name,
                "supplier_group": "Sub-contractor" if sgroup in ("Fabrication", "Machining") else "Services",
                "supplier_type": "Company",
                "country": "India",
                "tax_id": gstin,
            })
    for name, state, gstin, city in CUSTOMERS:
        if not exists("Customer", name):
            make({
                "doctype": "Customer",
                "customer_name": name,
                "customer_type": "Company",
                "customer_group": "Commercial",
                "territory": "India" if state else "Rest Of The World",
                "tax_id": gstin,
                "default_currency": "INR" if state else "USD",
            })
    log("parties done: %d customers, %d suppliers" % (len(CUSTOMERS), len(SUPPLIERS)))


# ---------------------------------------------------------------- items
ITEMS = [
    # (code, name, group, uom, is_stock, valuation_rate, is_purchase, is_sales)
    ("CCM-2S-130", "Continuous Casting Machine, 2 strand, 130 sq billet", "Machines (ETO)", "Set", 0, 0, 0, 1),
    ("ALBC-7", "Aluminium Billet Casting Machine, 7 inch", "Machines (ETO)", "Set", 0, 0, 0, 1),
    ("ASM-LADLE-TURRET", "Ladle Turret Assembly", "Assemblies", "Nos", 1, 1850000, 1, 0),
    ("ASM-TUNDISH-CAR", "Tundish Car Assembly", "Assemblies", "Nos", 1, 920000, 1, 0),
    ("ASM-MOULD", "Mould Assembly with Oscillator", "Assemblies", "Nos", 1, 1450000, 1, 0),
    ("ASM-WSU", "Withdrawal & Straightening Unit", "Assemblies", "Nos", 1, 2100000, 1, 0),
    ("ASM-DUMMY-BAR", "Dummy Bar & Storage", "Assemblies", "Nos", 1, 480000, 1, 0),
    ("ASM-RUNOUT", "Run-out Roller Table", "Assemblies", "Nos", 1, 760000, 1, 0),
    ("ASM-COOLING-BED", "Cooling Bed / Transfer Conveyor", "Assemblies", "Nos", 1, 640000, 1, 0),
    ("ASM-HYD-POWERPACK", "Hydraulic Power Pack 90 LPM", "Assemblies", "Nos", 1, 890000, 1, 0),
    ("ASM-WATER-SYS", "Primary & Secondary Water System", "Assemblies", "Nos", 1, 1250000, 1, 0),
    ("ASM-MCC-PLC", "MCC Panel with PLC & HMI", "Assemblies", "Nos", 1, 1680000, 1, 0),
    ("FAB-FRAME-WSU", "Fabricated Frame - WSU", "Fabricated Parts", "Nos", 1, 320000, 1, 0),
    ("FAB-SPRAY-CHAMBER", "Fabricated Spray Chamber", "Fabricated Parts", "Nos", 1, 245000, 1, 0),
    ("FAB-TUNDISH-SHELL", "Tundish Shell Fabrication", "Fabricated Parts", "Nos", 1, 180000, 1, 0),
    ("FAB-PLATFORM", "Operating Platform & Walkway", "Fabricated Parts", "Nos", 1, 165000, 1, 0),
    ("BO-GEARMOTOR-5", "Geared Motor 5.5 kW", "Bought-out - Mechanical", "Nos", 1, 62000, 1, 0),
    ("BO-GEARBOX-HEL", "Helical Gearbox Ratio 40:1", "Bought-out - Mechanical", "Nos", 1, 88000, 1, 0),
    ("BO-BEARING-SET", "Bearing Set with Housing", "Bought-out - Mechanical", "Set", 1, 24000, 1, 0),
    ("BO-COUPLING", "Flexible Coupling", "Bought-out - Mechanical", "Nos", 1, 9500, 1, 0),
    ("BO-CYL-100", "Hydraulic Cylinder 100 mm bore", "Bought-out - Hydraulics", "Nos", 1, 46000, 1, 0),
    ("BO-VALVE-PROP", "Proportional Valve", "Bought-out - Hydraulics", "Nos", 1, 78000, 1, 0),
    ("BO-ACCUMULATOR", "Hydraulic Accumulator 20 L", "Bought-out - Hydraulics", "Nos", 1, 34000, 1, 0),
    ("BO-HOSE-KIT", "Hose & Fitting Kit", "Bought-out - Hydraulics", "Lot", 1, 52000, 1, 0),
    ("BO-VFD-22", "VFD 22 kW", "Bought-out - Electrical", "Nos", 1, 74000, 1, 0),
    ("BO-PLC-CPU", "PLC CPU with I/O", "Bought-out - Electrical", "Nos", 1, 265000, 1, 0),
    ("BO-HMI-15", "HMI Panel 15 inch", "Bought-out - Electrical", "Nos", 1, 98000, 1, 0),
    ("BO-PYROMETER", "Infrared Pyrometer", "Bought-out - Electrical", "Nos", 1, 118000, 1, 0),
    ("BO-CABLE-LOT", "Power & Control Cable Lot", "Bought-out - Electrical", "Lot", 1, 145000, 1, 0),
    ("BO-MOULD-TUBE", "Copper Mould Tube 130 sq", "Bought-out - Casting", "Nos", 1, 185000, 1, 0),
    ("BO-MOULD-JACKET", "Mould Water Jacket", "Bought-out - Casting", "Nos", 1, 96000, 1, 0),
    ("BO-SPRAY-NOZZLE", "Spray Nozzle Set", "Bought-out - Casting", "Set", 1, 28000, 1, 0),
    ("BO-ROLL-SET", "Withdrawal Roll Set", "Bought-out - Casting", "Set", 1, 156000, 1, 0),
    ("BO-GRAPHITE-RING", "Graphite Hot-top Ring", "Bought-out - Casting", "Nos", 1, 42000, 1, 0),
    ("BO-PUMP-CENT", "Centrifugal Pump 50 HP", "Bought-out - Mechanical", "Nos", 1, 132000, 1, 0),
    ("BO-PHE", "Plate Heat Exchanger", "Bought-out - Mechanical", "Nos", 1, 224000, 1, 0),
    ("RM-PLATE-20", "MS Plate 20 mm IS 2062", "Raw Material - Steel", "Kg", 1, 78, 1, 0),
    ("RM-PLATE-40", "MS Plate 40 mm IS 2062", "Raw Material - Steel", "Kg", 1, 82, 1, 0),
    ("RM-SECTION-ISMB", "ISMB Structural Section", "Raw Material - Steel", "Kg", 1, 74, 1, 0),
    ("RM-PIPE-SEAMLESS", "Seamless Pipe", "Raw Material - Steel", "Kg", 1, 168, 1, 0),
    ("SPR-MOULD-TUBE", "Spare Copper Mould Tube", "Spares", "Nos", 1, 192000, 1, 1),
    ("SPR-ROLL", "Spare Withdrawal Roll", "Spares", "Nos", 1, 62000, 1, 1),
    ("SRV-DESIGN", "Engineering Design & Drawing Service", "Engineering Services", "Manhour", 0, 0, 0, 1),
    ("SRV-ERECTION", "Erection & Commissioning Supervision", "Site Services", "Manday", 0, 0, 0, 1),
]


def setup_items():
    made = 0
    for code, name, group, uom, is_stock, rate, is_pur, is_sal in ITEMS:
        if exists("Item", code):
            continue
        d = {
            "doctype": "Item",
            "item_code": code,
            "item_name": name[:140],
            "description": name,
            "item_group": group,
            "stock_uom": uom,
            "is_stock_item": is_stock,
            "is_purchase_item": is_pur,
            "is_sales_item": is_sal,
            "include_item_in_manufacturing": 0,
            "valuation_rate": rate,
            "item_defaults": [{"company": COMPANY, "default_warehouse": "Stores - " + ABBR}],
        }
        make(d)
        made += 1
    log("items created: %d (total %d)" % (made, len(ITEMS)))


def run():
    setup_company()
    setup_basics()
    setup_parties()
    setup_items()
    frappe.db.commit()
    log("DONE")


run()
