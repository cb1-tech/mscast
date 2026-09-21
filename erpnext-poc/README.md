# MSCAST ERP — POC on ERPNext v16 (WSL / Docker)

**Version:** 3.0 · 21 September 2026 · **Release:** `v0.9.0` · **Repository:** `github.com/cb1-tech/mscast` (owner-held)
**Where:** WSL Ubuntu on thinkstation · **Live POC:** https://mscast.carobar.net (local http://localhost:8080) · **DEV:** https://mscastdev.carobar.net (local http://localhost:8081)

- All company data is **fictional demo data**; customer and supplier names end with "(DEMO)". MSCAST's own identity (name, GSTIN, CIN, branding) is real and deliberate.
- **Build checks: 42.** DEV and Live POC: 40 PASS, 2 WARN, 0 FAIL. See *Build checks*.

---

## Instances and access

| | Live POC | DEV |
|--------------------|-----------------------------------------------|---------------------------------|
| URL | https://mscast.carobar.net | https://mscastdev.carobar.net |
| Used by | MSCAST staff trying it with their own logins | Demos, screenshots, development |
| Users | Mustaque@mcast.co.in, aiqaz@mcast.co.in, waseemraj@mcast.co.in; demo logins Anita (carobar.tradecars@gmail.com), Sameer (uattech@carobar.net), Rohit (autoelectron.jp@gmail.com) | Full demo cast (below) |
| Changes | None without the owner's say-so | Free |

- **Live POC:** MSCAST's trial admin deleted most demo personas on 21 Sep 2026 (Meera, Kavita, Vinod, Prashant, Nikhil, the CA login, all `@mscast.demo` accounts).
- **DEV demo cast:** Mustaque Chandankeri (Director, latookaushik@yahoo.com) · Aiqaz Chandankeri (Director, latookaushik@hotmail.com) · Anita Deshpande (Accounts Manager, carobar.tradecars@gmail.com) · Sameer Lokhande (Purchase Manager, uattech@carobar.net) · Meera Rane (Design, meera.rane@mscast.co.in) · S. Joshi (CA/Auditor, autoelectron.jp+ca@gmail.com) · Rohit Kulkarni (prepares PCCs, autoelectron.jp@gmail.com) · Nikhil Sawant (Purchase Executive) · Kavita Joshi (Accounts Executive) · Prashant More (Stores) · Ganesh Pawar (Quality Manager, autoelectron.jp+site@gmail.com) · Vinod Shelke (records inspections). Directors are MSCAST's real directors; the others are demo faces. Site administrator: `admin@mscast.local`.
- **Personas with real mailboxes are deliberate**, so the 08:30 and 08:35 mails can be shown arriving.
- **No password appears in this file, and none may.** Passwords are shared separately.
- **Administrator password:** must be rotated before real data goes on a server (parked by the owner until then).
- **Administrators:** `admin@mscast.local` holds `System Manager` only; with the built-in `Administrator`, that is the whole list on DEV. The ERPNext setup wizard gives its administrator every role on each fresh install; cutting it back is a go-live checklist step (doc 08, section 7). On Live POC, Aiqaz was also given `System Manager` (T6f warns).

---

## What is running

| Piece | Detail |
|----------------------------|------------------------------------------------------------------------|
| Stack | compose project `mscast-poc`, 9 containers, from `~/mscast-poc/compose.yaml` |
| Image | **`mscast/erpnext:v16-app`** (5.13 GB): the frappe_docker build plus `mscast_erp` baked in, via `erpnext-poc/Containerfile.mscast` |
| Apps | frappe 16.34.0 · erpnext 16.35.0 · **india_compliance 16.9.1** · **hrms 16.19.0** · **india_payroll 16.0.4** · **mscast_erp 0.1.0** |
| Database | MariaDB 11.8 (ERPNext does not support PostgreSQL) |
| Site | `frontend`, port 8080 · server scripts **enabled** |
| Files | scripts and seed data in `D:\MSCAST\erpnext-poc`; the app in `D:\MSCAST\mscast_erp` |
| Memory | WSL capped at 8 GB; the stack idles at about 1.5–2.5 GB |

- **The configuration is an installable app.** `mscast_erp` carries every custom document, report, print format, workflow, control, the permission matrix and the desk theme. Anything that must be clicked in by hand after an install is a defect in the app.
- **The app must be in the image.** `apps/` comes from the image; only `sites` and `logs` are volumes. An app in one container only gives HTTP 500 on the web and scheduled jobs that never run, while `bench console`/`bench execute` and the build checks still pass. `T9f` checks each job's `last_execution`.
- **WSL shuts its VM down when idle**, which stops the containers. Keep any WSL terminal open; `demo-up.ps1` does this.

## Day-to-day commands

```powershell
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/start-poc.sh    # start
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/status-poc.sh   # status + URL check
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/stop-poc.sh     # stop (data kept)
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/snapshot.sh <label>   # backup before anything risky
```

Re-run any seed step (safe to repeat):

```powershell
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/run-seed.sh 102_test_harness
```

| Script | What it does |
|---------------------------------|-------------------------------------------------------------------|
| `run-seed.sh 102_test_harness` | the 42 build checks — **run after any change** (`C=mscast-dev-backend-1` for DEV) |
| `run-harness.sh` | the same, output filtered to the result lines |
| `run-seed.sh 127_exception_engine` | run the overnight rule sweep by hand |
| `run-seed.sh 160_omni_test` | prove the AI briefing end to end |
| `run-seed.sh 177_census` | one authoritative count of everything |
| `doc-facts.sh` | print what the documents assert (roles, workflows, schedules) straight from the running system |
| `audit-sod.sh` | full segregation-of-duties audit, including create-permission overlaps |
| `snapshot.sh <label>` | database + files backup, copied out to `backups\` |
| `reset-poc.sh` | wipe and rebuild from every seed script (~30 min). **Reproduces the configuration, not the demo data** (see *Known limitations*) |
| `reset-poc-run.sh` | run the above unattended, from a snapshot, logging to `reset-run.log` |
| `deploy-app.sh` | build the image and redeploy after an app code change, then prove `/login` answers |
| `backup-out.sh` | copy a backup set out of the Docker volume onto `D:` |
| `restore-test.sh` | restore a backup into a **separate** site and count what came back |
| `restore-live.sh` | restore a backup **over** the live site |
| `verify-site.sh` | count what is in a site |
| `status.sh` | sites, bench processes, local and public HTTP status, containers, age of the last backup |
| `new-mscast-site.sh` | **the production install path**: fresh site, six apps, MSCAST's configuration, no demo data; reports success only if the 19 system checks pass |
| `nightly.sh` | **what the Windows task "MSCAST nightly backup" runs (02:30 JST)**: `backup-nightly.sh`, then all build checks; records both outcomes in site config; emails `mscast_alerts_to` (autoelectron.jp@gmail.com) if either failed. `SIMULATE_FAIL=1` sends a test alert. In-site watchdog `mscast_erp.controls.watchdog` (09:00 IST) emails if the nightly job has not run in 26 hours |
| `backup-nightly.sh` | backup, copy off the volume onto `D:`, verify, prune (14 newest + monthly for a year). Refuses if the site cannot decrypt its own secrets. Called by `nightly.sh` |
| `restore-key.sh` | put a backup's `encryption_key` back on a site; without it every stored password is unreadable after a restore |
| `build-base-image.sh` | build the base image (Frappe + erpnext, hrms, india_compliance, india_payroll) from `apps.json` via frappe_docker |
| `app-versions.sh` | print every app's version in an image |
| `completeness-test.sh` | build a fresh site and compare it with live, record by record and permission row by permission row. Anything live has that a fresh install lacks exists only in the database |
| `upgrade-test.sh` | restore a backup into a **separate** stack on :8090 running a candidate image, `bench migrate`, run all checks, tear down. Mail muted, scheduler off |
| `build-mscast-image.sh` | rebuild `mscast/erpnext:v16-app` with the current app baked in — **the real way to ship a code change** |
| `push-app.sh` | copy the app into the running containers and restart them; fast iteration only. Container recreation discards anything pushed this way |
| `pull-fixtures.sh` | copy exported fixtures out of the container into the app |
| `test-stale-deploy.sh` | reproduce the stale-deploy failure and watch the guard catch it |

- **The container's app is a copy, not a mount.** Editing `D:\MSCAST\mscast_erp` changes nothing until the image is rebuilt (or `push-app.sh` runs). Never install from a stale container copy (see *Deploying*).

## Public access (Cloudflare tunnel)

| Piece | Detail |
|---------------------------------------|-------------------------------------------------------------|
| Route | Cloudflare Tunnel `mscast-demo` (one tunnel, two ingress rules: Live POC and DEV) |
| DNS | CNAME `mscast.carobar.net` in the Cloudflare zone |
| Origin | `http://<WSL IP>:8080`, rewritten each time `demo-up.ps1` runs because the IP changes |
| Credentials | `%USERPROFILE%\.cloudflared\` — keep private |

```powershell
powershell -ExecutionPolicy Bypass -File D:\MSCAST\erpnext-poc\scripts\demo-up.ps1
```

- `demo-up.ps1` starts both stacks, pins the WSL VM up, rewrites the tunnel config with the current WSL IP, restarts the tunnel and verifies the public URLs. A Startup shortcut brings it back after a reboot.
- **Take offline:** `Get-Process cloudflared | Stop-Process`. Remove the Startup shortcut to stop it returning; `cloudflared tunnel delete mscast-demo` revokes it permanently.
- Rejected: Tailscale Funnel (503 at the ingress; every client needs Tailscale); `networkingMode=mirrored` (breaks Docker's embedded DNS).
- Known issue, parked by the owner: live screen refresh (socket.io) through the tunnel.

## MSCAST's own forms

25 document types in the MSCAST module, 8 of them child tables.

| Form | Purpose |
|---------------------------------------|-------------------------------------------------------------|
| **MSCAST PCC** + items | Purchase Cost Calculation: component-wise estimate, revision, approval; baseline for PO control and MIS |
| **MSCAST Drawing** + revisions | Drawing register with revision history, driven by a workflow |
| **MSCAST MDF** + items | Material Data File per assembly, released to procurement |
| **MSCAST BRM** | Billing Routing Memo: quantity, rate, inspection and delivery certified before accounts pay |
| **MSCAST MDM** + items | Material Dispatch Memo with free-issue (Annexure-I) flag |
| **MSCAST Delivery Instruction** | Direct-to-site dispatch: consignee, transporter, LR, annexure |
| **MSCAST Inspection Plan** | In-process / pre-dispatch / third-party / customer inspection with result |
| **MSCAST Project Certificate** | Commissioning / preliminary / final acceptance, retention release |
| **MSCAST Project Kickoff** | Customer-PO verification checklist + kick-off minutes, driven by a workflow |
| **MSCAST Transmittal** + items | Drawing transmittal with acknowledgement |
| **MSCAST Commissioning Report** + parameters | Specified vs achieved, punch list, guarantee start |
| **MSCAST Spares Handover** + items | Commissioning and 2-year mandatory spares, with part numbers |
| **MSCAST Client Claim** | Scope variation, idle time, escalation; agreed value and settling invoice |
| **MSCAST Customer Asset** | Customer-owned tooling held by MSCAST or its sub-contractors |
| **MSCAST Installed Machine** | The installed base: 14 machines, 2009–2024 |
| **MSCAST Bid Outcome** | Won and lost bids with reasons (basis for a win/loss view) |
| **MSCAST Exception** | What the overnight checks found. Written by the system, cleared by people |
| **MSCAST Archival Log** | Monthly archival run record with the 8-year retention note |

### Workflows (five, all active)

| Workflow | On | The control |
|-------------------------|------------------|---------------------------------------------------------|
| **MSCAST PCC Approval** | MSCAST PCC | Approve and Send Back are a **director's** |
| **MSCAST Purchase Order Approval** | Purchase Order | Sent for approval by `Purchase User`, **approved by a director**. A PO cannot be approved unless someone with `Purchase User` sent it. Nobody holds both roles |
| **MSCAST BRM Certification** | MSCAST BRM | Purchase prepares, a **director certifies**, Accounts marks paid. Cannot be certified unless its four checks (qty, rate, inspection, delivery) are ticked |
| **MSCAST Project Kick-off** | MSCAST Project Kickoff | Accounts verify the customer PO, a **director approves**. Cannot be approved while the PO checklist is incomplete |
| **MSCAST Drawing Release** | MSCAST Drawing | *Released for Manufacture* is reachable **only** from *Approved by Customer*, and only by a Projects Manager |

- **Three roles on the BRM workflow do not mean three people.** Both directors hold `Projects Manager` (can create a BRM), `MSCAST Director` (certifies) and `Accounts Manager` (marks paid). See T6g.

### Other controls

- **BRM payment block** — application code `mscast_erp.controls.brm_payment`, on `before_submit` of **Payment Entry and Journal Entry**. No certified BRM covering the bill and amount → no supplier payment, for everyone including directors; an advance with no invoice reference is refused. Tested on six routes on every run (`T6a`). Only exception: a supplier ticked *Exempt from BRM certification* (electricity, water, rent, telephone, statutory bills).
- **Overnight exception sweep** — 16 rules at 06:00 IST comparing documents against each other and the calendar; writes to MSCAST Exception. No model, no network.
- **AI morning briefing** — 08:35 IST; turns the findings plus the management summary into a few sentences on what matters today, every item linked. Live POC recipient: waseemraj@mcast.co.in (owner's decision). Falls back to a plain list if the model is unreachable.
- **Post-deploy verification** — after every install and upgrade, six control transitions are checked and repaired, with a banner (see *Deploying*).
- **Monthly archival job** — writes an MSCAST Archival Log entry.

### Roles

- `MSCAST Director` is the **approving** role: PCC approval, purchase order approval, BRM certification, kick-off approval.
- **Auditor** (held by the external CA) is read-only: read, report, print, export including version history; no write anywhere.
- Per-role detail: doc 09 (Role Cards).

## Print formats

- 15 custom formats on MSCAST letterhead, A4. Every format with a sample document is rendered in the build checks (15 on the current data set, `T4`).
- `MSCAST PCC Sheet` · `MSCAST MDF Sheet` · `MSCAST Material Dispatch Memo` · `MSCAST Delivery Instruction Print` (Annexure-I) · `MSCAST Billing Routing Memo` · `MSCAST Inspection Report` · `MSCAST Project Certificate Print` · `MSCAST Proforma Invoice` · `MSCAST Project Schedule (Client)` · `MSCAST Project Status Report` · `MSCAST Transmittal Note` · `MSCAST Commissioning Report Print` · `MSCAST Spares Handover Note` · `MSCAST Client Claim Print`
- The DEMONSTRATION watermark is app code, switched on by `bench --site <site> set-config mscast_demo 1`. Never set it in production; `T4b` fails either way round.

## Reports (28 custom)

The eight originals: `Project MIS` · `PO vs PCC Variance` · `Drawing Register` · `Free Issue at Vendor` · `Dispatch Schedule` · `Retention and Certificates` · `BRM Register` · `Inspection Status`

| Report | What it answers |
|-------------------------------------|---------------------------------------------------------------|
| **MSME 45-Day Dues** | Which MSME bills are past 45 days and what is at risk under s.43B(h) |
| **SO – PO – Invoice Tracker** | Per order: value, billed, collected, PO committed, % delivered, % billed |
| **Project Closure Report** | Contract vs PCC vs actual, receivable, certificates, open claims, with a verdict |
| **Balance Sheet (Schedule III)** | Ledger balances mapped to the statutory vertical format |
| **Statement of P&L (Schedule III)** | Revenue through to tax and EPS |
| **Daily Management Summary** | 20 indicators with an OK / WATCH / ACT column and the reason spelled out |
| **Expense Analysis** | Growth and margin against last year |
| **Installed Base** and **Bid Outcomes** | The machines in the field, and why bids were won or lost |

- **Report names must be URL-safe** (no `/`), and a `%` in report SQL is read as a formatting character; `T2`/`T2b` run each report as the desk does, as the users who need it.
- **Indian dates:** MariaDB runs UTC inside the container while the site runs Asia/Kolkata. Every custom report uses `date(convert_tz(utc_timestamp(),'+00:00','+05:30'))`, never `curdate()`; `T3` fails any report that does not. The MSMED 45-day clock depends on it.

## Accounting depth

- Schedule III statements that balance to the rupee and tie to the ledger.
- 25 notes to accounts, including the MSMED s.22 disclosure, related party, contingent liabilities from live bank guarantees, and the 2021 negative disclosures.
- The eleven prescribed ratios, guarded so an immaterial denominator shows `n/a`.
- Current and deferred tax; project WIP; landed cost, credit and debit notes, TDS 194C, dunning, retention reclassification, gratuity provision; four assets including CWIP and an intangible.

## GST, HR and mail

- **GST** — company and all parties carry GSTIN, state and category; every invoiced item has an HSN; intra-state and inter-state invoices both present; MCA audit trail on and non-disableable; four suppliers tagged Micro/Small with Udyam numbers feeding the MSME report. GSTIN check digits and pincode-to-state validated on entry.
- **HR** — 6 employees, holiday list, 150 attendance records, leave, expense claim, salary structure and submitted salary slips; Gratuity Rule and provision. **Biometric pull switched off**: 72 punches and the reconciliation report exist, the automation is not running.
- **Mail** — Purelymail on `uattech@carobar.net`; SPF, DKIM and DMARC pass at Gmail. Driven by a cron server script (not Frappe's midnight job), Asia/Kolkata:

| Time (IST) | Mail | To |
|----------------------|-----------------------------------|-------------------------------------------|
| 08:30 | Daily summary, dispatch schedule, project MIS | autoelectron.jp@gmail.com |
| 08:35 | AI briefing | waseemraj@mcast.co.in (Live POC) |
| 09:00 | Watchdog, only if the nightly job has not run in 26 h | `mscast_alerts_to` |

- Email links use the public host (`host_name` set per site); `T9i`.

## Deploying

**Read before installing or upgrading anything.** Production steps: doc 08 (Production Cutover Runbook).

- **Installing or upgrading the app re-imports its configuration and overwrites the database** (a plain `bench migrate` resets a workflow role changed in the database).
- **Deploying from a stale copy reverts business rules** to that copy (PCC approval to System Manager, BRM certification to Purchase Manager, with no check failing — before T6d existed).
- **Anything changed in the ERPNext screens is reverted at the next upgrade.** Business rules live in git.
- **Guard:** after every install and migrate, six control transitions are verified and repaired, with a banner and an Error Log entry naming each one. A banner means package and agreed configuration have diverged: reconcile, do not just note it. `test-stale-deploy.sh` reproduces it.
- **Fixtures carry only MSCAST's records** (39 custom fields / 38 property setters / 3 email templates, measured against `evidence/baseline-without-mscast.json`). `mscast_erp` migrates last, so a foreign fixture would revert its owner's next release. New MSCAST customisations must carry module **MSCAST** or they are not exported. `T6m`.
- **Permission matrix ships in the app** (`mscast_erp.controls.permissions`, run on every install and migrate). Inserting one custom permission row replaces *all* of a doctype's standard rows, so every row is declared. `T6k`, `T6l`.
- **Oversight roles' rights** (directors, statutory auditor, Design User) are declared as data in `mscast_erp/controls/oversight.json`; `completeness-test.sh` confirms a fresh install matches live.
- **Settings outside the database — a restore does not carry them:** `encryption_key` (`restore-key.sh`, `T9g`), `server_script_enabled` (bench-wide, `T1c`), `host_name` (`T9i`).
- **Restore path:** the db root password is in `compose.yaml` as `MYSQL_ROOT_PASSWORD`, not in `common_site_config.json`; use `--mariadb-user-host-login-scope` (`--no-mariadb-socket` is deprecated).
- **Backups live in the Docker volume**, and `reset-poc.sh` runs `docker compose down -v`: copy them out first (`backup-out.sh`). `restore-test.sh` restores into a separate site for the build checks to run against.

## Build checks

42 automated checks in `seed/102_test_harness.py` (the harness). Run with `run-seed.sh 102_test_harness` or `run-harness.sh`; prefix `C=mscast-dev-backend-1` for DEV.

- **DEV (21 September 2026):** 40 PASS, 2 WARN (T6e, T6g), 0 FAIL. Both warnings wait on MSCAST's answers to Q20 and Q21 (doc 03).
- **Live POC (21 September 2026, after the Stores/Accounts access fix):** 40 PASS, 2 WARN (the same T6e, T6g), 0 FAIL.
- **Fresh install (`new-mscast-site.sh`):** must pass the 19 system checks.

| Check | Area | What it asserts | DEV | Live POC |
|-------------|--------------------|-------------------------------------------|------------|------------|
| T1 | reports | 326 SQL literal comparisons match the fields' real Select options (0 mismatched) | PASS | PASS |
| T1b | reports | Server-script literals match the fields' real Select options (the home page's counts) | PASS | PASS |
| T1c | reports | Server scripts are enabled on this bench (a restore does not carry `server_script_enabled`) | PASS | PASS |
| T2 | reports | Every custom report executes the way the desk runs it (with a filters dict); 0 failures | PASS | PASS |
| T2b | reports | Report names are safe in a URL, and each report opens for the users who need it, run as those users | PASS | PASS |
| T3 | reports | No report uses the container's UTC date | PASS | PASS |
| T4 | prints | 15 custom print formats render; 0 problems | PASS | PASS |
| T4b | prints | Demonstration site: every print watermarked; any other site: none | PASS | PASS |
| T5a | ledger | Trial balance nets to zero | PASS | PASS |
| T5b | ledger | Schedule III balance sheet balances to the rupee | PASS | PASS |
| T5c | ledger | P&L profit ties to the ledger surplus | PASS | PASS |
| T5d | ledger | No ledger entry without a cost centre | PASS | PASS |
| T6a | controls | BRM payment block guards every payment route; six routes attempted on each run and rolled back | PASS | PASS |
| T6b | controls | 5 workflows active and complete | PASS | PASS |
| T6c | controls | Controls live in the application package; server scripts only where intended; fails if the retired BRM payment script reappears | PASS | PASS |
| T6d | controls | Approval authority is where the business put it; 5 transitions asserted | PASS | PASS |
| T6e | controls | Nobody can both raise and approve the same document. Warns: a director can prepare a PCC or verify a customer PO and approve it alone (Q20) | WARN | WARN |
| T6f | controls | Only administrators hold System Manager. Administrators = `Administrator`, `admin@mscast.local`, plus site config `mscast_admins` (Live POC: aiqaz@ and arham@mcast.co.in, MSCAST's own admins) | PASS | PASS |
| T6g | controls | No one person can create a document and then approve it. Warns: a director can create, certify and mark paid a BRM alone (Q21) | WARN | WARN |
| T6h | controls | The auditor's login cannot change anything (effective rights, not stored rows) | PASS | PASS |
| T6i | controls | Every role can raise the documents its role card describes | PASS | PASS |
| T6j | controls | A guarded workflow state is guarded on every route into it | PASS | PASS |
| T6k | controls | Everyone who can approve a document can open it (asked per real user) | PASS | PASS |
| T6l | controls | No role silently lost access to a customised document type | PASS | PASS |
| T6m | controls | The package ships all of MSCAST's configuration and none of any other app's | PASS | PASS |
| T6n | controls | A BRM cannot be certified with its four checks (qty, rate, inspection, delivery) unticked; attempted as a director, then rolled back | PASS | PASS |
| T7a | data | Every MSCAST form has records; fails if it finds no forms to check | PASS | PASS |
| T7b | data | Every stored Select value is a valid option (45 fields on 25 document types) | PASS | PASS |
| T7c | data | Every invoiced item carries an HSN code | PASS | PASS |
| T8 | gst | GST head matches the place of supply on every invoice | PASS | PASS |
| T9a | email | Outgoing mail account configured | PASS | PASS |
| T9b | email | Mail actually leaves the system | PASS | PASS |
| T9c | email | Morning report batch scheduled | PASS | PASS |
| T9d | email | Every enabled notification has a live recipient | PASS | PASS |
| T9e | email | No live user on a non-deliverable domain (.demo, .local, example.com …) | PASS | PASS |
| T9f | automation | Every enabled MSCAST scheduled job has actually run (a real `last_execution`) | PASS | PASS |
| T9g | automation | Every stored secret decrypts with this site's key (`restore-key.sh` restores the key) | PASS | PASS |
| T9h | automation | The nightly backup ran in the last 26 hours and succeeded (DEV: reads "not applicable", `mscast_dev_copy`) | PASS | PASS |
| T9i | automation | Links in emails point at the public address, not the container's internal name | PASS | PASS |
| T10a | hr | Payroll and attendance loaded | PASS | PASS |
| T10b | hr | No duplicate attendance for an employee on a date | PASS | PASS |
| T10c | hr | Biometric punches converted into attendance; no punches at all is accepted (device not connected, attendance by hand) | PASS | PASS |

## Known limitations (not production yet)

- Demo data throughout; DEMONSTRATION watermark on client-facing prints.
- Administrator password to be rotated before real data goes on a server (parked by the owner).
- Previous-year comparatives blank until Tally opening balances are migrated.
- Biometric attendance pull switched off.
- Hosting: VPS in India, HTTPS, daily India-resident backups (Companies (Accounts) Rules r.3(5)). VPS move parked by the owner. See doc 08.
- The AI briefing points at a model router on this laptop; a server needs a hosted endpoint (three config lines, no code change).
- **`reset-poc.sh` reproduces the configuration, not the demo dataset.**
  - It installs all four extra apps in dependency order and aborts if any is missing (the compose `create-site` step installs only `erpnext`).
  - Seed steps then fail in a cascade: masters created by scripts numbered 150+ are referenced by scripts numbered 25. The seed scripts record how the POC was explored, not a designed build order (hence `*_fix`, `*_fix2`, `*_fix3`).
  - Every configuration check passes on a rebuilt site (reports, workflows, print formats, roles and permissions, BRM payment control, approval matrix); only data checks fail.
- **Use the right mechanism:** a fresh MSCAST system = `new-mscast-site.sh` (apps + fixtures, no data); *this* system with its data = restore a backup (`restore-test.sh` / `restore-live.sh`).
- Six accounting and scope assumptions await MSCAST and the CA; they are listed in doc 04 (Implementation Report) and written into the narration of the affected vouchers.

## Demo walkthrough

Full demo script with talking points: doc 12 (Demo Run-sheet). Short 15-minute route:

1. Workspace `/app/mscast` (KPIs and charts) → 2. MSCAST Exception (this morning's findings) → 3. MSCAST Project Kickoff for PROJ-0002 (parked in *PO Query Raised*) → 4. Project MIS → 5. PCC-2026-00001 (print it) → 6. PO vs PCC Variance → 7. a Drawing in Draft (release for manufacture is not offered) → 8. Drawing register + Transmittal → 9. Free Issue at Vendor → 10. BRM, then a Payment Entry against an uncertified bill (refused) → 11. MDM → Delivery Instruction (print shows dispatch list and Annexure-I) → 12. Commissioning report and spares handover (print both) → 13. MSME 45-Day Dues and Daily Management Summary → 14. Schedule III balance sheet and P&L, then Project Closure Report → 15. run the build checks (DEV: 42 checks, 40 pass, 2 expected warnings).

## Files

```
D:\MSCAST\                       git repository, remote github.com/cb1-tech/mscast
  mscast_erp\                    THE INSTALLABLE APP - this is what deploys
    mscast_erp\
      mscast\doctype\            25 document definitions
      fixtures\                  16 configuration files, exported from a working site
      agents\briefing.py         the 08:35 judgement half
      install.py                 post-install / post-migrate, incl. the control verification
      hooks.py                   fixtures list, scheduler events, CSS
  erpnext-poc\
    seed\                        114 scripts that build the POC, numbered in run order
      _archive\                  32 diagnostics and superseded iterations
    scripts\                     start/stop/status/backup/reset/run-seed/push/pull/deploy tests
    backups\                     dated backups (git-ignored)
  ERP Plan\                      the documents: For MSCAST\, Internal\, markdown\ (source)
~/mscast-poc\                    compose.yaml, apps.json, frappe_docker checkout (inside WSL)
```

- Everything in `_archive\` can be deleted without affecting the POC or a rebuild.
- **Documents:** `ERP Plan\` holds the documents (`For MSCAST\`, `Internal\`, and markdown sources; see `ERP Plan\README.md`); the ERP-MSCAST project on claude.ai holds the same content.

## DEV instance — https://mscastdev.carobar.net

Fully separate copy for demos, screenshots and development, so MSCAST's users work on the Live POC undisturbed.

| | Live POC | DEV |
|---------------------------|-------------------------------------|-------------------------------------|
| URL | mscast.carobar.net | mscastdev.carobar.net |
| Compose project | `mscast-poc` (~/mscast-poc) | `mscast-dev` (~/mscast-dev) |
| Local port | 8080 | 8081 |
| Database / Redis / volumes | own | own — nothing shared |
| Image | mscast/erpnext:v16-app | mscast/erpnext:v16-app-next: app changes are tested here before they go live (since 21 Sep 2026: report and settings access for Stores and Accounts) |
| Marker | DEMONSTRATION on prints | + orange "DEV INSTANCE" desk banner, tab title "MSCAST ERP - DEV" |
| Mail, scheduler | on | on (by decision; DEV mails go to the same addresses) |
| Backup alerts | on (`mscast_alerts_to`) | off: no `mscast_alerts_to`; `mscast_dev_copy` makes T9h read "not applicable" |
| Nightly backup | yes | no — rebuildable from its seed |

- **Seed data:** `D:\MSCAST\backups-dev-seed\20260921_125913` (Live POC at 12:59 IST, 21 Sep 2026; kept outside the pruned backup folder).
- **Build (first time):** `scripts/dev-create.sh` — compose copy on 8081, restore seed, key + `mscast_*` settings, `server_script_enabled`, `host_name`, migrate, DEV marker (seed 193).
- **Start after reboot:** `demo-up.ps1` starts both stacks and serves both hostnames (`start-dev.sh` for DEV alone).
- **Tunnel:** one tunnel (`mscast-demo`), two ingress rules. `tunnel-add-dev.ps1` adds the second host with zero downtime (new connector up before the old one stops).
- **Scripts against DEV:** prefix `C=mscast-dev-backend-1`, e.g. `C=mscast-dev-backend-1 bash scripts/run-harness.sh`.
- `restore-key.sh` sets config without `set-config --parse` (which rejects JSON `true`).
