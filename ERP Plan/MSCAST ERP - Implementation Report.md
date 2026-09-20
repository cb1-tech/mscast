# MSCAST ERP - overnight implementation report

**19 September 2026** · POC on ERPNext v16 · site `frontend` · http://localhost:8080 ·
public https://thinkstation.tailf78e82.ts.net

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

### Controls

- **Four active workflows**: PCC approval, purchase order approval, BRM certification, project kick-off. The BRM workflow drives the same `status` field the payment block reads, so certifying through the workflow is what unlocks payment — no parallel truth
- **Five department users** (accounts, purchase, design, stores, HR) on matching roles, so the demo never runs as Administrator
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
no ledger entry without a cost centre; the BRM payment block actually refuses an uncertified bill
(tested live and rolled back); workflows are complete; every stored Select value is a valid option;
every invoiced item has an HSN; GST head matches place of supply on every invoice; mail works and
no notification has a dead recipient; payroll and attendance are consistent.

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
| 8 | **Shareholding was allocated to the wrong directors** (70% to Zameer instead of Mustaque), and **the bank guarantees had no expiry date** — so the BG expiry alert could never fire | Both corrected from the knowledge base; the ABG now expires 29 Oct, so the 30-day alert fires on 29 Sep |

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

If any answer differs, the change is small and local in every case.

---

## What is still genuinely outstanding

Nothing on the requirement list. What remains is the gap between a POC and production:

- **Previous-year comparatives** are blank until the Tally opening balances are migrated
- **Opening data migration** from Tally — masters, open POs/SOs, stock, retention, BGs
- **Production hosting** — VPS, HTTPS, real users and passwords, daily India-hosted backups (Companies (Accounts) Rules r.3(5))
- **Google Chat webhooks** need the space URL to be enabled
- **Gemini automation layer** from the phased plan — needs a Google Cloud project (decision D5)

---

## Where things are

| | |
|---|---|
| Matrix | `D:\MSCAST\ERP Plan\MSCAST ERP - Requirements Traceability Matrix v1.5.xlsx` |
| Traceability (markdown) | `D:\MSCAST\ERP Plan\03-MSCAST-ERP-Requirements-Traceability-v1.5.md` and in the project |
| This report | `D:\MSCAST\ERP Plan\MSCAST-ERP-Overnight-Implementation-Report.md` |
| Seed scripts | `D:\MSCAST\erpnext-poc\seed\90-105` (this run), `102` is the test harness |
| POC README | `D:\MSCAST\erpnext-poc\README-v3.md` and in the project |

The stack is running and the 08:30 IST report batch is scheduled, so the daily management summary
should be in your inbox by the time you read this.

## Suggested first fifteen minutes

1. Open **MSCAST Balance Sheet (Schedule III)** and confirm it balances.
2. Open **MSCAST Notes to Accounts** — note 6 is the MSMED disclosure your auditor will ask for first.
3. Open **MSCAST Schedule III - Ratios** and see which show `n/a` and why.
4. Open a **Purchase Order** and watch the approval workflow bar appear.
5. Try to pay `SMW/CAP/2026/08` and watch the BRM block refuse it.
6. Run the test harness and watch 23 checks pass.
