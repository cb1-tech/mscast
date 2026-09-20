---
title: "MSCAST ERP — Independent Review and Verification"
---

# MSCAST ERP — Independent Review and Verification

**Date:** 20 September 2026 · **Status:** findings as recorded on the morning of 20 September

> **This document is a point-in-time record and is deliberately not rewritten.** The findings below are left exactly as the reviewers made them, including the ones that have since been fixed and the one that turned out to be wrong. **Section F, at the end, gives the position as at the evening of 20 September** and should be read alongside any finding here. Editing findings after the fact destroys the only thing a review is for.

Two independent reviewers were run against the delivered work — one across everything delivered, one against the ERPens proposal. Neither built any of it. Their findings were then **verified against the live POC** where verification was possible. This document separates what is *confirmed true* from what is *claimed but unverified*, because the two carry very different weight.

---

## A. Confirmed by direct test against the live system

### A1. The demo was publicly reachable with the default Administrator password — FIXED

`mscast.carobar.net` is a public URL. `check_password("Administrator", "admin")` succeeded. Anyone who found the address could have logged in with full rights.

Changed by Sanjay on 20 Sep 2026; `admin`, `Administrator` and `admin123` all now rejected. **The replacement password was typed into a chat transcript and must be rotated again.**

Related settings as found: `allow_consecutive_login_attempts = 10`, `session_expiry = 170:00` (seven days). Both are loose for an internet-facing site.

### A2. MSCAST's real-world identity is on the public demo — OPEN

- `Company.tax_id` = `27AAGCM8444B1ZI` — MSCAST's real GSTIN, printed on every demo tax invoice
- Shareholder records name the three real directors — Mustaque Ahmed N. Chandankeri (7,000 shares), Aiqaz M. Chandankeri (2,000), Zameer Alam Chandankeri (1,000) — with holdings that were **invented**; the knowledge base has no shareholding data and flags Zameer's directorship as possibly ceased

A fictional tax invoice carrying a real GSTIN, and real named individuals with fabricated shareholdings, on a public URL, is a legal and reputational exposure rather than a cosmetic one.

**Fix:** placeholder GSTIN, `Director A/B/C`, and a "DEMONSTRATION — NOT A TAX INVOICE" watermark on every print format.

### A3. The demo story contradicts itself in ways MSCAST will see in seconds — OPEN

| What the data says | Why it cannot be true |
|---|---|
| `SAL-ORD-2026-00001` (PROJ-0001): `per_delivered = 0`, delivery date 2 Dec 2026 | Nothing has shipped against this order |
| `COMM-2026-00001`: commissioned at Jalna works 10–15 Sep 2026, "Completed – provisional acceptance" | A machine was commissioned that was never dispatched |
| `SPH-2026-00001`: commissioning spares handed to the customer 15 Sep 2026 | Same |
| `CERT-2026-00001`: acceptance certificate awaited | Awaited for a machine that has not left the works |
| `DN-26-00001`: the only delivery note, `project = NULL` | The one dispatch is linked to no project |

A MSCAST engineer will spot a commissioned-but-undispatched caster immediately, and after that will not trust any figure on the dashboard.

### A4. Dunning contradicts the receivables position — OPEN

`DUNN-09-26-00001`, ₹4,80,000, status *Unresolved* — while **no** sales invoice is past its due date. The daily summary correctly reports "nothing overdue"; the dunning record says a customer is being chased. Both are on the same demo.

It is also `docstatus = 0` (never submitted), so it is a draft dunning being counted as evidence of a working collections process.

### A5. Retention is posted against the wrong party — OPEN

`ACC-JV-2026-00007` debits *Retention Receivable* ₹1,81,248 with party **Konark Alloys Pvt Ltd (DEMO)**.

₹1,81,248 is exactly 10% of `SINV-26-00002` (₹18,12,480, Konark Alloys). The arithmetic is right. But Konark Alloys is not the customer of either project, while the *Retention and Certificates* report attributes retention to SAL-ORD-00001 (Sahyadri) and SAL-ORD-00002 (Deccan). **The ledger and the report disagree about whose money is being held.**

### A6. Report counts in the documents are wrong

26 custom reports exist (`Report` where `is_standard = No`). The documents variously say 15, 25 and 26.

---

## B. Serious findings not yet verified — check before the client demo

Listed in the reviewers' order of severity. Each needs a test against the live system.

1. **The BRM payment block is narrower than the SOPs claim.** It is a Server Script on Payment Entry *before submit*. Untested: a Journal Entry paying the supplier; an advance Payment Entry with no invoice reference (MSCAST's own requirement routes 30% PO advances through BRM against a proforma); non-project suppliers such as electricity; partial certification where the bill is for 10 and 9 arrived. SOP-04 states "the system will not let one person do both" for PO approval — the owner ≠ approver condition has never been tested.
2. **The MSCAST Director role is read-only on ~30 doctypes but is named as the approver** on PCC, quotation, kick-off, claims, closure, payroll and payments. A read-only role cannot execute a workflow transition. If true, every approval path is broken.
3. **The MSME 45-day clock probably starts from the wrong date.** MSMED s.15 runs from acceptance or deemed acceptance (15 days from delivery), not the invoice date; 45 days applies only with a written agreement, otherwise 15; s.43B(h) covers micro and small only, not medium; s.16 interest must be accrued and disclosed under s.22.
4. **Free issue to fabricators is a plain stock transfer**, not a Subcontracting Order with the India Compliance job-work challan. If so, ITC-04 data is not generated and the one-year return rule is untracked — a GST exposure, not a reporting nicety.
5. **Project WIP uses a method that is neither AS 7 nor AS 9 + AS 2.** Completion is measured as billing ÷ contract value, which recognises profit at the PCC margin regardless of actual cost. The ₹450/hr engineering rate and 12% works overhead need to be cost rates under AS 2.
6. **Tax, PF, ESI and gratuity provisions may be for statutes MSCAST is not under.** 25.168% presumes a s.115BAA election (irrevocable, Form 10-IC); EPF is mandatory at 20+ employees, ESI at 10/20, gratuity at 10+. MSCAST has "up to 10" and no factory. "Lease Liabilities" is an Ind AS 116 head; under AS 19 an operating lease is off balance sheet.
7. **Customer-deducted TDS is absent.** Steel plants deduct 2% under 194C on every payment; there is no TDS-receivable treatment or 26AS reconciliation.
8. **A −₹24.7 L "stock adjustment" sits in the P&L**, almost certainly an artefact of seeding opening stock via Stock Reconciliation instead of Temporary Opening.
9. **Two sales invoice series** (`SINV-26-` and `ACC-SINV-2026-`) run in one company.
10. **TDS on PINV-26-00003 does not reconcile**: ₹10,320 on a ₹5,98,560 bill implies a ₹5,16,000 base at 16% tax, not 18%.

---

## C. Structural findings — these decide whether the project succeeds

### C1. It was built without MSCAST

Every MSCAST-specific form is an inference from a 15-page requirement PDF. The traceability matrix still contains the open questions that would have defined them:

- **Q2** — the real PCC template, who prepares and approves it, at what level. The requirement (S-02) says the PCC is prepared *by Sales from the Sales Order*; the delivered system makes it a **pre-quote** estimate and builds the first control of the whole SOP set on that reading. If MSCAST's PCC is post-order, SOP-01 is wrong from page one.
- **Q3** — the Project MIS format. **Q4** — the BRM format and payment-release rules. **Q5** — MDM, DI and Annexure-I. The Setup Guide and the matrix currently describe Annexure-I going to two different destinations.

"97 of 97 implemented" is the framing most likely to cause damage. The same POC presented as *"this is our reading of your document — correct us"* is a strong opening; presented as finished, the first "that isn't how we do it" collapses the credibility of everything else in the room.

### C2. The delivery is measured against a proposal that was declined

The Strategy document records decision **D4 — decline the fixed-bid ERPens proposal**, replaces its 12–14 weeks with a 10-month self-build, and prices it at "₹0 cash (Sanjay's time)". Against the ERPens proposal as written, the second reviewer scored roughly **60% of base scope, 70% of custom scope, and none of the commercial deliverables** — no UAT, no migration, no training, no production hosting.

That gap only matters if MSCAST believes the ERPens proposal describes what it is getting. **There is no signed scope, fee, milestone or acceptance criterion between Sanjay and MSCAST in any document in this project.** That is the single largest commercial exposure, and it is fixable with one page.

Specific gaps against that proposal, if it is the reference: no ERPNext BOM (the MDF substitutes), no ECR/ECN, no drawing *workflow* (status field plus notification only), no techno-commercial comparison report (fields only, no output), no supplier performance report, no asset movement or maintenance, no batch/serial tracking, no bank reconciliation.

### C3. The operating model needs more people than MSCAST has

Part C of the SOPs names eleven roles. The Director approves PCC, quotation, kick-off, claims, closure, payroll and payments. MSCAST has fewer than ten people, one of whom is the Director. A control that requires a person who does not exist gets bypassed in week two, usually by sharing a login — which destroys the audit trail the entire compliance story rests on.

Same class of problem: timesheets per engineer per equipment feed both WIP and the MIS and decay silently; the drawing register duplicates CAD/Drive; retention is a manual JV per invoice; free-issue consumption is manual; four scheduled emails a day to a director with nine staff.

### C4. There is no path from POC to production

All customisation is database-resident — custom doctypes, server scripts, query reports, workflows, print formats — rebuilt by 73 seed scripts on a Windows PC in Japan. No `mscast_erp` app, no Git repo, no fixtures export, no staging site. The Strategy document lists exactly these as the mitigation for key-person risk, and criticises ERPens for not offering code ownership. MSCAST would own a system it cannot rebuild, upgrade, or hand to another Frappe partner, and an ERPNext minor upgrade can silently break 26 raw-SQL reports that only a harness on Sanjay's PC would detect.

### C5. Everything runs on personal infrastructure

Sanjay's workstation, Sanjay's domain (`carobar.net`), Sanjay's mail account (`uattech@carobar.net`), reports emailed to Sanjay's Gmail, tunnel credentials in Sanjay's user profile, a Startup-folder shortcut to bring the demo back after reboot. The client-facing Setup Guide and SOPs name **Sanjay** as the owner of users, print formats, email, backups, the annual restore test and the monthly archival — indefinite operations work with no support agreement behind it.

### C6. The accounting layer is ahead of the CA

WIP and revenue policy, the MSME clock, the tax regime, PF/ESI/gratuity applicability, works-contract GST and the retention posting all need a chartered accountant's decision, and several are currently non-standard. If the CA is not engaged first, accounts stay in Tally — and the project loses the one thing that justified ERPNext over a cheaper composable stack.

---

## D. What is sound

Stated plainly, because the list above is long:

- The platform choice and the reasoning behind it are well argued; the alternatives assessment is thorough.
- The 23-check test harness is the best engineering decision in the project. T1 — comparing SQL string literals against the real Select options on the referenced doctype — is the kind of check that catches defects nobody would otherwise find. The IST date fix and the report-batch timing fix are both things a client would have suffered silently.
- The defects found and fixed in the implementation report are real, and the candour about them is a strength worth keeping in front of the CA.
- The Setup Guide's dependency order, its "before you start" collection list, and the go-live checklist are good client material once Sanjay's name comes out of the owner column.
- Legal facts checked and correct as stated: the audit-trail rule from 1 Apr 2023, Rule 3(5) India backups, the ₹5 Cr e-invoice threshold, the ₹250 Cr Ind AS threshold, the SMC definition, the 25.168% arithmetic, 194C thresholds.

---

## E. The order to fix things in

**Before anyone outside sees the demo**

1. Placeholder GSTIN and director names; watermark the print formats *(A2)*
2. Rotate the Administrator password again; tighten session expiry and login attempts *(A1)*
3. Repair the demo story — either dispatch PROJ-0001 before commissioning it, or move the commissioning to a third, closing project; link DN-26-00001 to a project; submit or delete the dunning; repost retention against the right party *(A3, A4, A5)*
4. Reframe "97 of 97" as "our reading of your requirement document — correct us" *(C1)*

**Before any invoice or sign-off**

5. One page of signed scope: deliverables, milestones, fee, acceptance test *(C2)*
6. A support arrangement, or strike Sanjay's name from the client-facing owner columns *(C5)*
7. The discovery workshop that was skipped — the four real formats, and Q1–Q19 answered in writing *(C1)*

**Before go-live**

8. The CA session: WIP policy, tax regime, MSME rules, retention posting, GST treatment *(C6, B3, B5, B6)*
9. The custom app, the Git repo, fixtures, a staging site, a proven clean build *(C4)*
10. Test the controls that the SOPs promise are hard *(B1, B2)*
11. Migration plan, training material, restore test, named support contact, upgrade routine

---

# F. Status as at the evening of 20 September 2026

Added after the findings above were worked. **Nothing above has been edited.** This section says what happened to each.

## Closed

| Finding | What changed |
|---|---|
| **A2** — real GSTIN and real directors on a public demo | Shareholders are now `Promoter A / B / C`; client-facing print formats carry a demonstration watermark |
| **A6** — report counts wrong in the documents | 28 custom reports; every document now says 28, asserted by the census script |
| **B2** — "MSCAST Director is read-only, so every approval path is broken" | **The reviewer's premise was wrong, and this is worth recording.** `MSCAST Director` is the *approving* role and always was; the read-only role is `Auditor`, held by the external CA. No approval path was broken. The confusion came from the documents themselves, which had described the Director role as read-only — the documents were wrong, not the system |
| **C4** — no path from POC to production | `mscast_erp` is an installable app carrying every doctype, report, print format, workflow and control; the repository is `github.com/cb1-tech/mscast` at tagged release `v0.9.0`; fixtures are exported; the app reinstalls onto an empty site. The residual risk named in section 10 of the POC README is that `reset-poc.sh` has not been re-run end to end since the four most recent scripts joined it |
| **D** — "the 23-check harness" | Now **27 checks**: 25 pass, 2 warn, 0 fail |

## Confirmed, and worse than the reviewer knew

**B1 was right, and for a better reason than the one given.**

The reviewer flagged that the SOPs claimed a separation the system had never been tested for — specifically "the system will not let one person do both" — and noted the owner ≠ approver condition was untested. That test now exists, in two forms, and it found a real hole:

- **Purchase orders are genuinely separated.** Sending one for approval requires `Purchase User`; approving it requires `MSCAST Director`; nobody holds both. The SOP claim was true here.
- **Supplier bills are not.** Both directors hold `Projects Manager`, which can create a BRM, `MSCAST Director`, which certifies it, and `Accounts Manager`, which marks it paid. **One person can carry a supplier bill from creation to payment alone**, and three delivered documents said explicitly that this was impossible.

The first segregation check, `T6e`, did not catch it because it compares *workflow transition* roles, and creating a document is a permission rather than a transition. `T6g` was written to ask the question the way an auditor would and now reports it on every build. The three documents have been corrected, and the decision is put to MSCAST as **Q21** in the traceability matrix.

The payment block itself — the thing that actually protects the money — was tested and holds: no certified BRM, no payment, for anyone, including a director. The reviewer's other B1 sub-cases (journal-entry payments, advance payments with no invoice reference, partial certification) **remain untested** and are still worth doing.

## Still open, unchanged

- **A1** — the Administrator password has not been rotated again. A deliberate decision: this is a POC on a laptop. It becomes mandatory the moment the system moves to a server or carries real data.
- **A3, A4, A5** — the demo story contradictions, the draft dunning, and the retention posted against the wrong party. All still present. **A3 is the one most likely to be noticed in the room**, and it is a seeding fix, not a code fix.
- **B3 to B10** — none has been tested. They need the CA session and a day of ledger work.
- **C1, C2, C3, C5, C6** — every structural finding stands untouched. The four real formats and the CA answers are exactly what the Data Request Covering Note asks MSCAST for; **C2, the absence of a signed scope, remains the largest commercial exposure and is still fixable with one page.**

## What this review got right

Worth saying, because it is the argument for running one again. Of the findings that could be tested, the reviewer was right about the demo-story contradictions, the retention posting, the report counts, the GSTIN exposure and — most usefully — about a control being claimed and never tested. The one significant miss, **B2**, was caused by the documentation being wrong rather than by careless review.

Three of the fixes prompted by this review are now permanent automated checks rather than one-off corrections: `T6d` asserts the approval matrix, `T6f` reports who holds `System Manager`, and `T6g` reports who can create and then approve the same document. Findings that become tests do not come back.
