"""Every demonstration party carries '(DEMO)' in its name.

`Ambika Steel Rolling Mills` was the one customer without it (added by the
project-three expansion). There is no company of exactly that name, but several
real steel firms are one letter away - Ambica Steels Ltd, Ambica Steel
Industries, Ambika Forge - so on a demo tax invoice it reads as a real customer.
Same exposure as review finding A2. Renamed; ledger and documents follow.
"""
import frappe
log = lambda m: print("[188] " + m, flush=True)

frappe.flags.ignore_permissions = True
for dt in ("Customer", "Supplier"):
    for name in frappe.get_all(dt, pluck="name"):
        if "(DEMO)" in name:
            continue
        new = name + " (DEMO)"
        frappe.rename_doc(dt, name, new, force=True, merge=False)
        log("%s: %s -> %s" % (dt, name, new))
frappe.db.commit()
left = [n for dt in ("Customer", "Supplier") for n in frappe.get_all(dt, pluck="name")
        if "(DEMO)" not in n]
log("parties without (DEMO): %s" % (left or "none"))
