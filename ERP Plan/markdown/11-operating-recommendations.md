---
title: "MSCAST ERP — Operating Recommendations"
---

# MSCAST ERP — Operating Recommendations

**For:** MSCAST Engineering Pvt Ltd · **Version:** 1.1 · **Date:** 21 September 2026

## Why this document exists

Every recommendation here comes from a mistake that was actually made while building this system — not from a list of good practice. Each one was found, traced to its cause, and in most cases turned into an automated check so it cannot happen again silently.

That matters because of what these errors had in common: **none of them announced themselves.** The system kept working. Reports kept running. Totals kept adding up. In one case a control that three documents described as enforced had never existed; in another, a figure of ₹24.74 lakh sat in the profit and loss account for weeks without anyone noticing that it was not profit.

They are written down because the same mistakes are available to MSCAST every day once the system carries real data, and because the ones that hurt are not the obvious ones.

**How to use it.** Part A is for whoever enters transactions. Part B is for whoever closes the books. Part C is for whoever administers the system. Part D is the short version, for pinning up.

---

# Part A — Entering transactions

## A1. Opening balances go to the opening account, never to an adjustment account

**What happened.** Opening stock was brought in with a Stock Entry. ERPNext posts the counterpart of a Stock Entry to whatever account is set as the *difference account*, and the default is **Stock Adjustment** — which is an **expense** account. Two such entries credited **₹24,74,400** to it.

A credit sitting in an expense account behaves exactly like a reduction in costs. Reported profit was inflated by ₹24.74 lakh, the tax provision was computed on that inflated figure, and every ratio derived from profit was wrong. The balance sheet still balanced. The trial balance still netted to zero. Nothing was flagged, because nothing was broken — the money had simply been booked to the wrong kind of account.

**What to do.** When bringing in opening balances — stock, assets, anything carried over from Tally — set the difference account to **`1910 Temporary Opening`**. That account exists for exactly this. It is an asset account, so the entry stays on the balance sheet where an opening balance belongs, and it is cleared by the opening trial balance entry.

**How to spot it.** Open the Statement of Profit and Loss and look for any line that is *negative when it should be positive*. A negative expense is almost always a posting to the wrong account, not a genuine credit.

## A2. Retention belongs only where a contract calls for it

**What happened.** A journal entry reclassified **₹1,81,248** from trade receivables into Retention Receivable. The entry was internally perfect: the amount was exactly 10% of the invoice it referenced, the party matched on both lines, and it was posted against the right invoice.

It was still wrong. The customer was a **spares customer with no project and no retention clause**. Nothing in the contract entitled MSCAST to hold that money back. Meanwhile the *Retention and Certificates* report calculates entitlement from `Sales Order.retention_percent` — so it listed two entirely different customers. The ledger and the report described different worlds, and neither was checkable against the other.

**What to do.**

- Reclassify retention **only** where the sales order carries a retention percentage. If the order has no retention clause, there is no retention.
- Post it **against the invoice** it relates to, with the customer on both lines.
- Retention on a **spares sale is unusual** — question it before posting it.
- At month end, compare the Retention Receivable ledger against the *Retention and Certificates* report. If a customer appears in one and not the other, one of them is wrong.

**Why it matters.** Retention is money MSCAST is owed but cannot yet collect. Recorded against the wrong customer, it is chased from the wrong person and released against the wrong certificate. Recorded where no contract supports it, it is not an asset at all.

## A3. Not every document belongs to a project

A delivery note with no project was flagged during review as an error. It was not. It was **8 mould tubes sold as spares** to a customer who has no project and no sales order — a perfectly ordinary transaction.

**Do not force a project reference onto spares sales, non-project purchases or administrative expenses.** A wrong project link is worse than a blank one: it silently corrupts the project MIS, the WIP valuation and the closure report, and it is far harder to find afterwards than an empty field.

The rule: a project goes on a document when the work is *for that project*. Spares, utilities, insurance, travel and office costs mostly are not.

## A4. TDS is deducted on the amount excluding GST

A supplier bill was reported during review as having TDS that "does not reconcile". It reconciled exactly:

| | |
|---|---|
| Net (before GST) | ₹5,16,000.00 |
| CGST 9% + SGST 9% | ₹92,880.00 |
| Gross | ₹6,08,880.00 |
| **TDS at 2% of the net** | **₹10,320.00** |
| Payable after TDS | ₹5,98,560.00 |

TDS under s.194C is **2% of ₹5,16,000**, not of the gross and not of the amount payable. **CBDT Circular 23/2017** requires TDS to be computed on the value *excluding* GST wherever GST is shown separately on the invoice.

The reviewer had divided TDS by the amount payable *after* TDS had already been deducted, and concluded the rate was wrong. It is worth knowing both directions of this: deducting on the gross over-deducts and irritates suppliers; deducting on the post-TDS figure under-deducts and leaves MSCAST liable for the shortfall.

## A5. One naming series per document type

One sales invoice was created on ERPNext's default series (`ACC-SINV-2026-`) while every other invoice used MSCAST's (`SINV-26-`). Harmless in itself — but two series in one company means any report filtering or sorting by invoice number silently misses records, and an auditor asking "is this the complete set of invoices for the year?" cannot be answered from the numbering alone.

**Pick the series once, and never accept the default when creating a document by hand.**

## A6. Master data is created by the function that owns it, before the first transaction

- **Suppliers** need a GSTIN and, where applicable, a **Udyam number with MSME class** — captured at creation, in writing from the supplier. Without it, the 45-day clock cannot run and a bill past day 45 is a disallowed expense under s.43B(h).
- **Items** need an **HSN/SAC code** at creation. Without one, a GST invoice cannot be submitted at all.
- **Customers** need a GSTIN and the correct state before the first quotation.

**Search before creating.** "Suvarna Copper" and "Suvarna Copper Moulds Pvt Ltd" as two suppliers means two ledgers, two ageing lines, and an MSME position that is wrong on both.

## A7. Enter transactions the day they happen

The habit that makes the difference, and the one that slips first. A system updated daily tells you the truth about the business. A system updated at month end tells you what somebody remembered.

Every control in this system compares documents against each other. A bill entered three weeks late was not covered by any of them for three weeks.

## A8. The BRM exemption is for bills that cannot be certified — nothing else

No supplier can be paid without a **certified Billing Routing Memo**. That is refused in software, on every route: a Payment Entry, a Journal Entry, and an advance with no invoice behind it. It applies to everyone, directors included.

Some bills cannot have a BRM, because there is no purchase order, no inspection and no delivery to certify against — **electricity, water, rent, telephone, statutory payments**. For those, and only those, tick **Exempt from BRM certification** on the supplier record.

**How to use it:**

- Tick it when the supplier is created, not when a payment is stuck. A tick applied under time pressure is how a trade supplier becomes exempt.
- **It is a property of the supplier, not of the bill.** Once ticked, *every* bill from that supplier is payable without a certificate. Never tick a supplier who also sells goods or services against a purchase order.
- A supplier who starts as a utility and later supplies materials must be **untick**ed, or split into two records.
- The count of exempt suppliers belongs in the monthly review (B2). It should be small, and it should change rarely. At handover it was **0 of 15**.

**If a payment is refused, the refusal is the control working.** The answer is to raise and certify the BRM, not to exempt the supplier. Certifying is what releases the money; that is the whole point of the memo.

---

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

## B2. Three numbers to look at every month before anything else

These are the ones that were wrong at some point during the build, and each was invisible in the totals.

| Look at | Because |
|---|---|
| **Any negative expense line** | A credit in an expense account is nearly always a wrong posting, not a genuine credit. This is how ₹24.74 lakh of phantom profit survived for weeks |
| **Retention Receivable, by customer** | Compare it to the retention entitlement report. Different customers in each means one is wrong |
| **Trade receivables gross, not netted** | Customer advances netted against receivables produce a meaningless ageing and a negative turnover ratio |

## B3. Provisions follow the final profit, not a draft of it

When something changes the profit — a reclassification, a correction, a payroll change — the **tax provision has to be recomputed afterwards, not before.** During this build, correcting the opening-stock posting reduced profit before tax by ₹24.74 lakh, and the existing provision of ₹5,23,156 had been calculated on the inflated figure. It was reprovisioned at ₹15,32,737 on the corrected profit before tax of ₹60,90,022.

The order is: make every correction, then provide for tax, then produce the statements.

## B4. Statutory applicability is a question of fact, not of headcount alone

PF, ESI and gratuity were built into payroll on the assumption that all three apply. MSCAST has since confirmed they do — but the thresholds differ and one of them has an exception that costs money to get wrong:

| | Threshold | Note |
|---|---|---|
| **Gratuity** (Payment of Gratuity Act, s.1(3)) | 10+ employees | Once applicable, continues under s.1(3A) |
| **ESI** (ESI Act, s.1(5)) | 10+ in Maharashtra | Applies to employees earning up to ₹21,000/month |
| **EPF** (EPF & MP Act, s.1(3)) | **20+ employees** | **See below** |

**The EPF exception.** MSCAST is under 20 employees and no employee carries a UAN, so PF has been removed from payroll at MSCAST's instruction. But **under s.1(5), an establishment that has once been covered remains covered even if its headcount later falls below 20.** If MSCAST has ever held an EPF establishment code, stopping PF is not a correction — it is non-compliance, and s.14B damages plus s.7Q interest follow.

**This is one line for the CA, and it should be answered before the first real payroll run.** The system refuses to remove PF if any employee record carries a UAN, which is the visible sign of registration.

## B5. Assumptions are written where the reader meets them

Six accounting positions in this system rest on assumptions MSCAST and the CA have not yet confirmed: the Schedule III presentation, the AS/SMC basis, the s.115BAA tax election, the WIP valuation method, what "finance scaling" means, and the biometric device pattern.

Each is written into the narration of the voucher it affects, so whoever reviews the books meets the assumption at the point it matters rather than in a document they may never open. **Keep doing that.** An assumption recorded in a policy note is an assumption nobody reads; an assumption in the voucher narration is one the auditor finds.

---

# Part C — Administering the system

## C1. Business rules live in the package, not in the screens

Changing a workflow, an approval role, a notification or a print format **through the ERPNext interface is temporary.** Installing or upgrading the application re-imports its configuration and overwrites the database. This was established by experiment, not assumed.

It has already happened once: an install from a slightly out-of-date directory silently moved cost-sheet approval to a system role and bill certification back to the purchase manager. Everything still worked. Every check still passed. Nobody would have known until an audit.

**If an approval must change, it changes in the repository and is deployed.** After every install and upgrade the system verifies six control transitions and repairs them loudly. **A repair banner is not "handled"** — it means what you deployed and what MSCAST agreed have diverged.

## C2. Roles are a control, and they drift

Two accounts were found holding far more than their job required: the setup-wizard administrator with **41 roles**, and an ordinary staff account that also held `System Manager`, which bypasses every control in the system. Neither had been noticed, and nothing reported them.

- **Nobody who does day-to-day work should hold `System Manager`.**
- A fresh install recreates the over-privileged administrator every time. Cutting it back is a deployment step, not a one-off.
- Review the role list quarterly. Roles accumulate; they are never removed by accident.

## C3. "Configured" and "runs" are different claims

Four of the five scheduled jobs in this system — including the 06:00 exception sweep and the 08:35 morning briefing — were correctly configured, enabled, and **had never executed once.** They worked perfectly when run by hand, which is how they were built and demonstrated. The scheduler could not load the application that defines them.

Every check asked *"is this configured?"* and all of them passed. None asked *"has it ever run?"*

**Check `last_execution` on every scheduled job, not just that the scheduler process is alive.** A job that is enabled, correctly scheduled and has never run is the failure mode that hides longest.

## C4. Test the backup, not the backup job

An untested backup is a belief. Restore one before go-live and once a year afterwards, and **write down how long it took** — that number is what MSCAST is actually buying.

Under Rule 3(5) of the Companies (Accounts) Rules the server and its daily backups must both be physically in India, and under s.128(5) the books and the audit trail are kept for eight financial years. Dailies may rotate at thirty days; monthlies may not.

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
13. **Read the morning note.** An item appearing six mornings running is a procedure not being followed, not a document needing fixing.

---

## What is checked automatically

These no longer depend on anyone remembering. The build checks assert them on every deployment, and a failure stops the release:

| Check | Asserts |
|---|---|
| `T5a`–`T5d` | Trial balance nets to zero; the balance sheet balances; profit ties to the ledger; no entry without a cost centre |
| `T6a` | A supplier bill with no certified BRM cannot be paid — by anyone, on **any** of six routes: payment entry, journal entry, advance without a reference, and an amount above the certificate. A properly certified bill, and a BRM-exempt supplier, must still pay |
| `T6c` | The payment control is in the application package, not in a screen-edited script |
| `T6d` | The approval authority sits where MSCAST put it |
| `T6e`, `T6g` | Whether one person can raise and approve, or create and approve, the same document |
| `T6f` | Only administrators hold `System Manager` |
| `T6h` | The auditor login cannot change anything |
| `T6i` | Every role can raise the documents its role card describes |
| `T6j` | A guarded workflow state is guarded on **every** route into it |
| `T7c` | Every invoiced item carries an HSN code |
| `T8` | The GST head matches the place of supply on every invoice |
| `T9f` | Every enabled scheduled job has actually run |

Current result: **29 pass, 2 warnings, 0 failures of 31.** Both warnings are accepted positions on director self-approval, put to MSCAST as Q20 and Q21 in the traceability matrix — not defects.

**The pattern worth taking from all of this:** every one of these was found by asking the system, not by reading the configuration. A system that reports itself healthy is making a claim, and the claim is only as good as the question behind it.
