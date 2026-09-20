---
title: "MSCAST ERP — Standard Operating Procedures and Use Cases"
---

# MSCAST ERP — Standard Operating Procedures and Use Cases

**For:** MSCAST Engineering Pvt Ltd · **Version:** 2.2 · **Date:** 21 September 2026

> **What changed in version 2.0.** Version 1.0 was written before the roles were rebuilt around real people and before the approval authority was settled. It described some controls that the software did not actually enforce. Every claim in this version has been checked against the running system, and the ones that were not true have been either corrected or made true. The differences are listed in *Appendix — what changed and why*, at the end.

> **Correction, version 2.1 (20 September).** This document previously claimed a separation of duties that does not exist. It said the person who prepares a BRM cannot certify it, and that a supplier bill passes through three different hands. Neither is true: both directors hold roles that can *create* a BRM, the role that certifies one, and the role that marks it paid, so a director can carry a supplier bill from creation to payment alone. The build checks missed it because the segregation test compared workflow transition roles, and creating a document is a permission rather than a transition. A test that asks the auditor's question — can one person create this and then approve it? — now runs on every build (**T6g**) and reports it. The payment block itself is unaffected and still holds for everyone.

## How to read this

Part A gives one procedure per business process: what triggers it, who does it, the steps, and — most importantly — the **control**, meaning the thing that stops the process going wrong. Part B walks through nine situations that actually happen at MSCAST, showing how the pieces connect. Part C is who does what. Part D is the recurring calendar.

These procedures are written for an engineer-to-order machine builder with fewer than ten people, where fabrication is outsourced and one person often covers several roles. They assume the ERPNext configuration described in the setup guide.

Two phrases are used precisely throughout, and the difference matters:

- **The system will not allow** — a hard control built into the software. It cannot be skipped, forgotten or overridden under pressure.
- **The procedure is** — a way of working that depends on people following it. Valuable, but it is discipline, not enforcement.

Version 1.0 blurred these two. Where this version says a control is enforced, it has been tested.

## MSCAST's abbreviations

These are MSCAST's own terms, taken from the requirement document. They are used throughout this guide and are the names on the forms in the system.

| Term | Stands for | What it is |
|---|---|---|
| **PCC** | Purchase Cost Calculation | The cost estimate sheet for a machine, built component by component — bought-outs, fabrication, engineering hours, erection, freight, contingency. Prepared before quoting, carries revisions and an approval. Every purchase order is later measured against it, so it is the baseline for cost control and the project MIS |
| **MDF** | Material Data File | The material list per project or assembly, released by Design from the final drawings. What procurement buys from |
| **BRM** | Billing Routing Memo | The certificate that a supplier's bill is correct — quantity, rate, inspection and delivery all checked — before Accounts may pay it |
| **MDM** | Material Dispatch Memo | What physically goes out in a dispatch lot, including any free-issue items |
| **DI** | Delivery Instruction | The instruction to a supplier to ship directly to the customer's site: consignee, transporter, vehicle, LR number |
| **Annexure-I** | — | The free-issue material list attached to a Delivery Instruction: MSCAST's own material sitting with a subcontractor |
| **PBG / ABG** | Performance / Advance Bank Guarantee | Guarantees given to the customer, with expiry dates that must be tracked |
| **LD** | Liquidated Damages | The penalty for late delivery, usually a percentage per week capped at a maximum |
| **CCM** | Continuous Casting Machine | MSCAST's principal product |
| **ITC-04** | — | The GST return for goods sent to and received from job workers |
| **MSME** | Micro, Small and Medium Enterprise | Suppliers registered under Udyam. Their bills must be paid within 45 days or the expense is disallowed under section 43B(h) |

# Part A — Standard Operating Procedures

## SOP-01 — Enquiry to quotation

**Trigger:** Enquiry from IndiaMART, TradeIndia, email, exhibition or referral · **Owner:** Sales / Projects

1. Record the enquiry as a Lead the day it arrives, with the source. Source matters: it tells you which channel is worth the money.
2. Qualify it — machine type, capacity, site, budget, timeline — and convert to an Opportunity.
3. Raise a **PCC** for anything non-standard. Build it up component by component: bought-outs, fabrication, engineering hours, erection and commissioning, freight, contingency.
4. Apply the target margin and arrive at the offer price.
5. Send the PCC for approval and have it approved before the quotation goes out. Approval sits with a **director**.
6. Issue the Quotation referencing the PCC revision it was priced on.

**Control:** No quotation leaves without an approved PCC. Quoting from memory is how an engineer-to-order business loses money on a job it thought was profitable.

**A limit you should know about.** Both directors hold the Projects Manager role as well as the director role, so a director can prepare a PCC and then approve it. This is a deliberate decision for a company of this size, not an oversight — but it means the PCC approval is a *review step*, not a separation of duties. If the same person did both, the only safeguard is that the approval is recorded with their name and time against the revision. Where a PCC matters commercially, have the other director approve it.

**Records:** Lead, Opportunity, PCC with revision, Quotation.

## SOP-02 — Order booking and project kick-off

**Trigger:** Customer purchase order received · **Owner:** Projects, with Accounts

1. Raise a **Project Kick-off** record against the customer PO.
2. Work through the checklist, ticking only what has actually been verified:
   - Price matches the offer
   - Scope and technical specification match
   - Payment terms accepted
   - Delivery period acceptable
   - LD / penalty clause reviewed
   - GST rate, HSN and place of supply verified
   - BG / PBG requirement identified
   - Advance received
3. Anything that does not match goes in *deviations* and the record goes to **PO Query Raised** — work does not start.
4. Accounts verify the PO and the record moves to **PO Verified**. A **director** then approves kick-off.
5. Create the Project and the Sales Order, linked to the PCC.
6. Enter the billing and dispatch schedule on the project: each milestone, its planned dispatch date, billing percentage and value.
7. Hold the kick-off meeting and record attendees, agreed actions and open points.

**Control:** The workflow will not let a kick-off reach *PO Verified* — and therefore cannot let it be approved — while price, scope, payment terms and GST are unticked. **On every route**, including via *PO Query Raised*. This is the single highest-value control in the system — nearly every loss-making project in this industry traces back to a purchase order accepted without being read against the offer.

**The same limit as SOP-01 applies.** The directors also hold the Accounts Manager role, so a director can verify the customer PO and approve the kick-off. The checklist still has to be worked through and the answers are recorded, but two pairs of eyes are a practice here, not an enforcement. Anita in Accounts verifying the PO, and a director approving, is the stronger arrangement and is what should happen by default.

**Records:** Kick-off record, Project, Sales Order, billing schedule.

## SOP-03 — Engineering: drawings, revisions and transmittals

**Trigger:** Design release on a live project · **Owner:** Design, with Projects

1. Register every drawing: number, title, assembly, revision. A new drawing starts in **Draft**.
2. The drawing office issues it to the customer with **Issue for Customer Approval**; the drawing moves to **For Customer Approval**.
3. When the customer responds, a **Projects Manager** either records the approval (**Record Customer Approval** → *Approved by Customer*) or sends it back (**Return for Rework** → *Draft*).
4. A **Projects Manager** then uses **Release for Manufacture**. Only from *Approved by Customer*, and only by a Projects Manager.
5. Every issue to a customer, vendor or inspection agency goes out on a **Transmittal** listing document numbers, revisions, sheet counts and purpose (approval, construction, information, as-built).
6. Chase acknowledgement and record it. An unacknowledged transmittal is not proof of issue.
7. On revision: **Supersede** the old drawing, register and issue the new one on a fresh transmittal, and tell procurement in writing if material has already been ordered against it.
8. Release the **MDF** — the material list procurement buys from.

**Control:** *Released for Manufacture* can only be reached from *Approved by Customer*, and only by a Projects Manager. The drawing office can issue a drawing for customer approval but cannot release it for manufacture. A drawing cannot jump from Draft to Released, which is exactly the mistake that puts metal on the floor against a drawing the customer never saw.

**Records:** Drawing register with revision history, Transmittals with acknowledgements, MDF.

## SOP-04 — Procurement: requisition to purchase order

**Trigger:** MDF released, or a stock item reaching its reorder level · **Owner:** Purchase

1. Raise a Material Request from the MDF.
2. Issue an **RFQ** to at least three suppliers for anything material. One quotation is a price, not a comparison.
3. Record each Supplier Quotation with the technical score, compliance, deviations and delivery weeks — not only the price. The cheapest offer that does not comply is not the cheapest.
4. Compare against the **PCC budget** for that scope.
5. Raise the Purchase Order. If it exceeds the PCC line, record the justification — an alert goes to management.
6. The PO goes through approval: raised by Purchase, **approved by a director**. Purchase can reject a PO but cannot approve one.

**Control:** A purchase order commits MSCAST's money to an outside supplier, so it is approved by a director. **The person who raises a purchase order cannot approve it** — this is enforced, and it is checked automatically on every build. Purchase orders are also measured against the PCC continuously, not at the end of the job; the *PO vs PCC Variance* report is the early warning that a project is drifting while there is still time to act.

**Records:** Material Request, RFQ, Supplier Quotations with scoring, Purchase Order.

## SOP-05 — Free issue to subcontractors

**Trigger:** Material issued to a fabricator against a job · **Owner:** Stores

1. Transfer the material to that subcontractor's warehouse in the system — it remains MSCAST's stock, it has only moved.
2. Record it on the **Annexure-I** attached to the Delivery Instruction.
3. Track it on the *Free Issue at Vendor* report: what is lying where, and its value.
4. Reconcile on receipt of the fabricated item. Account for scrap and returns explicitly.

**Control:** Free-issue material stays on MSCAST's books and stays visible. Under GST, inputs sent to a job worker must return within one year (three for capital goods) or become a deemed supply — the report is what tells you before the deadline, not after.

**Records:** Stock transfer, Annexure-I, ITC-04 data.

## SOP-06 — Inspection and quality

**Trigger:** Manufacturing stage reached at a supplier or in-house · **Owner:** Quality / Projects

1. Raise an **Inspection Plan** per stage: in-process, pre-dispatch, third-party, customer.
2. Record the planned date, the inspector and the result: Pending, Accepted, Accepted with deviation, Rejected.
3. Deviations are recorded with what was accepted and who accepted it — never as a silent pass.
4. Rejections go back to the supplier with the observations, and the pre-dispatch inspection is repeated.

**Control:** The procedure is that no dispatch happens without a cleared pre-dispatch inspection, and the open inspection stages appear on the daily summary. This one depends on Stores checking before they dispatch — the software does not block the delivery note. A deviation accepted verbally and not recorded becomes the customer's warranty claim later, with nothing in writing to point to.

**Records:** Inspection Plan with result, Inspection Report print.

## SOP-07 — Supplier bill to payment (the BRM route)

**Trigger:** Supplier invoice received · **Owner:** Purchase prepares, a director certifies, Accounts pays

1. Purchase raises a **BRM** against the supplier bill.
2. Purchase checks and ticks: quantity, rate against the PO, inspection cleared, delivery received.
3. A **director** certifies it: status moves **Pending → Certified**. Purchase can reject a bill back to the supplier with the reason, but cannot certify one.
4. Accounts book the Purchase Invoice against the PO and receipt.
5. Accounts **Mark Paid** only against a **Certified** BRM.

**Control:** **The system will refuse a payment entry against a supplier bill that has no certified BRM.** It is not a policy that can be forgotten under pressure at month end — the payment is blocked and the reason is displayed. That block is real and applies to everyone.

**What the block does not do** is guarantee three different people were involved. Certification is restricted to a director — but both directors also hold the roles that can *create* a BRM and the role that marks one paid, so a director can carry a supplier bill from creation to payment alone. Sameer and Nikhil cannot: they prepare and they may reject, but they cannot certify. **So the separation is real for Purchase and absent for the directors**, and the honest instruction is the same as for the PCC: where the amount matters, have the other director certify it.

**Records:** BRM with certification, Purchase Invoice, Payment Entry.

## SOP-08 — Dispatch

**Trigger:** Material ready and inspection cleared · **Owner:** Stores

1. Raise the **MDM** for the lot: items, quantities, free-issue flags.
2. Raise the **Delivery Instruction** for direct-to-site dispatches: consignee, transporter, vehicle type, LR number, with Annexure-I for free-issue items.
3. Raise the Delivery Note and generate the **e-way bill** where the threshold applies. ODC movements need the vehicle and route recorded.
4. Update the milestone on the project's dispatch schedule.
5. Send the dispatch documents to the customer the same day.

**Control:** The procedure is that dispatch follows inspection, and that the dispatch schedule on the project is updated as it happens. Procurement and accounts both read from that schedule, so a stale one misleads two functions at once. The overnight checks flag a dispatch made before its commissioning or inspection record exists.

**Records:** MDM, Delivery Instruction with Annexure-I, Delivery Note, e-way bill.

## SOP-09 — Billing, retention and claims

**Trigger:** A billing milestone is reached · **Owner:** Accounts

1. Raise the Sales Invoice against the milestone on the billing schedule, with the correct GST treatment for the place of supply.
2. Where the contract holds retention, reclassify it out of trade receivables into **Retention Receivable** — it is not collectable until the performance certificate.
3. Record scope variations, idle time and escalation as **Client Claims** as they arise, not at the end. A claim raised six months late is a negotiation; raised the same week, it is a fact.
4. Settle an agreed claim by a **supplementary invoice** referencing it.
5. Follow up receivables against due dates. Send a payment reminder on anything overdue.

**Control:** Retention is visible as a separate asset with a release trigger. Money held back by customers is the most commonly forgotten asset in project businesses — it sits in receivables looking collectable, and nobody chases it because it is not yet due.

**Records:** Sales Invoice, retention journal, Client Claim, supplementary invoice.

## SOP-10 — Commissioning to project closure

**Trigger:** Machine erected at site · **Owner:** Site engineer, then Projects

1. Record the **Commissioning Report**: each performance parameter, specified versus achieved, trial runs, and the result — met, not met, or deviation accepted.
2. Record the punch list. Every open point, with who owns it.
3. Hand over spares on a **Spares Handover** note: commissioning spares and the two-year mandatory list, with part numbers.
4. Obtain the **Project Certificate** — provisional or final acceptance. The guarantee period starts here.
5. Release retention against the certificate.
6. Run the **Project Closure Report**: contract value versus PCC estimate versus actual cost, billed, collected, certificates, open claims, drawings and inspections outstanding. The report gives a closure verdict; a project with open claims or uncollected money is not closed.

**Control:** A project is closed on evidence, not on a feeling that the work is finished. Closure with an open claim means the claim is abandoned in practice.

**Records:** Commissioning Report, Spares Handover, Project Certificate, Closure Report.

## SOP-11 — Month-end close

**Trigger:** First working week of each month · **Owner:** Accounts, reviewed by the CA

1. Book all supplier invoices for the month. Anything received and not billed should be visible as such.
2. Reconcile the bank.
3. Reconcile GST: GSTR-2B against the purchase register using the reconciliation tool; resolve mismatches with suppliers before filing.
4. File GSTR-1 and GSTR-3B by their due dates.
5. Deposit TDS and reconcile the ledger.
6. Check the **MSME 45-day report**. Anything beyond 45 days is a section 43B(h) disallowance — pay it or accept the tax cost knowingly.
7. Update **project WIP**: cost incurred on unbilled scope.
8. Post provisions: depreciation, gratuity, and any known liabilities.
9. Review the Schedule III balance sheet and statement of profit and loss; confirm the trial balance nets to zero and the profit ties to the ledger.
10. Review the project MIS: contract value versus PCC versus committed versus billed, per project.

**Control:** The close follows the same sequence every month, and the Schedule III statements are produced monthly rather than once a year. Year-end surprises are almost always things that were visible monthly and nobody looked.

## SOP-12 — HR and payroll

**Trigger:** Monthly, plus events · **Owner:** HR

1. Record attendance. Where a biometric device is fitted and connected, punches are pulled automatically and converted to attendance; **this pull is currently switched off**, so until it is enabled and tested, attendance is entered in the system. Review exceptions weekly, not at month end when nobody remembers.
2. Leave applications are approved in the system before the leave is taken.
3. Run payroll: PF, ESIC, Professional Tax and TDS on salary computed from the salary structure.
4. Release salaries, then deposit the statutory dues by their due dates.
5. Maintain the gratuity provision annually at year end.
6. On exit, run full and final settlement: notice, leave encashment, gratuity where eligible, recovery of advances.

**Control:** Attendance feeds payroll directly, so the payroll is only as good as the attendance discipline. Duplicate attendance on the same day for the same employee is prevented. Fix attendance exceptions weekly and payroll takes an hour instead of a week.

## SOP-13 — Master data governance

**Trigger:** Any new customer, supplier or item · **Owner:** the function that owns the master

1. New customer: name, GSTIN, state, addresses and payment terms — before the first quotation, not before the first invoice.
2. New supplier: GSTIN, and **Udyam number with MSME class** where applicable. Ask in writing and keep the declaration.
3. New item: HSN/SAC and UOM at creation. An item without an HSN cannot be invoiced.
4. Duplicates are the enemy. Search before creating — "Suvarna Copper" and "Suvarna Copper Moulds Pvt Ltd" as two suppliers means two ledgers, two ageing lines and one wrong MSME position.

**Control:** GSTIN format and the state it implies are validated on entry, and an invoice line without an HSN is refused. The rest is procedure: masters are created by the function that owns them, not by whoever happens to be entering the transaction at the time.

## SOP-14 — The overnight checks and the morning note

**Trigger:** Automatic, every day · **Owner:** Directors read it; nobody has to run it

This is what the system does on its own before anyone logs in.

1. **06:00 — the checks run.** A set of rules compares documents against each other and against the calendar: a supplier bill with no certified BRM, an MSME bill approaching day 45, a bank guarantee approaching expiry, an open project with no time ever booked, a dispatch without its paperwork, and others. Anything found is written to the **MSCAST Exception** list with a severity, the document it concerns and the suggested action. No judgement, no internet, no cost — only rules.
2. **08:35 — the note is written.** The findings and the morning's management summary are turned into a few sentences that say which one matters most today, and emailed to the directors. Every item links to the document it came from.
3. **During the day.** Work the exception list. Mark an item **Acknowledged** when someone has picked it up, **Resolved** when the underlying document is fixed. Resolved items stop appearing.

**Control:** The checks are the safety net under every procedure in this document. They do not prevent a mistake; they make sure a mistake does not stay invisible for a month. If the model that writes the note is unreachable, the email still goes out as a plain list — a missing model never means a missing morning email.

**What to do with it:** read it, and act on anything marked High. If the same item appears for the sixth morning running, that is the system telling you a procedure is not being followed.

**Records:** MSCAST Exception list, the morning email.

## SOP-15 — Backups, audit trail and archival

**Trigger:** Daily, with an annual review · **Owner:** the implementation partner

1. Automated daily backup of database and files, with a copy held on a server physically in India.
2. Monthly archival record of what has been archived and where.
3. Retain books of account and vouchers for eight financial years; the audit trail likewise.
4. Test a restore annually. An untested backup is an assumption.
5. The audit trail stays on. It cannot be disabled, and that is deliberate.

# Part B — Use cases

## UC-1: An enquiry arrives from IndiaMART

A steel plant asks for a two-strand billet caster. Sales records the Lead with source *IndiaMART* the same day and qualifies it into an Opportunity. Design sizes the machine; Projects builds the **PCC** — copper moulds, hydraulics, drives, fabrication, engineering hours, erection, freight, contingency — and applies the target margin. The PCC goes for approval; a director approves revision 2. The quotation goes out referencing that revision.

Six weeks later the customer's purchase order arrives, and the story continues in UC-2.

*If the enquiry had been quoted from a spreadsheet, nobody would know six months later why the price was what it was, or which assumptions the margin depended on.*

## UC-2: The customer PO does not match the offer

The purchase order arrives. Projects raises a **Kick-off** record and works the checklist. Price matches, scope matches, GST is right — but the PO says 100% payment against delivery, where the offer said 30% advance, 60% against dispatch and 10% after commissioning.

The checkbox stays unticked, the record moves to **PO Query Raised**, and the workflow will not let kick-off be approved. Design release does not start. Accounts take it up with the customer's purchase head; an amendment arrives four days later and the record moves to *PO Verified*, then a director approves kick-off.

*Four days of delay, instead of discovering at dispatch that ₹60 lakh of cash flow assumed in the PCC was never going to arrive.*

## UC-3: A supplier bill arrives at month end

The fabricator's invoice for spray chamber work lands on the 29th, and the supplier is calling. Accounts cannot pay it: there is no certified BRM. Purchase check the quantity against the PO, the rate, the inspection result and the delivery — the quantity is short by one assembly still at the fabricator. The bill is rejected back to the supplier with the reason.

The balance arrives on the 3rd, the inspection clears, a director certifies the BRM, and Accounts release the payment.

*Without the block, the bill would have been paid on the 29th because the supplier was persistent and it was month end. The short delivery would have surfaced — if at all — when the assembly was needed.*

## UC-4: A drawing changes after material is ordered

The customer approves the general arrangement, then asks for a different mould tube length. The Projects Manager **supersedes** the drawing; the drawing office registers the revision and issues it, and it works through customer approval and **Release for Manufacture** again.

But the mould tubes were ordered against the previous revision. The drawing register shows the transmittal and its date; the purchase order references the superseded revision. Purchase go back to the supplier the same day — the tubes have not been cut. The revised requirement replaces them, and the cost difference is recorded as a **Client Claim** because the change came from the customer after approval.

*The claim is raised in the week it happened, with the drawing revisions and transmittal dates as evidence. Raised at the end of the project it would have been a conversation; raised now it is a document.*

## UC-5: An MSME supplier crosses day 40

The daily management summary shows *MSME dues due within the next 15 days: ₹7.80 L*. One supplier, a Small enterprise with a Udyam number, has a bill at day 31. It is on the morning note as a Medium-severity item, and it has appeared six mornings running.

Accounts check the MSME 45-day report, confirm the appointed date, and schedule the payment for day 42.

*Had it passed day 45, the expense would be disallowed under section 43B(h) in that year's assessment, and interest would be payable under section 16 of the MSMED Act. The cost of missing it is real money; the cost of catching it is reading one line of a daily email.*

## UC-6: Month end

First working week. Accounts book the remaining supplier invoices, reconcile the bank, and run GSTR-2B reconciliation — two invoices are missing from 2B and the suppliers are chased before filing. GSTR-1 and 3B are filed, TDS deposited.

The MSME report is clean. Project WIP is updated: ₹26.7 lakh of cost on unbilled scope carried forward. Depreciation and gratuity provisions are posted.

The Schedule III balance sheet is produced. It balances. The profit ties to the ledger. The CA logs in with a read-only account, reviews the trial balance and the ageing, and signs off.

*The close takes a day because it is the same sequence every month, and the statements are produced monthly rather than reconstructed in September for the year that ended in March.*

## UC-7: A new engineer joins

HR creates the Employee record on day one: joining date, department, designation, UAN, ESIC, PAN, bank. Attendance recording begins — automatically from the biometric device once that pull is enabled, and by entry until then. The salary structure is assigned.

The engineer gets a login on the Projects role — able to raise drawings, MDF and PCC, unable to approve a PCC, release a drawing for manufacture, approve a purchase order or certify a BRM.

At the first month end, payroll picks up the attendance and computes PF, ESIC, PT and TDS. The gratuity provision includes the new service from the year end.

*Nobody has to remember to add them to a payroll spreadsheet, and nobody has to decide what they are allowed to do — the role decides.*

## UC-8: The machine is commissioned

Six trial heats at the customer's plant. The site engineer records the **Commissioning Report**: casting speed achieved 2.6 m/min against 2.2–2.8 specified; billet surface accepted on six heats; water circuit pressure 7.6 bar against 8 bar specified — a deviation, accepted, because the limitation is the customer's pump.

Three punch points are recorded, one of them the customer's. **Spares** are handed over with part numbers. The customer issues the **Project Certificate** for provisional acceptance; the twelve-month guarantee starts from that date.

Retention of ₹1.81 lakh is released against the certificate. The **Project Closure Report** shows contract value against PCC estimate against actual cost, and flags one open claim — so the project is not closed yet.

*The deviation on water pressure is recorded, signed and attributable to the customer's pump. When a performance question arises in month eight, that record is the answer.*

## UC-9: A Tuesday morning

Aiqaz opens the email at 08:40. Four items. The note leads with a supplier bill for ₹2.86 L that has no certified BRM — Accounts cannot release it, and the supplier has been waiting.

Below that, three items flagged repeatedly: an MSME bill at day 31, a bank guarantee expiring in 39 days, and a project with no timesheets ever booked.

He clicks through to the BRM, checks it against the PO and the inspection, certifies it. Two minutes. He forwards the bank guarantee line to Anita. The timesheet item he takes up at the Monday meeting, because it has now appeared twice and that makes it a habit, not an oversight.

*Nothing here was discovered. Everything was already true yesterday. The difference is that it arrived in front of the person who could act on it, ranked, before the day started.*

# Part C — Who does what

**Every line below has been checked against the running system.** Where a column says *enforced*, the software refuses the action to anyone else. Where it says *practice*, it is how MSCAST works but the software would permit otherwise.

| Process | Prepares | Approves / certifies | Enforced? |
|---|---|---|---|
| PCC | Projects | **Director** | Enforced — but see the note below |
| Quotation | Sales / Projects | Against an approved PCC | Practice |
| Kick-off / PO check | Projects, verified by Accounts | **Director** | Enforced — but see the note below |
| Drawing → For Customer Approval | Design (drawing office) | — | Enforced |
| Drawing → Released for Manufacture | — | **Projects Manager** | Enforced |
| Purchase Order | Purchase | **Director** | Enforced, and the raiser cannot approve |
| Inspection | Quality | Third party, where specified | Practice |
| BRM certification | Purchase prepares | **Director** certifies | Enforced |
| Supplier payment | Accounts | Certified BRM required | Enforced — payment is blocked without one |
| Dispatch | Stores | Quality (pre-dispatch) | Practice |
| Sales Invoice | Accounts | Against the billing schedule | Practice |
| Client Claim | Projects | Accounts, then Director | Practice |
| Project closure | Projects | Director | Practice |
| Payroll | HR | Director | Practice |

## The separation of duties, stated honestly

The principle is that **the person who prepares a document should not be the person who approves it.**

Where this is fully true today:

- **Purchase Orders.** Sending a purchase order for approval requires `Purchase User`; approving it requires `MSCAST Director`. Nobody holds both, so a purchase order cannot reach approval without a second person. (One director does hold `Purchase Manager`, which can *create* a purchase order — but not move it forward, which is what matters here.)
- **The payment block itself.** No supplier bill can be paid without a certified BRM — not by a payment entry, not by a journal entry, and not as an advance with no invoice behind it. Paying more than the certificate covers is refused too. That is enforced in software, for everyone including a director, and it is the control that actually protects the money. The one exception is deliberate: a supplier ticked *Exempt from BRM certification*, for bills that cannot be certified against a purchase order — electricity, water, rent, telephone, statutory. Ticking a trade supplier defeats the control; see *Operating Recommendations* A8.
- **Drawing release.** The drawing office issues for approval; only a Projects Manager releases for manufacture.

Where it is **not** true, deliberately:

- **PCC approval** and **project kick-off**. Both directors hold the Projects Manager and Accounts Manager roles in addition to the director role, because in a company of this size they have to. A director can therefore prepare a PCC and approve it, or verify a customer PO and approve the kick-off, alone.

This is an accepted position, not an accident. It is written down here so that nobody — an auditor, a customer's procurement team, a new joiner — is told a control exists that does not. The mitigations are that every approval is recorded with a name and a timestamp against the revision, and that the second director can always be the approver when the commitment is significant. **Where a PCC or a kick-off carries real commercial exposure, have the other director approve it.**

## One more thing, for whoever administers the system

Everything above depends on people holding only the roles their job needs. Two accounts were found holding far more than that: the setup-wizard administrator with **41 roles**, and an ordinary staff account that also carried **System Manager** — which bypasses every control in this document. Both have been corrected, and the build checks now report it if it happens again.

This is worth knowing because it recurs. A fresh install creates its own administrator with the same spread of roles, and roles accumulate quietly on long-lived accounts. **A control environment is only as real as the role list behind it.**

# Part D — Recurring calendar

| When | What | Owner |
|---|---|---|
| Daily, automatic | Overnight checks run at 06:00; morning note emailed at 08:35 | *the system* |
| Daily | Read the morning note; act on anything marked High | Directors |
| Daily | Clear or acknowledge items on the exception list | The named owner |
| Daily | Read the management summary; act on anything marked ACT | Director |
| Daily | Enter transactions the day they happen | All |
| Weekly | Review attendance exceptions | HR |
| Weekly | Review drawings awaiting customer approval and chase | Design |
| Weekly | Review purchase orders against the PCC | Purchase |
| Weekly | Review any exception seen more than twice — it is a process problem, not a document problem | Directors |
| Monthly | GSTR-1, GSTR-3B, GSTR-2B reconciliation | Accounts |
| Monthly | TDS deposit and reconciliation | Accounts |
| Monthly | MSME 45-day review | Accounts |
| Monthly | Payroll and statutory dues | HR |
| Monthly | Project WIP update and MIS review | Accounts, Projects |
| Monthly | Archival record | Implementation partner |
| Quarterly | TDS returns; bank guarantee expiry review | Accounts |
| Annually | Gratuity provision; deferred tax; fixed asset verification | Accounts, CA |
| Annually | Physical stock count, including material at subcontractors | Stores |
| Annually | Test a backup restore | Implementation partner |
| Annually | Financial statements, Schedule III, notes to accounts, audit | Accounts, CA |

# Appendix — what changed in version 2.0, and why

Version 1.0 was written on 19 September, before the user roles were rebuilt around real people and before the approval authority was settled. An audit on 20 September compared every claim in it against the running system. These were wrong, and are now corrected:

| Version 1.0 said | Reality | Resolution |
|---|---|---|
| Purchase Orders are approved by the Purchase Manager | Approved by a director | **Doc corrected** |
| BRMs are certified by the Purchase Manager | Certified by a director | **Doc corrected** |
| Supplier payment needs Director approval above a threshold | No threshold is configured anywhere | **Claim removed.** The BRM certificate is the control, not a value threshold |
| Drawing status moves Draft → For Customer Approval → Released for Manufacture, and nothing is manufactured against an unreleased drawing | Status was a plain field. Any value could be set in any order, including Draft straight to Released | **System changed.** A workflow now enforces the sequence and restricts release to a Projects Manager |
| Attendance begins automatically from the biometric device | The biometric pull is switched off | **Doc corrected** to say attendance is entered until the pull is enabled and tested |
| "The person who prepares a document never approves it" | True for Purchase Orders and BRMs. Not true for PCC and kick-off — both directors hold the preparing roles as well as the director role | **Position stated openly** in Part C rather than claimed and untrue |
| — | The 06:00 overnight checks and the 08:35 morning note were not mentioned anywhere, despite being the daily operating rhythm | **SOP-14 added**, plus UC-9 and four calendar lines |
| — | Two accounts held roles far beyond their job, one of them bypassing every control in this document | **System corrected**, and a note added to Part C |

Added in **version 2.1**, and the most serious of the lot:

| Version 2.0 said | Reality | Resolution |
|---|---|---|
| "Purchase prepare, a director certifies, Accounts pay. Three different hands" | A director holds a role that can create a BRM, the role that certifies it, and the role that marks it paid. One person can do all three | **Claim removed**, and the real position stated in SOP-07 and Part C |
| "The person who prepares a BRM cannot certify it" | A director can | **Corrected** |
| "Purchase Orders … Nobody holds both roles" | One director holds `Purchase Manager`, which can create a purchase order. He cannot send it for approval — that needs `Purchase User`, which he does not hold — so the control survives, but the sentence was wrong | **Made precise** |

Four of these are now checked automatically on every build, so they cannot drift back silently: that the approval authority sits where the business put it, whether any ordinary user can both raise and approve the same document, and whether anyone outside the administrators holds System Manager.

## A closing note on discipline

Most of what is described here can be bypassed by someone determined enough. Four things cannot, because the software enforces them: the BRM payment block, the purchase order approval, the drawing release sequence, and the kick-off checklist. The payment block was narrowed to one route until 21 September, when it was tested at the others and found open at three of them; it now holds on every route a supplier can be paid by.

*(The kick-off checklist earned its place on that list only on 20 September. Until then the condition sat on one route into* PO Verified *and not the other, so raising a query first went round it — and a record in the demonstration data had already done exactly that. Both routes now carry it, and* `T6j` *checks that every guarded state in every workflow is guarded on every route in.)* Everything else depends on people entering documents when things happen rather than reconstructing them later.

The single habit that makes the difference is same-day entry. A system updated daily tells you the truth about the business; a system updated at month end tells you what somebody remembered.

The overnight checks exist because that habit slips. They will not stop a mistake — they will stop it staying invisible.
