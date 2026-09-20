# MSCAST ERP: Options Assessment & Phased Build Plan

**Version:** 1.1 (updated with MSCAST's final requirement document) · **Date:** 16 Sep 2026 · **Prepared for:** Sanjay · **Status:** Recommendation. Decisions D1–D7 in §10 are still open.

**Inputs:** MSCAST "ERP_Requirement_Final" (PDF, 15 pages, incl. Accounts POV) — mapped line by line in the *Requirements Traceability Matrix* (97 requirements); ERPens "Revised Proposal – Mscast" (PDF); public research on MSCAST (see the *MSCAST Knowledge Base*); GitHub and web research on open-source ERPs, Frappe apps, alternative strategies and Gemini automation (see *Research Appendix*).

**Assumptions confirmed by Sanjay on 16 Sep 2026:**
- Up to 10 ERP users.
- Today's tools are Tally Prime, Excel/Google Sheets, and paper/WhatsApp.
- Delivery will be a phased self-build.
- This is a greenfield project: it does not reuse any existing server or software stack. The only existing assets are the domain and Google Workspace.

---

## 1. Executive summary

> **What changed in v1.1.** MSCAST's final requirement document was mapped into 97 traceable requirements.
> - **Coverage:** about half are standard ERPNext v16 / India Compliance / Frappe HR features, a quarter are configuration, and 22 need custom work. One (biometric access control) is an integration; 3 need clarification or sit with the CA.
> - **Gap in the ERPens proposal:** by my reading, **31 requirements are not in it and 18 only partly**. The biggest gaps are the PCC cost sheet, the Billing Routing Memo, the audit-trail and auditor login, MSME payables, biometric attendance, the daily management summary, project WIP valuation, and customer-owned assets.
> - **Recommendation unchanged:** ERPNext v16.
> - **Timeline:** extended by about 5 weeks, to Jul 2027.
> - **Two new decisions:** D6 (WIP valuation method) and D7 (daily-summary channel).
> - **Payroll:** PF/ESI/PT/TDS payroll is confirmed in scope.

1. **The ERPens proposal already is open source.** It is ERPNext (GPL-3, 38.6k GitHub stars, v16.35.0 released 15 Sep 2026). The ₹3.6 L + GST buys *configuration and customisation*, not software. So there is no hidden open-source product to "switch to". The real choice is **who builds it, on which version, with which scope, and who owns the code**.
2. **After checking ~25 alternatives, ERPNext v16 is still the best core system for MSCAST.**
   - **Alternatives checked:** Odoo CE/EE + OCA, Dolibarr, iDempiere, OFBiz, Tryton, Axelor, metasfresh, AureusERP, Carbon, qcadoo; composable stacks (InvenTree + OpenProject + Mayan EDMS + Tally); low-code tools (AppSheet, NocoDB, Appsmith, Budibase); a custom Next.js build; SaaS (Zoho One, SAP B1).
   - **Why ERPNext wins:** it is the only fully open-source option covering all of these, without per-user licences:
     - India GST
     - e-way bill and e-invoice
     - GSTR-1/2B reconciliation
     - TDS
     - Indian payroll
   - **Why it fits MSCAST:** it already handles most of the engineer-to-order (ETO) project, procurement, subcontracting and quality flows MSCAST needs.
   - **Runners-up:**
     - *Odoo Enterprise:* full-featured but a recurring subscription (≈₹1,150 per user per month on the Custom plan, secondary source).
     - *Zoho One:* weak for ETO work.
     - *Tally + InvenTree + OpenProject:* cheap, but leaves data in separate silos.
3. **Roughly half of the proposal's "custom development" line items are standard ERPNext v16 configuration.** Examples: free-issue material, supplier scorecard, inspection templates, man-hour timesheets, approval workflows, bought-out tracking. The genuinely custom items are:
   - drawing register with revision control
   - engineering change requests and notices (ECR/ECN)
   - techno-commercial (technical + price) bid comparison
   - retention money
   - completion certificates
   - dispatch memo and dispatch schedule
   - bank guarantee (BG) and liquidated damages (LD) registers
   - inspection plan

   Most of these can be built with ERPNext's no-code tools (custom forms and fields, workflows, print formats), packaged in a custom app.
4. **Recommended plan: a phased self-build on ERPNext v16, rolled out in six staggered phases over about 10 months (Oct 2026 – Jul 2027).**
   - Operations go live first: engineering, projects, procurement, stock, dispatch.
   - **Accounts move from Tally at the start of the financial year on 1 Apr 2027**, a clean cut-over.
   - A parallel track adds **Gemini-based automation** step by step.
5. **Gemini automation is feasible and cheap, if designed as "AI drafts, humans approve".**
   - **Stack:** Google Apps Script or n8n, plus Gemini on Vertex AI in the Mumbai region (asia-south1), plus the ERPNext REST API.
   - **First wins:**
     - daily project/dispatch digest
     - Gmail/IndiaMART enquiry → Lead
     - supplier quotation PDF → Supplier Quotation draft with a techno-commercial summary
     - purchase invoice → draft with GST checks done in code, not by the AI
   - **Model cost:** estimated at about US$0.02 per document.
6. **Indicative 3-year cash cost:**
   - Self-build: **≈₹2.5–4.5 L**, plus Sanjay's time.
   - ERPens: **≈₹7.8 L** without their support plan, **≈₹12.5–14 L** with it.
   - See §8. Every figure is labelled as an estimate or a verified price.

---

## 2. MSCAST in brief (from the Knowledge Base and the final requirement document)

**Confirmed by MSCAST's requirement document:**
- **Business:** engineering consultancy for the steel industry — design & drawing, consultancy, spares supply, equipment supply.
- **Manufacturing is outsourced.**
- **Departments:** Sales, Projects (with a project coordinator in Accounts), Engineering, Procurement, Accounts & Finance, Erection & Commissioning, Spares.
- **Key internal documents:**
  - **PCC** (Purchase Cost Calculation) sheet
  - **MDF** (Material Data File / material list)
  - bought-out list
  - techno-commercial comparison
  - **MDM** (Material Dispatch Memo) with **Annexure-I** free-issue list
  - **Delivery Instruction** to suppliers, who ship direct to customer site
  - **BRM** (Billing Routing Memo) certifying supplier bills
  - PBG
  - proforma and retention supplementary invoices
  - commissioning / preliminary / final certificates
- **Accounts today:** Tally, with a monthly project-cost MIS, BS, P&L and cash flow.
- **Accounts wants:**
  - MCA audit trail with auditor login
  - alerts
  - a daily SMS summary to COO/CFO
  - 8-year record retention
  - Schedule III-style registers: MSME payables, fixed assets and CWIP, inventory and WIP, GSTR reconciliations, payroll reconciliation

**From public research (to be confirmed in discovery):**

- **Legal and size:** MSCAST Engineering Pvt Ltd, Pune (CIN U74900PN2010PTC137644, incorporated 29 Oct 2010, GSTIN 27AAGCM8444B1ZI). Up to 10 people. Declared turnover ₹1–2 Cr; GST turnover band ₹1.5–5 Cr.
- **Offer:**
  - Machines: continuous casting machines (CCMs) and CCM equipment for steel billets, aluminium billet casting machines, pouring casting machines, conveyors.
  - Engineering services: layouts, P&IDs, hydraulic circuits, erection supervision.
- **Business model (inferred):** a design-led **engineer-to-order project business**, probably outsourcing fabrication (job work).
  - Few, large orders (market prices ₹11 L – ₹2 Cr per machine).
  - Deep multi-level BOMs, many bought-out items.
  - Dispatch in lots, erection and commissioning, retention, bank guarantees.
- **Online presence is minimal:** two free IndiaMART listings, one TradeIndia listing, a placeholder website. There is a separate opportunity for digital lead generation.

**What this means for the ERP:** it must be **project-centric** (Sales Order = Project = cost centre). The key reports are project P&L (estimate vs actual), cash-flow forecast, and exposure to BGs, retention and LD. Transaction volume is low, so a small server is enough.

---

## 3. What the ERPens proposal really contains

| Proposal item | What it really is in ERPNext v16 | Classification |
|---|---|---|
| CRM, Sales, Procurement, Inventory, Accounts, GST/TDS, Projects, HR/Payroll, Assets, roles, workflows | Standard modules + India Compliance app + Frappe HR | **Configuration** |
| Drawing upload & revision control | Nothing built in; a custom "Drawing" form with revision history and Draft → Released → Superseded workflow | **Custom** (mostly no-code) |
| Engineering documentation forms ("MDF") | Custom forms and print formats (the meaning of "MDF" is still unknown) | **Custom** (no-code) |
| Bought-out item tracking | Item groups, Material Request from BOM, Procurement Tracker and Project-wise Stock Tracking reports | **Configuration** |
| Engineering approvals | Workflow | **Configuration** |
| Activity & man-hour tracking, engineering cost allocation | Timesheet, Activity Type/Cost → Project costing | **Configuration** |
| Project kick-off workflow | Project Template + Workflow | **Configuration** |
| Dispatch schedule | Delivery dates on Sales Order lines + custom report | Light custom |
| Completion certificate | New form + print format | **Custom** (no-code) |
| Retention amount tracking | Not in ERPNext or India Compliance; payment terms + custom fields + report (automatic retention ledger entries need code) | **Custom** |
| Supplier coordination, project-wise docs | Supplier portal, comments, assignments, Google Drive attachments | **Configuration** |
| Techno-commercial comparison | The built-in "Supplier Quotation Comparison" report compares **price only**; technical scoring must be added | **Custom** (light) |
| Material Dispatch Memo, delivery instructions | Delivery Note / Shipment + custom fields + print formats | Light custom |
| Free-issue material | Subcontracting Order "Supplied Items", Customer Provided Items; India Compliance handles job-work GST challans | **Configuration** |
| Inspection planning | Quality Inspection Templates and Quality Procedures exist; an inspection *plan/calendar* is custom | Partly custom |
| Supplier performance | Supplier Scorecard | **Configuration** |

**Missing from the proposal and required by MSCAST's own document (see RTM, "In ERPens proposal" = No):**
- PCC sheet and PO-vs-PCC control
- Billing Routing Memo
- project MIS template and closure reports
- SO↔PO↔invoice tracker
- proforma invoice
- additional claims
- spares handover
- MCA audit trail with auditor login
- incomplete-data alerts
- daily COO/CFO summary
- 8-year retention and India data residency
- MSME payables
- gratuity, deferred tax and customer-owned (Tata Motors) assets
- CWIP
- project WIP valuation
- biometric access-control attendance
- cheque printing
- prior-period and penalty accounts
- warranty claims

**Also missing (from business analysis):**
- bank guarantee and LC register with expiry alerts
- liquidated damages tracking
- milestone billing / payment schedules
- cost-estimation sheet per machine family
- engineering change requests and notices (ECR/ECN)
- partial BOM release
- e-way bill scope and India Compliance API credits
- export documents and multi-currency
- warranty, spares and service visits
- data-migration volumes
- ERPNext **version** (must be v16)
- **code ownership**: a custom app in MSCAST's own Git repository
- handover and exit terms

**Commercial observations:**
- AWS at ₹10k/month is high for ≤10 users. A managed Frappe Cloud Mumbai site or a small India VPS costs roughly half.
- The 12–14 week "big bang" rollout gives the whole business one go-live.
- The proposal says nothing about accounting cut-over timing against the financial year.

---

## 4. Options assessed (summary; details in the Research Appendix)

Scores are 1–5 (higher is better; for cost, higher = cheaper; for lock-in, higher = less lock-in).

| Strategy | India compliance | ETO fit | Cost | Time-to-value | Maintainability | Lock-in | Google Workspace fit | AI readiness | **Total** |
|---|---|---|---|---|---|---|---|---|---|
| **ERPNext v16 + India Compliance (recommended)** | 5 | 4 | 4 | 4 | 3 | 5 | 3 | 3 | **31** |
| Odoo 19 Enterprise (Custom plan) | 5 | 4 | 2 | 4 | 4 | 2 | 3 | 4 | 28 |
| Zoho One / Zoho apps (SaaS) | 5 | 2 | 3 | 5 | 5 | 1 | 3 | 4 | 28 |
| Low-code (AppSheet/NocoDB) + Tally | 2 | 3 | 4 | 4 | 2 | 3 | 5 | 3 | 26 |
| Odoo 19 Community + OCA | 3 | 4 | 3 | 3 | 2 | 4 | 3 | 2 | 24 |
| Best-of-breed OSS (InvenTree + OpenProject + Mayan) + Tally | 4 | 4 | 3 | 2 | 2 | 4 | 2 | 3 | 24 |
| Custom build (e.g. Next.js/Postgres) | 1 | 5 | 1 | 1 | 2 | 3 | 4 | 5 | 22 |
| SAP Business One | 5 | 3 | 1 | 3 | 4 | 1 | 2 | 3 | 22 |
| Carbon (crbnos) | 1 | 3 | 3 | 2 | 2 | 3 | 2 | 4 | 20 |
| Dolibarr / Tryton / iDempiere / Axelor / metasfresh / OFBiz | 1–2 | 2–4 | 3–4 | 2 | 2 | 4 | 1–2 | 1–2 | ≤20 |

**Why the others fell short:**
- **Odoo Community:** GSTR filing (`l10n_in_reports`), Indian payroll, PLM, Quality, and full accounting reports are Enterprise-only. OCA `l10n-india` is empty.
- **Carbon:** its licence restricts internal production use unless changes are open-sourced; no GST support.
- **Custom build:** rebuilds what ERPNext already solves, and carries GST, payroll and audit-trail compliance risk.
- **Tally-centred stacks:** no single project P&L across systems.

**Compliance facts that shaped the choice:**
- Since 1 Apr 2023, every Pvt Ltd company must keep books in software with an **audit trail (edit log) that cannot be switched off**. This rules out spreadsheets and low-code tools for accounting.
- **E-invoicing** is mandatory above ₹5 Cr aggregate annual turnover (AATO). MSCAST is near that band; confirm with the CA.
- **E-way bills** apply to machine dispatches.

---

## 5. Target solution (greenfield)

```
                Google Workspace (existing)
   Gmail · Calendar · Shared Drives · Chat · Meet · Gemini in Workspace
        │ Google Sign-In   │ drawings/docs      │ alerts / digests
        ▼                  ▼                    ▲
 ┌───────────────────────────────────────────────────────────┐
 │  erp.<mscast-domain>  — ERPNext v16 (Frappe Cloud Mumbai  │
 │  or India VPS)                                            │
 │   • ERPNext core  • India Compliance  • Frappe HR         │
 │   • mscast_erp (custom app, MSCAST-owned private Git repo)│
 │   • offsite_backups → Google Drive / S3                   │
 │   • Staging site (UAT) + Production site                  │
 └───────────────▲──────────────────────────────▲────────────┘
                 │ REST API (draft-only user)   │ Webhooks (HMAC)
        ┌────────┴──────────────────────────────┴───────┐
        │  Automation layer: Apps Script (start) → n8n  │
        │  Gemini on Vertex AI (asia-south1, Mumbai)    │
        └───────────────────────────────────────────────┘
   Tally Prime: stays the books of account until 31 Mar 2027,
   then read-only for FY 2026-27 audit.
```

| Layer | Recommendation | Why / notes |
|---|---|---|
| ERP core | **ERPNext v16** (not v15) | v16 is current; frappe/india-payroll works only on v16 |
| India compliance | **India Compliance** (resilient-tech, GPL-3, v16.9.0) | Covers GST, e-way bill, e-invoice, GSTR-1 (books vs filed reconciliation), 2A/2B purchase reconciliation, **MCA audit trail** (cannot be disabled once enabled; switch on at site creation) and Schedule III Balance Sheet/P&L templates. API calls use paid credits (500 free trial). **Get a quote.** |
| HR | Frappe HR (v16.18.1) for employees, leave, attendance, site expense claims | Payroll decision is D3 |
| Custom app | `mscast_erp`, private GitHub repo owned by MSCAST | All forms, custom fields, workflows and print formats exported as fixtures, so they are version-controlled and portable |
| Hosting (**D1**) | **Must be in India:** Companies (Accounts) Rules 2014, Rule 3(5), as amended 2022, requires daily backups of electronic books on servers physically located in India. **Option A (recommended): Frappe Cloud, Mumbai region** (server and offsite backups in ap-south-1). Site plans run $25–38/month (₹2,050–3,075) for Standard/Professional; custom apps need a private bench group (from $25/month). Expect ≈$50–65/month (≈₹4–5.5k); confirm at sign-up. Managed upgrades and backups. **Option B:** self-managed India VPS (e.g. DigitalOcean Bangalore; General Purpose 2 vCPU/8 GB is $63/month) running frappe_docker, plus a small staging droplet | Option A minimises ops work for a remote, one-person build team. You can move later: ERPNext is GPL and backups restore anywhere |
| Identity | Google Sign-In (built-in Social Login Key), restricted to the company domain | One login; offboarding happens in Workspace |
| Documents | Drawings and project files in a **Shared Drive per project**; ERPNext Drawing Register holds drawing number, revision, status, approval and Drive link | Uses Workspace storage, keeps ERP storage small, familiar to engineers |
| Email / calendar | Gmail email account in ERPNext; Google Calendar sync | Built-in |
| Reporting | ERPNext reports and dashboards; Frappe Insights later if needed | |
| Automation / AI | Apps Script + Vertex AI to start (no new server); n8n in Docker when there are more than ~5 flows | See §7 |
| Mobile / site | ERPNext responsive web + Frappe HR mobile (attendance, expenses) | |

---

## 6. Phased, staggered roadmap

**Principles:**
- Each phase goes live on its own and is used for real before the next starts.
- Tally stays the book of record until the year-end cut-over.
- Every phase ends at a **go/no-go gate** with named MSCAST users signing off UAT on staging.

| Phase | Window (indicative) | Goes live for | Gate |
|---|---|---|---|
| **P0 Discovery & foundations** | 21 Sep – 16 Oct 2026 (4 wks) | Nobody yet | G0: scope, hosting, CA alignment |
| **P1 Sales, PCC, projects & engineering core** | 19 Oct – 4 Dec 2026 (7 wks) | Sales, projects, engineering | G1 |
| **P2 Procurement, PCC control, BRM, stock, subcontracting, quality** | 7 Dec 2026 – 29 Jan 2027 (8 wks incl. holidays) | Procurement, stores, QC | G2 (incl. D6 WIP method) |
| **P3 MDM/DI dispatch, commercial controls + accounts dry-run** | 1 Feb – 26 Mar 2027 (8 wks) | Project coordinator, procurement, accounts (trial) | G3: accounts cut-over go/no-go |
| **P4 Accounts, GST, assets & MIS go-live** | 1 Apr – 28 May 2027 (8 wks) | Accounts / CA / auditor / management | G4 |
| **P5 HR, payroll, biometric attendance, after-sales** | 1 Jun – 30 Jul 2027 (9 wks, 2 parallel payroll cycles) | All staff | G5: project close-out |
| **AI track A1–A7** | Nov 2026 → mid 2027, in parallel | See §7 | Each flow has its own pilot gate |

### P0: Discovery & foundations (3–4 weeks)
- **Discovery workshop with MSCAST.** Use the 15-question agenda in KB `00-index.md`: machine families, standard designs, BOM depth, in-house vs outsourced work, commercial terms (advance, retention, BG, LD), lead sources, what "MDF" means, data to migrate.
- **Process maps (as-is → to-be)** for: enquiry → quotation → order → engineering → procurement → job work → inspection → dispatch → erection → retention release.
- **CA / tax consultant session:**
  - Is e-invoicing applicable (AATO)?
  - Which HSN/SAC codes apply to complete machines vs services?
  - Job-work ITC-04 filing.
  - Accepting a Tally → ERPNext cut-over on 1 Apr 2027 (**D2**).
  - Audit-trail requirements.
- **Collect MSCAST's working formats:**
  - PCC sheet
  - Project MIS template
  - BRM
  - MDM
  - Delivery Instruction
  - Annexure-I
  - certificates
  - claims
  - proforma and supplementary invoices
- **Get answers to the 19 open questions** in the RTM "Open Questions" sheet, e.g.:
  - "Finance Scaling Management"
  - biometric device model
  - Tata Motors assets
  - GST on closing inventory
  - WIP method
  - AS vs Ind AS
- **CA session additions:**
  - WIP valuation method (**D6**)
  - SMC / small-company status and cash flow statement
  - gratuity valuation method
  - MSME disclosures
  - acceptance of the 8-year archival policy instead of a vendor undertaking
- **Foundations:**
  - Decide hosting (**D1**, India-located) and provision production + staging sites. **Enable the India Compliance audit trail at site creation.**
  - Set up `erp.<domain>` DNS and SSL.
  - Configure Google Sign-In and a Shared Drive structure.
  - Create the private Git repo and scaffold `mscast_erp`.
  - Define naming conventions (projects, items `<Project>-<Assy>-<DrgNo>-<Rev>`, drawings).
  - Set up user roles.
- **Master-data templates:** customers, suppliers (capability tags, approved makes), item groups (machines, assemblies, fabricated, bought-outs by category, raw material, spares, services), UOMs (Nos, Set, Kg, m, Manhour, Manday, Lot).
- **Exit criteria (G0):** signed scope and backlog; hosting live; CA agrees the accounting approach; data owners named.

### P1: Sales, PCC, projects & engineering core (≈7 weeks)
- **PCC (Purchase Cost Calculation) sheet:**
  - A custom form per Sales Order/Project: component-wise estimated cost, make and supplier category.
  - Revisions and approval.
  - It is the baseline for procurement control and the project MIS.
- **Kick-off handover:**
  - A checklist with mandatory PCC, signed technical specs, sales MOMs and contract/scope.
  - Purchase-order checks against the agreed terms.
  - Notifications to Engineering, Projects, Procurement and Finance.
  - Project code naming series.
- **Client schedules:** project execution, delivery and billing schedules as print formats; periodic overall project status report to the client.
- **MDF:** Material Data File / material list per project/assembly from final drawings, plus the bought-out list, generating Material Requests.
- **Timesheets:** man-hours captured **equipment-wise** and project-wise.
- **CRM:** Lead → Opportunity → Quotation with versions. Lead source tags: IndiaMART, TradeIndia, referral, exhibition. Technical questionnaire (child table), cost-estimate sheet per machine family.
- **Sales Order → Project** created from a template with a kick-off workflow and milestones: GA approval, BOM release, dispatch lots, erection, commissioning.
- **Timesheets:** activity types (layout, detail design, hydraulics, P&ID, vendor visit, site) → man-hour cost rolls up to the project.
- **Custom:**
  - **Drawing Register** (revision table, customer-approval status, transmittals, superseded control, Drive link)
  - **ECR/ECN** approval workflow
  - engineering documentation forms ("MDF")
- **Engineering BOMs** per project (multi-level, partial release of long-lead items); template BOMs for standard assemblies.
- **Migration:** open projects, customers, key suppliers, item catalogue (bought-outs first).
- **Exit (G1):** all live projects in ERPNext with tasks, drawings and hours logged for 2+ weeks; project status meeting runs from ERPNext, not Excel.

### P2: Procurement, PCC control, BRM, stock, subcontracting & quality (≈8 weeks)
- **PO vs PCC control:** variance report, with approval required when a PO exceeds the PCC. PCC status updates.
- **Billing Routing Memo (BRM):** Procurement certifies the supplier bill/proforma/internal memo against the PO. In P2–P3 it is a register (Tally still books); from P4 it gates Payment Entry.
- **Drawing/MDF transmittal** to equipment manufacturers.
- **Vendor free-issue stock declarations** project-wise.
- **Supplier MSME/Udyam fields** captured.
- **Major-value PO alerts** to management (see D7).
- **D6 decided with the CA:** project WIP valuation method (Work Order + WIP warehouse vs Project WIP account + JV), because it affects warehouse and account setup.
- **Purchasing:** Material Request from BOM → RFQ (supplier portal / email) → Supplier Quotation → **techno-commercial comparison** (custom technical scoring + built-in price comparison; custom print) → approval workflow → PO.
- **Stock:** purchase receipts, stock entries, project-wise stock. **Perpetual inventory stays off until P4**, so there are no accounting postings while Tally is still the book of record.
- **Subcontracting / job work:** Subcontracting Order with supplied (free-issue) items, vendor-wise balance, subcontracting receipt, GST job-work challans (India Compliance) → ITC-04 data.
- **Quality:**
  - Quality Inspection Templates per item group
  - **Inspection plan** (custom: stage/final/third-party inspection calendar per project and vendor)
  - pre-dispatch inspection as a mandatory gate
- **Supplier Scorecard:** on-time delivery, rejection %.
- **Exit (G2):** every PO for new projects raised in ERPNext; free-issue balances reconcile with vendors; inspection records attached.

### P3: MDM/DI dispatch & commercial controls, plus accounts dry-run (≈8 weeks)
- **Material Dispatch Memo → Delivery Instruction to supplier** (direct-to-site dispatch, transport arrangement), with **Annexure-I** free-issue list.
- **Billing & despatch schedule** updated with consignor, transporter, LR no./date and invoice no./date.
- **Proforma invoice** for advances and scheduled supply.
- **Additional client claims** register.
- **Commissioning / Preliminary / Final certificates.**
- **PBG** register.
- **Erection & commissioning:** site tasks, timesheets and expense claims.
- **Dispatch:** contractual delivery schedule vs actual; **Material Dispatch Memo**, packing list, Delivery Note per lot (supports ship-from-vendor), **e-way bill through India Compliance**.
- **Commercial:** payment-terms templates (advance / against dispatch / commissioning), milestone billing plan, **retention tracker**, **BG/LC register** with expiry alerts, **LD exposure** report, **completion certificate** form and print.
- **Accounts dry-run (Feb–Mar 2027):**
  - Chart of accounts, tax templates and TDS categories set up on staging.
  - Load test opening balances from Tally (e.g. 31 Dec 2026).
  - Run one month of invoices in parallel on staging.
  - CA reviews GSTR-1 and the 2B reconciliation outputs.
  - Load the fixed-asset register (Companies Act and Income Tax finance books, CWIP, intangibles, customer-owned asset register) and MSME supplier data for the opening balances.
  - Configure the Statutory Auditor and Director read-only roles.
- **Exit (G3):** dispatches and e-way bills from ERPNext; CA signs off the accounts dry-run → go/no-go for 1 Apr 2027.

### P4: Accounts & GST go-live (from 1 Apr 2027)
- **Opening balances as of 31 Mar 2027:** provisional on day 1, finalised after Tally year-end close. Covers customer/supplier open items, retention receivables, advances, stock, assets, bank.
- **Live transactions:** sales invoices (e-invoice if applicable), purchase invoices, payments, bank reconciliation, TDS, GSTR-1 export, 2A/2B reconciliation; perpetual inventory switched on.
- **Project P&L** (estimate vs actual) and cash-flow forecast go live.
- **Monthly MIS** of project costs, PCC vs actual, and SO↔PO↔invoice tracker.
- **Project completion accounting closure report.**
- **BRM-gated project payments.**
- **Cheque printing, petty cash and supplementary (retention) invoices.**
- **Schedule III** Balance Sheet/P&L templates; expense last-year comparison and ratio to sales; TDS on expenses.
- **Separate accounts** for prior-period items and fines/penalties.
- **MSME 45-day dues report** (Form I, Schedule III, s.43B(h)).
- **Fixed assets** live with depreciation.
- **Daily management summary** (D7) and incomplete-data alerts.
- **Auditor login.**
- **8-year archival SOP:** yearly dumps plus year-end exports.
- **Tally** becomes read-only for the FY 2026-27 audit. Keep its TSS subscription until the audit closes.
- **Fallback if D2 = keep Tally:** ERPNext stays the operations system; monthly voucher export to Tally via XML/JSON integration. Accept that project P&L will be partial.
- **Exit (G4):** first monthly close and GST return filed from ERPNext.

### P5: HR, payroll, biometric attendance, after-sales (≈9 weeks)
- **HR:** employees, attendance (mobile), leave, **expense claims for site travel** booked to projects.
- **Payroll (D3, revised):** PF, ESI, PT and TDS payroll with salary slips is required.
  - Run Frappe HR + india-payroll in parallel with the current payroll for June and July 2027, then go live.
  - **Before go-live, verify the Maharashtra Professional Tax women-exemption fix** (₹25,000 threshold) is in the v16 release; the v16.0.4 code still uses ₹10,000.
- **Payroll reconciliation:** Salary Register and PF/ESI/PT/TDS registers.
- **Gratuity:** payouts in Frappe HR; the liability valuation is an external/rational method booked by journal entry.
- **Biometric access-control attendance:**
  - Device punches go to Employee Checkin, then Shift auto-attendance.
  - ZKTeco/eSSL via the LAN sync tool or ADMS push; Matrix COSEC via a small connector.
  - Door locking stays in the access-control system.
- **Assets:** (register moved to P4) tools and instruments with calibration.
- **After-sales:** project closure handover to the Spares Dept (installed-machine record), serial number per machine/strand, warranty claims, maintenance visits, spares sales orders, AMC.
- **Close-out:** admin runbook, backup restore test, user guide (short videos), handover.

### Staggering and parallel-run rules
- Only one department cuts over at a time; the previous phase must be stable for ≥2 weeks.
- **Everything is built and tested on staging first.** Production changes ship via the Git repo, never by editing production directly.
- For each phase, name one **key user** at MSCAST who owns UAT and trains colleagues.
- **Remote-delivery note:** MSCAST is in Pune and the build lead works remotely. Budget for (a) scheduled video UAT sessions and (b) optionally a local Pune ERPNext freelancer or partner for on-site training and the P4 accounts cut-over.

---

## 7. Gemini automation track (parallel)

**Design rules:**
- A dedicated "AI Integration" ERPNext user may **create drafts only, never submit** (enforced by role).
- JSON-schema output from Gemini; totals, taxes and GSTINs **re-checked in code**.
- Source file always attached; low-confidence results go to "Needs Review".
- No HR/payroll data sent to AI.
- Paid API only: **Vertex AI in asia-south1** for India data residency (currently only certain models, e.g. Gemini 3.5 Flash / 2.5 Flash, are processed in India; check the model list at build time).
- Google Cloud budget alerts; every AI action logged.

| # | Flow | Build on | Starts after | Value | Risk |
|---|---|---|---|---|---|
| A1 | **Daily project & dispatch digest and COO/CFO summary**: overdue tasks, drawings pending approval, POs over PCC, dispatches this week, BG expiries; from P4, major-value transactions and revenue/receipts vs purchases/expenses → Google Chat / WhatsApp / email (D7) | Apps Script (time trigger) → ERPNext REST → Gemini summary → Chat webhook | P1 (Nov 2026) | High visibility, zero data entry | Very low (read-only) |
| A2 | **Enquiry → Lead**: sales Gmail + IndiaMART/TradeIndia emails classified; company, country, machine type, billet size, capacity extracted → Lead draft, duplicate check | Apps Script Gmail trigger or Workspace Studio triage → REST | P1 (Dec 2026) | No lost enquiries; source analytics | Low |
| A3 | **Supplier quotation PDF → Supplier Quotation draft + techno-commercial summary** (rates, GST %, delivery, payment terms, validity, deviations from spec) posted to the RFQ | n8n (or Apps Script) → Gemini (PDF input) → match to RFQ items → REST | P2 (Jan–Feb 2027) | Big time saver for buyers | Medium: item mapping; human check |
| A4 | **Supplier bill → BRM + Purchase Invoice draft** with GSTIN checksum, supplier match, CGST/SGST vs IGST by state code, totals reconciliation (all in code) | n8n → Gemini → validation → REST (consider adapting open-source `erpocr_integration`) | P4 (Apr–May 2027) | Faster AP, fewer typos | Medium: finance review mandatory |
| A5 | **Meeting notes → Tasks**: Gemini in Meet notes/Doc → actions, owner, due date, project → Task drafts | Apps Script → Gemini → REST | P1+ (anytime) | Follow-through on customer/vendor meetings | Low |
| A6 | **Ask-ERP**: natural-language questions over ERP data, read-only, permission-aware | Frappe Assistant Core (MCP, AGPL) or frappe/mcp + Gemini CLI | P4 (mid 2027) | Owner self-service analytics | Medium: read-only role, logged |
| A7 | **Drawing title block / BOM table → Item + BOM drafts** (pilot) | Gemini on exported PDF/Excel BOMs; prefer CAD BOM exports | After P2, pilot only | Faster BOM creation | High for dense drawings; limit to title block + part list |

**Workspace-native extras (no build):** Gemini in Gmail/Docs/Meet (included in Workspace Business plans at different levels; check MSCAST's edition) for drafting quotations and cover letters, and summarising customer spec documents.

**Cost indication (estimate):** ~US$0.02 per 5-page document on Gemini 3.5 Flash (Vertex regional). At MSCAST volumes (a few hundred documents a month) that is **under ~US$10/month**. Watch for "thinking-token" usage and price changes (some Flash models reprice on 1 Jan 2027).

---

## 8. Indicative 3-year cost comparison (cash, excl. internal time)

| Item | ERPens proposal | Self-build (recommended) | Basis |
|---|---|---|---|
| Implementation | ₹3.6 L + 18% GST ≈ **₹4.25 L** | ₹0 cash (Sanjay's time) + optional Pune freelancer for training/accounts cut-over **₹0.5–1.5 L** (estimate) | Proposal; freelancer rate unverified |
| Hosting (36 months) | AWS ₹10k/month after month 1 ≈ **₹3.5 L** ("may increase") | Frappe Cloud Mumbai ≈ ₹4–5.5k/month ≈ **₹1.5–2.0 L** (or VPS ≈ similar) | Frappe Cloud price page; confirm bench + site total at sign-up |
| Support | Optional ₹25k/month + GST (includes cloud, 20 dev-hrs) ≈ ₹10 L over ~33 months, replacing AWS line | Own; Frappe community; ad-hoc paid help as needed | Proposal |
| India Compliance API credits | Not mentioned | Needed for e-way bill/e-invoice/GSTIN checks: **get quote** (500 free credits) | Price not published |
| Gemini / Google Cloud | n/a | **₹0.1–0.4 L** over 3 years (estimate, with buffer) | Published per-token prices |
| Tally | Not addressed | TSS until FY26-27 audit closes (~₹5–15k) | Tally price page |
| **3-year total** | **≈₹7.8 L** (no support) · **≈₹12.5–14 L** (with support; excl./incl. GST) | **≈₹2.5–4.5 L** + credits | |

**Hidden cost of self-build: time and key-person risk.** After mapping MSCAST's final requirements, custom and configuration work is estimated at **≈28 person-weeks** (RTM Summary sheet). Adding standard setup, data migration, training and UAT gives **≈35–45 person-weeks** spread over about 10 months, plus about 6–10 weeks for the AI track. Mitigations: Git repo, staging, runbook, documented fixtures, and the option to engage a Frappe partner for specific tasks.

---

## 9. Custom app backlog (`mscast_erp`)

Effort sizes: S ≤2 days · M 3–6 days · L 7–12 days. "No-code" means built with ERPNext's settings screens (custom forms and fields, workflows, print formats, Server Scripts), exported into the app.

| # | Feature | Approach | Phase | Size |
|---|---|---|---|---|
| 1 | Project template + kick-off workflow + milestones | Config | P1 | S |
| 2 | Quotation cost-estimate sheet per machine family | No-code form + child tables | P1 | M |
| 3 | Technical questionnaire on Opportunity | Custom fields/child table | P1 | S |
| 4 | Drawing Register with revisions, approvals, transmittals, Drive links | Custom form + workflow + Server Script | P1 | L |
| 5 | ECR/ECN with impact list (BOM/MR/PO) | Custom form + workflow; auto-replacement later (Python) | P1/P2 | M |
| 6 | Engineering doc forms ("MDF") | Custom form + print format | P1 | S–M |
| 7 | Techno-commercial comparison (technical scoring + price) | Custom fields on Supplier Quotation + script report + print | P2 | M |
| 8 | Inspection plan / calendar | Custom form linked to PO/project + report | P2 | M |
| 9 | Free-issue material balance by vendor (ITC-04 support) | Standard subcontracting + report | P2 | S |
| 10 | Dispatch schedule vs contract + Material Dispatch Memo + packing list | Custom fields, form, print formats, report | P3 | M |
| 11 | Retention tracker (and optional retention receivable postings) | Payment terms + custom fields + report; postings in Python | P3/P4 | M |
| 12 | BG/LC register with expiry alerts; LD exposure report | Standard Bank Guarantee + notifications + report | P3 | S–M |
| 13 | Completion certificate | Custom form + print | P3 | S |
| 14 | Project P&L (estimate vs budget vs actual) and cash-flow forecast | Script/query reports, dashboard | P4 | M–L |
| 15 | Warranty / serial / service visit setup | Config | P5 | S |
| 16 | AI integration user, custom fields `ai_generated`/`ai_confidence`/`ai_raw_json`, webhooks | Config + small code | AI track | S |
| 17 | PCC sheet with revisions + PO-vs-PCC variance/approval | Custom form + script report + server script | P1/P2 | L + M |
| 18 | Billing Routing Memo (register → Payment Entry gate) | Custom form + workflow + server script | P2/P4 | M |
| 19 | Project MIS (MSCAST template) and project closure report; SO↔PO↔invoice tracker | Script reports | P1/P4 | M + M |
| 20 | Additional client claims; Commissioning/PAC/FAC certificates; proforma print | Custom forms + print formats | P3 | S |
| 21 | Equipment-wise man-hours | Custom field + report | P1 | S |
| 22 | MSME supplier fields + 45-day dues report | Custom fields + script report | P2/P4 | M |
| 23 | Statutory Auditor / Director roles; incomplete-data alerts; archival SOP | Config | P0/P4 | S |
| 24 | Daily COO/CFO summary (email digest + WhatsApp/Chat or DLT SMS) | Config + small scheduled job | P4 | M |
| 25 | Project WIP valuation (per D6) | Config or small script | P3/P4 | M |
| 26 | Customer-owned (Tata Motors) asset register | Custom form | P4 | S |
| 27 | Biometric access-control attendance connector | Integration | P5 | M |

---

## 10. Decisions needed

| ID | Decision | Recommendation | Needed by |
|---|---|---|---|
| **D1** | Hosting: Frappe Cloud Mumbai (managed) vs self-managed India VPS | Frappe Cloud (private bench) for P0–P5; revisit at 12 months | P0 (early Oct 2026) |
| **D2** | Accounting: move from Tally on 1 Apr 2027 vs keep Tally permanently | Move on 1 Apr 2027, subject to CA dry-run sign-off (G3) | CA meeting in P0; final at G3 |
| **D3** | Payroll: ERPNext india-payroll vs keep current provider (**revised**: PF/ESI/PT/TDS payroll is a stated requirement) | Move to india-payroll after 2 parallel cycles (Jun–Jul 2027), subject to PT bug check | P5 |
| **D6** | Project WIP valuation method: Work Order + WIP warehouse vs Project WIP account + JV | Agree with CA; lighter JV method unless MSCAST needs stage-wise WIP | Gate G2 (Jan 2027) |
| **D7** | Daily COO/CFO summary channel: SMS (TRAI DLT, ≤40 chars per variable) vs WhatsApp utility template vs Google Chat/email | Email digest + WhatsApp or Google Chat; optional one-line DLT SMS alert | P3 |
| **D4** | ERPens: decline, renegotiate, or retain for specific tasks only | Decline the fixed-bid proposal; optionally keep a paid on-call Frappe expert (ERPens or a Pune partner) for the accounts cut-over | Now |
| **D5** | Google Cloud project for Vertex AI under MSCAST Workspace (billing owner, budget cap) | Create in P1 with a ₹1–2k/month budget alert | Before A1 |

## 11. Risks & mitigations

| Risk | Mitigation |
|---|---|
| Key-person dependency (one builder, remote) | Git, staging, fixtures, runbook; a named MSCAST key user per phase; optional partner retainer |
| Adoption at a ≤10-person firm used to WhatsApp and Excel | Operations-first phasing; mobile-friendly screens; daily digest (A1) makes ERP the place to look; stop parallel Excel after each gate |
| Accounting/GST errors at cut-over | Financial-year boundary, CA dry-run, Tally read-only fallback |
| India Compliance credit costs | Disable unneeded GSTIN validations; watch the usage report |
| Young apps (india-payroll, AI community apps) | Parallel runs; pin versions; prefer thin integrations |
| AI mistakes or prompt injection from external PDFs/emails | Draft-only role, code-side validation, no auto-submit, logging |
| Unclear requirements ("Finance Scaling Management", "GST on closing inventory", Tata Motors assets) | Open Questions sheet resolved at G0; unresolved items deferred, not guessed |
| Compliance expectations beyond ERP (Ind AS list, 8-year vendor undertaking) | CA confirms AS/SMC status; archival SOP + open-source licence in place of an undertaking |
| Biometric device incompatibility | Get the device model in P0; budget a connector or device replacement |
| Scope creep (e.g. export docs, full PLM) | Backlog with phase gates; changes go into the next phase |

## 12. Next 2 weeks

1. Sanjay reviews this plan and the Requirements Traceability Matrix; decides D1, D4, D5 and sends the 19 open questions and the format request (PCC, MIS, BRM, MDM, DI, Annexure-I) to MSCAST.
2. Book the MSCAST discovery workshop (2 × 2-hour video sessions) using the KB question list; also collect sample documents (quotation, PO, BOM/drawing list, dispatch memo, invoice, retention letter, BG).
3. Book the CA session (D2, e-invoice applicability, HSN/SAC, ITC-04).
4. Provision hosting (staging first), set up the domain and Google Sign-In, and create the Git repo.
5. Prepare master-data Google Sheets templates for MSCAST to start filling.

---

### Key sources
- ERPNext: https://github.com/frappe/erpnext · India Compliance: https://github.com/resilient-tech/india-compliance · Frappe HR: https://github.com/frappe/hrms · India Payroll: https://github.com/frappe/india-payroll · Offsite backups: https://github.com/frappe/offsite_backups
- Frappe Cloud pricing (Mumbai region): https://frappe.io/cloud/sites · DigitalOcean pricing: https://www.digitalocean.com/pricing/droplets
- Odoo editions/pricing: https://www.odoo.com/page/editions · https://www.odoo.com/pricing · Odoo India docs: https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/india.html
- Retention money gap: https://discuss.frappe.io/t/retention-money/127161 · Item revisioning gap: https://discuss.frappe.io/t/item-revisioning/162669
- Gemini models/pricing: https://ai.google.dev/gemini-api/docs/models · https://ai.google.dev/gemini-api/docs/pricing · Vertex data residency: https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/data-residency
- Frappe webhooks/REST: https://docs.frappe.io/framework/user/en/guides/integration/webhooks · https://docs.frappe.io/framework/user/en/api/rest
- Audit trail rule: https://www.india-briefing.com/news/india-mandates-audit-trail-compliance-for-all-companies-explainer-key-obligations-34837.html/ · E-invoice threshold: https://www.gimbooks.com/blog/5-crore-e-invoice-turnover-rule-2026/
- MSCAST public profile: https://www.indiamart.com/mscast-engineering/ · https://www.zaubacorp.com/company/Mscast-Engineering-Private-Limited/U74900PN2010PTC137644
- Companies (Accounts) Rules audit trail & India backups: https://www.scconline.com/blog/post/2022/08/16/record-keeping-requirements-modified-vide-companies-accounts-fourth-amendment-rules-2022/ · ICAI audit trail guidance: https://cajournal.icai.org/article-details/audit-trail-requirements-responsibilities
- Ind AS applicability (Rule 4): https://ca2013.com/rule-4-companies-indian-accounting-standards-rules-2015/ · Companies (AS) Rules 2021 / SMC: https://taxguru.in/company-law/companies-accounting-standard-rules-2021.html
- Small company threshold (Dec 2025): https://www.scconline.com/blog/post/2025/12/02/mca-notified-expansion-threshold-limit-small-companies-2025-compliance-update-scctimes/ · MSME Form I: https://mmjc.in/change-in-form-msme-1-exhaustive-disclosure-framework/
- SMS DLT templates: https://msg91.com/help/dlt-registration-in-india/dlt-content-template-faqs · Biometric integration: https://docs.frappe.io/hr/integrating-frappe-hr-with-biometric-attendance-devices · Frappe Cloud backups: https://docs.frappe.io/cloud/sites/backups
- The full source lists are in the Research Appendix and the KB `sources.md`.
