# 02 — Products & Services Catalogue

> Last updated: 2026-09-16. Sources: IndiaMART (two seller accounts, all pages traversed), TradeIndia, own website. Source keys → URLs at the bottom and in `sources.md`.

## Headline finding
MSCAST's public catalogue is **thin**: 10 IndiaMART items (5 machines + 5 engineering services) and 2 TradeIndia items. **None** has specifications, price, MOQ, photos, applications or its own product-detail page (IndiaMART `PDP_VISIBILITY_FLAG = 0`; guessed `/proddetail/` URLs return 404). All descriptions are either blank or repeat the product name. Technical specs therefore **must be collected from the company** (drawings, quotations, GA drawings, datasheets) — see §4 for the specification template to fill in during ERP item-master design.

## 1. Summary table

| # | Name (as listed) | Portal / account | Category on portal | IndiaMART item ID | Portal "MCAT" (IndiaMART generic category) | Price | MOQ | Specs | URL |
|---|---|---|---|---|---|---|---|---|---|
| P1 | Aluminum Billet Casting Machine | IndiaMART / mscast-engineering | Continuous Casting Machine | 25600096312 | 187452 (Billet Casting Machines); also 156459 | "Ask Price" — none | none | none | https://www.indiamart.com/mscast-engineering/continuous-casting-machine.html#25600096312 |
| P2 | Continuous Casting Machines | IndiaMART / mscast-engineering | Other Products | 5687550373 | 3998 (Continuous Casting Machines) | none | none | none | https://www.indiamart.com/mscast-engineering/other-products.html#5687550373 |
| P3 | Conveyors | IndiaMART / mscast-engineering | Other Products | 5687550455 | 78120 (Conveyors) | none | none | none | https://www.indiamart.com/mscast-engineering/other-products.html#5687550455 |
| P4 | Pouring Casting Machine | IndiaMART / mscast-engineering | Other Products | 25600096433 | 160639 | none | none | none | https://www.indiamart.com/mscast-engineering/other-products.html#25600096433 |
| P5 | Continuous Casting Equipments | IndiaMART / mscast-engineering | Other Products | 5687550291 | 3998 (Continuous Casting Machines) | none | none | none | https://www.indiamart.com/mscast-engineering/other-products.html (anchor #5687550291 not linked on desktop) |
| S1 | P & I Diagrams For Primary/Secondary/Machinery Cooling | IndiaMART / mscast-engineering-pvt-ltd | Machinery Services | 2939522633 | 27842 | none | none | desc = name | https://www.indiamart.com/mscast-engineering-pvt-ltd/machinery-services.html#2939522633 |
| S2 | Preparation Of Plant Layout Drawing | IndiaMART / mscast-engineering-pvt-ltd | Other Services | 2939522012 | 174036 (Layout Drawings Services) | none | none | desc = name | https://www.indiamart.com/mscast-engineering-pvt-ltd/other-services.html#2939522012 |
| S3 | Preparation Of CCM Layout Drawing | IndiaMART / mscast-engineering-pvt-ltd | Other Services | 2939522130 | 174036 | none | none | desc = name | https://www.indiamart.com/mscast-engineering-pvt-ltd/other-services.html#2939522130 |
| S4 | CCM Erection Supervision Services | IndiaMART / mscast-engineering-pvt-ltd | Other Services | 2939522730 | 170262 | none | none | desc = name | https://www.indiamart.com/mscast-engineering-pvt-ltd/other-services.html#2939522730 |
| S5 | Preparation Of Hydraulic Circuits Related To CCM | IndiaMART / mscast-engineering-pvt-ltd | Other Services | 2939522597 | 1860 | none | none | desc = name | https://www.indiamart.com/mscast-engineering-pvt-ltd/other-services.html#2939522597 |
| T1 | Designing of casting machines | TradeIndia | Products & Services | — | — | none | none | none | https://www.tradeindia.com/mscast-engineering-pvt-ltd-3965535/product-services.html |
| T2 | "metel handling" [sic — metal handling] | TradeIndia | Products & Services | — | — | none | none | none | https://www.tradeindia.com/mscast-engineering-pvt-ltd-3965535/product-services.html |

Sources: P1–P5 [IM1] [IM3] [IM4] [IM5] [IM7]; S1–S5 [IP1] [IP3] [IP4] [IP5] [IP7]; T1–T2 [TI2]. Other directories (Connect2India) mirror P2, P3, P5 titles only [C2I].

## 2. Product detail records (everything that is public)

### P1 — Aluminum Billet Casting Machine
- **Category page:** https://m.indiamart.com/mscast-engineering/continuous-casting-machine.html (desktop https://www.indiamart.com/mscast-engineering/continuous-casting-machine.html) [IM4]
- **Category blurb:** "Offering you a complete choice of products which include Aluminum Billet Casting Machine." [IM7]
- **Description / specs / price / MOQ / applications:** none published. Image: IndiaMART generic stock category image only (`billet-casting-machines-250x250.jpg`). [IM4]
- **Meta title used by IndiaMART for the whole showroom:** "Continuous Casting Machine and Aluminum Billet Casting Machine Manufacturer | Mscast Engineering Private Limited, Pune" (search-result title) — i.e. this is the listing's lead product. [IM1]
- **Likely application (inference):** casting 6xxx-series aluminium extrusion billets/logs (vertical DC, hot-top or air-slip moulds) for extrusion plants and secondary aluminium smelters. **[INFERENCE]**

### P2 — Continuous Casting Machines
- **Category page:** https://m.indiamart.com/mscast-engineering/other-products.html [IM5]
- **Category blurb:** "Manufacturer of a wide range of products which include Continuous Casting Machines, Conveyors, Pouring Casting Machine and Continuous Casting Equipments." / "We are a leading Manufacturer of Continuous Casting Machines, Conveyors, Pouring Casting Machine and Continuous Casting Equipments from Pune, India." [IM7]
- **Specs/price/MOQ:** none. Appears in IndiaMART's Pune "Continuous Casting Machines" city directory without price or specs. [IMD]
- **Likely application (inference):** steel billet CCMs (curved-mould machines, typically 3/6, 4/7 or 6/11 m radius, 1–3 strands, 100–160 mm square billets) for induction-furnace / EAF mini steel plants — supported by the related service listings that use steel-CCM vocabulary ("primary/secondary/machinery cooling", "CCM erection supervision", "hydraulic circuits related to CCM"). **[INFERENCE]**

### P3 — Conveyors
- Category page as P2. No specs. Company blurb: "we have a team of engineers who are experts in the conveyors." [IM1]
- Likely scope (inference): billet/ingot transfer & cooling-bed conveyors, roller tables, scrap/charge-material conveyors for melt shops. **[INFERENCE]**

### P4 — Pouring Casting Machine
- Category page as P2. No specs. IndiaMART MCAT 160639. [IM5]
- Likely scope (inference): ladle-pouring / ingot or pig casting machine (chain-type or carousel) — requires confirmation. **[INFERENCE]**

### P5 — Continuous Casting Equipments
- Category page as P2. No specs. [IM5]
- Likely scope (inference): CCM sub-assemblies and spares — tundish & tundish car, mould & mould oscillator, withdrawal-straightening unit (WSU), dummy bar & storage, spray (secondary cooling) chamber, torch-cutting / shear, run-out roller table, cooling bed, hydraulic power pack, water system. **[INFERENCE]**

### S1–S5 — Engineering services (listing 2)
| ID | Service | Public description | What it tells us (inference) |
|---|---|---|---|
| S1 | P & I diagrams for primary / secondary / machinery cooling | "P & I diagrams for Primary/secondary/machinery cooling"; machinery category blurb "Providing you the best range of P & I Diagrams… with effective & timely delivery." [IP4] [IP7] | CCM water systems design: primary = mould cooling, secondary = spray-zone cooling, machinery = equipment cooling. Steel-CCM terminology. |
| S2 | Preparation of plant layout drawing | "Preparation of plant layout drawing" [IP5] | Melt-shop / casting-bay layout engineering. |
| S3 | Preparation of CCM layout drawing | "Preparation of CCM layout drawing" [IP5] | Machine GA / layout — probably the first deliverable of a CCM project. |
| S4 | CCM erection supervision services | "CCM Erection supervision services" [IP5] | Site service; implies manday-rate billing & travel expenses. |
| S5 | Preparation of hydraulic circuits related to CCM | "Preparation of hydraulic circuits related to CCM" [IP5] | Hydraulic design for oscillator, WSU, ladle turret, cutting; ties to HSN 8412. |

Services category blurb: "Leading Service Provider of Preparation Of Plant Layout Drawing, Preparation Of Ccm Layout Drawing, CCM Erection Supervision Services and Preparation Of Hydraulic Circuits Related To Ccm from Pune." [IP5]

### T1–T2 — TradeIndia
- "Designing of casting machines" and "metel handling" — names only, "Send Inquiry" buttons, no descriptions. [TI2]

## 3. Inferred product/service architecture (for ERP item & BOM design) **[INFERENCE — validate with MSCAST]**

```
MSCAST offering
├── A. Engineered machines (make-to-order / engineer-to-order projects)
│   ├── A1 Steel billet continuous casting machine (CCM) – complete or retrofit
│   ├── A2 Aluminium billet casting machine / casting table
│   ├── A3 Pouring / ingot casting machine
│   └── A4 Conveyors & metal-handling equipment
├── B. CCM equipment, sub-assemblies & spares (make-to-order, repeat items)
│   └── tundish, moulds/mould tubes & jackets, oscillator, WSU, dummy bar, spray headers, hydraulic cylinders & power packs, cooling bed parts …
├── C. Engineering services (billable, deliverable-based)
│   └── layouts, P&IDs, hydraulic circuits, casting-machine design (drawings, HSN 49119920)
└── D. Site services
    └── erection supervision, commissioning, trouble-shooting (manday-based)
```

## 4. Specification template to collect per machine (proposed ERP item attributes)

| Attribute group | Steel CCM | Aluminium billet caster | Conveyor |
|---|---|---|---|
| Capacity | t/heat, t/day, heat size (t), sequence casting | t/drop, drops/day, t/year | t/h, load per metre |
| Geometry | machine radius (e.g. 4/7, 6/11 m), no. of strands, strand pitch | casting pit depth, platen size, cylinder stroke | length, width, pitch, elevation |
| Product size | billet section (e.g. 100–160 mm sq), cut length | billet dia (e.g. 5"–10"), log length, no. of moulds | item size & temperature |
| Material / alloy | steel grades (MS, TMT, alloy) | alloy series (6063/6061 etc.) | material handled |
| Mould / technology | mould tube length, oscillation type/stroke/frequency, EMS | hot-top / air-slip, mould lubrication, launder, filter/degasser | chain / roller / belt / apron |
| Utilities | water flow for primary/secondary/machinery circuits, power kW | water flow, hydraulic kW, compressed air | drive kW |
| Automation | PLC/HMI make, casting-speed control, mould-level control | PLC/HMI, drop-speed & water ramping recipes | VFD, interlocks |
| Scope boundaries | supply / fabrication / bought-outs / erection / commissioning / civil & structural exclusions | same | same |

(Template is generic domain background, informed by competitor published specs — e.g. Megatherm CCM: radius 4/7 & 6/11, 1–3 strands, 100–200 mm sq, 2.5–3.5 m/min, Siemens PLC [MEG]; Mexxiss refurbished Concast CCM: 2-strand, 110/130 mm sq, 250 TPD, 12–15 t furnaces [MEX].)

## 5. IndiaMART pages that do NOT exist / redirect (checked)
- `/testimonial.html`, `/photo-gallery.html`, `/factsheet.html` → 404 (both accounts)
- `/profile.html` → 301 to `/aboutus.html`; `/sitenavigation.html` and m-site `/enquiry.html` → 301 to home
- `/products-and-services.html` (desktop) → 301 to `/products.html` (listing 1) or `/services.html` (listing 2)
- Brochure, gallery, corporate video fields are **empty** in the page data; ratings block empty (no reviews)
- Only "Company Album" image (listing 1): https://4.imimg.com/data4/WF/SN/NSDMERP-2619862/1484580330board-1000x1000.png — a near-blank photograph of a wall (uploaded Jan 2017). Logo (listing 2): https://3.imimg.com/data3/KC/ML/ETO-3469833/data2-bi-xb-eto-3469833-images-logo-120x120.png ("Mscast Engineering Pvt Ltd", blue/white "M" mark). [IM7] [IP1]

---
### Source keys used in this file
| Key | URL |
|---|---|
| IM1 | https://m.indiamart.com/mscast-engineering/ |
| IM3 | https://m.indiamart.com/mscast-engineering/products-and-services.html |
| IM4 | https://m.indiamart.com/mscast-engineering/continuous-casting-machine.html |
| IM5 | https://m.indiamart.com/mscast-engineering/other-products.html |
| IM7 | https://www.indiamart.com/mscast-engineering/ , /products.html , /aboutus.html , /continuous-casting-machine.html , /other-products.html |
| IP1 | https://m.indiamart.com/mscast-engineering-pvt-ltd/ |
| IP3 | https://m.indiamart.com/mscast-engineering-pvt-ltd/products-and-services.html |
| IP4 | https://m.indiamart.com/mscast-engineering-pvt-ltd/machinery-services.html |
| IP5 | https://m.indiamart.com/mscast-engineering-pvt-ltd/other-services.html |
| IP7 | https://www.indiamart.com/mscast-engineering-pvt-ltd/ , /services.html , /machinery-services.html , /other-services.html |
| IMD | https://m.indiamart.com/city/pune/continuous-casting-machines.html |
| TI2 | https://www.tradeindia.com/mscast-engineering-pvt-ltd-3965535/product-services.html |
| C2I | https://connect2india.com/Mscast-Engineering-Private-Limited/1901303/products (page body empty to crawler; title from search) |
| MEG | https://megatherm.com/product/continuous-casting-machine/ |
| MEX | https://m.indiamart.com/proddetail/concast-india-fully-refurbished-4-7-6-11-ccm-billet-casters-22066768088.html |
