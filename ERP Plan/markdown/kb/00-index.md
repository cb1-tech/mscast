# MSCAST Engineering Pvt. Ltd. — Business Knowledge Base

**Last updated:** 2026-09-16 · **Scope:** public-internet research (IndiaMART, TradeIndia, MCA-data aggregators, own website, directories, competitor & industry sources) + the ERP-MSCAST project proposal · **Purpose:** support the ERPNext implementation and future sales, marketing and automation work.

## 1. One-paragraph overview
MSCAST Engineering Private Limited (CIN U74900PN2010PTC137644, GSTIN 27AAGCM8444B1ZI, IEC 3112018541) is a Pune-based private company incorporated on 29 Oct 2010 [ZC1]. It designs and supplies **continuous casting machines (CCMs) and CCM equipment for steel billet making, aluminium billet casting machines, pouring (ingot) casting machines and conveyors**, and sells **engineering services**: plant/CCM layouts, P&IDs for primary/secondary/machinery cooling, CCM hydraulic circuits and CCM erection supervision [IM1] [IP1]. The promoter-director (Mustaque Ahmed N. Chandankeri; "Company CEO" on IndiaMART, "Head Design" on TradeIndia) leads a very small team (≤10 people) with a declared turnover of ₹1–2 Cr (GST band ₹1.5–5 Cr) [IM2] [TI1]. Paid-up capital is ₹1 lakh, with a ₹2.5 Cr HDFC Bank charge [ZC1]. FY2024-25 filings show revenue up ~7% and profit roughly doubled, with borrowings down ~81% [FE1]. Its online presence is minimal: two unconnected free IndiaMART accounts with no specs, prices or photos, a thin TradeIndia listing, and a placeholder GoDaddy website [IM1] [IP1] [TI1] [WEB1]. The business looks like a design-led **engineer-to-order project business that outsources much of its fabrication** (inference, see 05).

## 2. Files
| File | What's inside | Use it for |
|---|---|---|
| `01-company-profile.md` | Legal & statutory data, directors/roles, size & financial indicators, history timeline, addresses, contacts, declared HSN codes | Company master, compliance set-up, onboarding |
| `02-products-catalogue.md` | Every listed product/service with URL, IndiaMART IDs, categories; inferred product architecture; spec template per machine type | Item groups, item attributes, quotation templates, catalogue rebuild |
| `03-market-customers-competitors.md` | Customer segments, industry context (secondary steel, aluminium extrusion), trade fairs, 15+ competitors with URLs & price points | Sales strategy, CRM segmentation, pricing benchmarks |
| `04-digital-presence.md` | All listings/profiles, ratings, SEO/content audit, prioritised improvements | Marketing plan, lead-generation automation |
| `05-erp-implications.md` | **Inference:** ETO order-to-cash flow, BOM depth, bought-outs, subcontracting/job work, dispatch/erection, retention/BG/LD, GST/export, KPIs, gaps vs ERPens proposal | ERP discovery workshop agenda & design |
| `sources.md` | Every URL visited with result and what it contributed; searches run | Traceability |
| `raw/` | Page captures, IndiaMART embedded JSON, images (DINs redacted) | Re-checking exact values |

## 3. How to use
- Every fact carries a **source key** like `[IM2]`; resolve it in the file's footer table or `sources.md`.
- **[CONFLICT]** = sources disagree (both values shown); **[UNVERIFIED]** = weak/single/secondary source; **[STALE]** = old data; **[INFERENCE]** = analyst reasoning, not published fact.
- Treat everything as **"to be confirmed with MSCAST"** before loading it into ERP masters. The questions in §6 are a ready agenda.
- Personal data is limited to names and business roles. No personal phone numbers are stored; phone numbers shown are IndiaMART call-routing (PNS) numbers. Director identification numbers are left out on purpose.

## 4. Key facts at a glance
| Item | Value | Src |
|---|---|---|
| Incorporated | 29-10-2010, RoC Pune, private company limited by shares, Active | ZC1 |
| Capital | Authorised ₹1 L; paid-up ₹1 L | ZC1 FE1 |
| Latest filings | AGM 30-09-2025; balance sheet 31-03-2025 | FE1 IF1 |
| Directors | Mustaque Ahmed N. Chandankeri (since 2010); Aiqaz Mustaque Chandankeri (since 2019); Zameer Alam Chandankeri (since 2010; **possibly ceased**) | ZC1 FE1 IM6 |
| Staff / turnover | ≤10 people; ₹1–2 Cr self-declared; GST band ₹1.5–5 Cr | IM2 |
| Registered office | Kondhwa Khurd, Pune 411048 (see 01) | ZC1 |
| Offer | Steel CCMs & CCM equipment, aluminium billet casting machine, pouring casting machine, conveyors; layouts, P&IDs, hydraulics, erection supervision | IM1 IP1 |
| Online | IndiaMART ×2 (free, no reviews), TradeIndia, LinkedIn ×2, placeholder website | 04 |

## 5. Gaps & unknowns (public research could not find these)
1. **Product specifications, price ranges, capacity ranges, photos**: none published anywhere.
2. **Customer names, installed base, project references, export destinations**: none public (no trade-data hits, news, case studies or testimonials).
3. **Works/factory address, in-house manufacturing facilities and machine tools**: not published. Unclear whether fabrication is in-house or outsourced.
4. **Absolute financials** (revenue, PAT, net worth in ₹): only growth percentages obtained (Tofler blocked, reports paid).
5. **Current board composition**: sources conflict on Zameer Alam Chandankeri.
6. **Certifications** (ISO 9001 etc.), UDYAM/MSME registration, banker details: not published.
7. **Trade-fair participation, patents, trademarks, tenders**: nothing found.
8. **LinkedIn content**, employee count on LinkedIn, Google Business Profile: not accessible.
9. Status of **mcast.co.in** e-mail domain: unreachable from the research environment.
10. Meaning of **"MDF"** in the ERP proposal, and the actual contract terms (advance %, retention %, BG, LD): not public.

## 6. Questions to confirm with the company (discovery-workshop agenda)
**Corporate & compliance**
1. Is Zameer Alam Chandankeri still a director? Who are the key people and roles (design, projects, purchase, accounts, site)?
2. Registered office vs operating office vs any works/assembly yard: which addresses should go into ERP (company, warehouse, dispatch-from)?
3. Correct legal and brand spelling (MSCAST / Mscast / MsCast), official e-mail domain (mcast.co.in vs mscastengineering.com), logo files.
4. UDYAM number, ISO certification, bankers, BG/LC limits (HDFC charge ₹2.5 Cr: still active?).
5. Is e-invoicing applicable (aggregate turnover)? Is there an LUT for exports? Which HSN/SAC codes are used on invoices today (declared codes are parts-only)?

**Products & engineering**
6. Machine families actually sold in the last 5 years (steel CCM radius/strands/billet sizes; aluminium billet caster sizes/moulds; pouring machines; conveyors) and share of revenue each.
7. Are there standard/template designs that can become template BOMs? Typical BOM line count and depth?
8. CAD tools used, drawing numbering and revision practice, what "MDF" means.
9. In-house vs outsourced: fabrication, machining, assembly, trial runs, painting? Who are the key fabricators, and is material issued free of cost?

**Sales & projects**
10. Number of projects per year, typical order value, lead time (PO to dispatch, dispatch to commissioning).
11. Standard commercial terms: advance %, dispatch payments, retention %, ABG/PBG %, LD clauses, warranty period.
12. Customer list and segments (IF mini mills, extruders, EPCs, exports by country); repeat/spares business share.
13. Lead sources today (IndiaMART, TradeIndia, referrals, consultants, exhibitions) and approximate monthly enquiry volume.
14. How are erection supervision and commissioning billed (lump sum or per manday + expenses)?

**Data migration**
15. Open projects, open POs, vendor FIM balances, retention receivables and live BGs as at go-live; historic drawings to migrate.

## 7. Source list (summary; full list in `sources.md`)
- IndiaMART listing 1: https://www.indiamart.com/mscast-engineering/ (m-site pages: home, aboutus, products-and-services, continuous-casting-machine, other-products, registration-directors-info)
- IndiaMART listing 2: https://www.indiamart.com/mscast-engineering-pvt-ltd/ (home, aboutus, products-and-services, machinery-services, other-services, registration-directors-info, services)
- TradeIndia: https://www.tradeindia.com/mscast-engineering-pvt-ltd-3965535/
- MCA aggregators: ZaubaCorp, InstaFinancials, Falcon eBiz, CompanyVakil, InsiderBiz (Tofler, TheCompanyCheck, ClearTax blocked)
- Website: https://mscastengineering.com/ · LinkedIn (2 pages, not readable)
- Industry/competitors: IndiaMART directories, Electrotherm, Megatherm, Electramech, Concast Techno, Meeracle, V-fast, Almec Tech, AlCircle, Lohaa, Aluminium Bharat
- Internal: ERP-MSCAST project file "Revised Proposal - ERPENS - Mscast.pdf"

### Source keys used in this file
IM1 https://m.indiamart.com/mscast-engineering/ · IM2 https://m.indiamart.com/mscast-engineering/aboutus.html · IM6 https://m.indiamart.com/mscast-engineering/registration-directors-info.html · IP1 https://m.indiamart.com/mscast-engineering-pvt-ltd/ · TI1 https://www.tradeindia.com/mscast-engineering-pvt-ltd-3965535/ · ZC1 https://www.zaubacorp.com/MSCAST-ENGINEERING-PRIVATE-LIMITED-U74900PN2010PTC137644 · IF1 https://www.instafinancials.com/company/mscast-engineering-private-limited-U74900PN2010PTC137644 · FE1 https://www.falconebiz.com/company/MSCAST-ENGINEERING-PRIVATE-LIMITED-U74900PN2010PTC137644 · WEB1 https://mscastengineering.com/
