# On a site WITHOUT mscast_erp: every configuration record the other apps create
# themselves. Anything in our fixtures that is also here belongs to them.
import frappe, json
out = {}
for dt, fields in (("Custom Field", ["name", "dt", "fieldname", "module", "label", "fieldtype", "options", "insert_after", "reqd", "hidden", "read_only", "default", "description"]),
                   ("Property Setter", ["name", "doc_type", "field_name", "property", "value"]),
                   ("Email Template", ["name", "subject", "response"]),
                   ("Workflow State", ["name"]), ("Workflow Action Master", ["name"]),
                   ("Report", ["name", "is_standard", "module"]),
                   ("Notification", ["name", "is_standard"]),
                   ("Client Script", ["name"]), ("Server Script", ["name"])):
    out[dt] = {r["name"]: r for r in frappe.get_all(dt, fields=fields)}
    print("%-24s %d" % (dt, len(out[dt])))
json.dump(out, open("/tmp/baseline.json", "w"), default=str, indent=0)
print("written")
