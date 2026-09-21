---
title: "MSCAST ERP — Independent Review and Verification"
---

# MSCAST ERP — Independent Review and Verification

**Version 2.0 · 21 September 2026**

**Purpose:** every finding from the two independent reviews (one across all delivered work, one against the ERPens proposal) and from the follow-up tests, with its current status and who must act. Each finding was re-tested against the running system, not re-read from documents.

- Build checks referenced below (`T…`) are listed in full in the POC README (POC README). Current result: 42 checks; DEV 40 PASS, 2 WARN (T6e, T6g: waiting on Q20/Q21), 0 FAIL. Live POC: 38 PASS, 3 WARN, 1 FAIL (T10c: demo biometric punches deleted by MSCAST's trial admin; T6f warns because Aiqaz holds System Manager). Live is left in that state.
- Confirmed correct by the reviewers: platform choice and alternatives assessment; Setup Guide dependency order and go-live checklist; legal facts (audit-trail rule from 1 Apr 2023, Rule 3(5) India backups, ₹5 Cr e-invoice threshold, ₹250 Cr Ind AS threshold, SMC definition, 25.168% arithmetic, s.194C thresholds).
- The engagement is unpaid: the implementer builds this for MSCAST as a family friend and is not competing with ERPens.

# Status of every finding

| ID | Finding (one line) | Status | Evidence or fix | Who acts |
|-------------|------------------------------|----------|-------------------------------------|----------|
| A1 | Public Administrator login accepted the default password; `allow_consecutive_login_attempts = 10` and `session_expiry = 170:00` (7 days) are loose for a public site | Parked by owner | `admin`, `Administrator`, `admin123` rejected since 20 Sep. The replacement password was typed into a chat transcript and must be rotated again; rotation (and tighter session/login settings) is mandatory before real data or a server | Owner |
| A2 | Real GSTIN (27AAGCM8444B1ZI) and real directors with invented shareholdings on the public demo | Closed | Shareholders are `Promoter A / B / C`. The GSTIN stays real on the demo; every print carries a DEMONSTRATION watermark (app code, site setting `mscast_demo`; never set in production). Check `T4b` | — |
| A3 | Demo story contradictory: machine commissioned but never dispatched; `DN-26-00001` has no project | Withdrawn | Not a defect: `DN-26-00002` ships the caster (`CCM-2S-130 x1`) to PROJ-0001 before `COMM-2026-00001`; `DN-26-00001` is a spares sale to Konark Alloys, which has no project | — |
| A4 | Draft dunning (₹4,80,000) contradicted "nothing overdue" | Closed | No Dunning records exist; no invoice is past due | — |
| A5 | Retention posted against the wrong party (Konark Alloys) | Closed | `ACC-JV-2026-00007` reversed by `ACC-JV-2026-00020`; retention now `ACC-JV-2026-00021`, ₹4,52,530 against Ambika Steel Rolling Mills (10% of `SINV-26-00005`, ₹45,25,300; `SAL-ORD-2026-00003` has `retention_percent = 10`). Ledger and *Retention and Certificates* report agree. Rule: doc 11, A2 | — |
| A6 | Report counts inconsistent across documents (15, 25, 26) | Closed | 28 custom reports; every document says 28, asserted by the census script | — |
| B1 | BRM payment block narrower than the SOPs claim (Journal Entry, advance with no invoice, over-payment, utilities) | Closed | Control is `mscast_erp/controls/brm_payment.py` on `before_submit` of Payment Entry and Journal Entry; old Server Script deleted. Blocks: no certified BRM, advance with no invoice reference, amount above certificate, BRM already *Paid*. Supplier flag *Exempt from BRM certification* for utilities/rent/statutory (0 of 15 suppliers ticked on 21 Sep). Checks `T6a` (six routes, each asserting which rule blocked), `T6c` | MSCAST: list exempt suppliers |
| B1-PO | PO separation ("one person cannot do both") never tested | Closed | Tested: sending a PO needs `Purchase User`, approving needs `MSCAST Director`; nobody holds both | — |
| B1-BRM | A director can create, certify and mark paid the same BRM alone (holds `Projects Manager`, `MSCAST Director`, `Accounts Manager`) | Waiting on MSCAST | Check `T6g` warns on every build; question **Q21** (doc 03). The payment block still applies to directors | MSCAST (Q21) |
| B1-PCC | A director can prepare a PCC or verify a customer PO and then approve it alone | Waiting on MSCAST | Check `T6e` warns; question **Q20** (doc 03) | MSCAST (Q20) |
| B2 | "MSCAST Director is read-only, so every approval is broken" | Withdrawn | Premise wrong: `MSCAST Director` is the approving role; the read-only role is `Auditor` (the CA). The documents had mis-described it and were corrected | — |
| B3 | MSME 45-day clock may start from the wrong date (MSMED s.15 acceptance/deemed acceptance; 15 days without written agreement; s.43B(h) micro and small only; s.16 interest disclosed under s.22) | Waiting on CA | Untested; needs MSCAST's supplier terms and the CA's position | CA |
| B4 | Free issue to fabricators is a stock transfer, not a Subcontracting Order with job-work challan (no ITC-04 data, one-year return rule untracked) | Waiting on CA | Untested; needs MSCAST's practice and the CA's position | CA |
| B5 | Project WIP method (billing ÷ contract value) is neither AS 7 nor AS 9 + AS 2; ₹450/hr engineering rate and 12% works overhead must be cost rates under AS 2 | Waiting on CA | Untested | CA |
| B6 | Tax and payroll provisions may assume statutes MSCAST is not under | Waiting on CA | PF is not deducted: removed from payroll on MSCAST's instruction (under 20 staff, no UANs); ESI and the gratuity provision are kept. Open for the CA: confirm there is no continuing EPF coverage under s.1(5), s.115BAA election (Form 10-IC, irrevocable), "Lease Liabilities" head (Ind AS 116; under AS 19 an operating lease is off balance sheet) | CA |
| B7 | Customer-deducted TDS (2% under s.194C) has no TDS-receivable treatment or 26AS reconciliation | Waiting on CA | Untested; needs confirmation that customers deduct | CA |
| B8 | −₹24.7 L "stock adjustment" in the P&L | Closed | ₹24,74,400 reposted from `5119 Stock Adjustment` to `1910 Temporary Opening`. Tax provision recomputed: ₹15,32,737 on PBT ₹60,90,022 (25.168%). Trial balance nets to zero | — |
| B9 | Two sales invoice series in one company | Closed | `ACC-SINV-2026-00001` renamed `SINV-26-00006`; GL followed | — |
| B10 | TDS on `PINV-26-00003` does not reconcile | Withdrawn | Reviewer's arithmetic wrong: ₹5,16,000 net + 18% GST = ₹6,08,880, less ₹10,320 TDS (2.0000% of net, s.194C, computed excluding GST per CBDT Circular 23/2017) = ₹5,98,560 | — |
| C1 | Built without MSCAST: every MSCAST form is an inference from the requirement PDF; PCC built as pre-quote whereas S-02 says prepared by Sales from the Sales Order | Waiting on MSCAST | Q2 (PCC), Q3 (Project MIS), Q4 (BRM), Q5 (MDM, DI, Annexure-I) in doc 03; requested in doc 10. Present the POC as "our reading of your requirements — correct us" (doc 12), not "97 of 97 implemented" | MSCAST |
| C2 | Delivery measured against the declined ERPens proposal; no signed scope or fee | Withdrawn | Unpaid work for a family friend, not competing with ERPens; no fee, invoice, milestone or acceptance criterion exists. Code ownership settled: `github.com/cb1-tech/mscast` (owner-held). The expectation risk is kept under C1 | — |
| C3 | Operating model needs more people than MSCAST has (Director approves PCC, quotation, kick-off, claims, closure, payroll, payments; under 10 staff) | Open | Risk: shared logins destroy the audit trail. Also: timesheets feed WIP and MIS and decay silently; drawing register duplicates CAD/Drive; retention is a manual JV per invoice; free-issue consumption is manual; several scheduled mails a day | MSCAST (Q20/Q21, owners of monthly jobs) |
| C4 | No path from POC to production | Closed | Installable app `mscast_erp`, repo `github.com/cb1-tech/mscast` (tag `v0.9.0`), fixtures exported; `new-mscast-site.sh` builds a fresh site (six apps, no demo data) and must pass 19 system checks. Exact system with data: restore a backup (tested; all checks passed; under 3 minutes). Known limitation: `reset-poc.sh` seed scripts do not rebuild the demo data from empty and will not be repaired | — |
| C5 (commercial) | Commercial half: no support agreement | Withdrawn | No commercial relationship to formalise | — |
| C5 (delivery) | Delivery half: MSCAST depends on one person, on personal infrastructure (implementer's PC in Japan, `carobar.net` domain, `uattech@carobar.net` mail, tunnel) | Open | Mitigations in place: app, fixtures, 42 build checks, fresh-install and restore paths, documentation. Remaining: MSCAST names who runs the monthly and annual jobs; VPS move parked by owner | MSCAST; Owner (VPS) |
| C6 | Accounting layer ahead of the CA: WIP/revenue policy, MSME clock, tax regime, PF/ESI/gratuity, works-contract GST, retention posting | Waiting on CA | See B3–B7. If the CA is not engaged first, accounts stay in Tally | CA; MSCAST (CA contact) |
| F1 | Kick-off could be approved with the PO checklist incomplete (condition on one route only; `KICK-2026-00002` had passed) | Closed | Every route into a guarded state carries the condition; check `T6j`. Fix is in the app's workflow fixture (fixtures re-import on every migrate) | — |
| F2 | Four roles could not do their job (`Design User` had no permission rows; Stores, Quality, Purchase Executive likewise) | Closed | Permissions match the Role Cards (doc 09); check `T6i` | — |
| F3 | Auditor roles could write (`Auditor` on two GST documents; `MSCAST Statutory Auditor` could delete MSCAST Exception records) | Closed | Read-only everywhere; check `T6h` | — |
| F4 | Permissions matrix: one custom permission row replaced all standard rows; on five doctypes named approvers (Mustaque, Aiqaz, Anita, directors on Transmittal) could not open what they approve | Closed | Matrix written as a whole set by `mscast_erp.controls.permissions` on every install and migrate; approvers named in workflows can open, edit and submit what they approve. Checks `T6k` (per real user), `T6l` (no role silently dropped) | — |
| F5 | Fixtures captured other apps' configuration (663 of 702 custom fields, 344 of 382 property setters, 7 of 10 email templates), which would overwrite their releases on migrate | Closed | Fixtures carry only MSCAST's records (39 / 38 / 3); new customisations must carry module **MSCAST**. Check `T6m` | — |
| F6 | DEMONSTRATION watermark lost on `bench migrate` (was a setup script) | Closed | Watermark is app code; check `T4b` (both directions) | — |
| F7 | Fresh install lacked live configuration: `Design User` role, "drawing awaiting customer approval" notification, directors' and statutory auditor's access to the books | Closed | Packaged; oversight rights declared in `mscast_erp/controls/oversight.json`; `completeness-test.sh` compares a fresh install with live | — |
| F8 | Encryption key: a restore kept the target site's key, so stored secrets (mail password) could not be decrypted | Closed | Both restore scripts restore the key (`restore-key.sh`); check `T9g` (every secret decrypts); nightly backup refuses a set whose secrets do not decrypt. One set from the mismatch is quarantined | — |
| F9 | `server_script_enabled` is bench-wide and not carried by a restore (all MSCAST server scripts were off on the first DEV build) | Closed | Set by `dev-create.sh`; check `T1c`. `restore-key.sh` no longer aborts on JSON `true` | — |
| F10 | Links in emails pointed at `http://frontend` | Closed | `host_name` set; check `T9i` | — |
| F11 | Eight demo customers lacked the "(DEMO)" suffix | Closed | Renamed; ledgers and documents followed | — |
| F12 | Theme stylesheet returned 404 | Closed | `deploy-app.sh` recreates the web container and fails unless the stylesheet is served | — |
| F13 | Drawing-register access: Meera could not open the Drawing Register | Closed | Report-role rule now only adds roles, never removes them | — |
| F14 | Report names containing `/` gave a server error from the desk | Closed | Renamed; check `T2b` runs each report as the users who need it | — |
| F15 | Six reports failed from the desk: literal `%` in SQL | Closed | Escaped; check `T2` runs reports the way the desk does | — |
| F16 | Home-page literals: pending-BRM and open-claim counts compared against non-existent status names | Closed | Fixed; check `T1b` checks server-script literals | — |
| F17 | BRM four-checks guard: a BRM could be Certified with none of qty, rate, inspection, delivery ticked | Closed | Guarded; check `T6n` | — |
| F18 | Prints showed login emails instead of names for prepared/approved/certified by | Closed | Prints show full names | — |

# Open items

- **MSCAST:** real formats (PCC, Project MIS, BRM, MDM with DI and Annexure-I) — C1; answers to Q20 and Q21; list of BRM-exempt suppliers; owners of the monthly and annual jobs (C3, C5); Tally export; CA name and contact. Requested in doc 10.
- **CA:** B3, B4, B5, B7; EPF: confirm no continuing coverage under s.1(5) (B6); the s.115BAA election; the Ind AS 116 "Lease Liabilities" head; works-contract GST and retention posting (C6).
- **Parked by owner:** Administrator password rotation and tighter session/login settings (A1, until real data or a server); VPS move (C5); tunnel fix for live screen refresh (socket.io).
- **Before go-live:** migration plan, training material, named support contact at MSCAST (C5).

# Lessons that are now rules

- Test a finding against the running system (attempt the action, as the real user) before accepting or rejecting it; a review is a set of hypotheses.
- Every fixed finding becomes a build check, and a new check must be seen to fail before the fix.
- All configuration lives in the `mscast_erp` app; nothing is set only in the database. `bench migrate` re-imports fixtures; `completeness-test.sh` shows anything live has that a fresh install lacks.
- A restore does not carry settings outside the database: `encryption_key` (`restore-key.sh`), `server_script_enabled` (bench-wide), `host_name`.
- One custom permission row replaces all of a doctype's standard rows; permissions are written only as a whole set by `mscast_erp.controls.permissions`.
