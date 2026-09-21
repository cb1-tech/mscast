---
title: "MSCAST ERP — Overnight Implementation Report"
---

# MSCAST ERP - overnight implementation report

**19 September 2026** · POC on ERPNext v16 · site `frontend`

---

> ## Read this first — what has changed since 19 September
>
> **This is a dated record of one night's work, kept as written.** Its findings and defect list are history and are not edited. But several of its statements about the system are no longer true, and anyone reading it for the *current* state should use these numbers instead:
>
> | This report says | As at 20 September, evening |
> |---|---|
> | Four active workflows | **Five** — a drawing release workflow was added, so a drawing cannot reach *Released for Manufacture* without customer approval |
> | 23 automated checks | **27** — four control checks were added, each because something got past the one before |
> | Five department users | **13 staff logins** (12 named people plus the site administrator), rebuilt with a real approval matrix |
> | BRM certified by the Purchase Manager | Certified by a **director**. But see the row below — that does not make it three separate people |
> | — | **A director can create a BRM, certify it and mark it paid, alone.** Both directors hold `Projects Manager` (which can create one), `MSCAST Director` (which certifies) and `Accounts Manager` (which marks it paid). Found on 20 September by a new check, `T6g`; three documents had claimed the opposite. The payment block itself is unaffected — no certified BRM, no payment, for anyone |
> | PO approved by the Purchase Manager | Approved by a **director**, and sent for approval by `Purchase User`. Nobody holds both, so purchase orders genuinely do take two people |
> | Biometric attendance "converted automatically" | The device pull is **switched off**. Attendance is entered until it is enabled and proven |
> | Nothing about deployment | Installing or upgrading the app **overwrites configuration from the package**. See the cutover runbook, section 5a — this is the most important thing learned since |
> | Gemini automation "needs a Google Cloud project" | The agent is **built and running**: a 16-rule sweep at 06:00 and an AI-written morning note at 08:35, via a local router. No cloud project needed for the POC |
> | The demo administrator holds fourteen roles | It held **41**, not fourteen, and now holds `System Manager` and nothing else. A second account — ordinary staff — was also found holding `System Manager` and has had it removed |
>
> Current authoritative documents: *Client Setup Guide v2.2*, *SOPs and Use Cases v2.1*, *Role Cards v1.2*, *Production Cutover Runbook*, *Requirements Traceability v1.7*. Current release: **`v0.9.0`**.

---

## Headline

**All 97 requirements from MSCAST's requirement document are now implemented.** Coverage went
53 → 86 → **97** across v1.3, v1.4 and v1.5 of the traceability matrix.

**23 of 23 automated checks pass.** That harness is new and is the more important half of the
night's work — see *How this was verified* below.

Six requirements rest on assumptions, because MSCAST and the CA haven't answered. Every one of them
is stated in the matrix, and also written into the narration of the voucher inside the system, so
whoever reviews the books sees the assumption at the point it matters rather than in a document.

---

## What was built

### Accounting and statutory (the largest block)

| Item | What exists now |
|---|---|
| **Schedule III balance sheet** | Statutory vertical format, note references, MSME/other split of trade payables, advances shown gross rather than netted. **Balances to the rupee** (₹1,58,71,795 both sides), nothing unclassified |
| **Schedule III P&L** | Revenue, changes in inventories and WIP, employee benefits, finance costs, depreciation, other expenses, current and deferred tax, EPS. Profit **ties exactly** to the ledger surplus |
| **2021 amendment disclosures** | Trade receivable ageing, trade payable ageing split MSME/others, and the **eleven prescribed ratios** — guarded so that immaterial denominators show `n/a` instead of a meaningless "ROE 100%" |
| **Notes to accounts** | 25 notes: MSMED s.22 disclosure, related party (AS 18), contingent liabilities pulled from the live bank guarantees, CWIP ageing, EPS basis, audit-trail note, and the Schedule III negative disclosures (no benami, no struck-off dealings, no crypto, CSR not applicable) |
| **Tax provisions** | Current tax ₹5,23,156 at 25.168% (s.115BAA) and deferred tax — DTA on the gratuity provision (s.43B, allowed on payment) against DTL on the depreciation timing difference |
| **Project WIP valuation** | ₹26,70,766 carried, with a report showing the build-up: bought-out billed + material issued + engineering hours at ₹450/hr + 12% works overhead, less the cost of the billed portion |
| **GST on closing inventory** | Stock by warehouse with HSN, value, embedded ITC, and the treatment note — separating stock at the job worker (ITC-04, one-year return rule) from stock on own premises |

### Operations

- **Billing and dispatch schedule** on the Project — 9 milestones across the two projects with planned dispatch date, billing %, value, status and an action note for procurement, plus a report they can work from
- **Payment receipt print** with amount in words and the allocation table
- **Finance scaling report** — order book and pipeline against scheduled collections, committed outflows, cash and the ₹2.5 Cr HDFC limit, with the projected 90-day headroom
- **Biometric attendance** — a shift with auto-attendance, 72 punches from device `MSCAST-DOOR-01`, converted automatically into Attendance, with an audit report reconciling punches to attendance

  *(Since superseded: the scheduled pull that would keep this current is switched off. The 72 punches and the reconciliation report are real; the automation behind them is not yet running.)*

### Controls

- **Four active workflows**: PCC approval, purchase order approval, BRM certification, project kick-off. The BRM workflow drives the same `status` field the payment block reads, so certifying through the workflow is what unlocks payment — no parallel truth. The block sits in application code (`mscast_erp.controls.brm_payment`) on both Payment Entry and Journal Entry, not in a screen-edited script

  *(Since superseded: five workflows. Drawing release was added, and the approving roles moved to the directors.)*
- **Five department users** (accounts, purchase, design, stores, HR) on matching roles, so the demo never runs as Administrator

  *(Since superseded: 13 staff logins — 12 named people plus the site administrator — with a documented approval matrix. See Role Cards.)*
- **Google Chat webhooks** for transactions above ₹5 L — configured, left disabled until you paste the space URL

---

## How this was verified

The daily summary shipped to you yesterday with two wrong numbers. It ran without error and
returned plausible figures; the only reason it was caught is that you sent a screenshot. That is
not a repeatable quality process, so I built one.

**`seed/102_test_harness.py` — 23 checks, all passing.** The one that matters most:

> **T1** parses every custom report's SQL, finds every literal compared against a field
> (`status = 'Approved'`, `result in ('Accepted')`, …), looks up that field's real Select options,
> and fails if the literal isn't one of them.
> **324 literal comparisons checked, 0 mismatched.**

That check would have caught yesterday's bug — the report compared against `'Approved'` when the
field's actual option is `'Approved by Customer'`, so it matched all nine drawings instead of two.

The rest: every report executes; no report uses the container's UTC date; every print format
renders; the trial balance nets to zero; the balance sheet balances; the P&L ties to the ledger;
no ledger entry without a cost centre; the BRM payment block actually refuses an uncertified bill on all six routes tested
(tested live and rolled back); workflows are complete; every stored Select value is a valid option;
every invoiced item has an HSN; GST head matches place of supply on every invoice; mail works and
no notification has a dead recipient; payroll and attendance are consistent.

> *(Since extended to **37 checks**, in several steps, and the sequence is worth reading because each
> step exists only because the one before it missed something.*
>
> *First, **T6d**. An app install silently moved cost-sheet approval and bill certification to the
> wrong roles and this harness still passed, because it checked that workflows were **active and
> complete** and never checked **who they gave authority to**. T6d asserts the approval matrix
> outright.*
>
> *Then **T6e**, which asks whether any ordinary user can both raise and approve the same document.
> It excludes System Manager holders, on the reasoning that someone who can do anything is not a
> meaningful segregation breach.*
>
> *That exclusion turned out to be a blind spot, so **T6f** reports it instead of hiding it: who
> holds System Manager, and what else they hold. It immediately found an operational staff account
> carrying it, which bypassed every control in the system and which nothing had reported.*
>
> *Finally **T6g**, added on 20 September. T6e compares workflow **transition** roles — but creating
> a document is a permission, not a transition, so "prepare a BRM" was invisible to it. T6g asks the
> auditor's question: can one person create this document and then approve it? It found that a
> director can create a BRM, certify it and mark it paid, alone — which three delivered documents
> had explicitly said was impossible. Those documents are now corrected.*
>
> *Current result: **35 pass, 2 warn, 0 fail of 37**. Both warnings are accepted positions put to
> MSCAST as Q20 and Q21, not defects.)*

Re-run it any time:

```powershell
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/run-seed.sh 102_test_harness
```

---

## What the work found (and fixed)

Building against the books surfaced eight real defects. These are the valuable part of the night:

| # | Found | Fix |
|---|---|---|
| 1 | Balance sheet out by ₹86,400 — totals were being reconstructed from name filters instead of the ledger | Totals now come from the ledger; presentation lines carry an explicit *unclassified* reconciling line so nothing can hide |
| 2 | "Other expenses" negative — expense filters weren't constrained to expense accounts, so `Purchase`/`Material` matched balance-sheet heads | Every filter now constrained by `root_type` |
| 3 | Stock adjustment (−₹24.7 L) sitting in other expenses | Moved to *changes in inventories*, where Schedule III puts it |
| 4 | Receivables netted to zero against customer advances, producing a negative receivables-turnover ratio | Party-wise gross: debit-balance parties are receivables, credit-balance parties are advances |
| 5 | **Share capital of ₹1,00,000 was nowhere in the ledger** — the share transfers registered the holding but posted no entry | Opening entry posted; share capital now appears on the balance sheet |
| 6 | **PPE showed nil** — two assets were created as "existing" with no accounting entry | Opening entry for ₹8,45,000, excluding the test bench whose cost is already in CWIP (that first attempt double-counted it; caught and reversed) |
| 7 | This chart of accounts had **no plant-and-machinery head**, so everything landed in Software | Head created, ₹6,05,000 reclassified, asset categories repointed |
| 8 | **Shareholding was allocated to the wrong directors**, and **the bank guarantees had no expiry date** — so the BG expiry alert could never fire | Both corrected; the ABG now expires 29 Oct, so the 30-day alert fires on 29 Sep. *(Shareholdings were later replaced with unnamed Promoter A/B/C, because attributing invented percentages to real named people is not something a demonstration should do.)* |

Defects 5–8 would have been visible to a client or an auditor. None of them were visible from the
requirement list.

---

## Assumptions I made — please confirm

| ID | Assumption | Who should confirm |
|---|---|---|
| A-14 | The Schedule III presentation as built | CA |
| AC-07 | MSCAST is an SMC reporting under **AS with SMC exemptions**, not Ind AS (correct for this size — Ind AS starts at ₹250 Cr net worth) | CA |
| AC-11 | Income tax at **25.168%** under s.115BAA; the depreciation timing difference is an estimate pending the tax depreciation schedule | CA |
| AC-17 | WIP at cost on unbilled scope, completion measured by billing against contract value | CA (decision D6) |
| M-02 | "Finance Scaling Management" was never defined — read as *can the business fund the order book it is chasing* | MSCAST (Q1) |
| M-03 | No device model given — modelled the standard push pattern; a real ESSL/Matrix/ZKTeco controller posts to the same endpoint and nothing downstream changes | MSCAST (Q6) |

All six remain open as at 20 September. If any answer differs, the change is small and local in every case.

---

## What is still genuinely outstanding

Nothing on the requirement list. What remains is the gap between a POC and production:

- **Previous-year comparatives** are blank until the Tally opening balances are migrated
- **Opening data migration** from Tally — masters, open POs/SOs, stock, retention, BGs
- **Production hosting** — VPS, HTTPS, real users and passwords, daily India-hosted backups (Companies (Accounts) Rules r.3(5))
- **Google Chat webhooks** need the space URL to be enabled
- **Gemini automation layer** from the phased plan — needs a Google Cloud project (decision D5)

  *(Since built. The exception sweep and the AI morning briefing both run, through a local model router rather than a cloud project. A cloud key is only needed when the system moves to a server that cannot reach that router — a configuration change, not a build.)*

Added since, and not on the original list:

- **The demonstration administrator account holds fourteen roles** including every manager role. Convenient for a demo, a hole in the separation of duties on a live system. Must be cut back before real data

  *(Since closed, and the figure was wrong: it held **41**, not fourteen. It now holds `System Manager` and nothing else. Auditing it turned up a second and worse case — an ordinary staff account also holding `System Manager`, which bypasses every control in the system. Removed. Both are now asserted on every build by T6f, because a fresh install recreates the first one.)*
- **The Administrator password** set during the POC must be rotated

  *(Still open, deliberately. This is a POC on a laptop; it becomes mandatory the moment the system moves to a server or carries real data.)*
- **Deployment discipline** — deploy from a tagged release, never a copied folder, and read the post-deploy verification output
- **The segregation of duties around supplier bills** is weaker than three of these documents claimed, and the decision now sits with MSCAST as Q21 in the traceability matrix

  *(Added 20 September, from T6g.)*
- **`reset-poc.sh` has not been run end to end** since the four most recent seed scripts joined it. Each was verified individually against the live site, but the claim that the system rebuilds from nothing is currently untested

---

## Where things are

| | |
|---|---|
| Repository | `github.com/cb1-tech/mscast` — release **`v0.9.0`** |
| Installable app | `mscast_erp/` in that repository |
| Seed scripts | `erpnext-poc/seed/` — `102` is the test harness |
| Rebuild from scratch | `erpnext-poc/scripts/reset-poc.sh` |
| Current documents | *Client Setup Guide v2.2*, *SOPs v2.1*, *Role Cards v1.2*, *Cutover Runbook*, *Traceability v1.7*, *Independent Review* — in the project and in `ERP Plan\` |

## Suggested first fifteen minutes

1. Open **MSCAST Balance Sheet (Schedule III)** and confirm it balances.
2. Open **MSCAST Notes to Accounts** — note 6 is the MSMED disclosure your auditor will ask for first.
3. Open **MSCAST Schedule III - Ratios** and see which show `n/a` and why.
4. Open a **Purchase Order** and watch the approval workflow bar appear.
5. Try to pay an uncertified supplier bill and watch the BRM block refuse it.
6. Open a **Drawing** in *Draft* and try to release it for manufacture — the system will not offer it.
7. Run the test harness and watch 37 checks report **35 pass, 2 expected warnings, 0 failures** — then read what the two warnings say, because they are the honest part.
