# 05 — ERP Implications of MSCAST's Business Model

> **Everything in this file is INFERENCE** drawn from public facts (01–04) plus the ERP-MSCAST project file "Revised Proposal - ERPENS - Mscast.pdf" [ERP1] (ERPNext implementation by ERPens: base modules + custom Engineering Management, Project Enhancements and Procurement Enhancements; 12–14 weeks). It must be validated in the discovery workshop. Date: 2026-09-16.

## 1. Business-model read-out

| Public fact | Source | ERP implication |
|---|---|---|
| ≤10 employees, ₹1–2 Cr turnover self-declared (GST band ₹1.5–5 Cr), but sells machines worth ₹11 L – ₹2 Cr each | [IM2] [IMB] | Few, large, lumpy orders → **project-centric** ERP (Project = Sales Order = cost centre); a single project can be a big share of annual revenue, so project P&L and cash-flow visibility matter more than volume throughput. |
| Offers design services (layouts, P&IDs, hydraulic circuits) + machines + erection supervision | [IP1] [IM1] | Mixed revenue types in one contract: engineering (services, SAC), supply (goods, HSN), site services. Need **separate line types, tax codes and revenue recognition** per contract. |
| "Head Design" is the promoter; ERP proposal has high-effort Engineering Management module (drawings, revisions, MDF, bought-out tracking, manhours) | [TI1] [ERP1] | **Engineer-to-Order (ETO)**: design happens *after* order; BOM is born from drawings; engineering hours are a major cost. |
| No works address public; tiny headcount; proposal includes supplier coordination, free-issue material, inspection planning, delivery instructions, Material Dispatch Memo | [ERP1] [IM2] | Fabrication/machining largely **outsourced (job work)** with MSCAST buying raw material & bought-outs and issuing them to fabricators → subcontracting, job-work GST compliance, third-party inspection, direct dispatch from vendor to site. |
| HDFC ₹2.5 Cr charge | [ZC1] | Likely bank guarantees (ABG/PBG) and working-capital limits → track **BGs, LCs and margin money** by project. |
| IEC held; "Export" in GST NOB | [IM2] | Export order flow (LUT/IGST refund, shipping bill, BRC/e-BRC, packing list, COO) must be supported even if infrequent. |
| Quality statement: "100% quality check before any despatch" | [IM7] | Pre-dispatch inspection as a mandatory gate before dispatch/invoice. |

## 2. Typical order-to-cash flow for a casting-machine project (proposed reference process)

```
1  Enquiry (IndiaMART/TradeIndia/referral/exhibition)
      → ERPNext Lead (source tagged)            [CRM]
2  Techno-commercial discussion: heat size, radius/strands, billet section, utilities,
   scope split (supply / erection / civil exclusions)
      → Opportunity + "Technical Questionnaire" (custom child table)
3  Budgetary offer → revisions → final techno-commercial offer
      → Quotation (versions), cost estimate sheet (material kg, bought-outs, fab rate,
        engineering hrs, erection mandays, freight, BG cost, contingency)
4  PO / LoI from customer; commercial terms: advance %, payment milestones, ABG/PBG,
   LD clause, delivery schedule, warranty period, retention %
      → Sales Order + Payment Terms Template + Project auto-created
      → Project kick-off workflow (proposal §2.2)
5  Advance received against ABG → Payment Entry (advance) + Bank Guarantee record
6  Engineering: GA/layout → customer approval → detail drawings → hydraulic & P&ID
   → BOM release (by assembly) ; revisions controlled
      → Engineering Management module: drawing register, revision, approval
        workflow, MDF, manhour timesheets
7  Procurement: Material Requests from released BOM
      - Raw material (plates, sections, rounds, pipes; copper mould tubes)
      - Bought-outs (see §4)
      → RFQ → Supplier Quotation → Techno-commercial comparison → PO
8  Fabrication/machining at vendors (job work)
      - Free-issue material sent under delivery challan
      → Subcontracting Order / custom FIM tracking; GST ITC-04
      - Stage & final inspection (in-house / customer / TPI)
      → Inspection plan + Quality Inspection
9  Dispatch in lots (often ODC loads, direct from vendor to customer site)
      → Dispatch schedule, Material Dispatch Memo, Delivery Note (per lot),
        packing list, e-way bill, transporter/LR details
10 Invoicing: supply invoices per dispatch lot (HSN) ; engineering invoices per drawing
   milestone (SAC) ; e-invoice (IRN) if applicable
11 Erection supervision & commissioning at site
      → Tasks + site timesheets, travel expense claims, manday billing
      → Commissioning / hot-trial report ; Completion Certificate
12 Retention release (after PG test/warranty) & PBG return ; LD deduction if any
      → Retention tracking (proposal §2.2), BG expiry alerts
13 Warranty & after-sales: spares orders, service visits, AMC
      → Serial No per machine, Warranty Claim, Maintenance Visit
```

## 3. BOM structure & depth (expected)

A steel CCM is a deep, multi-level engineered BOM; an aluminium billet caster is somewhat shallower.

```
L0  CCM – Project XYZ (1 set)                       [ETO, project-specific item]
L1  ├─ Ladle turret / ladle car
L1  ├─ Tundish, tundish car, tundish preheater
L1  ├─ Mould assembly (per strand) + mould oscillator
L1  │   L2 ├─ Copper mould tube (bought-out)         L3 … fasteners, seals
L1  ├─ Secondary cooling (spray) chamber & headers
L1  ├─ Withdrawal & straightening unit (per strand)
L1  │   L2 ├─ Rolls, bearings, gearbox, motor (bought-outs), fabricated frame
L1  ├─ Dummy bar & storage
L1  ├─ Torch cutting machine / shear
L1  ├─ Run-out roller table, transfer, cooling bed / conveyors
L1  ├─ Hydraulic system: power pack, cylinders, valves, piping
L1  ├─ Water system: primary / secondary / machinery circuits (pumps, filters, heat exchanger, cooling tower – often bought-out)
L1  ├─ Electrical & automation: MCC, VFDs, PLC/HMI, instrumentation, cabling
L1  └─ Erection kit, spares (commissioning & 2-year), documentation
```
- Typical depth: **4–6 levels**, several hundred to a few thousand line items per machine. **[INFERENCE]**
- Many items are **project-specific (non-stock)** → item naming convention: `<Project>-<Assembly>-<Drawing No>-<Rev>`; separate generic stock items for bought-outs.
- BOM releases are **incremental** (long-lead items first) — ERP must allow partial BOM release and change management (ECN) without breaking MR/PO links.
- Weight (kg) is a key attribute: fabrication is often priced per kg; freight/ODC planning uses weights.

## 4. Bought-out items (typical, to seed item groups & supplier masters)
| Group | Examples |
|---|---|
| Mechanical drives | geared motors, gearboxes, couplings, brakes, bearings & housings, chains/sprockets |
| Hydraulics & pneumatics | power packs, cylinders, proportional/servo valves, accumulators, hoses, fittings |
| Casting-specific | copper mould tubes/plates, mould jackets, spray nozzles, oscillator springs/bearings, rolls, dummy-bar heads, tundish nozzles/refractory (customer or bought-out), hot-top rings/graphite (aluminium) |
| Water systems | pumps, strainers/filters, plate heat exchangers, cooling towers, valves, instrumentation (flow/pressure/temperature) |
| Electrical & automation | PLC/HMI (e.g. Siemens), VFDs, MCC panels, sensors, encoders, pyrometers, cables |
| Cutting | oxy-fuel torch cutting sets, shear blades |
| Raw material | MS plates, structural sections, rounds, seamless pipes, SS pipes |
| Services | machining, fabrication, galvanising/painting, TPI, transport (ODC), crane hire |

ERP notes: supplier-wise lead time and approved-make lists (customers often specify makes); techno-commercial comparison (proposal §2.3); supplier performance (OTD, rejection) reports.

## 5. Manufacturing / subcontracting model
- Expect **"make" = subcontracted fabrication** + in-house assembly/trial (if any). Use ERPNext **Subcontracting Order / Receipt** (v14+) or the proposal's custom Free-Issue Material tracking; ensure vendor-wise FIM balance, scrap/wastage reconciliation, and **GST job-work compliance (delivery challan under Rule 55, ITC-04 filing)**.
- Work Orders / Job Cards are only needed if MSCAST has its own shop; otherwise project tasks + inspection stages suffice.
- Costing: project cost = material (issued + direct-to-project POs) + subcontract charges + engineering manhours × rate + site mandays + freight + BG/finance cost + warranty provision.

## 6. Dispatch, erection & commissioning
- Dispatch in **lots/consignments** by assembly, frequently direct from vendor works → Delivery Note must support "ship-from vendor" addresses and e-way bills generated by MSCAST as supplier (bill-to-ship-to).
- Material Dispatch Memo & delivery instructions (proposal §2.3) → link to Sales Order lines & packing lists (case-wise).
- Site phase: erection supervision (manday rates, travel/boarding), commissioning, hot trials, performance-guarantee test, **Completion Certificate** (proposal §2.2) triggering milestone invoice & retention clock.
- Site issues/punch lists → Project Tasks or Issue doctype.

## 7. Commercial & finance specifics
| Topic | Requirement |
|---|---|
| Payment milestones | e.g. 30% advance / 60% pro-rata against dispatch / 10% on commissioning (typical Indian capital-equipment terms — confirm). Use Payment Terms Template on SO; milestone billing on Project. |
| Retention | Retention % withheld from invoices, released after PG/warranty → custom Retention ledger (proposal §2.2) or separate receivable account + due-date tracking. |
| Bank guarantees | ABG / PBG / warranty BG: amount, bank, expiry, claim date, margin money → ERPNext **Bank Guarantee** doctype + expiry reminders. |
| Liquidated damages | LD % per week of delay, cap → capture on SO; track delay vs contractual delivery. |
| Price variation | Some steel-plant contracts have PV clauses on steel/copper indices — optional field. |
| Advances to vendors | Vendor advances against PO; debit-note on rejection. |
| TDS / TCS | TDS on contractor/professional payments (194C/194J); customers deduct TDS on engineering invoices. |
| GST | Supply of goods (HSN) vs services (SAC); possible composite/works-contract treatment for supply+erection — **tax advisor to confirm**. E-invoice applicability depends on aggregate turnover threshold (currently ₹5 Cr) — MSCAST is near the band (GST turnover 1.5–5 Cr [IM2]). E-way bills mandatory for dispatches. |
| Export | Proforma invoice, commercial invoice (USD/EUR), packing list, LUT for zero-rated exports, shipping bill, BL/AWB, certificate of origin, e-BRC; multi-currency SO/Invoice & exchange gain/loss. |

## 8. Engineering management (maps to proposal §2.1)
- Drawing register: project, assembly, drawing no., title, revision, status (Draft → For Approval → Approved by Customer → Released for Manufacture), transmittal to customer/vendor.
- Engineering change: revision impact on BOM, MR, PO, vendor work; superseded-drawing control at vendors.
- Manhours: timesheets by project & activity (layout, detail design, hydraulics, P&ID, vendor visit, site) → cost and billable-hours for pure-service jobs (S1–S5 in 02).
- Knowledge reuse: template BOMs by machine family (e.g. "CCM 4/7 2-strand 130 sq"), standard assemblies (WSU, oscillator) → faster quotations and estimate accuracy.

## 9. Master-data implications
- **Item groups:** Machines (ETO), Assemblies, Fabricated parts, Bought-outs (sub-groups per §4), Raw material, Spares, Consumables, Engineering services, Site services.
- **HSN/SAC review:** currently declared HSN codes are parts-oriented (84549000, 84179000, 8412, 9033, 49119920) [IM1]. Complete machines likely need 8454 30 (casting machines), conveyors 8428, hydraulic cylinders 8412 21, and services SAC 9983 (engineering) / 9987 (installation) — **confirm exact 8-digit/6-digit codes with the tax consultant** before loading item tax templates.
- **Customers:** plant name, group company, GSTIN, site address (ship-to) separate from billing, consultants/EPC involved.
- **Suppliers:** capability tags (fabrication/machining/hydraulics/electrical), approved makes, location (for ODC freight), job-work registration.
- **Serial numbers:** each machine / strand assembly for warranty & spares history.
- **UOMs:** Nos, Set, Kg, Metre, Manday, Manhour, Lot.

## 10. Reports / KPIs to design for
- Project P&L: estimate vs budget vs actual (material, subcontract, engineering hours, site, freight) and margin erosion.
- Order book & revenue forecast by milestone; cash-flow forecast (advances, dispatch receivables, retention, BG release).
- Engineering: drawings due vs released, revision counts, hours by project.
- Procurement: open POs by project, long-lead items, vendor OTD & rejection, FIM balance per vendor.
- Dispatch schedule vs contractual delivery (LD exposure).
- Receivables ageing incl. retention; BG expiry calendar.
- Sales funnel by source (IndiaMART / TradeIndia / referral / exhibition) and win-rate by machine type.

## 11. Gaps / checks against the ERPens proposal [ERP1]
| Topic | In proposal? | Recommendation |
|---|---|---|
| Engineering drawings, revisions, MDF, manhours | Yes (§2.1) | Define MDF meaning & format early |
| Retention, completion certificate, dispatch schedule, kick-off | Yes (§2.2) | Add BG & LD tracking explicitly |
| Techno-commercial comparison, MDM, FIM, inspection plan, supplier performance | Yes (§2.3) | Link FIM to GST ITC-04 output |
| Multi-level ETO BOM with partial release / ECN | Partly ("BOM setup" in timeline) | Specify BOM release & change workflow |
| Cost estimation / quotation costing sheet | Not explicit | Add estimate template per machine family |
| Milestone billing & payment schedule | Not explicit | Include in Sales/Project config |
| Bank guarantees / LCs | Not mentioned | Configure Bank Guarantee doctype |
| E-invoice / e-way bill (India Compliance app) | "GST/TDS compliance setup" | Confirm e-way bill & e-invoice scope |
| Export documentation & multi-currency | Not mentioned | Add if exports are real |
| Warranty, spares, service visits | Not mentioned | Phase 2 (Support/Maintenance module) |
| IndiaMART/TradeIndia lead integration | Not mentioned | Phase 2 automation (API → Lead) |
| Data migration of past projects/customers/drawings | "Data migration" in go-live week | Scope volume early |

---
### Source keys used in this file
| Key | URL / reference |
|---|---|
| IM1 / IM2 / IM7 | https://m.indiamart.com/mscast-engineering/ ; https://m.indiamart.com/mscast-engineering/aboutus.html ; https://www.indiamart.com/mscast-engineering/aboutus.html |
| IP1 | https://m.indiamart.com/mscast-engineering-pvt-ltd/ |
| IMB | https://m.indiamart.com/impcat/billet-casting-machines.html |
| TI1 | https://www.tradeindia.com/mscast-engineering-pvt-ltd-3965535/ |
| ZC1 | https://www.zaubacorp.com/MSCAST-ENGINEERING-PRIVATE-LIMITED-U74900PN2010PTC137644 |
| ERP1 | ERP-MSCAST project file "Revised Proposal - ERPENS - Mscast.pdf" |
