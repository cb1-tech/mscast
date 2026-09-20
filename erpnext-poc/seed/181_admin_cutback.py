# -*- coding: utf-8 -*-
"""Cut the setup-wizard admin down to an administrator, and nothing more.

admin@mscast.local was created by the ERPNext setup wizard and collected 41
roles - every manager role in the system plus a good deal it has no use for.
It has never logged in and has never created a document.

Forty-one roles on an account nobody uses is not untidy, it is a hole. Every
separation described in the SOPs and the role cards has an exception nobody
wrote down, and anyone who gets that password gets all of it.

It keeps System Manager, because a site needs a named administrator that is not
the built-in Administrator account. It keeps nothing else. A System Manager can
still grant itself a role, and that is fine - the point is that doing so leaves
a record, where quietly holding Purchase Manager forever does not.
"""
import frappe

U = "admin@mscast.local"
KEEP = {"System Manager"}

doc = frappe.get_doc("User", U)
before = sorted({r.role for r in doc.get("roles")})
print("before: %d roles" % len(before))

removed = [r for r in before if r not in KEEP]
doc.set("roles", [{"role": r} for r in sorted(KEEP)])
doc.flags.ignore_permissions = True
doc.save()
frappe.db.commit()

after = sorted({r.role for r in frappe.get_doc("User", U).get("roles")})
print("after : %d roles -> %s" % (len(after), ", ".join(after)))
print()
print("removed %d:" % len(removed))
for r in removed:
    print("   ", r)

print()
print("still able to administer the site:")
for x in frappe.db.sql("""select h.parent from `tabHas Role` h
                          join `tabUser` u on u.name=h.parent
                          where h.role='System Manager' and u.enabled=1""", as_dict=True):
    print("   ", x.parent)
print("    Administrator  (built in, always present)")
