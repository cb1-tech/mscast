# MSCAST ERP - Requirements Traceability (v1.9)

**Version 1.9 · 21 Sep 2026** · every requirement implemented; verified by a 37-check automated harness.

Source of requirements: MSCAST `ERP_Requirement_Final.pdf`. Solution: ERPNext v16.35 + India Compliance 16.9.1 + Frappe HR 16.19 + India Payroll 16.0.4 + `mscast_erp` 0.1.0 (release **`v0.9.0`**).

> **What changed in v1.9.** No requirement changed status. The evidence behind several changed, because a fresh install of the package and an upgrade of a copy of the live system were both tested for the first time. **The directors could not open some of the documents they approve** - the managing director could not open a Project Kick-off, Aiqaz could not open a Purchase Order - because a permission change had dropped every standard role from five document types. **A fresh install lacked the drawing office's role and the auditor's read access to the books.** **An upgrade would have stripped the demonstration watermark** and would have overwritten other applications' configuration, including India Compliance's GST fields. All fixed in the package, and each now has a build check: the harness is 37 checks. Two further checks (T7a, T7b) turned out to have been examining nothing since the documents moved into the package; they now fail if they find nothing to examine.
>
> **What changed in v1.8.** No requirement changed status. **A-05 changed its evidence, and its mechanism.** The BRM payment block was a Server Script on Payment Entry, and on 21 September it was tested at every other door rather than only the one it guarded. Three ways round it were open: a Journal Entry debiting Creditors paid an uncertified bill straight through; an advance Payment Entry with no invoice reference passed silently; and the certified *amount* was never read, so a memo certified for nine units paid for ten. It was also too wide in the other direction — an electricity bill, which can have no BRM at all, was refused with no way out. The control now lives in the application package (`mscast_erp.controls.brm_payment`) on both Payment Entry and Journal Entry, the Server Script is deleted, and a per-supplier *Exempt from BRM certification* flag covers utilities, rent and statutory bills. `T6a` went from one route to six; `T6c` now fails if the retired script reappears. The harness stands at 31 checks.
>
> **What changed in v1.7.** No requirement changed status. One piece of **evidence was found to be wrong**, and it is the kind worth naming rather than quietly fixing. P-08 and PC-06 said a supplier bill passes through three separate hands — Purchase prepares, a director certifies, Accounts pays. It does not have to. Both directors hold a role that can *create* a BRM, the role that certifies one and the role that marks it paid, so a director can carry a supplier bill from creation to payment alone. The harness had not caught it because the segregation check compared workflow *transition* roles, and creating a document is a permission rather than a transition. A new check, **T6g**, asks the question the way an auditor would and now reports it. The payment block itself is unaffected: no certified BRM, no payment, for anyone. The administrator-account item under *What still stands* is closed, and the harness is now 27 checks.

> **What changed in v1.6.** No requirement changed status. What changed is the evidence behind several of them, after the users were rebuilt as named people and the approval authority was settled. Corrected: the harness went from 23 checks to 25; `MSCAST Director` is the **approving** role, not a read-only one; BRM certification and purchase-order approval sit with a director, not the Purchase Manager; the drawing register is driven by a workflow rather than a status field; and the counts in the "built beyond" table were all understated. The Gemini automation listed as outstanding has been built.

## Coverage

| POC status | v1.3 | v1.4 | v1.5 | v1.6 | v1.7 |
|---|---:|---:|---:|---:|---:|
| Live in POC | 53 | 88 | 97 | 97 | **97** |
| Partly in POC | 20 | 3 | 0 | 0 | **0** |
| Available (standard, not demoed) | 11 | 1 | 0 | 0 | **0** |
| Not in POC | 10 | 2 | 0 | 0 | **0** |
| Out of POC scope | 3 | 3 | 0 | 0 | **0** |
| **Total** | **97** | **97** | **97** | **97** | **97** |

**All 97 requirements are live.** Six rest on assumptions that MSCAST or the CA should confirm — each is stated in the evidence column and in the voucher narrations inside the system. All six remain open.

## Assumptions carried

| ID | Assumption | Who confirms |
|---|---|---|
| A-14 | Schedule III presentation format as built | CA |
| AC-07 | MSCAST is an SMC reporting under AS, claiming SMC exemptions, not Ind AS | CA |
| AC-11 | Income tax at 25.168% under s.115BAA; depreciation timing difference estimated | CA |
| AC-17 | WIP at cost on unbilled scope, completion measured by billing vs contract value | CA (decision D6) |
| M-02 | 'Finance Scaling Management' means funding capacity for the order book | MSCAST (Q1) |
| M-03 | Biometric device pushes punches to the standard checkin endpoint | MSCAST (Q6) |

## Test harness result (20 Sep 2026)

| Check | Area | Result |
|---|---|---|
| T1 | reports | 326 SQL literal comparisons validated against the fields' real Select options - 0 mismatched |
| T2 | reports | 28 custom reports execute - 0 failures |
| T3 | reports | no report uses the container's UTC date |
| T4 | prints | 15 custom print formats render - 0 problems |
| T4b | prints | demonstration site: every print watermarked; any other site: none |
| T5a | ledger | trial balance nets to zero |
| T5b | ledger | Schedule III balance sheet balances to the rupee |
| T5c | ledger | P&L profit ties to the ledger surplus |
| T5d | ledger | no ledger entry without a cost centre |
| T6a | controls | BRM payment block guards every payment route — six routes attempted live on each build |
| T6b | controls | **5 workflows** active and complete |
| T6c | controls | controls live in the application package, scripts only where intended |
| **T6d** | controls | **approval authority is where the business put it** - 5 transitions asserted |
| **T6e** | controls | **nobody can both raise and approve the same document** - *warns*, see below |
| **T6f** | controls | **only administrators hold System Manager** - 2 holders, both expected |
| **T6g** | controls | **no one person can create and then approve the same document** - *warns*, see below |
| T6h | controls | the auditor's login cannot change anything - effective rights, not stored rows |
| T6i | controls | every role can raise the documents its role card describes |
| T6j | controls | a guarded workflow state is guarded on every route into it |
| **T6k** | controls | **everyone who can approve a document can open it** - asked per real user |
| **T6l** | controls | **no role silently lost access** to a customised document type |
| **T6m** | controls | **the package ships all of MSCAST's configuration and none of anyone else's** |
| T7a | data | every MSCAST form has records - fails if it finds no forms to check |
| T7b | data | every stored Select value is a valid option - 45 fields on 25 document types |
| T7c | data | every invoiced item carries an HSN code |
| T8 | gst | GST head matches the place of supply on every invoice |
| T9a-e | email | outgoing account live, mail sent without error, morning batch scheduled, no dead notification recipient, no bounce-prone user |
| T9f | automation | every enabled MSCAST scheduled job has actually run |
| T9g | automation | every stored secret decrypts with this site's key |
| T9h | automation | the nightly backup ran in the last 26 hours and succeeded |
| T10a-c | hr | payroll and attendance loaded, no duplicates, biometric punches converted |

**35 pass, 2 warn, 0 fail, of 37.**

### The two warnings, and why they are warnings

Both are positions somebody has taken, not defects to chase. Both are stated in the SOPs and the role cards.

- **T6e — can an ordinary user both raise and approve the same document?** Yes, for the PCC and the kick-off. Both directors hold the Projects Manager and Accounts Manager roles as well as the director role, so a director can prepare a PCC or verify a customer PO and then approve it alone.
- **T6g — can one person *create* a document and then approve it?** Yes, for the BRM. This is the check added in v1.7. T6e compares workflow *transition* roles; creating a document is a permission, not a transition, so preparing a BRM was invisible to it. Both directors hold `Projects Manager` (which can create a BRM), `MSCAST Director` (which certifies one) and `Accounts Manager` (which marks it paid) — one person, all three steps.

**Why T6d, T6e, T6f and T6g exist.** An app install silently rewrote the workflow roles back to an older definition — cost-sheet approval to a system role, bill certification to the purchase manager — and the 23-check harness still passed, because it checked that workflows were *active and complete* and never checked *who they gave authority to*. T6d closed that. T6e, T6f and T6g each closed a further gap that the one before could not see. Business rules now have tests like any other code, and each test exists because something got past the previous one.

## Full matrix

| ID | Area | Requirement | ERPNext v16 solution | Category | Phase | Size | POC evidence (20 Sep 2026) |
|---|---|---|---|---|---|---|---|
| S-01 | Sales | Prepare Sales Orders from customer orders | ERPNext Sales Order (customer PO no./date, payment terms template) | Standard | P1 | S | 3 sales orders submitted with customer PO no., retention/LD/PBG fields |
| S-02 | Sales | PCC sheet (Purchase Cost Calculation): cost price of each component of CCM/spares, prepared by Sales from the Sales Order | Custom 'PCC' doctype linked to Sales Order/Project: component lines, revisions + approval; baseline for PO control and project MIS | Custom (no-code + script report) | P1 | L | PCC-2026-00001 (R2, approved, 15 lines, Rs 1.82 Cr) and PCC-2026-00002 (approved). **Approval is a director's** — though a director may also prepare one, see T6e |
| S-03 | Sales | Order-status analysis; leads from customer enquiry or direct approach | CRM Lead → Opportunity → Quotation; Sales Pipeline Analytics | Standard | P1 | S | Lead (Gulf Aluminium), 2 Opportunities, Quotation SAL-QTN-2026-00001; order-book chart. Plus **14 bid outcomes** (6 won / 6 lost with reasons) |
| S-04 | Sales | Scope of work/contract and PCC handed to Engineering and Projects | Kick-off workflow on Project; mandatory attachments and notifications | Config | P1 | S | MSCAST Project Kickoff form with the 8-point customer-PO checklist, linked PCC / SO / project. **Kick-off approval is a director's** |
| S-05 | Sales | List of potential/probable customers for forecasting | Leads/Opportunities with expected value and closing date | Standard | P1 | S | Open lead + spares opportunity; 'Order Book by Customer' chart |
| PR-01 | Projects | Internal kick-off meeting; Projects receives PCC, signed tech specs, sales MOMs | Project Template + kick-off checklist child table; Workflow 'Kick-off done' | Config | P1 | S | Project kick-off task completed on PROJ-0001, PCC + SO linked |
| PR-02 | Projects | Project planning: targets for Engineering, Procurement, Despatch, Erection & Commissioning | Project tasks, milestones, dependencies, Gantt | Standard | P1 | S | Tasks across 3 projects with dates, status and progress |
| PR-03 | Projects | Prepare and submit Project Execution, Delivery and Billing schedules to client/consultant | Delivery + billing schedule child tables on Project/SO; print formats | Config + light custom | P1/P3 | M | 'MSCAST Project Schedule (Client)' print - contractual milestones with live drawing, inspection, dispatch and commissioning status |
| PR-04 | Projects | Periodic 'Overall Project Status/Schedule' submission to client | Project status print format/report | Custom (report + print) | P1 | M | 'MSCAST Project Status Report' - progress bar, commercial and engineering position, open punch points |
| PR-05 | Projects | Submit invoices and follow up receivables from client | Accounts Receivable, Payment Reminder/Dunning, Notification before due date | Standard | P4 | S | Payment request + AR ageing + overdue notification |
| PR-06 | Projects | Project completion: completeness of supplies | Sales Order Analysis (ordered vs delivered), SO–DN tracking | Standard | P3 | S | MSCAST Dispatch Schedule shows ordered vs delivered vs pending |
| PR-07 | Projects | Additional claims discussion and settlement with client | Custom 'Client Claim' doctype → amended SO / additional invoice | Custom (no-code) | P3 | S | Client Claim register + print; CLM-2026-00001 (Rs 6.85 L scope variation, agreed Rs 6.40 L) and CLM-2026-00002 (idle time, settled by supplementary invoice) |
| PR-08 | Projects | Obtain Commissioning, Preliminary and Final certificates from client | Custom 'Project Certificate' doctype; triggers milestone billing and retention clock | Custom (no-code) | P3 | S | Certificates across projects with retention due date + print format |
| PR-09 | Projects | After final closure, hand over project info to Spares Dept for spares business | Project closure checklist; installed-machine record + customer spares price list | Config | P5 | S | MSCAST Spares Handover + print. Plus the **MSCAST Installed Machine** register: 14 machines, 2009–2024, the basis of the spares and retrofit business |
| PC-01 | Project coordination | Check customer PO against agreed terms; forward to Finance and Procurement | SO approval workflow with PO-vs-quotation check; notifications | Config | P1 | S | 'MSCAST Project Kick-off' workflow: Draft → PO Verified (**Accounts**, only when price, scope, payment terms and GST are ticked) → Kick-off Approved (**director**); PROJ-0002 sits in 'PO Query Raised' because the customer's payment terms differ from the offer |
| PC-02 | Project coordination | Give billing and dispatch schedule to Procurement based on PCC | Schedule child tables visible in Procurement workspace; report | Config | P2 | S | 'Billing / Dispatch Schedule' child table on the Project + report, carrying the action note per milestone |
| PC-03 | Project coordination | Check supplier POs against PCC requirement and commercial terms | Validation + 'PO vs PCC' variance report; approval required if over PCC | Custom (script report + server script) | P2 | M | MSCAST PO vs PCC Variance report + PO PCC fields + 'PO over PCC' notification |
| PC-04 | Project coordination | Issue Delivery Instruction to supplier for dispatch to customer site | Custom 'Delivery Instruction' doctype from PO/MDM | Custom (no-code) | P3 | M | DI-2026-00001 with consignee, transporter, LR, vehicle + print format |
| PC-05 | Project coordination | Free-issue list dispatched with Delivery Instruction to sub-contractor | Subcontracting supplied items / Stock Entry; Annexure-I print | Standard + print format | P2/P3 | S | Free-issue stock transfer to 'Free Issue at Vendor' + Annexure-I on the DI print |
| PC-06 | Project coordination | Receive purchase bills, check against PO and Delivery Instruction; original to Accounts, duplicate to Purchase for BRM | BRM register records supplier bill against PO; Purchase Invoice with certification workflow | Custom → Standard + workflow | P2/P4 | M | 3 BRMs against POs. The workflow is Purchase prepares → a director certifies → Accounts marks paid. **It does not follow that three people are involved**: a director also holds a role that can create a BRM and the role that marks it paid (T6g) |
| PC-07 | Project coordination | Prepare Sales Invoice, Delivery Challan and Packing List | Delivery Note, Packing Slip, Sales Invoice; e-way bill | Standard | P3/P4 | S | 6 sales invoices, 3 delivery notes; packing slip not demoed |
| PC-08 | Project coordination | Update stock items and free-issue statement | Stock Ledger; vendor-wise free-issue balance report | Standard + report | P2 | S | MSCAST Free Issue at Vendor report (plate + sections at vendor) |
| PC-09 | Project coordination | Update billing & despatch schedule with consignor, transporter, LR no./date, invoice no./date | Delivery Note transporter/LR/vehicle fields + schedule-vs-actual report | Standard + report | P3 | S | DN carries transporter, LR no./date, vehicle; dispatch schedule report |
| PC-10 | Project coordination | Project code allocation | Project naming series | Config | P0 | S | PROJ-0001 / 0002 / 0003 |
| PC-11 | Project coordination | Update ongoing/new and executed/closed project and Sales Order lists | Project and Sales Order list views/reports with status filters | Standard | P1 | S | List views with status filters |
| PC-12 | Project coordination | Maintain supplier and customer information | Customer/Supplier masters (GSTIN, PAN, MSME/Udyam, contacts, addresses) | Standard + custom fields | P0/P1 | S | **13 customers, 15 suppliers** with GSTIN, state, MSME type and addresses. GSTIN check digits and pincode-to-state validated on entry |
| PC-13 | Project coordination | New Project MIS as per given template | Custom project MIS report per MSCAST template | Custom (script report) | P1/P4 | M | MSCAST Project MIS report (contract vs PCC vs PO vs billed vs hours) |
| PC-14 | Project coordination | Project completion accounting closure reports | Project Profitability + custom closure report | Custom (script report) | P4 | M | 'MSCAST Project Closure Report' with a closure verdict per project |
| PC-15 | Project coordination | Pending Sales Order review | Sales Order Analysis / pending items to deliver and bill | Standard | P1 | S | Pending quantities in the dispatch schedule report |
| PC-16 | Project coordination | Material movement tracking | Stock Ledger, Project-wise Stock Tracking, DI/Delivery Note status | Standard + report | P2/P3 | S | Stock ledger, project-wise stock, stock entries, DI/DN status |
| PC-17 | Project coordination | Proforma Invoice for advance/scheduled supply per SO payment terms | 'Proforma Invoice' print format on Sales Order + Payment Request | Config (print format) | P3 | S | 'MSCAST Proforma Invoice' + advance payment request |
| PC-18 | Project coordination | Supplementary Invoice for retention amount | Payment Terms Template + retention tracker; Retention Receivable account | Custom | P3/P4 | M | Retention reclassified to Retention Receivable on two projects; supplementary invoice against the agreed claim |
| PC-19 | Project coordination | Track Sales Order vs Purchase Order vs Supply Invoice | Custom tracker report SO ↔ PCC ↔ PO ↔ PI ↔ SI | Custom (script report) | P3/P4 | M | 'MSCAST SO - PO - Invoice Tracker' per order |
| E-01 | Engineering | Receive PCC / division scope list | Link on Project; notification | Config | P1 | S | PCC linked from the project; engineering tasks assigned |
| E-02 | Engineering | Prepare engineering programme and design/drawings | Engineering tasks + Drawing Register (revisions, approvals, transmittals, Drive links) | Custom (no-code + **workflow**) | P1 | L | 9 drawings with revision tables and Drive links; MSCAST Drawing Register report. **Driven by the 'MSCAST Drawing Release' workflow**: Draft → For Customer Approval → Approved by Customer → Released for Manufacture → Superseded. *Released for Manufacture* is reachable only from *Approved by Customer* and only by a Projects Manager, so a drawing cannot jump to released without the customer seeing it |
| E-03 | Engineering | Prepare MDF once drawings are final | Engineering BOM or custom 'MDF' doctype with print; generates Material Requests | Config + custom print | P1 | M | 3 MDFs (WSU, Mould, Hydraulics) + MDF print format |
| E-04 | Engineering | Finalise extra bought-out item list | Bought-out item groups; Material Request from BOM/MDF | Standard | P1/P2 | S | Bought-out item groups; Material Request raised from the MDF lists |
| E-05 | Engineering | Send MDF and bought-out list to Procurement; follow up | MDF submit → Material Request + notification; Procurement Tracker report | Config | P2 | S | MSCAST Transmittal register + note print; drawing set issued to the customer (acknowledged) and to the fabricator |
| E-06 | Engineering | Capture engineering man-hours equipment-wise and project-wise | Timesheet with custom 'Equipment' field + man-hour report | Config + custom field/report | P1 | S | Timesheets with Equipment field; 'Engineering Hours by Activity' chart. The overnight checks flag any open project with no time ever booked |
| P-01 | Procurement | Receive PCC, drawings, MDF and bought-out list | Links from Material Request to PCC/Drawing/MDF | Config | P2 | S | PCC, drawings and MDF linked into the procurement flow |
| P-02 | Procurement | Send enquiries to vendors | Request for Quotation | Standard | P2 | S | PUR-RFQ-2026-00001 to 3 suppliers for 3 items |
| P-03 | Procurement | Techno-commercial comparison of offers and supplier selection | Supplier Quotation Comparison + custom technical scoring fields | Custom (light) | P2 | M | 2 supplier quotations with technical score, compliance, deviations, recommended flag |
| P-04 | Procurement | Release PO with technical specifications, price, terms and conditions | Purchase Order + T&C templates + spec attachments | Standard + print format | P2 | S | Purchase orders with terms, PCC reference and budget. **Sent for approval by `Purchase User`, approved by a director; nobody holds both roles**, so a purchase order always passes through two people |
| P-05 | Procurement | Release drawings and MDF to equipment manufacturers | Drawing transmittal from Drawing Register | Custom (part of E-02) | P2 | S | TRN-2026-00002 to Pushkar Fabricators with revision and sheet counts |
| P-06 | Procurement | Arrange bought-outs and supply them to the manufacturer | Subcontracting supplied items / Stock Entry to vendor | Standard | P2 | S | Free issue of plate and sections to the fabricator |
| P-07 | Procurement | Supplier follow-up; coordinate inspection of equipment and bought-outs | Quality Inspection Templates + custom Inspection Plan per PO/project | Standard + custom | P2 | M | 4 inspection plans + templates on 4 items + 2 incoming inspections |
| P-08 | Procurement | Release supplier payments against invoice/proforma/internal memo invoice with certification via Billing Routing Memo (BRM) to Accounts | Custom 'BRM' doctype + workflow; Payment Entry allowed only against a certified BRM | Custom (no-code + server script) | P2/P4 | M | 3 BRMs + print format + BRM Register report. Purchase prepares and may reject; **a director certifies**; Accounts marks paid. Certification sits with a director because certifying is what releases the money. **Known limitation (T6g):** a director also holds roles that can create a BRM and mark it paid, so the certificate does not by itself prove three people were involved. The payment block does hold for everyone |
| P-09 | Procurement | Track POs against PCC and update status (PCC updation) | PO vs PCC report + PCC status column | Custom (report) | P2 | S | MSCAST PO vs PCC Variance report with committed % and variance |
| P-10 | Procurement | Collect vendor stock declaration of free-issue items project-wise | Vendor-wise, project-wise supplied-item balance report | Standard + custom | P2 | S | Free Issue at Vendor report by item and value |
| P-11 | Procurement | Prepare Material Dispatch Memo (MDM) → Delivery Instruction to supplier | Custom 'MDM' doctype → creates Delivery Instruction | Custom (no-code) | P3 | M | MDM-2026-00001 with free-issue flag + print format |
| P-12 | Procurement | Free-issue items list as Annexure-I with MDM | Annexure-I print format from MDM/Subcontracting data | Config (print format) | P3 | S | Annexure-I printed with the Delivery Instruction |
| P-13 | Procurement | Performance Bank Guarantee (PBG) certification | Bank Guarantee doctype + expiry notifications + BG register | Standard + config | P3 | S | 2 bank guarantees (ABG + PBG) with validity + 30-day expiry notification. The overnight checks also raise an exception as expiry approaches |
| EC-01 | Erection & Commissioning | Erection and commissioning of CCM at site | Site tasks, site timesheets, Expense Claims, commissioning report | Standard + config | P3 | S | MSCAST Commissioning Report: 5 performance parameters, 6 trial heats, punch list, provisional acceptance + signature print |
| EC-02 | Operations flow | Inspection → Packing → Loading → Transport → Commissioning | Quality Inspection gate before Delivery Note; Packing Slip; e-way bill | Standard + config | P2/P3 | S | Quality inspection → delivery note with transport details; packing slip not demoed |
| A-01 | Accounts | Check PO and contract before giving credit to vendor | Supplier payment terms; Purchase Invoice linked to PO; hold/approval | Standard | P4 | S | Supplier credit limit set + PO/contract check |
| A-02 | Accounts | Purchase voucher entries for bought-outs and equipment with taxes, duties, freight | Purchase Invoice with tax templates; Landed Cost Voucher | Standard | P4 | S | Landed cost voucher MAT-LCV-2026-00001 (Rs 45,000 freight) apportioned onto the mould-tube receipt |
| A-03 | Accounts | Check purchase invoices against PO qty, rates, terms | PO–PR–PI matching; over-billing allowance = 0 | Standard | P4 | S | Purchase invoice matched to the purchase receipt and PO |
| A-04 | Accounts | Sales entry from sales invoice raised by project coordinator | Sales Invoice (e-invoice if applicable) | Standard | P4 | S | Intra-state CGST+SGST, inter-state IGST and services invoices |
| A-05 | Accounts | Project payments only after BRM from Procurement | Payment Entry **and Journal Entry** validation against a certified BRM | Custom (**application code**, `mscast_erp.controls.brm_payment`) | P4 | S | **Verified live on every build, on six routes** (T6a): a bill with no certified BRM cannot be paid by payment entry, by journal entry, or as an advance with no reference; a payment above the certified amount is refused; an already-paid BRM cannot fund a second payment. Holds for every user including a director. Bills that cannot be certified against a PO — electricity, rent, statutory — are released by ticking *Exempt from BRM certification* on the supplier (0 of 15 ticked at handover). Moved out of a Server Script into the app on 21 Sep so it is version-controlled, shipped in the image and testable |
| A-06 | Accounts | Non-project payments: admin, utilities, credit cards, government, salary | Payment Entry / Journal Entry | Standard | P4 | S | 6 journal vouchers: electricity, petty cash imprest and spend, foreign travel, insurance, cargo agency |
| A-07 | Accounts | Petty cash payments | Petty cash account + Mode of Payment; Employee Advance for imprest | Config | P4 | S | Petty Cash account + 'Cash' mode of payment |
| A-08 | Accounts | Customer receipts and receipt to customer | Payment Entry (Receive) + receipt print format | Standard | P4 | S | Advance receipts against ABG across projects |
| A-09 | Accounts | Cheque printing | Cheque Print Template (bank-wise) | Standard | P4 | S | 'MSCAST Payment Receipt' print format with amount in words and allocation table; HDFC cheque template configured |
| A-10 | Accounts | Cash receipts against travel advances and sale of old items | Employee Advance return; asset/scrap sale invoice | Standard | P4/P5 | S | Configured |
| A-11 | Accounts | Debit/credit notes per PO terms | Debit Note / Credit Note | Standard | P4 | S | Credit note (sales rejection) and debit note (rate difference) |
| A-12 | Accounts | Journal vouchers: travel, asset purchase, insurance, year-end, cargo agencies | Journal Entry; multi-currency Expense Claim; Landed Cost Voucher | Standard | P4 | S | Foreign travel, marine + erection insurance, cargo agency vouchers |
| A-13 | Accounts | Monthly MIS reflecting monthly project costs | Cost Centre/Project dimension P&L + PCC vs actual MIS | Custom (report) | P4 | M | MSCAST Project MIS + PO vs PCC variance. Every ledger entry is checked to carry a cost centre |
| A-14 | Accounts | Monthly Balance Sheet, P&L, Funds Flow / Cash Flow | Balance Sheet, P&L, Cash Flow; Schedule III templates | Standard | P4 | S | Schedule III balance sheet and P&L in the statutory vertical format - verified to balance to the rupee and the profit ties to the ledger surplus. Plus the 2021-amendment disclosures and the eleven prescribed ratios (guarded so immaterial denominators show n/a). ASSUMPTION: format still to be signed off by the CA |
| M-01 | Management modules | Employee management: leave, attendance, hours, salary slips | Frappe HR + india-payroll salary slips | Standard | P5 | M | 6 employees, 150 attendance records, leave, 6 salary slips, expense claim |
| M-02 | Management modules | Finance Scaling Management | Unclear requirement | Open question | P0 | – | 'MSCAST Finance Scaling - Funding and Capacity': order book and pipeline against scheduled collections, committed outflows, cash, the Rs 2.5 Cr sanctioned HDFC limit and the projected 90-day headroom. ASSUMPTION: never defined by MSCAST - read as whether the business can fund the order book it is chasing (Q1) |
| M-03 | Management modules | Biometric door lock/unlock integration for attendance | Employee Checkin API + Shift Type auto-attendance; device sync agent | Integration | P5 | M | Shift type with auto attendance, 72 punches from device MSCAST-DOOR-01 converted into Attendance, plus the audit report. **The scheduled pull job is switched off** - it must be enabled and proven against manually checked attendance before payroll relies on it. ASSUMPTION: no device model given, so the standard push pattern is modelled (Q6) |
| M-04 | Management modules | Customer & supplier management | Customer/Supplier masters, portal, scorecard | Standard | P1 | S | Masters with GST, MSME, capability and scorecard |
| AC-01 | Accounts POV (compliance) | Audit trail facility (MCA rule from 1 Apr 2023) with auditor login | India Compliance audit trail (cannot be disabled once on) + a read-only auditor role + Accounting Period freeze | Config | P0/P4 | S | Audit trail enabled before first entry. **Auditor** role: read / report / print / export only, including Version history and GL Entry, held by the external CA (S. Joshi) - no write anywhere. *Correction carried from v1.6: `MSCAST Director` is **not** a read-only role. It is the approving role, carrying PCC approval, purchase order approval, BRM certification and kick-off approval. The `@mscast.demo` read-only demo logins were retired when the users were rebuilt as named people* |
| AC-02 | Accounts POV (compliance) | Edit log of each transaction in ERP | Version log on all ledger doctypes; 'Audit Trail' report | Standard | P0 | S | Version log + India Compliance Audit Trail report |
| AC-03 | Accounts POV (controls) | Alerts for incomplete data, masters and transactions | Notifications + Auto Email Reports on saved 'missing data' reports | Config | P1→P4 | S | 9 enabled notifications (BG expiry, PO over PCC, drawing approval) + scheduled reports, **all resolving to a live mailbox** - checked on every harness run. Plus the 16-rule overnight sweep, which is the systematic version of this requirement |
| AC-04 | Accounts POV (controls) | Emailing of all possible outputs | Email button with PDF print format; Notification attach print; Auto Email Report | Standard | All | S | Outgoing mail live through Purelymail; SPF, DKIM and DMARC all pass at Gmail; site host_name set so document links resolve publicly |
| AC-05 | Accounts POV (controls) | Daily SMS to COO/CFO: major-value transactions; revenue & receipts vs purchases & expenses; MIS | SMS needs TRAI DLT registration and fixed templates - poor fit for a multi-figure summary. Email / WhatsApp / Google Chat recommended | Config + custom (small) | P2 / P4 | M | Daily management summary (20 indicators with an Attention column) at **08:30 IST**, plus the **AI morning note at 08:35** which ranks the day's exceptions and names what matters most, emailed to the directors with every item linked. Google Chat webhooks for transactions above Rs 5 L are configured and left disabled pending the space URL |
| AC-06 | Accounts POV (Companies Act s.128) | Books in electronic mode; director inspection; 8-year retention; ERP provider undertaking | India VPS with daily India backups (Rule 3(5)); GPL software cannot be withdrawn; yearly archive dumps; IT policy | Config + policy | P0/P4 | S | MSCAST Archival Log + monthly scheduled script + 8-year retention note + rolling backups. Off-site India copy is a production step |
| AC-07 | Accounts POV (standards) | Indian Accounting Standards list | MSCAST likely follows Companies (AS) Rules 2021 as an SMC; Ind AS applies only at net worth ≥ ₹250 Cr | External (CA) | P0 | – | 'MSCAST Notes to Accounts' - 25 notes including MSMED s.22, related party (AS 18), contingent liabilities from live bank guarantees, CWIP ageing, EPS basis, audit-trail note and the Schedule III negative disclosures. ASSUMPTION: SMC reporting under AS, stated on the face of the note |
| AC-08 | Accounts POV (equity & liabilities) | Share capital: authorised, issued; reconciliation of shares; >5% shareholders; rights | Share capital accounts; Shareholder/Share Transfer records | Config / External | P4 | S | 3 shareholders, Share Type Equity, 10,000 equity shares of Rs 10 (paid-up Rs 1,00,000). **Held as Promoter A / B / C** - invented percentages are not attributed to real named directors in a demonstration |
| AC-09 | Accounts POV (equity & liabilities) | Reserves & surplus; borrowings; lease liabilities | Chart of accounts (Schedule III grouping); lease entries by JV | Config | P4 | S | Reserves and Surplus, Borrowings - HDFC Term Loan, Lease Liabilities, Prior Period Expenses, Fines and Penalties, Retention Receivable, Petty Cash |
| AC-10 | Accounts POV (equity & liabilities) | Trade payables split: micro & small enterprises vs others | Custom Supplier fields (Udyam no., class) + 45-day dues report | Custom (fields + script report) | P2 / P4 | M | Suppliers tagged Micro/Small with Udyam numbers; 'MSCAST MSME 45-Day Dues' report with days-beyond-45 and disallowance flag. The overnight checks raise an exception as a bill approaches day 45 |
| AC-11 | Accounts POV (equity & liabilities) | Provisions: gratuity, actuarial valuation & entries; income tax; deferred tax | Frappe HR Gratuity; liability valuation external → JV; tax & deferred tax by JV | Standard + External | P5 / P4 | S | Gratuity Rule + provision Rs 9.91 L; current tax Rs 5.23 L at 25.168% (s.115BAA); deferred tax with DTA on gratuity and DTL on depreciation timing. ASSUMPTIONS stated in each voucher narration |
| AC-12 | Accounts POV (assets) | Fixed asset register: additions, asset ID, disposals, depreciation | Asset with depreciation schedules, two Finance Books, disposal/scrap | Standard + config | P4 | S | 4 assets submitted with depreciation schedules |
| AC-13 | Accounts POV (assets) | Identification of own assets vs customer-owned assets | Separate register (custom doctype) | Custom (small) | P4 | S | MSCAST Customer Asset register - customer-supplied mould tube set and gauges held at the sub-contractor, explicitly not capitalised |
| AC-14 | Accounts POV (assets) | Intangible assets: software, life, amortisation, under development | Intangible Asset Category with SLM amortisation; CWIP | Config | P4 | S | 'Software (Intangible)' category + ERP licence Rs 2.40 L amortised over 36 months |
| AC-15 | Accounts POV (assets) | Capital work-in-progress list with completion status | CWIP accounting on Asset Category + Asset Capitalization | Standard + config | P4 | S | 'Plant under construction (CWIP)' category; Rs 7.80 L in CWIP; available for use in 3 months |
| AC-16 | Accounts POV (inventory) | Closing stock register category-wise and item-wise | Stock Balance by item group/warehouse | Standard | P2/P4 | S | Stock Balance by item group and warehouse |
| AC-17 | Accounts POV (inventory) | Working of valuation of semi-finished inventory (WIP) | Project WIP account + JV on sale | Custom / design decision | P3 / P4 | M | 'MSCAST Project WIP Valuation' report carrying Rs 26.71 L. Method: bought-out billed + material issued + engineering hours at Rs 450/hr + 12% works overhead, less the cost of the billed portion. ASSUMPTION: method needs the auditor's blessing (D6) |
| AC-18 | Accounts POV (inventory) | GST on closing inventory | Not a regular GST concept (ITC reversal only on cancellation) | Open question | P0 | – | 'MSCAST GST on Closing Inventory (ITC and ITC-04)' - stock by warehouse with HSN, value, embedded ITC and the treatment note, separating stock at the job worker (ITC-04, one-year rule) from stock on own premises |
| AC-19 | Accounts POV (sales) | Sales reconciliation incl. with GSTR-1; rate difference; rejections | GSTR-1 (Books vs Filed); credit/debit notes; sales returns | Standard | P4 | S | GST sales invoices with correct CGST/SGST vs IGST - **checked against the place of supply on every invoice, every harness run**; GSTR-1 and GST Sales Register available |
| AC-20 | Accounts POV (purchase) | Purchase reconciliation with GSTR; rejections | Purchase Reconciliation Tool (GSTR-2A/2B); purchase returns | Standard | P4 | S | PINV with input IGST; Purchase Reconciliation Tool available |
| AC-21 | Accounts POV (expenses) | Expenses: monthly volume, last-year comparison, ratio to sales | P&L Growth View and Margin View | Standard | P4 | S | 'MSCAST Expense Analysis (vs last year, % of sales)' report |
| AC-22 | Accounts POV (expenses) | TDS deduction on expenses | Tax Withholding Categories (194C/194J etc.) | Standard | P4 | S | TDS 194C category (2%) on the fabricator, with TDS deducted on the invoice |
| AC-23 | Accounts POV (payroll) | Monthly payroll matching all deductions: PF, ESI, PT, TDS | Salary Register + PF/ESI/PT/TDS registers | Standard (+ bug check) | P5 | M | 6 salary slips with PF 12%, ESIC, Professional Tax MH and TDS; india_payroll registers need statutory config. v16 Maharashtra PT women-exemption bug to be checked before go-live |
| AC-24 | Accounts POV (expenses) | Prior period expenses; fines & penalties under any law | Separate GL accounts + JV tagging | Config | P4 | S | Both accounts created |
| AC-25 | Accounts POV (expenses) | Warranty claims | Warranty Claim + Maintenance Visit; warranty provision account | Standard | P5 | S | 1 open warranty claim against a spare roll |

## Built beyond the requirement list

| Area | What was built |
|---|---|
| **Packaged as an installable app** | `mscast_erp` carries every doctype, report, print format, workflow, control and the theme, so the system rebuilds on a server rather than only on the build laptop. Tagged release `v0.9.0` |
| **Overnight exception engine** | 16 rules at 06:00 comparing documents against each other and the calendar - uncertified bills, MSME clock, guarantee expiry, projects with no time booked, dispatch without paperwork. Writes to the MSCAST Exception list with severity, document and suggested action. No model, no network, no cost |
| **AI morning briefing** | 08:35, turns the findings plus the management summary into a few sentences naming what matters most today, emailed to the directors with every item linked. Falls back to a plain list if the model is unreachable, so a missing model never means a missing morning email |
| **Post-deploy control verification** | Six control transitions verified and repaired after every install and upgrade, with a banner and an Error Log entry. Written after an install silently reverted the approval rules |
| Branding | MSCAST logo, favicon, app name, login branding, navy/amber desk theme, role-scoped workspaces |
| Executive dashboard | KPI number cards and charts on the MSCAST workspace, plus a role-aware home page |
| Letterhead | MSCAST letterhead with address, CIN, GSTIN, IEC on all custom print formats, with a demonstration watermark |
| MSCAST forms | **25 doctypes** (8 of them child tables) |
| Print formats | **16** MSCAST print formats; every one with a sample document is rendered as part of the build checks |
| Custom reports | **28** MSCAST query reports |
| Controls | BRM payment block, four approval workflows plus the drawing release workflow, monthly archival job |
| Roles | `MSCAST Director` (approving) and `Auditor` (read-only including Version history), plus `Design User` so the drawing office can issue but not release |
| Automation | 9 notifications, email digest, 3 scheduled email reports, 10 email templates |
| GST masters | 18,687 HSN codes, GST accounts, item tax templates, tax categories, addresses with GSTIN |
| Demo dataset | **3 projects** at different stages including one full lifecycle to certificate, **63 items**, **28 parties**, **14 installed machines** (2009–2024), **14 bid outcomes**, 4 assets, 6 employees with payroll, **13 staff logins** (12 named people plus the site administrator) with a real approval matrix |
| Public demo URL | Cloudflare Tunnel to `https://mscast.carobar.net` - own domain, valid certificate, no client software |
| Repeatable build | **114 idempotent seed scripts** + the operational script set; custom Docker image with 5 apps; a clean build proven from the repository onto an empty site |
| Statutory pack | Schedule III balance sheet and P&L that balance to the rupee, ageing, the eleven prescribed ratios, 25 notes to accounts |
| Test harness | **27 automated checks** covering SQL literals against real field options, report execution, Indian dates, print rendering, ledger integrity, the payment control, **the approval authority**, **segregation of duties on two independent axes**, **who holds System Manager**, seeded-data validity, GST place of supply, mail and payroll |
| Documentation | Client Setup Guide, SOPs and Use Cases, **Role Cards** (one page per role), Production Cutover Runbook, Independent Review, Data Request Covering Note, this matrix |

## What still stands between this and production

- Six items rest on stated assumptions that MSCAST or the CA should confirm: the Schedule III format, the SMC/AS basis, the WIP valuation method, the s.115BAA tax rate, the meaning of 'Finance Scaling Management', and the biometric device model
- Comparative (previous year) columns fill only when the Tally opening balances are migrated
- Google Chat webhooks are configured but disabled - they need the space URL
- **The biometric attendance pull is switched off** and must be enabled and proven before payroll relies on it
- **The Administrator password must be rotated** before the system carries real data on a server
- **`reset-poc.sh` has not been run end to end** since the four most recent scripts were added to it. Each was verified individually against the live site, but the claim that the system rebuilds from nothing is currently untested
- Opening data migration from Tally, production VPS, HTTPS and daily India-hosted backups
- The AI briefing points at a model router on the build laptop; a server needs a hosted endpoint — three configuration lines, no code change

*Closed since v1.6: the setup-wizard administrator held 41 roles and has been cut back to `System Manager` alone; an operational staff account was found also holding `System Manager` and has had it removed. Both are now asserted on every build by T6f.*

*Closed since v1.5: the Gemini automation layer. It is built and running — the rule sweep and the AI morning note both work end to end.*

## Open questions (now answered by assumption, still worth confirming)

| # | Topic | Question | Related IDs |
|---|---|---|---|
| Q1 | Finance Scaling Management | What exactly is meant (budgets, cash-flow forecasting, multi-entity growth, credit limits)? | M-02 |
| Q2 | PCC | Share the current PCC template, who prepares/approves it, how often it is revised, and whether it is at component or assembly level. | S-02, PC-03, P-09 |
| Q3 | Project MIS | Share the 'New Project MIS' template and the monthly project cost MIS format. | PC-13, A-13 |
| Q4 | BRM | Share the Billing Routing Memo format, approvers and payment release rules. **Certification currently sits with a director — confirm that matches MSCAST's intent.** | P-08, A-05 |
| Q5 | MDM / DI / Annexure-I | Share sample Material Dispatch Memo, Delivery Instruction and Annexure-I. | P-11, PC-04, P-12 |
| Q6 | Biometric access control | Device make/model and count; network; should ERP only read punches or also control door lock/unlock? | M-03 |
| Q7 | Daily SMS | Recipients; is WhatsApp/Google Chat/email acceptable instead of SMS? Is DLT registration done? | AC-05 |
| Q8 | Customer-owned assets | What are these assets? How are they recorded today? | AC-13 |
| Q9 | GST on closing inventory | What report/working is expected? | AC-18 |
| Q10 | Accounting standards | CA to confirm AS vs Ind AS and SMC/small-company status; cash flow statement needed? | AC-07, A-14 |
| Q11 | WIP valuation | How is project WIP valued in Tally today? | AC-17 |
| Q12 | Payroll | Headcount under PF/ESI; current payroll provider; gratuity valuation method. | M-01, AC-23, AC-11 |
| Q13 | 8-year undertaking | Is an open-source + archival/backup policy acceptable in place of a vendor undertaking? | AC-06 |
| Q14 | Additional claims | How are claims agreed and billed? | PR-07 |
| Q15 | Spares Dept | Separate team? Spares from stock or order-based? Price lists? | PR-09 |
| Q16 | Foreign travel / exports | Frequency, currencies, export orders? | A-12 |
| Q17 | Equipment-wise man-hours | Which list defines 'equipment'? | E-06 |
| Q18 | Flowchart order | Are long-lead bought-outs ordered before design is complete? | E-04, P-04 |
| Q19 | Share register | Keep shareholder/share transfer records in ERP, or with the company secretary? | AC-08 |
| **Q20** | **Self-approval on the cost sheet and the kick-off** | **A director can currently prepare a PCC or verify a customer PO and then approve it alone. Accepted for a company of this size and documented — but confirm it is intended, or move preparation to staff.** | **S-02, PC-01** |
| **Q21** | **Self-certification on supplier bills** | **A director can create a BRM, certify it and mark it paid — all three, alone. This is the more consequential of the two, because it is the step that releases money to an outside party. Confirm it is intended, or take `Projects Manager` off the director accounts so that preparing a BRM requires Purchase.** | **P-08, PC-06, A-05** |
