---
title: "MSCAST ERP — Role Cards"
---

# MSCAST ERP — Role Cards

**For:** MSCAST Engineering Pvt Ltd · **Version:** 2.0 · **Date:** 21 September 2026

- One page per role. Print it, or keep it open for the first fortnight.
- Each card answers: **what you open**, **what you do**, **what you approve**, **what will stop you**.
- Cards are per role, not per person. At go-live only the names change.
- **Who holds this today** = the demo cast on **DEV** (mscastdev.carobar.net). Aiqaz and Mustaque Chandankeri are MSCAST's real directors; the other names are demo faces.
- **Live POC note:** as of 21 September 2026 the Live POC (mscast.carobar.net) carries MSCAST's own users (Mustaque@mcast.co.in, aiqaz@mcast.co.in, waseemraj@mcast.co.in) plus demo logins for Anita, Sameer and Rohit; the other demo personas were deleted there on 21 September 2026. On the Live POC the 08:35 IST morning note goes to waseemraj@mcast.co.in, by the owner's decision.
- If a card says you can do something and the system refuses, that is a defect — report it to the implementer. Build checks T6i (every role can raise what its card describes) and T6k (whoever approves a document can open it) test this on every build.

## The one rule behind all of it

- **The person who prepares a document is usually not the person who approves it.** If the system stops you, that is almost always why. It is not a permissions bug; do not ask for "just the access".
- The exceptions are the directors'; see Card 1.

---

# Card 1 — Director

**Who holds this today:** Aiqaz Chandankeri, Mustaque Chandankeri
**Role name in the system:** MSCAST Director

## What you open

- **The morning note**, emailed at 08:35 IST. It names the one thing that matters most today and links to the document. If you read nothing else, read this.
- **MSCAST Director** workspace for the numbers.
- **MSCAST Exception** for the full list of what the overnight checks found.

## What you do

| When | What |
|------------------------------|----------------------------------------------------------------------|
| Daily | Read the morning note. Act on anything marked **High** |
| Daily | Approve what is waiting: cost sheets, purchase orders, kick-offs, supplier bills |
| Weekly | Look at any exception that has appeared more than twice: a process not being followed |
| Monthly | Review the project MIS: contract value vs estimate vs committed vs billed |

## What you approve

Everything that commits MSCAST to someone outside the company:

- **PCC** (cost sheet) — before any quotation goes out
- **Purchase Order** — money committed to a supplier
- **Project Kick-off** — accepting a customer's order
- **BRM certification** — this releases a supplier payment
- **Send Back** on a cost sheet

## What will stop you

- **A purchase order reaches you only if someone holding `Purchase User` sent it** (Sameer or Nikhil). Neither director holds that role, so every PO involves two people.
- **No supplier bill can be paid without a certified BRM** — this applies to you too.
- **A BRM cannot be certified unless its four checks (quantity, rate, inspection, delivery) are ticked.**
- **A kick-off cannot be approved while the checklist is unticked.**

## What will not stop you — read this

- You hold more than the director role. Aiqaz holds nine roles, Mustaque seven. Both hold Projects Manager and Accounts Manager. Mustaque also holds Purchase Manager; Aiqaz also holds Quality Manager and Stock User.
- So, alone, you can:
  - prepare a cost sheet and approve it;
  - verify a customer PO and approve the kick-off;
  - create a BRM, certify it and mark it paid.
- This is an accepted decision for a company this size. These approvals are a second look, not a second pair of eyes. **Where the money is significant, the other director approves.** Every approval is recorded with name and time.

---

# Card 2 — Projects Manager

**Who holds this today:** Aiqaz Chandankeri, Mustaque Chandankeri
**Role name in the system:** Projects Manager

## What you open

**MSCAST Projects** workspace.

## What you do

| When | What |
|----------------------------------------|------------------------------------------------------------|
| On a new enquiry | Build the **PCC** component by component, then apply the margin |
| On a customer PO | Raise the **Project Kick-off** and work the checklist honestly |
| On kick-off approval | Create the Project and Sales Order; enter the billing and dispatch schedule |
| When the customer responds on a drawing | **Record Customer Approval**, or **Return for Rework** |
| Before manufacture | **Release for Manufacture** on the drawing |
| Weekly | Chase drawings sitting with the customer |
| As they arise | Raise **Client Claims** the week the event happens |

## What you approve

- **Record Customer Approval** and **Release for Manufacture** on drawings
- **Raise Query to Customer** and **Reopen** on a kick-off

## What will stop you

- **You cannot release a drawing for manufacture unless the customer approved it.** Draft cannot go straight to Released.
- **A kick-off cannot be approved while the checklist (price, scope, payment terms, GST) is unticked.** If the PO does not match the offer, leave the box unticked; the record stays in *PO Query Raised*.

---

# Card 3 — Purchase Manager

**Who holds this today:** Sameer Lokhande
**Role name in the system:** Purchase Manager

## What you open

**MSCAST Purchase** workspace.

## What you do

| When | What |
|---------------------------------------|-------------------------------------------------------------|
| On MDF release | Raise the Material Request |
| Before ordering | **RFQ to at least three suppliers** |
| On quotations | Record technical score, compliance, deviations and delivery weeks — not only price |
| Before the PO | Compare against the **PCC budget** for that scope |
| Raise the PO | If it exceeds the PCC line, record the justification |
| On a supplier bill | Raise the **BRM** and tick what you actually checked: quantity, rate, inspection, delivery |
| Weekly | Review the **PO vs PCC Variance** report |

## What you approve

- **Reject** on a purchase order
- **Reject** on a BRM — sends the bill back to the supplier with the reason

## What will stop you

- **You cannot approve a purchase order.** You raise it; a director approves. Checked on every build.
- **You cannot certify a BRM.** You prepare; a director certifies. The person who placed the order does not certify what he bought.
- A director cannot certify your BRM until all four checks are ticked.

---

# Card 4 — Purchase Executive

**Who holds this today:** Nikhil Sawant
**Role name in the system:** Purchase User

## What you open

**MSCAST Purchase** workspace.

## What you do

Raise Material Requests, issue RFQs, record supplier quotations, raise Purchase Orders, then **Send for Approval**.

## What you approve

Nothing. You prepare; others release.

## What will stop you

- **You cannot approve any purchase order**, including your own. Send it; a director approves.
- You cannot certify a BRM.
- If a supplier is pressing and the PO is not approved, chase the approval.

---

# Card 5 — Accounts Manager

**Who holds this today:** Anita Deshpande
**Role name in the system:** Accounts Manager

## What you open

**MSCAST Accounts** workspace.

## What you do

| When | What |
|-----------------------------------|-----------------------------------------------------------------|
| On a customer PO | **Verify Customer PO** on the kick-off: price, payment terms, GST, place of supply |
| On a certified BRM | Book the Purchase Invoice, then **Mark Paid** |
| On a milestone | Raise the Sales Invoice with the right GST treatment |
| Where retention applies | Reclassify it into **Retention Receivable** (not yet collectable) |
| Monthly | GSTR-1, GSTR-3B, GSTR-2B reconciliation; TDS; MSME 45-day review; WIP; Schedule III |
| Quarterly | TDS returns; bank guarantee expiry review |

## What you approve

- **Verify Customer PO** on a project kick-off
- **Mark Paid** on a certified BRM

## What will stop you

- **You cannot pay a supplier bill that has no certified BRM** — by Payment Entry or Journal Entry, as an advance, or above the certified amount. The entry is refused with the reason. No override, not at month end. If urgent, get the BRM certified.
- Only exception: suppliers ticked *Exempt from BRM certification* (utilities, rent, statutory). Not for trade suppliers; see doc 11, A8.
- You cannot approve the kick-off. You verify the PO; a director approves.

## The one to watch

**The MSME 45-day clock.** Past day 45 the expense is disallowed under section 43B(h) and interest is payable. It shows on the morning note well before then.

---

# Card 6 — Accounts Executive

**Who holds this today:** Kavita Joshi
**Role name in the system:** Accounts User

## What you open

**MSCAST Accounts** workspace.

## What you do

Enter supplier invoices against the PO and receipt. Prepare payments. Enter sales invoices against the billing schedule. Keep the ledger current — **same day, not month end**.

## What you approve

Nothing. You prepare; the Accounts Manager releases.

## What will stop you

- You cannot mark a payment as paid.
- The BRM block applies to you: an uncertified supplier bill cannot be paid, whoever enters it.

---

# Card 7 — Stores Officer

**Who holds this today:** Prashant More
**Role name in the system:** Stock User, Item Manager

## What you open

**MSCAST Stores** workspace.

## What you do

| When | What |
|--------------------------------|--------------------------------------------------------------------|
| Material in | Receipt it against the purchase order |
| Material to a fabricator | Transfer it to that subcontractor's warehouse (still MSCAST's stock) and record it on **Annexure-I** |
| On dispatch | Raise the **MDM**, the **DI** (Delivery Instruction), the Delivery Note and the e-way bill |
| After dispatch | Update the milestone on the project's dispatch schedule; send the documents to the customer the same day |
| Monthly | Check the **Free Issue at Vendor** report: what is where, and its value |

## What you approve

Nothing. Dispatch paperwork and free-issue records depend on your accuracy.

## What will stop you

- The system does not block a dispatch before inspection. **Do not dispatch before the pre-dispatch inspection is cleared.**
- The overnight checks flag a dispatch with missing paperwork; it reaches a director the next morning.

## The one to watch

**Free-issue material at subcontractors.** Under GST it must return within 1 year (3 years for capital goods) or it becomes a deemed supply. The report warns before the deadline. Nobody else watches this.

---

# Card 8 — Design Draughtsman

**Who holds this today:** Meera Rane
**Role name in the system:** Design User

## What you open

**MSCAST Projects** workspace → Drawings.

## What you do

| When | What |
|----------------------------------|------------------------------------------------------------------|
| On design release | Register the drawing: number, title, assembly, revision. It starts in **Draft** |
| When ready for the customer | **Issue for Customer Approval** |
| Every issue out | Raise a **Transmittal**: document numbers, revisions, sheet counts, purpose |
| After issuing | **Chase the acknowledgement and record it.** Unacknowledged is not proof of issue |
| On revision | Register the new revision; issue it on a fresh transmittal |
| After final drawings | Release the **MDF** — the list procurement buys from |
| Weekly | Chase anything sitting with the customer |

## What you approve

**Issue for Customer Approval** on a drawing.

## What will stop you

- **You cannot release a drawing for manufacture.** A Projects Manager records the customer's approval and releases it.
- You cannot supersede a released drawing.

## Why transmittals matter

When a project runs late, a dated, acknowledged transmittal shows whose delay it was. Without one, the delay is MSCAST's by default.

---

# Card 9 — Quality / Inspection

**Who holds this today:** Ganesh Pawar (Quality Manager), Vinod Shelke (inspection recording)
**Role names in the system:** Quality Manager, Projects User

## What you open

**MSCAST Quality** workspace.

## What you do

| When | What |
|---------------------------------------|-------------------------------------------------------------|
| Per manufacturing stage | Raise an **Inspection Plan**: in-process, pre-dispatch, third-party, customer |
| On inspection | Record the planned date, the inspector and the result |
| On a deviation | Record **what was accepted and who accepted it** — never a silent pass |
| On rejection | Back to the supplier with the observations; repeat the pre-dispatch inspection |
| At commissioning | Record the **Commissioning Report**: every parameter, specified vs achieved |

## What you approve

Inspection results, including accepting a deviation.

## What will stop you

Nothing in the software. This role runs on discipline.

## The one to watch

**Write down every accepted deviation**: what was out of spec, by how much, who accepted it, why. A verbal acceptance becomes a warranty claim in month 8 with nothing to point to. Example: the water-pressure deviation on a commissioned machine, recorded on the day as caused by the customer's pump.

---

# Card 10 — Chartered Accountant (external)

**Who holds this today:** S. Joshi
**Role name in the system:** Auditor

## What you open

Anything. Read access across the books.

## What you do

At each month end, review the trial balance, Schedule III statements, ageing and GST position. Sign off the close.

## What will stop you

- **You cannot change anything.** Both auditor roles are read-only everywhere; build check T6h asserts it on every build.
- If something needs correcting, send it back to Accounts with a note.
- Nobody can switch off the audit trail.

---

# Appendix A — What each role can and cannot do, on one page

| | Director | Projects Mgr | Purchase Mgr | Purchase Exec | Accounts Mgr | Accounts Exec | Stores | Design | Quality | CA |
|------------|----------|----------|----------|----------|----------|----------|--------|--------|---------|-----|
| Prepare a PCC | ● | ● | | | | | | | | |
| **Approve a PCC** | **●** | | | | | | | | | |
| Raise a Purchase Order | | | ● | ● | | | | | | |
| **Approve a Purchase Order** | **●** | | | | | | | | | |
| Reject a Purchase Order | ● | | ● | | | | | | | |
| Prepare a BRM | ● | | ● | ● | | | | | | |
| **Certify a BRM** | **●** | | | | | | | | | |
| **Mark a supplier bill paid** | **●** | | | | **●** | | | | | |
| Verify a customer PO | ● | | | | ● | | | | | |
| **Approve a kick-off** | **●** | | | | | | | | | |
| Issue a drawing for approval | | | | | | | | ● | | |
| **Release a drawing for manufacture** | ● | **●** | | | | | | | | |
| Dispatch | | | | | | | ● | | | |
| Record an inspection result | ● | ● | | | | | | | ● | |
| Read everything | ● | | | | | | | | | ● |
| Change anything | | | | | | | | | | ✗ |

Bold = enforced by the software. Everything else is how MSCAST works. Directors can prepare a BRM through the roles they also hold (Card 1).

# Appendix B — The things the software will refuse

Know these; hitting one without warning is alarming, and the reason is always good.

1. **A supplier bill with no certified BRM cannot be paid** — by Payment Entry or Journal Entry, as an advance, or above the certified amount. Not by anyone. Only suppliers ticked *Exempt from BRM certification* (utilities, rent, statutory) are outside this.
2. **A BRM cannot be certified unless its four checks (quantity, rate, inspection, delivery) are ticked.**
3. **A purchase order cannot be approved unless someone holding `Purchase User` sent it.** Directors do not hold that role, so a PO always involves two people.
4. **A drawing cannot be released for manufacture unless the customer approved it**, and only a Projects Manager can release it.
5. **A project kick-off cannot be approved while the PO checklist is incomplete.**

Not on this list: **preparing and certifying a BRM are not separated for the directors.** They are separated for Purchase (Sameer and Nikhil prepare and may reject, but cannot certify). See Card 1.

# Appendix C — For the implementer

## Administrator and System Manager

- `admin@mscast.local` holds `System Manager` and nothing else.
- No operational account may hold `System Manager`; it bypasses every control (payment block, PO approval, drawing release).
- A fresh production install recreates the setup-wizard administrator with every manager role. Cutting it back is line 15 of the go-live checklist (doc 05).
- Build check T6f reports any non-administrator holding `System Manager`. On the Live POC (21 September 2026) it warns: MSCAST's trial admin gave Aiqaz Chandankeri `System Manager`.

## Where the rules live

- Business rules (who may approve what) and permissions ship in the packaged app `mscast_erp`, not in the screens.
- **A workflow role changed through the ERPNext interface is reverted at the next upgrade.** Change it in the package and deploy.
- After every deploy the system checks the approval authority and prints a warning if it repaired anything.
- A fresh install ships the *Design User* role and the auditor's read access in the package.

## Before real data

- **Administrator password:** rotate before the system carries real data or moves to a server. Parked by the owner until then.
- **Biometric attendance pull:** switched off. Enable it and prove it against manually checked attendance before payroll relies on it.
