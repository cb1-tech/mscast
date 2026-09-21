---
title: "MSCAST ERP — Client Setup Guide"
---

# MSCAST ERP — Client Setup Guide

**For:** MSCAST Engineering Pvt Ltd · **System:** ERPNext v16 with India Compliance, Frappe HR and India Payroll · **Version:** 3.0 · **Date:** 21 September 2026

## How to use this guide

- **Purpose:** the steps to take a freshly installed system to the point where MSCAST runs the business on it. Server build and cutover commands: see doc 08 (*Production Cutover Runbook*).
- **Order:** steps are in dependency order — masters before transactions, tax setup before invoices, opening balances last. ERPNext validates against what already exists, so skipping ahead causes rework.
- **Owner:** each step names one owner. Name a single individual, not a department.
- **Time:** about 3 weeks part-time for Steps 1–9, then 1 month of parallel running before relying on the system alone.
- **Companion documents:** doc 06 (*SOPs and Use Cases*, how the business runs on the system) and doc 09 (*Role Cards*, one page per role — hand these to staff). This guide is for whoever builds the system.

**The demonstration systems.**

- **Live POC** (https://mscast.carobar.net): MSCAST staff are trying it with their own logins.
- **DEV** (https://mscastdev.carobar.net): separate copy with the full demo cast, used for demos and development.
- Both hold fictional data; every demo customer and supplier name ends in "(DEMO)".
- Production starts empty. Only the configuration carries across.

## MSCAST's abbreviations

MSCAST's own terms from the requirement document; they are the names on the forms in the system.

| Term | Stands for | What it is |
|---------------------|-----------------------|--------------------------------------------------------|
| **PCC** | Purchase Cost Calculation | Cost estimate sheet per machine, component by component (bought-outs, fabrication, engineering hours, erection, freight, contingency). Prepared before quoting; has revisions and an approval. Every PO is measured against it — the baseline for cost control and the project MIS |
| **MDF** | Material Data File | Material list per project or assembly, released by Design from the final drawings. Procurement buys from it |
| **BRM** | Billing Routing Memo | Certificate that a supplier's bill is correct — quantity, rate, inspection and delivery checked — before Accounts may pay it |
| **MDM** | Material Dispatch Memo | What physically goes out in a dispatch lot, including free-issue items |
| **DI** | Delivery Instruction | Instruction to a supplier to ship direct to the customer's site: consignee, transporter, vehicle, LR number |
| **Annexure-I** | — | Free-issue material list attached to a DI: MSCAST's own material held by a subcontractor |
| **PBG / ABG** | Performance / Advance Bank Guarantee | Guarantees given to the customer; expiry dates must be tracked |
| **LD** | Liquidated Damages | Penalty for late delivery, usually a % per week capped at a maximum |
| **CCM** | Continuous Casting Machine | MSCAST's principal product |
| **ITC-04** | — | GST return for goods sent to and received from job workers |
| **MSME** | Micro, Small and Medium Enterprise | Suppliers registered under Udyam. Their bills must be paid within 45 days or the expense is disallowed under s.43B(h) |

## Before you start: what to collect

Collect all of this before touching the system; most go-live delays are one missing number.

| What | Why it is needed | Who holds it |
|--------------------------------------|----------------------------------|----------------------------|
| GSTIN, PAN, TAN | Every invoice, TDS deduction and return | Accounts / CA |
| CIN, date of incorporation, registered address | Letterhead, statutory reports, MCA filings | Company secretary |
| Udyam registration (if MSCAST is itself an MSME) | MSME status on MSCAST's own documents | Accounts |
| IEC code | Export invoices and shipping documents | Accounts |
| Bank account details, IFSC, branch | Payment entries, bank reconciliation, cheque printing | Accounts |
| Company logo (PNG, transparent background) and letterhead artwork | Print formats on every document | The implementer / design |
| Digital signature token | e-invoice and e-way bill, if enabled | Directors |
| Last audited balance sheet and current trial balance from Tally | Opening balances | CA |
| Customers with GSTIN, state and addresses | Sales invoices, place of supply | Sales |
| Suppliers with GSTIN, **Udyam number and MSME class** | MSME 45-day tracking, Schedule III disclosure | Purchase |
| Items with HSN/SAC codes and units of measure | GST rates, stock, BOM | Engineering + Accounts |
| Employees: joining dates, UAN, ESIC, PAN, bank, salary structure | Payroll | HR |
| Open sales orders, purchase orders, stock on hand, retention held, bank guarantees | Opening transactions | All functions |

The two items that most often hold things up:

- **Supplier Udyam numbers** — without them the MSME 45-day report cannot work; a s.43B(h) disallowance is a cash cost at assessment.
- **HSN codes** — without them no GST invoice can be submitted.

# Part 1 — Foundations

## Step 1: Company and financial year

**Owner:** Accounts · **Effort:** half a day

1. Create the company record: legal name exactly as on the GST certificate, abbreviation `MSCAST`, default currency INR, country India.
2. Enter GSTIN, PAN, TAN, CIN and registered address. They print on documents and feed GST returns; a typo propagates everywhere.
3. Set the financial year to 1 April – 31 March.
4. Set the time zone to **Asia/Kolkata**, even if the server is elsewhere. Every statutory clock (MSMED 45-day rule, GST periods, payroll cut-offs) runs on Indian dates.
5. Decide and record the date the system becomes the book of record. Enter nothing before that date as a live transaction.

## Step 2: Chart of accounts and cost centres

**Owner:** Accounts with the CA · **Effort:** 1–2 days

- Adapt ERPNext's standard Indian chart; do not rebuild it. A heavily customised chart makes upgrades and standard reports harder.
- Heads MSCAST needs beyond the default (all exist in the demonstration system):
  - Reserves and Surplus; Share Capital
  - Borrowings — the HDFC facility
  - Lease Liabilities
  - Retention Receivable — money held back by customers pending performance
  - Work in Progress — Projects
  - Provision for Gratuity; Provision for Income Tax; Deferred Tax Asset and Liability
  - Prior Period Expenses; Fines and Penalties under Law — kept separate because they are disallowed for tax
  - Petty Cash
- Cost centres: at least one per function that owns a budget. **Do not create a cost centre per project** — projects are tracked as projects; duplicating them doubles maintenance.
- **Every ledger entry must carry a cost centre.** The build checks test this; an entry without one is a hole in the project MIS.

## Step 3: Users, roles and who approves what

**Owner:** The implementer · **Effort:** half a day

Create **one user per person**. Shared logins destroy the audit trail, which cannot be reconstructed and is mandatory under the Companies (Accounts) Rules.

### The roles

Doc 09 (*Role Cards*) gives each role a page.

| Role | Typically held by | Can do | Cannot do |
|------------------|-------------------|-----------------------------------------|----------------------|
| **MSCAST Director** | The two directors | Approve a PCC, a purchase order, a project kick-off; certify a BRM; send a cost sheet back | — |
| **Projects Manager** | Projects head | PCC, MDF, project schedule, kick-off preparation; record customer approval on a drawing; **release a drawing for manufacture** | Approve a PCC or a kick-off, unless also a director |
| **Design User** | Drawing office | Register drawings, issue them for customer approval, transmittals, MDF | Release a drawing for manufacture |
| **Purchase Manager** | Purchase engineer | RFQ, PO, supplier masters, prepare a BRM, **reject** a PO or a bill | Approve any purchase order; certify a BRM |
| **Purchase User** | Purchase executive | Material requests, RFQs, raise purchase orders, prepare BRMs | Approve a purchase order; certify a BRM |
| **Accounts Manager** | Accounts head | Invoices, payments, journals, GST returns; verify a customer PO; **mark a certified bill paid** | Pay against an uncertified BRM; approve a kick-off |
| **Accounts User** | Accounts executive | Enter invoices, prepare payments, journals | Release a payment |
| **Stock User / Item Manager** | Stores in-charge | Receipts, issues, free-issue transfers, dispatch, item masters | Change approved purchase orders |
| **Quality Manager** | Quality | Inspection plans and results, commissioning reports | — |
| **HR Manager / HR User** | HR and admin officer | Employees, attendance, leave, payroll | Accounts postings |
| **Auditor** | External CA | Read, report, print, export — including version history | **Write anything** (build check `T6h`) |

Give the CA a read-only Auditor login with version history: the audit-trail requirement is then met by evidence, not assertion.

### What the software enforces (for everyone, directors included)

1. **No certified BRM, no supplier payment** — refused on Payment Entry and on Journal Entry, with the reason displayed. Exception: suppliers ticked *Exempt from BRM certification* (utilities, rent, statutory). Rule for the tick: doc 11, A8.
2. **A BRM cannot be certified** unless its four checks (quantity, rate, inspection, delivery) are ticked.
3. **A drawing cannot be released for manufacture** unless the customer approved it; only a Projects Manager releases.
4. **A purchase order cannot be approved** unless someone holding `Purchase User` sent it for approval. Sending and approving are different roles; no one person holds both.
5. **A project kick-off cannot be approved** while the PO checklist is incomplete.

### What is *not* separated

- Both directors hold `Projects Manager` and `Accounts Manager` as well as `MSCAST Director`. So a director **can**, alone:
  - create a BRM, certify it and mark it paid;
  - prepare a PCC and approve it;
  - verify a customer PO and approve the kick-off.
- Build checks `T6e` and `T6g` report this on every build as warnings; it is put to MSCAST as questions Q20 and Q21.
- What is protected regardless: the payment itself (item 1 above).
- Until MSCAST decides:
  - Every approval is recorded with name and timestamp.
  - For a significant commitment, the **other** director approves.
- To enforce separation later: move preparation to staff (a projects person prepares the PCC, Accounts verifies the customer PO) and leave directors approving only.

### Audit the role list

Roles drift; this step undoes everything above if skipped.

- **Setup-wizard administrator:** a fresh install creates it holding every manager role (41 roles in the POC). Cut it to `System Manager` only as soon as the site is built (go-live checklist line 15).
- **Nobody who does day-to-day work holds `System Manager`** — it bypasses every control in this guide. Administration = one named administrator + the built-in `Administrator` account, nothing more (checklist line 16).
- The build checks report both (`T6f`), so later drift is caught.

### Where the rules live

**Who may approve what lives in the packaged application (`mscast_erp`), not in the ERPNext screens.** A workflow role changed in the screens is reverted at the next upgrade. See Step 12.

## Step 4: Master data

**Owner:** each function for its own masters · **Effort:** 1 week

Load in this order; each depends on the one before.

1. **UOM and item groups.** Keep the list short; every extra item group is a decision on every new item.
2. **Items.** Item code, name, group, stock UOM, **HSN/SAC code**, GST rate template, stock item (yes/no), fixed asset (yes/no). Create items only for what MSCAST buys, stocks or sells repeatedly; the PCC and MDF carry one-off detail.
3. **Warehouses.** At minimum: Stores, Work in Progress, Finished Goods, and **one per subcontractor holding free-issue material** (this keeps ITC-04 reporting correct).
4. **Customers.** Name, GSTIN, state, addresses, credit terms, payment terms.
5. **Suppliers.** Name, GSTIN, state, addresses and, where applicable, **Udyam number plus MSME class (Micro / Small / Medium)**. Get it in writing from each supplier; the supplier's declaration is the evidence.

GSTIN format and implied state are validated on entry.

## Step 5: GST configuration

**Owner:** Accounts with the CA · **Effort:** 2 days

1. Enter the company GSTIN and confirm the state code. The system picks CGST+SGST or IGST by comparing it with the place of supply; a wrong address makes every invoice wrong.
2. Create tax templates: Output GST in-state, Output GST inter-state, Input GST in-state, Input GST inter-state.
3. Attach item tax templates for each GST rate MSCAST uses.
4. Confirm with the CA:
   - **e-invoice applicability** — turnover-based threshold; may not apply at MSCAST's size yet, but thresholds change and are checked retrospectively.
   - **e-way bill** thresholds for MSCAST's despatch patterns, including ODC movements.
   - **ITC-04** for goods sent to job workers — return within 1 year for inputs, 3 years for capital goods.
   - HSN/SAC codes against what is actually supplied, including engineering drawings sold as a deliverable.
5. Switch on the audit trail. In India Compliance it cannot be switched off again.

## Step 6: HR and payroll

**Owner:** HR · **Effort:** 2–3 days

1. Departments, designations and reporting lines.
2. Holiday list for the financial year: weekly offs plus the public holidays MSCAST observes.
3. Employees: joining date, department, designation, UAN, ESIC number, PAN, bank details.
4. Company statutory registrations: EPF, ESIC, Professional Tax (Maharashtra), Labour Welfare Fund.
5. Salary structure. The demonstration uses Basic 50%, HRA 40% of basic, conveyance and special allowance, ESIC 0.75% up to the wage limit, Maharashtra PT, TDS on salary. PF is not deducted: removed from payroll on MSCAST's instruction (under 20 staff, no UANs). Replace with MSCAST's actual structure. EPF applicability: see doc 11, B4.
6. Shift and attendance. **The biometric pull is switched off in the demonstration system.** If MSCAST uses a device: enable it, run it for 1 week against manually checked attendance, then rely on it. Until then, attendance is entered in the system. Either way, name who reviews exceptions and by when. Duplicate attendance (one employee, one date) is blocked automatically.
7. Gratuity: set the rule (15/26 days of last drawn basic per completed year, Payment of Gratuity Act) so the provision can be computed each year end.

**Run payroll in parallel with the existing method for 2 full cycles** before switching. Payroll errors are seen by every employee.

# Part 2 — MSCAST's own documents

## Step 7: The MSCAST forms

Each form needs an owner and a rule for when it is raised. Procedures: doc 06 (BRM route: SOP-07).

| Form | Raised by | Approved / certified by | When |
|---------------------------|---------------------|------------------------|-----------------------------|
| **PCC** — Purchase Cost Calculation | Projects | **Director** | Before quoting; revised on scope change |
| **Project Kick-off** | Projects, verified by Accounts | **Director** | On receipt of the customer PO |
| **Drawing register** | Design | Projects Manager releases for manufacture | Every drawing, every revision |
| **Transmittal** | Design | — | Whenever drawings go out |
| **MDF** — Material Data File | Design | — | On design release |
| **RFQ / Supplier Quotation** | Purchase | — | Before ordering bought-outs |
| **Purchase Order** | Purchase | **Director** | After approval |
| **Inspection Plan** | Quality | Quality records the result | Per stage, per supplier |
| **BRM** — Billing Routing Memo | Purchase prepares | **Director certifies**, Accounts marks paid | Every supplier bill |
| **MDM** — Material Dispatch Memo | Stores | — | Each dispatch lot |
| **Delivery Instruction** | Stores | — | Direct-to-site dispatches |
| **Commissioning Report** | Site | — | On commissioning |
| **Spares Handover** | Site | — | At handover |
| **Project Certificate** | Projects | — | Acceptance milestones; triggers retention release |
| **Client Claim** | Projects | Accounts, then Director | Scope variation, idle time, escalation |
| **Customer Asset register** | Stores | — | Customer tooling received |
| **MSCAST Exception** | *Raised by the system* | Cleared by the named owner | Automatically, every morning at 06:00 IST |

**Drawing workflow:** Draft → For Customer Approval → Approved by Customer → Released for Manufacture. No step can be skipped.

## Step 8: Print formats and letterhead

**Owner:** The implementer · **Effort:** 1 day

- Load the logo and letterhead once (address, CIN, GSTIN, IEC); every printed document inherits it.
- Check each format against a real document MSCAST issues today; fix wording before anyone outside MSCAST sees one.
- The build checks render every print format, so a format broken by a field change is caught before printing.

## Step 9: Email, alerts and the daily rhythm

**Owner:** The implementer · **Effort:** half a day

1. Configure the outgoing mail account on the company domain (mcast.co.in). Confirm SPF, DKIM and DMARC in DNS, or mail lands in spam.
2. Set the site URL (`host_name`) correctly; links inside emails are built from it.
3. **Name who receives what** — a named person who will act, not a distribution list:

| Time (IST) | What | Recommended recipient |
|-------------------|-------------------------------------------------|--------------------------------|
| 06:00 IST | Overnight checks. No email; findings go to the **MSCAST Exception** list | — |
| 08:30 | Daily summary, dispatch schedule and project MIS | Directors |
| 08:35 | Morning note (AI briefing): the exceptions summarised as what matters most today | Directors |

   On the Live POC today: 08:30 mails go to autoelectron.jp@gmail.com; the 08:35 briefing goes to waseemraj@mcast.co.in (owner's decision).

4. **Confirm the morning note reaches someone.** If the recipient setting is left unset, the note goes to whichever user is first in the system. Send one manually and confirm it arrives before go-live.
5. Review the alerts: drawings awaiting customer approval, purchase orders over the PCC, bank guarantees expiring.

# Part 3 — Cut-over and running it

## Step 10: Opening balances from Tally

**Owner:** Accounts with the CA · **Effort:** 1 week, plus the CA's review

Choose the cut-over date first. **1 April is strongly preferred**; a mid-year cut-over means two systems in one financial year and a costlier audit.

Bring across, in this order:

1. **Trial balance** as at the day before cut-over, as an opening journal entry. It must balance to the rupee before anything else is entered.
2. **Customer and supplier balances**, invoice by invoice, not lump sums — otherwise ageing, the MSME 45-day clock and payment allocation are wrong from day one.
3. **Stock on hand** by item and warehouse, with valuation, including material at subcontractors.
4. **Open sales orders and purchase orders**, with quantities already delivered and billed.
5. **Retention held** by customers, per project.
6. **Bank guarantees** with expiry dates (the expiry alert needs them).
7. **Fixed assets** with gross block, accumulated depreciation and remaining life.
8. **Employee balances**: leave, loans, advances.

- Opening entries use the difference account `1910 Temporary Opening`, never Stock Adjustment (doc 11, A1).
- Reconcile the opening trial balance against Tally; the CA signs it off. This is the most important go-live control.

## Step 11: Backups, audit trail and retention

**Owner:** The implementer · **Effort:** half a day, then ongoing

- Daily automated backups of database and files, **with a copy on a server physically in India** (Rule 3(5), Companies (Accounts) Rules — mandatory).
- Keep books of account, vouchers and the audit trail for **8 financial years** (s.128(5)).
- **Test a restore** once before go-live and once a year after.
- **Settings outside the database — a restore does not carry them:**
  - `encryption_key` — stored passwords are encrypted with it. Without it a restored system looks healthy but cannot send email. Keep it with the backups, guarded like a password; `restore-key.sh` puts it back.
  - `server_script_enabled` (bench-wide) and `host_name`.
  - After any restore, send a test email and confirm it arrives.
- Confirm the audit trail is enabled and nobody, including the administrator, can disable it.
- Backup schedule and monitoring on the server: doc 08.

## Step 12: Deployment and upgrades

**Owner:** The implementer · **Effort:** half a day to set up, then every deploy

How it works:

1. **Configuration in the package wins over configuration in the screens.** Every install and upgrade re-imports it.
2. **A workflow, approval role or notification changed in the ERPNext screens is reverted at the next upgrade.** To change a rule, change it in the package and deploy.
3. **Deploying from a stale copy reverts the business rules** to that copy's version, silently — everything keeps working and ordinary tests pass.

Rules:

- **Deploy from a tagged release, never a copied folder.** Check out the tag, then upgrade. Record which version is running.
- **Take a backup before any install or upgrade**; restore it if the checks fail.
- **Read the output of every upgrade.** After each install and upgrade the system verifies the approval authority. If it repaired anything, it prints a banner and writes an Error Log entry naming each rule, its old value and its restored value. A banner means the package and the agreed configuration differ — reconcile them before the next deploy.
- **Run the build checks after every upgrade**, before announcing the system is available. They assert, among other things, that the approval authority is where MSCAST put it and that only administrators hold `System Manager`.
- Commands: doc 08.

## Go-live checklist

Go-live is signed off only when every line is yes.

| # | Check | Owner |
|-------------|------------------------------------------------------|---------------------------------|
| 1 | Opening trial balance entered, balanced and signed off by the CA | Accounts |
| 2 | Customer and supplier balances match Tally, invoice by invoice | Accounts |
| 3 | Stock matches a physical count, including material at subcontractors | Stores |
| 4 | Every supplier has a GSTIN, and every MSME supplier a Udyam number | Purchase |
| 5 | Every item has an HSN/SAC code | Accounts |
| 6 | A test invoice produces the correct CGST+SGST and IGST | Accounts |
| 7 | Two payroll cycles have run in parallel and matched | HR |
| 8 | Each person has their own login; no shared accounts | The implementer |
| 9 | Approval workflows tested by the people who will use them | All |
| 10 | Print formats checked against real MSCAST paperwork | The implementer |
| 11 | Daily backup running, and a restore tested | The implementer |
| 12 | Audit trail on and confirmed non-disableable | Accounts |
| 13 | Administrator password changed from the installation default | The implementer |
| 14 | The CA has a read-only Auditor login | Accounts |
| 15 | **Setup-wizard administrator cut back to `System Manager` only** (a fresh install gives it every manager role; 41 in the POC) | The implementer |
| 16 | **No operational user holds `System Manager`** | The implementer |
| 17 | **A director has received the morning note** (received, not just sent) | The implementer |
| 18 | **Build checks pass on the production site**, including the approval-authority assertion | The implementer |
| 19 | **Running version is a tagged release**, and recorded | The implementer |
| 20 | Every role card handed to the person who holds that role | The implementer |

## The first month

Watch these, most important first:

1. **Is everyone using it?** A transaction entered a week late makes the system look wrong. If someone keeps a parallel spreadsheet, find out why — usually a missing field or report.
2. **Does the daily summary look right?** Fastest way to catch a configuration error.
3. **Is anyone reading the morning note?** The same exception 6 mornings running means nobody is reading it or a procedure is not followed.
4. **Is the MSME 45-day report clean?** Each overdue MSME bill is a disallowed expense at assessment.
5. **Does the month-end close work?** Run it once with the CA before it is needed for real.

Expect adjustments in the first month.
