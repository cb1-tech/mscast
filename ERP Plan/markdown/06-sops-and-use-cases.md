---
title: "MSCAST ERP — Standard Operating Procedures and Use Cases"
---

# MSCAST ERP — Standard Operating Procedures and Use Cases

**For:** MSCAST Engineering Pvt Ltd · **Version:** 1.0 · **Date:** 19 September 2026

## How to read this

Part A gives one procedure per business process: what triggers it, who does it, the steps, and — most importantly — the **control**, meaning the thing that stops the process going wrong. Part B walks through eight situations that actually happen at MSCAST, showing how the pieces connect. Part C is who does what. Part D is the recurring calendar.

These procedures are written for an engineer-to-order machine builder with fewer than ten people, where fabrication is outsourced and one person often covers several roles. They assume the ERPNext configuration described in the setup guide.

Where a procedure says **the system will not allow**, that is a hard control built into the software, not a policy someone can decide to skip.

## MSCAST's abbreviations

These are MSCAST's own terms, taken from the requirement document. They are used throughout this
guide and are the names on the forms in the system.

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
5. Get the PCC approved before the quotation goes out. The approval workflow requires someone other than the preparer.
6. Issue the Quotation referencing the PCC revision it was priced on.

**Control:** No quotation leaves without an approved PCC. Quoting from memory is how an engineer-to-order business loses money on a job it thought was profitable.

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
4. Once Accounts verify the PO, the record moves to **PO Verified**, then a director approves kick-off.
5. Create the Project and the Sales Order, linked to the PCC.
6. Enter the billing and dispatch schedule on the project: each milestone, its planned dispatch date, billing percentage and value.
7. Hold the kick-off meeting and record attendees, agreed actions and open points.

**Control:** The workflow will not let a kick-off be approved while price, scope, payment terms and GST are unticked. This is the single highest-value control in the system — nearly every loss-making project in this industry traces back to a purchase order accepted without being read against the offer.

**Records:** Kick-off record, Project, Sales Order, billing schedule.

## SOP-03 — Engineering: drawings, revisions and transmittals

**Trigger:** Design release on a live project · **Owner:** Design

1. Register every drawing: number, title, assembly, revision.
2. Status moves **Draft → For Customer Approval → Approved by Customer → Released for Manufacture**, and **Superseded** when replaced.
3. Every issue to a customer, vendor or inspection agency goes out on a **Transmittal** listing document numbers, revisions, sheet counts and purpose (approval, construction, information, as-built).
4. Chase acknowledgement and record it. An unacknowledged transmittal is not proof of issue.
5. On revision: supersede the old drawing, issue the new one on a fresh transmittal, and tell procurement in writing if material has already been ordered against it.
6. Release the **MDF** — the material list procurement buys from.

**Control:** Nothing is manufactured against a drawing that is not *Released for Manufacture*. Drawings awaiting customer approval appear on the daily summary, because they are the most common cause of schedule slip and the delay belongs to the customer, not to MSCAST — provided you can show when it was issued.

**Records:** Drawing register with revision history, Transmittals with acknowledgements, MDF.

## SOP-04 — Procurement: requisition to purchase order

**Trigger:** MDF released, or a stock item reaching its reorder level · **Owner:** Purchase

1. Raise a Material Request from the MDF.
2. Issue an **RFQ** to at least three suppliers for anything material. One quotation is a price, not a comparison.
3. Record each Supplier Quotation with the technical score, compliance, deviations and delivery weeks — not only the price. The cheapest offer that does not comply is not the cheapest.
4. Compare against the **PCC budget** for that scope.
5. Raise the Purchase Order. If it exceeds the PCC line, record the justification — an alert goes to management.
6. The PO goes through approval: raised by Purchase, approved by the Purchase Manager. The system will not let one person do both.

**Control:** Purchase orders are measured against the PCC, continuously, not at the end of the job. The *PO vs PCC Variance* report is the early warning that a project is drifting, while there is still time to act.

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

**Control:** No dispatch without a cleared pre-dispatch inspection. A deviation accepted verbally and not recorded becomes the customer's warranty claim later, with nothing in writing to point to.

**Records:** Inspection Plan with result, Inspection Report print.

## SOP-07 — Supplier bill to payment (the BRM route)

**Trigger:** Supplier invoice received · **Owner:** Purchase certifies, Accounts pays

1. Purchase raises a **BRM** against the supplier bill.
2. Purchase checks and ticks: quantity, rate against the PO, inspection cleared, delivery received.
3. Status moves **Pending → Certified**. Rejected bills go back to the supplier with the reason.
4. Accounts book the Purchase Invoice against the PO and receipt.
5. Accounts pay only against a **Certified** BRM.

**Control:** **The system will refuse a payment entry against a supplier bill that has no certified BRM.** It is not a policy that can be forgotten under pressure at month end — the payment is blocked and the reason is displayed. This is the control that separates "we checked it" from "we can prove we checked it".

**Records:** BRM with certification, Purchase Invoice, Payment Entry.

## SOP-08 — Dispatch

**Trigger:** Material ready and inspection cleared · **Owner:** Stores

1. Raise the **MDM** for the lot: items, quantities, free-issue flags.
2. Raise the **Delivery Instruction** for direct-to-site dispatches: consignee, transporter, vehicle type, LR number, with Annexure-I for free-issue items.
3. Raise the Delivery Note and generate the **e-way bill** where the threshold applies. ODC movements need the vehicle and route recorded.
4. Update the milestone on the project's dispatch schedule.
5. Send the dispatch documents to the customer the same day.

**Control:** Dispatch follows inspection, and the dispatch schedule on the project is updated as it happens — procurement and accounts both read from it, so a stale schedule misleads two functions at once.

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

1. Attendance is captured daily — from the biometric device where fitted. Review exceptions weekly, not at month end when nobody remembers.
2. Leave applications are approved in the system before the leave is taken.
3. Run payroll: PF, ESIC, Professional Tax and TDS on salary computed from the salary structure.
4. Release salaries, then deposit the statutory dues by their due dates.
5. Maintain the gratuity provision annually at year end.
6. On exit, run full and final settlement: notice, leave encashment, gratuity where eligible, recovery of advances.

**Control:** Attendance feeds payroll directly, so the payroll is only as good as the attendance discipline. Fix attendance exceptions weekly and payroll takes an hour instead of a week.

## SOP-13 — Master data governance

**Trigger:** Any new customer, supplier or item · **Owner:** the function that owns the master

1. New customer: name, GSTIN, state, addresses and payment terms — before the first quotation, not before the first invoice.
2. New supplier: GSTIN, and **Udyam number with MSME class** where applicable. Ask in writing and keep the declaration.
3. New item: HSN/SAC and UOM at creation. An item without an HSN cannot be invoiced.
4. Duplicates are the enemy. Search before creating — "Suvarna Copper" and "Suvarna Copper Moulds Pvt Ltd" as two suppliers means two ledgers, two ageing lines and one wrong MSME position.

**Control:** Masters are created by the function that owns them, not by whoever happens to be entering the transaction at the time.

## SOP-14 — Backups, audit trail and archival

**Trigger:** Daily, with an annual review · **Owner:** Sanjay

1. Automated daily backup of database and files, with a copy held on a server physically in India.
2. Monthly archival record of what has been archived and where.
3. Retain books of account and vouchers for eight financial years; the audit trail likewise.
4. Test a restore annually. An untested backup is an assumption.
5. The audit trail stays on. It cannot be disabled, and that is deliberate.

# Part B — Use cases

## UC-1: An enquiry arrives from IndiaMART

A steel plant asks for a two-strand billet caster. Sales records the Lead with source *IndiaMART* the same day and qualifies it into an Opportunity. Design sizes the machine; Projects builds the **PCC** — copper moulds, hydraulics, drives, fabrication, engineering hours, erection, freight, contingency — and applies the target margin. The PCC goes for approval; the Managing Director approves revision 2. The quotation goes out referencing that revision.

Six weeks later the customer's purchase order arrives, and the story continues in UC-2.

*If the enquiry had been quoted from a spreadsheet, nobody would know six months later why the price was what it was, or which assumptions the margin depended on.*

## UC-2: The customer PO does not match the offer

The purchase order arrives. Projects raises a **Kick-off** record and works the checklist. Price matches, scope matches, GST is right — but the PO says 100% payment against delivery, where the offer said 30% advance, 60% against dispatch and 10% after commissioning.

The checkbox stays unticked, the record moves to **PO Query Raised**, and the workflow will not let kick-off be approved. Design release does not start. Accounts take it up with the customer's purchase head; an amendment arrives four days later and the record moves to *PO Verified*, then *Kick-off Approved*.

*Four days of delay, instead of discovering at dispatch that ₹60 lakh of cash flow assumed in the PCC was never going to arrive.*

## UC-3: A supplier bill arrives at month end

The fabricator's invoice for spray chamber work lands on the 29th, and the supplier is calling. Accounts cannot pay it: there is no certified BRM. Purchase check the quantity against the PO, the rate, the inspection result and the delivery — the quantity is short by one assembly still at the fabricator. The BRM is not certified; the supplier is told what is missing.

The balance arrives on the 3rd, the inspection clears, the BRM is certified, and payment is released.

*Without the block, the bill would have been paid on the 29th because the supplier was persistent and it was month end. The short delivery would have surfaced — if at all — when the assembly was needed.*

## UC-4: A drawing changes after material is ordered

The customer approves the general arrangement, then asks for a different mould tube length. Design supersedes the drawing, issues the revision, and sends a **Transmittal** for construction.

But the mould tubes were ordered against the previous revision. The drawing register shows the transmittal and its date; the purchase order references the superseded revision. Purchase go back to the supplier the same day — the tubes have not been cut. The revised requirement replaces them, and the cost difference is recorded as a **Client Claim** because the change came from the customer after approval.

*The claim is raised in the week it happened, with the drawing revisions and transmittal dates as evidence. Raised at the end of the project it would have been a conversation; raised now it is a document.*

## UC-5: An MSME supplier crosses day 40

The daily management summary shows *MSME dues due within the next 15 days: ₹7.80 L*. One supplier, a Small enterprise with a Udyam number, has a bill at day 31.

Accounts check the MSME 45-day report, confirm the appointed date, and schedule the payment for day 42.

*Had it passed day 45, the expense would be disallowed under section 43B(h) in that year's assessment, and interest would be payable under section 16 of the MSMED Act. The cost of missing it is real money; the cost of catching it is reading one line of a daily email.*

## UC-6: Month end

First working week. Accounts book the remaining supplier invoices, reconcile the bank, and run GSTR-2B reconciliation — two invoices are missing from 2B and the suppliers are chased before filing. GSTR-1 and 3B are filed, TDS deposited.

The MSME report is clean. Project WIP is updated: ₹26.7 lakh of cost on unbilled scope carried forward. Depreciation and gratuity provisions are posted.

The Schedule III balance sheet is produced. It balances. The profit ties to the ledger. The CA logs in with a read-only account, reviews the trial balance and the ageing, and signs off.

*The close takes a day because it is the same sequence every month, and the statements are produced monthly rather than reconstructed in September for the year that ended in March.*

## UC-7: A new engineer joins

HR creates the Employee record on day one: joining date, department, designation, UAN, ESIC, PAN, bank. The biometric device is enrolled, so attendance begins automatically. The salary structure is assigned.

The engineer gets a login on the Projects role — able to raise drawings, MDF and PCC, unable to approve their own PCC or certify a BRM.

At the first month end, payroll picks up the attendance and computes PF, ESIC, PT and TDS. The gratuity provision includes the new service from the year end.

*Nobody has to remember to add them to a payroll spreadsheet, and nobody has to decide what they are allowed to do — the role decides.*

## UC-8: The machine is commissioned

Six trial heats at the customer's plant. The site engineer records the **Commissioning Report**: casting speed achieved 2.6 m/min against 2.2–2.8 specified; billet surface accepted on six heats; water circuit pressure 7.6 bar against 8 bar specified — a deviation, accepted, because the limitation is the customer's pump.

Three punch points are recorded, one of them the customer's. **Spares** are handed over with part numbers. The customer issues the **Project Certificate** for provisional acceptance; the twelve-month guarantee starts from that date.

Retention of ₹1.81 lakh is released against the certificate. The **Project Closure Report** shows contract value against PCC estimate against actual cost, and flags one open claim — so the project is not closed yet.

*The deviation on water pressure is recorded, signed and attributable to the customer's pump. When a performance question arises in month eight, that record is the answer.*

# Part C — Who does what

| Process | Prepares | Checks / certifies | Approves |
|---|---|---|---|
| PCC | Projects | Accounts (cost basis) | Director |
| Quotation | Sales / Projects | Projects (against PCC) | Director |
| Kick-off / PO check | Projects | Accounts (commercial terms) | Director |
| Drawing release | Design | Projects | Customer, where required |
| Purchase Order | Purchase | Against PCC budget | Purchase Manager |
| Inspection | Quality | Third party, where specified | Projects |
| BRM | Purchase | Purchase Manager | — |
| Supplier payment | Accounts | Certified BRM required | Director above a threshold |
| Dispatch | Stores | Quality (pre-dispatch) | Projects |
| Sales Invoice | Accounts | Against the billing schedule | — |
| Client Claim | Projects | Accounts | Director |
| Project closure | Projects | Accounts | Director |
| Payroll | HR | Accounts | Director |

The rule underneath the table: **the person who prepares a document never approves it.** In a company of ten this takes discipline, but it is the difference between a control environment and a filing system.

# Part D — Recurring calendar

| When | What | Owner |
|---|---|---|
| Daily | Read the management summary; act on anything marked ACT | Director |
| Daily | Enter transactions the day they happen | All |
| Weekly | Review attendance exceptions | HR |
| Weekly | Review drawings awaiting customer approval and chase | Design |
| Weekly | Review purchase orders against the PCC | Purchase |
| Monthly | GSTR-1, GSTR-3B, GSTR-2B reconciliation | Accounts |
| Monthly | TDS deposit and reconciliation | Accounts |
| Monthly | MSME 45-day review | Accounts |
| Monthly | Payroll and statutory dues | HR |
| Monthly | Project WIP update and MIS review | Accounts, Projects |
| Monthly | Archival record | Sanjay |
| Quarterly | TDS returns; bank guarantee expiry review | Accounts |
| Annually | Gratuity provision; deferred tax; fixed asset verification | Accounts, CA |
| Annually | Physical stock count, including material at subcontractors | Stores |
| Annually | Test a backup restore | Sanjay |
| Annually | Financial statements, Schedule III, notes to accounts, audit | Accounts, CA |

## A closing note on discipline

Every control described here can be bypassed by someone determined enough, except the BRM payment block, which the software enforces. The rest depend on people entering documents when things happen rather than reconstructing them later.

The single habit that makes the difference is same-day entry. A system updated daily tells you the truth about the business; a system updated at month end tells you what somebody remembered.
