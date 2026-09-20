# Sources — every URL visited (all accessed 2026-09-16)

Method notes: IndiaMART desktop URLs 302-redirect to m.indiamart.com; pages were fetched with WebFetch and with curl (browser User-Agent, via the agent proxy). IndiaMART pages embed the full seller record as JSON (`window.__COMPANY_HYDRATION__`), which was parsed for exact values (saved in `raw/indiamart-data_*.json`). Sites that WebFetch reported as robots-disallowed (LinkedIn, ExportersIndia search, TheCompanyCheck) were **not** fetched by other means; only search-result titles were used.

Legend — Result: ✅ read · ⚠️ partial/empty · ❌ blocked/error · ↪ redirect · 404 not found

## 1. IndiaMART — listing 1 `mscast-engineering` (products)
| Key | URL | Result | Contributed |
|---|---|---|---|
| IM1 | https://m.indiamart.com/mscast-engineering/ (desktop https://www.indiamart.com/mscast-engineering/ ↪) | ✅ | Name, GSTIN, verified flags, member 15 yrs, contact person Sameer Lokhande (Manager), PNS phone, 5 products & IDs, 2 categories, HSN codes, about text |
| IM2 | https://m.indiamart.com/mscast-engineering/aboutus.html | ✅ | Factsheet: CEO M Chandankeri, employees ≤10, est. 2010, turnover ₹1–2 Cr, GST turnover 1.5–5 Cr, GST NOB, IEC, CIN, legal status |
| IM3 | https://m.indiamart.com/mscast-engineering/products-and-services.html | ✅ | Category index |
| IM4 | https://m.indiamart.com/mscast-engineering/continuous-casting-machine.html | ✅ | Category "Continuous Casting Machine" → Aluminum Billet Casting Machine (no specs) |
| IM5 | https://m.indiamart.com/mscast-engineering/other-products.html | ✅ | Category "Other Products" → 4 items (no specs) |
| IM6 | https://m.indiamart.com/mscast-engineering/registration-directors-info.html | ✅ | CIN, directors "Current: 2" (Mustaque Ahmed N. Chandankeri, Zameer Alam Chandankeri, appointed 29-10-2010) |
| IM7 | https://www.indiamart.com/mscast-engineering/ ; /aboutus.html ; /continuous-casting-machine.html ; /other-products.html ; /products.html ; /products-and-services.html (↪ products.html) ; /enquiry.html ; /registration-directors-info.html | ✅ | Desktop category blurbs, "Company Album" image, quality statement, enquiry form |
| — | https://m.indiamart.com/mscast-engineering/profile.html | ↪ aboutus.html | — |
| — | https://m.indiamart.com/mscast-engineering/sitenavigation.html ; /enquiry.html (m) | ↪ home | — |
| — | https://m.indiamart.com/mscast-engineering/testimonial.html ; /photo-gallery.html ; /factsheet.html ; https://www.indiamart.com/mscast-engineering/testimonial.html ; /photo-gallery.html | 404 | Confirms no testimonials/gallery pages |
| — | https://m.indiamart.com/proddetail/aluminum-billet-casting-machine-25600096312.html ; …continuous-casting-machines-5687550373 ; …conveyors-5687550455 ; …pouring-casting-machine-25600096433 ; …continuous-casting-equipments-5687550291 | 404 | Confirms no product-detail pages |
| — | https://4.imimg.com/data4/WF/SN/NSDMERP-2619862/1484580330board-500x500.png | ✅ | Only company photo (near-blank wall), uploaded Jan 2017 |

## 2. IndiaMART — listing 2 `mscast-engineering-pvt-ltd` (services)
| Key | URL | Result | Contributed |
|---|---|---|---|
| IP1 | https://m.indiamart.com/mscast-engineering-pvt-ltd/ | ✅ | Name variant, contact "Chandekeri M C" (Manager), PNS phone, 5 services, logo, category "CAD CAM Design & Consultancy" |
| IP2 | https://m.indiamart.com/mscast-engineering-pvt-ltd/aboutus.html (+ desktop) | ✅ | Vision/mission, factsheet ("Exporter and Service Provider") |
| IP3 | https://m.indiamart.com/mscast-engineering-pvt-ltd/products-and-services.html | ✅ | Category index |
| IP4 | https://m.indiamart.com/mscast-engineering-pvt-ltd/machinery-services.html (+ desktop) | ✅ | P&I diagrams service |
| IP5 | https://m.indiamart.com/mscast-engineering-pvt-ltd/other-services.html (+ desktop) | ✅ | Layout drawings, CCM layout, erection supervision, hydraulic circuits |
| IP6 | https://m.indiamart.com/mscast-engineering-pvt-ltd/registration-directors-info.html | ✅ | Same director block as IM6 |
| IP7 | https://www.indiamart.com/mscast-engineering-pvt-ltd/ ; /services.html ; /products-and-services.html (↪ services.html) ; /enquiry.html ; /profile.html (↪ aboutus) | ✅ | Desktop blurbs |
| — | https://m.indiamart.com/mscast-engineering-pvt-ltd/testimonial.html ; /factsheet.html | 404 | — |
| — | https://m.indiamart.com/mscast-engineering-pvt-ltd/sitenavigation.html ; /enquiry.html ; /profile.html | ↪ | — |
| — | https://m.indiamart.com/proddetail/ccm-erection-supervision-services-2939522730.html and 4 other guessed service PDP URLs | 404 | — |
| — | https://3.imimg.com/data3/KC/ML/ETO-3469833/data2-bi-xb-eto-3469833-images-logo-120x120.png | ✅ | Company logo |

## 3. Other company-specific sources
| Key | URL | Result | Contributed |
|---|---|---|---|
| TI1 | https://www.tradeindia.com/mscast-engineering-pvt-ltd-3965535/ | ✅ | "Service Provider", registered 2011, Head Design Mr. Mustaque Ahmed Chandankeri, Manager Sameer Lokhande, address Prithvi Park NIBM Road Kondhwa |
| TI2 | https://www.tradeindia.com/mscast-engineering-pvt-ltd-3965535/product-services.html | ✅ | 2 items: Designing of casting machines; metel handling |
| ZC1 | https://www.zaubacorp.com/MSCAST-ENGINEERING-PRIVATE-LIMITED-U74900PN2010PTC137644 and https://www.zaubacorp.com/company/Mscast-Engineering-Private-Limited/U74900PN2010PTC137644 | ✅ (WebFetch) | Status, incorporation, capital, AGM 2023/BS 2023, registered office, 3 directors, past alternate director, HDFC ₹2.5 Cr charge, Whipsteels India directorship |
| IF1 | https://www.instafinancials.com/company/mscast-engineering-private-limited-U74900PN2010PTC137644 | ✅ | NIC 74900, AGM 30-09-2025, BS 31-03-2025, e-mail accounts@mcast.co.in |
| FE1 | https://www.falconebiz.com/company/MSCAST-ENGINEERING-PRIVATE-LIMITED-U74900PN2010PTC137644 | ✅ (curl) | Data as of 12-05-2026: 2 directors (Mustaque, Aiqaz), AGM 2025, FY25 growth metrics/ratios, GST reg 01-07-2017 & NOB, 1 active charge |
| CV1 | https://www.companyvakil.com/companysearch/MSCAST-ENGINEERING-PRIVATE-LIMITED/U74900PN2010PTC137644 | ⚠️ (HTTP 500 but content returned) | Stale AGM/BS 2017; old e-mail sec@vrushaliassociates.com |
| IB1 | https://www.insiderbiz.in/company-map/MSCAST-ENGINEERING-PRIVATE-LIMITED | ✅ | Registered office & e-mail (as on 14-Jan-2023) |
| TF1 | https://www.tofler.in/mscast-engineering-private-limited/company/U74900PN2010PTC137644 | ❌ 403 | — (no financial figures obtained) |
| TCC | https://www.thecompanycheck.com/org/mscast-engineering-private-limited/2c5334e133 | ❌ robots fetch failed / 522 | — |
| CT1 | https://cleartax.in/f/company/mscast-engineering-private-limited/U74900PN2010PTC137644 | ❌ 410 | — |
| C2I | https://connect2india.com/Mscast-Engineering-Private-Limited/1901303/products ; https://connect2india.com/MSCAST-ENGINEERING-PRIVATE-LIMITED/1901303 | ⚠️ empty body | Title only: "Continuous Casting Equipments, Conveyors, Continuous Casting Machines" |
| CI | https://www.clickedindia.net/0u115u9v37/mscast-engineering-pvt-ltd-pune.html ; …/contact.html | ❌ 403 (Cloudflare) | Title only: "Processing Services In Nibm Pune" |
| III | https://pune.infoisinfo.co.in/card/mscast_engineering_pvt_ltd/3222281 | ⚠️ empty | Existence only |
| WEB1 | https://mscastengineering.com/ (www.mscastengineering.com ↪) | ✅ | GoDaddy placeholder, tagline, © 2025 |
| — | https://mcast.co.in , https://www.mcast.co.in , https://mscast.co.in , https://www.mscast.co.in , https://mscast.in , https://www.mscast.com | ❌ connection rejected by egress proxy | Domain status unknown |
| LI1 | https://in.linkedin.com/company/mscast-engineering-private-limited | ❌ robots (not fetched) | Existence via search |
| LI2 | https://in.linkedin.com/company/mscast-engineering-pvt-ltd | not fetched | Existence via search (title "MScast Engineering Pvt. Ltd.") |
| — | https://www.justdial.com/Pune/Mscast-Engineering-Pvt-Ltd | ❌ 403 | No listing confirmed |
| — | https://www.exportersindia.com/search.php?srch_catg_ty=prod&term=mscast | ❌ robots | — |
| — | https://www.zaubacorp.com/company-by-address/CHETAS-HOUSE--PLOT-NO--1-… and …/FL--NO--E4-13--ARMY-WELFARE-… | ✅ | **False positives** from search — MSCAST not at these addresses; ignore |
| ERP1 | Project file "Revised Proposal - ERPENS - Mscast.pdf" (claude.ai Project ERP-MSCAST) | ✅ | ERP scope: ERPNext modules, custom Engineering/Project/Procurement enhancements, timeline 12–14 weeks, ₹3.6 L |

## 4. Industry / competitor sources
| Key | URL | Result | Contributed |
|---|---|---|---|
| IMD | https://m.indiamart.com/city/pune/continuous-casting-machines.html (from https://dir.indiamart.com/pune/continuous-casting-machines.html ↪) | ✅ | Pune CCM supplier list incl. MSCAST |
| IMB | https://m.indiamart.com/impcat/billet-casting-machines.html | ✅ | 27 billet-casting suppliers, prices & specs |
| ELT | https://electrotherment.com/ | ✅ | Electrotherm E&T profile |
| MEG | https://megatherm.com/product/continuous-casting-machine/ | ✅ | Megatherm CCM specs |
| — | https://www.indiamart.com/emt-megatherm-pvt-ltd-kolkata/ | search result | Megatherm location Kolkata |
| EMI | https://www.electramechindia.co.in/continuous-casting-machine.htm | ✅ | Electramech CCM sizes & price range |
| CTE | https://www.concasttechno.com/products.html | ✅ | Concast Techno Engineering products |
| SWG | https://swatiglobal.in/ccm-manufacturer-india/ | ✅ | Swati International profile |
| MEE | https://m.indiamart.com/meeracle-engineering/casting-machines.html | ✅ | Meeracle Engineering prices |
| MEX | https://m.indiamart.com/proddetail/concast-india-fully-refurbished-4-7-6-11-ccm-billet-casters-22066768088.html | ✅ | Refurbished CCM spec & price |
| VF | https://m.indiamart.com/vfast-furnaces-technology/hot-top-casting-machines.html | ✅ | V-fast hot-top casting |
| ALM | https://almectech.com/custom-technology/complete-dc-casting-machine/ | ✅ | Almec Tech DC casting spec |
| LABH | https://m.indiamart.com/proddetail/continuous-casting-machine-ccm-for-bloom-slab-billet-labh-group-2858162521333.html | search result | Labh Group CCM |
| SRI | https://www.srishtechindia.com/ | search result | Srishtech |
| — | https://www.fidusconcastmachine.com/steel-continuous-casting-machines-703782.html | search result | Fidus Concast |
| ALC | https://www.alcircle.com/news/66-and-counting-china-leads-aluminium-extrusions-as-indias-demand-nears-858-000-tonnes-120611 | ✅ | India extrusion demand 2025/2026, capacity, utilisation |
| LOH | https://lohaa.co.in/blog/india-secondary-steel-outlook-2026-to-2030 | ✅ | Secondary steel figures (blog — indicative) |
| ALB | https://alubharat.org/ | ✅ | Aluminium Bharat 2026 dates/venue/scale |
| IFEX | https://foundry-suppliers.com/events/8f8499b6-3e89-4f32-860f-38b9c351768c | ❌ robots | Event existence only |
| ALUC / ISE / BME | https://alucastexpo.com/ ; https://www.indiasteelexpo.in/ ; https://www.steel-technology.com/events/bharat-metal-expo-2026 | search results | Event existence |

### Web searches run (2026-09-16)
"Mscast Engineering" Pune · "MSCAST" continuous casting machine · "U74900PN2010PTC137644" · "Mscast Engineering Private Limited" tofler/zaubacorp/thecompanycheck · mcast.co.in · "Chandankeri" casting Pune · "MS Cast Engineering" OR "M S Cast Engineering" OR "Mscast Engg" · Mscast Engineering LinkedIn … · Mscast Engineering justdial/exportersindia/facebook/youtube · "Mscast" import export data volza/seair/eximpedia · eximpedia "mscast" · "Mscast Engineering" exporter/importer shipment data · "Mscast" steel plant CCM project/tender/erection · "27AAGCM8444B1ZI" · site:youtube.com Mscast Engineering · "Mscast Engineering" youtube/facebook/instagram · "MSCAST" trademark/patent · "Whipsteels India Private Limited" · Mscast revenue tofler/falconebiz · aluminium billet casting machine manufacturer India (×2) · continuous casting machine manufacturers India (×3) · Electrotherm CCM · Megatherm/Inductotherm CCM · India secondary steel market · India aluminium extrusion demand · Aluminium India/ALUMEX/IFEX 2026 · India Steel Expo 2026.
