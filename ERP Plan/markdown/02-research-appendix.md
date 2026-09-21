# MSCAST ERP: Research Appendix

**Version:** 2.0 · **Date:** 21 September 2026 · research data as of 16 Sep 2026 · companion to doc 01 (*Options Assessment & Phased Build Plan*).

- **Method:** release tags, dates, licences and module lists read from the Git repositories (`git ls-remote` / shallow fetch). Star counts from GitHub pages, approximate.
- *(unverified)* or *(sec)* (secondary source): re-check before any commitment.
- **Status:** research input to the platform choice (ERPNext v16). The POC as built uses a local model router, not Gemini on Vertex AI (see doc 01, "Current state"); section D is the option research as done.

---

## A. Full open-source ERP suites

| Project | Stars | Latest release (date) | Licence | Stack |
|----------------------|---------------|----------------------|---------------------|--------------------|
| **frappe/erpnext** | ~38.6k | v16.35.0 (15 Sep 2026); v15.121.3 maintained | GPL-3 (Frappe framework MIT) | Python, JS, MariaDB 11.8, Redis; v16 needs Python 3.14, Node 24 |
| **odoo/odoo** (Community) | ~52.8k | 19.0 branch, commit 15 Sep 2026 | LGPL-3 (Enterprise is proprietary) | Python, JS, PostgreSQL |
| OCA/l10n-india | 1 | Branches 12.0–19.0, **contain no modules** | AGPL-3 | Odoo add-ons |
| Dolibarr | ~7.4k | 24.0.1 (6 Sep 2026) | GPL-3 | PHP |
| iDempiere | ~661 | release-13 branch (10 Sep 2026) | GPL-2 | Java 17, OSGi, PostgreSQL |
| Apache OFBiz | ~1.1k | release24.09.07 (5 Jun 2026) | Apache-2 | Java 17, Groovy |
| Tryton | ~220 (mirror) | 8.0.8 (15 Aug 2026) | GPL-3+ | Python, PostgreSQL |
| Axelor Open Suite | ~970 | v9.1.7 (3 Sep 2026) | AGPL-3 | Java 21, PostgreSQL 16 |
| metasfresh | ~2.4k | commit 15 Sep 2026 | GPL-2 | Java/Spring, React |
| AureusERP | ~11.9k | v1.6.0 (27 Aug 2026) | MIT | PHP 8.3, Laravel 13 |
| Carbon (crbnos) | ~2.4k | No tags; commit 15 Sep 2026 | AGPL-3 + clause restricting internal production use unless modifications are open-sourced; `packages/ee` commercial | TypeScript, Supabase, Redis, Rust |
| qcadoo MES | – | 3.1.20 (11 Sep 2026) | AGPL | Java |
| frePPLe | ~740 | 9.18.1 (30 Aug 2026) | MIT (community) | Planning add-on only |
| Stale / avoid | – | Flectra (last tag 2021), Openbravo CE (ended 2020), ADempiere (last tag Dec 2023), xTuple PostBooks (discontinued, unverified) | – | – |

### Fit for MSCAST

| | India GST / e-invoice / e-way bill / TDS | Indian payroll | ETO / project manufacturing | Drawing revision control | Google Workspace |
|--------------|---------------------|-----------------|-----------------|--------------|-----------------|
| **ERPNext v16** | **Yes**, via India Compliance (GSTR-1, IMS, 2A/2B reconciliation, e-invoice / e-way bill via NIC; paid API credits) | **Yes:** Frappe HR + frappe/india-payroll (EPF ECR, ESI, PT, LWF, 24Q, Form 16; young) | Good: Projects, BOM Creator, subcontracting, QI, scorecard | Not built in → custom | Google login, Calendar, Contacts, Drive picker built in; Drive backup via offsite_backups (v16) |
| Odoo 19 CE | GST, e-invoice, e-way bill modules free but use paid IAP credits; **GSTR filing is Enterprise-only** | Enterprise-only | MRP/Projects in CE; PLM, Quality, work orders Enterprise | Enterprise PLM or OdooPLM | Google login, Gmail, Calendar in CE |
| Axelor | None | None | Good | None found | OIDC |
| iDempiere | Third-party only | None | Medium | None | OIDC |
| Dolibarr | Old GST slabs; e-invoice module in development | None | Weak | Folders only | OAuth |
| Tryton / metasfresh / OFBiz / AureusERP / Carbon | None | None | Medium–weak | None | Varies |

**Odoo modules absent from Community 19.0 source:** `account_accountant`, `account_reports`, `hr_payroll`, `l10n_in_hr_payroll`, `l10n_in_reports`, `mrp_plm`, `quality`, `quality_control`, `documents`, `web_studio`, `mrp_workorder`.

**Implementer ecosystem:** Frappe partners: 73 in India, incl. Indictrans (Pune, Gold) and Hybrowlabs (Pune office). Odoo partners: 173 in India, e.g. Pragmatic Techsoft (Pune).

---

## B. Frappe ecosystem: coverage of MSCAST needs

### Base and India apps

| Need | App | Latest | v15/v16 | Licence | Coverage |
|-------------------|----------------------|---------------|--------------|--------------|-----------------|
| GST, e-invoice, e-way bill, GSTR, audit trail, job-work challans | resilient-tech/india-compliance | v16.9.0 / v15.31.4 (1 Sep 2026) | Both | GPL-3 | Full (paid API credits) |
| TDS | ERPNext Tax Withholding Category | core | Both | – | Full |
| HR, leave, attendance, expenses, payroll engine | frappe/hrms | v16.18.1 (9 Sep 2026) | Both | GPL-3 | Partial for Indian statutory payroll |
| Indian statutory payroll | frappe/india-payroll | v16.0.4 (8 Sep 2026) | **v16 only** | GPL-3 | Full but young |
| Documents | frappe/drive | v0.3.0 (Oct 2025), beta | v15–16 | AGPL-3 | Partial |
| Reporting | frappe/insights | v3.13.2 (5 Sep 2026) | v15+ | AGPL-3 | Full |
| CRM | frappe/crm | v1.84.0 (15 Sep 2026) | Both | AGPL-3 | Full (optional) |
| Helpdesk | frappe/helpdesk | v1.30.1 | Both | AGPL-3 | Optional |
| Chat | Raven | v2.8.11 | v15–16 | AGPL-3 | Optional |
| WhatsApp | shridarpatil/frappe_whatsapp | v1.0.11; master Aug 2026 | v14–16 | MIT | Full (Meta Cloud API, charged per message) |
| Backups | frappe/offsite_backups | v16 branch (Aug 2026) | v16 | MIT | Full (Drive, Dropbox, S3) |

**Google Workspace:** built in: Sign in with Google (Social Login Key), Calendar and Contacts sync, Drive file picker in attachments; Gmail works as an ERPNext email account. Drive backups: built in on v15; v16 needs the offsite_backups app.

**MSCAST-specific scope** (coverage and remaining effort per need, where Python code is needed): doc 01, §3.

---

## C. Alternative strategies beyond Frappe

### C1. Odoo Community 19 + OCA

- **India localisation in Community:** `l10n_in`, `l10n_in_edi`, `l10n_in_ewaybill`, `l10n_in_ewaybill_irn`, `l10n_in_ewaybill_stock`, `l10n_in_purchase_stock`, `l10n_in_sale_stock`; e-invoice and e-way bill use paid in-app-purchase (IAP) credits. **Not included:** GSTR reports, Indian payroll.
- **OCA modules on 19.0 filling Enterprise gaps** (many Beta): accounting `account_financial_report`, `mis_builder`, `account_asset_management`, `account_reconcile_oca`, `account_budget_oca`; documents/quality `dms`, `quality_control_oca`; purchasing `purchase_request`; manufacturing `mrp_multi_level`; projects `project_timeline`; quality management `mgmtsystem_*`; PLM: OdooPLM (third-party, 19.0 branch updated Sep 2026).
- **Enterprise pricing (sec):** Standard ≈ ₹725/user/month; Custom (Studio/API/on-premise) ≈ ₹1,150/user/month. Official: $31.10 and $61/user/month.
- **3-year cost:** Community ₹6–13 L cash; Enterprise ₹8–15 L at 10 users.
- **Risks:** a new major version every year, OCA modules lag behind; GST returns and payroll stay outside the system.

### C2. Best-of-breed open-source stack + Tally

| Role | Component (release, licence) |
|----------------------------------|------------------------------------------------------------------|
| Parts / BOM / purchasing / stock | InvenTree 1.5.4 (9 Sep 2026, MIT) |
| CRM | Twenty v2.40.2 (AGPL) · EspoCRM 10.0.8 (AGPL) |
| Projects / time / cost | OpenProject 17.8.0 (GPL-3; SSO paid) · Kimai 2.67.0 |
| Drawings / documents | Mayan EDMS 4.12.1 (GPL-2, versioning + workflows) |
| Accounting | TallyPrime: Silver ₹22,500 lifetime or ₹8,100/yr; Gold ₹67,500 or ₹24,300/yr (+GST). XML/JSON/ODBC integration. Akaunting is unsuitable (BSL licence, 2-user limit) |
| Assets | Snipe-IT v8.7.2 (AGPL) |
| HR / payroll | Horilla 2.1.7 (LGPL, Indian) · Zoho Payroll (free up to 10 employees per official page, re-check) |

**Assessment:** effort 14–22 weeks · 3-year cost ₹2.5–4 L cash, ₹11–20 L with developer time · hosting ~8 vCPU, 16–24 GB RAM · weaknesses: no single project P&L, 6 separate upgrade paths, reconciliation errors between systems.

### C3. Low-code / AppSheet + Tally

- **Tools checked:** NocoDB 2026.09.0 (Sustainable Use License since Jan 2026); Baserow 2.3.4 (MIT core); Appsmith v2.4 (Apache-2); Budibase v3.45; ToolJet 3.20 (AGPL); Directus v12.3.1 (source-available); Google AppSheet Core (included in Workspace Business Starter, Standard, Plus).
- **Good for:** trackers (drawing register, inspections, retention follow-up). **Not for:** accounting, stock valuation, the legally required audit trail.
- **3-year cost:** ₹1–3 L cash.

### C4. Custom build (Next.js + Postgres) and Carbon

- **Custom build:** 26–52 weeks for the operational layer alone; GST and e-invoice need a GST Suvidha Provider API (ClearTax, Masters India, IRIS, Sandbox, WhiteBooks); payroll bought in. Risks: key-person dependency, audit-trail compliance.
- **Carbon:** strong on MES, QMS, BOM. Blockers: no GST, licence restriction on internal production use, complex self-hosting. Cloud plans $40–100/user/month.

### C5. Commercial SaaS benchmarks (India, excl. GST)

- **Zoho One:** all-employee plan ₹1,500/employee/month, ≈₹1.8 L/yr for 10 staff (sec); separate apps: Books Premium ₹2,999/month (official); weak ETO fit.
- **SAP Business One:** licences ₹67k–1.6 L per user + implementation ₹3–5 L (sec); 3-year ≈ ₹20–25 L.
- **Marg ERP:** built for pharma and distribution, not ETO.

---

## D. Gemini automation research

### D1. Frappe/ERPNext AI apps on GitHub

| App | Stars | Latest | Licence | v15/v16 | Gemini | Function |
|-----------------|--------|---------------|-----------------|----------|-----------------|-----------------|
| buildswithpaul/Frappe_Assistant_Core | ~284 | v2.5.0 (Jun 2026); v3 beta Sep 2026 | AGPL-3 | Both | Via MCP clients; v3 chat multi-provider (needs FAC Cloud registration) | MCP server: 24 tools, OAuth, role-aware, audit log, OCR |
| frappe/mcp | ~165 | Experimental | MIT | Needs OAuth2 update | Any MCP client | Library to build MCP tools |
| ERPGulf/changAI | ~74 | Early | MIT | Both | **Yes (primary)** | Plain-English questions → SQL/ORM queries |
| wphamman/erpocr_integration | 2 | – | GPL-3 | v15+ | **Yes** (2.5 Flash) | Invoice/delivery note → draft PI/PR/PO with review statuses |
| kainotomo/invoice2erpnext | ~35 | v16.0.4 | unverified | Both | No (vendor server) | PDF → PI (sends data to a third party) |
| erpnextai/next_ai | ~31 | Aug 2026 | **Non-commercial** | v14–15 | Yes | Text helpers: **not usable** |

ERPNext v16 has no official AI engine. The AI projects Frappe showed at Frappeverse 2026 were demos only.

### D2. Gemini platform facts (verify at build time)

- **Models:** stable: Gemini 3.8/3.7/3.6/3.5 Flash, 3.5 Flash-Lite, 2.5 Flash/Pro; 3.1 Pro in preview. Vertex AI is renamed **Gemini Enterprise Agent Platform**.
- **Paid API, per 1M tokens (input / output):** 3.5 Flash $1.50 / $9.00; 2.5 Flash $0.30 / $2.50; 3.8 Flash $0.75 / $3.75, doubling on 1 Jan 2027. Regional (non-global) Vertex endpoints ≈10% more; batch 50% less.
- **Data handling:** free tier may use content for training and human review: **never send ERP data to the free tier.** Paid tier does not train on your data; zero data retention available. **India data residency (asia-south1, Mumbai)** covers only Gemini 3.5 Flash, 2.5 Flash and text-embedding-005.
- **Workspace options:** Workspace Studio (formerly Flows, GA March 2026): no-code Gemini agents across Gmail, Chat, Drive, Sheets; usage limits enforced from 1 Oct 2026. Apps Script + Vertex AI: an advanced service. AppSheet + Gemini: needs Enterprise Plus.

### D3. Workflow orchestration tools

| | n8n | Activepieces | Node-RED |
|-----------------------|--------------------------|----------------------------|-----------------------|
| Licence | Sustainable Use License: internal business use OK, not OSI | MIT (community) | Apache-2 |
| ERPNext connector | Built-in node | HTTP | HTTP |
| Gemini connector | Built-in Gemini + Vertex nodes | Gemini piece | Community node / HTTP |

**Frappe side:** webhooks with HMAC-SHA256 signature; REST API at `/api/resource/{doctype}` with token or OAuth; a create-only integration user so the AI can never submit documents.

### D4. Use cases, controls and cost
- **Flows A1–A7, design rules and cost estimate:** doc 01, §7.
- **Controls in addition to doc 01 §7:** match extracted values against master data only; confidence thresholds; test on about 50 historical documents per flow; treat email and PDF content as untrusted (prompt injection).
- **DPDP Act:** DPDP Rules notified 14 Nov 2025; main obligations apply from about May 2027. A proposal to shorten this is not notified; confirm with counsel.

---

## E. Consolidated sources
- **ERPNext / Frappe:**
  - Repos: https://github.com/frappe/erpnext · https://github.com/frappe/frappe · https://github.com/frappe/hrms · https://github.com/frappe/india-payroll · https://github.com/frappe/offsite_backups · https://github.com/frappe/drive · https://github.com/frappe/insights · https://github.com/frappe/crm · https://github.com/frappe/helpdesk · https://github.com/frappe/raven · https://github.com/frappe/mcp
  - India Compliance: https://github.com/resilient-tech/india-compliance · https://docs.indiacompliance.app/docs/getting-started/india_compliance_account
  - Docs: https://docs.frappe.io/framework/user/en/installation · https://github.com/frappe/frappe/wiki/Migrating-to-version-16 · https://docs.frappe.io/framework/user/en/guides/integration/social_login_key · https://docs.frappe.io/framework/user/en/guides/integration/webhooks · https://docs.frappe.io/framework/user/en/api/rest
  - Forum: https://discuss.frappe.io/t/retention-money/127161 · https://discuss.frappe.io/t/item-revisioning/162669 · https://discuss.frappe.io/t/e-invoice-with-india-compliance-pricing/145343 · https://discuss.frappe.io/t/hardware-requirements-for-frappe-erpnext-setup/134991
  - Partners and hosting: https://frappe.io/partners/regions · https://frappe.io/cloud/sites
  - Community apps: https://github.com/gavindsouza/awesome-frappe · https://github.com/shridarpatil/frappe_whatsapp
- **Odoo:** https://github.com/odoo/odoo · https://github.com/OCA/l10n-india · https://github.com/OCA/payroll · https://github.com/OCA/manufacture · https://github.com/OCA/dms · https://github.com/OmniaGit/odooplm · https://www.odoo.com/page/editions · https://www.odoo.com/pricing · https://www.odoo.com/documentation/19.0/applications/finance/fiscal_localizations/india.html · https://www.odoo.com/documentation/19.0/administration/on_premise/deploy.html · https://oec.sh/odoo-pricing/india
- **Other ERPs:** https://github.com/Dolibarr/dolibarr · https://github.com/idempiere/idempiere · https://github.com/apache/ofbiz-framework · https://github.com/tryton/tryton · https://github.com/axelor/axelor-open-suite · https://github.com/metasfresh/metasfresh · https://github.com/aureuserp/aureuserp · https://github.com/crbnos/carbon · https://github.com/qcadoo/mes · https://github.com/frePPLe/frepple
- **Composable stack and low-code:** https://github.com/inventree/InvenTree · https://github.com/twentyhq/twenty · https://github.com/opf/openproject · https://gitlab.com/mayan-edms/mayan-edms · https://github.com/nocodb/nocodb · https://github.com/appsmithorg/appsmith · https://github.com/ToolJet/ToolJet · https://support.google.com/appsheet/answer/10105400
- **Commercial SaaS and Indian compliance:** https://tallysolutions.com/buy-tally/ · https://help.tallysolutions.com/integration-methods-and-technologies/ · https://www.zoho.com/in/books/pricing/ · https://www.zoho.com/in/payroll/pricing · https://www.cogniscient.in/sap-business-one-price-in-india-a-detailed-breakdown-of-sap-b1-cost-2026/ · https://www.india-briefing.com/news/india-mandates-audit-trail-compliance-for-all-companies-explainer-key-obligations-34837.html/ · https://www.gimbooks.com/blog/5-crore-e-invoice-turnover-rule-2026/
- **Hosting:** https://www.digitalocean.com/pricing/droplets · https://docs.frappe.io/cloud/sites/backups
- **MSCAST public profile:** https://www.indiamart.com/mscast-engineering/ · https://www.zaubacorp.com/company/Mscast-Engineering-Private-Limited/U74900PN2010PTC137644
- **Indian company law and accounting:** Companies (Accounts) Rules audit trail and India backups: https://www.scconline.com/blog/post/2022/08/16/record-keeping-requirements-modified-vide-companies-accounts-fourth-amendment-rules-2022/ · ICAI audit trail guidance: https://cajournal.icai.org/article-details/audit-trail-requirements-responsibilities · Ind AS applicability (Rule 4): https://ca2013.com/rule-4-companies-indian-accounting-standards-rules-2015/ · Companies (AS) Rules 2021 / SMC: https://taxguru.in/company-law/companies-accounting-standard-rules-2021.html · Small company threshold (Dec 2025): https://www.scconline.com/blog/post/2025/12/02/mca-notified-expansion-threshold-limit-small-companies-2025-compliance-update-scctimes/ · MSME Form I: https://mmjc.in/change-in-form-msme-1-exhaustive-disclosure-framework/
- **Messaging and attendance:** SMS DLT templates: https://msg91.com/help/dlt-registration-in-india/dlt-content-template-faqs · Biometric integration: https://docs.frappe.io/hr/integrating-frappe-hr-with-biometric-attendance-devices
- **Gemini and automation:** https://ai.google.dev/gemini-api/docs/models · https://ai.google.dev/gemini-api/docs/pricing · https://ai.google.dev/gemini-api/docs/zdr · https://docs.cloud.google.com/gemini-enterprise-agent-platform/resources/data-residency · https://workspace.google.com/studio/ · https://developers.google.com/apps-script/advanced/vertex-ai · https://github.com/n8n-io/n8n/blob/master/LICENSE.md · https://docs.n8n.io/integrations/builtin/app-nodes/n8n-nodes-base.erpnext/ · https://github.com/buildswithpaul/Frappe_Assistant_Core · https://github.com/ERPGulf/changAI · https://github.com/wphamman/erpocr_integration · https://www.amsshardul.com/insight/enforcement-of-the-dpdp-act-and-notification-of-the-dpdp-rules/
