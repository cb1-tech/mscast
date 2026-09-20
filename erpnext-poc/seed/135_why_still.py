import frappe
print("PCC-2026-00002:", frappe.db.get_value("MSCAST PCC","PCC-2026-00002",["status","workflow_state"], as_dict=True))
print("PROJ-0002 percent:", frappe.db.get_value("Project","PROJ-0002","percent_complete"))
print("KICK-2026-00002:", frappe.db.get_value("MSCAST Project Kickoff","KICK-2026-00002",["workflow_state"], as_dict=True))
print("Dunning rows:", frappe.db.sql("select name, status, docstatus from `tabDunning`", as_dict=True))
print()
print("X07 rule result:", frappe.db.sql("""
    select p.name, p.percent_complete, pc.name pcc, pc.status
    from `tabProject` p join `tabMSCAST PCC` pc on pc.project = p.name
    where p.status = 'Open' and pc.status <> 'Approved' and ifnull(p.percent_complete, 0) > 10""", as_dict=True))
print("X08 rule result:", frappe.db.sql("""
    select k.name, k.project, k.workflow_state, p.percent_complete
    from `tabMSCAST Project Kickoff` k join `tabProject` p on p.name = k.project
    where ifnull(k.workflow_state, '') <> 'Kick-off Approved' and ifnull(p.percent_complete, 0) > 0""", as_dict=True))
print()
print("open exceptions:", frappe.db.sql("select rule_code, ref_name, status, last_seen from `tabMSCAST Exception` order by rule_code", as_dict=True))
