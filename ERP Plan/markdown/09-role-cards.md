---
title: "MSCAST ERP — Role Cards"
---

# MSCAST ERP — Role Cards

**For:** MSCAST Engineering Pvt Ltd · **Version:** 1.3 · **Date:** 20 September 2026

One page per role. Print it, or keep it open for the first fortnight.

Each card answers four questions: **what you open**, **what you do**, **what you can approve**, and **what will stop you** — because being blocked by the system without knowing why is the fastest way to lose someone's trust in it.

> **Corrected in version 1.2.** The Director card previously said the directors hold two extra roles and that purchase orders and BRMs were fully separated. Both were wrong — see that card. A build check (**T6g**) now reports this rather than leaving it to be discovered.

> **Corrected in version 1.3.** An audit on 20 September found that four of the people named below could not do the work their card describes. `Design User` held no permissions anywhere in the system, so the drawing office could not open a drawing, and *Issue for Customer Approval* was executable by nobody at all; Stores, Quality and the Purchase Executive were in the same position on their own documents. The system has been corrected to match these cards rather than the cards softened to match the system, and `T6i` now checks it on every build. If a card says you can raise something and the system refuses, that is a defect — report it.

Cards are written **per role**, not per person, because roles outlive people. The *Who holds this today* line names the accounts set up in the demo system; when MSCAST's real staff are loaded, only those names change.

> **A note on the names below.** Aiqaz Chandankeri and Mustaque Chandankeri are MSCAST's directors. The remaining names are staff accounts created for the demonstration so that every role has a face. They will be replaced with real people at go-live.

## The one rule behind all of it

**The person who prepares a document is usually not the person who approves it.** If the system stops you doing something, that is almost always why. It is not a permissions bug, and asking someone to "just give me the access" defeats the point of having it.

Two exceptions are deliberate and are described on the Director card.

---

# Card 1 — Director

**Who holds this today:** Aiqaz Chandankeri, Mustaque Chandankeri
**Role name in the system:** MSCAST Director

## What you open

**Your email, at 08:40.** The morning note is the job. It arrives every day, names the one thing that matters most, and links straight to the document. If you read nothing else in the system, read this.

Then **MSCAST Director** workspace for the numbers, and **MSCAST Exception** for the full list of what the overnight checks found.

## What you do

| When | What |
|---|---|
| Daily | Read the morning note. Act on anything marked **High** |
| Daily | Approve what is waiting: cost sheets, purchase orders, kick-offs, supplier bills |
| Weekly | Look at any exception that has appeared more than twice. That is a process not being followed, not a document needing fixing |
| Monthly | Review the project MIS: contract value against estimate against committed against billed |

## What you approve

You are the approval on everything that commits MSCAST to someone outside the company:

- **PCC** (cost sheet) — before any quotation goes out
- **Purchase Order** — money committed to a supplier
- **Project Kick-off** — accepting a customer's order
- **BRM certification** — this is what releases a supplier payment
- **Send Back** on a cost sheet

## What will stop you

Very little — and that is the point of the two exceptions below.

**Read this part.** You hold a good deal more than the director role — Aiqaz holds nine roles and Mustaque seven, and they are not the same seven. Both of you hold Projects Manager and Accounts Manager, because in a company this size you have to. Mustaque also holds Purchase Manager; Aiqaz also holds Quality Manager and Stock User.

What that adds up to:

- **You can prepare a cost sheet and then approve it yourself.**
- **You can verify a customer PO and then approve the kick-off yourself.**
- **You can create a supplier-bill certificate, certify it, and mark it paid** — all three, alone, with nobody else involved.

The system permits all of it. That is an accepted decision for a company this size, not an oversight — but it means these are a second look, not a real second pair of eyes. **Where the money is significant, have the other director do the approving.** Every approval is recorded with your name and the time, so who approved what is never in doubt.

One thing genuinely is enforced: **a purchase order cannot reach you for approval unless somebody holding `Purchase User` sent it** — Sameer or Nikhil. Neither of you holds that role, so purchase orders always involve two people. And **no bill of any kind can be paid without a certified BRM**, which applies to you as much as to anyone.

---

# Card 2 — Projects Manager

**Who holds this today:** Aiqaz Chandankeri, Mustaque Chandankeri
**Role name in the system:** Projects Manager

## What you open

**MSCAST Projects** workspace.

## What you do

| When | What |
|---|---|
| On a new enquiry | Build the **PCC** — component by component, then apply the margin |
| On a customer PO | Raise the **Project Kick-off** and work the checklist honestly |
| On kick-off approval | Create the Project and Sales Order; enter the billing and dispatch schedule |
| When the customer responds on a drawing | **Record Customer Approval**, or **Return for Rework** |
| Before manufacture | **Release for Manufacture** on the drawing |
| Weekly | Chase drawings sitting with the customer |
| As they arise | Raise **Client Claims** the week the event happens, not at the end |

## What you approve

- **Record Customer Approval** and **Release for Manufacture** on drawings
- **Raise Query to Customer** and **Reopen** on a kick-off

## What will stop you

- **You cannot release a drawing for manufacture unless the customer has approved it.** A drawing cannot go from Draft straight to Released. This is the control that stops metal being cut against a drawing the customer never saw.
- **A kick-off will not be approved while the checklist is unticked** — price, scope, payment terms, GST. If the customer's PO does not match the offer, leave the box unticked and let it sit in *PO Query Raised*. Four days of delay now beats discovering at dispatch that the advance was never coming.

---

# Card 3 — Purchase Manager

**Who holds this today:** Sameer Lokhande
**Role name in the system:** Purchase Manager

## What you open

**MSCAST Purchase** workspace.

## What you do

| When | What |
|---|---|
| On MDF release | Raise the Material Request |
| Before ordering | **RFQ to at least three suppliers.** One quotation is a price, not a comparison |
| On quotations | Record the technical score, compliance, deviations and delivery weeks — not only price |
| Before the PO | Compare against the **PCC budget** for that scope |
| Raise the PO | If it exceeds the PCC line, record the justification |
| On a supplier bill | Raise the **BRM** and tick what you have actually checked: quantity, rate, inspection, delivery |
| Weekly | Review the **PO vs PCC Variance** report |

## What you approve

- **Reject** on a purchase order
- **Reject** on a BRM — sending a bill back to the supplier with the reason

## What will stop you

- **You cannot approve a purchase order.** You raise it, a director approves it. This is enforced and it is checked automatically on every system update.
- **You cannot certify a BRM.** You prepare it; a director certifies it. Certifying is what releases the money, and the person who placed the order must not be the person who certifies what he himself bought.

You can still stop a bad bill — **Reject** is yours. Stopping something is safe; releasing money is not.

---

# Card 4 — Purchase Executive

**Who holds this today:** Nikhil Sawant
**Role name in the system:** Purchase User

## What you open

**MSCAST Purchase** workspace.

## What you do

Raise Material Requests, issue RFQs, record supplier quotations, and raise Purchase Orders. Then **Send for Approval**.

## What you approve

Nothing. You prepare; others release.

## What will stop you

- **You cannot approve your own purchase order**, or anyone else's. Send it for approval and it goes to a director.
- You cannot certify a BRM.

If a supplier is pressing and the PO is not approved yet, the answer is to chase the approval — not to find a way round it.

---

# Card 5 — Accounts Manager

**Who holds this today:** Anita Deshpande
**Role name in the system:** Accounts Manager

## What you open

**MSCAST Accounts** workspace.

## What you do

| When | What |
|---|---|
| On a customer PO | **Verify Customer PO** on the kick-off — price, payment terms, GST, place of supply |
| On a certified BRM | Book the Purchase Invoice, then **Mark Paid** |
| On a milestone | Raise the Sales Invoice with the right GST treatment |
| Where retention applies | Reclassify it into **Retention Receivable** — it is not collectable yet |
| Monthly | GSTR-1, GSTR-3B, GSTR-2B reconciliation; TDS; MSME 45-day review; WIP; Schedule III |
| Quarterly | TDS returns and the bank guarantee expiry review |

## What you approve

- **Verify Customer PO** on a project kick-off
- **Mark Paid** on a certified BRM

## What will stop you

- **You cannot pay a supplier bill that has no certified BRM.** The payment entry is refused and the reason is shown. This is the hardest control in the system and it cannot be overridden — not at month end, not when the supplier is calling. If the payment is genuinely urgent, get the BRM certified; do not look for another route.
- You cannot approve the kick-off itself. You verify the PO; a director approves.

## The one to watch

**The MSME 45-day clock.** Past day 45 the expense is disallowed under section 43B(h) and interest is payable. It shows on the morning note well before then. Catching it costs one line of reading; missing it costs real money.

---

# Card 6 — Accounts Executive

**Who holds this today:** Kavita Joshi
**Role name in the system:** Accounts User

## What you open

**MSCAST Accounts** workspace.

## What you do

Enter supplier invoices against the PO and the receipt. Prepare payments. Enter sales invoices against the billing schedule. Keep the ledger current — **same day, not month end**.

## What you approve

Nothing. You prepare; the Accounts Manager releases.

## What will stop you

- You cannot mark a payment as paid.
- The BRM block applies to you too: an uncertified supplier bill cannot be paid, whoever enters it.

---

# Card 7 — Stores Officer

**Who holds this today:** Prashant More
**Role name in the system:** Stock User, Item Manager

## What you open

**MSCAST Stores** workspace.

## What you do

| When | What |
|---|---|
| Material in | Receipt it against the purchase order |
| Material to a fabricator | Transfer it to that subcontractor's warehouse — **it is still MSCAST's stock, it has only moved** — and record it on **Annexure-I** |
| On dispatch | Raise the **MDM**, the **Delivery Instruction**, the Delivery Note and the e-way bill |
| After dispatch | Update the milestone on the project's dispatch schedule, and send the documents to the customer the same day |
| Monthly | Check the **Free Issue at Vendor** report: what is lying where, and what it is worth |

## What you approve

Nothing, but two things depend entirely on you being accurate.

## What will stop you

The system will not physically stop you dispatching before inspection — but **do not**. Pre-dispatch inspection first, always. The overnight checks will flag a dispatch whose paperwork is missing, and it will be on a director's screen the next morning.

## The one to watch

**Free-issue material at subcontractors.** Under GST it must come back within one year, or three for capital goods, or it becomes a deemed supply. The report tells you before the deadline. Nobody else is watching this.

---

# Card 8 — Design Draughtsman

**Who holds this today:** Meera Rane
**Role name in the system:** Design User

## What you open

**MSCAST Projects** workspace → Drawings.

## What you do

| When | What |
|---|---|
| On design release | Register the drawing: number, title, assembly, revision. It starts in **Draft** |
| When ready for the customer | **Issue for Customer Approval** |
| Every issue out | Raise a **Transmittal** — document numbers, revisions, sheet counts, purpose |
| After issuing | **Chase the acknowledgement and record it.** An unacknowledged transmittal is not proof of issue |
| On revision | Register the new revision and issue it on a fresh transmittal |
| After final drawings | Release the **MDF** — the list procurement buys from |
| Weekly | Chase anything sitting with the customer |

## What you approve

**Issue for Customer Approval** on a drawing.

## What will stop you

- **You cannot release a drawing for manufacture.** You can issue it to the customer; a Projects Manager records the customer's approval and releases it. That separation is the control.
- You cannot supersede a released drawing yourself.

## Why the transmittal discipline matters

When a project runs late, the question is always whose delay it was. A transmittal with a date and an acknowledgement is the answer. Without it, the delay is MSCAST's by default.

---

# Card 9 — Quality / Inspection

**Who holds this today:** Ganesh Pawar (Quality Manager), Vinod Shelke (inspection recording)
**Role names in the system:** Quality Manager, Projects User

## What you open

**MSCAST Quality** workspace.

## What you do

| When | What |
|---|---|
| Per manufacturing stage | Raise an **Inspection Plan**: in-process, pre-dispatch, third-party, customer |
| On inspection | Record the planned date, the inspector, and the result |
| On a deviation | Record **what was accepted and who accepted it** — never a silent pass |
| On rejection | Back to the supplier with the observations; repeat the pre-dispatch inspection |
| At commissioning | Record the **Commissioning Report**: every parameter, specified against achieved |

## What you approve

Inspection results, including accepting a deviation.

## What will stop you

Nothing in the software — this role runs on discipline. Which is exactly why the next line matters.

## The one to watch

**A deviation accepted verbally and not written down becomes a warranty claim in month eight with nothing to point to.** Record it: what was out of spec, by how much, who accepted it, and why. The water-pressure deviation on a commissioned machine was the customer's own pump — that sentence, recorded on the day, is worth more later than any amount of recollection.

---

# Card 10 — Chartered Accountant (external)

**Who holds this today:** S. Joshi
**Role name in the system:** Auditor

## What you open

Anything. You have read access across the books.

## What you do

Review the trial balance, the Schedule III statements, the ageing and the GST position at each month end. Sign off the close.

## What will stop you

**You cannot change anything.** The account is read-only by design, so an external reviewer can never alter a record. *This was checked on 20 September and was not true at the time — the role could write and create on two GST documents, and delete records from the exception log. Both auditor roles are now read-only everywhere, and* `T6h` *asserts it on every build.* If something needs correcting, it goes back to Accounts with a note.

The audit trail cannot be switched off, by anyone. That is deliberate.

---

# Appendix A — What each role can and cannot do, on one page

| | Director | Projects Mgr | Purchase Mgr | Purchase Exec | Accounts Mgr | Accounts Exec | Stores | Design | Quality | CA |
|---|---|---|---|---|---|---|---|---|---|---|
| Prepare a PCC | ● | ● | | | | | | | | |
| **Approve a PCC** | **●** | | | | | | | | | |
| Raise a Purchase Order | | | ● | ● | | | | | | |
| **Approve a Purchase Order** | **●** | | | | | | | | | |
| Reject a Purchase Order | ● | | ● | | | | | | | |
| Prepare a BRM | | | ● | ● | | | | | | |
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

Bold entries are the ones the software enforces. Everything else is how MSCAST works.

# Appendix B — The three things the software will simply refuse

Everyone should know these, because hitting one of them without warning is alarming, and the reason is always good.

1. **A supplier bill with no certified BRM cannot be paid.** Not by anyone, not at month end, not under pressure from the supplier. Get the BRM certified.
2. **A purchase order cannot be approved unless someone holding `Purchase User` sent it for approval.** Directors do not hold that role, so a purchase order always passes through two people.
3. **A drawing cannot be released for manufacture unless the customer has approved it.** And only a Projects Manager can release it.

One thing that is *not* on this list, and was wrongly claimed to be: **preparing a BRM and certifying it are not separated for the directors.** They are for Purchase — Sameer and Nikhil prepare and may reject, but cannot certify. See the Director card.

Plus one that blocks a workflow rather than refusing outright:

4. **A project kick-off cannot be approved while the checklist is unticked.** If the customer's PO does not match the offer, that is the system doing its most valuable job.

# Appendix C — For the implementation partner

## Two accounts that held far more than they should — now fixed

Version 1.0 of this document said the demonstration administrator held fourteen roles. That was wrong, and the real number is worth recording because it is the kind of thing that accumulates quietly on any ERP.

**`admin@mscast.local` held 41 roles** — every manager role in the system plus a good deal it had no use for. It had never logged in and had never created a document. Forty-one roles on an unused account is not untidy; it means every separation described in these cards had an exception nobody had written down, and whoever got that password got all of it. **It now holds System Manager and nothing else.**

Auditing that turned up a second and worse one. **An operational staff account — Item Manager, Projects User, Stock User — also held `System Manager`**, which bypasses every control in the system: the payment block, the purchase order approval, the drawing release sequence, all of it. **Removed.**

Nothing had reported either, and the reason is worth understanding. The segregation check deliberately excludes System Manager holders, because someone who can do anything is not a meaningful segregation breach. That exclusion is correct — and it is also a blind spot: an ordinary user carrying System Manager vanishes from the check entirely while being able to approve anything. The build checks now report that exclusion rather than hiding it.

**On a fresh production install, both will happen again.** The setup wizard creates its own administrator with the same spread of roles. Cutting it back is line 15 of the go-live checklist, and the build checks will tell you if an operational account picks up System Manager later.

## Where the rules live

Business rules — who may approve what — live in the packaged app, not in the screens. **Changing a workflow role through the ERPNext interface will be reverted at the next upgrade.** If an approval needs to change, it changes in the package and is deployed. After every deploy the system checks the approval authority and prints a warning if it had to repair anything.

## Still to do before real data

- The **Administrator password** should be rotated before the system carries real data. On the POC laptop it does not matter; on a server it does.
- The **biometric attendance pull is switched off**. Enable it and prove it against manually checked attendance before payroll relies on it.
