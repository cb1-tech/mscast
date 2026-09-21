"""Two report names could not be opened from the desk.

'MSCAST MSME 45-Day Dues (s.15 MSMED / s.43B(h))' - the '/' is a path separator
in the desk's URL, so the name arrived truncated and the page failed with a 500.
'MSCAST Expense Analysis (vs last year, % of sales)' - the '%' breaks URL
decoding; through the public URL the connection was reset. The MD's home page
links to the first one. Both worked when run as Administrator from Python, which
is how the build checks ran them - found 21 Sep 2026 by the demo screenshot run,
logged in as the accounts manager. Renamed; links follow. Idempotent.
"""
import frappe
RENAME = {
    "MSCAST MSME 45-Day Dues (s.15 MSMED / s.43B(h))": "MSCAST MSME 45-Day Dues (MSMED s.15, s.43B(h))",
    "MSCAST Expense Analysis (vs last year, % of sales)": "MSCAST Expense Analysis (vs last year, share of sales)",
    # found by T2b once it existed - the same '/' problem
    "MSCAST Schedule III - Trade Payable Ageing (MSME / others)": "MSCAST Schedule III - Trade Payable Ageing (MSME and others)",
}
frappe.flags.ignore_permissions = True
for old, new in RENAME.items():
    if frappe.db.exists("Report", old) and not frappe.db.exists("Report", new):
        frappe.rename_doc("Report", old, new, force=True, merge=False)
        frappe.db.set_value("Report", new, "report_name", new, update_modified=False)
        print("[191] renamed:", new)
    else:
        print("[191] already:", new if frappe.db.exists("Report", new) else "MISSING " + old)
    # text that embeds the name: the home page block, workspace links and shortcuts
    for dt, fields in (("Custom HTML Block", ("html", "script", "style")),
                       ("Workspace", ("content",)), ("Workspace Link", ("link_to", "label")),
                       ("Workspace Shortcut", ("link_to", "label")), ("Auto Email Report", ("report",))):
        if not frappe.db.exists("DocType", dt):
            continue
        for f in fields:
            if not frappe.get_meta(dt).has_field(f) and f not in ("html", "script", "style"):
                continue
            try:
                n = frappe.db.sql("update `tab%s` set `%s` = replace(`%s`, %%s, %%s) where `%s` like %%s"
                                  % (dt, f, f, f), (old, new, "%" + old.replace("%", "\\%") + "%"))
            except Exception as e:
                continue
            hits = frappe.db.sql("select count(*) from `tab%s` where `%s` like %%s" % (dt, f), ("%" + new.replace("%", "\\%") + "%"))[0][0]
            if hits: print("[191]   %s.%s now references the new name in %d row(s)" % (dt, f, hits))
# sidebar labels carry a short form of the same name
for o, n in (("MSME 45-Day Dues (s.15 MSMED / s.43B(h))", "MSME 45-Day Dues (MSMED s.15, s.43B(h))"),
             ("Expense Analysis (vs last year, % of sales)", "Expense Analysis (vs last year, share of sales)"),
             ("Trade Payable Ageing (MSME / others)", "Trade Payable Ageing (MSME and others)")):
    for dt in ("Workspace Link", "Workspace Shortcut"):
        frappe.db.sql("update `tab%s` set label = %%s where label = %%s" % dt, (n, o))
    frappe.db.sql("update `tabWorkspace` set content = replace(content, %s, %s)", (o, n))
frappe.db.commit()
frappe.clear_cache()
left = frappe.get_all("Report", filters={"is_standard": "No"}, pluck="name")
print("[191] report names still unsafe in a URL:", [n for n in left if any(c in n for c in "/%?#")] or "none")
