"""MSCAST ERPNext POC - 04: query reports + MSCAST workspace."""
import json
import frappe

log = lambda m: print("[seed-04] " + m, flush=True)
COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"

REPORTS = [
    ("MSCAST PO vs PCC Variance", "MSCAST PCC", """
select
    p.project        as "Project:Link/Project:220",
    p.name           as "PCC:Link/MSCAST PCC:110",
    p.revision       as "Rev::50",
    p.total_estimated_cost as "PCC Estimate:Currency:130",
    ifnull(po.committed, 0) as "PO Committed:Currency:130",
    (ifnull(po.committed,0) - p.total_estimated_cost) as "Variance:Currency:120",
    round(ifnull(po.committed,0) / nullif(p.total_estimated_cost,0) * 100, 1) as "Committed %%:Float:100",
    ifnull(gl.actual, 0) as "Actual Cost (GL):Currency:140"
from `tabMSCAST PCC` p
left join (
    select poi.project, sum(poi.base_amount) as committed
    from `tabPurchase Order Item` poi
    inner join `tabPurchase Order` po on po.name = poi.parent and po.docstatus = 1
    group by poi.project
) po on po.project = p.project
left join (
    select project, sum(debit - credit) as actual
    from `tabGL Entry` where docstatus = 1 and ifnull(project,'') != '' and is_cancelled = 0
    group by project
) gl on gl.project = p.project
where p.status != 'Superseded'
order by p.project
"""),
    ("MSCAST Project MIS", "Project", """
select
    pr.name                as "Project:Link/Project:230",
    pr.customer            as "Customer:Link/Customer:200",
    pr.status              as "Status::80",
    pr.contract_delivery_date as "Contract Delivery:Date:120",
    ifnull(so.contract_value,0)  as "Contract Value:Currency:130",
    ifnull(pcc.est,0)            as "PCC Estimate:Currency:130",
    ifnull(po.committed,0)       as "PO Committed:Currency:130",
    ifnull(si.billed,0)          as "Billed:Currency:120",
    ifnull(ts.hours,0)           as "Engg Hours:Float:100",
    round((ifnull(so.contract_value,0) - ifnull(pcc.est,0)) / nullif(so.contract_value,0) * 100, 1)
                                 as "Est. Margin %%:Float:110"
from `tabProject` pr
left join (select name, project, grand_total as contract_value from `tabSales Order` where docstatus=1) so
       on so.project = pr.name or so.name = pr.sales_order
left join (select project, sum(total_estimated_cost) est from `tabMSCAST PCC` where status='Approved' group by project) pcc
       on pcc.project = pr.name
left join (select poi.project, sum(poi.base_amount) committed from `tabPurchase Order Item` poi
           inner join `tabPurchase Order` po on po.name=poi.parent and po.docstatus=1 group by poi.project) po
       on po.project = pr.name
left join (select sii.project, sum(sii.base_amount) billed from `tabSales Invoice Item` sii
           inner join `tabSales Invoice` si on si.name=sii.parent and si.docstatus=1 group by sii.project) si
       on si.project = pr.name
left join (select project, sum(hours) hours from `tabTimesheet Detail` group by project) ts
       on ts.project = pr.name
order by pr.creation desc
"""),
    ("MSCAST Free Issue at Vendor", "Bin", """
select
    b.item_code   as "Item:Link/Item:160",
    i.item_name   as "Description::260",
    b.warehouse   as "Warehouse:Link/Warehouse:180",
    b.actual_qty  as "Qty at Vendor:Float:110",
    b.stock_uom   as "UOM::70",
    b.stock_value as "Value:Currency:120"
from `tabBin` b inner join `tabItem` i on i.name = b.item_code
where b.warehouse like 'Free Issue%%' and b.actual_qty != 0
order by b.stock_value desc
"""),
    ("MSCAST Drawing Register", "MSCAST Drawing", """
select
    d.drawing_no        as "Drawing No:Link/MSCAST Drawing:150",
    d.title             as "Title::280",
    d.project           as "Project:Link/Project:200",
    d.assembly          as "Assembly::120",
    d.drawing_type      as "Type::120",
    d.current_revision  as "Rev::60",
    d.status            as "Status::170",
    (select max(revision_date) from `tabMSCAST Drawing Revision` r where r.parent = d.name)
                        as "Last Revised:Date:110"
from `tabMSCAST Drawing` d
order by d.project, d.drawing_no
"""),
    ("MSCAST Dispatch Schedule", "Sales Order", """
select
    soi.parent        as "Sales Order:Link/Sales Order:140",
    so.customer       as "Customer:Link/Customer:200",
    soi.item_code     as "Item:Link/Item:150",
    soi.delivery_date as "Scheduled:Date:100",
    soi.qty           as "Qty:Float:80",
    soi.delivered_qty as "Delivered:Float:90",
    (soi.qty - soi.delivered_qty) as "Pending:Float:80",
    case when soi.delivered_qty >= soi.qty then 'Delivered'
         when soi.delivery_date < curdate() then 'OVERDUE'
         else 'On schedule' end as "Status::110",
    so.contract_delivery_date as "Contract Date:Date:110",
    so.ld_percent     as "LD %%/week:Float:90"
from `tabSales Order Item` soi
inner join `tabSales Order` so on so.name = soi.parent and so.docstatus = 1
order by soi.delivery_date
"""),
    ("MSCAST Retention and Certificates", "Sales Order", """
select
    so.name        as "Sales Order:Link/Sales Order:140",
    so.customer    as "Customer:Link/Customer:200",
    so.grand_total as "Order Value:Currency:130",
    so.retention_percent as "Retention %%:Float:90",
    so.grand_total * ifnull(so.retention_percent,0) / 100 as "Retention Amount:Currency:140",
    so.pbg_percent as "PBG %%:Float:80",
    c.certificate_type as "Certificate::150",
    c.status       as "Cert Status::100",
    c.retention_release_due as "Retention Due:Date:120"
from `tabSales Order` so
left join `tabMSCAST Project Certificate` c on c.customer = so.customer
where so.docstatus = 1 and ifnull(so.retention_percent,0) > 0
order by so.transaction_date desc
"""),
    ("MSCAST BRM Register", "MSCAST BRM", """
select
    b.name as "BRM:Link/MSCAST BRM:110",
    b.supplier as "Supplier:Link/Supplier:220",
    b.project as "Project:Link/Project:200",
    b.purchase_order as "PO:Link/Purchase Order:140",
    b.invoice_type as "Invoice Type::130",
    b.supplier_invoice_no as "Supplier Inv::130",
    b.supplier_invoice_date as "Inv Date:Date:100",
    b.amount as "Amount:Currency:120",
    b.status as "Status::90",
    b.certification_date as "Certified On:Date:110"
from `tabMSCAST BRM` b order by b.supplier_invoice_date desc
"""),
    ("MSCAST Inspection Status", "MSCAST Inspection Plan", """
select
    p.name as "Plan:Link/MSCAST Inspection Plan:110",
    p.project as "Project:Link/Project:200",
    p.supplier as "Supplier:Link/Supplier:220",
    p.item_or_assembly as "Item / Assembly::220",
    p.stage as "Stage::110",
    p.planned_date as "Planned:Date:100",
    p.actual_date as "Actual:Date:100",
    p.result as "Result::150"
from `tabMSCAST Inspection Plan` p order by p.planned_date
"""),
]


def make_reports():
    for name, ref_dt, query in REPORTS:
        if frappe.db.exists("Report", name):
            frappe.db.set_value("Report", name, "query", query)
            log("updated report: " + name)
            continue
        d = frappe.get_doc({
            "doctype": "Report", "report_name": name, "ref_doctype": ref_dt,
            "report_type": "Query Report", "is_standard": "No", "module": "Custom",
            "query": query, "disabled": 0,
            "roles": [{"role": "System Manager"}, {"role": "Projects Manager"},
                      {"role": "Purchase Manager"}, {"role": "Accounts User"}],
        })
        d.flags.ignore_permissions = True
        d.insert()
        log("created report: " + name)


SHORTCUTS = [
    ("MSCAST PCC", "DocType", "Blue"), ("MSCAST Drawing", "DocType", "Green"),
    ("MSCAST MDF", "DocType", "Orange"), ("MSCAST BRM", "DocType", "Red"),
    ("MSCAST MDM", "DocType", "Purple"), ("MSCAST Delivery Instruction", "DocType", "Cyan"),
    ("Project", "DocType", "Grey"), ("MSCAST Project MIS", "Report", "Yellow"),
]

CARDS = [
    ("Engineering", [("MSCAST Drawing", "DocType"), ("MSCAST MDF", "DocType"),
                     ("Timesheet", "DocType"), ("MSCAST Drawing Register", "Report")]),
    ("Sales & Projects", [("Opportunity", "DocType"), ("Quotation", "DocType"),
                          ("Sales Order", "DocType"), ("Project", "DocType"),
                          ("MSCAST PCC", "DocType"), ("MSCAST Project Certificate", "DocType"),
                          ("MSCAST Project MIS", "Report")]),
    ("Procurement", [("Material Request", "DocType"), ("Request for Quotation", "DocType"),
                     ("Supplier Quotation", "DocType"), ("Purchase Order", "DocType"),
                     ("MSCAST BRM", "DocType"), ("MSCAST Inspection Plan", "DocType"),
                     ("MSCAST PO vs PCC Variance", "Report")]),
    ("Dispatch & Stock", [("MSCAST MDM", "DocType"), ("MSCAST Delivery Instruction", "DocType"),
                          ("Delivery Note", "DocType"), ("Stock Entry", "DocType"),
                          ("MSCAST Free Issue at Vendor", "Report"),
                          ("MSCAST Dispatch Schedule", "Report")]),
    ("Commercial", [("Sales Invoice", "DocType"), ("Payment Entry", "DocType"),
                    ("MSCAST Retention and Certificates", "Report"),
                    ("MSCAST BRM Register", "Report")]),
]


def make_workspace():
    if frappe.db.exists("Workspace", "MSCAST"):
        frappe.delete_doc("Workspace", "MSCAST", force=1, ignore_permissions=True)
    content = [{"id": "hdr1", "type": "header",
                "data": {"text": "<span class=\"h4\"><b>MSCAST ERP - POC</b></span>", "col": 12}}]
    for label, _t, _c in SHORTCUTS:
        content.append({"id": "sc-" + label.replace(" ", "-"), "type": "shortcut",
                        "data": {"shortcut_name": label, "col": 3}})
    content.append({"id": "sp1", "type": "spacer", "data": {"col": 12}})
    for card, _ in CARDS:
        content.append({"id": "cd-" + card.replace(" ", "-").replace("&", "and"),
                        "type": "card", "data": {"card_name": card, "col": 4}})

    ws = frappe.get_doc({
        "doctype": "Workspace", "name": "MSCAST", "label": "MSCAST", "title": "MSCAST",
        "module": "Custom", "public": 1, "icon": "tool", "sequence_id": 1.0,
        "content": json.dumps(content),
        "shortcuts": [{"type": t, "link_to": n, "label": n, "color": c} for n, t, c in SHORTCUTS],
        "links": [],
    })
    for card, links in CARDS:
        ws.append("links", {"type": "Card Break", "label": card, "hidden": 0,
                            "link_count": len(links), "onboard": 0})
        for name, ltype in links:
            ws.append("links", {"type": "Link", "label": name, "link_type": ltype,
                                "link_to": name, "hidden": 0, "onboard": 0, "is_query_report":
                                1 if ltype == "Report" else 0})
    ws.flags.ignore_permissions = True
    ws.insert()
    log("workspace created")


def system_settings():
    ss = frappe.get_single("System Settings")
    ss.country = "India"
    ss.time_zone = "Asia/Kolkata"
    ss.date_format = "dd-mm-yyyy"
    ss.number_format = "#,###.##"
    ss.currency_precision = "2"
    ss.float_precision = "3"
    ss.save(ignore_permissions=True)
    log("system settings: India / Asia/Kolkata / dd-mm-yyyy")


def run():
    make_reports()
    make_workspace()
    system_settings()
    frappe.db.commit()
    frappe.clear_cache()
    log("DONE")


run()
