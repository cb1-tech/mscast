---
title: "MSCAST ERP — Client Setup Guide"
---

# MSCAST ERP — Client Setup Guide

**For:** MSCAST Engineering Pvt Ltd · **System:** ERPNext v16 with India Compliance, Frappe HR and India Payroll · **Version:** 1.0 · **Date:** 19 September 2026

## How to use this guide

This is the sequence to take a freshly installed system to the point where MSCAST can run the business on it. The steps are in dependency order: masters before transactions, tax setup before invoices, opening balances last. Skipping ahead creates rework, because ERPNext validates against what already exists.

Each step names **who owns it** — in a ten-person company one person often wears several hats, but the owner should be a single named individual, not a department.

Allow about three weeks of part-time effort for steps 1 to 9, then a month of parallel running before you rely on the system alone.

> **A note on the demonstration system.** What you were shown is a proof of concept containing fictional data — every customer and supplier name ends in "(DEMO)". The production system starts empty. Nothing from the demonstration carries across except the configuration itself.

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

## Before you start: what to collect

Gather all of this before touching the system. Most delays in an ERP go-live are waiting for one missing number.

| What | Why it is needed | Who holds it |
|---|---|---|
| GSTIN, PAN, TAN | Every invoice, every TDS deduction, every return | Accounts / CA |
| CIN, date of incorporation, registered address | Letterhead, statutory reports, MCA filings | Company secretary |
| Udyam registration (if MSCAST is itself an MSME) | MSME status on your own documents | Accounts |
| IEC code | Export invoices and shipping documents | Accounts |
| Bank account details, IFSC, branch | Payment entries, bank reconciliation, cheque printing | Accounts |
| Company logo (PNG, transparent background) and letterhead artwork | Print formats on every document | Sanjay / design |
| Digital signature token | e-invoice and e-way bill, if enabled | Directors |
| Last audited balance sheet and the current trial balance from Tally | Opening balances | CA |
| List of customers with GSTIN, state and addresses | Sales invoices, place of supply | Sales |
| List of suppliers with GSTIN, **Udyam number and MSME class** | MSME 45-day tracking, Schedule III disclosure | Purchase |
| Item list with HSN/SAC codes and units of measure | GST rates, stock, BOM | Engineering + Accounts |
| Employee list: joining dates, UAN, ESIC, PAN, bank, salary structure | Payroll | HR |
| Open sales orders, purchase orders, stock on hand, retention held, bank guarantees | Opening transactions | All functions |

The two that consistently cause trouble are **supplier Udyam numbers** and **HSN codes**. Without Udyam numbers the MSME 45-day report cannot work, and section 43B(h) disallowance is a real cash cost at assessment. Without HSN codes no GST invoice can be submitted at all.

# Part 1 — Foundations

## Step 1: Company and financial year

**Owner:** Accounts · **Effort:** half a day

1. Create the company record: legal name exactly as on the GST certificate, abbreviation `MSCAST`, default currency INR, country India.
2. Enter GSTIN, PAN, TAN, CIN and the registered address. These appear on printed documents and in GST returns — a typo here propagates everywhere.
3. Set the financial year to 1 April – 31 March.
4. Set the time zone to **Asia/Kolkata**. Do this even if a server sits elsewhere; every statutory clock — the MSMED 45-day rule, GST periods, payroll cut-offs — runs on Indian dates.
5. Decide the date the system becomes the book of record and note it. Nothing before that date should be entered as a live transaction.

## Step 2: Chart of accounts and cost centres

**Owner:** Accounts with the CA · **Effort:** one to two days

ERPNext ships a standard Indian chart. Adapt rather than rebuild — a heavily customised chart makes every future upgrade and every standard report harder.

Heads MSCAST needs beyond the default set, all of which exist in the demonstration system:

- Reserves and Surplus; Share Capital
- Borrowings — the HDFC facility
- Lease Liabilities
- Retention Receivable — money held back by customers pending performance
- Work in Progress — Projects
- Provision for Gratuity; Provision for Income Tax; Deferred Tax Asset and Liability
- Prior Period Expenses; Fines and Penalties under Law — kept separate because they are disallowed for tax
- Petty Cash

Cost centres: at minimum one per function that owns a budget. Do not create a cost centre per project — projects are tracked as projects, and duplicating them as cost centres doubles the maintenance for no benefit.

## Step 3: Users, roles and who approves what

**Owner:** Sanjay · **Effort:** half a day

Create one user per person. Shared logins destroy the audit trail, which is the one thing that cannot be reconstructed afterwards — and under the Companies (Accounts) Rules the audit trail is not optional.

| Role | Typically held by | Can do | Cannot do |
|---|---|---|---|
| Projects Manager | Design / projects head | PCC, drawings, MDF, project schedule, kick-off | Approve own PCC; certify BRM |
| Purchase Manager | Purchase engineer | RFQ, PO, supplier masters, BRM certification | Approve a PO they raised |
| Stores | Stores in-charge | Receipts, issues, free-issue transfers, dispatch | Change item rates |
| Accounts | Accounts executive | Invoices, payments, journals, GST returns | Certify a BRM |
| HR | HR and admin officer | Employees, attendance, leave, payroll | Accounts postings |
| Director | Managing Director | Everything, read-only on operations plus approvals | — |
| Statutory Auditor | External CA | Read, report, print, export — including version history | Write anything at all |

The auditor role matters more than it looks. Giving your CA a read-only login with access to the version history means the audit-trail requirement is satisfied by evidence rather than by assertion.

**Three separations to preserve**, because they are what make the control environment real:

- The person who raises a purchase order does not approve it.
- The person who certifies a supplier bill (BRM) is not the person who pays it.
- The person who prepares payroll is not the person who releases the payment.

## Step 4: Master data

**Owner:** each function for its own masters · **Effort:** one week

Load in this order — each depends on the one before.

1. **UOM and item groups.** Keep the list short. Every extra item group is a decision someone has to make on every new item.
2. **Items.** Item code, name, group, stock UOM, **HSN/SAC code**, GST rate template, whether it is a stock item, whether it is a fixed asset. For an engineer-to-order business, do not attempt to create an item for every part on every machine; create items for what you buy, stock or sell repeatedly, and let the PCC and MDF carry the one-off detail.
3. **Warehouses.** At minimum: Stores, Work in Progress, Finished Goods, and one per subcontractor holding your free-issue material. That last one is how ITC-04 reporting stays honest.
4. **Customers.** Name, GSTIN, state, addresses, credit terms, payment terms.
5. **Suppliers.** Name, GSTIN, state, addresses — and **Udyam number plus MSME class (Micro / Small / Medium)** wherever it applies. Ask every supplier for this in writing; a supplier's own declaration is your evidence.

## Step 5: GST configuration

**Owner:** Accounts with the CA · **Effort:** two days

1. Enter the company GSTIN and confirm the state code. The system decides CGST+SGST versus IGST by comparing your state code with the place of supply — get the address wrong and every invoice is wrong.
2. Create the tax templates: Output GST in-state, Output GST inter-state, Input GST in-state, Input GST inter-state.
3. Attach item tax templates for each GST rate you deal in.
4. Confirm with the CA:
   - **e-invoice applicability.** The threshold is aggregate turnover based; at MSCAST's size it may not yet apply, but it changes and it is checked retrospectively.
   - **e-way bill** thresholds for your despatch patterns, including ODC movements.
   - **ITC-04** for goods sent to job workers — the one-year return rule for inputs, three years for capital goods.
   - HSN/SAC codes against what is actually supplied, including engineering drawings sold as a deliverable.
5. Switch on the audit trail. In India Compliance this cannot be switched off again, which is the point.

## Step 6: HR and payroll

**Owner:** HR · **Effort:** two to three days

1. Departments, designations and reporting lines.
2. Holiday list for the financial year: weekly offs plus the public holidays MSCAST observes.
3. Employees: joining date, department, designation, UAN, ESIC number, PAN, bank details.
4. Company statutory registrations: EPF, ESIC, Professional Tax (Maharashtra), Labour Welfare Fund.
5. Salary structure. The demonstration uses Basic 50%, HRA 40% of basic, conveyance and special allowance, with PF at 12% (₹15,000 ceiling), ESIC at 0.75% up to the wage limit, Maharashtra PT, and TDS on salary. Replace with MSCAST's actual structure.
6. Shift and attendance. If a biometric device is used, it pushes punches into the system and attendance is generated from them; agree who reviews exceptions and by when.
7. Gratuity: set the rule (15/26 days of last drawn basic per completed year under the Payment of Gratuity Act) so the provision can be computed each year end.

**Run payroll in parallel with the existing method for two full cycles** before switching. Payroll errors are visible to every employee and damage confidence in the whole system.

# Part 2 — MSCAST's own documents

## Step 7: The MSCAST forms

These are the forms built specifically for how MSCAST works. They are what distinguishes this system from a generic accounting package, and each needs an owner and a rule about when it is raised.

| Form | Raised by | When | Why it exists |
|---|---|---|---|
| **PCC** — Purchase Cost Calculation | Projects | Before quoting, revised on scope change | The cost baseline. Every purchase order is measured against it |
| **Project Kick-off** | Projects | On receipt of the customer PO | Forces the PO to be checked against the offer — price, scope, payment terms, LD, GST, BG — before work starts |
| **Drawing register** | Design | Every drawing, every revision | Revision control, and proof of what was issued to whom |
| **Transmittal** | Design | Whenever drawings go out | Record of what was sent to the customer or vendor, and acknowledgement |
| **MDF** — Material Data File | Design | On design release | The material list procurement works from |
| **RFQ / Supplier Quotation** | Purchase | Before ordering bought-outs | Technical and commercial comparison on one screen |
| **Purchase Order** | Purchase | After approval | Controlled against the PCC budget |
| **Inspection Plan** | Quality | Per stage, per supplier | In-process, pre-dispatch, third-party and customer inspection |
| **BRM** — Billing Routing Memo | Purchase | On every supplier bill | Certifies quantity, rate, inspection and delivery **before** accounts can pay |
| **MDM** — Material Dispatch Memo | Stores | Each dispatch lot | What physically goes, including free-issue items |
| **Delivery Instruction** | Stores | Direct-to-site dispatches | Consignee, transporter, LR, vehicle, Annexure-I |
| **Commissioning Report** | Site | On commissioning | Specified versus achieved, punch list, provisional acceptance |
| **Spares Handover** | Site | At handover | Commissioning and mandatory spares, with part numbers |
| **Project Certificate** | Projects | Acceptance milestones | Triggers retention release |
| **Client Claim** | Projects | Scope variation, idle time, escalation | Money owed beyond the contract, tracked to settlement |
| **Customer Asset register** | Stores | Customer tooling received | Assets held on your premises that are not yours |

## Step 8: Print formats and letterhead

**Owner:** Sanjay · **Effort:** one day

Load the logo and letterhead once — address, CIN, GSTIN, IEC — and every printed document inherits it. Check each format against a real document MSCAST issues today and adjust wording before anyone outside the company sees one.

## Step 9: Email, alerts and reports

**Owner:** Sanjay · **Effort:** half a day

1. Configure the outgoing mail account on the company domain. Confirm SPF, DKIM and DMARC are set in DNS, or mail lands in spam.
2. Set the site URL correctly — document links inside emails are built from it.
3. Decide who receives the daily management summary and at what hour. The demonstration sends at 08:30 IST, as the office opens.
4. Review the alerts: drawings awaiting customer approval, purchase orders over the PCC, bank guarantees expiring. Each must reach a named person who will act, not a distribution list nobody reads.

# Part 3 — Cut-over

## Step 10: Opening balances from Tally

**Owner:** Accounts with the CA · **Effort:** one week, plus the CA's review

Choose the cut-over date first. **1 April is strongly preferred** — a mid-year cut-over means two systems in one financial year and an audit that costs more.

Bring across, in this order:

1. **Trial balance** as at the day before cut-over, as an opening journal entry. It must balance to the rupee before anything else is entered.
2. **Customer and supplier balances**, invoice by invoice, not as lump sums — otherwise ageing, the MSME 45-day clock and payment allocation are all wrong from day one.
3. **Stock on hand** by item and warehouse, with valuation. Include material lying with subcontractors.
4. **Open sales orders and purchase orders**, with what is already delivered and billed.
5. **Retention held** by customers, per project.
6. **Bank guarantees** with expiry dates — without the dates, the expiry alert cannot fire.
7. **Fixed assets** with gross block, accumulated depreciation and remaining life.
8. **Employee balances**: leave, loans, advances.

Reconcile the opening trial balance against Tally and have the CA sign it off. This is the single most important control in the entire go-live.

## Step 11: Backups, audit trail and retention

**Owner:** Sanjay · **Effort:** half a day, then ongoing

- Daily automated backups of database and files, **with a copy on a server physically in India** — this is required by Rule 3(5) of the Companies (Accounts) Rules, not a preference.
- Books of account and vouchers retained for **eight financial years** (section 128(5)); the audit trail likewise.
- **Test a restore.** A backup nobody has restored is a belief, not a backup. Do it once before go-live and once a year after.
- Confirm the audit trail is enabled and that no one, including the administrator, can disable it.

## Go-live checklist

Nobody signs off go-live until every line is yes.

| # | Check | Owner |
|---|---|---|
| 1 | Opening trial balance entered, balanced and signed off by the CA | Accounts |
| 2 | Customer and supplier balances match Tally, invoice by invoice | Accounts |
| 3 | Stock matches a physical count, including material at subcontractors | Stores |
| 4 | Every supplier has a GSTIN, and every MSME supplier a Udyam number | Purchase |
| 5 | Every item has an HSN/SAC code | Accounts |
| 6 | A test invoice produces the correct CGST+SGST and IGST | Accounts |
| 7 | Two payroll cycles have run in parallel and matched | HR |
| 8 | Each person has their own login; no shared accounts | Sanjay |
| 9 | Approval workflows tested by the people who will use them | All |
| 10 | Print formats checked against real MSCAST paperwork | Sanjay |
| 11 | Daily backup running, and a restore tested | Sanjay |
| 12 | Audit trail on and confirmed non-disableable | Accounts |
| 13 | Administrator password changed from the installation default | Sanjay |
| 14 | The CA has a read-only auditor login | Accounts |

## The first month

Watch these, in this order of importance:

1. **Is everyone actually using it?** A transaction entered a week late is worse than useless — it makes the system look wrong. If somebody is keeping a parallel spreadsheet, find out why; it is usually a missing field or a report they need and do not have.
2. **Does the daily summary look right?** It is the fastest way to catch a configuration error, because wrong numbers are obvious to whoever knows the business.
3. **Is the MSME 45-day report clean?** Each overdue MSME bill is a disallowed expense at assessment.
4. **Does the month-end close work?** Run it once with the CA before you need it for real.

Expect to adjust in the first month. That is normal, and it is much cheaper than trying to predict everything in advance.
