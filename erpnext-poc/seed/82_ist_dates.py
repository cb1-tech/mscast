"""MSCAST POC - 82: make every custom SQL report use the Indian date, not the container's UTC date."""
import frappe
log = lambda m: print("[ist] " + m, flush=True)

IST = "date(convert_tz(utc_timestamp(),'+00:00','+05:30'))"

row = frappe.db.sql("""select @@global.time_zone, @@session.time_zone, now(), utc_timestamp(),
                              curdate(), """ + IST, as_dict=0)[0]
log("db global tz=%s session tz=%s" % (row[0], row[1]))
log("db now()=%s  utc_timestamp()=%s" % (row[2], row[3]))
log("db curdate()=%s   <-- what the reports were using" % row[4])
log("indian date =%s   <-- what they should use" % row[5])
log("site time zone = %s" % frappe.db.get_single_value("System Settings", "time_zone"))

patched = []
for name in frappe.get_all("Report", filters={"is_standard": "No"}, pluck="name"):
    q = frappe.db.get_value("Report", name, "query") or ""
    if "curdate()" not in q:
        continue
    newq = q.replace("curdate()", IST)
    d = frappe.get_doc("Report", name)
    d.query = newq
    d.flags.ignore_permissions = True
    d.save()
    patched.append((name, q.count("curdate()")))
frappe.db.commit()
for n, c in patched:
    log("patched %-52s (%d date references)" % (n, c))

log("--- smoke test every custom report ---")
for name in frappe.get_all("Report", filters={"is_standard": "No"}, pluck="name"):
    q = frappe.db.get_value("Report", name, "query")
    if not q:
        continue
    try:
        n = len(frappe.db.sql(q))
        log("  OK   %-52s %d rows" % (name, n))
    except Exception as e:
        log("  FAIL %-52s %s" % (name, repr(e)[:200]))
log("DONE")
