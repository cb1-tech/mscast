---
title: "MSCAST ERP — Operating Recommendations"
---

# MSCAST ERP — Operating Recommendations

**For:** MSCAST Engineering Pvt Ltd · **Version:** 2.0 · **Date:** 21 September 2026

**Purpose:** rules for accurate entries and system administration. Each rule targets an error that produces no warning: the system keeps working and totals still add up.

| Part | For |
|---------------------------------|-------------------------------------------------------------------|
| A | Whoever enters transactions |
| B | Whoever closes the books |
| C | Whoever administers the system |
| D | Everyone — the short version, for pinning up |

Procedures (how staff do the work): doc 06 (*SOPs and Use Cases*).

---

# Part A — Entering transactions

## A1. Opening balances go to the opening account, never to an adjustment account

- **Rule:** when bringing in opening balances (stock, assets, anything carried over from Tally), set the difference account to **`1910 Temporary Opening`**.
  - It is an asset account, so the entry stays on the balance sheet; the opening trial balance entry clears it.
- **Why:** a Stock Entry posts its counterpart to the difference account, whose default is **Stock Adjustment** — an **expense** account.
  - A credit there reads as reduced costs: profit is overstated, the tax provision is computed on it, and every profit ratio is wrong.
  - The balance sheet still balances and nothing is flagged.
  - Example (POC data): two opening-stock entries credited **₹24,74,400** to Stock Adjustment.
- **How to spot it:** in the Statement of Profit and Loss, look for any line that is *negative when it should be positive*. A negative expense is almost always a wrong posting.

## A2. Retention only where a contract calls for it

- **Rule:**
  - Reclassify to Retention Receivable **only** where the sales order carries a retention percentage (`Sales Order.retention_percent`). No retention clause = no retention.
  - Post it **against the invoice** it relates to, with the customer on both lines.
  - Retention on a **spares sale is unusual** — question it before posting.
  - **At month end**, compare the Retention Receivable ledger with the *Retention and Certificates* report (which calculates entitlement from `Sales Order.retention_percent`). A customer in one and not the other means one is wrong.
- **Why:** retention is money MSCAST is owed but cannot yet collect. Against the wrong customer, it is chased from the wrong person and released against the wrong certificate. Without a contract behind it, it is not an asset.
  - Example (POC data): ₹1,81,248 (exactly 10% of the invoice, correct party, correct invoice) was reclassified for a spares customer with no project and no retention clause. Every field was consistent; the entry was still wrong.

## A3. Not every document belongs to a project

- **Rule:** a project goes on a document only when the work is *for that project*. Spares, utilities, insurance, travel and office costs usually are not.
- **Do not force a project** onto spares sales, non-project purchases or administrative expenses.
- **Why:** a wrong project link corrupts the project MIS, the WIP valuation and the closure report, and is harder to find than a blank field.
  - Example (POC data): a delivery note for 8 mould tubes sold as spares, with no project and no sales order, is correct as it stands.

## A4. TDS is deducted on the amount excluding GST

- **Rule:** where GST is shown separately on the invoice, TDS is computed on the value **excluding GST** (CBDT Circular 23/2017). Under s.194C: 2% of the net.

| | |
|-----------------------------------------|-----------------------------------------------------------|
| Net (before GST) | ₹5,16,000.00 |
| CGST 9% + SGST 9% | ₹92,880.00 |
| Gross | ₹6,08,880.00 |
| **TDS at 2% of the net** | **₹10,320.00** |
| Payable after TDS | ₹5,98,560.00 |

- Deducting on the **gross** over-deducts and irritates suppliers.
- Checking the rate against the **amount payable after TDS** makes a correct deduction look wrong; deducting on that figure under-deducts and leaves MSCAST liable for the shortfall.

## A5. One naming series per document type

- **Rule:** pick the series once. **Never accept ERPNext's default when creating a document by hand.**
  - MSCAST sales invoices: `SINV-26-`. ERPNext's default: `ACC-SINV-2026-`.
- **Why:** two series in one company means reports filtering or sorting by number miss records, and the auditor's question "is this the complete set of invoices for the year?" cannot be answered from the numbering.

## A6. Master data is created by the function that owns it, before the first transaction

- **Suppliers:** GSTIN and, where applicable, **Udyam number with MSME class**, at creation, in writing from the supplier. Without it the 45-day clock cannot run, and a bill past day 45 is a disallowed expense under s.43B(h).
- **Items:** **HSN/SAC code** at creation. Without it no GST invoice can be submitted.
- **Customers:** GSTIN and correct state before the first quotation.
- **Search before creating.** "Suvarna Copper" and "Suvarna Copper Moulds Pvt Ltd" as two suppliers = two ledgers, two ageing lines, and a wrong MSME position on both.

## A7. Enter transactions the day they happen

- Every control compares documents against each other; a bill entered 3 weeks late is outside every control for those 3 weeks.
- A system updated daily shows the business as it is; one updated at month end shows what somebody remembered.

## A8. The BRM exemption is for bills that cannot be certified — nothing else

- **The control:** no supplier is paid without a **certified BRM**. Refused in software on every route — Payment Entry, Journal Entry, and an advance with no invoice behind it — for everyone, directors included.
- **The exemption:** tick **Exempt from BRM certification** on the supplier record only for suppliers whose bills have no purchase order, inspection or delivery to certify: **electricity, water, rent, telephone, statutory payments**.
- **How to use it:**
  - Tick it when the supplier is created, never to release a stuck payment.
  - **It applies to the supplier, not the bill:** once ticked, *every* bill from that supplier is payable without a certificate. Never tick a supplier who also sells goods or services against a purchase order.
  - A utility supplier who later supplies materials must be **unticked**, or split into two supplier records.
  - Report the count of exempt suppliers in the monthly review (B2). It should be small and change rarely. At POC handover: **0 of 15** suppliers ticked. MSCAST is to supply the list of BRM-exempt suppliers (open item).
- **A refused payment is the control working.** Raise and certify the BRM; do not exempt the supplier. Procedure: doc 06, SOP-07.

---

# Part B — Closing the books

## B1. The month-end sequence, in order

1. Book every supplier invoice for the month.
2. Reconcile the bank.
3. Reconcile GSTR-2B against the purchase register. Resolve mismatches with suppliers **before** filing.
4. File GSTR-1 and GSTR-3B. Deposit TDS.
5. **Check the MSME 45-day report.** Anything past day 45 is a s.43B(h) disallowance — pay it, or accept the tax cost knowingly.
6. Update project WIP.
7. Post provisions: depreciation, gratuity, known liabilities.
8. Review the Schedule III statements. Confirm the trial balance nets to zero and profit ties to the ledger.
9. Review the project MIS.

## B2. Three numbers to check every month, before anything else

Each can be wrong while the totals look right.

| Check | Because |
|----------------------------------|------------------------------------------------------------------|
| **Any negative expense line** | A credit in an expense account is nearly always a wrong posting (A1) |
| **Retention Receivable, by customer** | Compare with the *Retention and Certificates* report. Different customers in each = one is wrong (A2) |
| **Trade receivables gross, not netted** | Customer advances netted against receivables give a meaningless ageing and a negative turnover ratio |

Also report the count of BRM-exempt suppliers (A8).

## B3. Provisions follow the final profit, not a draft of it

- **Order:** make every correction → then provide for tax → then produce the statements.
- Any change to profit (reclassification, correction, payroll change) means the **tax provision is recomputed afterwards**.
- Example (POC data): after the opening-stock correction (A1) the provision was recomputed: ₹15,32,737 at 25.168% on profit before tax of ₹60,90,022.

## B4. Statutory applicability is a question of fact, not of headcount alone

| | Threshold | Note |
|-----------------------------|---------------------------------|--------------------------------------|
| **Gratuity** (Payment of Gratuity Act, s.1(3)) | 10+ employees | Once applicable, continues under s.1(3A) |
| **ESI** (ESI Act, s.1(5)) | 10+ in Maharashtra | Employees earning up to ₹21,000/month |
| **EPF** (EPF & MP Act, s.1(3)) | **20+ employees** | See below |

- **Current position:** MSCAST has under 20 employees and no employee has a UAN, so PF has been removed from payroll at MSCAST's instruction.
- **The EPF exception:** under s.1(5), an establishment once covered **stays covered** even if headcount falls below 20. If MSCAST has ever held an EPF establishment code, stopping PF is non-compliance; s.14B damages and s.7Q interest follow.
- **Action:** the CA confirms there is no continuing EPF coverage under s.1(5) (open question B6) **before the first real payroll run**.
- The system refuses to remove PF if any employee record carries a UAN (the visible sign of registration).

## B5. Assumptions are written where the reader meets them

- Six accounting positions rest on assumptions MSCAST and the CA have not yet confirmed:
  1. Schedule III presentation
  2. AS/SMC basis
  3. s.115BAA tax election
  4. WIP valuation method
  5. what "finance scaling" means
  6. biometric device pattern
- **Rule:** each is written into the narration of the voucher it affects. **Keep doing that** — the auditor reads voucher narrations, not policy notes.

---

# Part C — Administering the system

## C1. Business rules live in the package, not in the screens

- A workflow, approval role, notification or print format changed **in the ERPNext screens is temporary**: every install and upgrade re-imports the package configuration and overwrites the database.
- Installing from an out-of-date copy silently reverts approval rules (for example, cost-sheet approval moves to a system role and bill certification back to the Purchase Manager); everything keeps working and ordinary checks pass.
- **Rule:** an approval changes in the repository (github.com/cb1-tech/mscast, app `mscast_erp`) and is deployed.
- After every install and upgrade, the system verifies 6 control transitions and repairs any that differ, with a banner. **A repair banner is not "handled"**: it means the deployed package and what MSCAST agreed differ — reconcile them.
- **The package carries only MSCAST's configuration.** It re-applies what it carries on every upgrade, so another application's configuration in it would undo that application's next release. MSCAST customisations are marked with module *MSCAST*; everything else is left to the application that owns it.
- Deploy procedure: doc 05, Step 12, and doc 08.

## C2. Roles are a control, and they drift

- **Nobody who does day-to-day work holds `System Manager`** — it bypasses every control in the system.
- A fresh install recreates the over-privileged setup-wizard administrator (41 roles in the POC) every time. Cutting it back to `System Manager` only is a deployment step, not a one-off.
- Review the role list **quarterly**. Roles accumulate; they are never removed by accident.
- **Change permissions in the package, not the screens.** The permission matrix lives in the application and is re-applied on every upgrade.
  - Adding one custom permission row to a document type replaces all its standard rows, so other roles can lose access (in the POC, the managing director could not open the kick-offs he approves).
  - After any permission change, log in **as the approver** and open the document. Build check `T6k` tests this.

## C3. "Configured" and "runs" are different claims

- A scheduled job can be enabled, correctly configured, work when run by hand — and never run on schedule (for example, if the scheduler cannot load the application).
- **Check `last_execution` on every scheduled job**, not just that the scheduler process is alive. Build check `T9f` tests this.

## C4. Test the backup, not the backup job

- Restore a backup before go-live and once a year after. **Record how long the restore took** — that is the recovery time MSCAST actually has.
- **The encryption key is not in the database backup.** Keep it with the backups, protected like a password; `restore-key.sh` puts it back. Without it the restored system looks healthy but cannot send email.
- Also outside the database (not carried by a restore): `server_script_enabled` (bench-wide) and `host_name`.
- After any restore, send a test email and confirm it arrives.
- Rule 3(5), Companies (Accounts) Rules: the server and its daily backups must both be physically in India.
- s.128(5): books and audit trail kept for 8 financial years. Daily backups may rotate at 30 days; monthly backups may not.

---

# Part D — The short version

Pin this up.

1. **Opening balances go to `1910 Temporary Opening`**, never to Stock Adjustment.
2. **A negative expense line is a wrong posting** until proven otherwise.
3. **Retention only where the sales order has a retention clause**, against the invoice, same customer both sides.
4. **Do not force a project** onto spares, utilities or admin costs.
5. **TDS is 2% of the net, excluding GST** — not the gross, not the amount payable.
6. **One naming series** per document type. Never accept the default.
7. **Udyam number at supplier creation. HSN at item creation.** Neither can be added usefully later.
8. **No certified BRM, no payment.** The *BRM-exempt* tick is for electricity, rent and statutory bills only — never to clear a stuck payment.
9. **Enter it the day it happens.**
10. **Correct first, then provide for tax, then produce the statements.**
11. **Never change an approval rule through the screens** — it is reverted at the next upgrade.
12. **Nobody operational holds `System Manager`.**
13. **Read the morning note.** An item appearing 6 mornings running is a procedure not being followed, not a document needing fixing.

---

## Build checks behind these rules

The build checks assert these on every deployment; a failure stops the release. Full check list: the POC README (*POC README*).

| Check | Asserts | Rule |
|-----------------------|------------------------------------------------------------|-----------------|
| `T5a`–`T5d` | Trial balance nets to zero; balance sheet balances; profit ties to the ledger; no entry without a cost centre | B1 |
| `T6a` | No payment without a certified BRM, by anyone, on any of six routes (incl. payment entry, journal entry, advance without a reference, amount above the certificate). A certified bill and a BRM-exempt supplier still pay | A8 |
| `T6c` | The payment control is in the application package, not a screen-edited script | C1 |
| `T6d` | The approval authority sits where MSCAST put it | C1 |
| `T6e`, `T6g` | Whether one person can raise and approve, or create and approve, the same document | C2 |
| `T6f` | Only administrators hold `System Manager` | C2 |
| `T6h` | The Auditor login cannot change anything | C2 |
| `T6i` | Every role can raise the documents its role card describes | C2 |
| `T6j` | A guarded workflow state is guarded on every route into it | C1 |
| `T6k` | Whoever can approve a document can open it | C2 |
| `T7c` | Every invoiced item carries an HSN code | A6 |
| `T8` | The GST head matches the place of supply on every invoice | A6 |
| `T9f` | Every enabled scheduled job has actually run | C3 |

**Current result:** 42 checks.

- **DEV:** 40 PASS, 2 WARN, 0 FAIL. The warnings (`T6e`, `T6g`) are director self-approval positions awaiting MSCAST's answers to Q20 and Q21 — not defects.
- **Live POC:** 38 PASS, 3 WARN, 1 FAIL — its true state, left as is:
  - `T10c` fails: demo biometric punches were deleted by MSCAST's trial admin.
  - `T6f` warns: Aiqaz was given `System Manager`.
