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
def t1b_script_literals():
    # T1b - T1 for server scripts. Every "field": "literal" in a server script's
    # filters must be one of that field's real Select options. The home page
    # counted BRMs 'Pending Certification' (the option is 'Pending') and claims
    # 'Submitted' (not an option at all), so both counts were always zero - and
    # T1 only read reports. Found 21 Sep 2026 while reviewing the demo screenshots.
    pat_call = re.compile(r'"([A-Z][\w ]+)",\s*(?:filters=)?\{([^{}]*)\}')
    pat_kv = re.compile(r'"(\w+)":\s*("[^"]*"|\[[^\]]*\[[^\]]*\]\]|\[[^\]]*\])')
    bad, checked = [], 0
    for sname, src in frappe.get_all("Server Script", filters={"disabled": 0}, fields=["name", "script"], as_list=True):
        for m in pat_call.finditer(src or ""):
            dt, body = m.group(1), m.group(2)
            if not frappe.db.exists("DocType", dt):
                continue
            meta = frappe.get_meta(dt)
            for f, val in pat_kv.findall(body):
                fld = meta.get_field(f)
                if not fld or fld.fieldtype != "Select":
                    continue
                opts = [o.strip() for o in (fld.options or "").split("\n") if o.strip()]
                for v in re.findall(r'"([^"]+)"', val):
                    if v in ("in", "not in", "!=", "="):
                        continue
                    checked += 1
                    if v not in opts:
                        bad.append("%s: %s.%s = '%s'" % (sname, dt, f, v))
    rec("T1b", "reports", "server-script literals match the fields' real Select options",
        not bad and checked > 0, ("; ".join(bad[:4])) if bad else "%d literal comparisons checked, 0 mismatched" % checked)


def t1c_server_scripts_on():
    # T1c - server scripts actually run. server_script_enabled lives in the
    # bench-wide common_site_config.json, so a restore onto another bench does not
    # carry it and every MSCAST server script (home page, BRM rules, morning batch)
    # is silently off while every other check still passes. Found 21 Sep 2026
    # building the dev instance.
    from frappe.utils.safe_exec import is_safe_exec_enabled
    n = frappe.db.count("Server Script", {"disabled": 0})
    on = bool(is_safe_exec_enabled())
    rec("T1c", "reports", "server scripts are enabled on this bench",
        on, "%d enabled MSCAST server scripts; server_script_enabled=%s" % (n, on))


def t2_execute():
    fails = []
    for rep in custom_reports():
        if not rep.query:
            continue
        try:
            # With a values dict, as the desk runs it. Without one the driver skips
            # %-formatting, and six reports that failed for every user passed here
            # (found 21 Sep 2026).
            frappe.db.sql(rep.query, {})
        except Exception as e:
            fails.append("%s: %s" % (rep.name[:40], repr(e)[:110]))
    rec("T2", "reports", "every custom report executes", not fails,
        "%d reports, %d failed%s" % (len(custom_reports()), len(fails),
                                     (" :: " + " | ".join(fails)) if fails else ""))


def t2b_reports_as_users():
    # T2b - every report opens for the people meant to use it, through the real
    # report runner. T2 runs each report's SQL as Administrator, and on 21 Sep
    # 2026 said "28 reports, 0 failed" while the drawing office could not open
    # the Drawing Register and the MSME report failed with a 500 for accounts -
    # its name contained a '/', which the desk's URL splits. Found by logging in
    # as those people for the demo screenshots.
    from frappe.desk.query_report import run
    reps = frappe.get_all("Report", filters={"is_standard": "No"}, fields=["name", "ref_doctype"])
    problems = ["name unsafe in a URL: %s" % r.name for r in reps if any(c in r.name for c in "/%?#")]
    for r in reps:
        if r.ref_doctype and frappe.db.get_value("DocType", r.ref_doctype, "module") == "MSCAST":
            can = {p.role for p in frappe.get_meta(r.ref_doctype).permissions
                   if p.report and not p.permlevel} - {"All", "Guest", "Desk User"}
            have = {x.role for x in frappe.get_doc("Report", r.name).roles}
            if can - have:
                problems.append("%s closed to %s" % (r.name[:40], ", ".join(sorted(can - have))))
    users = frappe.get_all("User", filters={"enabled": 1, "user_type": "System User",
                                            "name": ["!=", "Administrator"]}, pluck="name")
    runs = 0
    for r in reps:
        roles = {x.role for x in frappe.get_doc("Report", r.name).roles}
        tried = set()
        for u in users:
            key = frozenset(frappe.get_roles(u))
            if key in tried:
                continue
            tried.add(key)
            frappe.set_user(u)
            # only people Frappe itself admits: a listed role AND the report right
            # on the document, possibly from different roles
            if not (frappe.get_doc("Report", r.name).is_permitted()
                    and frappe.has_permission(r.ref_doctype, "report")):
                frappe.set_user("Administrator")
                continue
            try:
                run(r.name, filters={})
                runs += 1
            except Exception as e:
                problems.append("%s as %s: %s" % (r.name[:40], frappe.db.get_value("User", u, "full_name"), str(e)[:70]))
            finally:
                frappe.set_user("Administrator")
    rec("T2b", "reports", "every report opens for the people meant to use it", not problems,
        (" :: ".join(problems[:4]) + (" (+%d more)" % (len(problems) - 4) if len(problems) > 4 else ""))
        if problems else "%d reports, %d runs as real users, all opened" % (len(reps), runs))


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
def t4b_watermark():
    # T4b - demonstration prints say so; production prints never do.
    #
    # The watermark was once a seed script, and an upgrade test on 21 Sep 2026
    # showed `bench migrate` stripping it from all 15 formats - which on the public
    # demo would have put the real GSTIN on unmarked invoices, with every other
    # check passing. It now lives in the app, switched by site config mscast_demo.
    MARK = "mscast-demo-watermark"
    demo = bool(frappe.conf.get("mscast_demo"))
    pf = [p for p in frappe.get_all("Print Format", filters={"custom_format": 1, "disabled": 0},
                                    fields=["name", "html"])
          if p.name.startswith("MSCAST") and (p.html or "").strip()]
    marked = [p.name for p in pf if MARK in (p.html or "")]
    if demo:
        bad = sorted(set(p.name for p in pf) - set(marked))
        rec("T4b", "prints", "demonstration site: every MSCAST print is watermarked", not bad,
            ("unmarked: " + ", ".join(bad[:4])) if bad else "%d of %d marked" % (len(marked), len(pf)))
    else:
        rec("T4b", "prints", "not a demonstration site: no print says DEMONSTRATION", not marked,
            ("marked: " + ", ".join(marked[:4])) if marked else "%d formats, none marked" % len(pf))


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
# --------------------------------------------------------- T6a payment block
def _bank_account():
    return frappe.db.get_value("Account", {"company": COMPANY, "account_type": "Bank",
                                           "is_group": 0}, "name")


def _attempt(build):
    """Run `build` to submit a document; return (went_through, message).

    Everything is rolled back either way, so the harness can attempt payments
    against live demo data without moving a rupee.
    """
    try:
        doc = build()
        doc.flags.ignore_permissions = True
        doc.insert()
        doc.submit()
        return True, doc.name
    except Exception as e:
        return False, str(e)
    finally:
        frappe.db.rollback()


def _pay_invoice(pi, amount=None):
    def build():
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Pay"
        pe.company = COMPANY
        pe.posting_date = TODAY
        pe.party_type = "Supplier"
        pe.party = pi.supplier
        pe.paid_from = _bank_account()
        pe.paid_to = pi.credit_to
        amt = flt(amount or pi.outstanding_amount)
        pe.paid_amount = pe.received_amount = amt
        pe.reference_no = "HARNESS/T6A"
        pe.reference_date = TODAY
        pe.append("references", {"reference_doctype": "Purchase Invoice",
                                 "reference_name": pi.name,
                                 "total_amount": pi.outstanding_amount,
                                 "outstanding_amount": pi.outstanding_amount,
                                 "allocated_amount": amt})
        return pe
    return build


def t6a_payment_block():
    open_pis = frappe.get_all(
        "Purchase Invoice", filters={"docstatus": 1, "outstanding_amount": (">", 0)},
        fields=["name", "supplier", "bill_no", "outstanding_amount", "credit_to"])

    def brm_of(pi):
        return frappe.db.get_value("MSCAST BRM",
                                   {"supplier": pi.supplier,
                                    "supplier_invoice_no": pi.bill_no},
                                   ["name", "status", "amount"], as_dict=True)

    certified = uncertified = None
    for pi in open_pis:
        b = brm_of(pi)
        if b and b.status == "Certified" and flt(b.amount) >= flt(pi.outstanding_amount):
            certified = certified or (pi, b)
        elif not b:
            uncertified = uncertified or pi

    if not (certified and uncertified):
        rec("T6a", "controls", "BRM payment block guards every payment route", "warn",
            "need one open bill with a full certified BRM and one with none; "
            "found certified=%s uncertified=%s"
            % (certified[0].name if certified else None,
               uncertified.name if uncertified else None))
        return

    cpi, cbrm = certified
    upi = uncertified
    fails = []

    def case(label, expect_blocked, build, must_say=None):
        went, msg = _attempt(build)
        blocked = (not went) and ("Payment blocked" in msg)
        ok = (blocked == expect_blocked)
        if ok and blocked and must_say and must_say not in msg:
            ok = False
            msg = "blocked for the wrong reason: " + msg
        if not went and not blocked and expect_blocked is False:
            msg = "refused by ERPNext, not by the control: " + msg
        if not ok:
            fails.append("%s -> %s (%s)"
                         % (label, "blocked" if blocked else "allowed", msg[:120]))
        return ok

    # 1. the control must not block a properly certified bill.
    case("certified bill pays", False, _pay_invoice(cpi))

    # 2. Payment Entry against a bill with no BRM at all.
    case("no BRM, payment entry", True, _pay_invoice(upi),
         must_say="no Billing Routing Memo")

    # 3. Journal Entry - the door the Server Script never guarded.
    def jv():
        je = frappe.new_doc("Journal Entry")
        je.company = COMPANY
        je.posting_date = TODAY
        je.voucher_type = "Journal Entry"
        je.user_remark = "HARNESS/T6A"
        je.append("accounts", {"account": upi.credit_to, "party_type": "Supplier",
                               "party": upi.supplier,
                               "debit_in_account_currency": upi.outstanding_amount})
        je.append("accounts", {"account": _bank_account(),
                               "credit_in_account_currency": upi.outstanding_amount})
        return je
    case("no BRM, journal entry", True, jv, must_say="no purchase invoice referenced")

    # 4. an advance with no invoice reference - the empty-loop hole.
    def advance():
        pe = frappe.new_doc("Payment Entry")
        pe.payment_type = "Pay"
        pe.company = COMPANY
        pe.posting_date = TODAY
        pe.party_type = "Supplier"
        pe.party = upi.supplier
        pe.paid_from = _bank_account()
        pe.paid_to = upi.credit_to
        pe.paid_amount = pe.received_amount = 50000
        pe.reference_no = "HARNESS/T6A"
        pe.reference_date = TODAY
        return pe
    case("advance, no reference", True, advance,
         must_say="no supplier invoice referenced")

    # 5. paying more than the certificate covers. The BRM is trimmed inside the
    #    attempt's own rollback window, so the demo data is untouched.
    def over():
        frappe.db.set_value("MSCAST BRM", cbrm.name, "amount",
                            flt(cpi.outstanding_amount) / 2, update_modified=False)
        return _pay_invoice(cpi)()
    case("amount above the certificate", True, over, must_say="certifies")

    # 6. the exemption - an electricity bill has to be payable.
    def exempt():
        frappe.db.set_value("Supplier", upi.supplier, "mscast_brm_exempt", 1,
                            update_modified=False)
        return _pay_invoice(upi)()
    case("BRM-exempt supplier pays", False, exempt)

    rec("T6a", "controls", "BRM payment block guards every payment route", not fails,
        "6 routes tested on %s / %s%s"
        % (cpi.name, upi.name, (" :: " + "; ".join(fails)) if fails else ""))


def t6_controls():
    # T6a - the BRM payment block, tested at every door rather than one.
    #
    # The Server Script this replaced guarded Payment Entry only, and a probe on
    # 21 Sep 2026 walked round it four ways: a Journal Entry, an advance with no
    # invoice reference, an amount larger than the certificate, and no exemption
    # for bills that cannot have a BRM at all. Each of those is a case below, and
    # each is proved by attempting the real transaction and reading what happened
    # - not by reading the configuration, which is what missed it the first time.
    t6a_payment_block()

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

    # T6c - one implementation of each control, in the right place.
    #
    # The BRM block was a Server Script until 21 Sep 2026. It now lives in the app
    # (mscast_erp.controls.brm_payment) where it is version-controlled, shipped in
    # the image and tested by T6a. This check fails if it comes back as a script,
    # because two implementations of one rule drift apart in silence.
    ss = frappe.get_all("Server Script", fields=["name", "disabled", "script_type"])
    live = [s for s in ss if not s.disabled]
    problems = []
    if frappe.db.exists("Server Script", "MSCAST BRM payment block"):
        problems.append("the retired 'MSCAST BRM payment block' Server Script is back")
    if len(live) < 2:
        problems.append("only %d live server scripts" % len(live))
    hooks = frappe.get_hooks("doc_events") or {}
    for dt in ("Payment Entry", "Journal Entry"):
        wired = [h for h in ((hooks.get(dt) or {}).get("before_submit") or [])
                 if "brm_payment" in h]
        if not wired:
            problems.append("%s before_submit is not wired to the BRM control" % dt)
    rec("T6c", "controls", "controls live in the app, scripts only where intended",
        not problems,
        "%d live scripts; %s" % (len(live),
                                 "; ".join(problems) if problems
                                 else "BRM control wired on Payment Entry + Journal Entry"))

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


    # T6g - the segregation question T6e cannot answer.
    #
    # T6e compares WORKFLOW TRANSITION roles. But creating a document is a
    # permission, not a transition, so a user can hold create rights on a
    # document and the approval role for the same document and never appear in
    # T6e. That is not hypothetical: a director holds Projects Manager, which
    # can create a BRM, and MSCAST Director, which certifies one. T6e sees no
    # overlap because "prepare a BRM" is not a workflow transition at all.
    #
    # This asks the question in the form an auditor would: can one person carry
    # this document from creation to the approval that commits money?
    def can_create(roles, dt):
        rows = (frappe.get_all("Custom DocPerm", filters={"parent": dt},
                               fields=["role", "create"])
                + frappe.get_all("DocPerm", filters={"parent": dt},
                                 fields=["role", "create"]))
        return sorted({r.role for r in rows if r.create and r.role in roles})

    END_TO_END = [("MSCAST BRM", "MSCAST Director", "certify"),
                  ("MSCAST BRM", "Accounts Manager", "mark paid"),
                  ("Purchase Order", "MSCAST Director", "approve"),
                  ("MSCAST PCC", "MSCAST Director", "approve")]
    carries = []
    for dt, appr_role, appr in END_TO_END:
        if not frappe.db.exists("DocType", dt):
            continue
        for u in frappe.get_all("User", filters={"enabled": 1, "user_type": "System User"},
                                fields=["name", "full_name"]):
            rs = set(frappe.get_all("Has Role",
                     filters={"parent": u.name, "parenttype": "User"}, pluck="role"))
            # System Manager holders can do anything; T6f is where they are reported.
            if "System Manager" in rs or appr_role not in rs:
                continue
            if can_create(rs, dt):
                carries.append("%s can create %s and %s it"
                               % (u.full_name or u.name, dt.replace("MSCAST ", ""), appr))
    rec("T6g", "controls", "no one person can create and then approve the same document",
        "warn" if carries else True,
        " :: ".join(carries) if carries
        else "checked %d document/approval pairs" % len(END_TO_END))


    # T6h - the auditor really is read-only.
    #
    # Four documents state that the CA's login cannot change anything. It could:
    # `Auditor` held write and create on GSTR-1 and GST Return Log, and
    # `MSCAST Statutory Auditor` held write, create and DELETE on MSCAST
    # Exception - the ability to erase the output of the overnight sweep. This is
    # the claim an auditor is most likely to test in person.
    #
    # It asks for the EFFECTIVE rights - what Frappe actually applies. Once a
    # doctype has any Custom DocPerm rows, its standard DocPerm rows are ignored,
    # so reading both tables reports rights nobody holds. The first version did,
    # and failed a fresh install whose auditor was correctly read-only.
    AUD = ("Auditor", "MSCAST Statutory Auditor")
    writable = []
    candidates = set()
    for tbl in ("Custom DocPerm", "DocPerm"):
        candidates.update(frappe.get_all(tbl, filters={"role": ["in", AUD]}, pluck="parent"))
    for dt in sorted(candidates):
        if not frappe.db.exists("DocType", dt):
            continue
        for r in frappe.get_meta(dt).permissions:     # effective rows only
            if r.role in AUD and (r.write or r.create or r.delete or r.submit
                                  or r.cancel or r.amend):
                writable.append("%s on %s" % (r.role, dt))
    rec("T6h", "controls", "the auditor login cannot change anything", not writable,
        " :: ".join(sorted(set(writable))[:6]) if writable
        else "both auditor roles are read-only everywhere")

    # T6i - can the people named in the Role Cards do the work described there?
    #
    # `Design User` had zero permission rows in the entire system, so the drawing
    # office could not open a drawing, and the Draft -> For Customer Approval
    # transition was executable by nobody at all. Stores, Quality and the
    # Purchase Executive were in the same position on their own documents. The
    # role cards are handed to staff; they have to be true.
    MUST_CREATE = [
        ("Design User", "MSCAST Drawing"),
        ("Design User", "MSCAST Transmittal"),
        ("Design User", "MSCAST MDF"),
        ("Projects User", "MSCAST PCC"),
        ("Stock User", "MSCAST MDM"),
        ("Stock User", "MSCAST Delivery Instruction"),
        ("Quality Manager", "MSCAST Inspection Plan"),
        ("Purchase User", "MSCAST BRM"),
    ]
    cannot = []
    for role, dt in MUST_CREATE:
        if not frappe.db.exists("DocType", dt) or not frappe.db.exists("Role", role):
            continue
        rows = (frappe.get_all("Custom DocPerm", filters={"parent": dt, "role": role},
                               fields=["create"])
                + frappe.get_all("DocPerm", filters={"parent": dt, "role": role},
                                 fields=["create"]))
        if not any(r.create for r in rows):
            cannot.append("%s cannot create %s" % (role, dt))
    rec("T6i", "controls", "every role can raise the documents its card describes",
        not cannot, " :: ".join(cannot) if cannot
        else "checked %d role/document pairs" % len(MUST_CREATE))

    # T6j - a guarded workflow state is guarded on EVERY route into it.
    #
    # The kick-off checklist condition sat on one transition into PO Verified and
    # not on the other, so raising a query first was a way round the single
    # highest-value control in the system - and a record in the demo data had
    # already gone through that way. This is the general form of that bug: if one
    # route into a state carries a condition, the others must carry it too.
    holes = []
    for w in frappe.get_all("Workflow", pluck="name"):
        doc = frappe.get_doc("Workflow", w)
        by_state = {}
        for t in doc.transitions:
            by_state.setdefault(t.next_state, []).append((t.state, t.action,
                                                          (t.condition or "").strip()))
        for state, routes in by_state.items():
            conds = {c for _, _, c in routes}
            if len(conds) > 1 and any(c for c in conds):
                for frm, action, cond in routes:
                    if not cond:
                        holes.append("%s: %s --%s--> %s has no condition while "
                                     "another route into %s does"
                                     % (doc.document_type, frm, action, state, state))
    rec("T6j", "controls", "a guarded workflow state is guarded on every route in",
        not holes, " :: ".join(holes[:4]) if holes
        else "every guarded state is guarded consistently")

    # T6n - a BRM cannot be certified with its checks unticked. Attempted as the
    # certifying director, through the real workflow action, and rolled back.
    from frappe.model.workflow import apply_workflow
    director = frappe.db.get_value("Has Role", {"role": "MSCAST Director", "parenttype": "User",
                                               "parent": ["!=", "Administrator"]}, "parent")
    sup = frappe.db.get_value("Supplier", {}, "name")
    outcome = "not run"
    if director and sup:
        try:
            b = frappe.get_doc({"doctype": "MSCAST BRM", "supplier": sup, "invoice_type": "Tax Invoice",
                                "supplier_invoice_no": "HARNESS/T6N", "amount": 1000, "status": "Pending"})
            b.flags.ignore_permissions = True; b.flags.ignore_mandatory = True
            b.insert()
            frappe.set_user(director)
            try:
                apply_workflow(frappe.get_doc("MSCAST BRM", b.name), "Certify")
                outcome = "CERTIFIED with no checks ticked"
            except Exception as e:
                outcome = "refused"
        finally:
            frappe.set_user("Administrator")
            frappe.db.rollback()
    if outcome == "not run":
        # A fresh install has no director and no supplier to try it with, so check
        # the rule itself instead: every route into Certified must require all four
        # ticks. (Found 21 Sep 2026: T6n in the fresh-install list failed as "not run".)
        need = ("qty_check", "rate_check", "inspection_check", "delivery_check")
        routes = [(t.state, t.action, t.condition or "")
                  for w in frappe.get_all("Workflow", {"document_type": "MSCAST BRM", "is_active": 1}, pluck="name")
                  for t in frappe.get_doc("Workflow", w).transitions if t.next_state == "Certified"]
        open_ = ["%s --%s-->" % (a, b) for a, b, c in routes if not all(f in c for f in need)]
        outcome = ("refused" if routes and not open_
                   else "rule missing on: " + ", ".join(open_) if routes else "no route into Certified")
        how = "no director or supplier yet - checked the workflow rule on %d route(s): %s" % (len(routes), outcome)
    else:
        how = "certify attempted as %s: %s" % (frappe.db.get_value("User", director, "full_name"), outcome)
    rec("T6n", "controls", "a BRM cannot be certified with its checks unticked", outcome == "refused", how)

    # T6k - whoever can approve a document can open it.
    #
    # T6d checked that the approval ROLE was right; nothing checked that the
    # people holding it could open the document. On 21 Sep 2026 the managing
    # director - named as the kick-off approver - could not open a single
    # kick-off, because a permission change had dropped every standard role from
    # the doctype. Asked per real user, the way the business experiences it.
    frappe.clear_cache()
    locked = []
    users = frappe.get_all("User", filters={"enabled": 1, "user_type": "System User",
                                            "name": ["!=", "Administrator"]}, pluck="name")
    for w in frappe.get_all("Workflow", filters={"is_active": 1},
                            fields=["name", "document_type"]):
        approvers = {t.allowed for t in frappe.get_doc("Workflow", w.name).transitions}
        for u in users:
            if not approvers & set(frappe.get_roles(u)):
                continue
            if not frappe.has_permission(w.document_type, "write", user=u):
                locked.append("%s cannot open %s" % (
                    frappe.db.get_value("User", u, "full_name") or u, w.document_type))
    rec("T6k", "controls", "everyone who can approve a document can open it",
        not locked, " :: ".join(locked[:4]) + (" (+%d more)" % (len(locked) - 4)
                                               if len(locked) > 4 else "")
        if locked else "checked every active workflow against every user")

    # T6l - no role silently loses access.
    #
    # A single Custom DocPerm row replaces ALL of a doctype's standard ones. So a
    # change meant to ADD one role can REMOVE every other - which is what caused
    # T6k's failure. The matrix may narrow a role's rights; it never removes a
    # role outright, so any standard role missing from a customised doctype is a
    # bug of exactly that kind.
    dropped = []
    for dt in sorted(set(frappe.get_all("Custom DocPerm", pluck="parent"))):
        std = set(frappe.get_all("DocPerm", filters={"parent": dt}, pluck="role"))
        cus = set(frappe.get_all("Custom DocPerm", filters={"parent": dt}, pluck="role"))
        gone = std - cus
        if gone:
            dropped.append("%s lost %s" % (dt, ", ".join(sorted(gone))))
    rec("T6l", "controls", "no role silently lost access to a customised doctype",
        not dropped, " :: ".join(dropped[:3]) if dropped
        else "%d customised doctypes, every standard role still present"
             % len(set(frappe.get_all("Custom DocPerm", pluck="parent"))))

    # T6m - the app ships all of MSCAST's configuration, and none of anyone else's.
    #
    # Fixtures overwrite live rows on every migrate, and mscast_erp migrates last.
    # Until 21 Sep 2026 the app shipped 663 custom fields, 344 property setters
    # and 7 email templates belonging to India Compliance, ERPNext and HRMS - so
    # their next release would have been silently reverted by ours. One already
    # had been overtaken. Ownership is the module field (MSCAST) or the name.
    import json as _json, os as _os
    fx = frappe.get_app_path("mscast_erp", "fixtures")
    def _load(f):
        p = _os.path.join(fx, f)
        return _json.load(open(p)) if _os.path.isfile(p) else []
    foreign = []
    for f in ("custom_field.json", "property_setter.json"):
        foreign += ["%s (%s)" % (r["name"], r.get("module")) for r in _load(f)
                    if r.get("module") != "MSCAST"]
    for f in ("email_template.json", "notification.json"):
        foreign += [r["name"] for r in _load(f) if not r["name"].startswith("MSCAST")]
    shipped = {r["name"] for f in ("custom_field.json", "property_setter.json") for r in _load(f)}
    unshipped = [n for dt in ("Custom Field", "Property Setter")
                 for n in frappe.get_all(dt, filters={"module": "MSCAST"}, pluck="name")
                 if n not in shipped]
    # ... and every document the app defines is owned by the app on this site. A
    # database-defined copy of the same name is never replaced by the app's, so
    # changes in the package silently stop reaching the site (MSCAST Exception,
    # found 21 Sep 2026).
    dt_dir = frappe.get_app_path("mscast_erp", "mscast", "doctype")
    for folder in sorted(_os.listdir(dt_dir)):
        jp = _os.path.join(dt_dir, folder, folder + ".json")
        if not _os.path.isfile(jp):
            continue
        dname = _json.load(open(jp)).get("name")
        row = frappe.db.get_value("DocType", dname, ["module", "custom"], as_dict=True)
        if row and (row.module != "MSCAST" or row.custom):
            foreign.append("%s is a database copy (module %s), not the app's" % (dname, row.module))
    rec("T6m", "controls", "the app ships all of MSCAST's configuration and none of anyone else's",
        not (foreign or unshipped),
        ("foreign: " + ", ".join(foreign[:3]) + " " if foreign else "")
        + ("not in the package: " + ", ".join(unshipped[:3]) if unshipped else "")
        if (foreign or unshipped) else "%d custom fields and property setters, all MSCAST's" % len(shipped))


# ---------------------------------------------------------------- T7 data
def t7_data():
    # Both checks here selected doctypes with custom = 1. When the MSCAST
    # documents moved into the app they became app doctypes (custom = 0), so
    # from then on both examined NOTHING and passed - T7a even passed on an empty
    # site. They now select by module, and a check that finds nothing to examine
    # fails rather than passing: "0 problems in 0 things" is not a result.
    ours = frappe.get_all("DocType", filters={"module": "MSCAST"}, fields=["name", "istable"])
    if not ours:
        rec("T7a", "data", "every MSCAST form has demo records", False,
            "no MSCAST doctypes found - the check has nothing to examine")
        rec("T7b", "data", "stored Select values are all valid options", False,
            "no MSCAST doctypes found - the check has nothing to examine")
        return

    forms = [d.name for d in ours if not d.istable]
    empty = [d for d in forms if not frappe.db.count(d)]
    rec("T7a", "data", "every MSCAST form has demo records", not empty,
        ("empty: %s" % ", ".join(empty[:6]) + (" (+%d more)" % (len(empty) - 6) if len(empty) > 6 else ""))
        if empty else "%d forms, all with records" % len(forms))

    bad, fields_checked = [], 0
    for d in [x.name for x in ours]:
        meta = frappe.get_meta(d)
        for fl in meta.fields:
            if fl.fieldtype != "Select" or not fl.options or not fl.fieldname:
                continue
            opts = [x.strip() for x in fl.options.split("\n") if x.strip()]
            if not opts:
                continue
            fields_checked += 1
            try:
                rows = frappe.db.sql("select distinct `%s` from `tab%s` where ifnull(`%s`,'') != ''"
                                     % (fl.fieldname, d, fl.fieldname))
            except Exception:
                continue
            for (v,) in rows:
                if v not in opts:
                    bad.append("%s.%s = '%s' not in options" % (d, fl.fieldname, v))
    rec("T7b", "data", "stored Select values are all valid options", not bad and fields_checked > 0,
        "%d Select fields on %d doctypes, %d violations%s" % (
            fields_checked, len(ours), len(bad), (" :: " + "; ".join(bad[:6])) if bad else ""))

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
    # made-up domain such as @mscast.demo. It used to allow-list the providers
    # we happened to use, so MSCAST's own domain (mcast.co.in) failed on the
    # day they created real users (21 Sep 2026) - mail to it was delivered and
    # read. It now refuses only domains that cannot receive mail.
    FAKE_EXACT = ("example.com", "example.org", "example.net", "localhost")
    FAKE_SUFFIX = (".demo", ".local", ".test", ".invalid", ".example", ".localhost")
    bad_users = []
    for u, email in frappe.db.sql("""select name, email from `tabUser` where enabled = 1
            and unsubscribed = 0 and name not in ('Guest','Administrator')"""):
        dom = ((email or u).rsplit("@", 1)[-1] if "@" in (email or u) else "").lower()
        if not dom or dom in FAKE_EXACT or dom.endswith(FAKE_SUFFIX):
            bad_users.append(email or u)
    bounce = len(bad_users)
    rec("T9e", "email", "no live user on a non-deliverable domain", bounce == 0,
        ("%d users would bounce: %s" % (bounce, ", ".join(bad_users[:5]))) if bounce
        else "every enabled user is on a real mail domain")


    # T9f - do the MSCAST scheduled jobs actually RUN?
    #
    # This check exists because four of them never had. The scheduler and the two
    # queue containers are built from the image, and mscast_erp was never in the
    # image - it had been copied into the backend container by hand. So the
    # backend could import it and nothing else could. Every script, every bench
    # execute and every demonstration ran in the backend and worked perfectly;
    # the 06:00 exception sweep and the 08:35 briefing were never once executed
    # by the scheduler, and last_execution sat at NULL for the life of the POC.
    #
    # Nothing reported it, because every other check asks "is this configured?"
    # and none asked "has it ever run?".
    stale, never = [], []
    for j in frappe.get_all("Scheduled Job Type",
                            fields=["name", "method", "stopped", "last_execution"]):
        if "mscast" not in (j.method or "").lower() or j.stopped:
            continue
        if not j.last_execution:
            never.append(j.method)
        else:
            age = frappe.utils.time_diff_in_hours(frappe.utils.now(), j.last_execution)
            # Monthly jobs get a long leash; the daily ones should be recent.
            limit = 24 * 40 if "monthly" in (j.method or "").lower() else 48
            if age > limit:
                stale.append("%s (%.0fh ago)" % (j.method, age))
    detail = []
    if never:
        detail.append("NEVER RUN: " + ", ".join(never))
    if stale:
        detail.append("stale: " + ", ".join(stale))
    rec("T9f", "email", "enabled MSCAST scheduled jobs have actually run", not (never or stale),
        " :: ".join(detail) if detail
        else "all enabled MSCAST jobs have a recent last_execution")


# ---------------------------------------------------------------- T10 hr
def t9g_secrets():
    # T9g - every stored secret can actually be decrypted.
    #
    # T9a asked whether the mail password was SET. After a restore on 21 Sep 2026
    # it was set, and unreadable: the database came back but the site kept a
    # different encryption_key, so the password could not be decrypted and the
    # digest failed. "Present" and "usable" are different claims; this checks the
    # second one, for every encrypted value on the site.
    from frappe.utils.password import get_decrypted_password
    bad, n = [], 0
    for r in frappe.db.sql("select doctype, name, fieldname from `__Auth` where encrypted = 1",
                           as_dict=True):
        n += 1
        try:
            get_decrypted_password(r.doctype, r.name, r.fieldname, raise_exception=True)
        except Exception:
            bad.append("%s %s.%s" % (r.doctype, r.name, r.fieldname))
    rec("T9g", "automation", "every stored secret decrypts with this site's key", not bad,
        ("cannot decrypt: " + "; ".join(bad) + " - restore the backup's encryption_key")
        if bad else "%d secret(s), all readable" % n)


def t9h_safety_net():
    # T9h - the nightly safety net ran recently, and its backup succeeded.
    # Recorded in site config by nightly.sh; the in-site watchdog reads the same.
    import time
    last = frappe.conf.get("mscast_last_backup") or {}
    if frappe.conf.get("mscast_dev_copy"):
        # The DEV copy is not backed up by design - it is rebuilt from its seed
        # (dev-create.sh). Said out loud in the result rather than silently passed.
        rec("T9h", "automation", "nightly backup ran in the last 26 hours and succeeded", True,
            "not applicable - DEV copy (mscast_dev_copy), rebuilt from its seed, never backed up")
        return
    if not last.get("at"):
        rec("T9h", "automation", "nightly backup ran in the last 26 hours and succeeded", False,
            "no nightly backup has ever been recorded on this site")
        return
    age = (time.time() - float(last["at"])) / 3600
    ok = age <= 26 and last.get("ok") is not False
    rec("T9h", "automation", "nightly backup ran in the last 26 hours and succeeded", ok,
        "set %s, %.1fh ago, %s" % (last.get("set"), age, "ok" if last.get("ok") else "FAILED: %s" % last.get("detail")))


def t9i_links():
    # T9i - links the system writes into emails point somewhere a person can reach.
    # With no host_name set, every link is built as http://frontend - the
    # container's internal name - so "open this document" in any alert or
    # notification led nowhere. Found 21 Sep 2026 chasing a console error in the
    # demo screenshot run.
    url = frappe.utils.get_url()
    internal = any(h in url for h in ("//frontend", "//localhost", "//127.0.0.1", "//backend"))
    rec("T9i", "automation", "emailed links use a public address, not the container's name",
        not internal, "links are built as %s%s" % (url, " - set host_name in site config" if internal else ""))


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
    for fn in (t1_literals, t1b_script_literals, t1c_server_scripts_on, t2_execute, t2b_reports_as_users, t3_dates, t4_prints, t4b_watermark, t5_ledger, t6_controls,
               t7_data, t8_gst, t9_automation, t9g_secrets, t9h_safety_net, t9i_links, t10_hr):
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
