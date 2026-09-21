# -*- coding: utf-8 -*-
import frappe, json

D = "DocType"; R = "Report"; P = "Page"

SPACES = [
    ("MSCAST Sales", "Sales & estimation", "sell", "blue", 1.0,
     ["Sales Manager", "Sales User", "MSCAST Director", "Accounts Manager"],
     [("Enquiry to order", [(D, "Lead"), (D, "Opportunity"), (D, "Quotation"), (D, "Sales Order"), (D, "Customer")]),
      ("Estimation", [(D, "MSCAST PCC"), (R, "MSCAST PO vs PCC Variance")]),
      ("Billing", [(R, "MSCAST Billing and Dispatch Schedule"), (D, "Sales Invoice"), (R, "MSCAST SO - PO - Invoice Tracker")])]),

    ("MSCAST Projects", "Projects & design", "project", "blue", 2.0,
     ["Projects User", "Projects Manager", "MSCAST Director"],
     [("Execution", [(D, "Project"), (D, "Task"), (D, "MSCAST Project Kickoff"), (D, "MSCAST Project Certificate"), (D, "MSCAST Client Claim")]),
      ("Design", [(D, "MSCAST Drawing"), (D, "MSCAST MDF"), (D, "MSCAST Transmittal"), (R, "MSCAST Drawing Register")]),
      ("Site", [(D, "MSCAST Commissioning Report"), (D, "MSCAST Spares Handover"), (D, "Warranty Claim"), (D, "Timesheet")]),
      ("Reports", [(R, "MSCAST Project MIS"), (R, "MSCAST Project Closure Report"), (R, "MSCAST Project WIP Valuation")])]),

    ("MSCAST Purchase", "Purchase & vendors", "buying", "blue", 3.0,
     ["Purchase User", "Purchase Manager", "MSCAST Director"],
     [("Buying", [(D, "Material Request"), (D, "Request for Quotation"), (D, "Supplier Quotation"), (D, "Purchase Order"), (D, "Supplier")]),
      ("Bills & certification", [(D, "MSCAST BRM"), (D, "Purchase Invoice"), (R, "MSCAST BRM Register"), (R, "MSCAST MSME 45-Day Dues (MSMED s.15, s.43B(h))")]),
      ("Control", [(R, "MSCAST PO vs PCC Variance"), (R, "MSCAST Free Issue at Vendor")])]),

    ("MSCAST Stores", "Stores & dispatch", "stock", "blue", 4.0,
     ["Stock User", "Stock Manager", "Purchase User", "MSCAST Director"],
     [("Stock", [(D, "Stock Entry"), (D, "Purchase Receipt"), (D, "Item"), (D, "Warehouse")]),
      ("Dispatch", [(D, "MSCAST MDM"), (D, "MSCAST Delivery Instruction"), (D, "Delivery Note"), (D, "MSCAST Customer Asset")]),
      ("Reports", [(R, "Stock Balance"), (R, "MSCAST Dispatch Schedule"), (R, "MSCAST Free Issue at Vendor")])]),

    ("MSCAST Quality", "Quality", "quality", "blue", 5.0,
     ["Quality Manager", "Projects User", "Purchase User", "MSCAST Director"],
     [("Inspection", [(D, "MSCAST Inspection Plan"), (D, "Quality Inspection"), (D, "Quality Inspection Template")]),
      ("Reports", [(R, "MSCAST Inspection Status")])]),

    ("MSCAST Accounts", "Accounts & compliance", "accounting", "blue", 6.0,
     ["Accounts User", "Accounts Manager", "MSCAST Director", "MSCAST Statutory Auditor"],
     [("Day to day", [(D, "Payment Entry"), (D, "Journal Entry"), (D, "Sales Invoice"), (D, "Purchase Invoice"), (D, "Bank Guarantee")]),
      ("Statutory", [(R, "MSCAST Balance Sheet (Schedule III)"), (R, "MSCAST Statement of Profit and Loss (Schedule III)"), (R, "MSCAST Schedule III - Ratios"), (R, "MSCAST Notes to Accounts")]),
      ("Ageing & GST", [(R, "MSCAST Schedule III - Trade Receivable Ageing"), (R, "MSCAST Schedule III - Trade Payable Ageing (MSME and others)"), (R, "MSCAST GST on Closing Inventory (ITC and ITC-04)"), (R, "MSCAST Retention and Certificates")])]),

    ("MSCAST People", "People", "users", "blue", 7.0,
     ["HR User", "HR Manager", "MSCAST Director"],
     [("Every day", [(D, "Attendance"), (D, "Leave Application"), (D, "Expense Claim"), (D, "Employee")]),
      ("Payroll", [(D, "Salary Structure"), (D, "Payroll Entry"), (D, "Salary Slip")]),
      ("Reports", [(R, "MSCAST Biometric Attendance Audit")])]),

    ("MSCAST Director", "Director's desk", "dashboard", "blue", 8.0,
     ["MSCAST Director", "MSCAST Statutory Auditor"],
     [("Every morning", [(R, "MSCAST Daily Management Summary"), (R, "MSCAST SO - PO - Invoice Tracker"), (R, "MSCAST Project MIS")]),
      ("Money", [(R, "MSCAST Schedule III - Trade Receivable Ageing"), (R, "MSCAST Schedule III - Trade Payable Ageing (MSME and others)"), (R, "MSCAST Retention and Certificates"), (R, "MSCAST Finance Scaling - Funding and Capacity")]),
      ("Year end", [(R, "MSCAST Balance Sheet (Schedule III)"), (R, "MSCAST Statement of Profit and Loss (Schedule III)"), (R, "MSCAST Schedule III - Ratios"), (R, "MSCAST Expense Analysis (vs last year, share of sales)"), (R, "MSCAST Project Closure Report")])]),

    ("MSCAST Setup", "Setup", "setting", "gray", 9.0,
     ["System Manager"],
     [("People & access", [(D, "User"), (D, "Role"), (D, "Workflow"), (D, "Custom HTML Block")]),
      ("Company", [(D, "Company"), (D, "Fiscal Year"), (D, "Print Format"), (D, "Notification")]),
      ("Records", [(D, "MSCAST Archival Log"), (D, "Server Script"), (D, "Scheduled Job Type")])]),
]

KEEP = ["MSCAST"] + [s[0] for s in SPACES]

existing_roles = set(r.name for r in frappe.get_all("Role", fields=["name"]))


def link_rows(cards):
    rows = []
    for title, items in cards:
        rows.append({"type": "Card Break", "label": title, "hidden": 0, "onboard": 0})
        for lt, target in items:
            if lt == D and not frappe.db.exists("DocType", target):
                print("   skip missing doctype", target); continue
            if lt == R and not frappe.db.exists("Report", target):
                print("   skip missing report", target); continue
            rows.append({"type": "Link", "label": target.replace("MSCAST ", ""), "link_type": lt,
                         "link_to": target, "hidden": 0, "onboard": 0, "is_query_report": 1 if lt == R else 0})
    return rows


# ---------- 1. the landing page workspace -------------------------------
home = frappe.get_doc("Workspace", "MSCAST")
home.title = "Home"
home.label = "MSCAST"
home.icon = "home"
home.sequence_id = 0.1
home.public = 1
home.is_hidden = 0
home.module = "Custom"
home.set("custom_blocks", [{"custom_block_name": "MSCAST Home", "label": "MSCAST Home"}])
home.set("number_cards", [])
home.set("charts", [])
home.set("shortcuts", [])
home.content = json.dumps([
    {"id": "mscasthomeblk", "type": "custom_block", "data": {"custom_block_name": "MSCAST Home", "col": 12}}
])
home.save(ignore_permissions=True)
print("landing workspace saved:", home.name, "title:", home.title)

# ---------- 2. the role-scoped spaces -----------------------------------
for wsname, title, icon, colour, seq, roles, cards in SPACES:
    if frappe.db.exists("Workspace", wsname):
        w = frappe.get_doc("Workspace", wsname)
    else:
        w = frappe.new_doc("Workspace")
        w.name = wsname
    w.label = wsname
    w.title = title
    w.icon = icon
    w.indicator_color = colour
    w.sequence_id = seq
    w.public = 1
    w.is_hidden = 0
    w.module = "Custom"
    w.type = "Workspace"
    rows = link_rows(cards)
    w.set("links", rows)
    use_roles = [r for r in roles if r in existing_roles]
    w.set("roles", [{"role": r} for r in use_roles])
    content = []
    for title_card, _items in cards:
        content.append({"id": "c" + title_card.replace(" ", "")[:10], "type": "card", "data": {"card_name": title_card, "col": 4}})
    w.content = json.dumps(content)
    w.save(ignore_permissions=True)
    print("space:", wsname, "->", title, "| links", len(rows), "| roles", use_roles or "everyone")

# ---------- 3. hide the stock spaces ------------------------------------
hidden = []
for w in frappe.get_all("Workspace", filters={"public": 1}, fields=["name", "is_hidden"]):
    if w.name in KEEP:
        continue
    frappe.db.set_value("Workspace", w.name, "is_hidden", 1, update_modified=False)
    hidden.append(w.name)
print("hidden", len(hidden), "stock spaces:", ", ".join(sorted(hidden)))

frappe.db.commit()
frappe.clear_cache()
print("DONE")
