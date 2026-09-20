---
title: "MSCAST ERP — Data Request: covering note and draft email"
---

# Data Request — covering note and draft email

**Version 1.1 · 20 September 2026**

The workbook is ready to send: `MSCAST ERP - Data Collection Workbook.xlsx`, 16 sheets.

This document holds the message that should go with it, and the answer to the question MSCAST will actually ask — *how long will this take us?*

> **Correction in version 1.1 — read this before sending.** Version 1.0 of the draft email told MSCAST that *"purchase orders and supplier bills are different: there the separation is enforced and cannot be bypassed."* **Half of that is wrong.** Purchase orders are genuinely separated — sending one for approval needs `Purchase User`, approving it needs `MSCAST Director`, and nobody holds both. Supplier bills are not: a director holds roles that can create a BRM, certify it and mark it paid. The paragraph below has been rewritten. **If the version 1.0 text was already sent or forwarded, send the corrected paragraph after it** — telling a client a control exists when it does not is the one error that is worse than the control being absent.

---

## Draft email

> **Subject:** MSCAST ERP — what we need from you to start on real data
>
> Dear Aiqaz, dear Mustaque,
>
> Following the demonstration, here is the workbook that turns it into your system.
>
> The demonstration you saw runs entirely on invented data — every customer and supplier name in it ends in "(DEMO)". None of that carries across. The production system starts empty and is built from this workbook, which is why it matters more than it looks.
>
> **Please don't wait until it is complete.** Sheets 1 to 5 are the masters — company, customers, suppliers, items, employees — and nothing else can be loaded until they exist. If you send only those, we can begin. The rest can follow.
>
> Two things are worth flagging because they hold everything else up if they are missing:
>
> - **Udyam numbers for your MSME suppliers.** Without them the 45-day clock cannot run, and a bill past 45 days is a disallowed expense under section 43B(h) — real money at assessment. Please ask each supplier for their number in writing; their own declaration is your evidence.
> - **HSN/SAC codes on every item.** Without them a GST invoice cannot be submitted at all.
>
> Alongside the workbook we still need four of your own documents, because the system currently carries *our reading* of them rather than yours: your **PCC** sheet, the **Project MIS** format, the **Billing Routing Memo**, and one sample **MDM** with its Delivery Instruction and Annexure-I. A photograph of a filled-in paper copy is perfectly good.
>
> And four questions for your CA: the **accounting basis** (we have assumed AS with SMC exemptions, not Ind AS), the **income tax regime** (assumed s.115BAA at 25.168%), **how work in progress should be valued**, and whether **PF, ESI and gratuity** apply as we have modelled them. Each assumption is written into the system where it matters, so nothing is hidden — but they should be confirmed rather than inherited.
>
> **Two decisions we would like your view on, and we would rather raise them than let you find them later.**
>
> As the system stands, a director can prepare a cost sheet and then approve it, and can verify a customer purchase order and then approve the kick-off. For a company of your size that is normal and we have left it that way deliberately — but it means those approvals are a second look rather than a second pair of hands.
>
> The second is the one that matters more, because it is the step that sends money out of the company. **A director can also raise a supplier-bill certificate, certify it, and mark it paid — all three, alone.** That is not what we originally described to you, and we would rather correct it than leave it. It is a consequence of the directors holding the operational roles as well as the approving one, which in a company of ten people is difficult to avoid entirely.
>
> Two things are worth saying alongside it. **Purchase orders are genuinely separated** — a purchase order cannot reach a director for approval unless someone in Purchase has sent it, and no director holds that role. And **no bill of any kind can be paid without a certified certificate**; that block applies to everyone including the directors, and it is the control that actually protects the money.
>
> If you would prefer the tighter arrangement, it is a small change: preparation moves to your staff, and the directors approve only. Tell us which you want.
>
> Happy to walk through any sheet on a call.
>
> Kind regards,
> Sanjay

---

## What to expect back, and when

The honest answer to *"how long will this take us?"* is that the effort is not evenly spread. Setting expectations early stops the whole thing stalling on sheet 6.

| Sheet | Who fills it | Realistic effort | The usual hold-up |
|---|---|---|---|
| 1 Company | Accounts | 30 minutes | Finding the CIN and IEC |
| 2 Customers | Sales | Half a day | GSTINs for older customers |
| 3 Suppliers | Purchase | **One to two weeks** | **Udyam numbers — every supplier has to be asked** |
| 4 Items | Engineering + Accounts | Two to three days | HSN codes; the temptation to list every part |
| 5 Employees | HR | Half a day | UAN and ESIC numbers |
| 6 Opening trial balance | Accounts + CA | One day | Must balance to the rupee before anything loads |
| 7–8 Receivables, payables | Accounts | One to two days | **Invoice by invoice, not lump sums** — this is the one people shortcut |
| 9 Opening stock | Stores | Two days | Material lying at subcontractors is always forgotten |
| 10–11 Open orders | Sales, Purchase | One day | — |
| 12 Installed machines | Sales / Projects | Two hours | Worth doing even if nothing else is |
| 13 Bank guarantees | Accounts | One hour | **Expiry dates** — without them the alert cannot fire |
| 14 Users | Directors | One hour | See the roles reference on that sheet |

**Sheet 3 is the critical path.** Not because it is hard, but because it depends on suppliers replying. It should be started on day one regardless of everything else.

**Sheets 7 and 8 are where quality is lost.** Sent as totals rather than invoice by invoice, the ageing is wrong, the MSME clock is wrong and payment allocation is wrong from day one — and it is not fixable later without redoing it.

---

## What we do with it

1. Masters loaded and checked (sheets 1–5)
2. Users created, roles assigned, everyone logs in once and changes their password
3. Each person walks their own process on the system, holding their role card
4. Opening balances loaded and reconciled against Tally **to the rupee**, signed off by the CA
5. One month of parallel running before Tally is retired

Full sequence in the *Client Setup Guide*, and the day itself in the *Production Cutover Runbook*.

---

## Before sending — a short checklist

- [ ] **Use the version 1.1 paragraph on approvals.** The version 1.0 wording claimed supplier bills were separated. They are not.
- [ ] Delete nothing from the workbook. The grey example rows are meant to be there; MSCAST deletes them.
- [ ] Confirm the current recipients — this goes to both directors, not one.
- [ ] Attach nothing else. One workbook and one message; a pack of documents gets skimmed.
- [ ] Say when you will chase. A data request with no follow-up date is a data request that arrives in March.
- [ ] Have the role cards ready to send **after** sheet 14 comes back, not with it — they are for the people who will use the system, and they land better once the names exist.

---

## A note on raising the second decision at all

There is a temptation to fix the BRM separation quietly before MSCAST ever hears about it, and send the original paragraph unchanged.

That would be a mistake for a practical reason as much as an honest one. The arrangement exists because the directors hold operational roles, which in a ten-person company is a real constraint rather than an oversight — so "fixing" it silently means imposing a working practice on them that they never agreed to, and which they will route around in week three. Raised as a choice, it is a conversation about how they want to work. Discovered later by their auditor, it is a question about what else was described inaccurately.

The same argument applies to having claimed it in the first place. Correcting it in the next message costs a paragraph; leaving it costs the credibility of every other control in the document.
