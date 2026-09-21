---
title: "MSCAST ERP — Demo Run-sheet"
---

# MSCAST ERP — Demo Run-sheet

**For:** the MSCAST walkthrough · **Version:** 1.0 · **Date:** 21 September 2026

**How to pitch it:** *"This is our reading of your requirements. Correct us."* Every screen below ends with a question for MSCAST. Their answers matter more than the demo does.

- **Length:** about 45 minutes, 10 stops. Stop 6 is the one to protect if time runs short.
- **Each stop gives:** who is logged in, where to click, what to say (two or three points) and what to ask.
- **The pictures** were taken on the demo system on 21 September 2026. What you see on the day should match them.

## Before the meeting

- **Use the DEV instance: https://mscastdev.carobar.net**
  - The live POC (mscast.carobar.net) is open for people to try. Its users can change, and some of the demo logins no longer exist there.
  - Dev is a separate copy with the full demo cast. Nothing done in the meeting touches live.
  - An orange **DEV INSTANCE** banner runs along the top of every page. Say once: *"this is our test copy"*, and move on.
- **One browser window per person** (Chrome profiles or incognito windows). Each login allows only two sessions at a time. A third one logs out the oldest, which is what disrupted the first screenshot run.
- **Log in beforehand** as Mustaque, Meera, Anita and S. Joshi, and keep the four windows open.
- **Passwords** are shared separately and are not written in this sheet.
- **Five minutes before:** open the home page as Mustaque. If the cards load, everything is up.

## The cast

| Person | What they do | Login on dev |
|---|---|---|
| Mustaque Chandankeri | Director (approves) | latookaushik@yahoo.com |
| Aiqaz Chandankeri | Director (backup) | latookaushik@hotmail.com |
| Anita Deshpande | Accounts Manager | carobar.tradecars@gmail.com |
| Meera Rane | Design draughtsman | meera.rane@mscast.co.in |
| S. Joshi | Chartered Accountant (read-only) | autoelectron.jp+ca@gmail.com |
| Rohit Kulkarni | Prepares cost sheets (named on the PCC) | — not used live |

The directors are MSCAST's real directors. Everyone else is a demo face, and only the names change at go-live.

---

# Stop 1 — The director's morning

![Home page as Mustaque](demo-screens/01-md-home.png){width=6.3in}

- **Login:** Mustaque.
- **Click:** sidebar → **Home**.
- **Say:**
  - One page answers *"where do we stand?"*: cash ₹1.07 Cr, receivables ₹24.64 L, payables ₹30.52 L, order book ₹3.45 Cr, retention held ₹4.53 L.
  - Each project card shows contract, cost, margin and billing against its delivery date.
  - **"Needs attention today"** lists seven items, one click each. Money falling due, MSME bills nearing 45 days, drawings stuck with the customer.
  - The same figures reach his inbox at 08:30 IST, so he doesn't have to log in to know.
- **Ask:**
  - *Is this what you look at first thing? What's missing, and what could go?*
  - *Who else should get the 08:30 summary?*

# Stop 2 — The cost sheet (PCC)

![PCC-2026-00001, approved](demo-screens/02-cost-sheet.png){width=6.3in}

- **Login:** Mustaque.
- **Click:** sidebar → **MSCAST PCC** → **PCC-2026-00001** (PROJ-0001, CCM 2-Strand 130sq for Sahyadri Steels).
- **Say:**
  - Built up component by component: ladle turret, tundish car, mould, WSU and so on. Each line is marked fabricated or bought-out.
  - It's on revision **R2**. Rohit prepared it, Mustaque approved it, and the system records both.
  - An approved PCC is locked. A change means a new revision, and the old one stays on file.
- **Show the print:** printer icon → format **MSCAST PCC Sheet**.

![The PCC as printed](demo-screens/03-cost-sheet-print.png){width=5.2in}

- **Ask:**
  - *This layout is our guess. Can we have a real PCC of yours, even a photo of a filled-in sheet?*
  - *Who prepares it today, and does a director always approve it?*

# Stop 3 — Kick-off held: the customer PO doesn't match our offer

![KICK-2026-00002, PO Query Raised](demo-screens/04-kickoff-held.png){width=6.3in}

- **Login:** Mustaque.
- **Click:** search bar (Ctrl+K) → **MSCAST Project Kickoff** → **KICK-2026-00002** (Deccan Extrusions, PROJ-0002).
- **Say:**
  - Before a project starts, someone checks the customer's PO against our offer, point by point.
  - Here the PO says 100% payment on delivery. Our offer was 30% advance, 60% on dispatch and 10% after commissioning. The kick-off is held, status **PO Query Raised**.
  - The kick-off **cannot be approved** until the checklist is complete. The system is doing its most valuable job here.
- **Ask:**
  - *Is this checklist right? What else do you check on a customer PO: LD clauses, PBG, advance?*
  - *Who does this check today?*

# Stop 4 — Drawings, and who is waiting on whom

![Drawing Register as Meera](demo-screens/05-drawing-register.png){width=6.3in}

- **Login:** Meera (switch windows).
- **Click:** search bar → **MSCAST Drawing Register**.
- **Say:**
  - Every drawing shows its number, revision and status: Draft, For Customer Approval, Approved by Customer, Released for Manufacture.
  - Meera sees her own work. She doesn't see the books.
- **Then:** open **MSC-2601-PID-50** (Cooling water P&ID), which is waiting on the customer.

![A drawing waiting on the customer](demo-screens/06-drawing-with-customer.png){width=6.3in}

- **Say:**
  - A drawing cannot be **released for manufacture** until the customer has approved it. Only a Projects Manager can release it.
  - The revision history and the Google Drive link travel with the record.
- **Ask:**
  - *How do you number drawings today? Is MSC-YYNN-XXX-NN close?*
  - *Do customers approve by email, on a transmittal, or by marking up prints?*

# Stop 5 — The purchase order

![PUR-ORD-2026-00002, approved](demo-screens/07-purchase-order.png){width=6.3in}

- **Login:** Mustaque.
- **Click:** search bar → **Purchase Order** → **PUR-ORD-2026-00002** (Pushkar Fabricators, ₹44.76 L).
- **Say:**
  - Purchase raises the PO and a director approves it.
  - A PO **cannot be approved unless someone in Purchase sent it**, so every PO passes through two people.
- **Ask:**
  - *Is there a value below which a PO doesn't need a director?*

# Stop 6 — The BRM: no certified memo, no payment (the headline)

![BRM-2026-00003, certified with its four checks](demo-screens/08-brm-certified.png){width=6.3in}

- **Login:** Mustaque.
- **Click:** sidebar → **MSCAST BRM** → **BRM-2026-00003** (Shivneri Machining Works, ₹7.80 L).
- **Say:**
  - The Billing Routing Memo is MSCAST's own control. Before a supplier bill is paid, someone certifies quantity, rate, inspection and delivery against the PO.
  - All four boxes are ticked, and the memo shows who certified it and when.
  - **The system will not accept "Certified" with a box left unticked.** We tested that on purpose.
- **Now the moment:** switch to **Anita** and open **Payment Entry ACC-PAY-2026-00003** (Ashoka Heavy Fabricators, ₹2,85,600). It is a draft. Click **Submit**.

![Payment refused: no certified BRM](demo-screens/09-payment-refused.png){width=6.3in}

- **Say:**
  - *"Payment blocked: no BRM has been raised for supplier bill AHF/2026/0341."*
  - It applies to everyone: not at month end, not under pressure from the supplier, not through a journal entry either.
  - The payment stays a draft, so you can show this as often as you like.
- **Then:** search bar → **MSCAST BRM Register** (as Anita).

![BRM Register](demo-screens/10-brm-register.png){width=6.3in}

- **Ask:**
  - *Which suppliers, if any, should be exempt: utilities, statutory dues, petty cash?*
  - *Can we have a real BRM of yours to copy the layout from?*
  - *Today a director can prepare, certify and pay a BRM alone. Is that intended? (Q21)*

# Stop 7 — Dispatch and the proforma

![DN-26-00002 to Sahyadri Steels](demo-screens/11-dispatch.png){width=6.3in}

- **Login:** Mustaque.
- **Click:** search bar → **Delivery Note** → **DN-26-00002** (Sahyadri Steels, CCM-2S-130 plus erection supervision).
- **Say:** the machine is dispatched against the sales order, and GST is calculated and posted to the right heads automatically.
- **Then:** open **Sales Order SAL-ORD-2026-00001** → printer icon → **MSCAST Proforma Invoice**.

![Proforma invoice (demo watermark)](demo-screens/12-proforma-print.png){width=5.2in}

- **Say:**
  - The advance due (30%) is worked out from the order. Retention and PBG percentages are carried from the contract.
  - Every print carries a **DEMONSTRATION** watermark on this system.
- **Ask:**
  - *What do your MDM, Delivery Instruction and Annexure-I look like? A sample of each, please.*

# Stop 8 — Project MIS

![Project MIS](demo-screens/13-project-mis.png){width=6.3in}

- **Login:** Mustaque.
- **Click:** sidebar → **MSCAST Project MIS**.
- **Say:** one line per project: contract value, PCC estimate, PO commitments, billed. Estimate against commitment is where the margin is lost or kept.
- **Ask:**
  - *What columns does your MIS have today? Please send us the actual format.*

# Stop 9 — MSME 45-day dues

![MSME 45-Day Dues](demo-screens/14-msme-45-day.png){width=6.3in}

- **Login:** Anita.
- **Click:** search bar → **MSCAST MSME 45-Day Dues**.
- **Say:**
  - A payment to an MSME supplier made after 45 days cannot be deducted for income tax in that year (s.43B(h)). The report shows each bill's deadline, using each supplier's Udyam registration.
  - The home page shows the same figure as a warning: ₹7.80 L within 15 days.
- **Ask:**
  - *Do you have Udyam numbers for your suppliers? Which of them are micro or small?*

# Stop 10 — The CA's view: read everything, change nothing

![Balance Sheet, Schedule III](demo-screens/15-balance-sheet.png){width=6.3in}

- **Login:** S. Joshi (the CA).
- **Click:** search bar → **MSCAST Balance Sheet (Schedule III)**.
- **Say:**
  - Laid out in the Schedule III format. MSME payables are shown separately, as the law requires.
  - The CA can open anything.

![The CA opens a PCC: read-only](demo-screens/16-ca-read-only.png){width=6.3in}

- **Say:** the same PCC as in Stop 2, but the CA **cannot change it**. No auditor role can create, edit or delete anything, and the audit trail cannot be switched off.
- **Ask:**
  - *Who is your CA? We'd like them to review the chart of accounts and opening balances before go-live.*

---

# Questions to leave with MSCAST

| # | Question | Why it matters |
|---|---|---|
| 1 | Real formats: **PCC, Project MIS, BRM, MDM with DI and Annexure-I** (photos are fine) | Today the system carries our reading of them, not yours |
| 2 | **Q20:** a director can prepare a PCC or verify a PO and then approve it alone. Intended? | Segregation of duties |
| 3 | **Q21:** a director can create, certify and pay a BRM alone. Intended? | That is the step that releases money |
| 4 | Suppliers exempt from the BRM rule, if any | Otherwise every payment needs one |
| 5 | Who owns the monthly jobs: MSME review, GST, close | A control nobody runs is not a control |
| 6 | Tally: which year, and who exports the masters and balances | Opening balances must match Tally to the rupee |
| 7 | CA name and contact | Sign-off on the books before go-live |
| 8 | PO value limit, if any, below which a director needn't approve | Speeds up small purchases |

# Rough edges: say them before anyone finds them

- **Screens don't refresh by themselves over this link.** Press F5 to see someone else's change. It's a setting in the public link, not in the ERP, and it goes away on a proper server.
- **Balance sheet: "Goods received but not billed" shows ₹ −6.10 L.** A negative there is impossible in real books. It comes from the way the demo entries were loaded (receipts and bills entered without their real sequence). Point it out yourself: *"this is exactly what the CA review catches."*
- **MSME report: one row shows ₹ −2,26,560.** The bill reference starts DN/, so it is a debit note (goods returned) against that supplier, not a bill. Real data won't carry it.
- **The proforma carries MSCAST's real GSTIN.** It's on a demo system, so every print is watermarked **DEMONSTRATION** and none of them is a tax invoice.
- **Logins are placeholder email addresses.** Real staff get their own at go-live, and only the names change.
- **The orange DEV banner** is the test copy's marker. Production won't have it.

# After the meeting

- Write down every correction MSCAST gives, stop by stop. Those corrections are the real output of the meeting.
- Nothing needs resetting. The payment in Stop 6 stays a draft, and nothing else is changed by the walkthrough.
- If anything *was* changed on dev, it can be rebuilt from its saved copy in about ten minutes (`dev-create.sh`). Live is never affected.
