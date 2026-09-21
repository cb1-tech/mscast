"""Make the demo's people and numbers tell the story the system is built for.

Found by the demo screenshot run, 21 Sep 2026, looking at the screens as MSCAST
would:
  - every cost sheet was 'prepared by Administrator, approved by Administrator',
    which undercuts the one control the demo leads with - a director approves;
  - PROJ-0003 (the Ambika revamp) had no cost sheet at all, so the MD's home page
    showed its cost as Rs 0 and its margin as 100% - the first card on screen;
  - BRMs had no certifier, or 'Administrator'.
Demo data only; no configuration changes. Idempotent.
"""
import frappe
log = lambda m: print("[190] " + m, flush=True)
ROHIT, MUSTAQUE, AIQAZ = "autoelectron.jp@gmail.com", "latookaushik@yahoo.com", "latookaushik@hotmail.com"
frappe.flags.ignore_permissions = True

# 1. who prepared and approved each cost sheet
for pcc, approver in (("PCC-2026-00001", MUSTAQUE), ("PCC-2026-00002", AIQAZ)):
    frappe.db.set_value("MSCAST PCC", pcc, {"prepared_by": ROHIT, "approved_by": approver}, update_modified=False)
    log("%s: prepared by Rohit Kulkarni, approved by %s" % (pcc, frappe.db.get_value("User", approver, "full_name")))

# 2. a cost sheet for the Ambika revamp (SO net Rs 38.35 L: 250 revamp man-days + 40 commissioning)
if not frappe.db.exists("MSCAST PCC", {"project": "PROJ-0003"}):
    ref = frappe.get_doc("MSCAST PCC", "PCC-2026-00002")
    cats = [c.strip() for c in (frappe.get_meta("MSCAST PCC Item").get_field("category").options or "").split("\n") if c.strip()]
    pick = lambda *want: next((c for w in want for c in cats if w.lower() in c.lower()), cats[0] if cats else None)
    rows = [
        ("SRV-REVAMP", "Revamp engineering and site labour (man-days)", pick("labour", "service", "site"), 250, 7800),
        ("SRV-COMMISSION", "Commissioning engineers at site (man-days)", pick("labour", "service", "site"), 40, 6500),
        ("BO-MOULD-TUBE", "Copper mould tubes - replacement set", pick("bought"), 4, 185000),
        ("BO-ROLL-SET", "Withdrawal roll set - refurbishment", pick("bought"), 1, 156000),
    ]
    d = frappe.get_doc({
        "doctype": "MSCAST PCC", "naming_series": ref.naming_series, "project": "PROJ-0003",
        "sales_order": "SAL-ORD-2026-00003", "customer": "Ambika Steel Rolling Mills (DEMO)",
        "revision": "R0", "prepared_by": ROHIT, "approved_by": MUSTAQUE,
        "contract_value": 3835000, "remarks": "Revamp of an existing caster: labour-led, two bought-out packages.",
        "items": [{"item_code": i, "description": ds, "category": c, "qty": q, "est_rate": r, "est_amount": q * r}
                  for i, ds, c, q, r in rows],
    })
    d.flags.ignore_permissions = True; d.flags.ignore_links = True
    d.insert()
    cost = sum(q * r for _, _, _, q, r in rows)
    frappe.db.set_value("MSCAST PCC", d.name, {"status": "Approved", "workflow_state": "Approved",
        "total_estimated_cost": cost, "target_margin_pct": round((3835000 - cost) * 100.0 / 3835000, 1),
        "docstatus": ref.docstatus}, update_modified=False)
    if ref.docstatus:
        frappe.db.sql("update `tabMSCAST PCC Item` set docstatus=%s where parent=%s", (ref.docstatus, d.name))
    log("%s created for PROJ-0003: cost Rs %s against contract Rs 38.35 L (margin %.1f%%)"
        % (d.name, "{:,}".format(cost), (3835000 - cost) * 100.0 / 3835000))
else:
    log("PROJ-0003 already has a cost sheet")

# 3. who certified each BRM
for brm, who in (("BRM-2026-00001", AIQAZ), ("BRM-2026-00002", MUSTAQUE), ("BRM-2026-00003", MUSTAQUE)):
    frappe.db.set_value("MSCAST BRM", brm, "certified_by", who, update_modified=False)
# a certified BRM records the four checks that justified it, and when
CERT_DATE = {"BRM-2026-00001": "2026-09-10", "BRM-2026-00002": "2026-09-14", "BRM-2026-00003": "2026-08-24"}
for brm, d in CERT_DATE.items():
    frappe.db.set_value("MSCAST BRM", brm, {"qty_check": 1, "rate_check": 1, "inspection_check": 1,
                        "delivery_check": 1, "certification_date": d}, update_modified=False)
    po = frappe.db.get_value("MSCAST BRM", brm, "purchase_order")
    if not po:
        sup = frappe.db.get_value("MSCAST BRM", brm, "supplier")
        po = frappe.db.get_value("Purchase Order", {"supplier": sup, "docstatus": 1}, "name")
        if po:
            frappe.db.set_value("MSCAST BRM", brm, "purchase_order", po, update_modified=False)
log("BRMs certified by the directors, with their four checks and a certification date")
frappe.db.commit()
