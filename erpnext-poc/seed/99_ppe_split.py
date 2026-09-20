"""MSCAST POC - 99: this chart of accounts has no plant-and-machinery head, so the opening entry
put the workstation and welding equipment into Software. Create the head and reallocate."""
import frappe

COMPANY = "MSCAST Engineering Pvt Ltd"
log = lambda m: print("[99] " + m, flush=True)


def acc(**f):
    f.setdefault("company", COMPANY)
    f.setdefault("is_group", 0)
    return frappe.db.get_value("Account", f, "name")


def cc():
    return frappe.db.get_value("Cost Center", {"company": COMPANY, "is_group": 0}, "name")


sw = acc(account_name=("like", "%Software%"))
pm = acc(account_name="Plant and Machinery")
if not pm:
    parent = frappe.db.get_value("Account", {"company": COMPANY, "is_group": 1,
                                             "account_name": ("like", "%Fixed Asset%")}, "name")
    log("fixed asset parent group: %s" % parent)
    d = frappe.get_doc({"doctype": "Account", "account_name": "Plant and Machinery",
                        "parent_account": parent, "company": COMPANY, "root_type": "Asset",
                        "account_type": "Fixed Asset"})
    d.flags.ignore_permissions = True
    d.insert()
    pm = d.name
    frappe.db.commit()
    log("created %s" % pm)

if frappe.db.exists("Journal Entry", {"user_remark": ("like", "Reclassification of plant%")}):
    log("already reclassified")
else:
    amt = 605000.0          # CAD workstation 185,000 + welding and testing equipment 420,000
    j = frappe.get_doc({"doctype": "Journal Entry", "voucher_type": "Journal Entry",
                        "company": COMPANY, "posting_date": "2026-04-01",
                        "user_remark": "Reclassification of plant and machinery out of the "
                                       "software head - this chart of accounts had no plant and "
                                       "machinery account when the opening entry was posted. "
                                       "CAD workstation Rs 1,85,000 and welding / testing "
                                       "equipment Rs 4,20,000.",
                        "accounts": [{"account": pm, "debit_in_account_currency": amt,
                                      "cost_center": cc()},
                                     {"account": sw, "credit_in_account_currency": amt,
                                      "cost_center": cc()}]})
    j.flags.ignore_permissions = True
    j.insert()
    j.submit()
    frappe.db.commit()
    log("posted %s" % j.name)

for r in frappe.db.sql("""select a.name, round(sum(gl.debit - gl.credit),0) net
    from `tabGL Entry` gl inner join `tabAccount` a on a.name = gl.account
    where gl.is_cancelled = 0 and (a.account_type in ('Fixed Asset','Capital Work in Progress')
       or a.account_name like '%%Software%%')
    group by a.name having abs(net) > 0.5""", as_dict=True):
    log("  %-46s %s" % (r.name[:46], r.net))

# also fix the asset-category mapping so future assets post to the right head
for cat, account in [("Plant & Machinery (Demo)", pm), ("Plant under construction (CWIP)", pm)]:
    if frappe.db.exists("Asset Category", cat):
        row = frappe.db.get_value("Asset Category Account", {"parent": cat}, "name")
        if row:
            frappe.db.set_value("Asset Category Account", row, "fixed_asset_account", account)
            log("asset category '%s' now posts to %s" % (cat, account))
frappe.db.commit()
log("DONE")
