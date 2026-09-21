---
title: "MSCAST ERP — Standard Operating Procedures and Use Cases"
---

# MSCAST ERP — Standard Operating Procedures and Use Cases

**For:** MSCAST Engineering Pvt Ltd · **Version:** 3.1 · **Date:** 21 September 2026

## How to read this

- **Part A** — one SOP per business process: trigger, owner, steps, **control**, records.
- **Part B** — nine MSCAST situations showing how the pieces connect.
- **Part C** — who prepares and who approves; where separation of duties holds and where it does not.
- **Part D** — recurring calendar.
- **Screenshots:** each SOP ends with the screens it uses, taken on the demonstration system (demo data, names ending in "(DEMO)"), logged in as the person who does that step. *Where* says how to open the screen: the search bar (Ctrl+K) finds any form or report by name.
- Written for an engineer-to-order machine builder with fewer than ten people, fabrication outsourced, one person often covering several roles.
- Assumes the configuration in doc 05 (Client Setup Guide).
- Two phrases are used precisely:
  - **The system will not allow** — a hard control in the software, tested by the build checks. It cannot be skipped or overridden.
  - **The procedure is** — a way of working that depends on people. Discipline, not enforcement.

## MSCAST's abbreviations

MSCAST's own terms, from the requirement document; they are the form names in the system.

| Term | Stands for | What it is |
|---------------------|-----------------------|--------------------------------------------------------|
| **PCC** | Purchase Cost Calculation | Cost estimate sheet for a machine, built component by component (bought-outs, fabrication, engineering hours, erection, freight, contingency). Prepared before quoting; has revisions and an approval. Baseline for every purchase order and for the project MIS |
| **MDF** | Material Data File | Material list per project or assembly, released by Design from the final drawings. Procurement buys from it |
| **BRM** | Billing Routing Memo | Certificate that a supplier's bill is correct (quantity, rate, inspection, delivery) before Accounts may pay it |
| **MDM** | Material Dispatch Memo | What physically goes out in a dispatch lot, including free-issue items |
| **DI** | Delivery Instruction | Instruction to a supplier to ship direct to the customer's site: consignee, transporter, vehicle, LR number |
| **Annexure-I** | — | Free-issue material list attached to a DI: MSCAST's own material sitting with a subcontractor |
| **PBG / ABG** | Performance / Advance Bank Guarantee | Guarantees given to the customer; expiry dates must be tracked |
| **LD** | Liquidated Damages | Penalty for late delivery, usually a percentage per week up to a cap |
| **CCM** | Continuous Casting Machine | MSCAST's principal product |
| **ITC-04** | — | GST return for goods sent to and received from job workers |
| **MSME** | Micro, Small and Medium Enterprise | Suppliers registered under Udyam. Bills must be paid within 45 days or the expense is disallowed under section 43B(h) |

# Part A — Standard Operating Procedures

## SOP-01 — Enquiry to quotation

**Trigger:** Enquiry from IndiaMART, TradeIndia, email, exhibition or referral · **Owner:** Sales / Projects

1. Record the enquiry as a Lead the day it arrives, with its source (shows which channel is worth the money).
2. Qualify it (machine type, capacity, site, budget, timeline) and convert to an Opportunity.
3. Raise a **PCC** for anything non-standard, component by component: bought-outs, fabrication, engineering hours, erection and commissioning, freight, contingency.
4. Apply the target margin to reach the offer price.
5. Send the PCC for approval. A **director** approves it before the quotation goes out.
6. Issue the Quotation referencing the PCC revision it was priced on.

**Control:** The procedure is that no quotation leaves without an approved PCC. The system allows only a director to approve a PCC. **Limit:** a director can prepare and approve the same PCC; see Part C.

**Records:** Lead, Opportunity, PCC with revision, Quotation.

**On screen**

![A quotation, priced from the approved PCC](demo-screens/m01-quotation.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Quotation* and open it.

![The PCC behind it: components, revision, approval](demo-screens/02-cost-sheet.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *PCC* and open it.

## SOP-02 — Order booking and project kick-off

**Trigger:** Customer purchase order received · **Owner:** Projects, with Accounts

1. Raise a **Project Kick-off** record against the customer PO.
2. Tick only what has actually been verified:
   - Price matches the offer
   - Scope and technical specification match
   - Payment terms accepted
   - Delivery period acceptable
   - LD / penalty clause reviewed
   - GST rate, HSN and place of supply verified
   - BG / PBG requirement identified
   - Advance received
3. Anything that does not match goes in *deviations*; the record goes to **PO Query Raised** and work does not start.
4. Accounts verify the PO (**PO Verified**). A **director** approves kick-off.
5. Create the Project and the Sales Order, linked to the PCC.
6. Enter the billing and dispatch schedule on the project: each milestone, planned dispatch date, billing percentage and value.
7. Hold the kick-off meeting; record attendees, agreed actions and open points.

**Control:** The system will not allow a kick-off to reach *PO Verified*, and so will not allow approval, while price, scope, payment terms or GST is unticked — on every route in, including via *PO Query Raised* (build check T6j). This is the highest-value control in the system. **Limit:** a director can verify the PO and approve the kick-off alone (see Part C); default practice is Anita (Accounts) verifies, a director approves.

**Records:** Kick-off record, Project, Sales Order, billing schedule.

**On screen**

![A kick-off held at *PO Query Raised*: the PO's payment terms differ from the offer](demo-screens/04-kickoff-held.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Project Kickoff* and open it.

![The project, where the billing and dispatch schedule is entered](demo-screens/m02-project-schedule.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Project* and open it.

## SOP-03 — Engineering: drawings, revisions and transmittals

**Trigger:** Design release on a live project · **Owner:** Design, with Projects

1. Register every drawing: number, title, assembly, revision. It starts in **Draft**.
2. The drawing office uses **Issue for Customer Approval**; the drawing moves to **For Customer Approval**.
3. On the customer's response, a **Projects Manager** uses **Record Customer Approval** (→ *Approved by Customer*) or **Return for Rework** (→ *Draft*).
4. A **Projects Manager** uses **Release for Manufacture** (only from *Approved by Customer*).
5. Every issue to a customer, vendor or inspection agency goes on a **Transmittal**: document numbers, revisions, sheet counts, purpose (approval, construction, information, as-built).
6. Chase the acknowledgement and record it. An unacknowledged transmittal is not proof of issue.
7. On revision: **Supersede** the old drawing, register and issue the new one on a fresh transmittal, and tell Purchase in writing if material is already ordered against it.
8. Release the **MDF**.

**Control:** The system will not allow *Released for Manufacture* except from *Approved by Customer*, and only by a Projects Manager. Draft cannot jump to Released.

**Records:** Drawing register with revision history, Transmittals with acknowledgements, MDF.

**On screen**

![The drawing register: every drawing, its revision and status](demo-screens/05-drawing-register.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Drawing Register* and open it.

![A drawing waiting for the customer's approval](demo-screens/06-drawing-with-customer.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Drawing* and open it.

![A transmittal: what was issued, to whom, and the acknowledgement](demo-screens/m03-transmittal.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Transmittal* and open it.

![The MDF released to Procurement](demo-screens/m04-mdf.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *MDF* and open it.

## SOP-04 — Procurement: requisition to purchase order

**Trigger:** MDF released, or a stock item at its reorder level · **Owner:** Purchase

1. Raise a Material Request from the MDF.
2. Issue an **RFQ** to at least three suppliers for anything material.
3. Record each Supplier Quotation with technical score, compliance, deviations and delivery weeks, not only price. A cheaper offer that does not comply is not cheaper.
4. Compare against the **PCC budget** for that scope.
5. Raise the Purchase Order. If it exceeds the PCC line, record the justification; an alert goes to management.
6. A Purchase User sends the PO for approval; a **director** approves it. Purchase can reject a PO but cannot approve one.

**Control:** The system will not allow a PO to be approved unless someone holding `Purchase User` sent it; approval is a director's. The raiser cannot approve (checked on every build). The *PO vs PCC Variance* report measures POs against the PCC continuously, as the early warning of cost drift.

**Records:** Material Request, RFQ, Supplier Quotations with scoring, Purchase Order.

**On screen**

![Material Request raised from the MDF](demo-screens/m05-material-request.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Material Request* and open it.

![A supplier's quotation, recorded for comparison](demo-screens/m06-supplier-quotation.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Supplier Quotation* and open it.

![An approved purchase order](demo-screens/07-purchase-order.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Purchase Order* and open it.

![PO vs PCC Variance: purchases against the cost sheet, per project](demo-screens/m07-po-vs-pcc.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *PO vs PCC Variance* and open it.

## SOP-05 — Free issue to subcontractors

**Trigger:** Material issued to a fabricator against a job · **Owner:** Stores

1. Transfer the material to that subcontractor's warehouse in the system. It remains MSCAST's stock.
2. Record it on the **Annexure-I** attached to the DI.
3. Track it on the *Free Issue at Vendor* report (what is where, and its value).
4. Reconcile on receipt of the fabricated item; account for scrap and returns explicitly.

**Control:** Free-issue material stays on MSCAST's books and visible. Under GST, inputs sent to a job worker must return within 1 year (3 years for capital goods) or become a deemed supply; the report shows this before the deadline.

**Records:** Stock transfer, Annexure-I, ITC-04 data.

**On screen**

![Free issue: material transferred to the fabricator's warehouse (Annexure-I)](demo-screens/m08-free-issue-transfer.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Stock Entry* and open it.

![Free Issue at Vendor: what is where, and its value](demo-screens/m09-free-issue-report.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Free Issue at Vendor* and open it.

## SOP-06 — Inspection and quality

**Trigger:** Manufacturing stage reached at a supplier or in-house · **Owner:** Quality / Projects

1. Raise an **Inspection Plan** per stage: in-process, pre-dispatch, third-party, customer.
2. Record planned date, inspector and result: Pending, Accepted, Accepted with deviation, Rejected.
3. Record every deviation with what was accepted and who accepted it. Never a silent pass.
4. Rejections go back to the supplier with the observations; repeat the pre-dispatch inspection.

**Control:** The procedure is: no dispatch without a cleared pre-dispatch inspection. The software does not block the Delivery Note; Stores must check. Open inspection stages appear on the daily summary.

**Records:** Inspection Plan with result, Inspection Report print.

**On screen**

![An inspection stage with its result](demo-screens/m10-inspection-plan.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Inspection Plan* and open it.

![Inspection Status: every stage across projects](demo-screens/m11-inspection-status.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Inspection Status* and open it.

## SOP-07 — Supplier bill to payment (the BRM route)

**Trigger:** Supplier invoice received · **Owner:** Purchase prepares, a director certifies, Accounts pays

1. Purchase raises a **BRM** against the supplier bill.
2. Purchase checks and ticks all four: quantity, rate against the PO, inspection cleared, delivery received.
3. A **director** certifies it (**Pending → Certified**). Purchase can reject a bill back to the supplier with the reason, but cannot certify.
4. Accounts book the Purchase Invoice against the PO and receipt.
5. Accounts **Mark Paid** only against a **Certified** BRM.

**Control — the system will not allow:**

- Certifying a BRM unless its four checks (quantity, rate, inspection, delivery) are ticked.
- Paying a supplier bill with no certified BRM — by Payment Entry, by Journal Entry, or as an advance with no invoice behind it. Applies to everyone, including directors. The reason is displayed.
- Paying more than the certified amount.
- **Only exception:** a supplier ticked *Exempt from BRM certification*, for bills with no PO to certify against (electricity, water, rent, telephone, statutory). Ticking a trade supplier defeats the control; see doc 11 (Operating Recommendations), A8.
- There is no value threshold for payment approval; the certified BRM is the control.

**Limit:** one director can create, certify and mark paid the same BRM alone; see Part C.

**Records:** BRM with certification, Purchase Invoice, Payment Entry.

**On screen**

![A certified BRM: all four checks ticked, certifier and date recorded](demo-screens/08-brm-certified.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *BRM* and open it.

![What Accounts sees when paying a bill with no certified BRM](demo-screens/09-payment-refused.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Payment Entry* and open it.

![The BRM Register](demo-screens/10-brm-register.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *BRM Register* and open it.

## SOP-08 — Dispatch

**Trigger:** Material ready and inspection cleared · **Owner:** Stores

1. Raise the **MDM** for the lot: items, quantities, free-issue flags.
2. Raise the **DI** for direct-to-site dispatches: consignee, transporter, vehicle type, LR number, with Annexure-I for free-issue items.
3. Raise the Delivery Note and generate the **e-way bill** where the threshold applies. ODC movements need vehicle and route recorded.
4. Update the milestone on the project's dispatch schedule.
5. Send the dispatch documents to the customer the same day.

**Control:** The procedure is: dispatch follows inspection, and the dispatch schedule is updated as it happens (Purchase and Accounts both read it). The overnight checks flag a dispatch made before its commissioning or inspection record exists.

**Records:** MDM, DI with Annexure-I, Delivery Note, e-way bill.

**On screen**

![Material Dispatch Memo for a lot, with free-issue items flagged](demo-screens/m12-mdm.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *MDM* and open it.

![Delivery Instruction to the supplier, with Annexure-I](demo-screens/m13-delivery-instruction.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Delivery Instruction* and open it.

![The Delivery Note](demo-screens/11-dispatch.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Delivery Note* and open it.

## SOP-09 — Billing, retention and claims

**Trigger:** A billing milestone is reached · **Owner:** Accounts

1. Raise the Sales Invoice against the milestone on the billing schedule, with the correct GST treatment for the place of supply.
2. Where the contract holds retention, reclassify it from trade receivables to **Retention Receivable**. It is not collectable until the performance certificate.
3. Record scope variations, idle time and escalation as **Client Claims** the week they arise, not at project end.
4. Settle an agreed claim by a **supplementary invoice** referencing it.
5. Follow up receivables against due dates; send a payment reminder on anything overdue.

**Control:** Retention is a separate asset with a release trigger.

**Records:** Sales Invoice, retention journal, Client Claim, supplementary invoice.

**On screen**

![A milestone sales invoice](demo-screens/m14-sales-invoice.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Sales Invoice* and open it.

![Retention and Certificates: retention held per contract and its release trigger](demo-screens/m15-retention.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Retention and Certificates* and open it.

![A client claim, agreed and settled by supplementary invoice](demo-screens/m16-client-claim.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Client Claim* and open it.

![Proforma invoice for an advance](demo-screens/12-proforma-print.png){width=6.2in}

*Where:* Open the Sales Order → printer icon → *MSCAST Proforma Invoice*.

## SOP-10 — Commissioning to project closure

**Trigger:** Machine erected at site · **Owner:** Site engineer, then Projects

1. Record the **Commissioning Report**: each performance parameter specified vs achieved, trial runs, result (met, not met, deviation accepted).
2. Record the punch list: every open point, with its owner.
3. Hand over spares on a **Spares Handover** note: commissioning spares and the two-year mandatory list, with part numbers.
4. Obtain the **Project Certificate** (provisional or final acceptance). The guarantee period starts here.
5. Release retention against the certificate.
6. Run the **Project Closure Report**: contract value vs PCC estimate vs actual cost, billed, collected, certificates, open claims, drawings and inspections outstanding. It gives a closure verdict; a project with open claims or uncollected money is not closed.

**Control:** Closure is on evidence. Closing with an open claim abandons the claim.

**Records:** Commissioning Report, Spares Handover, Project Certificate, Closure Report.

**On screen**

![Commissioning report: each parameter, specified vs achieved](demo-screens/m17-commissioning.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Commissioning Report* and open it.

![Project certificate received from the customer](demo-screens/m18-project-certificate.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Project Certificate* and open it.

![Project Closure Report](demo-screens/m19-closure-report.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Project Closure Report* and open it.

## SOP-11 — Month-end close

**Trigger:** First working week of each month · **Owner:** Accounts, reviewed by the CA

1. Book all supplier invoices for the month; goods received and not billed must show as such.
2. Reconcile the bank.
3. Reconcile GSTR-2B against the purchase register with the reconciliation tool; resolve mismatches with suppliers before filing.
4. File GSTR-1 and GSTR-3B by their due dates.
5. Deposit TDS and reconcile the ledger.
6. Check the **MSME 45-day report**. Anything beyond 45 days is a section 43B(h) disallowance: pay it, or accept the tax cost knowingly.
7. Update **project WIP**: cost incurred on unbilled scope.
8. Post provisions: depreciation, gratuity, known liabilities.
9. Review the Schedule III balance sheet and statement of profit and loss; confirm the trial balance nets to zero and profit ties to the ledger.
10. Review the project MIS per project: contract value vs PCC vs committed vs billed.

**Control:** Same sequence every month; Schedule III statements produced monthly, not once a year.

**On screen**

![MSME 45-Day Dues: each bill's deadline](demo-screens/14-msme-45-day.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *MSME 45-Day Dues* and open it.

![Balance sheet in Schedule III format](demo-screens/15-balance-sheet.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Balance Sheet (Schedule III)* and open it.

![Statement of profit and loss in Schedule III format](demo-screens/m20-profit-loss.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Statement of Profit and Loss (Schedule III)* and open it.

![Project MIS: contract vs PCC vs committed vs billed](demo-screens/13-project-mis.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Project MIS* and open it.

## SOP-12 — HR and payroll

**Trigger:** Monthly, plus events · **Owner:** HR

1. Record attendance. The biometric pull (device punches converted to attendance) is switched off as of 21 September 2026; until it is enabled and tested against manually checked attendance, attendance is entered in the system. Review exceptions weekly.
2. Leave is approved in the system before it is taken.
3. Run payroll: ESIC, Professional Tax and TDS on salary, computed from the salary structure (PF is not deducted; see doc 11, B4).
4. Release salaries, then deposit statutory dues by their due dates.
5. Update the gratuity provision annually at year end.
6. On exit, run full and final settlement: notice, leave encashment, gratuity where eligible, recovery of advances.

**Control:** Attendance feeds payroll directly. The system will not allow duplicate attendance for the same employee on the same day.

**On screen**

![Attendance list](demo-screens/m22-attendance.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Attendance* and open it.

![A salary slip](demo-screens/m21-salary-slip.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Salary Slip* and open it.

## SOP-13 — Master data governance

**Trigger:** Any new customer, supplier or item · **Owner:** The function that owns the master

1. New customer: name, GSTIN, state, addresses, payment terms — before the first quotation.
2. New supplier: GSTIN, and **Udyam number with MSME class** where applicable. Ask in writing and keep the declaration.
3. New item: HSN/SAC and UOM at creation.
4. Search before creating. "Suvarna Copper" and "Suvarna Copper Moulds Pvt Ltd" as two suppliers means two ledgers, two ageing lines and one wrong MSME position.

**Control:** The system validates GSTIN format and the state it implies, and refuses an invoice line without an HSN. The procedure is that masters are created only by the function that owns them.

**On screen**

![A supplier master (GSTIN, MSME class and Udyam number sit on its tabs)](demo-screens/m23-supplier-master.png){width=6.2in}

*Where:* Search bar (Ctrl+K) → type *Supplier* and open it.

## SOP-14 — The overnight checks and the morning mails

**Trigger:** Automatic, daily · **Owner:** Directors read; nobody runs it

1. **06:00 IST — exception checks run.** 16 rules compare documents with each other and with the calendar: supplier bill with no certified BRM, MSME bill nearing day 45, bank guarantee nearing expiry, open project with no time booked, dispatch without paperwork, and others. Findings go to the **MSCAST Exception** list with severity, document and suggested action. Rules only; no model, no internet, no cost.
2. **08:30 IST — daily management summary** (with dispatch schedule and project MIS) is emailed.
3. **08:35 IST — the morning note.** The findings and the summary are turned into a few sentences naming what matters most today; every item links to its document. If the model is unreachable, the note goes out as a plain list. Recipients: the directors by design; on the Live POC, waseemraj@mcast.co.in by the owner's decision.
4. **During the day:** work the exception list. Mark **Acknowledged** when picked up, **Resolved** when the document is fixed; resolved items stop appearing.

**Control:** The checks do not prevent mistakes; they stop mistakes staying invisible.

**Action:** Read the note; act on anything marked **High**. An item that appears six mornings running means a procedure is not being followed.

**Records:** MSCAST Exception list, the morning emails.

**On screen**

![The home page: today's position and what needs attention](demo-screens/01-md-home.png){width=6.2in}

*Where:* Sidebar **Home**.

![The exception list: open findings with severity and owner](demo-screens/m24-exception-list.png){width=6.2in}

*Where:* Search bar (Ctrl+K): *MSCAST Exception*.

## SOP-15 — Backups, audit trail and archival

**Trigger:** Daily, with an annual review · **Owner:** The implementer

1. Automated daily backup of database and files, with a copy on a server physically in India. On the POC: Windows task "MSCAST nightly backup" at 02:30 JST runs the backup and all 42 build checks and emails autoelectron.jp@gmail.com on failure; a watchdog at 09:00 IST emails if the nightly has not run in 26 hours.
2. Keep a monthly archival record: what was archived and where.
3. Retain books of account, vouchers and the audit trail for eight financial years.
4. Test a restore annually. Three settings are not in the database backup: `encryption_key` (put back with `restore-key.sh`), `server_script_enabled` (bench-wide) and `host_name`. See the POC README (POC README).
5. The audit trail stays on. It cannot be disabled, by anyone.

# Part B — Use cases

**On screen**

![The monthly archival log](demo-screens/m25-archival-log.png){width=6.2in}

*Where:* Search bar (Ctrl+K): *MSCAST Archival Log*.

## UC-1: An enquiry arrives from IndiaMART

- A steel plant asks for a two-strand billet caster. Sales records the Lead (source *IndiaMART*) the same day and qualifies it into an Opportunity.
- Design sizes the machine. Projects builds the **PCC** (copper moulds, hydraulics, drives, fabrication, engineering hours, erection, freight, contingency) and applies the target margin.
- A director approves revision 2; the quotation references that revision.
- Six weeks later the customer's PO arrives (UC-2).

## UC-2: The customer PO does not match the offer

- Projects raises the **Kick-off** and works the checklist. Price, scope and GST match, but the PO says 100% against delivery; the offer said 30% advance, 60% against dispatch, 10% after commissioning.
- The box stays unticked; the record goes to **PO Query Raised**; the system will not allow kick-off approval. Design release does not start.
- Accounts take it up with the customer's purchase head. An amendment arrives 4 days later; the record moves to *PO Verified*; a director approves kick-off.
- Result: 4 days of delay, instead of finding at dispatch that ₹60 lakh of cash flow assumed in the PCC was never coming.

## UC-3: A supplier bill arrives at month end

- The fabricator's invoice for spray chamber work lands on the 29th; the supplier is calling. Accounts cannot pay: no certified BRM.
- Purchase check quantity against the PO, rate, inspection and delivery. Quantity is short by one assembly still at the fabricator. The bill is rejected back to the supplier with the reason.
- The balance arrives on the 3rd, inspection clears, a director certifies the BRM, Accounts release the payment.

## UC-4: A drawing changes after material is ordered

- The customer approves the general arrangement, then asks for a different mould tube length.
- The Projects Manager **supersedes** the drawing; the drawing office registers and issues the revision; it goes through customer approval and **Release for Manufacture** again.
- The mould tubes were ordered against the previous revision. The register shows the transmittal and date; the PO references the superseded revision. Purchase contact the supplier the same day; the tubes have not been cut and the revised requirement replaces them.
- The cost difference is recorded as a **Client Claim** (change came from the customer after approval), that week, with drawing revisions and transmittal dates as evidence.

## UC-5: An MSME supplier bill nears day 45

- The daily management summary shows *MSME dues due within the next 15 days: ₹7.80 L*.
- One supplier (Small enterprise, Udyam number) has a bill at day 31. It is a Medium-severity item on the morning note and has appeared six mornings running.
- Accounts check the MSME 45-day report, confirm the appointed date, and schedule payment for day 42.
- *If missed:* past day 45 the expense is disallowed under section 43B(h) for that year, and interest is payable under section 16 of the MSMED Act.

## UC-6: Month end

- First working week. Accounts book remaining supplier invoices, reconcile the bank, run GSTR-2B reconciliation: two invoices missing from 2B; suppliers chased before filing. GSTR-1 and 3B filed; TDS deposited.
- MSME report clean. Project WIP updated: ₹26.7 lakh of cost on unbilled scope carried forward. Depreciation and gratuity provisions posted.
- Schedule III balance sheet produced; it balances and profit ties to the ledger.
- The CA logs in read-only, reviews the trial balance and ageing, and signs off.
- The close takes one day.

## UC-7: A new engineer joins

- Day one: HR creates the Employee record (joining date, department, designation, UAN, ESIC, PAN, bank) and assigns the salary structure. Attendance is entered until the biometric pull is enabled, then pulled from the device.
- The engineer gets a login on the Projects role: can raise drawings, MDF and PCC; cannot approve a PCC, release a drawing for manufacture, approve a PO or certify a BRM.
- First month end: payroll picks up attendance and computes ESIC, PT and TDS. The year-end gratuity provision includes the new service.

## UC-8: The machine is commissioned

- Six trial heats at the customer's plant. The site engineer records the **Commissioning Report**:
  - Casting speed 2.6 m/min against 2.2–2.8 m/min specified
  - Billet surface accepted on six heats
  - Water circuit pressure 7.6 bar against 8 bar specified — deviation accepted; the limit is the customer's pump
- Three punch points recorded, one of them the customer's. **Spares** handed over with part numbers.
- The customer issues the **Project Certificate** (provisional acceptance); the 12-month guarantee starts from that date.
- Retention of ₹1.81 lakh released against the certificate. The **Project Closure Report** flags one open claim, so the project stays open.

## UC-9: A Tuesday morning

- Aiqaz opens the morning note at 08:40. Four items. It leads with a supplier bill for ₹2.86 L with no certified BRM; Accounts cannot release it and the supplier is waiting.
- Below: an MSME bill at day 31, a bank guarantee expiring in 39 days, a project with no timesheets ever booked — each flagged repeatedly.
- He opens the BRM, checks it against the PO and inspection, certifies it (2 minutes). He forwards the bank guarantee line to Anita. He takes the timesheet item to the Monday meeting because it has appeared twice, which makes it a habit.

# Part C — Who does what

*Enforced* = the software refuses the action to anyone else. *Practice* = how MSCAST works; the software would permit otherwise.

| Process | Prepares | Approves / certifies | Enforced? |
|---------------------------|---------------------|-----------------------------|-----------------------|
| PCC | Projects | **Director** | Enforced — but see the limits below |
| Quotation | Sales / Projects | Against an approved PCC | Practice |
| Kick-off / PO check | Projects, verified by Accounts | **Director** | Enforced (checklist too) — but see the limits below |
| Drawing → For Customer Approval | Design (drawing office) | — | Enforced |
| Drawing → Released for Manufacture | — | **Projects Manager**, only after customer approval | Enforced |
| Purchase Order | Purchase (sent by a `Purchase User`) | **Director** | Enforced; the raiser cannot approve |
| Inspection | Quality | Third party, where specified | Practice |
| BRM certification | Purchase prepares, ticks four checks | **Director** certifies | Enforced; cannot certify with a check unticked |
| Supplier payment | Accounts | Certified BRM required (unless supplier is BRM-exempt) | Enforced on Payment Entry and Journal Entry |
| Dispatch | Stores | Quality (pre-dispatch) | Practice |
| Sales Invoice | Accounts | Against the billing schedule | Practice |
| Client Claim | Projects | Accounts, then Director | Practice |
| Project closure | Projects | Director | Practice |
| Payroll | HR | Director | Practice |

## Separation of duties

Principle: **the person who prepares a document should not approve it.**

Where it holds:

- **Purchase Orders.** Sending for approval needs `Purchase User`; approving needs `MSCAST Director`. No one holds both. Mustaque holds `Purchase Manager`, which can *create* a PO but not send it for approval.
- **The payment block.** No certified BRM, no supplier payment, for everyone (see SOP-07).
- **Drawing release.** The drawing office issues; only a Projects Manager releases.
- **BRM for Purchase staff.** Sameer and Nikhil prepare and may reject, but cannot certify.

Where it does not hold (accepted decision for a company this size):

- **PCC and kick-off.** Both directors also hold Projects Manager and Accounts Manager, so a director can prepare a PCC and approve it, or verify a customer PO and approve the kick-off, alone (build check T6e warns).
- **BRM for directors.** A director can create, certify and mark paid alone (build check T6g warns).
- **Mitigation:** every approval is recorded with name and timestamp against the revision. **Where the commitment is significant, the other director approves.**

## For the system administrator

- Controls are only as real as the role list. No operational user may hold `System Manager`; it bypasses every control in this document.
- The setup-wizard administrator holds `System Manager` only. A fresh install recreates it with every manager role; cutting it back is line 15 of the go-live checklist (doc 05).
- Build check T6f reports any non-administrator holding `System Manager`. On the Live POC it warns: MSCAST's trial admin gave Aiqaz Chandankeri `System Manager`.

# Part D — Recurring calendar

| When | What | Owner |
|---------------------------|-----------------------------------------|-------------------------------|
| Daily, automatic | 02:30 JST nightly backup and build checks | *the system* |
| Daily, automatic | 06:00 IST exception checks; 08:30 IST management summary; 08:35 IST morning note | *the system* |
| Daily | Read the morning note; act on anything marked High | Directors |
| Daily | Read the management summary; act on anything marked ACT | Director |
| Daily | Clear or acknowledge items on the exception list | The named owner |
| Daily | Enter transactions the day they happen | All |
| Weekly | Review attendance exceptions | HR |
| Weekly | Review drawings awaiting customer approval and chase | Design |
| Weekly | Review purchase orders against the PCC | Purchase |
| Weekly | Review any exception seen more than twice (a process problem, not a document problem) | Directors |
| Monthly | GSTR-1, GSTR-3B, GSTR-2B reconciliation | Accounts |
| Monthly | TDS deposit and reconciliation | Accounts |
| Monthly | MSME 45-day review | Accounts |
| Monthly | Payroll and statutory dues | HR |
| Monthly | Project WIP update and MIS review | Accounts, Projects |
| Monthly | Archival record | The implementer |
| Quarterly | TDS returns; bank guarantee expiry review | Accounts |
| Annually | Gratuity provision; deferred tax; fixed asset verification | Accounts, CA |
| Annually | Physical stock count, including material at subcontractors | Stores |
| Annually | Test a backup restore | The implementer |
| Annually | Financial statements, Schedule III, notes to accounts, audit | Accounts, CA |

## What the software enforces, and what depends on people

- **Enforced:** BRM payment block (every payment route), BRM certification only with all four checks ticked, PO approval only after a `Purchase User` sends it, drawing release sequence, kick-off checklist.
- **Everything else depends on same-day entry.** The overnight checks exist because that habit slips.
