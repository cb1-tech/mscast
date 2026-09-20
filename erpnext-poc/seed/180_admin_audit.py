# -*- coding: utf-8 -*-
"""What does admin@mscast.local actually do here, before anything is taken away?"""
import frappe

U = "admin@mscast.local"
row = frappe.db.get_value("User", U, ["full_name", "enabled", "last_login",
                                      "last_active", "user_type"], as_dict=True)
print("user   :", row)
print("roles  :", len(frappe.db.sql("select 1 from `tabHas Role` where parent=%s", (U,))))
for r in sorted(x[0] for x in frappe.db.sql(
        "select role from `tabHas Role` where parent=%s", (U,))):
    print("          ", r)

print()
print("documents it owns / created, by doctype (top 15):")
rows = frappe.db.sql("""select 'owner' src, t.n, t.dt from (
    select count(*) n, 'see below' dt from `tabDocType` limit 0) t""", as_dict=True)
found = []
for dt in frappe.get_all("DocType", filters={"istable": 0, "issingle": 0}, pluck="name"):
    try:
        n = frappe.db.count(dt, {"owner": U})
    except Exception:
        continue
    if n:
        found.append((n, dt))
for n, dt in sorted(found, reverse=True)[:15]:
    print("   %-34s %d" % (dt, n))
if not found:
    print("   none - it has never created anything")

print()
print("is it a recipient of any notification?")
hits = frappe.db.sql("""select parent from `tabNotification Recipient`
                        where receiver_by_document_field is null
                          and ifnull(receiver_by_role,'') = ''""", as_dict=True)
print("   notifications with a literal recipient:", len(hits))

print()
print("other System Manager holders (so we are not removing the last one):")
for x in frappe.db.sql("""select h.parent, u.enabled from `tabHas Role` h
                          join `tabUser` u on u.name = h.parent
                          where h.role='System Manager'""", as_dict=True):
    print("   %-32s enabled=%s" % (x.parent, x.enabled))
