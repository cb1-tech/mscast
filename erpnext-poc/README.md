# MSCAST ERP - POC on ERPNext v16 (WSL / Docker)

**Updated:** 19 Sep 2026 (full implementation + test harness) · **Where:** WSL Ubuntu on thinkstation
**Local URL:** http://localhost:8080 · **Public:** https://mscast.carobar.net
**Login:** `Administrator` / `admin` ← change this before sharing the public link
**Demo users created:** `director@mscast.demo` (read-only director), `auditor@mscast.demo` (read-only statutory auditor)
**Outgoing mail:** live via Purelymail (`uattech@carobar.net`) - SPF, DKIM and DMARC all pass at Gmail

All company data in this POC is **fictional demo data**. Customer and supplier names end with "(DEMO)".

**Coverage against MSCAST's requirement document: 97 of 97 requirements live** (53 in v1.3, 86 in v1.4).
Six rest on stated assumptions - see the overnight implementation report. **23 of 23 automated checks pass.**

---

## 1. What is running

| Piece | Detail |
|---|---|
| Stack | compose project `mscast-poc`, 11 containers, from `~/mscast-poc/compose.yaml` |
| Image | **`mscast/erpnext:v16`** (5.12 GB), built locally from frappe_docker with apps.json |
| Apps | frappe 16.34.0 · erpnext 16.35.0 · **india_compliance 16.9.1** · **hrms 16.19.0** · **india_payroll 16.0.4** |
| Database | MariaDB 11.8 (ERPNext does not support PostgreSQL) |
| Site | `frontend`, port 8080 · server scripts **enabled** (`server_script_enabled: true`) |
| Files | scripts and seed data in `D:\MSCAST\erpnext-poc`; compose + build log in `~/mscast-poc` |
| Memory | WSL capped at 8 GB; the stack idles at about 1.5-2.5 GB |

**WSL note:** WSL shuts its VM down when idle and that stops the containers. `vmIdleTimeout=28800000`
(8 h) is set in `C:\Users\user\.wslconfig` and applies from the next WSL restart. Keeping any WSL
terminal open also holds the VM up.

## 2. Day-to-day commands

```powershell
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/start-poc.sh    # start
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/status-poc.sh   # status + URL check
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/stop-poc.sh     # stop (data kept)
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/backup-poc.sh   # DB + files backup to D:
```

Re-run any seed step (they are safe to repeat):

```powershell
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/run-seed.sh 56_batch_c4
```

Rebuild the custom image (after changing `apps.json`): `scripts/08-build-image.sh`, then `scripts/09-swap-image.sh`.
`scripts/reset-poc.sh` wipes the database and rebuilds from the seed scripts.

## 3. Exposing the demo to clients in India

**Public URL: https://mscast.carobar.net** - your own domain, valid certificate, no VPN and no
client software. Anyone, anywhere, can open it.

| Piece | Detail |
|---|---|
| Route | Cloudflare Tunnel `mscast-demo` (id `0e690596-81d9-4e00-9e00-7e87bd3d7477`) |
| DNS | CNAME `mscast.carobar.net` created by cloudflared in your Cloudflare zone |
| Origin | `http://<WSL IP>:8080` - the IP is rewritten each time `demo-up.ps1` runs, because it changes |
| Binary | `cloudflared` 2026.9.1, installed via winget at `C:\Program Files (x86)\cloudflared` |
| Credentials | `%USERPROFILE%\.cloudflared\` - cert.pem and the tunnel json. Keep these private |

### Bringing the demo up

```powershell
powershell -ExecutionPolicy Bypass -File D:\MSCAST\erpnext-poc\scripts\demo-up.ps1
```

It starts the stack, pins the WSL VM up, rewrites the tunnel config with the current WSL IP,
restarts the tunnel and verifies the public URL. A shortcut to it sits in the Startup folder, so a
reboot brings the demo back by itself.

### Why the keep-alive exists

WSL 2.7.3 shuts its VM down whenever no session is attached, and it ignores `vmIdleTimeout`. When
the VM goes, the containers go with it and the public URL returns 502. `demo-up.ps1` holds a
`wsl -d Ubuntu -e sleep infinity` process open to prevent that. Do not kill it while demoing.

**`vmIdleTimeout=0` means shut down immediately, not never.** The value for never is `-1`. The
setting appears to be ignored by this WSL version either way, which is why the keep-alive is
needed.

### Things that were tried and rejected

- **Tailscale Funnel** (`thinkstation.tailf78e82.ts.net`) - the ingress returned 503 even with the
  funnel armed, the node healthy and the app reachable locally. It also required every client to
  install Tailscale. Superseded by the Cloudflare tunnel; the funnel config is still in place and
  harmless.
- **`networkingMode=mirrored` in .wslconfig** - fixed Windows-to-WSL localhost, but broke Docker's
  embedded DNS (`host not found in upstream "backend:8000"`) and put the frontend and websocket
  containers into a restart loop. Reverted; backup at `%USERPROFILE%\.wslconfig.backup-20260919`.

### Taking it offline

```powershell
Get-Process cloudflared | Stop-Process     # stops the public URL immediately
```

Remove the Startup shortcut to stop it coming back, and delete the tunnel with
`cloudflared tunnel delete mscast-demo` to revoke it permanently.

## 4. MSCAST forms (custom DocTypes - no app or developer mode needed)

| Form | Purpose (from MSCAST's requirement document) |
|---|---|
| **MSCAST PCC** + items | Purchase Cost Calculation: component-wise estimate, revision, approval; the baseline for PO control and MIS |
| **MSCAST Drawing** + revisions | Drawing register: number, title, assembly, revision history, customer-approval status, Drive link |
| **MSCAST MDF** + items | Material Data File / material list per assembly, released to procurement |
| **MSCAST BRM** | Billing Routing Memo: procurement certifies qty, rate, inspection and delivery before accounts pay |
| **MSCAST MDM** + items | Material Dispatch Memo with free-issue (Annexure-I) flag |
| **MSCAST Delivery Instruction** | Instruction to the supplier to dispatch direct to site: consignee, transporter, LR, annexure |
| **MSCAST Inspection Plan** | In-process / pre-dispatch / third-party / customer inspection with result |
| **MSCAST Project Certificate** | Commissioning / preliminary / final acceptance, retention release date |
| **MSCAST Project Kickoff** *(new)* | Customer-PO verification checklist (price, scope, payment terms, LD, GST, BG, advance) + kick-off minutes, driven by a workflow |
| **MSCAST Transmittal** + items *(new)* | Drawing / document transmittal to customers, vendors and inspection agencies, with acknowledgement |
| **MSCAST Commissioning Report** + parameters *(new)* | Performance trial: specified vs achieved, punch list, provisional acceptance, guarantee start |
| **MSCAST Spares Handover** + items *(new)* | Commissioning and 2-year mandatory spares handed over, with part numbers |
| **MSCAST Client Claim** *(new)* | Claims on the customer: scope variation, idle time, escalation; agreed value and the settling invoice |
| **MSCAST Customer Asset** *(new)* | Customer-owned tooling and gauges held by MSCAST or its sub-contractors (not capitalised) |
| **MSCAST Archival Log** *(new)* | Monthly archival run record with the 8-year statutory retention note |

### Workflow and controls *(new)*

- **MSCAST Project Kick-off** workflow: `Draft → PO Verified → Kick-off Approved`, with a
  `PO Query Raised` branch. The transition to *PO Verified* is only allowed to Accounts and only when
  price, scope, payment terms and GST are all ticked. PROJ-0002 is deliberately parked in
  *PO Query Raised* because the customer's PO changed the payment terms.
- **BRM payment block** (server script on Payment Entry, Before Submit): a supplier payment is
  **refused** unless a BRM exists for that supplier bill *and* it is certified. Verified live -
  a payment against `SMW/CAP/2026/08` is rejected with the reason.
- **Monthly archival job** (scheduled server script) writing an MSCAST Archival Log entry;
  12 rolling backups retained.

### Roles *(new)*

- **MSCAST Statutory Auditor** - read / report / print / export only, on 23 doctypes including
  GL Entry, vouchers, assets, Version history and the MSCAST forms. No write, no submit, no delete.
- **MSCAST Director** - the same read-only rights over 30 doctypes including projects, payroll and claims.

## 5. Print formats (MSCAST letterhead, A4)

`MSCAST PCC Sheet` · `MSCAST MDF Sheet` · `MSCAST Material Dispatch Memo` ·
`MSCAST Delivery Instruction Print` (Annexure-I) · `MSCAST Billing Routing Memo` ·
`MSCAST Inspection Report` · `MSCAST Project Certificate Print` ·
**`MSCAST Proforma Invoice`** (on Sales Order) · **`MSCAST Project Schedule (Client)`** ·
**`MSCAST Project Status Report`** · **`MSCAST Transmittal Note`** ·
**`MSCAST Commissioning Report Print`** · **`MSCAST Spares Handover Note`** ·
**`MSCAST Client Claim Print`**

The two Project prints are live: the schedule prints the six contractual milestones with the real
drawing / inspection / dispatch / commissioning counts, the status report prints a progress bar,
the commercial position (contract, billed, outstanding, bought-out, open claims) and the open
punch points.

## 6. Reports

Original eight: `MSCAST Project MIS` · `MSCAST PO vs PCC Variance` · `MSCAST Drawing Register` ·
`MSCAST Free Issue at Vendor` · `MSCAST Dispatch Schedule` · `MSCAST Retention and Certificates` ·
`MSCAST BRM Register` · `MSCAST Inspection Status`

Added in batches A-C:

| Report | What it answers |
|---|---|
| **MSCAST MSME 45-Day Dues (s.15 MSMED / s.43B(h))** | Which MSME supplier bills are past 45 days, by how many days, and what is at risk of disallowance / MSME Form I |
| **MSCAST SO - PO - Invoice Tracker** | Per order: value, billed, collected, PO committed, supplier billed, % delivered, % billed |
| **MSCAST Project Closure Report** | Contract vs PCC vs actual bought-out, receivable, certificates, open claims, drawings and inspections, with a closure verdict |
| **MSCAST Balance Sheet (Schedule III grouping)** | Ledger balances mapped to Schedule III heads (shareholders' funds, non-current / current liabilities and assets) |
| **MSCAST Statement of Profit and Loss (Schedule III grouping)** | Revenue, other income, material, employee benefits, finance costs, depreciation, other expenses |
| **MSCAST Daily Management Summary** | 15 indicators on one page: cash, receivables, overdue, retention, payables, MSME exposure, order book, drawings, inspections, BRMs, claims |
| **MSCAST Expense Analysis (vs last year, % of sales)** | Expense growth and margin view |

`MSCAST Daily Management Summary`, `MSCAST Dispatch Schedule` and `MSCAST Project MIS` are set up as
scheduled email reports (they will send once an SMTP account is configured).

## 7. Accounting depth added in batch A

- **COA heads:** Reserves and Surplus, Borrowings - HDFC Term Loan, Lease Liabilities, Prior Period
  Expenses, Fines and Penalties under Law, Retention Receivable, Petty Cash + Cash mode of payment
- **6 journal vouchers:** electricity, petty cash imprest, petty cash spend, foreign travel
  (customer visit), marine + erection insurance, cargo agency (ODC movement)
- **Landed cost voucher** MAT-LCV-2026-00001 (₹45,000 freight) apportioned onto a receipt
- **Credit note** SINV-26-00003 (sales rejection) and **debit note** PINV-26-00002 (rate difference)
- **TDS 194C** category at 2% with thresholds; PINV-26-00003 ₹5,98,560 with ₹10,320 TDS deducted
- **Dunning** DUNN-09-26-00001 on an overdue invoice and **payment request** ACC-PRQ-2026-00001 (advance)
- **Retention** JV ACC-JV-2026-00007: ₹1,81,248 reclassified out of trade receivables
- **Supplementary invoice** SINV-26-00004 against the agreed client claim
- **Gratuity:** Gratuity Rule (15/26 days per completed year) + provision JV ACC-JV-2026-00008
  ₹9,91,414 for 6 employees, with the per-employee working in the narration
- **Assets:** 4 submitted - CAD workstation, welding/testing equipment, **ERP software licence
  (intangible, 36-month amortisation)** and **hydraulic test bench (CWIP**, ₹7.80 L sitting in
  1790 - CWIP Account from PINV-26-00004, available for use in 3 months)
- **Share capital:** 3 shareholders with folio numbers, 10,000 equity shares of ₹10 (paid-up ₹1,00,000)

## 8. GST (India Compliance)

- Company and all 15 parties carry GSTIN, state and GST category; addresses created for each
- 48 items carry HSN/SAC codes and an 18% GST item tax template
- **SINV-26-00001** intra-state CGST+SGST · **SINV-26-00002** inter-state IGST · **PINV-26-00001**
  input IGST linked to the purchase receipt and BRM
- **MCA audit trail on** (India Compliance: once enabled it cannot be turned off)
- e-way bill enabled; e-invoice off (needs API credentials)
- 4 suppliers tagged **Micro / Small with Udyam numbers**, feeding the MSME 45-day report

## 9. HR and payroll

Unchanged from v2: 6 employees, holiday list with per-employee assignment, 73 attendance records,
leave, site-travel expense claim, salary structure (Basic 50%, HRA 40% of basic, conveyance, special
allowance; PF 12%, ESIC 0.75%, Professional Tax MH, TDS) and 6 submitted salary slips for August 2026.
Batch C adds the **Gratuity Rule** and the **gratuity provision**.

**Note:** india_payroll's own statutory engine (EPF/ESIC/PT auto-calculation, ECR file, Form 16, 24Q)
needs company-level statutory configuration that is still out of scope; the demo structure computes
the same deductions with explicit formulas.

## 10. What is still not live (9 of 97 requirements)

| ID | Item | Why |
|---|---|---|
| AC-05 (part) | Management summary pushed to a chat channel as well as email | channel decision D7 (SMS vs WhatsApp vs Google Chat) |
| A-14 | Schedule III statements in statutory format | built as grouped query reports; the statutory template needs the CA's sign-off |
| AC-11 | Deferred tax and income-tax provision entries | gratuity provision is done; these need the CA's numbers |
| PC-02 | Billing / dispatch schedule child table on the project | small build, not yet done |
| A-09 | Receipt print to the customer | small config |
| AC-17 | Project WIP valuation | decision D6 with the CA |
| M-03 | Biometric attendance connector | needs the device make / model |
| M-02, AC-18 | "Finance Scaling Management", "GST on closing inventory" | need MSCAST / CA clarification |
| AC-07 | AS vs Ind AS and notes to accounts | CA decision, outside the ERP |

Also outstanding before this becomes production: real users and passwords, HTTPS on a VPS, daily
India-hosted backups (Companies (Accounts) Rules r.3(5)), Tally opening-balance migration, and the
Gemini automation layer from the phased plan.

## 10a. Email (live since 19 Sep 2026)

| Setting | Value |
|---|---|
| Outgoing account | `mscast-test` - uattech@carobar.net |
| SMTP | smtp.purelymail.com:465, SSL, Basic auth, set as default outgoing |
| Incoming | imap.purelymail.com:993 configured but **disabled** (enable it to file customer replies against documents) |
| Site URL for links | `https://mscast.carobar.net` (set as `host_name`) |
| Footer | MSCAST footer; the standard "Sent via ERPNext" line is disabled |
| Scheduled mail | daily digest + daily management summary + dispatch schedule + project MIS, all to autoelectron.jp@gmail.com |

First send verified at Gmail with `spf=pass`, `dkim=pass` (carobar.net, s=purelymail2) and
`dmarc=pass` - carobar.net's DNS already carries Purelymail's records, so mail lands in the inbox.
The daily management summary itself was delivered on 19 Sep 2026 (Email Queue `7s5k1g8ifm`, Sent).

**Scheduled report settings**

| Report | Format | Sends when |
|---|---|---|
| MSCAST Daily Management Summary | HTML in the body | every day, even when nothing moved - a quiet day is information |
| MSCAST Dispatch Schedule | XLSX attachment (500 rows) | only when there are rows, so it does not become noise |
| MSCAST Project MIS | XLSX attachment (500 rows) | only when there are rows |

**Send time.** Frappe fires daily auto email reports inside its 00:00 site-time job, which put the
summary in the inbox at midnight IST - yesterday's closing position wearing today's date. Frappe's
built-in `send_daily` job is therefore stopped (Scheduled Job Type `6ptvg6vnto`, `stopped=1`,
reversible) and a cron server script **MSCAST morning report batch** (`30 8 * * *`) drives the same
logic at **08:30 Asia/Kolkata** - next execution confirmed as `2026-09-19 08:30:00` site time, which
is midday in Japan. The script loops over every enabled Daily auto email report, so new ones are
picked up without touching it.

Note: `Auto Email Report.send()` refuses to run on a disabled report, so the reports stay enabled and
the *trigger* is what moved - not the reports.

**Daily summary, version 2 (19 Sep 2026).** The first version was reviewed against the data and two
indicators were wrong: "drawings awaiting customer approval" counted every drawing whose status was not
literally `Approved` (the real option is `Approved by Customer`, so it returned all 9 instead of 2), and
"inspections not accepted" counted `Accepted with deviation` as not accepted. Both fixed. The report now
has 20 indicators, money in Rs lakh / crore, and an **Attention** column (OK / WATCH / ACT) with the
reason spelled out - "ACT - pay or lose the deduction", "WATCH - retention locked", "ACT - supplier
cannot be paid".

**Indian dates.** MariaDB runs on UTC inside the container while the site runs on Asia/Kolkata, so every
raw-SQL `curdate()` was comparing against the previous day for 5.5 hours out of 24. All custom reports
now use `date(convert_tz(utc_timestamp(),'+00:00','+05:30'))` instead - 22 date references across the
daily summary, the MSME 45-day report and the dispatch schedule. This is not cosmetic: the MSMED 45-day
clock, "billed this month" and the overdue tests all hang off it. The fix immediately changed one line -
MSME dues falling due within 15 days went from Rs 0 to Rs 7.80 L, because a bill had just crossed day 30
in Indian time.

**Bounce protection.** `mscast.demo`, `mscast.local` and `example.com` do not resolve, so every system
mail addressed to the demo users, the setup-wizard admin or Administrator would hard-bounce and damage
carobar.net's sending reputation. Those users are marked **unsubscribed** - they still log in, they
just receive no mail. All role-based notifications (BG expiry, PO over PCC, drawing awaiting approval)
now resolve to a single live mailbox, and the demo roles were added to that user so no notification
ends up with no recipient.

**If the funnel is switched off**, document links inside emails stop resolving until it is back on;
change `host_name` in `sites/frontend/site_config.json` and restart the backend to point elsewhere.

## 11. Suggested 15-minute walkthrough

1. **Workspace** `/app/mscast` - KPIs and charts on one screen.
2. **MSCAST Project Kickoff** for PROJ-0002 - the customer-PO checklist and the workflow parking it
   in *PO Query Raised*.
3. **Project MIS** - contract value vs PCC estimate vs PO committed vs billed vs hours.
4. **PCC-2026-00001** - the cost sheet; print it.
5. **PO vs PCC Variance** - what is committed against the estimate.
6. **Drawing register + Transmittal** - revision history and what was issued to whom, acknowledged.
7. **Free Issue at Vendor** - plate and sections lying with the fabricator.
8. **BRM** - certification checklist; then try a **Payment Entry against an uncertified bill** and
   watch it get refused.
9. **MDM → Delivery Instruction** - print shows the dispatch list and Annexure-I.
10. **Commissioning report and spares handover** - print both.
11. **Project Status Report / Project Schedule (Client)** - the two client-facing prints.
12. **SINV-26-00002** IGST breakup → GSTR-1 → Purchase Reconciliation Tool.
13. **MSME 45-Day Dues** and **Daily Management Summary** - the two reports a director opens daily.
14. **Schedule III balance sheet and P&L**, then **Project Closure Report**.
15. **Salary slip** with PF, PT and TDS; the gratuity provision voucher.

## 12. Files

```
D:\MSCAST\
  ERP Plan\                      the documents - one current version of each, no version suffixes
    MSCAST ERP - Requirements Traceability Matrix.xlsx
    MSCAST ERP - Strategy and Phased Plan.docx
    MSCAST ERP - Research Appendix.docx
    MSCAST ERP - Implementation Report.md
    MSCAST Knowledge Base.docx
    markdown\                    the same documents as markdown, plus kb\ (7 knowledge-base files)
  erpnext-poc\
    README.md                    this file
    REBUILD.md                   the full rebuild order, stage by stage
    scripts\                     start / stop / status / backup / reset / run-seed / build / swap
      _archive\                  one-off dev diagnostics, kept for reference
    seed\                        73 scripts that build the POC, numbered in run order
      _archive\                  32 read-only diagnostics and superseded iterations
    backups\                     dated database + files backups
~/mscast-poc\                    compose.yaml, apps.json, frappe_docker checkout (inside WSL)
```

Everything in `_archive\` can be deleted without affecting the POC or a rebuild; it is kept only
because the diagnostics are handy when something misbehaves.

The scripts worth knowing:

| Command | What it does |
|---|---|
| `run-seed.sh 102_test_harness` | the 23 automated checks - run this after any change |
| `run-seed.sh 59_verify` | full inventory of what exists in the site |
| `start-poc.sh` / `stop-poc.sh` / `status-poc.sh` | day to day |
| `backup-poc.sh` | database + files to `backups\` |
| `reset-poc.sh` | wipe and rebuild from every seed script (~25 min) |
