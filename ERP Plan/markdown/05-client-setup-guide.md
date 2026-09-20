---
title: "MSCAST ERP — Client Setup Guide"
---

# MSCAST ERP — Client Setup Guide

**For:** MSCAST Engineering Pvt Ltd · **System:** ERPNext v16 with India Compliance, Frappe HR and India Payroll · **Version:** 2.2 · **Date:** 20 September 2026

> **What changed in version 2.** Version 1.0 was written before the roles were rebuilt around real people and before the approval authority was settled. Its role table and two of its claims no longer matched the system. Every statement here has been checked against the running configuration. A new Step 12 covers deployment and upgrades, after a live incident in which an app install silently reverted the approval rules. Version 2.1 corrects the size of the administrator-account problem, which was worse than first reported. The differences are listed in the appendix.

> **Correction, version 2.2 (20 September).** This document previously claimed a separation of duties that does not exist. It said the person who prepares a BRM cannot certify it, and that a supplier bill passes through three different hands. Neither is true: both directors hold roles that can *create* a BRM, the role that certifies one, and the role that marks it paid, so a director can carry a supplier bill from creation to payment alone. The build checks missed it because the segregation test compared workflow transition roles, and creating a document is a permission rather than a transition. A test that asks the auditor's question — can one person create this and then approve it? — now runs on every build (**T6g**) and reports it. The payment block itself is unaffected and still holds for everyone.

## How to use this guide

This is the sequence to take a freshly installed system to the point where MSCAST can run the business on it. The steps are in dependency order: masters before transactions, tax setup before invoices, opening balances last. Skipping ahead creates rework, because ERPNext validates against what already exists.

Each step names **who owns it** — in a ten-person company one person often wears several hats, but the owner should be a single named individual, not a department.

Allow about three weeks of part-time effort for steps 1 to 9, then a month of parallel running before you rely on the system alone.

> **A note on the demonstration system.** What you were shown is a proof of concept containing fictional data — every customer and supplier name ends in "(DEMO)". The production system starts empty. Nothing from the demonstration carries across except the configuration itself.

**Companion documents:** *Standard Operating Procedures and Use Cases* (how the business runs on the system) and *Role Cards* (one page per role, for the people who will use it). The role cards are the thing to hand to staff; this guide is for whoever builds the system.

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

## Before you start: what to collect

Gather all of this before touching the system. Most delays in an ERP go-live are waiting for one missing number.

| What | Why it is needed | Who holds it |
|---|---|---|
| GSTIN, PAN, TAN | Every invoice, every TDS deduction, every return | Accounts / CA |
| CIN, date of incorporation, registered address | Letterhead, statutory reports, MCA filings | Company secretary |
| Udyam registration (if MSCAST is itself an MSME) | MSME status on your own documents | Accounts |
| IEC code | Export invoices and shipping documents | Accounts |
| Bank account details, IFSC, branch | Payment entries, bank reconciliation, cheque printing | Accounts |
| Company logo (PNG, transparent background) and letterhead artwork | Print formats on every document | Implementation partner / design |
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

**Every ledger entry must carry a cost centre.** This is checked automatically; an entry without one is a hole in the project MIS.

## Step 3: Users, roles and who approves what

**Owner:** Implementation partner · **Effort:** half a day

Create one user per person. Shared logins destroy the audit trail, which is the one thing that cannot be reconstructed afterwards — and under the Companies (Accounts) Rules the audit trail is not optional.

### The roles, and what each can and cannot do

This table reflects the configuration as it actually stands. *Role Cards* gives each of these a page of its own.

| Role | Typically held by | Can do | Cannot do |
|---|---|---|---|
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
| **Auditor** | External CA | Read, report, print, export — including version history | **Write anything at all** |

The auditor role matters more than it looks. Giving your CA a read-only login with access to the version history means the audit-trail requirement is satisfied by evidence rather than by assertion.

### What the software actually enforces

Three things are enforced in software and cannot be bypassed:

1. **A supplier bill cannot be paid without a certified BRM.** The payment entry is refused, and the reason is displayed.
2. **A drawing cannot be released for manufacture unless the customer has approved it**, and only a Projects Manager can release it.
3. **A purchase order cannot reach a director for approval except through someone holding `Purchase User`.** Sending it for approval and approving it are different roles, and no one person holds both.

### What is *not* separated, and should be understood before anyone claims it is

An earlier version of this guide said a fourth thing was enforced: that the person who prepares a BRM cannot certify it. **That was wrong**, and the way it was wrong is instructive.

Certifying a BRM is restricted to a director. But *creating* a BRM is a permission, not a workflow step — and both directors hold `Projects Manager`, which can create one. They also hold `Accounts Manager`, which marks a certified bill paid. So a director can create a supplier-bill certificate, certify it, and mark it paid, **without anybody else touching it**.

The build checks did not catch this for a long time because the segregation test compared *workflow transition* roles, and "prepare a BRM" is not a transition. A test that asks the question the way an auditor would — can one person create this document and then approve it? — now runs on every build and reports exactly this.

For a company of MSCAST's size this may well be acceptable. The point is that it is now a decision somebody has made, rather than a control somebody believes exists. **What is genuinely protected is the payment itself**: no certified BRM, no payment, for anyone. What is weaker than it looks is who may do the certifying.

### One separation that is deliberately not enforced

Both directors also hold the Projects Manager and Accounts Manager roles, because in a company of this size they must. That means a director **can** prepare a PCC and approve it, or verify a customer PO and approve the kick-off, alone.

This is an accepted position and it is stated openly here so that nobody is told a control exists that does not. Every approval is recorded with a name and a timestamp. Where the commitment is significant, have the *other* director approve it.

If MSCAST later wants this enforced, the way to do it is to move preparation to staff — a projects person prepares the PCC, Accounts verifies the customer PO — and leave the directors approving only.

### The role list is itself a control — audit it

**This is the step most likely to be done once and never revisited, and it undoes everything above when it drifts.**

In the demonstration system two accounts were found holding far more than their job needed:

- The **setup-wizard administrator** created by ERPNext itself had accumulated **41 roles** — every manager role in the system, plus a good deal it had no use for. It had never logged in and had never created a document. Forty-one roles on an unused account is not untidy; it means every separation above had an exception nobody had written down. It now holds `System Manager` and nothing else.
- An **ordinary staff account** — stores and projects roles — also carried **`System Manager`**, which bypasses every control in this guide. Removed.

**Both will recur on a fresh install.** The setup wizard always creates its own administrator with the same spread, and roles accumulate quietly on long-lived accounts. So:

- Cut the setup-wizard administrator back to `System Manager` only, as soon as the site is built. It is line 15 of the go-live checklist.
- **Nobody who does day-to-day work in the system should hold `System Manager`.** Administration is one named administrator plus the built-in `Administrator` account, and that is the whole list.
- The build checks report both, so a later drift is caught.

### Where the rules live

**Who may approve what lives in the packaged application, not in the ERPNext screens.** A workflow role changed through the interface will be reverted at the next upgrade. See Step 12.

## Step 4: Master data

**Owner:** each function for its own masters · **Effort:** one week

Load in this order — each depends on the one before.

1. **UOM and item groups.** Keep the list short. Every extra item group is a decision someone has to make on every new item.
2. **Items.** Item code, name, group, stock UOM, **HSN/SAC code**, GST rate template, whether it is a stock item, whether it is a fixed asset. For an engineer-to-order business, do not attempt to create an item for every part on every machine; create items for what you buy, stock or sell repeatedly, and let the PCC and MDF carry the one-off detail.
3. **Warehouses.** At minimum: Stores, Work in Progress, Finished Goods, and one per subcontractor holding your free-issue material. That last one is how ITC-04 reporting stays honest.
4. **Customers.** Name, GSTIN, state, addresses, credit terms, payment terms.
5. **Suppliers.** Name, GSTIN, state, addresses — and **Udyam number plus MSME class (Micro / Small / Medium)** wherever it applies. Ask every supplier for this in writing; a supplier's own declaration is your evidence.

GSTIN format and the state it implies are validated on entry, so a mistyped GSTIN is caught at the point of entry rather than at the point of filing.

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
6. Shift and attendance. **The biometric pull exists but is switched off in the demonstration system.** If MSCAST uses a device, enable it, run it for a week against manually checked attendance, and only then rely on it. Until it is enabled and proven, attendance is entered in the system. Either way, agree who reviews exceptions and by when. Duplicate attendance for one employee on one date is prevented automatically.
7. Gratuity: set the rule (15/26 days of last drawn basic per completed year under the Payment of Gratuity Act) so the provision can be computed each year end.

**Run payroll in parallel with the existing method for two full cycles** before switching. Payroll errors are visible to every employee and damage confidence in the whole system.

# Part 2 — MSCAST's own documents

## Step 7: The MSCAST forms

These are the forms built specifically for how MSCAST works. They are what distinguishes this system from a generic accounting package, and each needs an owner and a rule about when it is raised.

| Form | Raised by | Approved / certified by | When |
|---|---|---|---|
| **PCC** — Purchase Cost Calculation | Projects | **Director** | Before quoting, revised on scope change |
| **Project Kick-off** | Projects, verified by Accounts | **Director** | On receipt of the customer PO |
| **Drawing register** | Design | Projects Manager releases for manufacture | Every drawing, every revision |
| **Transmittal** | Design | — | Whenever drawings go out |
| **MDF** — Material Data File | Design | — | On design release |
| **RFQ / Supplier Quotation** | Purchase | — | Before ordering bought-outs |
| **Purchase Order** | Purchase | **Director** | After approval |
| **Inspection Plan** | Quality | Quality records the result | Per stage, per supplier |
| **BRM** — Billing Routing Memo | Purchase prepares | **Director certifies**, Accounts marks paid | On every supplier bill |
| **MDM** — Material Dispatch Memo | Stores | — | Each dispatch lot |
| **Delivery Instruction** | Stores | — | Direct-to-site dispatches |
| **Commissioning Report** | Site | — | On commissioning |
| **Spares Handover** | Site | — | At handover |
| **Project Certificate** | Projects | — | Acceptance milestones; triggers retention release |
| **Client Claim** | Projects | Accounts, then Director | Scope variation, idle time, escalation |
| **Customer Asset register** | Stores | — | Customer tooling received |
| **MSCAST Exception** | *raised by the system* | Cleared by the named owner | Automatically, every morning at 06:00 |

The drawing register is the one that changed most since version 1.0: it now carries a workflow rather than a free-text status. A drawing moves Draft → For Customer Approval → Approved by Customer → Released for Manufacture, and **cannot skip a step**.

## Step 8: Print formats and letterhead

**Owner:** Implementation partner · **Effort:** one day

Load the logo and letterhead once — address, CIN, GSTIN, IEC — and every printed document inherits it. Check each format against a real document MSCAST issues today and adjust wording before anyone outside the company sees one.

Every print format is rendered automatically as part of the build checks, so a format that has been broken by a field change is caught before anyone tries to print it in front of a customer.

## Step 9: Email, alerts and the daily rhythm

**Owner:** Implementation partner · **Effort:** half a day

1. Configure the outgoing mail account on the company domain. Confirm SPF, DKIM and DMARC are set in DNS, or mail lands in spam.
2. Set the site URL correctly — document links inside emails are built from it.
3. **Set who receives what.** Three things go out and each needs a named recipient who will act, not a distribution list nobody reads:

| Time | What | Who should get it |
|---|---|---|
| 06:00 | The overnight checks run. No email; findings land in the **MSCAST Exception** list | — |
| 08:30 | Daily management summary — the headline figures | Directors |
| 08:35 | The morning note — the exceptions turned into a few sentences saying what matters most today | Directors |

4. **Confirm the morning note actually reaches someone.** The recipient list is a configuration setting; if it is left unset the note falls back to whichever user happens to be first in the system, which may be nobody useful. Send one manually and confirm it arrives before go-live.
5. Review the alerts: drawings awaiting customer approval, purchase orders over the PCC, bank guarantees expiring.

# Part 3 — Cut-over and running it

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

**Owner:** Implementation partner · **Effort:** half a day, then ongoing

- Daily automated backups of database and files, **with a copy on a server physically in India** — this is required by Rule 3(5) of the Companies (Accounts) Rules, not a preference.
- Books of account and vouchers retained for **eight financial years** (section 128(5)); the audit trail likewise.
- **Test a restore.** A backup nobody has restored is a belief, not a backup. Do it once before go-live and once a year after.
- Confirm the audit trail is enabled and that no one, including the administrator, can disable it.

## Step 12: Deployment and upgrades

**Owner:** Implementation partner · **Effort:** half a day to set up, then a discipline

This step exists because of a real incident during the build, and it is the part of this guide most likely to be skipped and most expensive to skip.

**What happened.** The application was installed onto a working system from a directory that was slightly out of date. Installing an application re-imports its configuration and overwrites what is in the database. The approval rules silently went backwards — cost sheet approval returned to a system role, and bill certification returned to the purchase manager. Everything still worked. Every test still passed. Nobody would have noticed until an audit, or until the wrong person approved something.

**What this means in practice:**

1. **Configuration in the package wins over configuration in the screens.** Every install and every upgrade re-imports it.
2. **Changing a workflow, an approval role or a notification through the ERPNext interface is temporary.** It will be reverted at the next upgrade. If a rule must change, it changes in the package and is deployed.
3. **Deploying from a stale copy reverts the business rules** to whatever that copy contained.

**The rules to follow:**

- **Deploy from a tagged release, never from a copied folder.** Check out the tag, then upgrade. If you cannot say which version is running, you cannot say what the approval rules are.
- **Read the output of every upgrade.** The system verifies the approval authority after every install and every upgrade. If it had to repair anything it prints a banner and writes an Error Log entry naming each rule, what it was, and what it was restored to. A banner means the package and the agreed configuration have diverged — reconcile them before the next deploy, or it repeats.
- **Run the build checks after every upgrade**, before telling anyone the system is available. They assert, among other things, that the approval authority is where MSCAST put it and that nobody outside the administrators holds `System Manager`.
- **Take a backup before any install or upgrade.** Not as a formality — restore it if the checks fail.

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
| 8 | Each person has their own login; no shared accounts | Implementation partner |
| 9 | Approval workflows tested by the people who will actually use them | All |
| 10 | Print formats checked against real MSCAST paperwork | Implementation partner |
| 11 | Daily backup running, and a restore tested | Implementation partner |
| 12 | Audit trail on and confirmed non-disableable | Accounts |
| 13 | Administrator password changed from the installation default | Implementation partner |
| 14 | The CA has a read-only auditor login | Accounts |
| 15 | **The setup-wizard administrator is cut back to `System Manager` only.** On a fresh install it arrives holding every manager role — in the POC it had accumulated 41 | Implementation partner |
| 16 | **No operational user holds `System Manager`.** It bypasses every control in this guide | Implementation partner |
| 17 | **The morning note has been received by a director**, not just sent | Implementation partner |
| 18 | **The build checks pass on the production site**, including the approval-authority assertion | Implementation partner |
| 19 | **The running version is a tagged release** and is written down | Implementation partner |
| 20 | Every role card has been handed to the person who holds that role | Implementation partner |

## The first month

Watch these, in this order of importance:

1. **Is everyone actually using it?** A transaction entered a week late is worse than useless — it makes the system look wrong. If somebody is keeping a parallel spreadsheet, find out why; it is usually a missing field or a report they need and do not have.
2. **Does the daily summary look right?** It is the fastest way to catch a configuration error, because wrong numbers are obvious to whoever knows the business.
3. **Is anyone reading the morning note?** If the same exception appears six mornings running, either nobody is reading it or a procedure is not being followed. Both are worth knowing in week two rather than month six.
4. **Is the MSME 45-day report clean?** Each overdue MSME bill is a disallowed expense at assessment.
5. **Does the month-end close work?** Run it once with the CA before you need it for real.

Expect to adjust in the first month. That is normal, and it is much cheaper than trying to predict everything in advance.

# Appendix — what changed, and why

An audit on 20 September compared every claim in version 1.0 against the running system.

| Version 1.0 said | Reality | Resolution |
|---|---|---|
| Purchase Manager can do "BRM certification" | Certification is a director's | **Corrected** |
| Purchase Manager cannot "approve a PO they raised" | Cannot approve *any* purchase order | **Corrected** — it was weaker than the real rule |
| Projects Manager cannot "approve own PCC" | Cannot approve *any* PCC. But a director can approve their own | **Corrected, and the exception stated openly** |
| Role table listed seven generic roles | Eleven roles exist, including Design User, which did not exist in v1.0 | **Table rebuilt** from the live configuration |
| "Three separations to preserve", one of them payroll preparation versus release | Four separations are enforced in software; the payroll one is not among them | **Rewritten** as what is enforced versus what is practice |
| Biometric device "pushes punches into the system and attendance is generated from them" | The pull is switched off | **Corrected**, with an instruction to prove it before relying on it |
| Drawing register described as revision control | It now carries a workflow that cannot be skipped | **Updated** |
| Daily summary at 08:30 was the only scheduled output | The 06:00 overnight checks and the 08:35 morning note also run | **Step 9 rewritten** as a timetable |
| — | Nothing covered deployment or upgrades | **Step 12 added**, after an install silently reverted the approval rules |
| Go-live checklist had 14 lines | Six were missing | **Six lines added** |

Corrected again in **version 2.1**: version 2.0 said the demonstration administrator held "fourteen roles". The real number was **41**, and a second account — an ordinary staff login — was found holding `System Manager` as well, bypassing every control in this guide. Both are fixed, both now have a named step in Step 3 and two lines in the checklist, and both are checked automatically on every build.

Corrected again in **version 2.2**: the claim that preparing and certifying a BRM are separated was false, and is replaced by what the system actually does. See the correction note at the top.

Four things are now asserted automatically on every build and after every deploy, so they cannot drift back unnoticed: that the approval authority sits where MSCAST put it, whether any ordinary user can both raise and approve the same document, and whether anyone outside the administrators holds `System Manager`.
