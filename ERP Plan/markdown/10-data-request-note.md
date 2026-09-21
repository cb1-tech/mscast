---
title: "MSCAST ERP — Data Request: covering note and draft email"
---

# Data Request — covering note and draft email

**Version 2.0 · 21 September 2026**

- Send with: `MSCAST ERP - Data Collection Workbook.xlsx` (16 sheets).
- To: both directors, Aiqaz and Mustaque.
- The approvals paragraph below is the corrected one: supplier bills (BRM) are **not** separated; purchase orders are. If the version 1.0 email (which said both were separated) was already sent or forwarded, send the corrected paragraph as a follow-up.

## Draft email

> **Subject:** MSCAST ERP — what we need from you to start on real data
>
> Dear Aiqaz, dear Mustaque,
>
> Following the demonstration, here is the workbook that turns it into your system. The demonstration runs on invented data (every customer and supplier name ends in "(DEMO)"); none of it carries across. The production system starts empty and is built from this workbook.
>
> **Please don't wait until it is complete.** Sheets 1 to 5 are the masters (company, customers, suppliers, items, employees); nothing else can be loaded until they exist. Send those first; the rest can follow.
>
> Two items hold up everything else:
>
> - **Udyam numbers for your MSME suppliers.** Without them the 45-day clock cannot run, and a bill unpaid after 45 days is a disallowed expense under s.43B(h). Please ask each supplier for their number in writing.
> - **HSN/SAC codes on every item.** Without them a GST invoice cannot be submitted.
>
> **Your own formats.** The system carries our reading of these, not yours: your **PCC** sheet, the **Project MIS** format, the **Billing Routing Memo (BRM)**, and one sample **MDM** with its Delivery Instruction (DI) and Annexure-I. A photo of a filled-in paper copy is fine.
>
> **Also from you:**
>
> - Suppliers that should be exempt from BRM certification (electricity, water, rent, telephone, statutory payments).
> - Who will run the monthly jobs (MSME review, GST, month-end close).
> - Which Tally year we take opening balances from, and who exports the masters and balances.
> - Your CA's name and contact.
>
> **For your CA:** the accounting basis (we assumed AS with SMC exemptions, not Ind AS); the income-tax regime (we assumed s.115BAA at 25.168% — has the election been made?); how work in progress should be valued; the basis on which EPF applies at your headcount; whether "Lease Liabilities" (an Ind AS 116 head) should stay; when the MSME 45-day clock starts; whether free issue to fabricators goes out on a job-work challan; and whether customers deduct TDS under s.194C. Each assumption is visible in the system, but it should be confirmed rather than inherited.
>
> **Two decisions for you.**
>
> 1. A director can prepare a cost sheet and then approve it, and can verify a customer PO and then approve the kick-off. For a company of your size we have left this deliberately; it means those approvals are a second look, not a second person.
> 2. **A director can also raise a supplier-bill certificate (BRM), certify it and mark it paid — all three, alone.** That is not what we first described to you, and we are correcting it. It follows from the directors holding the operational roles as well as the approving one.
>
> **Purchase orders are separated:** a PO cannot reach a director for approval unless someone in Purchase has sent it, and no director holds that role. And **no supplier bill can be paid without a certified BRM**, for anyone including the directors; that is the control that protects the money. If you prefer the tighter arrangement, preparation moves to your staff and the directors approve only. Please tell us which you want.
>
> Happy to walk through any sheet on a call.
>
> Kind regards,
> Sanjay

## Effort per sheet

| Sheet | Who fills it | Effort | Usual hold-up |
|---------------------------|-------------------------|------------------|------------------------------|
| 1 Company | Accounts | 30 minutes | CIN and IEC |
| 2 Customers | Sales | Half a day | GSTINs for older customers |
| 3 Suppliers | Purchase | **1–2 weeks** | **Udyam numbers: every supplier must be asked** |
| 4 Items | Engineering + Accounts | 2–3 days | HSN codes; listing every part |
| 5 Employees | HR | Half a day | UAN and ESIC numbers |
| 6 Opening trial balance | Accounts + CA | 1 day | Must balance to the rupee before anything loads |
| 7–8 Receivables, payables | Accounts | 1–2 days | **Invoice by invoice, not totals** |
| 9 Opening stock | Stores | 2 days | Material lying at subcontractors |
| 10–11 Open orders | Sales, Purchase | 1 day | — |
| 12 Installed machines | Sales / Projects | 2 hours | Worth doing even if nothing else is |
| 13 Bank guarantees | Accounts | 1 hour | **Expiry dates**, or the alert cannot fire |
| 14 Users | Directors | 1 hour | Roles reference is on that sheet |

- **Sheet 3 is the critical path** (it waits on supplier replies). Start it on day one.
- **Sheets 7–8 as totals** make ageing, the MSME clock and payment allocation wrong from day one, and cannot be fixed later without redoing them.

## What happens next

1. Masters loaded and checked (sheets 1–5).
2. Users created, roles assigned; everyone logs in once and changes their password.
3. Each person walks their own process on the system with their role card.
4. Opening balances loaded and reconciled against Tally to the rupee, signed off by the CA.
5. One month of parallel running before Tally is retired.

Full sequence: doc 05 (Client Setup Guide); the cutover day: doc 08 (Production Cutover Runbook).

## Before sending

- [ ] The approvals paragraph is the version 2.0 text above.
- [ ] Workbook unchanged: the grey example rows stay; MSCAST deletes them.
- [ ] Addressed to both directors.
- [ ] Attach only the workbook.
- [ ] State a follow-up date.
- [ ] Send the role cards (doc 09) **after** sheet 14 comes back, not with it.
- [ ] Do not change the BRM separation quietly before MSCAST decides (Q21): raise it as their choice.
