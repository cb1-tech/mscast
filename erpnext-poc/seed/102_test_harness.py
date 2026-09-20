"""MSCAST POC - 102: full test harness.

The daily summary shipped with two wrong numbers because a SQL literal ('Approved') did not match
the field's real options ('Approved by Customer'). Nothing in the stack catches that - the query
runs, returns a number, and the number is wrong. T1 below is the systematic version of that check
across every custom report; the rest validate execution, dates, prints, the ledger, the controls
and the seeded data itself.
"""
import re
import frappe
from frappe.utils import flt, nowdate

COMPANY = "MSCAST Engineering Pvt Ltd"
TODAY = nowdate()
R = []          # (id, area, name, status, detail)
log = lambda m: print("[T] " + m, flush=True)


def rec(tid, area, name, ok, detail=""):
    status = "PASS" if ok is True else ("WARN" if ok == "warn" else "FAIL")
    R.append((tid, area, name, status, detail))
    log("%-5s %-9s %-58s %s%s" % (tid, status, name[:58], detail[:150],
                                  "" if len(detail) <= 150 else "..."))


def custom_reports():
    return frappe.get_all("Report", filters={"is_standard": "No"}, fields=["name", "query"])


# ---------------------------------------------------------------- T1 literals
def t1_literals():
    tables = re.compile(r"`tab([^`]+)`")
    eq = re.compile(r"(?:\w+\.)?(\w+)\s*(?:=|!=|<>)\s*'([^']*)'")
    inl = re.compile(r"(?:\w+\.)?(\w+)\s+(?:not\s+)?in\s*\(([^)]*)\)", re.I)
    bad, checked = [], 0
    for rep in custom_reports():
        q = rep.query or ""
        if not q:
            continue
        dts = [d for d in set(tables.findall(q)) if frappe.db.exists("DocType", d)]
        metas = {}
        for d in dts:
            try:
                metas[d] = frappe.get_meta(d)
            except Exception:
                pass
        pairs = [(f, v) for f, v in eq.findall(q)]
        for f, vals in inl.findall(q):
            for v in re.findall(r"'([^']*)'", vals):
                pairs.append((f, v))
        for fname, val in pairs:
            if not val:
                continue
            opts_seen, match = [], False
            for d, m in metas.items():
                fl = m.get_field(fname)
                if fl and fl.fieldtype == "Select" and fl.options:
                    o = [x.strip() for x in fl.options.split("\n") if x.strip()]
                    opts_seen.append((d, o))
                    if val in o:
                        match = True
            if opts_seen and not match:
                checked += 1
                bad.append("%s: %s = '%s' (valid: %s)"
                           % (rep.name[:40], fname, val,
                              "/".join(opts_seen[0][1])[:90]))
            elif opts_seen:
                checked += 1
    rec("T1", "reports", "SQL literals match the field's real Select options",
        True if not bad else False,
        "%d literal comparisons checked, %d mismatched%s"
        % (checked, len(bad), (" :: " + " | ".join(bad)) if bad else ""))


# ---------------------------------------------------------------- T2 execution
def t2_execute():
    fails = []
    for rep in custom_reports():
        if not rep.query:
            continue
        try:
            frappe.db.sql(rep.query)
        except Exception as e:
            fails.append("%s: %s" % (rep.name[:40], repr(e)[:110]))
    rec("T2", "reports", "every custom report executes", not fails,
        "%d reports, %d failed%s" % (len(custom_reports()), len(fails),
                                     (" :: " + " | ".join(fails)) if fails else ""))


# ---------------------------------------------------------------- T3 dates
def t3_dates():
    bad = []
    for rep in custom_reports():
        q = rep.query or ""
        if re.search(r"\bcurdate\(\)|\bcurrent_date\b|\bnow\(\)", q, re.I):
            if "convert_tz" not in q:
                bad.append(rep.name)
            elif re.search(r"(?<!convert_tz\(utc_timestamp\(\),'\+00:00','\+05:30'\))\bcurdate\(\)", q):
                bad.append(rep.name + " (mixed)")
    rec("T3", "reports", "dates use the Indian day, not the container's UTC day", not bad,
        "offenders: %s" % (", ".join(bad) if bad else "none"))


# ---------------------------------------------------------------- T4 prints
def t4_prints():
    fails, done = [], 0
    for p in frappe.get_all("Print Format", filters={"standard": "No", "disabled": 0},
                            fields=["name", "doc_type"]):
        if not p.doc_type or not frappe.db.exists("DocType", p.doc_type):
            continue
        docname = frappe.db.get_value(p.doc_type, {}, "name")
        if not docname:
            fails.append("%s: no %s document to render" % (p.name[:40], p.doc_type))
            continue
        try:
            html = frappe.get_print(p.doc_type, docname, print_format=p.name)
            done += 1
            if len(html) < 400:
                fails.append("%s: rendered only %d chars" % (p.name[:40], len(html)))
        except Exception as e:
            fails.append("%s: %s" % (p.name[:40], repr(e)[:110]))
    rec("T4", "prints", "every custom print format renders", not fails,
        "%d rendered, %d problems%s" % (done, len(fails),
                                        (" :: " + " | ".join(fails)) if fails else ""))


# ---------------------------------------------------------------- T5 ledger
def t5_ledger():
    tb = flt(frappe.db.sql("""select round(sum(debit - credit), 2) from `tabGL Entry`
                              where is_cancelled = 0 and company = %s""", COMPANY)[0][0])
    rec("T5a", "ledger", "trial balance nets to zero", abs(tb) < 0.01, "difference %s" % tb)

    def run_named(nm):
        q = frappe.db.get_value("Report", nm, "query")
        return frappe.db.sql(q) if q else []

    try:
        bs = run_named("MSCAST Balance Sheet (Schedule III)")
        tot = [flt(r[2]) for r in bs if (r[1] or "").strip() == "TOTAL"]
        ok = len(tot) == 2 and abs(tot[0] - tot[1]) < 1
        rec("T5b", "ledger", "Schedule III balance sheet balances", ok,
            "equity+liabilities %s vs assets %s" % (tot[0] if tot else "?",
                                                    tot[1] if len(tot) > 1 else "?"))
    except Exception as e:
        rec("T5b", "ledger", "Schedule III balance sheet balances", False, repr(e)[:150])

    try:
        pl = run_named("MSCAST Statement of Profit and Loss (Schedule III)")
        pat = [flt(r[2]) for r in pl if "Profit for the period" in (r[1] or "")][0]
        inc = flt(frappe.db.sql("""select sum(gl.credit - gl.debit) from `tabGL Entry` gl
            inner join `tabAccount` a on a.name = gl.account
            where gl.is_cancelled = 0 and a.root_type = 'Income'""")[0][0])
        exp = flt(frappe.db.sql("""select sum(gl.debit - gl.credit) from `tabGL Entry` gl
            inner join `tabAccount` a on a.name = gl.account
            where gl.is_cancelled = 0 and a.root_type = 'Expense'""")[0][0])
        rec("T5c", "ledger", "P&L profit ties to the ledger surplus", abs(pat - (inc - exp)) < 1,
            "statement %s vs ledger %s" % (pat, inc - exp))
    except Exception as e:
        rec("T5c", "ledger", "P&L profit ties to the ledger surplus", False, repr(e)[:150])

    orphan = frappe.db.sql("""select count(*) from `tabGL Entry`
                              where is_cancelled = 0 and ifnull(cost_center,'') = ''
                                and account not in (select name from `tabAccount`
                                                    where account_type in ('Receivable','Payable'))""")[0][0]
    rec("T5d", "ledger", "no ledger entry without a cost centre", orphan == 0,
        "%d entries" % orphan)


# ---------------------------------------------------------------- T6 controls
def t6_controls():
    pi = frappe.db.get_value("Purchase Invoice", {"docstatus": 1, "outstanding_amount": (">", 0)},
                             ["name", "supplier", "bill_no", "outstanding_amount", "credit_to"],
                             as_dict=True)
    blocked = None
    if pi:
        brm = frappe.db.get_value("MSCAST BRM", {"supplier": pi.supplier,
                                                 "supplier_invoice_no": pi.bill_no}, "status")
        try:
            pe = frappe.new_doc("Payment Entry")
            pe.payment_type = "Pay"
            pe.company = COMPANY
            pe.posting_date = TODAY
            pe.party_type = "Supplier"
            pe.party = pi.supplier
            pe.paid_from = frappe.db.get_value("Account", {"company": COMPANY,
                                                           "account_type": "Bank",
                                                           "is_group": 0}, "name")
            pe.paid_to = pi.credit_to
            pe.paid_amount = pe.received_amount = pi.outstanding_amount
            pe.reference_no = "HARNESS/T6"
            pe.reference_date = TODAY
            pe.append("references", {"reference_doctype": "Purchase Invoice",
                                     "reference_name": pi.name,
                                     "total_amount": pi.outstanding_amount,
                                     "outstanding_amount": pi.outstanding_amount,
                                     "allocated_amount": pi.outstanding_amount})
            pe.flags.ignore_permissions = True
            pe.insert()
            pe.submit()
            blocked = False
            pe.cancel()
        except Exception as e:
            blocked = "Payment blocked" in str(e)
        frappe.db.rollback()
        expected = (brm != "Certified")
        rec("T6a", "controls", "BRM payment block refuses an uncertified supplier bill",
            blocked == expected,
            "bill %s, BRM status %s, payment %s" % (pi.bill_no, brm,
                                                    "blocked" if blocked else "allowed"))
    else:
        rec("T6a", "controls", "BRM payment block", "warn", "no open supplier bill to test with")

    bad = []
    for w in frappe.get_all("Workflow", fields=["name", "is_active", "document_type",
                                               "workflow_state_field"]):
        ns = frappe.db.count("Workflow Document State", {"parent": w.name})
        nt = frappe.db.count("Workflow Transition", {"parent": w.name})
        if not w.is_active or ns < 2 or nt < 1:
            bad.append("%s (active=%s states=%d transitions=%d)" % (w.name, w.is_active, ns, nt))
        if not frappe.db.exists("DocType", w.document_type):
            bad.append("%s -> missing doctype" % w.name)
    rec("T6b", "controls", "workflows are active and complete", not bad,
        "%d workflows%s" % (frappe.db.count("Workflow"),
                            (" :: " + "; ".join(bad)) if bad else ""))

    ss = frappe.get_all("Server Script", fields=["name", "disabled", "script_type"])
    live = [s for s in ss if not s.disabled]
    rec("T6c", "controls", "server scripts present and enabled where intended", len(live) >= 2,
        "; ".join("%s (%s, disabled=%s)" % (s.name, s.script_type, s.disabled) for s in ss))

    # T6d - the approval authority, asserted.
    #
    # Installing the app silently rewrote these back to an older definition and
    # nothing noticed: a decision the business had made was undone by a routine
    # operation. Business rules need a test like any other code, so the intended
    # matrix is written down here and checked on every run.
    #
    # The rule behind it: a decision that commits MSCAST to an outside party -
    # money to a supplier, a cost sheet going back, a bill certified for payment
    # - belongs to the directors.
    INTENDED = {
        ("MSCAST Purchase Order Approval", "Approve"): "MSCAST Director",
        ("MSCAST PCC Approval", "Approve"): "MSCAST Director",
        ("MSCAST PCC Approval", "Send Back"): "MSCAST Director",
        ("MSCAST BRM Certification", "Certify"): "MSCAST Director",
        ("MSCAST Project Kick-off", "Approve Kick-off"): "MSCAST Director",
    }
    drift = []
    for (wf_name, action), want in sorted(INTENDED.items()):
        if not frappe.db.exists("Workflow", wf_name):
            drift.append("%s missing" % wf_name)
            continue
        got = [t.allowed for t in frappe.get_doc("Workflow", wf_name).transitions
               if t.action == action]
        if not got:
            drift.append("%s/%s missing" % (wf_name, action))
        elif any(g != want for g in got):
            drift.append("%s/%s is %s, should be %s"
                         % (wf_name, action, "/".join(sorted(set(got))), want))
    rec("T6d", "controls", "approval authority is where the business put it", not drift,
        "%d transitions checked" % len(INTENDED) if not drift
        else " :: ".join(drift))

    # T6e - nobody may both raise and approve the same document.
    def role_holders(role):
        return {u[0] for u in frappe.db.sql(
            """select distinct h.parent from `tabHas Role` h join `tabUser` u
               on u.name = h.parent where h.role = %s and u.enabled = 1
               and u.user_type = 'System User'
               and u.name not in (
                   select parent from `tabHas Role` where role = 'System Manager'
               )""", (role,))}
    # Administrators are excluded above: someone with System Manager can already
    # do anything, so counting them as a segregation breach says nothing useful.
    # The question this asks is whether an ORDINARY user can raise and approve
    # the same document.

    PAIRS = [("MSCAST Purchase Order Approval", "Send for Approval", "Approve"),
             ("MSCAST PCC Approval", "Send for Approval", "Approve"),
             ("MSCAST Project Kick-off", "Verify Customer PO", "Approve Kick-off")]
    clashes = []
    for wf_name, prep, appr in PAIRS:
        if not frappe.db.exists("Workflow", wf_name):
            continue
        doc = frappe.get_doc("Workflow", wf_name)
        p = set().union(*[role_holders(t.allowed) for t in doc.transitions
                          if t.action == prep] or [set()])
        a = set().union(*[role_holders(t.allowed) for t in doc.transitions
                          if t.action == appr] or [set()])
        both = p & a
        if both:
            clashes.append("%s: %s" % (wf_name.replace("MSCAST ", ""),
                                       ", ".join(sorted(both))))
    rec("T6e", "controls", "nobody can both raise and approve the same document",
        "warn" if clashes else True,
        " :: ".join(clashes) if clashes else "no overlap on %d workflows" % len(PAIRS))

    # T6f - who bypasses all of the above.
    #
    # T6e excludes System Manager holders, because someone who can do anything
    # is not a meaningful segregation breach. That exclusion is correct and it
    # is also a blind spot: an ordinary member of staff carrying System Manager
    # disappears from T6e entirely while being able to approve anything. That
    # is exactly what had happened - an operational account held it and nothing
    # said so. So the exclusion is reported rather than hidden.
    #
    # Administrator is expected. A named administrator is expected. An account
    # that also does day-to-day work is not.
    EXPECTED_ADMINS = {"Administrator", "admin@mscast.local"}
    admins = {u[0] for u in frappe.db.sql(
        """select h.parent from `tabHas Role` h join `tabUser` u on u.name = h.parent
           where h.role = 'System Manager' and u.enabled = 1
             and u.user_type = 'System User'""")}
    unexpected = sorted(admins - EXPECTED_ADMINS)
    detail = []
    for name in unexpected:
        other = sorted(x[0] for x in frappe.db.sql(
            """select role from `tabHas Role` where parent = %s
               and role != 'System Manager'""", (name,)))
        detail.append("%s (also holds %s)"
                      % (name, ", ".join(other[:4]) + ("..." if len(other) > 4 else "")
                         if other else "nothing else"))
    rec("T6f", "controls", "only administrators hold System Manager",
        "warn" if unexpected else True,
        " :: ".join(detail) if unexpected
        else "%d System Manager holders, all expected" % len(admins))


# ---------------------------------------------------------------- T7 data
def t7_data():
    empty = []
    for d in frappe.get_all("DocType", filters={"custom": 1, "istable": 0}, pluck="name"):
        if not frappe.db.count(d):
            empty.append(d)
    rec("T7a", "data", "every MSCAST form has demo records", not empty,
        "empty: %s" % (", ".join(empty) if empty else "none"))

    bad = []
    for d in frappe.get_all("DocType", filters={"custom": 1}, pluck="name"):
        meta = frappe.get_meta(d)
        for fl in meta.fields:
            if fl.fieldtype != "Select" or not fl.options or not fl.fieldname:
                continue
            opts = [x.strip() for x in fl.options.split("\n") if x.strip()]
            if not opts:
                continue
            try:
                rows = frappe.db.sql("select distinct `%s` from `tab%s` where ifnull(`%s`,'') != ''"
                                     % (fl.fieldname, d, fl.fieldname))
            except Exception:
                continue
            for (v,) in rows:
                if v not in opts:
                    bad.append("%s.%s = '%s' not in options" % (d, fl.fieldname, v))
    rec("T7b", "data", "stored Select values are all valid options", not bad,
        "%d violations%s" % (len(bad), (" :: " + "; ".join(bad[:6])) if bad else ""))

    nogst = frappe.db.sql("""select count(distinct sii.item_code) from `tabSales Invoice Item` sii
        inner join `tabSales Invoice` si on si.name = sii.parent
        inner join `tabItem` i on i.name = sii.item_code
        where si.docstatus = 1 and ifnull(i.gst_hsn_code,'') = ''""")[0][0]
    rec("T7c", "data", "every invoiced item carries an HSN code", nogst == 0,
        "%d items without HSN" % nogst)


# ---------------------------------------------------------------- T8 gst
def t8_gst():
    rows = frappe.db.sql("""
        select si.name, si.taxes_and_charges,
               (select count(*) from `tabSales Taxes and Charges` t
                where t.parent = si.name and t.account_head like '%%IGST%%') as igst,
               (select count(*) from `tabSales Taxes and Charges` t
                where t.parent = si.name and (t.account_head like '%%CGST%%'
                                              or t.account_head like '%%SGST%%')) as cgst,
               a.gstin, ca.gstin as company_gstin
        from `tabSales Invoice` si
        left join `tabAddress` a on a.name = si.customer_address
        left join `tabAddress` ca on ca.name = si.company_address
        where si.docstatus = 1 and si.is_return = 0""", as_dict=True)
    bad = []
    for r in rows:
        if not r.gstin or not r.company_gstin:
            continue
        inter = r.gstin[:2] != r.company_gstin[:2]
        if inter and not r.igst:
            bad.append("%s: inter-state but no IGST" % r.name)
        if not inter and not r.cgst:
            bad.append("%s: intra-state but no CGST/SGST" % r.name)
    rec("T8", "gst", "GST head matches the place of supply on every invoice", not bad,
        "%d invoices checked%s" % (len(rows), (" :: " + "; ".join(bad)) if bad else ""))


# ---------------------------------------------------------------- T9 automation
def t9_automation():
    out_acc = frappe.db.get_value("Email Account", {"default_outgoing": 1, "enable_outgoing": 1},
                                  "name")
    has_pw = bool(frappe.db.get_value("Email Account", out_acc, "password")) if out_acc else False
    rec("T9a", "email", "outgoing mail account configured", bool(out_acc) and has_pw,
        "account %s, password set %s" % (out_acc, has_pw))

    sent = frappe.db.count("Email Queue", {"status": "Sent"})
    err = frappe.db.count("Email Queue", {"status": "Error"})
    rec("T9b", "email", "mail actually leaves the system", sent > 0 and err == 0,
        "%d sent, %d errored" % (sent, err))

    cron = frappe.db.get_value("Scheduled Job Type", {"server_script": "MSCAST morning report batch"},
                               ["name", "cron_format", "stopped"], as_dict=True)
    rec("T9c", "email", "morning report batch scheduled", bool(cron) and not cron.stopped,
        "%s at %s" % (cron.name, cron.cron_format) if cron else "not found")

    dead = []
    for n in frappe.get_all("Notification", filters={"name": ("like", "MSCAST%"), "enabled": 1},
                            pluck="name"):
        live = 0
        for r in frappe.get_all("Notification Recipient", filters={"parent": n},
                                fields=["receiver_by_role", "receiver_by_document_field"]):
            if r.receiver_by_document_field:
                live += 1
            if r.receiver_by_role:
                us = frappe.get_all("Has Role", filters={"role": r.receiver_by_role,
                                                         "parenttype": "User"}, pluck="parent")
                live += len([u for u in us if frappe.db.get_value("User", u, "enabled")
                             and not frappe.db.get_value("User", u, "unsubscribed")])
        if not live:
            dead.append(n)
    rec("T9d", "email", "every enabled notification has a live recipient", not dead,
        "dead: %s" % (", ".join(dead) if dead else "none"))

    # Deliverable domains. The point of this check is to catch a live user on a
    # made-up domain such as @mscast.demo, not to police which real provider
    # somebody uses - so the mailboxes MSCAST actually gave us are listed here.
    bounce = frappe.db.sql("""select count(*) from `tabUser` where enabled = 1
        and unsubscribed = 0
        and name not like '%%@gmail.com'
        and name not like '%%@carobar%%'
        and name not like '%%@yahoo.com'
        and name not like '%%@hotmail.com'
        and name not in ('Guest','Administrator')""")[0][0]
    rec("T9e", "email", "no live user on a non-deliverable domain", bounce == 0,
        "%d users would bounce" % bounce)


# ---------------------------------------------------------------- T10 hr
def t10_hr():
    slips = frappe.db.count("Salary Slip", {"docstatus": 1})
    att = frappe.db.count("Attendance", {"docstatus": 1})
    dup = frappe.db.sql("""select count(*) from (select employee, attendance_date, count(*) c
        from `tabAttendance` where docstatus = 1 group by employee, attendance_date
        having c > 1) x""")[0][0]
    rec("T10a", "hr", "payroll and attendance loaded", slips > 0 and att > 0,
        "%d salary slips, %d attendance records" % (slips, att))
    rec("T10b", "hr", "no duplicate attendance for an employee on a date", dup == 0,
        "%d duplicates" % dup)
    punches = frappe.db.count("Employee Checkin")
    linked = frappe.db.count("Employee Checkin", {"attendance": ("is", "set")})
    rec("T10c", "hr", "biometric punches converted into attendance", punches > 0 and linked > 0,
        "%d punches, %d linked to attendance" % (punches, linked))


def run():
    for fn in (t1_literals, t2_execute, t3_dates, t4_prints, t5_ledger, t6_controls,
               t7_data, t8_gst, t9_automation, t10_hr):
        try:
            fn()
        except Exception as e:
            rec(fn.__name__, "harness", "test crashed", False, repr(e)[:250])
    p = sum(1 for r in R if r[3] == "PASS")
    w = sum(1 for r in R if r[3] == "WARN")
    f = sum(1 for r in R if r[3] == "FAIL")
    log("=" * 78)
    log("RESULT: %d PASS, %d WARN, %d FAIL out of %d checks" % (p, w, f, len(R)))
    for r in R:
        if r[3] != "PASS":
            log("  %s %-5s %s -- %s" % (r[3], r[0], r[2][:56], r[4][:200]))
    log("=" * 78)


run()
