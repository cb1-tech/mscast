"""MSCAST POC - 105: two data defects found by reading the notes to accounts.

1. Share allocation was zipped against an unordered query, so the 70 percent holding landed on the
   wrong director. The knowledge base has Mustaque Ahmed N. Chandankeri as founder/CEO.
2. The bank guarantees carry no end date, so the 'BG expiry alert' notification could never fire -
   a control that looks configured but is dead.
"""
import frappe
from frappe.utils import add_days, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
log = lambda m: print("[105] " + m, flush=True)

WANT = {"Mustaque Ahmed N. Chandankeri": 7000,
        "Aiqaz M. Chandankeri": 2000,
        "Zameer Alam Chandankeri": 1000}

current = frappe.db.sql("""select t.name, s.title, t.no_of_shares, t.from_no, t.to_no
    from `tabShare Transfer` t inner join `tabShareholder` s on s.name = t.to_shareholder
    where t.docstatus = 1""", as_dict=True)
for c in current:
    log("  before: %s -> %s %s shares (%s-%s)" % (c.name, c.title, c.no_of_shares, c.from_no, c.to_no))

if any(c.title == "Mustaque Ahmed N. Chandankeri" and c.no_of_shares == 7000 for c in current):
    log("allocation already correct")
else:
    for c in current:
        d = frappe.get_doc("Share Transfer", c.name)
        d.flags.ignore_permissions = True
        d.cancel()
        frappe.db.commit()
        frappe.delete_doc("Share Transfer", c.name, force=1, ignore_permissions=True)
    frappe.db.commit()
    log("cleared %d share transfers" % len(current))

    eq = frappe.db.get_value("Account", {"company": COMPANY, "root_type": "Equity",
                                         "is_group": 0, "account_name": ("like", "%Share Capital%")},
                             "name") or frappe.db.get_value(
        "Account", {"company": COMPANY, "root_type": "Equity", "is_group": 0}, "name")
    bank = frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Bank",
                                           "is_group": 0}, "name")
    start = 1
    for title, qty in WANT.items():
        holder = frappe.db.get_value("Shareholder", {"title": title}, "name")
        if not holder:
            log("  shareholder missing: %s" % title)
            continue
        d = frappe.get_doc({"doctype": "Share Transfer", "transfer_type": "Issue",
                            "date": "2026-04-01", "to_shareholder": holder, "share_type": "Equity",
                            "from_no": start, "to_no": start + qty - 1, "no_of_shares": qty,
                            "rate": 10, "amount": qty * 10, "company": COMPANY,
                            "equity_or_liability_account": eq, "asset_account": bank})
        d.flags.ignore_permissions = True
        d.flags.ignore_mandatory = True
        d.insert()
        d.submit()
        start += qty
    frappe.db.commit()
    log("reissued: Mustaque 7000 (70%), Aiqaz 2000 (20%), Zameer 1000 (10%)")

# ---- bank guarantee validity
if frappe.db.exists("DocType", "Bank Guarantee"):
    for b in frappe.get_all("Bank Guarantee", fields=["name", "bank_guarantee_number", "start_date",
                                                      "end_date", "amount", "bg_type"]):
        if b.end_date:
            log("  BG %s already valid to %s" % (b.name, b.end_date))
            continue
        start = b.start_date or add_days(TODAY, -80)
        # advance BG runs to the contract delivery, performance BG one year past commissioning
        end = add_days(TODAY, 40) if "ABG" in (b.bank_guarantee_number or "") else add_days(TODAY, 400)
        frappe.db.set_value("Bank Guarantee", b.name,
                            {"start_date": start, "end_date": end,
                             "validity": (frappe.utils.date_diff(end, start))})
        log("  BG %s (%s) now valid %s to %s" % (b.name, b.bank_guarantee_number, start, end))
    frappe.db.commit()

n = frappe.db.get_value("Notification", {"name": ("like", "%BG expiry%")},
                        ["name", "document_type", "event", "date_changed", "days_in_advance",
                         "enabled"], as_dict=True)
log("BG expiry notification: %s" % n)
if n and n.date_changed:
    due = frappe.db.sql("""select count(*) from `tabBank Guarantee`
        where %s is not null and datediff(%s, date(convert_tz(utc_timestamp(),'+00:00','+05:30')))
              between 0 and %s""" % ("`" + n.date_changed + "`", "`" + n.date_changed + "`",
                                     n.days_in_advance or 30))[0][0]
    log("guarantees that would trigger the alert in the next %s days: %s"
        % (n.days_in_advance or 30, due))
log("DONE")
