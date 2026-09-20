"""MSCAST ERPNext POC - 02: MSCAST-specific doctypes and custom fields.

Creates Custom DocTypes (custom=1, module Custom) so no app/developer mode is needed:
  MSCAST PCC (+ Item)        Purchase Cost Calculation sheet
  MSCAST Drawing (+ Revision) drawing register with revision control
  MSCAST MDF (+ Item)        Material Data File / material list
  MSCAST BRM                 Billing Routing Memo
  MSCAST MDM (+ Item)        Material Dispatch Memo
  MSCAST Delivery Instruction
  MSCAST Inspection Plan
  MSCAST Project Certificate
plus custom fields for techno-commercial scoring, retention/LD/PBG, MSME, equipment-wise hours.
"""
import frappe

log = lambda m: print("[seed-02] " + m, flush=True)

PERMS = [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "submit": 0, "report": 1, "export": 1, "share": 1, "print": 1, "email": 1},
    {"role": "Projects Manager", "read": 1, "write": 1, "create": 1, "report": 1, "print": 1, "email": 1},
    {"role": "Purchase Manager", "read": 1, "write": 1, "create": 1, "report": 1, "print": 1, "email": 1},
    {"role": "Accounts User", "read": 1, "report": 1, "print": 1},
]


def doctype(name, fields, istable=0, title_field=None, search_fields=None, sort_field="modified"):
    if frappe.db.exists("DocType", name):
        log("exists: " + name)
        return
    d = frappe.get_doc({
        "doctype": "DocType",
        "name": name,
        "module": "Custom",
        "custom": 1,
        "istable": istable,
        "editable_grid": 1 if istable else 0,
        "track_changes": 0 if istable else 1,
        "quick_entry": 0,
        "allow_rename": 1,
        "title_field": title_field,
        "search_fields": search_fields,
        "sort_field": sort_field,
        "sort_order": "DESC",
        "fields": fields,
        "permissions": [] if istable else PERMS,
    })
    d.flags.ignore_permissions = True
    d.insert()
    log("created: " + name)


def f(fieldname, label, fieldtype, **kw):
    d = {"fieldname": fieldname, "label": label, "fieldtype": fieldtype}
    d.update(kw)
    return d


# ------------------------------------------------------------------ PCC
def pcc():
    doctype("MSCAST PCC Item", [
        f("item_code", "Item", "Link", options="Item", in_list_view=1, columns=2),
        f("description", "Description", "Data", in_list_view=1, columns=3),
        f("assembly", "Assembly", "Data"),
        f("category", "Category", "Select", options="Bought-out\nFabrication\nRaw Material\nService\nFreight", in_list_view=1, columns=1),
        f("qty", "Qty", "Float", default="1", in_list_view=1, columns=1),
        f("uom", "UOM", "Link", options="UOM"),
        f("est_rate", "Est. Rate", "Currency", in_list_view=1, columns=1),
        f("est_amount", "Est. Amount", "Currency", in_list_view=1, columns=2, read_only=0),
        f("approved_make", "Approved Make", "Data"),
        f("lead_time_days", "Lead Time (days)", "Int"),
    ], istable=1)

    doctype("MSCAST PCC", [
        f("naming_series", "Series", "Select", options="PCC-.YYYY.-", default="PCC-.YYYY.-", reqd=1),
        f("project", "Project", "Link", options="Project", in_standard_filter=1),
        f("sales_order", "Sales Order", "Link", options="Sales Order"),
        f("customer", "Customer", "Link", options="Customer", fetch_from="sales_order.customer"),
        f("cb0", "", "Column Break"),
        f("revision", "Revision", "Data", default="R0"),
        f("status", "Status", "Select", options="Draft\nApproved\nSuperseded", default="Draft", in_list_view=1, in_standard_filter=1),
        f("prepared_by", "Prepared By", "Link", options="User"),
        f("approved_by", "Approved By", "Link", options="User"),
        f("sb0", "Cost Build-up", "Section Break"),
        f("items", "Components", "Table", options="MSCAST PCC Item"),
        f("sb1", "", "Section Break"),
        f("total_estimated_cost", "Total Estimated Cost", "Currency", read_only=1, in_list_view=1),
        f("contract_value", "Contract Value", "Currency", fetch_from="sales_order.grand_total", read_only=1),
        f("cb1", "", "Column Break"),
        f("target_margin_pct", "Target Margin %", "Percent", read_only=1),
        f("remarks", "Remarks", "Small Text"),
    ], title_field="project", search_fields="project,sales_order,status")


# -------------------------------------------------------------- drawings
def drawings():
    doctype("MSCAST Drawing Revision", [
        f("revision", "Rev", "Data", in_list_view=1, columns=1),
        f("revision_date", "Date", "Date", in_list_view=1, columns=2),
        f("change_description", "Change Description", "Small Text", in_list_view=1, columns=5),
        f("issued_to", "Issued To", "Data", in_list_view=1, columns=2),
        f("attachment", "File", "Attach"),
    ], istable=1)

    doctype("MSCAST Drawing", [
        f("naming_series", "Series", "Select", options="DRG-.YYYY.-", default="DRG-.YYYY.-", reqd=1),
        f("drawing_no", "Drawing No", "Data", reqd=1, in_list_view=1, in_standard_filter=1),
        f("title", "Title", "Data", in_list_view=1),
        f("project", "Project", "Link", options="Project", in_standard_filter=1),
        f("assembly", "Assembly", "Data"),
        f("cb0", "", "Column Break"),
        f("current_revision", "Current Revision", "Data", default="R0", in_list_view=1),
        f("status", "Status", "Select",
          options="Draft\nFor Customer Approval\nApproved by Customer\nReleased for Manufacture\nSuperseded",
          default="Draft", in_list_view=1, in_standard_filter=1),
        f("drawing_type", "Type", "Select", options="GA / Layout\nDetail\nHydraulic Circuit\nP&ID\nElectrical\nErection"),
        f("drive_link", "Google Drive Link", "Data"),
        f("sb0", "Revision History", "Section Break"),
        f("revisions", "Revisions", "Table", options="MSCAST Drawing Revision"),
        f("sb1", "Transmittal", "Section Break"),
        f("issued_to_vendors", "Issued to Vendors", "Small Text"),
        f("remarks", "Remarks", "Small Text"),
    ], title_field="drawing_no", search_fields="drawing_no,title,project,status")


# ------------------------------------------------------------------- MDF
def mdf():
    doctype("MSCAST MDF Item", [
        f("item_code", "Item", "Link", options="Item", in_list_view=1, columns=2),
        f("description", "Description", "Data", in_list_view=1, columns=3),
        f("drawing_no", "Drawing No", "Data", in_list_view=1, columns=2),
        f("material_spec", "Material Spec", "Data"),
        f("qty", "Qty", "Float", default="1", in_list_view=1, columns=1),
        f("uom", "UOM", "Link", options="UOM"),
        f("weight_kg", "Weight (kg)", "Float"),
        f("category", "Category", "Select", options="Fabrication\nBought-out\nRaw Material", in_list_view=1, columns=2),
    ], istable=1)

    doctype("MSCAST MDF", [
        f("naming_series", "Series", "Select", options="MDF-.YYYY.-", default="MDF-.YYYY.-", reqd=1),
        f("project", "Project", "Link", options="Project", in_standard_filter=1),
        f("assembly", "Assembly", "Data", in_list_view=1),
        f("drawing", "Drawing", "Link", options="MSCAST Drawing"),
        f("cb0", "", "Column Break"),
        f("status", "Status", "Select", options="Draft\nReleased to Procurement\nOrdered\nClosed",
          default="Draft", in_list_view=1, in_standard_filter=1),
        f("released_on", "Released On", "Date"),
        f("prepared_by", "Prepared By", "Link", options="User"),
        f("sb0", "Material List", "Section Break"),
        f("items", "Items", "Table", options="MSCAST MDF Item"),
        f("remarks", "Remarks", "Small Text"),
    ], title_field="assembly", search_fields="project,assembly,status")


# ------------------------------------------------------------------- BRM
def brm():
    doctype("MSCAST BRM", [
        f("naming_series", "Series", "Select", options="BRM-.YYYY.-", default="BRM-.YYYY.-", reqd=1),
        f("supplier", "Supplier", "Link", options="Supplier", reqd=1, in_list_view=1, in_standard_filter=1),
        f("purchase_order", "Purchase Order", "Link", options="Purchase Order", in_list_view=1),
        f("project", "Project", "Link", options="Project", in_standard_filter=1),
        f("cb0", "", "Column Break"),
        f("invoice_type", "Invoice Type", "Select", options="Tax Invoice\nProforma\nInternal Memo Invoice", default="Tax Invoice"),
        f("supplier_invoice_no", "Supplier Invoice No", "Data"),
        f("supplier_invoice_date", "Supplier Invoice Date", "Date"),
        f("amount", "Amount", "Currency", in_list_view=1),
        f("sb0", "Certification", "Section Break"),
        f("qty_check", "Qty as per PO", "Check"),
        f("rate_check", "Rate as per PO", "Check"),
        f("inspection_check", "Inspection cleared", "Check"),
        f("delivery_check", "Delivered as per DI", "Check"),
        f("cb1", "", "Column Break"),
        f("status", "Status", "Select", options="Pending\nCertified\nRejected\nPaid", default="Pending",
          in_list_view=1, in_standard_filter=1),
        f("certified_by", "Certified By", "Link", options="User"),
        f("certification_date", "Certification Date", "Date"),
        f("remarks", "Remarks", "Small Text"),
    ], title_field="supplier", search_fields="supplier,purchase_order,project,status")


# ------------------------------------------------------- MDM + DI + insp
def dispatch():
    doctype("MSCAST MDM Item", [
        f("item_code", "Item", "Link", options="Item", in_list_view=1, columns=2),
        f("description", "Description", "Data", in_list_view=1, columns=4),
        f("qty", "Qty", "Float", default="1", in_list_view=1, columns=1),
        f("uom", "UOM", "Link", options="UOM", in_list_view=1, columns=1),
        f("is_free_issue", "Free Issue (Annexure-I)", "Check", in_list_view=1, columns=1),
        f("remarks", "Remarks", "Data"),
    ], istable=1)

    doctype("MSCAST MDM", [
        f("naming_series", "Series", "Select", options="MDM-.YYYY.-", default="MDM-.YYYY.-", reqd=1),
        f("project", "Project", "Link", options="Project", reqd=1, in_standard_filter=1),
        f("supplier", "Dispatching Supplier", "Link", options="Supplier", in_list_view=1),
        f("purchase_order", "Purchase Order", "Link", options="Purchase Order"),
        f("cb0", "", "Column Break"),
        f("lot_no", "Dispatch Lot", "Data", in_list_view=1),
        f("scheduled_date", "Scheduled Dispatch Date", "Date", in_list_view=1),
        f("status", "Status", "Select", options="Draft\nIssued\nDispatched\nClosed", default="Draft",
          in_list_view=1, in_standard_filter=1),
        f("sb0", "Items", "Section Break"),
        f("items", "Items", "Table", options="MSCAST MDM Item"),
        f("remarks", "Remarks", "Small Text"),
    ], title_field="project", search_fields="project,supplier,lot_no,status")

    doctype("MSCAST Delivery Instruction", [
        f("naming_series", "Series", "Select", options="DI-.YYYY.-", default="DI-.YYYY.-", reqd=1),
        f("mdm", "Material Dispatch Memo", "Link", options="MSCAST MDM", in_list_view=1),
        f("project", "Project", "Link", options="Project", fetch_from="mdm.project", in_standard_filter=1),
        f("supplier", "Supplier", "Link", options="Supplier", fetch_from="mdm.supplier", in_list_view=1),
        f("cb0", "", "Column Break"),
        f("consignee", "Consignee / Site", "Data", in_list_view=1),
        f("transporter", "Transporter", "Link", options="Supplier"),
        f("vehicle_type", "Vehicle Type", "Data"),
        f("lr_no", "LR No", "Data"),
        f("dispatch_date", "Dispatch Date", "Date", in_list_view=1),
        f("status", "Status", "Select", options="Issued\nAcknowledged\nDispatched\nDelivered", default="Issued",
          in_list_view=1, in_standard_filter=1),
        f("sb0", "Instructions", "Section Break"),
        f("instructions", "Instructions to Supplier", "Small Text"),
        f("free_issue_annexure", "Annexure-I (Free Issue List)", "Small Text"),
    ], title_field="consignee", search_fields="project,supplier,lr_no,status")

    doctype("MSCAST Inspection Plan", [
        f("naming_series", "Series", "Select", options="INSP-.YYYY.-", default="INSP-.YYYY.-", reqd=1),
        f("project", "Project", "Link", options="Project", in_standard_filter=1),
        f("purchase_order", "Purchase Order", "Link", options="Purchase Order"),
        f("supplier", "Supplier", "Link", options="Supplier", in_list_view=1),
        f("item_or_assembly", "Item / Assembly", "Data", in_list_view=1),
        f("cb0", "", "Column Break"),
        f("stage", "Stage", "Select", options="In-process\nPre-dispatch\nThird-party\nCustomer", default="Pre-dispatch", in_list_view=1),
        f("planned_date", "Planned Date", "Date", in_list_view=1),
        f("actual_date", "Actual Date", "Date"),
        f("inspector", "Inspector", "Data"),
        f("result", "Result", "Select", options="Pending\nAccepted\nAccepted with deviation\nRejected",
          default="Pending", in_list_view=1, in_standard_filter=1),
        f("sb0", "Observations", "Section Break"),
        f("observations", "Observations", "Small Text"),
    ], title_field="item_or_assembly", search_fields="project,supplier,stage,result")

    doctype("MSCAST Project Certificate", [
        f("naming_series", "Series", "Select", options="CERT-.YYYY.-", default="CERT-.YYYY.-", reqd=1),
        f("project", "Project", "Link", options="Project", reqd=1, in_list_view=1, in_standard_filter=1),
        f("customer", "Customer", "Link", options="Customer", in_list_view=1),
        f("certificate_type", "Type", "Select",
          options="Commissioning\nPreliminary Acceptance\nFinal Acceptance\nCompletion", in_list_view=1),
        f("cb0", "", "Column Break"),
        f("issue_date", "Issue Date", "Date", in_list_view=1),
        f("status", "Status", "Select", options="Awaited\nReceived", default="Awaited", in_list_view=1, in_standard_filter=1),
        f("retention_release_due", "Retention Release Due", "Date"),
        f("reference", "Customer Reference", "Data"),
        f("sb0", "Notes", "Section Break"),
        f("notes", "Notes", "Small Text"),
    ], title_field="project", search_fields="project,certificate_type,status")


# --------------------------------------------------------- custom fields
CUSTOM_FIELDS = {
    "Supplier Quotation": [
        f("mscast_sb", "Techno-commercial Evaluation", "Section Break", insert_after="terms"),
        f("technical_score", "Technical Score (0-10)", "Float", insert_after="mscast_sb"),
        f("technical_compliance", "Technical Compliance", "Select",
          options="\nFully compliant\nDeviation\nNot compliant", insert_after="technical_score"),
        f("delivery_weeks", "Delivery (weeks)", "Int", insert_after="technical_compliance"),
        f("mscast_cb", "", "Column Break", insert_after="delivery_weeks"),
        f("deviations", "Deviations from Specification", "Small Text", insert_after="mscast_cb"),
        f("recommended", "Recommended", "Check", insert_after="deviations"),
    ],
    "Sales Order": [
        f("mscast_sb", "MSCAST Commercial Terms", "Section Break", insert_after="terms"),
        f("mscast_pcc", "PCC", "Link", options="MSCAST PCC", insert_after="mscast_sb"),
        f("retention_percent", "Retention %", "Percent", insert_after="mscast_pcc"),
        f("ld_percent", "LD % per week", "Percent", insert_after="retention_percent"),
        f("mscast_cb", "", "Column Break", insert_after="ld_percent"),
        f("pbg_percent", "PBG %", "Percent", insert_after="mscast_cb"),
        f("contract_delivery_date", "Contract Delivery Date", "Date", insert_after="pbg_percent"),
        f("customer_po_no", "Customer PO No", "Data", insert_after="contract_delivery_date"),
    ],
    "Project": [
        f("mscast_sb", "MSCAST", "Section Break", insert_after="notes"),
        f("mscast_pcc", "PCC", "Link", options="MSCAST PCC", insert_after="mscast_sb"),
        f("contract_delivery_date", "Contract Delivery Date", "Date", insert_after="mscast_pcc"),
        f("mscast_cb", "", "Column Break", insert_after="contract_delivery_date"),
        f("retention_amount", "Retention Amount", "Currency", insert_after="mscast_cb"),
        f("machine_family", "Machine Family", "Data", insert_after="retention_amount"),
    ],
    "Purchase Order": [
        f("mscast_sb", "MSCAST", "Section Break", insert_after="terms"),
        f("mscast_pcc", "PCC Reference", "Link", options="MSCAST PCC", insert_after="mscast_sb"),
        f("pcc_budget_amount", "PCC Budget for this scope", "Currency", insert_after="mscast_pcc"),
        f("mscast_cb", "", "Column Break", insert_after="pcc_budget_amount"),
        f("pcc_variance_note", "Variance Justification", "Small Text", insert_after="mscast_cb"),
    ],
    "Supplier": [
        f("mscast_sb", "MSME / Udyam", "Section Break", insert_after="tax_id"),
        f("msme_udyam_no", "Udyam Registration No", "Data", insert_after="mscast_sb"),
        f("msme_type", "MSME Type", "Select", options="\nMicro\nSmall\nMedium\nNot registered",
          insert_after="msme_udyam_no"),
        f("mscast_cb", "", "Column Break", insert_after="msme_type"),
        f("capability", "Capability", "Data", insert_after="mscast_cb"),
    ],
    "Timesheet Detail": [
        f("equipment", "Equipment / Assembly", "Data", insert_after="project"),
    ],
    "Delivery Note": [
        f("mscast_di", "Delivery Instruction", "Link", options="MSCAST Delivery Instruction", insert_after="project"),
    ],
}


def custom_fields():
    from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
    create_custom_fields(CUSTOM_FIELDS, ignore_validate=True)
    log("custom fields created for %d doctypes" % len(CUSTOM_FIELDS))


def run():
    pcc()
    drawings()
    mdf()
    brm()
    dispatch()
    custom_fields()
    frappe.db.commit()
    frappe.clear_cache()
    log("DONE")


run()
