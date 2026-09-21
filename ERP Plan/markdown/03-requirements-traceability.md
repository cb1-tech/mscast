# MSCAST ERP - Requirements Traceability

**Version 3.0 · 21 September 2026**

- **Source of requirements:** MSCAST `ERP_Requirement_Final.pdf` (97 requirements).
- **Solution:** ERPNext v16.35 + India Compliance 16.9.1 + Frappe HR 16.19 + India Payroll 16.0.4 + `mscast_erp` 0.1.0 (release `v0.9.0`).
- **Instances:** Live POC https://mscast.carobar.net (MSCAST staff trying it with their own logins) and DEV https://mscastdev.carobar.net (full demo cast; the evidence below is its demo data).

## Coverage

- **All 97 requirements are live in the POC.** 0 partly live, 0 not in the POC, 0 out of scope.
- **Six rest on assumptions** that MSCAST or the CA must confirm (table below). Each assumption is also written into the evidence column and into the narration of the affected vouchers in the system. If an answer differs, the change is small and local.

## Assumptions carried

| ID | Assumption | Who confirms |
|-----------------|----------------------------------------------------------|-------------------------|
| A-14 | Schedule III presentation format as built | CA |
| AC-07 | MSCAST is an SMC reporting under AS, claiming SMC exemptions, not Ind AS | CA |
| AC-11 | Income tax at 25.168% under s.115BAA; depreciation timing difference estimated | CA |
| AC-17 | WIP at cost on unbilled scope, completion measured by billing vs contract value | CA (decision D6) |
| M-02 | 'Finance Scaling Management' means funding capacity for the order book | MSCAST (Q1) |
| M-03 | Biometric device pushes punches to the standard checkin endpoint; a real ESSL/Matrix/ZKTeco controller posts to the same endpoint, so nothing downstream changes | MSCAST (Q6) |

## Build checks

- **42 automated build checks.** DEV (21 September 2026): 40 pass, 2 warn (T6e, T6g: open until MSCAST answers Q20 and Q21), 0 fail. Live POC: 38 pass, 3 warn (T6e, T6g, T6f), 1 fail (T10c); left as is.
- See the POC README, section 'Build checks'.

## Full matrix

| ID | Area | Requirement | ERPNext v16 solution | Category | Phase | Size | POC evidence (demo data, as on DEV) |
|------|-----------|----------------|-----------------|-----------|------|-----|-----------------------------|
| S-01 | Sales | Prepare Sales Orders from customer orders | ERPNext Sales Order (customer PO no./date, payment terms template) | Standard | P1 | S | 3 sales orders submitted with customer PO no., retention/LD/PBG fields |
| S-02 | Sales | PCC sheet (Purchase Cost Calculation): cost price of each component of CCM/spares, prepared by Sales from the Sales Order | Custom 'PCC' doctype linked to Sales Order/Project: component lines, revisions + approval; baseline for PO control and project MIS | Custom (no-code + script report) | P1 | L | PCC-2026-00001 (R2, approved, 15 lines, Rs 1.82 Cr) and PCC-2026-00002 (approved). **A director approves.** A director may also prepare one (T6e, Q20) |
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
| PC-06 | Project coordination | Receive purchase bills, check against PO and Delivery Instruction; original to Accounts, duplicate to Purchase for BRM | BRM register records supplier bill against PO; Purchase Invoice with certification workflow | Custom → Standard + workflow | P2/P4 | M | 3 BRMs against POs. Workflow: Purchase prepares → a director certifies → Accounts marks paid. A director can also do all three steps alone (T6g, Q21) |
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
| E-02 | Engineering | Prepare engineering programme and design/drawings | Engineering tasks + Drawing Register (revisions, approvals, transmittals, Drive links) | Custom (no-code + **workflow**) | P1 | L | 9 drawings with revision tables and Drive links; MSCAST Drawing Register report. **'MSCAST Drawing Release' workflow**: Draft → For Customer Approval → Approved by Customer → Released for Manufacture → Superseded. Only a Projects Manager releases, and only from *Approved by Customer* |
| E-03 | Engineering | Prepare MDF once drawings are final | Engineering BOM or custom 'MDF' doctype with print; generates Material Requests | Config + custom print | P1 | M | 3 MDFs (WSU, Mould, Hydraulics) + MDF print format |
| E-04 | Engineering | Finalise extra bought-out item list | Bought-out item groups; Material Request from BOM/MDF | Standard | P1/P2 | S | Bought-out item groups; Material Request raised from the MDF lists |
| E-05 | Engineering | Send MDF and bought-out list to Procurement; follow up | MDF submit → Material Request + notification; Procurement Tracker report | Config | P2 | S | MSCAST Transmittal register + note print; drawing set issued to the customer (acknowledged) and to the fabricator |
| E-06 | Engineering | Capture engineering man-hours equipment-wise and project-wise | Timesheet with custom 'Equipment' field + man-hour report | Config + custom field/report | P1 | S | Timesheets with Equipment field; 'Engineering Hours by Activity' chart. The overnight sweep flags any open project with no time ever booked |
| P-01 | Procurement | Receive PCC, drawings, MDF and bought-out list | Links from Material Request to PCC/Drawing/MDF | Config | P2 | S | PCC, drawings and MDF linked into the procurement flow |
| P-02 | Procurement | Send enquiries to vendors | Request for Quotation | Standard | P2 | S | PUR-RFQ-2026-00001 to 3 suppliers for 3 items |
| P-03 | Procurement | Techno-commercial comparison of offers and supplier selection | Supplier Quotation Comparison + custom technical scoring fields | Custom (light) | P2 | M | 2 supplier quotations with technical score, compliance, deviations, recommended flag |
| P-04 | Procurement | Release PO with technical specifications, price, terms and conditions | Purchase Order + T&C templates + spec attachments | Standard + print format | P2 | S | Purchase orders with terms, PCC reference and budget. **A `Purchase User` sends for approval; a director approves.** Nobody holds both roles, so every PO passes through two people |
| P-05 | Procurement | Release drawings and MDF to equipment manufacturers | Drawing transmittal from Drawing Register | Custom (part of E-02) | P2 | S | TRN-2026-00002 to Pushkar Fabricators with revision and sheet counts |
| P-06 | Procurement | Arrange bought-outs and supply them to the manufacturer | Subcontracting supplied items / Stock Entry to vendor | Standard | P2 | S | Free issue of plate and sections to the fabricator |
| P-07 | Procurement | Supplier follow-up; coordinate inspection of equipment and bought-outs | Quality Inspection Templates + custom Inspection Plan per PO/project | Standard + custom | P2 | M | 4 inspection plans + templates on 4 items + 2 incoming inspections |
| P-08 | Procurement | Release supplier payments against invoice/proforma/internal memo invoice with certification via Billing Routing Memo (BRM) to Accounts | Custom 'BRM' doctype + workflow; Payment Entry and Journal Entry allowed only against a certified BRM | Custom (no-code + application code) | P2/P4 | M | 3 BRMs + print format + BRM Register report. Purchase prepares and may reject; **a director certifies** (certifying releases the money); Accounts marks paid. A BRM cannot be certified unless its four checks (qty, rate, inspection, delivery) are ticked (T6n). **Limitation (T6g, Q21):** a director also holds the roles that create a BRM and mark it paid, so a certificate does not prove three people were involved. The payment block holds for everyone |
| P-09 | Procurement | Track POs against PCC and update status (PCC updation) | PO vs PCC report + PCC status column | Custom (report) | P2 | S | MSCAST PO vs PCC Variance report with committed % and variance |
| P-10 | Procurement | Collect vendor stock declaration of free-issue items project-wise | Vendor-wise, project-wise supplied-item balance report | Standard + custom | P2 | S | Free Issue at Vendor report by item and value |
| P-11 | Procurement | Prepare Material Dispatch Memo (MDM) → Delivery Instruction to supplier | Custom 'MDM' doctype → creates Delivery Instruction | Custom (no-code) | P3 | M | MDM-2026-00001 with free-issue flag + print format |
| P-12 | Procurement | Free-issue items list as Annexure-I with MDM | Annexure-I print format from MDM/Subcontracting data | Config (print format) | P3 | S | Annexure-I printed with the Delivery Instruction |
| P-13 | Procurement | Performance Bank Guarantee (PBG) certification | Bank Guarantee doctype + expiry notifications + BG register | Standard + config | P3 | S | 2 bank guarantees (ABG + PBG) with validity + 30-day expiry notification. The overnight sweep also raises an exception as expiry approaches |
| EC-01 | Erection & Commissioning | Erection and commissioning of CCM at site | Site tasks, site timesheets, Expense Claims, commissioning report | Standard + config | P3 | S | MSCAST Commissioning Report: 5 performance parameters, 6 trial heats, punch list, provisional acceptance + signature print |
| EC-02 | Operations flow | Inspection → Packing → Loading → Transport → Commissioning | Quality Inspection gate before Delivery Note; Packing Slip; e-way bill | Standard + config | P2/P3 | S | Quality inspection → delivery note with transport details; packing slip not demoed |
| A-01 | Accounts | Check PO and contract before giving credit to vendor | Supplier payment terms; Purchase Invoice linked to PO; hold/approval | Standard | P4 | S | Supplier credit limit set + PO/contract check |
| A-02 | Accounts | Purchase voucher entries for bought-outs and equipment with taxes, duties, freight | Purchase Invoice with tax templates; Landed Cost Voucher | Standard | P4 | S | Landed cost voucher MAT-LCV-2026-00001 (Rs 45,000 freight) apportioned onto the mould-tube receipt |
| A-03 | Accounts | Check purchase invoices against PO qty, rates, terms | PO–PR–PI matching; over-billing allowance = 0 | Standard | P4 | S | Purchase invoice matched to the purchase receipt and PO |
| A-04 | Accounts | Sales entry from sales invoice raised by project coordinator | Sales Invoice (e-invoice if applicable) | Standard | P4 | S | Intra-state CGST+SGST, inter-state IGST and services invoices |
| A-05 | Accounts | Project payments only after BRM from Procurement | Payment Entry **and Journal Entry** validation against a certified BRM | Custom (**application code**, `mscast_erp.controls.brm_payment`) | P4 | S | **Tested on six routes on every build** (T6a): a bill with no certified BRM cannot be paid by Payment Entry, by Journal Entry, or as an advance with no reference; a payment above the certified amount is refused; an already-paid BRM cannot fund a second payment. Holds for every user, including a director. Utilities, rent and statutory bills are released by ticking *Exempt from BRM certification* on the supplier (0 of 15 suppliers ticked; MSCAST to list them). App code, so it is version-controlled and shipped in the image |
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
| M-02 | Management modules | Finance Scaling Management | Unclear requirement | Open question | P0 | – | 'MSCAST Finance Scaling - Funding and Capacity': order book and pipeline against scheduled collections, committed outflows, cash, the Rs 2.5 Cr sanctioned HDFC limit and the projected 90-day headroom. ASSUMPTION: read as "can the business fund the order book it is chasing" (Q1) |
| M-03 | Management modules | Biometric door lock/unlock integration for attendance | Employee Checkin API + Shift Type auto-attendance; device sync agent | Integration | P5 | M | Shift type with auto attendance; 72 punches from device MSCAST-DOOR-01 converted into Attendance, plus the audit report (on DEV; on the Live POC MSCAST's trial admin deleted the punches, so T10c fails there). **The scheduled pull job is off**; enable it and prove it against manually checked attendance before payroll relies on it. ASSUMPTION: no device model given, so the standard push pattern is modelled (Q6) |
| M-04 | Management modules | Customer & supplier management | Customer/Supplier masters, portal, scorecard | Standard | P1 | S | Masters with GST, MSME, capability and scorecard |
| AC-01 | Accounts POV (compliance) | Audit trail facility (MCA rule from 1 Apr 2023) with auditor login | India Compliance audit trail (cannot be disabled once on) + a read-only auditor role + Accounting Period freeze | Config | P0/P4 | S | Audit trail enabled before first entry. **Auditor** role: read / report / print / export only, including Version history and GL Entry; no write anywhere. Held on DEV by the CA login (S. Joshi); that login was deleted on the Live POC. `MSCAST Director` is the approving role, not a read-only one |
| AC-02 | Accounts POV (compliance) | Edit log of each transaction in ERP | Version log on all ledger doctypes; 'Audit Trail' report | Standard | P0 | S | Version log + India Compliance Audit Trail report |
| AC-03 | Accounts POV (controls) | Alerts for incomplete data, masters and transactions | Notifications + Auto Email Reports on saved 'missing data' reports | Config | P1→P4 | S | 9 enabled notifications (BG expiry, PO over PCC, drawing approval) + scheduled reports, all resolving to a live mailbox (checked on every build-check run). Plus the 16-rule overnight sweep at 06:00 IST |
| AC-04 | Accounts POV (controls) | Emailing of all possible outputs | Email button with PDF print format; Notification attach print; Auto Email Report | Standard | All | S | Outgoing mail live through Purelymail; SPF, DKIM and DMARC all pass at Gmail; site host_name set so document links resolve publicly |
| AC-05 | Accounts POV (controls) | Daily SMS to COO/CFO: major-value transactions; revenue & receipts vs purchases & expenses; MIS | SMS needs TRAI DLT registration and fixed templates - poor fit for a multi-figure summary. Email / WhatsApp / Google Chat recommended | Config + custom (small) | P2 / P4 | M | Daily management summary (20 indicators with an Attention column) at **08:30 IST** to autoelectron.jp@gmail.com; **AI morning briefing at 08:35 IST**, ranking the day's exceptions with every item linked, to waseemraj@mcast.co.in on the Live POC (owner's decision). Google Chat webhooks for transactions above Rs 5 L are configured and disabled until MSCAST gives the space URL |
| AC-06 | Accounts POV (Companies Act s.128) | Books in electronic mode; director inspection; 8-year retention; ERP provider undertaking | India VPS with daily India backups (Rule 3(5)); GPL software cannot be withdrawn; yearly archive dumps; IT policy | Config + policy | P0/P4 | S | MSCAST Archival Log + monthly scheduled script + 8-year retention note + rolling backups; nightly backup at 02:30 JST with all build checks. Off-site India copy is a production step |
| AC-07 | Accounts POV (standards) | Indian Accounting Standards list | MSCAST likely follows Companies (AS) Rules 2021 as an SMC; Ind AS applies only at net worth ≥ ₹250 Cr | External (CA) | P0 | – | 'MSCAST Notes to Accounts' - 25 notes including MSMED s.22, related party (AS 18), contingent liabilities from live bank guarantees, CWIP ageing, EPS basis, audit-trail note and the Schedule III negative disclosures. ASSUMPTION: SMC reporting under AS, stated on the face of the note |
| AC-08 | Accounts POV (equity & liabilities) | Share capital: authorised, issued; reconciliation of shares; >5% shareholders; rights | Share capital accounts; Shareholder/Share Transfer records | Config / External | P4 | S | 3 shareholders, Share Type Equity, 10,000 equity shares of Rs 10 (paid-up Rs 1,00,000). **Held as Promoter A / B / C**, so invented percentages are not attributed to MSCAST's real directors |
| AC-09 | Accounts POV (equity & liabilities) | Reserves & surplus; borrowings; lease liabilities | Chart of accounts (Schedule III grouping); lease entries by JV | Config | P4 | S | Reserves and Surplus, Borrowings - HDFC Term Loan, Lease Liabilities, Prior Period Expenses, Fines and Penalties, Retention Receivable, Petty Cash |
| AC-10 | Accounts POV (equity & liabilities) | Trade payables split: micro & small enterprises vs others | Custom Supplier fields (Udyam no., class) + 45-day dues report | Custom (fields + script report) | P2 / P4 | M | Suppliers tagged Micro/Small with Udyam numbers; 'MSCAST MSME 45-Day Dues' report with days-beyond-45 and disallowance flag. The overnight sweep raises an exception as a bill approaches day 45 |
| AC-11 | Accounts POV (equity & liabilities) | Provisions: gratuity, actuarial valuation & entries; income tax; deferred tax | Frappe HR Gratuity; liability valuation external → JV; tax & deferred tax by JV | Standard + External | P5 / P4 | S | Gratuity Rule + provision Rs 9.91 L; current tax Rs 15.33 L at 25.168% (s.115BAA) on PBT Rs 60.90 L; deferred tax with DTA on gratuity and DTL on depreciation timing. ASSUMPTIONS stated in each voucher narration |
| AC-12 | Accounts POV (assets) | Fixed asset register: additions, asset ID, disposals, depreciation | Asset with depreciation schedules, two Finance Books, disposal/scrap | Standard + config | P4 | S | 4 assets submitted with depreciation schedules |
| AC-13 | Accounts POV (assets) | Identification of own assets vs customer-owned assets | Separate register (custom doctype) | Custom (small) | P4 | S | MSCAST Customer Asset register - customer-supplied mould tube set and gauges held at the sub-contractor, explicitly not capitalised |
| AC-14 | Accounts POV (assets) | Intangible assets: software, life, amortisation, under development | Intangible Asset Category with SLM amortisation; CWIP | Config | P4 | S | 'Software (Intangible)' category + ERP licence Rs 2.40 L amortised over 36 months |
| AC-15 | Accounts POV (assets) | Capital work-in-progress list with completion status | CWIP accounting on Asset Category + Asset Capitalization | Standard + config | P4 | S | 'Plant under construction (CWIP)' category; Rs 7.80 L in CWIP; available for use in 3 months |
| AC-16 | Accounts POV (inventory) | Closing stock register category-wise and item-wise | Stock Balance by item group/warehouse | Standard | P2/P4 | S | Stock Balance by item group and warehouse |
| AC-17 | Accounts POV (inventory) | Working of valuation of semi-finished inventory (WIP) | Project WIP account + JV on sale | Custom / design decision | P3 / P4 | M | 'MSCAST Project WIP Valuation' report carrying Rs 26.71 L. Method: bought-out billed + material issued + engineering hours at Rs 450/hr + 12% works overhead, less the cost of the billed portion. ASSUMPTION: method needs the auditor's blessing (D6) |
| AC-18 | Accounts POV (inventory) | GST on closing inventory | Not a regular GST concept (ITC reversal only on cancellation) | Open question | P0 | – | 'MSCAST GST on Closing Inventory (ITC and ITC-04)' - stock by warehouse with HSN, value, embedded ITC and the treatment note, separating stock at the job worker (ITC-04, one-year rule) from stock on own premises |
| AC-19 | Accounts POV (sales) | Sales reconciliation incl. with GSTR-1; rate difference; rejections | GSTR-1 (Books vs Filed); credit/debit notes; sales returns | Standard | P4 | S | GST sales invoices with correct CGST/SGST vs IGST, **checked against the place of supply on every invoice on every build-check run**; GSTR-1 and GST Sales Register available |
| AC-20 | Accounts POV (purchase) | Purchase reconciliation with GSTR; rejections | Purchase Reconciliation Tool (GSTR-2A/2B); purchase returns | Standard | P4 | S | PINV with input IGST; Purchase Reconciliation Tool available |
| AC-21 | Accounts POV (expenses) | Expenses: monthly volume, last-year comparison, ratio to sales | P&L Growth View and Margin View | Standard | P4 | S | 'MSCAST Expense Analysis (vs last year, share of sales)' report |
| AC-22 | Accounts POV (expenses) | TDS deduction on expenses | Tax Withholding Categories (194C/194J etc.) | Standard | P4 | S | TDS 194C category (2%) on the fabricator, with TDS deducted on the invoice |
| AC-23 | Accounts POV (payroll) | Monthly payroll matching all deductions: PF, ESI, PT, TDS | Salary Register + PF/ESI/PT/TDS registers | Standard (+ bug check) | P5 | M | 6 salary slips with PF 12%, ESIC, Professional Tax MH and TDS; india_payroll registers need statutory config. v16 Maharashtra PT women-exemption bug to be checked before go-live |
| AC-24 | Accounts POV (expenses) | Prior period expenses; fines & penalties under any law | Separate GL accounts + JV tagging | Config | P4 | S | Both accounts created |
| AC-25 | Accounts POV (expenses) | Warranty claims | Warranty Claim + Maintenance Visit; warranty provision account | Standard | P5 | S | 1 open warranty claim against a spare roll |

## Built beyond the requirement list

| Area | What was built |
|-----------------------|-----------------------------------------------------------------------------|
| **Installable app** | `mscast_erp` carries every doctype, report, print format, workflow, control and the theme, so the system rebuilds on a server, not only on the build laptop. Release `v0.9.0`, repository `github.com/cb1-tech/mscast` |
| **Overnight exception engine** | 16 rules at 06:00 IST comparing documents against each other and the calendar: uncertified bills, MSME clock, guarantee expiry, projects with no time booked, dispatch without paperwork. Writes to the MSCAST Exception list with severity, document and suggested action. No model, no network, no cost |
| **AI morning briefing** | 08:35 IST: turns the findings plus the management summary into a few sentences naming what matters most today, every item linked; sent to waseemraj@mcast.co.in on the Live POC. Falls back to a plain list if the model is unreachable, so the email always goes out |
| **Post-deploy control verification** | After every install and upgrade, six control transitions are verified and repaired, with a banner and an Error Log entry |
| Branding | MSCAST logo, favicon, app name, login branding, navy/amber desk theme, role-scoped workspaces |
| Executive dashboard | KPI number cards and charts on the MSCAST workspace, plus a role-aware home page |
| Letterhead | MSCAST letterhead with address, CIN, GSTIN, IEC on all custom print formats, with a demonstration watermark |
| MSCAST forms | **25 doctypes** (8 of them child tables) |
| Print formats | **15** MSCAST print formats; every one with a sample document is rendered by the build checks |
| Custom reports | **28** MSCAST query reports |
| Controls | BRM payment block (Payment Entry and Journal Entry), four approval workflows plus the drawing release workflow, monthly archival job |
| Roles | `MSCAST Director` (approving), `Auditor` (read-only, including Version history), `Design User` (the drawing office can issue drawings but not release them) |
| Automation | 9 notifications, email digest, 3 scheduled email reports, 10 email templates |
| GST masters | 18,687 HSN codes, GST accounts, item tax templates, tax categories, addresses with GSTIN |
| Demo dataset (DEV) | **3 projects** at different stages including one full lifecycle to certificate, **63 items**, **28 parties**, **14 installed machines** (2009–2024), **14 bid outcomes**, 4 assets, 6 employees with payroll, **13 staff logins** (12 named people plus the site administrator) with a real approval matrix. The Live POC carries MSCAST's own users (see doc 09) |
| Public URLs | Cloudflare Tunnel: Live POC `https://mscast.carobar.net`, DEV `https://mscastdev.carobar.net`. Own domain, valid certificate, no client software |
| Repeatable build | Custom Docker image `mscast/erpnext:v16-app` with 5 apps on Frappe v16; fresh install via `new-mscast-site.sh` (must pass 19 system checks); **114 idempotent seed scripts** for the demo data + the operational script set |
| Statutory pack | Schedule III balance sheet and P&L that balance to the rupee, ageing, the eleven prescribed ratios, 25 notes to accounts |
| Build checks | **42 automated checks**: SQL literals against real field options, report execution as the desk runs it, Indian dates, print rendering, ledger integrity, the payment control, approval authority, segregation of duties on two axes, who holds System Manager, permissions, packaging, seeded-data validity, GST place of supply, mail, automation and payroll |
| Documentation | Strategy and Phased Plan, Research Appendix, this matrix, Implementation Report, Client Setup Guide, SOPs and Use Cases, Independent Review, Production Cutover Runbook, Role Cards, Data Request Covering Note, Operating Recommendations, Demo Run-sheet, POC README |

## What still stands between this and production

- **Six assumptions** await MSCAST or the CA (see 'Assumptions carried').
- **Previous-year comparative columns** stay blank until the Tally opening balances are migrated.
- **Opening data migration from Tally:** masters, open POs/SOs, stock, retention, BGs. MSCAST to supply the Tally export.
- **Production hosting:** VPS in India (move parked by the owner), HTTPS, real users and passwords, daily India-hosted backups (Companies (Accounts) Rules r.3(5)).
- **Google Chat webhooks** are configured but disabled until MSCAST gives the space URL.
- **Biometric attendance pull is off.** Enable it and prove it before payroll relies on it.
- **Administrator password rotation:** parked by the owner until the system carries real data or moves to a server.
- **Demo data does not replay from `reset-poc.sh`.** Configuration does: a fresh MSCAST system is built with `new-mscast-site.sh`; the demo system is restored from a backup (POC README, section 10).
- **AI briefing model endpoint:** points at a model router on the build laptop; a server needs a hosted endpoint (three configuration lines, no code change).
- **Live screen refresh (socket.io) through the tunnel:** fix parked by the owner.
- **MSCAST to supply:** real formats (PCC, Project MIS, BRM, MDM with DI and Annexure-I), answers to Q20/Q21, the list of BRM-exempt suppliers, owners of the monthly jobs, the Tally export, the CA's contact.
- **CA to answer:** B3, B4, B5, B7, EPF: confirm no continuing coverage under s.1(5) (B6), the s.115BAA election and the Ind AS 116 "Lease Liabilities" head (see doc 07).

## Open questions (Q-list)

Each is answered in the POC by an assumption; MSCAST should confirm or correct it.

| # | Topic | Question | Related IDs |
|----------|-------------------------|-------------------------------------------------|----------------|
| Q1 | Finance Scaling Management | What exactly is meant (budgets, cash-flow forecasting, multi-entity growth, credit limits)? | M-02 |
| Q2 | PCC | Share the current PCC template, who prepares/approves it, how often it is revised, and whether it is at component or assembly level. | S-02, PC-03, P-09 |
| Q3 | Project MIS | Share the 'New Project MIS' template and the monthly project cost MIS format. | PC-13, A-13 |
| Q4 | BRM | Share the Billing Routing Memo format, approvers and payment release rules. A director certifies today: confirm that is MSCAST's intent. List the suppliers to mark *Exempt from BRM certification*. | P-08, A-05 |
| Q5 | MDM / DI / Annexure-I | Share sample Material Dispatch Memo, Delivery Instruction and Annexure-I. | P-11, PC-04, P-12 |
| Q6 | Biometric access control | Device make/model and count; network; should the ERP only read punches or also control door lock/unlock? | M-03 |
| Q7 | Daily SMS | Recipients; is WhatsApp/Google Chat/email acceptable instead of SMS? Is DLT registration done? | AC-05 |
| Q8 | Customer-owned assets | What are these assets? How are they recorded today? | AC-13 |
| Q9 | GST on closing inventory | What report/working is expected? | AC-18 |
| Q10 | Accounting standards | CA to confirm AS vs Ind AS and SMC/small-company status; is a cash flow statement needed? | AC-07, A-14 |
| Q11 | WIP valuation | How is project WIP valued in Tally today? | AC-17 |
| Q12 | Payroll | Headcount under PF/ESI; current payroll provider; gratuity valuation method. | M-01, AC-23, AC-11 |
| Q13 | 8-year undertaking | Is an open-source + archival/backup policy acceptable in place of a vendor undertaking? | AC-06 |
| Q14 | Additional claims | How are claims agreed and billed? | PR-07 |
| Q15 | Spares Dept | Separate team? Spares from stock or order-based? Price lists? | PR-09 |
| Q16 | Foreign travel / exports | Frequency, currencies, export orders? | A-12 |
| Q17 | Equipment-wise man-hours | Which list defines 'equipment'? | E-06 |
| Q18 | Flowchart order | Are long-lead bought-outs ordered before design is complete? | E-04, P-04 |
| Q19 | Share register | Keep shareholder/share transfer records in the ERP, or with the company secretary? | AC-08 |
| **Q20** | **Self-approval on the PCC and the kick-off** | **A director can prepare a PCC, or verify a customer PO, and then approve it alone (build check T6e). Confirm this is intended, or move preparation to staff.** | **S-02, PC-01** |
| **Q21** | **Self-certification on supplier bills** | **A director can create a BRM, certify it and mark it paid, alone (build check T6g). This step releases money to an outside party. Confirm this is intended, or remove `Projects Manager` from the director accounts so that only Purchase can prepare a BRM.** | **P-08, PC-06, A-05** |
