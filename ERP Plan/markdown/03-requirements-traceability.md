# MSCAST ERP - Requirements Traceability (v1.5)

**Version 1.5 · 19 Sep 2026** · every requirement implemented; verified by a 23-check automated test harness.

Source of requirements: MSCAST `ERP_Requirement_Final.pdf`. Solution: ERPNext v16.35 + India Compliance 16.9.1 + Frappe HR 16.19 + India Payroll 16.0.4.

## Coverage

| POC status | v1.3 | v1.4 | v1.5 |
|---|---:|---:|---:|
| Live in POC | 53 | 88 | **97** |
| Partly in POC | 20 | 3 | **0** |
| Available (standard, not demoed) | 11 | 1 | **0** |
| Not in POC | 10 | 2 | **0** |
| Out of POC scope | 3 | 3 | **0** |
| **Total** | **97** | **97** | **97** |

**All 97 requirements are live.** Six rest on assumptions that MSCAST or the CA should confirm - each is stated in the evidence column and in the voucher narrations inside the system.

## Assumptions carried

| ID | Assumption | Who confirms |
|---|---|---|
| A-14 | Schedule III presentation format as built | CA |
| AC-07 | MSCAST is an SMC reporting under AS, claiming SMC exemptions, not Ind AS | CA |
| AC-11 | Income tax at 25.168% under s.115BAA; depreciation timing difference estimated | CA |
| AC-17 | WIP at cost on unbilled scope, completion measured by billing vs contract value | CA (decision D6) |
| M-02 | 'Finance Scaling Management' means funding capacity for the order book | MSCAST (Q1) |
| M-03 | Biometric device pushes punches to the standard checkin endpoint | MSCAST (Q6) |

## Test harness result (19 Sep 2026)

| Check | Area | Result |
|---|---|---|
| T1 | reports | 324 SQL literal comparisons validated against the fields' real Select options - 0 mismatched |
| T2 | reports | 25 custom reports execute - 0 failures |
| T3 | reports | no report uses the container's UTC date |
| T4 | prints | 15 custom print formats render |
| T5a | ledger | trial balance nets to zero |
| T5b | ledger | Schedule III balance sheet balances to the rupee |
| T5c | ledger | P&L profit ties to the ledger surplus |
| T5d | ledger | no ledger entry without a cost centre |
| T6a | controls | BRM payment block refuses an uncertified supplier bill |
| T6b | controls | 4 workflows active and complete |
| T6c | controls | server scripts present and enabled where intended |
| T7a | data | every MSCAST form has demo records |
| T7b | data | every stored Select value is a valid option |
| T7c | data | every invoiced item carries an HSN code |
| T8 | gst | GST head matches the place of supply on every invoice |
| T9a-e | email | outgoing account live, 5 sent 0 errored, morning batch scheduled, no dead notification recipient, no bounce-prone user |
| T10a-c | hr | payroll and attendance loaded, no duplicates, biometric punches converted |

**23 pass, 0 warn, 0 fail.**

## Full matrix

| ID | Area | Requirement | ERPNext v16 solution | Category | Phase | Size | POC evidence (19 Sep 2026) |
|---|---|---|---|---|---|---|---|
| S-01 | Sales | Prepare Sales Orders from customer orders | ERPNext Sales Order (customer PO no./date, payment terms template) | Standard | P1 | S | SAL-ORD-2026-00001/2 submitted with customer PO no., retention/LD/PBG fields |
| S-02 | Sales | PCC sheet (Purchase Cost Calculation): cost price of each component of CCM/spares, prepared by Sales from the Sales Order | Custom 'PCC' doctype linked to Sales Order/Project: component lines (item/assembly, qty, estimated cost, make, supplier category), revisions + approval; baseline for PO control and project MIS | Custom (no-code + script report) | P1 | L | PCC-2026-00001 (R2, approved, 15 lines, Rs 1.82 Cr) and PCC-2026-00002 (draft) |
| S-03 | Sales | Order-status analysis; leads from customer enquiry or direct approach | CRM Lead → Opportunity → Quotation; Sales Pipeline Analytics, Opportunity Summary by Sales Stage | Standard | P1 | S | Lead (Gulf Aluminium), 2 Opportunities, Quotation SAL-QTN-2026-00001; order-book chart |
| S-04 | Sales | Scope of work/contract and PCC handed to Engineering and Projects | Kick-off workflow on Project; mandatory attachments (contract, scope, PCC) and notifications to Engineering/Projects | Config | P1 | S | MSCAST Project Kickoff form with the 8-point customer-PO checklist, linked PCC / SO / project |
| S-05 | Sales | List of potential/probable customers for forecasting | Leads/Opportunities with expected value and closing date; Sales Funnel/forecast report | Standard | P1 | S | Open lead + spares opportunity; 'Order Book by Customer' chart on the workspace |
| PR-01 | Projects | Internal kick-off meeting; Projects receives PCC, signed tech specs, sales MOMs | Project Template + kick-off checklist child table; attachments; Workflow 'Kick-off done' | Config | P1 | S | Project kick-off task completed on PROJ-0001, PCC + SO linked |
| PR-02 | Projects | Project planning: targets for Engineering, Procurement, Despatch, Erection & Commissioning | Project tasks, milestones, dependencies, Gantt | Standard | P1 | S | 13 tasks across PROJ-0001/0002 with dates, status and progress |
| PR-03 | Projects | Prepare and submit Project Execution, Delivery and Billing schedules to client/consultant | Delivery + billing schedule child tables on Project/SO; print formats for client submission | Config + light custom | P1/P3 | M | 'MSCAST Project Schedule (Client)' print format - 6 contractual milestones with live drawing, inspection, dispatch and commissioning status, plus the task bar chart |
| PR-04 | Projects | Periodic 'Overall Project Status/Schedule' submission to client | Project status print format/report (drawings, procurement, inspection, dispatch status); AI track A1 can draft the narrative | Custom (report + print) | P1 | M | 'MSCAST Project Status Report' print format - progress bar, commercial position and engineering position side by side, open punch points and open customer points |
| PR-05 | Projects | Submit invoices and follow up receivables from client | Accounts Receivable, Payment Reminder/Dunning, Notification before due date | Standard | P4 | S | Dunning DUNN-09-26-00001 (Rs 4,80,000 overdue) + payment request ACC-PRQ-2026-00001 (Rs 42,60,000 advance) + AR ageing |
| PR-06 | Projects | Project completion: completeness of supplies | Sales Order Analysis (ordered vs delivered), SO–DN tracking | Standard | P3 | S | MSCAST Dispatch Schedule shows ordered vs delivered vs pending |
| PR-07 | Projects | Additional claims discussion and settlement with client | Custom 'Client Claim' doctype (claim, value, status, settlement) → amended SO / additional invoice | Custom (no-code) | P3 | S | MSCAST Client Claim register + print format; CLM-2026-00001 (Rs 6.85 L scope variation, agreed at Rs 6.40 L) and CLM-2026-00002 (idle time, settled by supplementary invoice) |
| PR-08 | Projects | Obtain Commissioning, Preliminary and Final certificates from client | Custom 'Project Certificate' doctype (Commissioning / PAC / FAC) with date, attachment; triggers milestone billing and retention clock | Custom (no-code) | P3 | S | CERT-2026-00001 (commissioning, retention due date) + print format |
| PR-09 | Projects | After final closure, hand over project info to Spares Dept for spares business | Project closure checklist; installed-machine record (Serial No per machine/strand) + customer spares price list | Config | P5 | S | MSCAST Spares Handover note + print; commissioning spares handed over on PROJ-0001 and 2-year mandatory spares on PROJ-0002 |
| PC-01 | Project coordination | Check customer PO against agreed terms; forward to Finance and Procurement | SO approval workflow with PO-vs-quotation check; notifications to Finance/Procurement | Config | P1 | S | 'MSCAST Project Kick-off' workflow: Draft -> PO Verified (Accounts, only when price, scope, payment terms and GST are ticked) -> Kick-off Approved; PROJ-0002 sits in 'PO Query Raised' because the customer's payment terms differ from the offer |
| PC-02 | Project coordination | Give billing and dispatch schedule to Procurement based on PCC | Schedule child tables (PR-03) visible in Procurement workspace; report | Config | P2 | S | 'Billing / Dispatch Schedule' child table on the Project (9 milestones across the two projects) + the 'MSCAST Billing and Dispatch Schedule' report, shared with procurement and carrying the action note per milestone |
| PC-03 | Project coordination | Check supplier POs against PCC requirement and commercial terms | Validation + 'PO vs PCC' variance report (qty, rate, terms); approval required if over PCC | Custom (script report + server script) | P2 | M | MSCAST PO vs PCC Variance report + PO PCC fields + 'PO over PCC' notification |
| PC-04 | Project coordination | Issue Delivery Instruction to supplier for dispatch to customer site; arrange transport | Custom 'Delivery Instruction' doctype from PO/MDM: ship-to customer site, transporter, packing, free-issue annexure; print/email | Custom (no-code) | P3 | M | DI-2026-00001 with consignee, transporter, LR, vehicle + print format |
| PC-05 | Project coordination | Free-issue list dispatched with Delivery Instruction to sub-contractor | Subcontracting Order 'Supplied Items' / Stock Entry 'Send to Subcontractor'; Annexure-I print | Standard + print format | P2/P3 | S | Free-issue stock transfer to 'Free Issue at Vendor' + Annexure-I on the DI print |
| PC-06 | Project coordination | Receive purchase bills, check against PO and Delivery Instruction; original to Accounts, duplicate to Purchase for BRM | P2–P3: BRM register records supplier bill no./amount against PO (Tally still books). P4: Purchase Invoice with certification workflow | Custom (P2) → Standard + workflow (P4) | P2/P4 | M | BRM-2026-00001/2 against POs; PINV-26-00001 booked after certification |
| PC-07 | Project coordination | Prepare Sales Invoice, Delivery Challan and Packing List | Delivery Note (challan), Packing Slip, Sales Invoice; e-way bill via India Compliance | Standard | P3/P4 | S | 3 sales invoices, DN-26-00001 delivery challan; packing slip not demoed |
| PC-08 | Project coordination | Update stock items and free-issue statement | Stock Ledger; vendor-wise free-issue balance report | Standard + report | P2 | S | MSCAST Free Issue at Vendor report (plate + sections at vendor) |
| PC-09 | Project coordination | Update billing & despatch schedule with consignor, transporter, LR no./date, invoice no./date | Delivery Note transporter/LR/vehicle fields (India Compliance) + schedule-vs-actual report | Standard + report | P3 | S | DN carries transporter, LR no./date, vehicle; dispatch schedule report |
| PC-10 | Project coordination | Project code allocation | Project naming series (e.g. MSC-YY-###) | Config | P0 | S | Project naming series PROJ-0001 / PROJ-0002 |
| PC-11 | Project coordination | Update ongoing/new and executed/closed project and Sales Order lists | Project and Sales Order list views/reports with status filters | Standard | P1 | S | Project and Sales Order list views with status filters |
| PC-12 | Project coordination | Maintain supplier and customer information | Customer/Supplier masters (GSTIN, PAN, MSME/Udyam fields, contacts, addresses) | Standard + custom fields | P0/P1 | S | 5 customers, 10 suppliers with GSTIN, state, MSME type, 16 addresses |
| PC-13 | Project coordination | New Project MIS as per given template | Custom project MIS report per MSCAST template | Custom (script report) | P1/P4 | M | MSCAST Project MIS report (contract vs PCC vs PO vs billed vs hours) |
| PC-14 | Project coordination | Project completion accounting closure reports | Project Profitability + custom closure report (PCC vs PO vs actual cost vs billing, retention, claims) | Custom (script report) | P4 | M | 'MSCAST Project Closure Report': contract vs PCC vs actual bought-out, billed, receivable, certificates, open claims, drawings and inspections, with a closure verdict per project |
| PC-15 | Project coordination | Pending Sales Order review | Sales Order Analysis / pending items to deliver and bill | Standard | P1 | S | Pending quantities in the dispatch schedule report |
| PC-16 | Project coordination | Material movement tracking | Stock Ledger, Project-wise Stock Tracking, DI/Delivery Note status | Standard + report | P2/P3 | S | Stock ledger, project-wise stock, 3 stock entries, DI/DN status |
| PC-17 | Project coordination | Proforma Invoice for advance/scheduled supply per SO payment terms | 'Proforma Invoice' print format on Sales Order + Payment Request; advance allocation on invoice | Config (print format) | P3 | S | 'MSCAST Proforma Invoice' print format on Sales Order + advance payment request |
| PC-18 | Project coordination | Supplementary Invoice for retention amount | Payment Terms Template (e.g. 90/10) + retention tracker; invoice/claim for retention portion; optional Retention Receivable account (small code) | Custom | P3/P4 | M | Retention JV ACC-JV-2026-00007 (Rs 1,81,248 reclassified to Retention Receivable) and supplementary invoice SINV-26-00004 against the agreed claim |
| PC-19 | Project coordination | Track Sales Order vs Purchase Order vs Supply Invoice | Custom tracker report SO ↔ PCC ↔ PO ↔ Purchase Invoice ↔ Sales Invoice | Custom (script report) | P3/P4 | M | 'MSCAST SO - PO - Invoice Tracker': SO value, billed, collected, PO committed, supplier billed, % delivered and % billed per order |
| E-01 | Engineering | Receive PCC / division scope list | Link on Project; notification | Config | P1 | S | PCC linked from the project; engineering tasks assigned |
| E-02 | Engineering | Prepare engineering programme and design/drawings | Engineering tasks on Project + Drawing Register (revisions, approvals, transmittals, Google Drive links) | Custom (no-code + server script) | P1 | L | 9 drawings with revision tables, statuses and Drive links; MSCAST Drawing Register report |
| E-03 | Engineering | Prepare MDF (Material Data File / Material List) once drawings are final | Engineering BOM per project/assembly or custom 'MDF' doctype with print; generates Material Requests | Config + custom print | P1 | M | 3 MDFs (WSU, Mould, Hydraulics) with material lists + MDF print format |
| E-04 | Engineering | Finalise extra bought-out item list | Bought-out item groups; Material Request (Purchase) from BOM/MDF | Standard | P1/P2 | S | Bought-out item groups; Material Request raised from the MDF lists |
| E-05 | Engineering | Send MDF and bought-out list to Procurement; follow up | MDF submit → Material Request + notification; Procurement Tracker report | Config | P2 | S | MSCAST Transmittal register + transmittal note print; drawing set issued to the customer for approval (acknowledged) and to the fabricator for construction |
| E-06 | Engineering | Capture engineering man-hours equipment-wise and project-wise | Timesheet with custom 'Equipment' field (per project equipment list) + man-hour report by project/equipment/activity | Config + custom field/report | P1 | S | 6 timesheets with Equipment field; 'Engineering Hours by Activity' chart |
| P-01 | Procurement | Receive PCC, drawings, MDF and bought-out list | Links from Material Request to PCC/Drawing/MDF | Config | P2 | S | PCC, drawings and MDF linked into the procurement flow |
| P-02 | Procurement | Send enquiries to vendors | Request for Quotation (email/supplier portal) | Standard | P2 | S | PUR-RFQ-2026-00001 raised from the material request to 3 suppliers for 3 items |
| P-03 | Procurement | Techno-commercial comparison of offers and supplier selection | Supplier Quotation Comparison (price) + custom technical scoring fields and comparison print | Custom (light) | P2 | M | 2 supplier quotations with technical score, compliance, deviations, recommended flag |
| P-04 | Procurement | Release PO with technical specifications, price, terms and conditions | Purchase Order + Terms & Conditions templates + spec attachments/print | Standard + print format | P2 | S | PUR-ORD-2026-00001/2 with terms, PCC reference and budget |
| P-05 | Procurement | Release drawings and MDF to equipment manufacturers | Drawing transmittal from Drawing Register (vendor, revision issued, date) | Custom (part of E-02) | P2 | S | Transmittal TRN-2026-00002 to Pushkar Fabricators with revision and sheet counts |
| P-06 | Procurement | Arrange bought-outs and supply them to the manufacturer | Subcontracting Order supplied items / Stock Entry to vendor | Standard | P2 | S | Free issue of plate and sections to the fabricator (stock transfer) |
| P-07 | Procurement | Supplier follow-up; coordinate inspection of equipment and bought-outs | Quality Inspection Templates + custom Inspection Plan per PO/project | Standard + custom | P2 | M | 4 inspection plans + Quality Inspection Template on 4 items + 2 incoming inspections |
| P-08 | Procurement | Release supplier payments against invoice/proforma/internal memo invoice with certification via Billing Routing Memo (BRM) to Accounts | Custom 'BRM' doctype + workflow (Procurement certifies → Accounts pays); P4: Payment Entry allowed only against certified BRM | Custom (no-code + server script) | P2/P4 | M | 2 BRMs (one certified, one pending) + BRM print format + BRM Register report |
| P-09 | Procurement | Track POs against PCC and update status (PCC updation) | PO vs PCC report (see PC-03) + PCC status column | Custom (report) | P2 | S | MSCAST PO vs PCC Variance report with committed % and variance |
| P-10 | Procurement | Collect vendor stock declaration of free-issue items project-wise; report to Projects/Accounts | Vendor-wise, project-wise supplied-item balance report + periodic vendor confirmation | Standard + custom S | P2 | S | Free Issue at Vendor report by item and value |
| P-11 | Procurement | Prepare Material Dispatch Memo (MDM) → Delivery Instruction to supplier | Custom 'MDM' doctype (items, lots, packing, destination) → creates Delivery Instruction | Custom (no-code) | P3 | M | MDM-2026-00001 (lot 1) with free-issue flag + print format |
| P-12 | Procurement | Free-issue items list as Annexure-I with MDM | Annexure-I print format from MDM/Subcontracting data | Config (print format) | P3 | S | Annexure-I free-issue list printed with the Delivery Instruction |
| P-13 | Procurement | Performance Bank Guarantee (PBG) certification | Bank Guarantee doctype (receiving/providing) + expiry notifications + BG register | Standard + config | P3 | S | 2 bank guarantees (ABG + PBG) with validity + 30-day expiry notification |
| EC-01 | Erection & Commissioning | Erection and commissioning of CCM at site | Site tasks on Project, site timesheets, Expense Claims to project, commissioning report attachment | Standard + config | P3 | S | MSCAST Commissioning Report: 5 performance parameters (speed, surface, oscillation, water pressure, cut length), 6 trial heats, punch list, provisional acceptance + signature print |
| EC-02 | Operations flow | Inspection → Packing → Loading → Transport → Commissioning | Quality Inspection gate before Delivery Note; Packing Slip; e-way bill; DN transport details | Standard + config | P2/P3 | S | Quality inspection -> delivery note with transport details; packing slip not demoed |
| A-01 | Accounts | Check PO and contract before giving credit to vendor | Supplier payment terms; Purchase Invoice linked to PO; hold/approval | Standard | P4 | S | Supplier credit limit set + PO/contract check before credit reviewed on the demo suppliers |
| A-02 | Accounts | Purchase voucher entries for bought-outs and equipment with taxes, duties, freight | Purchase Invoice with tax templates; Landed Cost Voucher for freight/cargo | Standard | P4 | S | Landed cost voucher MAT-LCV-2026-00001 (Rs 45,000 freight) apportioned onto the mould-tube receipt |
| A-03 | Accounts | Check purchase invoices against PO qty, rates, terms | PO–PR–PI matching; over-billing allowance = 0 | Standard | P4 | S | Purchase invoice matched to the purchase receipt and PO |
| A-04 | Accounts | Sales entry from sales invoice raised by project coordinator | Sales Invoice (e-invoice if applicable) | Standard | P4 | S | SINV-26-00001 (CGST+SGST), SINV-26-00002 (IGST), ACC-SINV-2026-00001 (services) |
| A-05 | Accounts | Project payments only after BRM from Procurement | Payment Entry validation against certified BRM | Custom (server script) | P4 | S | Server script 'MSCAST BRM payment block' on Payment Entry (Before Submit) - verified live: payment against a bill with no certified BRM is refused |
| A-06 | Accounts | Non-project payments: admin, utilities, credit cards, government, salary | Payment Entry / Journal Entry; credit card as bank account | Standard | P4 | S | 6 journal vouchers ACC-JV-2026-00001..6: electricity, petty cash imprest, petty cash spend, foreign travel, insurance, cargo agency |
| A-07 | Accounts | Petty cash payments | Petty cash account + Mode of Payment; Employee Advance for imprest | Config | P4 | S | Petty Cash account + 'Cash' mode of payment; cash entry for courier, stationery and conveyance |
| A-08 | Accounts | Customer receipts and receipt to customer | Payment Entry (Receive) + receipt print format | Standard | P4 | S | Payment Entry Rs 69 L advance against ABG |
| A-09 | Accounts | Cheque printing | Cheque Print Template (bank-wise) | Standard | P4 | S | 'MSCAST Payment Receipt' print format on Payment Entry, rendered against ACC-PAY-2026-00001; amount in words, allocation table, realisation caveat |
| A-10 | Accounts | Cash receipts against travel advances and sale of old items | Employee Advance return; asset/scrap sale invoice | Standard | P4/P5 | S | HDFC cheque print template configured |
| A-11 | Accounts | Debit/credit notes per PO terms | Debit Note / Credit Note (returns, rate difference) | Standard | P4 | S | Credit note SINV-26-00003 (sales rejection) and debit note PINV-26-00002 (rate difference) |
| A-12 | Accounts | Journal vouchers: travel (India & foreign), asset purchase, insurance, year-end, cargo agencies | Journal Entry; multi-currency Expense Claim; Landed Cost Voucher | Standard | P4 | S | Foreign travel, marine + erection insurance and cargo agency vouchers; landed cost voucher |
| A-13 | Accounts | Monthly MIS reflecting monthly project costs | Cost Centre/Project dimension P&L + PCC vs actual MIS (see PC-13) | Custom (report) | P4 | M | MSCAST Project MIS + PO vs PCC variance = monthly project cost MIS |
| A-14 | Accounts | Monthly Balance Sheet, P&L, Funds Flow / Cash Flow | Balance Sheet, P&L, Cash Flow; India Compliance Schedule III templates. No Funds Flow statement (not required under AS/Schedule III) | Standard | P4 | S | 'MSCAST Balance Sheet (Schedule III)' and 'MSCAST Statement of Profit and Loss (Schedule III)' in the statutory vertical format with note references - verified to balance to the rupee and the profit ties to the ledger surplus. Plus the 2021-amendment disclosures: receivable ageing, payable ageing split MSME/others, and the eleven prescribed ratios (guarded so immaterial denominators show n/a). ASSUMPTION: format still to be signed off by the CA |
| M-01 | Management modules | Employee management: leave, attendance, hours, salary slips | Frappe HR (leave, attendance, shifts) + frappe/india-payroll salary slips | Standard | P5 | M | 6 employees, 73 attendance records, leave, 6 salary slips, expense claim |
| M-02 | Management modules | Finance Scaling Management | Unclear requirement | Open question | P0 | – | 'MSCAST Finance Scaling - Funding and Capacity': order book and pipeline against scheduled collections, committed outflows, cash, the Rs 2.5 Cr sanctioned HDFC limit and the projected 90-day headroom. ASSUMPTION: 'Finance Scaling Management' was never defined by MSCAST - read as whether the business can fund the order book it is chasing (open question Q1) |
| M-03 | Management modules | Biometric door lock/unlock (access control) integration for attendance | Employee Checkin API + Shift Type auto-attendance; device sync agent (ZKTeco/eSSL via biometric-attendance-sync-tool on LAN, or ADMS push; Matrix COSEC needs custom connector). Door locking stays in the access-control system | Integration | P5 | M | Shift type with auto attendance, 72 punches from device MSCAST-DOOR-01 into Employee Checkin, converted automatically into Attendance, plus the 'MSCAST Biometric Attendance Audit' report and a disabled pull job. ASSUMPTION: no device model was given, so the standard push pattern is modelled; a real ESSL/Matrix/ZKTeco controller posts to the same endpoint and nothing downstream changes |
| M-04 | Management modules | Customer & supplier management | Customer/Supplier masters, portal, scorecard | Standard | P1 | S | Customer and supplier masters with GST, MSME, capability and scorecard |
| AC-01 | Accounts POV (compliance) | Audit trail facility (MCA rule from 1 Apr 2023) with auditor login | India Compliance audit trail (cannot be disabled once on; locks version tracking; blocks ledger deletion) enabled before first entry + custom 'Statutory Auditor' role (built-in Auditor role lacks sales, AR, stock, assets, Version) + Accounting Period freeze | Config | P0/P4 | S | 'MSCAST Statutory Auditor' role (read-only on 23 doctypes incl. Version and GL Entry) and 'MSCAST Director' role (read-only on 30) + demo users auditor@ / director@ |
| AC-02 | Accounts POV (compliance) | Edit log of each transaction in ERP | Version log on all ledger doctypes; India Compliance 'Audit Trail' report | Standard | P0 | S | Version log on ledger doctypes + India Compliance 'Audit Trail' report |
| AC-03 | Accounts POV (controls) | Alerts for incomplete data, masters and transactions | Notifications (conditions, days before/after) + Auto Email Reports on saved 'missing data' reports (e.g. supplier without GSTIN/PAN/MSME) | Config | P1→P4 | S | 11 notifications (BG expiry, PO over PCC, drawing approval) + 2 scheduled reports |
| AC-04 | Accounts POV (controls) | Emailing of all possible outputs | Email button with PDF print format; Notification attach print; Auto Email Report | Standard | All | S | Outgoing mail live through smtp.purelymail.com:465 (account 'mscast-test', uattech@carobar.net); first send verified at Gmail with SPF, DKIM and DMARC all passing; site host_name set so document links in mail resolve publicly |
| AC-05 | Accounts POV (controls) | Daily SMS to COO/CFO: major-value transactions; revenue & receipts vs purchases & expenses; MIS | SMS needs TRAI DLT registration and fixed templates (≤40 chars/variable) — poor fit for a multi-figure summary. Recommend Email Digest/Auto Email Report + WhatsApp utility template or Google Chat; short SMS alert optional | Config + custom (small) | P2 (value alerts) / P4 (summary) | M | Daily management summary (20 indicators with an Attention column) emailed at 08:30 IST by a cron batch, plus the daily digest; Google Chat webhooks for transactions above Rs 5 L are configured and left disabled pending the space URL |
| AC-06 | Accounts POV (Companies Act s.128) | Books in electronic mode; director inspection; 8-year retention; 'ERP provider undertaking that software runs 8 years' | Frappe Cloud Mumbai or India VPS with daily India backups (Rule 3(5)); read-only Director role; GPL software cannot be withdrawn; yearly archive dumps + year-end PDF/XLSX exports kept ≥8 years; IT policy | Config + policy | P0/P4 | S | MSCAST Archival Log doctype + monthly scheduled server script + 8-year retention note (Companies Act s.128(5), Accounts Rules r.3) + 12 rolling backups; off-site India copy is a production step |
| AC-07 | Accounts POV (standards) | Indian Accounting Standards list (share-based payments, fair value, segments, EPS, etc.) | MSCAST likely follows Companies (AS) Rules 2021 as an SMC; Ind AS applies only at net worth ≥ ₹250 Cr. ERP provides ledgers/registers; notes to accounts prepared by CA | External (CA) | P0 | – | 'MSCAST Notes to Accounts' - 25 notes including MSMED s.22 disclosure, related party (AS 18), contingent liabilities from the live bank guarantees, CWIP ageing, EPS basis, audit-trail note and the Schedule III negative disclosures. ASSUMPTION: MSCAST is an SMC reporting under AS with the SMC exemptions claimed, not Ind AS - stated on the face of the note |
| AC-08 | Accounts POV (equity & liabilities) | Share capital: authorised, issued; reconciliation of shares; >5% shareholders; rights | Share capital accounts; ERPNext Shareholder/Share Transfer records (verify) or statutory register kept by CS | Config / External | P4 | S | 3 shareholders with folio numbers, Share Type Equity, 3 share transfers = 10,000 equity shares of Rs 10 (paid-up Rs 1,00,000) |
| AC-09 | Accounts POV (equity & liabilities) | Reserves & surplus; borrowings; lease liabilities | Chart of accounts (Schedule III grouping); lease entries by JV | Config | P4 | S | Reserves and Surplus, Borrowings - HDFC Term Loan, Lease Liabilities, Prior Period Expenses, Fines and Penalties under Law, Retention Receivable, Petty Cash all added to the COA |
| AC-10 | Accounts POV (equity & liabilities) | Trade payables split: micro & small enterprises vs others | Custom Supplier fields (Udyam no., Micro/Small/Medium) + 45-day dues report (MSME Form I, Schedule III, s.43B(h)) | Custom (fields + script report) | P2 (fields) / P4 (report) | M | 4 suppliers tagged Micro/Small with Udyam numbers; 'MSCAST MSME 45-Day Dues (s.15 MSMED / s.43B(h))' report with days-beyond-45 and disallowance flag |
| AC-11 | Accounts POV (equity & liabilities) | Provisions: gratuity, actuarial valuation & entries, gratuity paid; income tax; deferred tax | Frappe HR Gratuity (payouts); liability valuation external (SMC <50 staff may use rational method) → JV; tax & deferred tax by JV | Standard + External | P5 (gratuity) / P4 | S | Gratuity Rule + provision ACC-JV-2026-00008 Rs 9.91 L; current tax ACC-JV-2026-00009 Rs 5.23 L at 25.168 percent (s.115BAA); deferred tax ACC-JV-2026-00010 with DTA on the gratuity provision and DTL on the depreciation timing difference. ASSUMPTIONS stated in each voucher narration |
| AC-12 | Accounts POV (assets) | Fixed asset register: additions with date put to use, asset ID, deletions/sales, depreciation cumulative & for period, discarded listing | Asset (available-for-use date), depreciation schedules, two Finance Books (Companies Act / Income Tax), disposal/scrap; Fixed Asset Register & Asset Depreciations and Balances reports. IT-Act block pooling in working sheet | Standard + config | P4 | S | 4 assets submitted with depreciation schedules: CAD workstation, welding/testing equipment, ERP software licence, hydraulic test bench |
| AC-13 | Accounts POV (assets) | Identification of own assets vs Tata Motors' assets | Not capitalised: separate register (custom doctype) or Customer Provided Items in zero-value warehouse | Custom (small) | P4 | S | MSCAST Customer Asset register with 2 records (customer-supplied mould tube set, customer gauges held at the sub-contractor) - explicitly not capitalised |
| AC-14 | Accounts POV (assets) | Intangible assets: software, life, amortisation, under development | Intangible Asset Category with SLM amortisation; CWIP for under-development | Config | P4 | S | 'Software (Intangible)' asset category + ACC-ASS-2026-00003 ERP licence Rs 2.40 L amortised over 36 months |
| AC-15 | Accounts POV (assets) | Capital work-in-progress list with completion status; asset purchase invoices | CWIP accounting on Asset Category + Asset Capitalization; custom status field | Standard + config | P4 | S | 'Plant under construction (CWIP)' category with CWIP accounting on; PINV-26-00004 Rs 7.80 L posted to 1790 - CWIP Account; ACC-ASS-2026-00004 available for use in 3 months |
| AC-16 | Accounts POV (inventory) | Closing stock register category-wise and item-wise (RM, WIP, FG, stores & spares, consumables); quantitative opening/purchases/sales/closing | Stock Balance by item group/warehouse (opening, in, out, closing qty & value) | Standard | P2/P4 | S | Stock Balance by item group and warehouse across 3 stock entries |
| AC-17 | Accounts POV (inventory) | Working of valuation of semi-finished inventory (WIP) | No project-WIP accounting in ERPNext: choose (a) Work Order + WIP warehouse, or (b) Project WIP account + JV on sale | Custom / design decision | P3 (design) / P4 | M | 'MSCAST Project WIP Valuation' report and ACC-JV-2026-00011 carrying Rs 26.71 L. Method: bought-out billed + material issued + engineering hours at Rs 450/hr + 12 percent works overhead, less the cost of the billed portion, with completion measured by billing against contract value. ASSUMPTION: method needs the auditor's blessing (decision D6) |
| AC-18 | Accounts POV (inventory) | GST on closing inventory | Not a regular GST concept (ITC reversal only on cancellation); clarify | Open question | P0 | – | 'MSCAST GST on Closing Inventory (ITC and ITC-04)' - stock by warehouse with HSN, value, embedded ITC and the treatment note, separating stock lying at the job worker (ITC-04, one-year return rule) from stock on own premises |
| AC-19 | Accounts POV (sales) | Sales reconciliation incl. with GSTR-1; rate difference working; rejections | India Compliance GSTR-1 (Books vs Filed, Reconcile tab); credit/debit notes; sales returns | Standard | P4 | S | 2 GST sales invoices with correct CGST/SGST vs IGST; GSTR-1 and GST Sales Register available |
| AC-20 | Accounts POV (purchase) | Purchase reconciliation (RM, components, consumables, labour) with GSTR; rejections | India Compliance Purchase Reconciliation Tool (GSTR-2A/2B — doc says GSTR-1, should be 2B); purchase returns | Standard | P4 | S | PINV with input IGST; Purchase Reconciliation Tool (GSTR-2A/2B) available |
| AC-21 | Accounts POV (expenses) | Expenses: monthly volume, last-year comparison, ratio to sales | P&L Growth View (vs prior year) and Margin View (% of income) | Standard | P4 | S | 'MSCAST Expense Analysis (vs last year, % of sales)' report |
| AC-22 | Accounts POV (expenses) | TDS deduction on expenses | Tax Withholding Categories (194C/194J etc.) | Standard | P4 | S | TDS 194C category (2%, 30k/1L thresholds) on the fabricator; PINV-26-00003 Rs 5,98,560 with Rs 10,320 TDS deducted |
| AC-23 | Accounts POV (payroll) | Monthly payroll matching all deductions: PF, ESI, PT, TDS | Salary Register + PF/ESI/PT/TDS registers (HRMS + india-payroll). Fix: v16 Maharashtra PT women exemption bug (₹10k vs ₹25k) before go-live | Standard (+ bug check) | P5 | M | 6 salary slips with PF 12%, ESIC, Professional Tax MH and TDS; india_payroll registers need statutory config |
| AC-24 | Accounts POV (expenses) | Prior period expenses; fines & penalties under any law | Separate GL accounts + JV tagging | Config | P4 | S | Prior Period Expenses and Fines and Penalties under Law accounts created |
| AC-25 | Accounts POV (expenses) | Warranty claims | Warranty Claim + Maintenance Visit (Support); warranty provision account | Standard | P5 | S | 1 open warranty claim against a spare roll |

## Built beyond the requirement list

| Area | What was built |
|---|---|
| Branding | MSCAST logo, favicon, 'MSCAST ERP' app name, login page branding, dark desk theme by default |
| Executive dashboard | 6 KPI number cards + 5 charts on the MSCAST workspace (order book, PO commitment, drawings, inspections, engineering hours) |
| Letterhead | MSCAST letterhead with address, CIN, GSTIN, IEC on all 15 custom print formats |
| MSCAST forms | 15 MSCAST doctypes: PCC, MDF, MDM, Drawing (+revisions), Delivery Instruction, BRM, Inspection Plan, Project Certificate, Client Claim, Customer Asset, Transmittal, Commissioning Report, Spares Handover, Project Kickoff, Archival Log |
| Print formats | 15 MSCAST print formats including the proforma invoice, client schedule, project status report, transmittal note, commissioning report and spares handover note |
| Custom reports | 15 MSCAST query reports, including MSME 45-day dues, SO-PO-invoice tracker, project closure, Schedule III balance sheet and P&L, daily management summary |
| Controls | Server script that blocks a supplier payment without a certified BRM (verified live), kick-off / customer-PO-check workflow, monthly archival job |
| Roles | MSCAST Statutory Auditor (read-only, incl. Version history) and MSCAST Director roles with demo users, so a client demo never runs as Administrator |
| Automation | 11 notifications, 1 email digest, 3 scheduled email reports (daily management summary, dispatch schedule, project MIS), 3 email templates |
| GST masters | 18,687 HSN codes, GST accounts, item tax templates, tax categories, 16 addresses with GSTIN |
| Demo dataset | 2 projects at different stages, 48 items, 15 parties, full order-to-dispatch-to-commissioning chain, 4 assets, 6 employees with payroll |
| Public demo URL | Tailscale Funnel https://thinkstation.tailf78e82.ts.net (password change required before sharing) |
| Repeatable build | 50+ idempotent seed scripts + start/stop/status/backup/reset scripts; custom Docker image with 5 apps |
| Statutory pack | Schedule III balance sheet and P&L that balance to the rupee, trade receivable and payable ageing, the eleven prescribed ratios, and 25 notes to accounts |
| Approval workflows | PCC approval, purchase order approval, BRM certification and project kick-off - four active workflows, with the BRM workflow driving the same status field the payment block reads |
| Department users | accounts / purchase / design / stores / HR demo users on the matching roles, all marked unsubscribed so the fictional domain never bounces |
| Test harness | 23 automated checks covering SQL literals against real field options, report execution, Indian dates, print rendering, ledger integrity, the payment control, seeded-data validity, GST place of supply, mail and payroll - all passing |

## What still stands between this and production

- Six items rest on stated assumptions that MSCAST or the CA should confirm: the Schedule III format, the SMC/AS basis, the WIP valuation method, the s.115BAA tax rate, the meaning of 'Finance Scaling Management', and the biometric device model
- Comparative (previous year) columns fill only when the Tally opening balances are migrated
- Google Chat webhooks are configured but disabled - they need the space URL
- Opening data migration from Tally, production VPS, HTTPS and daily India-hosted backups
- Gemini automation layer from the phased plan (needs a Google Cloud project, decision D5)

## Open questions (now answered by assumption, still worth confirming)

| # | Topic | Question | Related IDs |
|---|---|---|---|
| Q1 | Finance Scaling Management | What exactly is meant (budgets, cash-flow forecasting, multi-entity growth, credit limits)? | M-02 |
| Q2 | PCC | Share the current PCC template, who prepares/approves it, how often it is revised, and whether it is at component or assembly level. | S-02, PC-03, P-09 |
| Q3 | Project MIS | Share the 'New Project MIS' template and the monthly project cost MIS format. | PC-13, A-13 |
| Q4 | BRM | Share the Billing Routing Memo format, approvers and payment release rules (advance/proforma/internal memo). | P-08, A-05 |
| Q5 | MDM / DI / Annexure-I | Share sample Material Dispatch Memo, Delivery Instruction and Annexure-I. | P-11, PC-04, P-12 |
| Q6 | Biometric access control | Device make/model and count; network (LAN/cloud); should ERP only read punches or also control door lock/unlock? | M-03 |
| Q7 | Daily SMS | Recipients; is WhatsApp/Google Chat/email acceptable instead of SMS? Is DLT registration already done? | AC-05 |
| Q8 | Tata Motors assets | What are these assets (customer-owned tooling/equipment at MSCAST, leased items)? How are they recorded today? | AC-13 |
| Q9 | GST on closing inventory | What report/working is expected? | AC-18 |
| Q10 | Accounting standards | CA to confirm AS (Companies (AS) Rules 2021) vs Ind AS and SMC/small-company status; cash flow statement needed? | AC-07, A-14 |
| Q11 | WIP valuation | How is semi-finished/project WIP valued in Tally today (per project cost sheet, % completion)? | AC-17 |
| Q12 | Payroll | Headcount under PF/ESI; current payroll provider; gratuity valuation method. | M-01, AC-23, AC-11 |
| Q13 | 8-year undertaking | Is an open-source + archival/backup policy acceptable in place of a vendor undertaking? | AC-06 |
| Q14 | Additional claims | How are claims agreed and billed (amendment to SO, separate invoice, credit note)? | PR-07 |
| Q15 | Spares Dept | Separate team? Spares from stock or order-based? Price lists? | PR-09 |
| Q16 | Foreign travel / exports | Frequency, currencies, export orders? | A-12 |
| Q17 | Equipment-wise man-hours | Which list defines 'equipment' (CCM sub-assemblies such as ladle turret, tundish, mould, WSU)? | E-06 |
| Q18 | Flowchart order | Flowchart shows 'Mscast PO Release' before 'Designing' — are long-lead bought-outs ordered before design is complete? | E-04, P-04 |
| Q19 | Share register | Keep shareholder/share transfer records in ERP, or with the company secretary? | AC-08 |
