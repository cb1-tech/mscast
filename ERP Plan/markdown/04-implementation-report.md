---
title: "MSCAST ERP — Implementation Report"
---

# MSCAST ERP - implementation report

**Version 2.0 · 21 September 2026** · executive summary of what exists today and where it is.

## Headline

- **All 97 requirements** in MSCAST's requirement document are implemented. Evidence per requirement: doc 03 (Requirements Traceability), 'Full matrix'.
- **42 automated build checks.** DEV: 40 pass, 2 warn, 0 fail. Live POC: 38 pass, 3 warn, 1 fail (left as is). Full list: POC README, section 'Build checks'.
- **Six requirements rest on assumptions** that MSCAST or the CA must confirm: doc 03, 'Assumptions carried'. Each assumption is also written into the narration of the affected vouchers in the system.

## Where things are

| | |
|---------------------------------|-------------------------------------------------------------------|
| Live POC | https://mscast.carobar.net. MSCAST staff are trying it with their own logins. Nobody changes it without the owner's say-so |
| DEV | https://mscastdev.carobar.net. Separate copy (own database, same image) with the full demo cast; used for demos, screenshots and development. Orange "DEV INSTANCE" banner |
| Repository | `github.com/cb1-tech/mscast` (held by the owner), release `v0.9.0` |
| Installable app | `mscast_erp` in that repository: every MSCAST doctype, report, print format, workflow and control |
| Image | `mscast/erpnext:v16-app`, ERPNext/Frappe v16 |
| Build checks | `seed/102_test_harness.py`; how to run it: POC README |
| Fresh install | `new-mscast-site.sh`; must pass 19 system checks |
| Documents | In the ERP-MSCAST project and in `ERP Plan\` (`For MSCAST\` and `Internal\`; see `ERP Plan\README.md`) |

## What was built

### Accounting and statutory

| Item | What exists |
|------------------|----------------------------------------------------------------------------------|
| **Schedule III balance sheet** | Statutory vertical format with note references; trade payables split MSME/other; advances shown gross. **Balances to the rupee** (₹1,79,02,695 both sides on the DEV data), nothing unclassified. Totals come from the ledger; presentation lines carry an explicit *unclassified* reconciling line so nothing can hide |
| **Schedule III P&L** | Revenue, changes in inventories and WIP, employee benefits, finance costs, depreciation, other expenses, current and deferred tax, EPS. Profit **ties exactly** to the ledger surplus. Expense filters are constrained by `root_type`. Opening stock is posted to `1910 Temporary Opening` (₹24,74,400), not to an expense account |
| **2021 amendment disclosures** | Trade receivable ageing, trade payable ageing split MSME/others, and the **eleven prescribed ratios**; immaterial denominators show `n/a`. Receivables are party-wise gross: debit-balance parties are receivables, credit-balance parties are advances |
| **Notes to accounts** | 25 notes: MSMED s.22 disclosure (note 6), related party (AS 18), contingent liabilities from the live bank guarantees, CWIP ageing, EPS basis, audit-trail note, and the Schedule III negative disclosures (no benami, no struck-off dealings, no crypto, CSR not applicable) |
| **Tax provisions** | Current tax ₹15,32,737 at 25.168% (s.115BAA) on profit before tax of ₹60,90,022; deferred tax: DTA on the gratuity provision (s.43B, allowed on payment) against DTL on the depreciation timing difference |
| **Project WIP valuation** | ₹26,70,766 carried; report shows the build-up: bought-out billed + material issued + engineering hours at ₹450/hr + 12% works overhead, less the cost of the billed portion |
| **GST on closing inventory** | Stock by warehouse with HSN, value, embedded ITC and the treatment note; stock at the job worker (ITC-04, one-year return rule) shown apart from stock on own premises |
| **Share capital** | ₹1,00,000 posted by opening entry and shown on the balance sheet. Shareholders held as unnamed Promoter A/B/C |
| **Fixed assets** | PPE opening entry ₹8,45,000, excluding the test bench, whose cost is in CWIP. Plant-and-machinery head exists; ₹6,05,000 reclassified to it from Software; asset categories point to it |
| **Bank guarantees** | Expiry dates set; the ABG expires 29 October 2026, so its 30-day expiry alert fires on 29 September 2026 |

### Operations

- **Billing and dispatch schedule** on the Project: 9 milestones across two projects with planned dispatch date, billing %, value, status and an action note for Procurement, plus a report.
- **Payment receipt print** with amount in words and the allocation table.
- **Finance scaling report:** order book and pipeline against scheduled collections, committed outflows, cash and the ₹2.5 Cr HDFC limit, with the projected 90-day headroom.
- **Biometric attendance:** a shift with auto-attendance; 72 punches from device `MSCAST-DOOR-01` converted into Attendance, with an audit report reconciling punches to attendance (on DEV; deleted on the Live POC). The scheduled pull is off; attendance is entered by hand until it is enabled and proven.

### Controls

- **Five workflows:** PCC approval, purchase order approval, BRM certification, project kick-off, drawing release.
- **Approval authority:** a director approves PCCs, purchase orders and kick-offs, and certifies BRMs. A `Purchase User` sends a PO for approval; nobody holds both roles, so every PO passes through two people.
- **Kick-off** cannot be approved while the PO checklist is incomplete. A **drawing** cannot be released for manufacture unless the customer approved it; only a Projects Manager releases.
- **BRM payment block:** no certified BRM, no supplier payment, on Payment Entry and Journal Entry, for everyone. It sits in application code (`mscast_erp.controls.brm_payment`) and reads the same `status` field the BRM workflow drives. Per-supplier *Exempt from BRM certification* flag for utilities, rent and statutory bills. A BRM cannot be certified unless its four checks (qty, rate, inspection, delivery) are ticked.
- **Known limitation:** a director can create a BRM, certify it and mark it paid, alone (build check T6g). MSCAST decides: Q21 in doc 03.
- **Users:** DEV has 13 staff logins (12 named people plus the site administrator) with a documented approval matrix (doc 09, Role Cards). The site administrator holds `System Manager` only; a fresh install recreates the setup-wizard administrator with many roles, so cut it back at go-live (doc 08).
- **Google Chat webhooks** for transactions above ₹5 L: configured, disabled until MSCAST gives the space URL.

### Automation

- **Overnight exception sweep** at 06:00 IST: 16 rules.
- **Morning mails:** 08:30 IST daily summary, dispatch schedule and project MIS (to autoelectron.jp@gmail.com); 08:35 IST AI briefing (to waseemraj@mcast.co.in on the Live POC, by the owner's decision). The briefing runs through a local model router on the build laptop, so the POC needs no Google Cloud project (decision D5); a server needs a hosted endpoint (a configuration change, not a build).
- **Nightly job:** Windows task "MSCAST nightly backup" at 02:30 JST runs the backup and all build checks and emails autoelectron.jp@gmail.com on failure. A watchdog at 09:00 IST emails if the nightly job has not run in 26 hours. Backup alerts are off on DEV.

## Rules that follow from how the system is built

- **Deploy only from a tagged release**, never a copied folder, and read the post-deploy verification output. Installing or upgrading the app overwrites configuration from the package (doc 08, Production Cutover Runbook).
- **Three settings are outside the database** and a restore does not carry them: `encryption_key` (`restore-key.sh` puts it back), `server_script_enabled` (bench-wide), `host_name`.

## Still outstanding

Nothing on the requirement list. The gap between the POC and production (Tally migration, hosting, open questions for MSCAST and the CA, parked items): doc 03, 'What still stands between this and production'.

## Suggested first fifteen minutes

1. Open **MSCAST Balance Sheet (Schedule III)** and confirm it balances.
2. Open **MSCAST Notes to Accounts**; note 6 is the MSMED disclosure the auditor will ask for first.
3. Open **MSCAST Schedule III - Ratios** and see which show `n/a` and why.
4. Open a **Purchase Order** and see the approval workflow bar.
5. Try to pay an uncertified supplier bill; the BRM block refuses it.
6. Open a **Drawing** in *Draft* and try to release it for manufacture; the system does not offer it.
7. Run the build checks: 42 checks, **40 pass, 2 expected warnings, 0 failures** on DEV. Read what the two warnings say (T6e, T6g; Q20, Q21 in doc 03).

The full demo route: doc 12 (Demo Run-sheet).
