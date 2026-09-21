# Every configuration record, and every effective permission row, on this site.
import frappe, json
F = ("read","write","create","delete","submit","cancel","amend","report","export","import","share","print","email","select")
out = {dt: sorted(frappe.get_all(dt, pluck="name")) for dt in
       ("Custom Field", "Property Setter", "Workflow", "Workflow State", "Workflow Action Master",
        "Report", "Print Format", "Role", "Email Template", "Notification", "Server Script")}
perms = set()
for dt in sorted(set(frappe.get_all("Custom DocPerm", pluck="parent")) | set(frappe.get_all("DocPerm", pluck="parent"))):
    if not frappe.db.exists("DocType", dt): continue
    for r in frappe.get_meta(dt).permissions:
        perms.add("%s | %s | %s" % (dt, r.role, ",".join(f for f in F if r.get(f))))
out["effective permission rows"] = sorted(perms)
json.dump(out, open("/tmp/conf-%s.json" % frappe.local.site, "w"))
print("dumped", {k: len(v) for k, v in out.items()})
