# MSCAST ERP: Options Assessment & Phased Build Plan

**Version:** 2.0 · **Date:** 21 September 2026 · **Prepared for:** Sanjay (the implementer) · **Status:** planning record, written 16 Sep 2026 before the POC was built. §1–4 (platform choice), §8 (cost) and §11 (risks) stand. §5–7, §9 and §10 are the plan as written; the build has overtaken parts of them (see below).

## Current state vs this plan

- **What exists today:** read doc 03 (Requirements Traceability) and the POC README (POC README), not this document.
- **Instances:** Live POC https://mscast.carobar.net (MSCAST staff, own logins); DEV https://mscastdev.carobar.net (demos, screenshots, development).
- **Built (§6 lists as P0 work):** app `mscast_erp` with every doctype, report, print format, workflow and control, fixtures exported; release `v0.9.0`; image mscast/erpnext:v16-app; ERPNext/Frappe v16.
- **Code ownership (open):** repo is github.com/cb1-tech/mscast (owner-held), not MSCAST's own. §3 cites "custom app in MSCAST's own Git repository" as a reason for self-build. Transfer or mirror to MSCAST: not decided.
- **AI layer (differs from §7):** the AI-written briefing, emailed 08:35 IST (to waseemraj@mcast.co.in on Live POC), runs through a local model router, not Gemini on Vertex AI. A 16-rule exception sweep runs at 06:00 with no model. No per-document cost; no Google Cloud project.
- **BRM control (built):** no certified BRM = no supplier payment, on Payment Entry and Journal Entry, for every user. Per-supplier "Exempt from BRM certification" flag for utilities, rent, statutory. A BRM cannot be certified until its four checks (qty, rate, inspection, delivery) are ticked. Differs from §6: a director can create, certify and mark paid a BRM alone; MSCAST to confirm (Q21, doc 03).
- **PO control (built):** a PO cannot be approved unless someone with Purchase User sent it.
- **Decisions:** D5 answered by the build; D4 is MSCAST's own decision; D1 decided in doc 08 (§10).
- **Engagement:** unpaid; the implementer builds this for MSCAST as a family friend and is not competing with ERPens. §3 and §8 compare options only.

**Inputs:** MSCAST "ERP_Requirement_Final" (PDF, 15 pages, incl. Accounts POV), mapped in doc 03 (97 requirements) · ERPens "Revised Proposal – Mscast" (PDF) · *MSCAST Knowledge Base* (public research) · doc 02 *Research Appendix* (open-source ERPs, Frappe apps, alternative strategies, Gemini automation).

**Assumptions (confirmed by Sanjay, 16 Sep 2026):** up to 10 ERP users · current tools Tally Prime, Excel/Google Sheets, paper/WhatsApp · phased self-build · greenfield: no existing server or software reused; only existing assets are the domain and Google Workspace.

---

## 1. Executive summary

- **Recommendation:** ERPNext v16 + India Compliance + Frappe HR, phased self-build, six staggered phases, Oct 2026 – Jul 2027 (§6). Operations first (engineering, projects, procurement, stock, dispatch). **Accounts leave Tally on 1 Apr 2027** (financial-year start). AI track in parallel (§7).
- **The ERPens proposal is already open source:** it is ERPNext (GPL-3, 38.6k GitHub stars, v16.35.0 released 15 Sep 2026). ₹3.6 L + GST buys configuration and customisation, not software. The real choice: who builds, which version, which scope, who owns the code.
- **Why ERPNext (of ~25 alternatives, §4):** only fully open-source option covering India GST, e-way bill, e-invoice, GSTR-1/2B reconciliation, TDS and Indian payroll without per-user licences; already handles most ETO project, procurement, subcontracting and quality flows. Runners-up: Odoo Enterprise (≈₹1,150/user/month, Custom plan, secondary source), Zoho One (weak ETO), Tally + InvenTree + OpenProject (cheap, data silos).
- **Coverage of 97 requirements (doc 03):** ~half standard ERPNext v16 / India Compliance / Frappe HR; ~a quarter configuration; 22 custom; 1 integration (biometric access control); 3 need clarification or the CA. PF/ESI/PT/TDS payroll is in scope.
- **ERPens proposal (implementer's reading):** 31 requirements absent, 18 partial; ~half its "custom development" lines are standard v16 configuration (§3).
- **3-year cash (§8):** self-build ≈₹2.5–4.5 L + implementer's time; ERPens ≈₹7.8 L without support plan, ≈₹12.5–14 L with it. Each figure labelled estimate or verified price.

---

## 2. MSCAST in brief

**From MSCAST's requirement document:**
- **Business:** engineering consultancy for the steel industry (design & drawing, consultancy, spares supply, equipment supply). **Manufacturing is outsourced.**
- **Departments:** Sales, Projects (project coordinator sits in Accounts), Engineering, Procurement, Accounts & Finance, Erection & Commissioning, Spares.
- **Internal documents:** PCC sheet · MDF (Material Data File / material list) · bought-out list · techno-commercial comparison · MDM (Material Dispatch Memo) with Annexure-I free-issue list · DI (Delivery Instruction; suppliers ship direct to customer site) · BRM certifying supplier bills · PBG · proforma and retention supplementary invoices · commissioning / preliminary / final certificates.
- **Accounts today:** Tally; monthly project-cost MIS, BS, P&L, cash flow.
- **Accounts wants:** MCA audit trail with auditor login · alerts · daily SMS summary to COO/CFO · 8-year retention · Schedule III-style registers (MSME payables, fixed assets and CWIP, inventory and WIP, GSTR reconciliations, payroll reconciliation).

**From public research (confirm in discovery):**
- MSCAST Engineering Pvt Ltd, Pune; CIN U74900PN2010PTC137644; incorporated 29 Oct 2010; GSTIN 27AAGCM8444B1ZI; up to 10 people; declared turnover ₹1–2 Cr; GST turnover band ₹1.5–5 Cr.
- **Offer:** continuous casting machines (CCMs) and CCM equipment for steel billets, aluminium billet casting machines, pouring casting machines, conveyors; engineering services (layouts, P&IDs, hydraulic circuits, erection supervision).
- **Model (inferred):** design-led engineer-to-order projects, fabrication probably outsourced (job work); few large orders (₹11 L – ₹2 Cr per machine, market prices); deep multi-level BOMs; many bought-outs; dispatch in lots; erection and commissioning; retention; bank guarantees.
- **Online:** two free IndiaMART listings, one TradeIndia listing, placeholder website. Digital lead generation is a separate opportunity.

**ERP implication:** project-centric (Sales Order = Project = cost centre). Key reports: project P&L (estimate vs actual), cash-flow forecast, BG/retention/LD exposure. Low volume: a small server is enough.

---

## 3. What the ERPens proposal contains

| Proposal item | In ERPNext v16 | Class | Coverage · remaining effort |
|------------------------|----------------------------------------|-----------------|-------------------|
| CRM, Sales, Procurement, Inventory, Accounts, GST/TDS, Projects, HR/Payroll, Assets, roles, workflows | Standard modules + India Compliance + Frappe HR | Config | Full · config |
| Drawing upload & revision control | Not built in (attachments + version log of field changes only; no open-source Frappe PLM app found); custom Drawing form, revision history, Draft → Released → Superseded workflow | Custom (mostly no-code) | None · medium, no-code |
| ECR/ECN (not in proposal) | Workflow + BOM Update Tool + BOM Creator | Custom | Partial · low–medium |
| Engineering documentation forms ("MDF") | Custom forms + print formats (proposal does not define "MDF") | Custom (no-code) | Framework · low |
| Bought-out item tracking | Item groups, Material Request from BOM, Procurement Tracker, Project-wise Stock Tracking | Config | Mostly full · low |
| Engineering approvals | Workflow | Config | Full · config |
| Activity & man-hours, engineering cost allocation | Timesheet, Activity Type/Cost → Project costing; cost centres/dimensions | Config | Full / mostly full · config–low |
| Project kick-off workflow | Project Template + Workflow | Config | Full · config |
| Dispatch schedule | Sales Order line delivery dates, milestones + custom report | Light custom | Partial · low |
| Completion certificate | New form + print format | Custom (no-code) | None · low |
| Retention tracking | Not in ERPNext or India Compliance ("retention" in code = stock samples); payment terms + custom fields + report; automatic retention ledger entries need code | Custom | Workaround · low–medium |
| Supplier coordination, project docs | Supplier portal, comments, assignments, Google Drive attachments | Config | Partial · low |
| Techno-commercial comparison | Built-in "Supplier Quotation Comparison" is **price only**; technical scoring to add | Custom (light) | Partial · low–medium |
| MDM, delivery instructions | Delivery Note / Shipment / e-way bill + custom fields + print formats | Light custom | Partial · low |
| Free-issue material | Subcontracting Order "Supplied Items", Customer Provided Items, v16 Subcontracting Inward Order; India Compliance job-work GST challans | Config | Full · config |
| Inspection planning | Quality Inspection Template, Quality Procedure/Goal/Review/NC exist; plan/calendar is custom | Partly custom | Partial · low–medium |
| Supplier performance | Supplier Scorecard | Config | Full · config |

**Genuinely custom:** drawing register with revision control; ECR/ECN; techno-commercial (technical + price) comparison; retention money; completion certificates; dispatch memo and schedule; BG and LD registers; inspection plan. Mostly no-code (custom forms/fields, workflows, print formats), packaged in a custom app. Python code is needed only for: automatic retention accounting postings; automatic BOM/work-order replacement from an ECN; CAD/PDM integration; custom web portals; changes to core document behaviour.

**In MSCAST's document, missing from the proposal** (doc 03, "In ERPens proposal" = No): PCC sheet and PO-vs-PCC control; BRM; project MIS template and closure reports; SO↔PO↔invoice tracker; proforma invoice; additional claims; spares handover; MCA audit trail with auditor login; incomplete-data alerts; daily COO/CFO summary; 8-year retention and India data residency; MSME payables; gratuity, deferred tax, customer-owned (Tata Motors) assets; CWIP; project WIP valuation; biometric access-control attendance; cheque printing; prior-period and penalty accounts; warranty claims.

**Also missing (business analysis):** BG/LC register with expiry alerts; LD tracking; milestone billing / payment schedules; cost-estimation sheet per machine family; ECR/ECN; partial BOM release; e-way bill scope and India Compliance API credits; export documents, multi-currency; warranty, spares, service visits; data-migration volumes; ERPNext version (must be v16); code ownership (custom app in MSCAST's own Git repo); handover and exit terms.

**Cost and rollout observations:** AWS at ₹10k/month is high for ≤10 users (Frappe Cloud Mumbai or a small India VPS ≈ half). The 12–14 week "big bang" rollout gives the whole business one go-live. No accounting cut-over timing against the financial year.

---

## 4. Options assessed (details in doc 02)

Scores 1–5, higher is better (cost: higher = cheaper; lock-in: higher = less lock-in).

| Strategy | India compliance | ETO fit | Cost | Time-to-value | Maintainability | Lock-in | Google Workspace fit | AI readiness | **Total** |
|--------------|-----------|-----|------|-------------|--------------|---------|----------|----------|-------|
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

Also checked: AureusERP, qcadoo, Appsmith, Budibase.

**Why others fell short:**
- **Odoo Community:** GSTR filing (`l10n_in_reports`), Indian payroll, PLM, Quality, full accounting reports are Enterprise-only; OCA `l10n-india` is empty.
- **Carbon:** licence restricts internal production use unless changes are open-sourced; no GST.
- **Custom build:** rebuilds what ERPNext solves; GST, payroll, audit-trail compliance risk.
- **Tally-centred stacks:** no single project P&L.

**Compliance facts:**
- Since 1 Apr 2023 every Pvt Ltd company must keep books in software with an **audit trail that cannot be switched off**. Rules out spreadsheets and low-code for accounting.
- **E-invoicing** mandatory above ₹5 Cr AATO; MSCAST is near that band; CA to confirm.
- **E-way bills** apply to machine dispatches.

---

## 5. Target solution (as planned)

| Layer | Plan |
|--------------------|--------------------------------------------------------------------------------|
| ERP core | **ERPNext v16** (not v15) at `erp.<mscast-domain>`; frappe/india-payroll works only on v16 |
| India compliance | **India Compliance** (resilient-tech, GPL-3, v16.9.0): GST, e-way bill, e-invoice, GSTR-1 (books vs filed), 2A/2B reconciliation, **MCA audit trail** (cannot be disabled once on; switch on at site creation), Schedule III BS/P&L templates. API calls use paid credits (500 free trial): **get a quote** |
| HR | Frappe HR (v16.18.1): employees, leave, attendance, site expense claims. Payroll: D3 |
| Custom app | `mscast_erp` in a private GitHub repo owned by MSCAST; forms, custom fields, workflows, print formats exported as fixtures (version-controlled, portable) |
| Sites | Staging (UAT) + Production; `offsite_backups` → Google Drive / S3 |
| Hosting (**D1**) | **Must be in India:** Companies (Accounts) Rules 2014, Rule 3(5) (amended 2022): daily backups of electronic books on servers in India. **A:** Frappe Cloud Mumbai (server and offsite backups in ap-south-1); site plans $25–38/month (₹2,050–3,075) Standard/Professional; custom apps need a private bench group (from $25/month); expect ≈$50–65/month (≈₹4–5.5k), confirm at sign-up; managed upgrades and backups. **B:** self-managed India VPS (e.g. DigitalOcean Bangalore, General Purpose 2 vCPU/8 GB, $63/month) with frappe_docker + a small staging droplet. Plan recommended A (least ops for a remote one-person team); ERPNext is GPL and backups restore anywhere. Current decision: §10 |
| Identity | Google Sign-In (built-in Social Login Key), restricted to the company domain; offboarding in Workspace |
| Documents | **Shared Drive per project** for drawings and files; ERPNext Drawing Register holds number, revision, status, approval, Drive link |
| Email / calendar | Gmail account in ERPNext; Google Calendar sync (built-in) |
| Reporting | ERPNext reports and dashboards; Frappe Insights later if needed |
| Automation / AI | Apps Script + Gemini on Vertex AI (asia-south1, Mumbai) to start, no new server; n8n in Docker above ~5 flows. ERPNext REST API via a draft-only user; webhooks signed with HMAC; alerts/digests to Gmail and Chat (§7) |
| Mobile / site | ERPNext responsive web + Frappe HR mobile (attendance, expenses) |
| Tally Prime | Books of account until 31 Mar 2027, then read-only for the FY 2026-27 audit |

---

## 6. Phased, staggered roadmap (as planned)

**Rules:**
- Each phase goes live alone and is used for real before the next starts; one department cuts over at a time; the previous phase stable ≥2 weeks.
- Tally stays the book of record until the year-end cut-over.
- Each phase ends at a **go/no-go gate**: named MSCAST users sign off UAT on staging. One named MSCAST **key user** per phase owns UAT and trains colleagues.
- **Build and test on staging first.** Production changes ship via the Git repo, never by editing production.
- **Remote delivery:** MSCAST is in Pune; the implementer is remote. Budget (a) scheduled video UAT sessions, (b) optionally a Pune ERPNext freelancer/partner for on-site training and the P4 accounts cut-over.
- `#n` below = backlog item in §9.

| Phase | Window (indicative) | Goes live for | Gate |
|------------------------------|-------------------------|-------------------------|--------------------|
| **P0 Discovery & foundations** | 21 Sep – 16 Oct 2026 (4 wks) | Nobody yet | G0: scope, hosting, CA alignment |
| **P1 Sales, PCC, projects & engineering core** | 19 Oct – 4 Dec 2026 (7 wks) | Sales, projects, engineering | G1 |
| **P2 Procurement, PCC control, BRM, stock, subcontracting, quality** | 7 Dec 2026 – 29 Jan 2027 (8 wks incl. holidays) | Procurement, stores, QC | G2 (incl. D6 WIP method) |
| **P3 MDM/DI dispatch, commercial controls + accounts dry-run** | 1 Feb – 26 Mar 2027 (8 wks) | Project coordinator, procurement, accounts (trial) | G3: accounts cut-over go/no-go |
| **P4 Accounts, GST, assets & MIS go-live** | 1 Apr – 28 May 2027 (8 wks) | Accounts / CA / auditor / management | G4 |
| **P5 HR, payroll, biometric attendance, after-sales** | 1 Jun – 30 Jul 2027 (9 wks, 2 parallel payroll cycles) | All staff | G5: project close-out |
| **AI track A1–A7** | Nov 2026 → mid 2027, parallel | §7 | Pilot gate per flow |

### P0: Discovery & foundations (3–4 weeks)
- **Discovery workshop** (15-question agenda, KB `00-index.md`): machine families, standard designs, BOM depth, in-house vs outsourced, commercial terms (advance, retention, BG, LD), lead sources, meaning of "MDF", data to migrate.
- **Process maps (as-is → to-be):** enquiry → quotation → order → engineering → procurement → job work → inspection → dispatch → erection → retention release.
- **CA session:** e-invoice applicability (AATO); HSN/SAC for complete machines vs services; job-work ITC-04; Tally → ERPNext cut-over 1 Apr 2027 (**D2**); audit trail; WIP method (**D6**); SMC / small-company status and cash flow statement; gratuity valuation; MSME disclosures; 8-year archival policy in place of a vendor undertaking.
- **Collect formats:** PCC, Project MIS, BRM, MDM, DI, Annexure-I, certificates, claims, proforma and supplementary invoices.
- **Answer the 19 open questions** (doc 03), e.g. "Finance Scaling Management", biometric device model, Tata Motors assets, GST on closing inventory, WIP method, AS vs Ind AS.
- **Foundations:** decide hosting (**D1**); provision production + staging; **enable the India Compliance audit trail at site creation**; `erp.<domain>` DNS and SSL; Google Sign-In; Shared Drive structure; private Git repo + `mscast_erp` scaffold (done; ownership open); naming conventions (projects, items `<Project>-<Assy>-<DrgNo>-<Rev>`, drawings); user roles.
- **Master-data templates:** customers; suppliers (capability tags, approved makes); item groups (machines, assemblies, fabricated, bought-outs by category, raw material, spares, services); UOMs (Nos, Set, Kg, m, Manhour, Manday, Lot).
- **Exit (G0):** signed scope and backlog; hosting live; CA agrees the accounting approach; data owners named.

### P1: Sales, PCC, projects & engineering core (≈7 weeks)
- PCC sheet (#17); kick-off handover (#1); client schedules: project execution, delivery and billing schedules as print formats, periodic project status report to the client.
- MDF: material list per project/assembly from final drawings + bought-out list → Material Requests.
- CRM: Lead → Opportunity → Quotation with versions; lead source tags (IndiaMART, TradeIndia, referral, exhibition); technical questionnaire (#3); cost-estimate sheet (#2).
- Sales Order → Project from template (#1). Timesheets and equipment-wise man-hours (#21).
- Drawing Register (#4), ECR/ECN (#5), engineering doc forms (#6).
- Engineering BOMs per project (multi-level, partial release of long-lead items); template BOMs for standard assemblies.
- Migration: open projects, customers, key suppliers, item catalogue (bought-outs first).
- **Exit (G1):** all live projects in ERPNext with tasks, drawings and hours logged for 2+ weeks; project status meeting runs from ERPNext, not Excel.

### P2: Procurement, PCC control, BRM, stock, subcontracting & quality (≈8 weeks)
- PO vs PCC control (#17); BRM as a register (#18); drawing/MDF transmittal to equipment manufacturers; vendor free-issue stock declarations, project-wise; supplier MSME/Udyam fields (#22); major-value PO alerts to management (D7).
- **D6 decided with the CA** (affects warehouse and account setup).
- **Purchasing:** Material Request from BOM → RFQ (supplier portal / email) → Supplier Quotation → techno-commercial comparison (#7) → approval workflow → PO.
- **Stock:** purchase receipts, stock entries, project-wise stock. **Perpetual inventory off until P4** (no accounting postings while Tally is the book of record).
- **Subcontracting / job work:** Subcontracting Order with supplied (free-issue) items; vendor-wise balance; subcontracting receipt; GST job-work challans (India Compliance) → ITC-04 data (#9).
- **Quality:** Quality Inspection Templates per item group; inspection plan (#8); pre-dispatch inspection as a mandatory gate. Supplier Scorecard: on-time delivery, rejection %.
- **Exit (G2):** every PO for new projects raised in ERPNext; free-issue balances reconcile with vendors; inspection records attached.

### P3: MDM/DI dispatch & commercial controls, plus accounts dry-run (≈8 weeks)
- Dispatch (#10): MDM → DI to supplier with Annexure-I; billing & despatch schedule; contractual delivery schedule vs actual; **e-way bill via India Compliance**.
- Proforma invoice for advances and scheduled supply; additional client claims; Commissioning / Preliminary / Final certificates (#20); PBG register (#12).
- Erection & commissioning: site tasks, timesheets, expense claims.
- Commercial: payment-terms templates (advance / against dispatch / commissioning); milestone billing plan; retention tracker (#11); BG/LC register, LD exposure (#12); completion certificate (#13).
- **Accounts dry-run (Feb–Mar 2027):**
  1. Chart of accounts, tax templates, TDS categories on staging.
  2. Test opening balances from Tally (e.g. 31 Dec 2026).
  3. One month of invoices in parallel on staging.
  4. CA reviews GSTR-1 and 2B reconciliation outputs.
  5. Load fixed-asset register (Companies Act and Income Tax finance books, CWIP, intangibles, customer-owned asset register) and MSME supplier data for opening balances.
  6. Configure **Auditor** (read-only, held by the external CA) and **MSCAST Director** (approving: PCC, PO, BRM certification, kick-off).
- **Exit (G3):** dispatches and e-way bills from ERPNext; CA signs off the dry-run → go/no-go for 1 Apr 2027.

### P4: Accounts & GST go-live (from 1 Apr 2027)
- **Opening balances at 31 Mar 2027:** provisional on day 1, final after Tally year-end close; customer/supplier open items, retention receivables, advances, stock, assets, bank.
- **Live:** sales invoices (e-invoice if applicable), purchase invoices, payments, bank reconciliation, TDS, GSTR-1 export, 2A/2B reconciliation; perpetual inventory on.
- **Reports:** project P&L and cash-flow forecast (#14); monthly MIS of project costs, PCC vs actual, SO↔PO↔invoice tracker, project completion closure report (#19).
- **Books and controls:** BRM gates project payments (#18); cheque printing, petty cash, supplementary (retention) invoices; Schedule III BS/P&L; expense last-year comparison and ratio to sales; TDS on expenses; separate accounts for prior-period items and fines/penalties; MSME 45-day dues report (Form I, Schedule III, s.43B(h)) (#22); fixed assets with depreciation.
- Daily management summary (D7, #24); incomplete-data alerts; auditor login (#23).
- **8-year archival SOP:** yearly dumps + year-end exports.
- **Tally:** read-only for the FY 2026-27 audit; keep TSS until the audit closes.
- **Fallback if D2 = keep Tally:** ERPNext stays the operations system; monthly voucher export to Tally via XML/JSON; project P&L partial.
- **Exit (G4):** first monthly close and GST return filed from ERPNext.

### P5: HR, payroll, biometric attendance, after-sales (≈9 weeks)
- **HR:** employees, attendance (mobile), leave, site-travel expense claims booked to projects.
- **Payroll (D3):** PF, ESI, PT, TDS with salary slips. Frappe HR + india-payroll in parallel with current payroll for June and July 2027, then live. **Before go-live, verify the Maharashtra PT women-exemption fix** (₹25,000 threshold) is in the v16 release; v16.0.4 code uses ₹10,000. Reconciliation: Salary Register; PF/ESI/PT/TDS registers.
- **Gratuity:** payouts in Frappe HR; liability valued by an external/rational method, booked by journal entry.
- **Biometric (#27):** device punches → Employee Checkin → Shift auto-attendance. ZKTeco/eSSL via LAN sync tool or ADMS push; Matrix COSEC via a small connector. Door locking stays in the access-control system.
- **Assets:** tools and instruments with calibration (register is in P4).
- **After-sales (#15):** closure handover to Spares Dept (installed-machine record); serial number per machine/strand; warranty claims; maintenance visits; spares sales orders; AMC.
- **Close-out:** admin runbook, backup restore test, user guide (short videos), handover.

---

## 7. Gemini automation track (as planned; built differently, see top)

**Design rules:**
- "AI Integration" ERPNext user may **create drafts only, never submit** (enforced by role).
- JSON-schema output; totals, taxes, GSTINs **re-checked in code**.
- Source file attached; low-confidence results → "Needs Review".
- No HR/payroll data to AI.
- Paid API only: **Vertex AI asia-south1** for India residency (only some models, e.g. Gemini 3.5 Flash / 2.5 Flash, processed in India; check at build time).
- Google Cloud budget alerts; every AI action logged.

| # | Flow | Build on | Starts | Risk |
|------|--------------------------------------------|-----------------------|------------|---------------|
| A1 | Daily project & dispatch digest + COO/CFO summary: overdue tasks, drawings pending approval, POs over PCC, dispatches this week, BG expiries; from P4 major-value transactions, revenue/receipts vs purchases/expenses → Chat / WhatsApp / email (D7) | Apps Script time trigger → REST → Gemini → Chat webhook | P1 (Nov 2026) | Very low (read-only) |
| A2 | Enquiry → Lead: sales Gmail + IndiaMART/TradeIndia emails classified; company, country, machine type, billet size, capacity → Lead draft, duplicate check | Apps Script Gmail trigger or Workspace Studio → REST | P1 (Dec 2026) | Low |
| A3 | Supplier quotation PDF → Supplier Quotation draft + techno-commercial summary (rates, GST %, delivery, payment terms, validity, deviations) on the RFQ | n8n or Apps Script → Gemini (PDF) → match RFQ items → REST | P2 (Jan–Feb 2027) | Medium: item mapping; human check |
| A4 | Supplier bill → BRM + Purchase Invoice draft; GSTIN checksum, supplier match, CGST/SGST vs IGST by state code, totals (all in code) | n8n → Gemini → validation → REST (consider adapting `erpocr_integration`) | P4 (Apr–May 2027) | Medium: finance review mandatory |
| A5 | Meeting notes (Gemini in Meet/Doc) → Task drafts with owner, due date, project | Apps Script → Gemini → REST | P1+ | Low |
| A6 | Ask-ERP: natural-language, read-only, permission-aware questions | Frappe Assistant Core (MCP, AGPL) or frappe/mcp + Gemini CLI | P4 (mid 2027) | Medium: read-only role, logged |
| A7 | Drawing title block / BOM table → Item + BOM drafts (pilot) | Gemini on exported PDF/Excel BOMs; prefer CAD BOM exports | After P2, pilot | High for dense drawings; limit to title block + part list |

- **Workspace extras (no build):** Gemini in Gmail/Docs/Meet (level depends on Workspace Business edition; check MSCAST's) for quotations, cover letters, summarising customer specs.
- **Cost (estimate):** ~US$0.02 per 5-page document on Gemini 3.5 Flash (Vertex regional); a few hundred documents a month = under ~US$10/month. Watch thinking-token usage; some Flash models reprice on 1 Jan 2027.

---

## 8. Indicative 3-year cost comparison (cash, excl. internal time)

| Item | ERPens proposal | Self-build | Basis |
|------------------------|-------------------------|--------------------------------|-------------------|
| Implementation | ₹3.6 L + 18% GST ≈ **₹4.25 L** | ₹0 cash (implementer's time) + optional Pune freelancer for training/accounts cut-over **₹0.5–1.5 L** (estimate) | Proposal; freelancer rate unverified |
| Hosting (36 months) | AWS ₹10k/month after month 1 ≈ **₹3.5 L** ("may increase") | Frappe Cloud Mumbai ≈ ₹4–5.5k/month ≈ **₹1.5–2.0 L** (VPS similar) | Frappe Cloud price page; confirm bench + site at sign-up |
| Support | Optional ₹25k/month + GST (incl. cloud, 20 dev-hrs) ≈ ₹10 L over ~33 months, replacing AWS line | Own; Frappe community; paid help as needed | Proposal |
| India Compliance API credits | Not mentioned | Needed for e-way bill/e-invoice/GSTIN checks: **get quote** (500 free) | Price not published |
| Gemini / Google Cloud | n/a | **₹0.1–0.4 L** over 3 years (estimate, with buffer) | Published per-token prices |
| Tally | Not addressed | TSS until FY26-27 audit closes (~₹5–15k) | Tally price page |
| **3-year total** | **≈₹7.8 L** (no support) · **≈₹12.5–14 L** (with support; excl./incl. GST) | **≈₹2.5–4.5 L** + credits | |

**Self-build effort:** custom + configuration ≈28 person-weeks (doc 03 Summary sheet); with setup, migration, training, UAT ≈35–45 person-weeks over ~10 months; AI track +6–10 weeks. Key-person risk mitigated by Git repo, staging, runbook, documented fixtures, option to hire a Frappe partner for specific tasks.

---

## 9. Custom app backlog (`mscast_erp`, as planned)

Sizes: S ≤2 days · M 3–6 days · L 7–12 days. "No-code" = ERPNext settings screens (custom forms/fields, workflows, print formats, Server Scripts), exported into the app.

| # | Feature | Approach | Phase | Size |
|--------|----------------------------------------------|------------------------|------------|----------|
| 1 | Project template + kick-off workflow + milestones (GA approval, BOM release, dispatch lots, erection, commissioning). Kick-off checklist: mandatory PCC, signed technical specs, sales MOMs, contract/scope; PO checked against agreed terms; notifies Engineering, Projects, Procurement, Finance; project code naming series | Config | P1 | S |
| 2 | Quotation cost-estimate sheet per machine family | No-code form + child tables | P1 | M |
| 3 | Technical questionnaire on Opportunity | Custom fields/child table | P1 | S |
| 4 | Drawing Register: revision table, customer-approval status, transmittals, superseded control, Drive links | Custom form + workflow + Server Script | P1 | L |
| 5 | ECR/ECN approval with impact list (BOM/MR/PO) | Custom form + workflow; auto-replacement later (Python) | P1/P2 | M |
| 6 | Engineering doc forms ("MDF") | Custom form + print format | P1 | S–M |
| 7 | Techno-commercial comparison: custom technical scoring + built-in price comparison; custom print | Custom fields on Supplier Quotation + script report + print | P2 | M |
| 8 | Inspection plan / calendar: stage, final, third-party, per project and vendor | Custom form linked to PO/project + report | P2 | M |
| 9 | Free-issue material balance by vendor (ITC-04 support) | Standard subcontracting + report | P2 | S |
| 10 | Dispatch schedule vs contract; MDM → DI (direct-to-site, transport arrangement) with Annexure-I; billing & despatch schedule (consignor, transporter, LR no./date, invoice no./date); packing list; Delivery Note per lot (ship-from-vendor) | Custom fields, form, print formats, report | P3 | M |
| 11 | Retention tracker (optional retention receivable postings) | Payment terms + custom fields + report; postings in Python | P3/P4 | M |
| 12 | BG/LC and PBG register with expiry alerts; LD exposure report | Standard Bank Guarantee + notifications + report | P3 | S–M |
| 13 | Completion certificate | Custom form + print | P3 | S |
| 14 | Project P&L (estimate vs budget vs actual), cash-flow forecast | Script/query reports, dashboard | P4 | M–L |
| 15 | Warranty / serial / service visit setup | Config | P5 | S |
| 16 | AI integration user; custom fields `ai_generated`/`ai_confidence`/`ai_raw_json`; webhooks | Config + small code | AI track | S |
| 17 | PCC sheet per Sales Order/Project (component-wise estimated cost, make, supplier category; revisions, approval; baseline for procurement control and project MIS) + PO-vs-PCC variance report, approval when a PO exceeds the PCC, PCC status updates | Custom form + script report + server script | P1/P2 | L + M |
| 18 | BRM: Procurement certifies supplier bill/proforma/internal memo against the PO. Register in P2–P3 (Tally books); gates Payment Entry from P4 | Custom form + workflow + server script | P2/P4 | M |
| 19 | Project MIS (MSCAST template), project closure report, SO↔PO↔invoice tracker | Script reports | P1/P4 | M + M |
| 20 | Additional client claims; Commissioning/PAC/FAC certificates; proforma print | Custom forms + print formats | P3 | S |
| 21 | Man-hours equipment-wise and project-wise; activity types (layout, detail design, hydraulics, P&ID, vendor visit, site) roll cost to the project | Custom field + report | P1 | S |
| 22 | MSME/Udyam supplier fields + 45-day dues report | Custom fields + script report | P2/P4 | M |
| 23 | Auditor role (read-only), MSCAST Director role (approving), Design User; incomplete-data alerts; archival SOP | Config | P0/P4 | S |
| 24 | Daily COO/CFO summary (email digest + WhatsApp/Chat or DLT SMS) | Config + small scheduled job | P4 | M |
| 25 | Project WIP valuation (per D6) | Config or small script | P3/P4 | M |
| 26 | Customer-owned (Tata Motors) asset register | Custom form | P4 | S |
| 27 | Biometric access-control attendance connector | Integration | P5 | M |

---

## 10. Decisions

| ID | Decision | Recommendation (16 Sep 2026) | Needed by | Status (21 Sep 2026) |
|-------|--------------------------------|-----------------------------|------------|-------------------|
| **D1** | Hosting: Frappe Cloud Mumbai vs self-managed India VPS | Frappe Cloud (private bench) for P0–P5; revisit at 12 months | P0 (early Oct 2026) | Decided: self-managed India VPS (doc 08). Move parked by the owner |
| **D2** | Accounts leave Tally on 1 Apr 2027 vs keep Tally permanently | Move on 1 Apr 2027, subject to CA dry-run sign-off (G3) | CA meeting in P0; final at G3 | Open |
| **D3** | Payroll: india-payroll vs current provider (PF/ESI/PT/TDS required) | india-payroll after 2 parallel cycles (Jun–Jul 2027), subject to the PT bug check | P5 | Open |
| **D4** | ERPens: decline, renegotiate, or retain for specific tasks | Decline the fixed-bid proposal; optionally a paid on-call Frappe expert (ERPens or a Pune partner) for the accounts cut-over | Now | MSCAST's decision. The implementer is not competing with ERPens (unpaid demonstration for a family friend) |
| **D5** | Google Cloud project for Vertex AI under MSCAST Workspace (billing owner, budget cap) | Create in P1 with a ₹1–2k/month budget alert | Before A1 | Answered by the build: not needed (local model router) |
| **D6** | Project WIP valuation: Work Order + WIP warehouse vs Project WIP account + JV | Agree with CA; lighter JV method unless stage-wise WIP needed | Gate G2 (Jan 2027) | Open with the CA (doc 03, AC-17) |
| **D7** | Daily COO/CFO summary channel: SMS (TRAI DLT, ≤40 chars per variable) vs WhatsApp utility template vs Google Chat/email | Email digest + WhatsApp or Google Chat; optional one-line DLT SMS | P3 | Open |
| – | Repository: transfer or mirror github.com/cb1-tech/mscast to MSCAST | – | – | Open |

## 11. Risks & mitigations

| Risk | Mitigation |
|-------------------------------------------|---------------------------------------------------------|
| Key-person dependency (one builder, remote) | Git, staging, fixtures, runbook; named MSCAST key user per phase; optional partner retainer |
| Adoption at a ≤10-person firm used to WhatsApp and Excel | Operations-first phasing; mobile-friendly screens; daily digest (A1) makes the ERP the place to look; stop parallel Excel after each gate |
| Accounting/GST errors at cut-over | Financial-year boundary, CA dry-run, Tally read-only fallback |
| India Compliance credit costs | Disable unneeded GSTIN validations; watch the usage report |
| Young apps (india-payroll, AI community apps) | Parallel runs; pin versions; thin integrations |
| AI mistakes or prompt injection from external PDFs/emails | Draft-only role, code-side validation, no auto-submit, logging |
| Unclear requirements ("Finance Scaling Management", "GST on closing inventory", Tata Motors assets) | Resolve open questions at G0; defer, do not guess |
| Compliance expectations beyond ERP (Ind AS list, 8-year vendor undertaking) | CA confirms AS/SMC status; archival SOP + open-source licence in place of an undertaking |
| Biometric device incompatibility | Get device model in P0; budget a connector or device replacement |
| Scope creep (e.g. export docs, full PLM) | Backlog with phase gates; changes go to the next phase |

## 12. Next steps (as planned 16 Sep 2026)

1. Sanjay reviews this plan and doc 03; decides D1, D4, D5; sends MSCAST the open questions (doc 03, Q1–Q21) and the format request (PCC, MIS, BRM, MDM, DI, Annexure-I). Current request: doc 10.
2. Book the discovery workshop (2 × 2-hour video sessions) using the KB question list; collect samples (quotation, PO, BOM/drawing list, dispatch memo, invoice, retention letter, BG).
3. Book the CA session (D2, e-invoice applicability, HSN/SAC, ITC-04).
4. Provision hosting (staging first), domain, Google Sign-In; Git repo (done: github.com/cb1-tech/mscast).
5. Prepare master-data Google Sheets templates for MSCAST to fill.

---

**Sources:** doc 02, section E.
