# -*- coding: utf-8 -*-
"""Two records MSCAST does not have and needs most:
   - why a bid was lost (the only honest input to competitor analysis)
   - every machine ever built (the revamp and spares pipeline)
"""
import frappe

def make(dt, fields, perms, autoname, title_field, desc=""):
    if frappe.db.exists("DocType", dt):
        d = frappe.get_doc("DocType", dt)
        d.set("fields", [])
        d.set("permissions", [])
    else:
        d = frappe.new_doc("DocType")
        d.name = dt
        d.custom = 1
    d.module = "Custom"
    d.custom = 1
    d.naming_rule = "By \"Naming Series\" field"
    d.autoname = autoname
    d.title_field = title_field
    d.track_changes = 1
    d.sort_field = "modified"
    d.sort_order = "DESC"
    d.description = desc
    for f in fields:
        d.append("fields", f)
    for p in perms:
        if frappe.db.exists("Role", p["role"]):
            d.append("permissions", p)
    d.save(ignore_permissions=True)
    return d

SALES_PERMS = [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1, "export": 1},
    {"role": "MSCAST Director", "read": 1, "write": 1, "create": 1, "report": 1, "export": 1},
    {"role": "Sales User", "read": 1, "write": 1, "create": 1, "report": 1},
    {"role": "Sales Manager", "read": 1, "write": 1, "create": 1, "report": 1},
    {"role": "Projects User", "read": 1, "report": 1},
]

# ------------------------------------------------------------ 1. bid outcome
BID = [
    {"fieldname": "naming_series", "label": "Series", "fieldtype": "Select", "options": "BID-.YYYY.-", "default": "BID-.YYYY.-", "reqd": 1},
    {"fieldname": "customer_name", "label": "Prospect", "fieldtype": "Data", "reqd": 1, "in_list_view": 1},
    {"fieldname": "customer", "label": "Customer (if on file)", "fieldtype": "Link", "options": "Customer"},
    {"fieldname": "opportunity", "label": "Opportunity", "fieldtype": "Link", "options": "Opportunity"},
    {"fieldname": "quotation", "label": "Our quotation", "fieldtype": "Link", "options": "Quotation"},
    {"fieldname": "cb1", "fieldtype": "Column Break"},
    {"fieldname": "machine_type", "label": "Machine", "fieldtype": "Select",
     "options": "Billet caster\nBloom caster\nSlab caster\nRound caster\nCombi caster\nRevamp / upgrade\nSpares only\nOther",
     "in_list_view": 1},
    {"fieldname": "strands", "label": "Strands", "fieldtype": "Int"},
    {"fieldname": "section_size", "label": "Section", "fieldtype": "Data", "description": "e.g. 130 sq"},
    {"fieldname": "site_location", "label": "Site", "fieldtype": "Data"},
    {"fieldname": "sec_out", "fieldtype": "Section Break", "label": "Outcome"},
    {"fieldname": "outcome", "label": "Outcome", "fieldtype": "Select",
     "options": "In progress\nWon\nLost\nNo bid\nAbandoned by customer", "default": "In progress",
     "reqd": 1, "in_list_view": 1, "in_standard_filter": 1},
    {"fieldname": "bid_date", "label": "Quoted on", "fieldtype": "Date", "in_list_view": 1},
    {"fieldname": "decision_date", "label": "Decision known on", "fieldtype": "Date"},
    {"fieldname": "cb2", "fieldtype": "Column Break"},
    {"fieldname": "our_price", "label": "Our price", "fieldtype": "Currency", "in_list_view": 1},
    {"fieldname": "our_lead_weeks", "label": "Our lead time (weeks)", "fieldtype": "Int"},
    {"fieldname": "sec_win", "fieldtype": "Section Break", "label": "Who won it", "depends_on": "eval:doc.outcome=='Lost'"},
    {"fieldname": "winner", "label": "Won by", "fieldtype": "Data",
     "description": "The competitor. Exactly as MSCAST knows them - consistency matters more than spelling."},
    {"fieldname": "winner_price", "label": "Their price (if known)", "fieldtype": "Currency"},
    {"fieldname": "winner_lead_weeks", "label": "Their lead time (weeks)", "fieldtype": "Int"},
    {"fieldname": "cb3", "fieldtype": "Column Break"},
    {"fieldname": "reason_lost", "label": "Main reason", "fieldtype": "Select",
     "options": "\nPrice\nLead time\nTechnical scope\nReferences / track record\nPayment terms\nRelationship / incumbency\nCapacity - we could not take it\nCustomer dropped the project\nOther",
     "in_standard_filter": 1},
    {"fieldname": "price_gap", "label": "Price gap", "fieldtype": "Percent", "read_only": 1,
     "description": "How far above the winner we were. Filled when both prices are known."},
    {"fieldname": "sec_learn", "fieldtype": "Section Break", "label": "What was actually said"},
    {"fieldname": "customer_feedback", "label": "Customer's words", "fieldtype": "Small Text",
     "description": "What the customer actually said, not our interpretation of it."},
    {"fieldname": "learning", "label": "What we would do differently", "fieldtype": "Small Text"},
]

make("MSCAST Bid Outcome", BID, SALES_PERMS, "naming_series:", "customer_name",
     "One record per bid, won or lost. The only honest input to any competitor analysis.")
print("doctype: MSCAST Bid Outcome")

# ------------------------------------------------------- 2. installed machine
MACHINE = [
    {"fieldname": "naming_series", "label": "Series", "fieldtype": "Select", "options": "MACH-.YYYY.-", "default": "MACH-.YYYY.-", "reqd": 1},
    {"fieldname": "machine_sn", "label": "Machine serial", "fieldtype": "Data", "reqd": 1, "in_list_view": 1, "unique": 1},
    {"fieldname": "customer", "label": "Customer", "fieldtype": "Link", "options": "Customer", "in_list_view": 1},
    {"fieldname": "customer_name_text", "label": "Customer (free text)", "fieldtype": "Data",
     "description": "For machines built before this system, where no customer record exists."},
    {"fieldname": "site_location", "label": "Site", "fieldtype": "Data", "in_list_view": 1},
    {"fieldname": "cb1", "fieldtype": "Column Break"},
    {"fieldname": "machine_type", "label": "Machine", "fieldtype": "Select",
     "options": "Billet caster\nBloom caster\nSlab caster\nRound caster\nCombi caster\nOther", "in_list_view": 1},
    {"fieldname": "strands", "label": "Strands", "fieldtype": "Int"},
    {"fieldname": "section_size", "label": "Section", "fieldtype": "Data"},
    {"fieldname": "capacity_tpa", "label": "Capacity (tpa)", "fieldtype": "Int"},
    {"fieldname": "sec_life", "fieldtype": "Section Break", "label": "Life"},
    {"fieldname": "commissioned_on", "label": "Commissioned", "fieldtype": "Date", "in_list_view": 1},
    {"fieldname": "warranty_end", "label": "Warranty ends", "fieldtype": "Date"},
    {"fieldname": "status", "label": "Status", "fieldtype": "Select",
     "options": "Running\nIdle\nRevamped by us\nRevamped by others\nDecommissioned\nUnknown",
     "default": "Running", "in_list_view": 1, "in_standard_filter": 1},
    {"fieldname": "cb2", "fieldtype": "Column Break"},
    {"fieldname": "project", "label": "Project", "fieldtype": "Link", "options": "Project"},
    {"fieldname": "sales_order", "label": "Sales order", "fieldtype": "Link", "options": "Sales Order"},
    {"fieldname": "contract_value", "label": "Original contract value", "fieldtype": "Currency"},
    {"fieldname": "sec_follow", "fieldtype": "Section Break", "label": "Follow-up"},
    {"fieldname": "last_contact", "label": "Last spoken to", "fieldtype": "Date"},
    {"fieldname": "spares_since", "label": "Spares billed since commissioning", "fieldtype": "Currency"},
    {"fieldname": "cb3", "fieldtype": "Column Break"},
    {"fieldname": "revamp_due", "label": "Revamp conversation due", "fieldtype": "Date",
     "description": "A caster past ten years is a revamp lead. Set a date and the radar will raise it."},
    {"fieldname": "notes", "label": "Notes", "fieldtype": "Small Text"},
]

make("MSCAST Installed Machine", MACHINE, SALES_PERMS, "naming_series:", "machine_sn",
     "Every machine MSCAST has built. The revamp and spares pipeline.")
print("doctype: MSCAST Installed Machine")

frappe.db.commit()

# --------------------------------------------------------------- reports
def report(name, ref, sql, letter="No"):
    if frappe.db.exists("Report", name):
        r = frappe.get_doc("Report", name)
    else:
        r = frappe.new_doc("Report")
        r.name = name
    r.report_name = name
    r.ref_doctype = ref
    r.report_type = "Query Report"
    r.is_standard = "No"
    r.module = "Custom"
    r.disabled = 0
    r.query = sql
    r.save(ignore_permissions=True)
    print("report:", name)

report("MSCAST Bid Win-Loss Analysis", "MSCAST Bid Outcome", """
select
    b.outcome                            as "Outcome:Data:90",
    b.customer_name                      as "Prospect:Data:190",
    b.machine_type                       as "Machine:Data:130",
    b.bid_date                           as "Quoted:Date:90",
    b.our_price                          as "Our price:Currency:120",
    ifnull(b.winner, '')                 as "Won by:Data:170",
    b.winner_price                       as "Their price:Currency:120",
    case when b.our_price > 0 and b.winner_price > 0
         then round((b.our_price - b.winner_price) * 100 / b.winner_price, 1) else null end
                                         as "Gap %:Float:70",
    ifnull(b.reason_lost, '')            as "Reason:Data:150",
    ifnull(b.customer_feedback, '')      as "What the customer said:Data:320"
from `tabMSCAST Bid Outcome` b
order by b.bid_date desc
""")

report("MSCAST Installed Base and Revamp Radar", "MSCAST Installed Machine", """
select
    m.machine_sn                         as "Machine:Link/MSCAST Installed Machine:130",
    ifnull(m.customer, m.customer_name_text) as "Customer:Data:190",
    m.site_location                      as "Site:Data:160",
    m.machine_type                       as "Type:Data:120",
    m.strands                            as "Strands:Int:70",
    m.commissioned_on                    as "Commissioned:Date:110",
    case when m.commissioned_on is null then null
         else round(datediff(date(convert_tz(utc_timestamp(),'+00:00','+05:30')), m.commissioned_on) / 365.25, 1)
    end                                  as "Age (yrs):Float:80",
    m.status                             as "Status:Data:110",
    m.spares_since                       as "Spares billed:Currency:120",
    m.last_contact                       as "Last spoken:Date:100",
    case
      when m.status in ('Decommissioned', 'Revamped by others') then 'Closed'
      when m.commissioned_on is not null
           and datediff(date(convert_tz(utc_timestamp(),'+00:00','+05:30')), m.commissioned_on) > 3650
        then 'REVAMP LEAD - past 10 years'
      when m.last_contact is null then 'Never followed up'
      when datediff(date(convert_tz(utc_timestamp(),'+00:00','+05:30')), m.last_contact) > 365
        then 'No contact for over a year'
      else 'OK'
    end                                  as "Opportunity:Data:210"
from `tabMSCAST Installed Machine` m
order by m.commissioned_on asc
""")

frappe.db.commit()
frappe.clear_cache()
print("\ndone")
