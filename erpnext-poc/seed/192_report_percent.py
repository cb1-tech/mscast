"""Six reports could not be opened from the desk.

The desk runs a query report as frappe.db.sql(query, filters) - always with a
filters dict - so the driver %-formats the SQL. A literal % (LIKE '%x', or a
'%' label) then fails: "unsupported format character" or "not enough arguments
for format string". The build check ran each query WITHOUT values, which skips
formatting, so it passed. Found 21 Sep 2026 opening Schedule III - Ratios as the
statutory auditor for the demo screenshots.

Every lone % becomes %%. Applied only if the escaped query, run the desk's way,
returns exactly the rows the original returns run the old way. Idempotent.
"""
import frappe, re
LONE = re.compile(r"(?<!%)%(?!%|\(\w+\)s)")
fixed = 0
for r in frappe.get_all("Report", filters={"is_standard": "No"}, fields=["name", "query"]):
    q = r.query or ""
    try:
        frappe.db.sql(q, {}); continue
    except Exception:
        pass
    new = LONE.sub("%%", q)
    before = frappe.db.sql(q); after = frappe.db.sql(new, {})
    if [tuple(x) for x in before] != [tuple(x) for x in after]:
        print("[192] NOT CHANGED, results differ:", r.name); continue
    frappe.db.set_value("Report", r.name, "query", new, update_modified=False)
    fixed += 1
    print("[192] escaped:", r.name)
frappe.db.commit()
still = []
for r in frappe.get_all("Report", filters={"is_standard": "No"}, fields=["name", "query"]):
    try: frappe.db.sql(r.query or "", {})
    except Exception as e: still.append(r.name)
print("[192] %d fixed; reports still failing the desk's way: %s" % (fixed, still or "none"))
