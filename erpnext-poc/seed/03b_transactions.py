"""MSCAST ERPNext POC - 03: demo transactions (all fictional).

Project 1  CCM-2 strand for Sahyadri Steels  - mid execution
Project 2  Aluminium billet caster           - just started
Plus an open export enquiry and a spares opportunity.
"""
import frappe
from frappe.utils import add_days, nowdate, flt

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[seed-03] " + m, flush=True)

P1_NAME = "CCM 2-Strand 130sq - Sahyadri Steels"
P2_NAME = "Aluminium Billet Caster 7in - Deccan Extrusions"
CUST1 = "Sahyadri Steels Ltd (DEMO)"
CUST2 = "Deccan Extrusions Pvt Ltd (DEMO)"
PJ = {}  # project_name -> actual docname


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


def get_or_none(dt, filters):
    n = frappe.db.get_value(dt, filters, "name")
    return frappe.get_doc(dt, n) if n else None


def project_name_to_doc(project_name):
    n = frappe.db.get_value("Project", {"project_name": project_name}, "name")
    return n


def ensure_project(payload):
    """Project uses a naming series, so resolve the real docname."""
    existing = project_name_to_doc(payload["project_name"])
    if existing:
        PJ[payload["project_name"]] = existing
        return existing
    d = ins(payload)
    PJ[payload["project_name"]] = d.name
    return d.name


def opp_item(code, qty, rate):
    return {"item_code": code, "qty": qty, "rate": rate, "amount": qty * rate,
            "base_rate": rate, "base_amount": qty * rate,
            "uom": frappe.db.get_value("Item", code, "stock_uom")}


# =====================================================================
# Project 1
# =====================================================================
def p1_lead_to_so():
    if not frappe.db.exists("Opportunity", {"party_name": CUST1}):
        ins({
            "doctype": "Opportunity", "opportunity_from": "Customer", "party_name": CUST1,
            "opportunity_type": "Sales", "source": "Existing Customer", "company": COMPANY,
            "transaction_date": add_days(TODAY, -150), "expected_closing": add_days(TODAY, -120),
            "opportunity_amount": 21500000, "status": "Converted",
            "items": [opp_item("CCM-2S-130", 1, 19500000)],
        })
    if not frappe.db.exists("Quotation", {"party_name": CUST1, "docstatus": 1}):
        ins({
            "doctype": "Quotation", "quotation_to": "Customer", "party_name": CUST1,
            "company": COMPANY, "transaction_date": add_days(TODAY, -140),
            "valid_till": add_days(TODAY, -80), "currency": "INR",
            "selling_price_list": "Standard Selling",
            "items": [
                {"item_code": "CCM-2S-130", "qty": 1, "uom": "Set", "rate": 19500000, "conversion_factor": 1,
                 "description": "Continuous casting machine, 2 strand, 130 sq billet, R6m radius"},
                {"item_code": "SRV-DESIGN", "qty": 400, "uom": "Manhour", "rate": 1200, "conversion_factor": 1},
                {"item_code": "SRV-ERECTION", "qty": 30, "uom": "Manday", "rate": 9500, "conversion_factor": 1},
            ],
        }, submit=True)
    so = get_or_none("Sales Order", {"customer": CUST1, "docstatus": 1})
    if not so:
        so = ins({
            "doctype": "Sales Order", "customer": CUST1, "company": COMPANY,
            "transaction_date": add_days(TODAY, -120), "delivery_date": add_days(TODAY, 45),
            "currency": "INR", "selling_price_list": "Standard Selling",
            "customer_po_no": "SSL/PO/2026-27/114", "retention_percent": 10, "ld_percent": 0.5,
            "pbg_percent": 10, "contract_delivery_date": add_days(TODAY, 45),
            "items": [
                {"item_code": "CCM-2S-130", "qty": 1, "uom": "Set", "rate": 19500000,
                 "delivery_date": add_days(TODAY, 45), "conversion_factor": 1},
                {"item_code": "SRV-DESIGN", "qty": 400, "uom": "Manhour", "rate": 1200,
                 "delivery_date": add_days(TODAY, -30), "conversion_factor": 1},
                {"item_code": "SRV-ERECTION", "qty": 30, "uom": "Manday", "rate": 9500,
                 "delivery_date": add_days(TODAY, 75), "conversion_factor": 1},
            ],
        }, submit=True)
    return so.name


def p1_project(so_name):
    pname = ensure_project({
        "doctype": "Project", "project_name": P1_NAME, "company": COMPANY, "status": "Open",
        "expected_start_date": add_days(TODAY, -115), "expected_end_date": add_days(TODAY, 75),
        "customer": CUST1, "sales_order": so_name, "project_type": "External",
        "contract_delivery_date": add_days(TODAY, 45), "machine_family": "CCM 2-strand",
        "estimated_costing": 14800000,
    })
    if not frappe.db.exists("Task", {"project": pname}):
        for subj, s, e, status, prog in [
            ("Project kick-off & handover", -115, -112, "Completed", 100),
            ("GA drawing & customer approval", -110, -85, "Completed", 100),
            ("Detail design - WSU & Mould", -84, -50, "Completed", 100),
            ("Hydraulic circuit & P&ID", -60, -35, "Completed", 100),
            ("MDF release & procurement", -50, -10, "Working", 80),
            ("Fabrication at vendors", -40, 20, "Working", 55),
            ("Pre-dispatch inspection", 10, 30, "Open", 0),
            ("Dispatch lots 1-3", 5, 45, "Working", 30),
            ("Erection & commissioning at site", 50, 75, "Open", 0),
        ]:
            ins({"doctype": "Task", "subject": subj, "project": pname, "status": status,
                 "exp_start_date": add_days(TODAY, s), "exp_end_date": add_days(TODAY, e),
                 "progress": prog, "company": COMPANY})
    frappe.db.set_value("Sales Order", so_name, "project", pname)
    return pname


def p1_timesheets(pname):
    if frappe.db.exists("Timesheet", {"parent_project": pname}):
        return
    for act, equip, day, hrs in [
        ("Layout & GA Drawing", "Ladle Turret", -100, 6.5),
        ("Detail Design", "Withdrawal & Straightening Unit", -70, 7.0),
        ("Detail Design", "Mould Assembly", -66, 6.0),
        ("Hydraulic Circuit", "Hydraulic Power Pack", -55, 5.5),
        ("P&ID / Cooling", "Water System", -45, 4.5),
        ("Project Management", "Project", -20, 3.0),
    ]:
        ins({
            "doctype": "Timesheet", "company": COMPANY, "parent_project": pname,
            "time_logs": [{
                "activity_type": act, "project": pname, "equipment": equip,
                "from_time": add_days(TODAY, day) + " 09:30:00", "hours": hrs,
                "description": act + " - " + equip,
            }],
        }, submit=True)


PCC_LINES = [
    ("ASM-LADLE-TURRET", "Ladle turret with hydraulic lift", "Ladle Turret", "Fabrication", 1, 1850000, "In-house design", 70),
    ("ASM-TUNDISH-CAR", "Tundish car with drive", "Tundish", "Fabrication", 1, 920000, "In-house design", 60),
    ("ASM-MOULD", "Mould assembly with oscillator", "Mould", "Fabrication", 2, 1450000, "In-house design", 75),
    ("BO-MOULD-TUBE", "Copper mould tube 130 sq", "Mould", "Bought-out", 4, 185000, "Approved make", 90),
    ("ASM-WSU", "Withdrawal & straightening unit", "WSU", "Fabrication", 2, 2100000, "In-house design", 80),
    ("BO-ROLL-SET", "Withdrawal roll set", "WSU", "Bought-out", 2, 156000, "Approved make", 70),
    ("ASM-DUMMY-BAR", "Dummy bar & storage", "Dummy Bar", "Fabrication", 1, 480000, "", 55),
    ("ASM-RUNOUT", "Run-out roller table", "Run-out", "Fabrication", 1, 760000, "", 50),
    ("ASM-COOLING-BED", "Cooling bed / transfer", "Cooling Bed", "Fabrication", 1, 640000, "", 50),
    ("ASM-HYD-POWERPACK", "Hydraulic power pack 90 LPM", "Hydraulics", "Bought-out", 1, 890000, "Approved make", 60),
    ("ASM-WATER-SYS", "Water system primary & secondary", "Water System", "Bought-out", 1, 1250000, "Approved make", 75),
    ("ASM-MCC-PLC", "MCC panel with PLC & HMI", "Electrical", "Bought-out", 1, 1680000, "Approved make", 85),
    ("RM-PLATE-20", "MS plate 20 mm", "Structure", "Raw Material", 12000, 78, "IS 2062", 20),
    ("RM-SECTION-ISMB", "ISMB structural section", "Structure", "Raw Material", 6000, 74, "IS 2062", 20),
    ("SRV-ERECTION", "Erection supervision mandays", "Site", "Service", 30, 5200, "", 0),
]


def p1_pcc(pname, so_name):
    if frappe.db.exists("MSCAST PCC", {"project": pname}):
        return
    items = [{
        "item_code": c, "description": d, "assembly": a, "category": cat, "qty": q,
        "uom": frappe.db.get_value("Item", c, "stock_uom"), "est_rate": r,
        "est_amount": flt(q) * flt(r), "approved_make": mk, "lead_time_days": lt,
    } for c, d, a, cat, q, r, mk, lt in PCC_LINES]
    total = sum(i["est_amount"] for i in items)
    cv = flt(frappe.db.get_value("Sales Order", so_name, "grand_total"))
    pcc = ins({
        "doctype": "MSCAST PCC", "project": pname, "sales_order": so_name, "customer": CUST1,
        "revision": "R2", "status": "Approved", "prepared_by": "Administrator",
        "approved_by": "Administrator", "items": items, "total_estimated_cost": total,
        "contract_value": cv,
        "target_margin_pct": round((cv - total) / cv * 100, 1) if cv else 0,
        "remarks": "R2 after customer approved GA drawing; mould tubes increased from 3 to 4 nos.",
    })
    frappe.db.set_value("Sales Order", so_name, "mscast_pcc", pcc.name)
    frappe.db.set_value("Project", pname, "mscast_pcc", pcc.name)
    return pcc.name


DRAWINGS = [
    ("MSC-2601-GA-01", "General arrangement - CCM 2 strand", "Overall", "GA / Layout", "R3", "Approved by Customer"),
    ("MSC-2601-WSU-10", "Withdrawal & straightening unit assembly", "WSU", "Detail", "R2", "Released for Manufacture"),
    ("MSC-2601-MLD-20", "Mould assembly with oscillator", "Mould", "Detail", "R1", "Released for Manufacture"),
    ("MSC-2601-TUN-30", "Tundish car general assembly", "Tundish", "Detail", "R1", "Released for Manufacture"),
    ("MSC-2601-HYD-40", "Hydraulic circuit diagram", "Hydraulics", "Hydraulic Circuit", "R2", "Approved by Customer"),
    ("MSC-2601-PID-50", "Cooling water P&ID", "Water System", "P&ID", "R0", "For Customer Approval"),
    ("MSC-2601-ELE-60", "Single line diagram & panel GA", "Electrical", "Electrical", "R0", "Draft"),
]


def p1_drawings(pname):
    if frappe.db.exists("MSCAST Drawing", {"project": pname}):
        return
    for no, title, asm, dtype, rev, status in DRAWINGS:
        n = int(rev[1:])
        revs = [{
            "revision": "R%d" % i, "revision_date": add_days(TODAY, -100 + i * 18),
            "change_description": "Initial issue" if i == 0 else "Revised after customer comments %d" % i,
            "issued_to": "Customer" if i == 0 else "Customer, Vendors",
        } for i in range(n + 1)]
        ins({
            "doctype": "MSCAST Drawing", "drawing_no": no, "title": title, "project": pname,
            "assembly": asm, "drawing_type": dtype, "current_revision": rev, "status": status,
            "drive_link": "https://drive.google.com/drive/folders/DEMO-" + no, "revisions": revs,
            "issued_to_vendors": "Pushkar Fabricators (DEMO)" if status == "Released for Manufacture" else "",
        })


MDF_SETS = [
    ("WSU", "MSC-2601-WSU-10", "Released to Procurement", [
        ("FAB-FRAME-WSU", "Fabricated frame - WSU", "Fabrication", 2, 4200, "IS 2062 E250"),
        ("BO-ROLL-SET", "Withdrawal roll set", "Bought-out", 2, 260, "EN8 hardened"),
        ("BO-GEARMOTOR-5", "Geared motor 5.5 kW", "Bought-out", 4, 95, "IE3"),
        ("BO-GEARBOX-HEL", "Helical gearbox 40:1", "Bought-out", 2, 180, ""),
        ("RM-PLATE-40", "MS plate 40 mm", "Raw Material", 3200, 1, "IS 2062"),
    ]),
    ("Mould", "MSC-2601-MLD-20", "Released to Procurement", [
        ("BO-MOULD-TUBE", "Copper mould tube 130 sq", "Bought-out", 4, 165, "DHP copper"),
        ("BO-MOULD-JACKET", "Mould water jacket", "Bought-out", 2, 240, "SS 304"),
        ("BO-SPRAY-NOZZLE", "Spray nozzle set", "Bought-out", 2, 18, ""),
        ("FAB-SPRAY-CHAMBER", "Spray chamber fabrication", "Fabrication", 2, 850, "SS 409"),
    ]),
    ("Hydraulics", "MSC-2601-HYD-40", "Draft", [
        ("BO-CYL-100", "Hydraulic cylinder 100 mm", "Bought-out", 6, 85, ""),
        ("BO-VALVE-PROP", "Proportional valve", "Bought-out", 2, 12, ""),
        ("BO-ACCUMULATOR", "Accumulator 20 L", "Bought-out", 2, 45, ""),
        ("BO-HOSE-KIT", "Hose & fitting kit", "Bought-out", 1, 60, ""),
    ]),
]


def p1_mdf(pname):
    if frappe.db.exists("MSCAST MDF", {"project": pname}):
        return
    for asm, drg_no, status, lines in MDF_SETS:
        drg = frappe.db.get_value("MSCAST Drawing", {"drawing_no": drg_no}, "name")
        items = [{
            "item_code": c, "description": d, "drawing_no": drg_no, "material_spec": spec,
            "qty": q, "uom": frappe.db.get_value("Item", c, "stock_uom"),
            "weight_kg": wt, "category": cat,
        } for c, d, cat, q, wt, spec in lines]
        ins({
            "doctype": "MSCAST MDF", "project": pname, "assembly": asm, "drawing": drg,
            "status": status, "prepared_by": "Administrator",
            "released_on": add_days(TODAY, -45) if status != "Draft" else None,
            "items": items,
        })


def p1_procurement(pname):
    if not frappe.db.exists("Material Request", {"title": "MDF WSU + Mould"}):
        ins({
            "doctype": "Material Request", "material_request_type": "Purchase", "company": COMPANY,
            "transaction_date": add_days(TODAY, -60), "schedule_date": add_days(TODAY, -20),
            "title": "MDF WSU + Mould",
            "items": [
                {"item_code": "BO-MOULD-TUBE", "qty": 4, "schedule_date": add_days(TODAY, -20),
                 "warehouse": "Stores - " + ABBR, "project": pname},
                {"item_code": "BO-ROLL-SET", "qty": 2, "schedule_date": add_days(TODAY, -20),
                 "warehouse": "Stores - " + ABBR, "project": pname},
                {"item_code": "BO-GEARMOTOR-5", "qty": 4, "schedule_date": add_days(TODAY, -15),
                 "warehouse": "Stores - " + ABBR, "project": pname},
            ],
        }, submit=True)

    for supplier, rates, score, comp, weeks, dev, recommended in [
        ("Suvarna Copper Moulds (DEMO)", {"BO-MOULD-TUBE": 192000, "BO-ROLL-SET": 168000, "BO-GEARMOTOR-5": 66000},
         8.5, "Fully compliant", 8, "", 1),
        ("Kalyani Gears & Drives (DEMO)", {"BO-MOULD-TUBE": 176000, "BO-ROLL-SET": 159000, "BO-GEARMOTOR-5": 61000},
         6.0, "Deviation", 12, "Mould tube taper not as per drawing; roll hardness 52 HRC vs 55 HRC asked", 0),
    ]:
        if frappe.db.exists("Supplier Quotation", {"supplier": supplier, "docstatus": 1}):
            continue
        ins({
            "doctype": "Supplier Quotation", "supplier": supplier, "company": COMPANY,
            "transaction_date": add_days(TODAY, -52), "valid_till": add_days(TODAY, 10),
            "technical_score": score, "technical_compliance": comp, "delivery_weeks": weeks,
            "deviations": dev, "recommended": recommended,
            "items": [{"item_code": c, "qty": q, "rate": rates[c], "project": pname,
                       "schedule_date": add_days(TODAY, -20), "warehouse": "Stores - " + ABBR}
                      for c, q in [("BO-MOULD-TUBE", 4), ("BO-ROLL-SET", 2), ("BO-GEARMOTOR-5", 4)]],
        }, submit=True)

    pcc_name = frappe.db.get_value("MSCAST PCC", {"project": pname}, "name")
    po = get_or_none("Purchase Order", {"supplier": "Suvarna Copper Moulds (DEMO)", "docstatus": 1})
    if not po:
        po = ins({
            "doctype": "Purchase Order", "supplier": "Suvarna Copper Moulds (DEMO)", "company": COMPANY,
            "transaction_date": add_days(TODAY, -48), "schedule_date": add_days(TODAY, -12),
            "mscast_pcc": pcc_name, "pcc_budget_amount": 4 * 185000 + 2 * 156000 + 4 * 62000,
            "pcc_variance_note": "Mould tube +3.8% over PCC: copper price revision accepted, recovered from contingency.",
            "items": [
                {"item_code": "BO-MOULD-TUBE", "qty": 4, "rate": 192000, "project": pname,
                 "schedule_date": add_days(TODAY, -12), "warehouse": "Stores - " + ABBR},
                {"item_code": "BO-ROLL-SET", "qty": 2, "rate": 168000, "project": pname,
                 "schedule_date": add_days(TODAY, -12), "warehouse": "Stores - " + ABBR},
                {"item_code": "BO-GEARMOTOR-5", "qty": 4, "rate": 66000, "project": pname,
                 "schedule_date": add_days(TODAY, -8), "warehouse": "Stores - " + ABBR},
            ],
        }, submit=True)

    if not frappe.db.exists("Purchase Order", {"supplier": "Pushkar Fabricators (DEMO)", "docstatus": 1}):
        ins({
            "doctype": "Purchase Order", "supplier": "Pushkar Fabricators (DEMO)", "company": COMPANY,
            "transaction_date": add_days(TODAY, -44), "schedule_date": add_days(TODAY, 8),
            "mscast_pcc": pcc_name, "pcc_budget_amount": 2 * 2100000,
            "items": [
                {"item_code": "ASM-WSU", "qty": 2, "rate": 1980000, "project": pname,
                 "schedule_date": add_days(TODAY, 8), "warehouse": "Vendor WIP - " + ABBR,
                 "description": "Fabrication & machining of WSU as per MSC-2601-WSU-10 R2; plates free issued by MSCAST"},
                {"item_code": "FAB-SPRAY-CHAMBER", "qty": 2, "rate": 258000, "project": pname,
                 "schedule_date": add_days(TODAY, 8), "warehouse": "Vendor WIP - " + ABBR},
            ],
        }, submit=True)
    return po.name


def p1_receipts_and_free_issue(pname, po_name):
    if not frappe.db.exists("Purchase Receipt", {"docstatus": 1}):
        po = frappe.get_doc("Purchase Order", po_name)
        pr = frappe.new_doc("Purchase Receipt")
        pr.supplier = po.supplier
        pr.company = COMPANY
        pr.set_posting_time = 1
        pr.posting_date = add_days(TODAY, -10)
        for it in po.items:
            pr.append("items", {
                "item_code": it.item_code, "qty": it.qty, "rate": it.rate,
                "warehouse": it.warehouse, "project": pname,
                "purchase_order": po.name, "purchase_order_item": it.name,
            })
        pr.flags.ignore_permissions = True
        pr.insert()
        pr.submit()

    if not frappe.db.exists("Stock Entry", {"stock_entry_type": "Material Receipt", "docstatus": 1}):
        ins({
            "doctype": "Stock Entry", "stock_entry_type": "Material Receipt", "company": COMPANY,
            "posting_date": add_days(TODAY, -40), "set_posting_time": 1,
            "items": [
                {"item_code": "RM-PLATE-40", "qty": 3200, "t_warehouse": "Stores - " + ABBR,
                 "basic_rate": 82, "project": pname},
                {"item_code": "RM-PLATE-20", "qty": 4000, "t_warehouse": "Stores - " + ABBR,
                 "basic_rate": 78, "project": pname},
                {"item_code": "RM-SECTION-ISMB", "qty": 6000, "t_warehouse": "Stores - " + ABBR,
                 "basic_rate": 74, "project": pname},
            ],
        }, submit=True)

    if not frappe.db.exists("Stock Entry", {"stock_entry_type": "Material Transfer", "docstatus": 1}):
        ins({
            "doctype": "Stock Entry", "stock_entry_type": "Material Transfer", "company": COMPANY,
            "posting_date": add_days(TODAY, -38), "set_posting_time": 1,
            "remarks": "Free issue to Pushkar Fabricators against PO for WSU fabrication (Annexure-I)",
            "items": [
                {"item_code": "RM-PLATE-40", "qty": 3200, "s_warehouse": "Stores - " + ABBR,
                 "t_warehouse": "Free Issue at Vendor - " + ABBR, "project": pname},
                {"item_code": "RM-SECTION-ISMB", "qty": 4200, "s_warehouse": "Stores - " + ABBR,
                 "t_warehouse": "Free Issue at Vendor - " + ABBR, "project": pname},
            ],
        }, submit=True)


def p1_inspection_brm_dispatch(pname):
    if not frappe.db.exists("MSCAST Inspection Plan", {"project": pname}):
        for sup, item, stage, pl, ac, res, obs in [
            ("Suvarna Copper Moulds (DEMO)", "Copper mould tubes 4 nos", "Pre-dispatch", -14, -13,
             "Accepted", "Dimensions and taper verified; MTC received."),
            ("Pushkar Fabricators (DEMO)", "WSU frame weld inspection", "In-process", -6, -6,
             "Accepted with deviation", "Two weld undercuts rectified and re-tested."),
            ("Pushkar Fabricators (DEMO)", "WSU assembly final", "Pre-dispatch", 12, None, "Pending", ""),
            ("Kalyani Gears & Drives (DEMO)", "Gearbox load test", "Third-party", 18, None, "Pending",
             "TPI by Precision Inspection Services."),
        ]:
            ins({
                "doctype": "MSCAST Inspection Plan", "project": pname, "supplier": sup,
                "item_or_assembly": item, "stage": stage, "planned_date": add_days(TODAY, pl),
                "actual_date": add_days(TODAY, ac) if ac is not None else None,
                "inspector": "MSCAST QC", "result": res, "observations": obs,
            })

    if not frappe.db.exists("MSCAST BRM", {"project": pname}):
        po_suv = frappe.db.get_value("Purchase Order", {"supplier": "Suvarna Copper Moulds (DEMO)"}, "name")
        po_pus = frappe.db.get_value("Purchase Order", {"supplier": "Pushkar Fabricators (DEMO)"}, "name")
        ins({
            "doctype": "MSCAST BRM", "supplier": "Suvarna Copper Moulds (DEMO)", "purchase_order": po_suv,
            "project": pname, "invoice_type": "Tax Invoice", "supplier_invoice_no": "SCM/26-27/0471",
            "supplier_invoice_date": add_days(TODAY, -9), "amount": 1370400,
            "qty_check": 1, "rate_check": 1, "inspection_check": 1, "delivery_check": 1,
            "status": "Certified", "certified_by": "Administrator",
            "certification_date": add_days(TODAY, -7),
            "remarks": "Certified for payment; material received and inspected.",
        })
        ins({
            "doctype": "MSCAST BRM", "supplier": "Pushkar Fabricators (DEMO)", "purchase_order": po_pus,
            "project": pname, "invoice_type": "Proforma", "supplier_invoice_no": "PF/PI/2026/118",
            "supplier_invoice_date": add_days(TODAY, -3), "amount": 990000,
            "qty_check": 1, "rate_check": 1, "inspection_check": 0, "delivery_check": 0,
            "status": "Pending",
            "remarks": "70% advance against proforma; awaiting stage inspection clearance.",
        })

    if not frappe.db.exists("MSCAST MDM", {"project": pname}):
        mdm = ins({
            "doctype": "MSCAST MDM", "project": pname, "supplier": "Suvarna Copper Moulds (DEMO)",
            "purchase_order": frappe.db.get_value("Purchase Order", {"supplier": "Suvarna Copper Moulds (DEMO)"}, "name"),
            "lot_no": "LOT-01 Mould & rolls", "scheduled_date": add_days(TODAY, -5), "status": "Dispatched",
            "items": [
                {"item_code": "BO-MOULD-TUBE", "description": "Copper mould tube 130 sq", "qty": 4, "uom": "Nos"},
                {"item_code": "BO-ROLL-SET", "description": "Withdrawal roll set", "qty": 2, "uom": "Set"},
                {"item_code": "RM-PLATE-20", "description": "MS plate 20 mm (free issue balance)", "qty": 800,
                 "uom": "Kg", "is_free_issue": 1},
            ],
            "remarks": "Direct dispatch from vendor works to customer site at Nagpur.",
        })
        ins({
            "doctype": "MSCAST Delivery Instruction", "mdm": mdm.name, "project": pname,
            "supplier": "Suvarna Copper Moulds (DEMO)", "consignee": CUST1 + " - Nagpur works",
            "transporter": "Vidarbha Heavy Transport (DEMO)", "vehicle_type": "Trailer 32 ft",
            "lr_no": "VHT/2026/8842", "dispatch_date": add_days(TODAY, -5), "status": "Delivered",
            "instructions": "Dispatch to site with packing list and test certificates. Insurance by MSCAST. "
                            "Unloading in customer scope. Send LR copy to projects@mcast.co.in same day.",
            "free_issue_annexure": "MS plate 20 mm - 800 kg (balance free issue material returned with lot)",
        })

    if not frappe.db.exists("MSCAST Project Certificate", {"project": pname}):
        ins({
            "doctype": "MSCAST Project Certificate", "project": pname, "customer": CUST1,
            "certificate_type": "Commissioning", "status": "Awaited",
            "issue_date": add_days(TODAY, 80), "retention_release_due": add_days(TODAY, 440),
            "notes": "Retention 10% released 12 months after commissioning certificate.",
        })


def p1_billing(pname, so_name):
    if not frappe.db.exists("Sales Invoice", {"customer": CUST1, "docstatus": 1}):
        si = frappe.new_doc("Sales Invoice")
        si.customer = CUST1
        si.company = COMPANY
        si.set_posting_time = 1
        si.posting_date = add_days(TODAY, -25)
        si.due_date = add_days(TODAY, 5)
        si.project = pname
        si.append("items", {
            "item_code": "SRV-DESIGN", "qty": 400, "rate": 1200, "uom": "Manhour",
            "conversion_factor": 1, "sales_order": so_name, "project": pname,
            "description": "Engineering design & drawing - milestone 1 (GA + detail drawings released)",
        })
        si.flags.ignore_permissions = True
        si.insert()
        si.submit()

    if not frappe.db.exists("Payment Entry", {"party": CUST1, "docstatus": 1}):
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Receive"
        pe.company = COMPANY
        pe.posting_date = add_days(TODAY, -110)
        pe.party_type = "Customer"
        pe.party = CUST1
        pe.paid_amount = 6900000
        pe.received_amount = 6900000
        pe.reference_no = "NEFT/SSL/8841"
        pe.reference_date = add_days(TODAY, -110)
        pe.paid_to = frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Bank", "is_group": 0}, "name")
        pe.paid_from = frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Receivable", "is_group": 0}, "name")
        pe.remarks = "30% advance against ABG as per Sales Order payment terms"
        pe.flags.ignore_permissions = True
        pe.insert()
        pe.submit()


# =====================================================================
# Project 2 + enquiries
# =====================================================================
def project2():
    so = get_or_none("Sales Order", {"customer": CUST2, "docstatus": 1})
    if not so:
        so = ins({
            "doctype": "Sales Order", "customer": CUST2, "company": COMPANY,
            "transaction_date": add_days(TODAY, -12), "delivery_date": add_days(TODAY, 160),
            "customer_po_no": "DEPL/PO/26/0098", "retention_percent": 5, "ld_percent": 0.5,
            "pbg_percent": 10, "contract_delivery_date": add_days(TODAY, 160),
            "items": [{"item_code": "ALBC-7", "qty": 1, "uom": "Set", "rate": 14200000,
                       "delivery_date": add_days(TODAY, 160), "conversion_factor": 1}],
        }, submit=True)

    pname = ensure_project({
        "doctype": "Project", "project_name": P2_NAME, "company": COMPANY, "status": "Open",
        "customer": CUST2, "sales_order": so.name, "project_type": "External",
        "expected_start_date": add_days(TODAY, -10), "expected_end_date": add_days(TODAY, 160),
        "contract_delivery_date": add_days(TODAY, 160), "machine_family": "Aluminium billet caster",
        "estimated_costing": 10800000,
    })
    frappe.db.set_value("Sales Order", so.name, "project", pname)

    if not frappe.db.exists("Task", {"project": pname}):
        for subj, s, e, status, prog in [
            ("Project kick-off & handover", -10, -8, "Completed", 100),
            ("Concept layout & customer approval", -7, 20, "Working", 40),
            ("Detail design", 20, 70, "Open", 0),
            ("Procurement of long-lead items", 15, 90, "Open", 0),
        ]:
            ins({"doctype": "Task", "subject": subj, "project": pname, "status": status,
                 "exp_start_date": add_days(TODAY, s), "exp_end_date": add_days(TODAY, e),
                 "progress": prog, "company": COMPANY})

    if not frappe.db.exists("MSCAST PCC", {"project": pname}):
        lines = [
            ("ASM-MOULD", "Casting table with hot-top moulds", "Casting Table", "Fabrication", 1, 1850000),
            ("BO-GRAPHITE-RING", "Graphite hot-top rings", "Casting Table", "Bought-out", 12, 42000),
            ("ASM-HYD-POWERPACK", "Hydraulic power pack with pit cylinder", "Hydraulics", "Bought-out", 1, 1650000),
            ("ASM-WATER-SYS", "Water system with cooling tower", "Water System", "Bought-out", 1, 1450000),
            ("ASM-MCC-PLC", "MCC with PLC & casting recipe HMI", "Electrical", "Bought-out", 1, 1580000),
            ("RM-PLATE-20", "MS plate 20 mm", "Structure", "Raw Material", 9000, 78),
        ]
        items = [{"item_code": c, "description": d, "assembly": a, "category": cat, "qty": q,
                  "uom": frappe.db.get_value("Item", c, "stock_uom"), "est_rate": r,
                  "est_amount": q * r} for c, d, a, cat, q, r in lines]
        pcc = ins({
            "doctype": "MSCAST PCC", "project": pname, "sales_order": so.name, "customer": CUST2,
            "revision": "R0", "status": "Draft", "prepared_by": "Administrator", "items": items,
            "total_estimated_cost": sum(i["est_amount"] for i in items),
            "contract_value": so.grand_total,
            "remarks": "Budgetary PCC pending vendor offers for hydraulics and water system.",
        })
        frappe.db.set_value("Project", pname, "mscast_pcc", pcc.name)

    if not frappe.db.exists("MSCAST Drawing", {"project": pname}):
        for no, title, asm, dtype, rev, status in [
            ("MSC-2607-GA-01", "General arrangement - aluminium billet caster", "Overall",
             "GA / Layout", "R1", "For Customer Approval"),
            ("MSC-2607-CT-10", "Casting table layout", "Casting Table", "Detail", "R0", "Draft"),
        ]:
            ins({"doctype": "MSCAST Drawing", "drawing_no": no, "title": title, "project": pname,
                 "assembly": asm, "drawing_type": dtype, "current_revision": rev, "status": status,
                 "revisions": [{"revision": "R0", "revision_date": add_days(TODAY, -6),
                                "change_description": "Initial issue", "issued_to": "Customer"}]})
    return pname


def open_enquiry_and_spares():
    if not frappe.db.exists("Lead", {"company_name": "Gulf Aluminium Industries LLC (DEMO)"}):
        ins({
            "doctype": "Lead", "lead_name": "Procurement Head",
            "company_name": "Gulf Aluminium Industries LLC (DEMO)", "status": "Open",
            "source": "Existing Customer", "country": "United Arab Emirates",
            "email_id": "buyer@example.com", "company": COMPANY,
        })
    if not frappe.db.exists("Opportunity", {"party_name": "Konark Alloys Pvt Ltd (DEMO)"}):
        ins({
            "doctype": "Opportunity", "opportunity_from": "Customer",
            "party_name": "Konark Alloys Pvt Ltd (DEMO)", "opportunity_type": "Sales",
            "company": COMPANY, "transaction_date": add_days(TODAY, -20),
            "expected_closing": add_days(TODAY, 20), "opportunity_amount": 1536000,
            "status": "Open", "items": [opp_item("SPR-MOULD-TUBE", 8, 192000)],
        })


def run():
    so1 = step("P1 lead->SO", p1_lead_to_so)
    if so1:
        pname = step("P1 project & tasks", p1_project, so1)
        if pname:
            step("P1 timesheets", p1_timesheets, pname)
            step("P1 PCC", p1_pcc, pname, so1)
            step("P1 drawings", p1_drawings, pname)
            step("P1 MDF", p1_mdf, pname)
            po = step("P1 procurement", p1_procurement, pname)
            if po:
                step("P1 receipts & free issue", p1_receipts_and_free_issue, pname, po)
            step("P1 inspection/BRM/dispatch", p1_inspection_brm_dispatch, pname)
            step("P1 billing", p1_billing, pname, so1)
    step("P2", project2)
    step("enquiries & spares", open_enquiry_and_spares)
    log("DONE")


run()
