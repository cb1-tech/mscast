"""MSCAST POC - 44: BATCH B - quick custom builds.

P-02 RFQ · PC-17 proforma invoice · PR-07 client claims register ·
AC-14 intangible assets · AC-15 CWIP · AC-13 customer-owned asset register · AC-08 share capital.
"""
import frappe
from frappe.utils import add_days, add_months, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
ABBR = "MSCAST"
TODAY = nowdate()
log = lambda m: print("[B] " + m, flush=True)

CSS = """
.print-format { font-family: Arial, Helvetica, sans-serif; font-size: 10.5px; color:#222; }
.ms-title { font-size:15px; font-weight:700; text-align:center; letter-spacing:1px;
            border:1px solid #1f3864; background:#eef2f9; color:#1f3864; padding:5px; margin-bottom:10px; }
table.ms { width:100%; border-collapse:collapse; margin-bottom:10px; }
table.ms th { background:#1f3864; color:#fff; font-size:10px; padding:4px 5px; border:1px solid #1f3864; text-align:left; }
table.ms td { border:1px solid #c6cbd4; padding:3px 5px; vertical-align:top; }
table.meta { width:100%; border-collapse:collapse; margin-bottom:10px; }
table.meta td { border:1px solid #c6cbd4; padding:3px 6px; font-size:10px; }
table.meta td.k { background:#f2f4f8; font-weight:600; width:18%; }
.num { text-align:right; }
.ms-note { font-size:9.5px; color:#444; margin-top:6px; }
.sign { margin-top:26px; width:100%; }
.sign td { border:none; font-size:10px; padding-top:22px; border-top:1px solid #888; width:33%; text-align:center; }
.badge { display:inline-block; padding:1px 7px; border-radius:9px; font-size:9px; border:1px solid #1f3864; color:#1f3864; }
"""


def step(name, fn, *a, **kw):
    try:
        out = fn(*a, **kw)
        frappe.db.commit()
        log("OK   " + name + ((" -> " + str(out)) if out else ""))
        return out or True
    except Exception as e:
        frappe.db.rollback()
        log("FAIL " + name + " :: " + repr(e)[:320])
        return None


def ins(doc, submit=False):
    d = frappe.get_doc(doc)
    d.flags.ignore_permissions = True
    d.flags.ignore_mandatory = True
    d.insert(ignore_if_duplicate=True)
    if submit:
        d.submit()
    return d


def f(fieldname, label, fieldtype, **kw):
    d = {"fieldname": fieldname, "label": label, "fieldtype": fieldtype}
    d.update(kw)
    return d


PERMS = [
    {"role": "System Manager", "read": 1, "write": 1, "create": 1, "delete": 1, "report": 1,
     "export": 1, "share": 1, "print": 1, "email": 1},
    {"role": "Projects Manager", "read": 1, "write": 1, "create": 1, "report": 1, "print": 1},
    {"role": "Accounts User", "read": 1, "report": 1, "print": 1},
]


def doctype(name, fields, istable=0, title_field=None, search_fields=None):
    if frappe.db.exists("DocType", name):
        return False
    d = frappe.get_doc({"doctype": "DocType", "name": name, "module": "Custom", "custom": 1,
                        "istable": istable, "editable_grid": 1 if istable else 0,
                        "track_changes": 0 if istable else 1, "allow_rename": 1,
                        "title_field": title_field, "search_fields": search_fields,
                        "sort_field": "modified", "sort_order": "DESC", "fields": fields,
                        "permissions": [] if istable else PERMS})
    d.flags.ignore_permissions = True
    d.insert()
    return True


def pf(name, doctype_name, html):
    exists = frappe.db.exists("Print Format", name)
    doc = frappe.get_doc("Print Format", name) if exists else frappe.new_doc("Print Format")
    doc.update({"name": name, "doc_type": doctype_name, "module": "Custom", "standard": "No",
                "custom_format": 1, "print_format_type": "Jinja", "disabled": 0,
                "margin_top": 12, "margin_bottom": 12, "letter_head": "MSCAST",
                "css": CSS, "html": html})
    doc.flags.ignore_permissions = True
    doc.save() if exists else doc.insert()


# ------------------------------------------------------------------- P-02
def rfq():
    if frappe.db.count("Request for Quotation"):
        return "already exists"
    mr = frappe.db.get_value("Material Request", {"docstatus": 1}, "name")
    mrd = frappe.get_doc("Material Request", mr)
    r = frappe.new_doc("Request for Quotation")
    r.company = COMPANY
    r.transaction_date = add_days(TODAY, -55)
    r.schedule_date = add_days(TODAY, -35)
    r.message_for_supplier = ("Please quote your best techno-commercial offer as per the attached "
                              "drawings and specifications. Indicate delivery period, payment terms "
                              "and any deviation from the specification.")
    for sup in ["Suvarna Copper Moulds (DEMO)", "Kalyani Gears & Drives (DEMO)",
                "Shivneri Machining Works (DEMO)"]:
        r.append("suppliers", {"supplier": sup})
    for it in mrd.items:
        r.append("items", {"item_code": it.item_code, "qty": it.qty, "warehouse": it.warehouse,
                           "schedule_date": add_days(TODAY, -35), "material_request": mr,
                           "material_request_item": it.name, "project": it.project})
    r.flags.ignore_permissions = True
    r.insert()
    r.submit()
    return "%s to 3 suppliers for %d items" % (r.name, len(r.items))


# ------------------------------------------------------------------ PC-17
PROFORMA_HTML = """
<div class="ms-title">PROFORMA INVOICE</div>
<table class="meta">
  <tr><td class="k">Proforma No.</td><td>PI/{{ doc.name }}</td>
      <td class="k">Date</td><td>{{ frappe.utils.formatdate(frappe.utils.nowdate(), "dd-MM-yyyy") }}</td></tr>
  <tr><td class="k">Customer</td><td>{{ doc.customer_name or doc.customer }}</td>
      <td class="k">Sales Order</td><td>{{ doc.name }} dated {{ frappe.utils.formatdate(doc.transaction_date, "dd-MM-yyyy") }}</td></tr>
  <tr><td class="k">Customer PO</td><td>{{ doc.customer_po_no or "-" }}</td>
      <td class="k">Contract delivery</td><td>{{ frappe.utils.formatdate(doc.contract_delivery_date, "dd-MM-yyyy") if doc.contract_delivery_date else "-" }}</td></tr>
</table>
<table class="ms">
  <thead><tr><th style="width:5%">#</th><th style="width:18%">Item</th><th>Description</th>
    <th style="width:9%" class="num">Qty</th><th style="width:7%">UOM</th>
    <th style="width:13%" class="num">Rate</th><th style="width:15%" class="num">Amount</th></tr></thead>
  <tbody>
  {% for r in doc.items %}
    <tr><td>{{ loop.index }}</td><td>{{ r.item_code }}</td><td>{{ r.description }}</td>
      <td class="num">{{ "{:,.2f}".format(r.qty) }}</td><td>{{ r.uom }}</td>
      <td class="num">{{ frappe.utils.fmt_money(r.rate, currency=doc.currency) }}</td>
      <td class="num">{{ frappe.utils.fmt_money(r.amount, currency=doc.currency) }}</td></tr>
  {% endfor %}
  </tbody>
</table>
<table class="meta">
  <tr><td class="k">Order value</td><td class="num">{{ frappe.utils.fmt_money(doc.grand_total, currency=doc.currency) }}</td>
      <td class="k">Advance due (30%)</td><td class="num">{{ frappe.utils.fmt_money(doc.grand_total * 0.3, currency=doc.currency) }}</td></tr>
  <tr><td class="k">Retention</td><td>{{ doc.retention_percent or 0 }} %</td>
      <td class="k">PBG</td><td>{{ doc.pbg_percent or 0 }} %</td></tr>
</table>
<div class="ms-note">
  This is a proforma invoice for advance payment / scheduled supply. It is not a tax invoice.<br>
  Bank: HDFC Bank · A/c 50200012345678 · IFSC HDFC0000123 · GSTIN 27AAGCM8444B1ZI
</div>
<table class="sign"><tr><td>Prepared by</td><td>Checked by</td><td>For MSCAST Engineering Pvt. Ltd.</td></tr></table>
"""


def proforma():
    pf("MSCAST Proforma Invoice", "Sales Order", PROFORMA_HTML)
    return "print format on Sales Order"


# ------------------------------------------------------------------ PR-07
CLAIM_HTML = """
<div class="ms-title">CLIENT CLAIM / VARIATION</div>
<table class="meta">
  <tr><td class="k">Claim No.</td><td>{{ doc.name }}</td>
      <td class="k">Type</td><td>{{ doc.claim_type }}</td>
      <td class="k">Status</td><td><span class="badge">{{ doc.status }}</span></td></tr>
  <tr><td class="k">Project</td><td>{{ doc.project }}</td>
      <td class="k">Customer</td><td>{{ doc.customer }}</td>
      <td class="k">Raised on</td><td>{{ frappe.utils.formatdate(doc.claim_date, "dd-MM-yyyy") if doc.claim_date else "-" }}</td></tr>
  <tr><td class="k">Claimed</td><td class="num">{{ frappe.utils.fmt_money(doc.claim_amount or 0, currency="INR") }}</td>
      <td class="k">Settled</td><td class="num">{{ frappe.utils.fmt_money(doc.settled_amount or 0, currency="INR") }}</td>
      <td class="k">Settled on</td><td>{{ frappe.utils.formatdate(doc.settlement_date, "dd-MM-yyyy") if doc.settlement_date else "-" }}</td></tr>
</table>
<div style="font-weight:600;margin:8px 0 4px;">Description of the claim</div>
<div style="border:1px solid #c6cbd4;padding:6px;min-height:60px;">{{ doc.description or "" }}</div>
{% if doc.settlement_notes %}
<div style="font-weight:600;margin:8px 0 4px;">Settlement</div>
<div style="border:1px solid #c6cbd4;padding:6px;">{{ doc.settlement_notes }}</div>
{% endif %}
<table class="sign"><tr><td>Projects</td><td>Commercial</td><td>Customer acceptance</td></tr></table>
"""


def claims():
    created = doctype("MSCAST Client Claim", [
        f("naming_series", "Series", "Select", options="CLM-.YYYY.-", default="CLM-.YYYY.-", reqd=1),
        f("project", "Project", "Link", options="Project", reqd=1, in_list_view=1, in_standard_filter=1),
        f("customer", "Customer", "Link", options="Customer", in_list_view=1),
        f("claim_type", "Claim Type", "Select",
          options="Scope variation\nPrice escalation\nIdle time at site\nDelay by customer\nExtra work",
          in_list_view=1),
        f("cb0", "", "Column Break"),
        f("claim_date", "Claim Date", "Date", in_list_view=1),
        f("claim_amount", "Claim Amount", "Currency", in_list_view=1),
        f("status", "Status", "Select", options="Open\nUnder discussion\nAgreed\nSettled\nRejected",
          default="Open", in_list_view=1, in_standard_filter=1),
        f("sb0", "Details", "Section Break"),
        f("description", "Description", "Small Text"),
        f("sb1", "Settlement", "Section Break"),
        f("settled_amount", "Settled Amount", "Currency"),
        f("settlement_date", "Settlement Date", "Date"),
        f("cb1", "", "Column Break"),
        f("sales_invoice", "Billed through", "Link", options="Sales Invoice"),
        f("settlement_notes", "Settlement Notes", "Small Text"),
    ], title_field="project", search_fields="project,customer,status")
    pf("MSCAST Client Claim Print", "MSCAST Client Claim", CLAIM_HTML)
    frappe.db.set_value("DocType", "MSCAST Client Claim", "default_print_format",
                        "MSCAST Client Claim Print")

    p1 = frappe.db.get_value("Project", {"project_name": ("like", "CCM 2-Strand%")}, "name")
    if not frappe.db.count("MSCAST Client Claim"):
        ins({"doctype": "MSCAST Client Claim", "project": p1,
             "customer": "Sahyadri Steels Ltd (DEMO)", "claim_type": "Scope variation",
             "claim_date": add_days(TODAY, -30), "claim_amount": 685000, "status": "Agreed",
             "description": "Customer asked for an additional 3 m run-out roller table and a second "
                            "dummy bar storage cradle, outside the original scope.",
             "settled_amount": 640000, "settlement_date": add_days(TODAY, -12),
             "settlement_notes": "Settled at Rs 6.40 L in the commercial meeting of "
                                 + str(add_days(TODAY, -12)) + "; to be billed with dispatch lot 3."})
        ins({"doctype": "MSCAST Client Claim", "project": p1,
             "customer": "Sahyadri Steels Ltd (DEMO)", "claim_type": "Idle time at site",
             "claim_date": add_days(TODAY, -6), "claim_amount": 235000, "status": "Under discussion",
             "description": "Erection team idle for 9 days at site awaiting customer civil foundation "
                            "and power supply readiness."})
    return "doctype + print format + 2 claims" if created else "claims updated"


# ------------------------------------------------------------ AC-14 / AC-15
def intangibles_and_cwip():
    made = []
    fa_soft = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Software%"), "is_group": 0}, "name")
    acc_dep = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Accumulated Depreciation%"), "is_group": 0}, "name")
    dep_exp = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Depreciation%"), "is_group": 0, "root_type": "Expense"}, "name")
    cwip_acc = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Capital Work in Progress%"), "is_group": 0}, "name") \
        or frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%CWIP%"), "is_group": 0}, "name")
    if not cwip_acc:
        parent = frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Fixed Asset%"), "is_group": 1}, "name")
        if parent:
            cwip_acc = ins({"doctype": "Account", "account_name": "Capital Work in Progress",
                            "parent_account": parent, "company": COMPANY, "root_type": "Asset",
                            "account_type": "Capital Work in Progress"}).name
            made.append("CWIP account")
    frappe.db.set_value("Company", COMPANY, "capital_work_in_progress_account", cwip_acc)

    cat = "Software (Intangible)"
    if not frappe.db.exists("Asset Category", cat):
        ins({"doctype": "Asset Category", "asset_category_name": cat, "enable_cwip_accounting": 0,
             "accounts": [{"company_name": COMPANY, "fixed_asset_account": fa_soft,
                           "accumulated_depreciation_account": acc_dep,
                           "depreciation_expense_account": dep_exp}],
             "finance_books": [{"depreciation_method": "Straight Line",
                                "total_number_of_depreciations": 36, "frequency_of_depreciation": 1}]})
        made.append("intangible asset category")
    cat2 = "Plant under construction (CWIP)"
    if not frappe.db.exists("Asset Category", cat2):
        ins({"doctype": "Asset Category", "asset_category_name": cat2, "enable_cwip_accounting": 1,
             "accounts": [{"company_name": COMPANY,
                           "fixed_asset_account": frappe.db.get_value("Account", {"company": COMPANY, "account_name": ("like", "%Plant and Machinery%"), "is_group": 0}, "name"),
                           "accumulated_depreciation_account": acc_dep,
                           "depreciation_expense_account": dep_exp,
                           "capital_work_in_progress_account": cwip_acc}],
             "finance_books": [{"depreciation_method": "Straight Line",
                                "total_number_of_depreciations": 120, "frequency_of_depreciation": 1}]})
        made.append("CWIP asset category")

    hsn = frappe.db.get_value("GST HSN Code", {"name": ("like", "8523%")}, "name") \
        or frappe.db.get_value("GST HSN Code", {}, "name")
    for code, name, cate in [("FA-ERP-SW", "ERP software licence (intangible)", cat),
                             ("FA-TEST-BENCH", "Hydraulic test bench under construction", cat2)]:
        if not frappe.db.exists("Item", code):
            ins({"doctype": "Item", "item_code": code, "item_name": name,
                 "item_group": "All Item Groups", "stock_uom": "Nos", "is_fixed_asset": 1,
                 "is_stock_item": 0, "asset_category": cate, "gst_hsn_code": hsn,
                 "item_defaults": [{"company": COMPANY}]})

    loc = frappe.db.get_value("Location", {}, "name")
    if not frappe.db.exists("Asset", {"item_code": "FA-ERP-SW"}):
        a = ins({"doctype": "Asset", "asset_name": "ERP software licence", "item_code": "FA-ERP-SW",
                 "asset_category": cat, "company": COMPANY, "is_existing_asset": 1,
                 "asset_quantity": 1, "location": loc,
                 "purchase_date": add_months(TODAY, -3), "available_for_use_date": add_months(TODAY, -3),
                 "gross_purchase_amount": 240000, "purchase_amount": 240000,
                 "net_purchase_amount": 240000, "calculate_depreciation": 1,
                 "finance_books": [{"depreciation_method": "Straight Line",
                                    "total_number_of_depreciations": 36,
                                    "frequency_of_depreciation": 1,
                                    "depreciation_start_date": add_months(TODAY, -2)}]})
        try:
            a.submit()
            made.append("intangible asset %s (amortised over 36 months)" % a.name)
        except Exception as e:
            made.append("intangible asset draft: " + repr(e)[:90])
    if not frappe.db.exists("Asset", {"item_code": "FA-TEST-BENCH"}):
        a2 = ins({"doctype": "Asset", "asset_name": "Hydraulic test bench (under construction)",
                  "item_code": "FA-TEST-BENCH", "asset_category": cat2, "company": COMPANY,
                  "is_existing_asset": 1, "asset_quantity": 1, "location": loc,
                  "purchase_date": add_months(TODAY, -2),
                  "available_for_use_date": add_months(TODAY, 3),
                  "gross_purchase_amount": 780000, "purchase_amount": 780000,
                  "net_purchase_amount": 780000, "calculate_depreciation": 0})
        try:
            a2.submit()
            made.append("CWIP asset %s (in progress, available for use in 3 months)" % a2.name)
        except Exception as e:
            made.append("CWIP asset draft: " + repr(e)[:90])
    return "; ".join(made) or "(all existed)"


# ------------------------------------------------------------------ AC-13
def customer_assets():
    created = doctype("MSCAST Customer Asset", [
        f("naming_series", "Series", "Select", options="CUSTASSET-.YYYY.-", default="CUSTASSET-.YYYY.-", reqd=1),
        f("asset_description", "Asset / Tooling", "Data", reqd=1, in_list_view=1),
        f("owner_customer", "Owned by (Customer)", "Link", options="Customer", reqd=1,
          in_list_view=1, in_standard_filter=1),
        f("project", "Project", "Link", options="Project", in_standard_filter=1),
        f("identification_no", "Identification / Tag No.", "Data", in_list_view=1),
        f("cb0", "", "Column Break"),
        f("received_on", "Received On", "Date", in_list_view=1),
        f("location", "Held At", "Data"),
        f("indicative_value", "Indicative Value (not capitalised)", "Currency"),
        f("status", "Status", "Select", options="In our custody\nAt sub-contractor\nReturned\nConsumed",
          default="In our custody", in_list_view=1, in_standard_filter=1),
        f("returned_on", "Returned On", "Date"),
        f("sb0", "Notes", "Section Break"),
        f("remarks", "Remarks", "Small Text",
          description="Customer-owned assets are NOT capitalised in MSCAST's books; this register "
                      "supports the Companies Act disclosure of assets held on behalf of others."),
    ], title_field="asset_description", search_fields="owner_customer,identification_no,status")
    if not frappe.db.count("MSCAST Customer Asset"):
        p1 = frappe.db.get_value("Project", {"project_name": ("like", "CCM 2-Strand%")}, "name")
        ins({"doctype": "MSCAST Customer Asset",
             "asset_description": "Customer-supplied copper mould tube set (free issue)",
             "owner_customer": "Sahyadri Steels Ltd (DEMO)", "project": p1,
             "identification_no": "SSL/MT/2026/07", "received_on": add_days(TODAY, -40),
             "location": "MSCAST stores, Pune", "indicative_value": 740000,
             "status": "In our custody",
             "remarks": "Received free of cost from the customer for fitment; not capitalised."})
        ins({"doctype": "MSCAST Customer Asset",
             "asset_description": "Customer gauges and inspection fixtures",
             "owner_customer": "Deccan Extrusions Pvt Ltd (DEMO)",
             "identification_no": "DEPL/GAUGE/11", "received_on": add_days(TODAY, -18),
             "location": "Pushkar Fabricators (sub-contractor)", "indicative_value": 125000,
             "status": "At sub-contractor",
             "remarks": "Issued onward to the fabricator against acknowledgement."})
    return "register + 2 records" if created else "records updated"


# ------------------------------------------------------------------ AC-08
def share_capital():
    made = []
    if not frappe.db.count("Shareholder"):
        for title, folk in [("Mustaque Ahmed N. Chandankeri", 7000),
                            ("Aiqaz M. Chandankeri", 2000),
                            ("Zameer Alam Chandankeri", 1000)]:
            ins({"doctype": "Shareholder", "title": title, "company": COMPANY,
                 "is_company": 0, "folio_no": "FOLIO-%04d" % folk})
        made.append("3 shareholders")
    if not frappe.db.exists("Share Type", "Equity"):
        ins({"doctype": "Share Type", "title": "Equity"})
    if not frappe.db.count("Share Transfer"):
        holders = frappe.get_all("Shareholder", pluck="name")
        allot = [(holders[0], 7000), (holders[1], 2000), (holders[2], 1000)]
        for holder, qty in allot:
            ins({"doctype": "Share Transfer", "transfer_type": "Issue", "date": "2026-04-01",
                 "to_shareholder": holder, "share_type": "Equity", "from_no": 1,
                 "to_no": qty, "no_of_shares": qty, "rate": 10, "amount": qty * 10,
                 "company": COMPANY,
                 "equity_or_liability_account": frappe.db.get_value(
                     "Account", {"company": COMPANY, "root_type": "Equity", "is_group": 0}, "name"),
                 "asset_account": frappe.db.get_value(
                     "Account", {"company": COMPANY, "account_type": "Bank", "is_group": 0}, "name")},
                submit=True)
        made.append("share issue 10,000 equity shares of Rs 10 (paid-up Rs 1,00,000)")
    return "; ".join(made) or "(already exists)"


def run():
    step("request for quotation", rfq)
    step("proforma invoice print", proforma)
    step("client claims register", claims)
    step("intangible assets + CWIP", intangibles_and_cwip)
    step("customer-owned asset register", customer_assets)
    step("share capital records", share_capital)
    frappe.clear_cache()
    log("BATCH B DONE")


run()
