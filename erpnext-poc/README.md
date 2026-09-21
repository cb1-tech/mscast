# MSCAST ERP — POC on ERPNext v16 (WSL / Docker)

**Updated:** 20 Sep 2026 · **Release:** `v0.9.0` · **Repository:** `github.com/cb1-tech/mscast`
**Where:** WSL Ubuntu on thinkstation · **Local:** http://localhost:8080 · **Public:** https://mscast.carobar.net

All company data in this POC is **fictional demo data**. Customer and supplier names end with "(DEMO)". MSCAST's own identity — name, GSTIN, CIN, branding — is real and deliberate, so the demonstration looks familiar to the client.

**Build checks: 34, of which 32 pass, 2 are expected warnings, 0 fail.**

---

## 0. Credentials and access — read this before sharing the link

**No password appears in this file, and none should.** An earlier version of this README printed the Administrator password in its header; anyone who had the document had the system.

- The Administrator password was changed during the POC. It has since been typed into a chat transcript, so it **must be rotated before the system carries real data on a server**. On this laptop it is a POC and does not matter.
- Every person has their own login: **12 named people, plus `admin@mscast.local`** as the site administrator. The old `@mscast.demo` role-shaped logins were retired when users were rebuilt as named people and are disabled.
- **The demonstration personas use real mailboxes deliberately.** Aiqaz, Mustaque, Sameer, Anita, Ganesh, Rohit and the CA are wired to addresses that actually receive mail, so the 08:30 summary and the 08:35 briefing can be demonstrated arriving. They are not stray accounts.

### Two role findings, both now fixed and both now checked

- **`admin@mscast.local` had collected 41 roles** — every manager role in the system plus a good deal it had no use for, on an account that had never logged in. It now holds `System Manager` and nothing else. **A fresh install will do this again**: the ERPNext setup wizard creates its own administrator the same way, which is why cutting it back is line 15 of the go-live checklist.
- **An operational staff account also held `System Manager`**, which bypasses every control in the system. Removed. Administration is now `admin@mscast.local` and the built-in `Administrator`, and that is the whole list.

`T6f` reports both on every build.

---

## 1. What is running

| Piece | Detail |
|---|---|
| Stack | compose project `mscast-poc`, 9 containers, from `~/mscast-poc/compose.yaml` |
| Image | **`mscast/erpnext:v16-app`** (5.13 GB) — the frappe_docker build plus `mscast_erp` baked in, via `erpnext-poc/Containerfile.mscast`. The app **must** be in the image: `apps/` comes from the image and only `sites` and `logs` are volumes |
| Apps | frappe 16.34.0 · erpnext 16.35.0 · **india_compliance 16.9.1** · **hrms 16.19.0** · **india_payroll 16.0.4** · **mscast_erp 0.1.0** |
| Database | MariaDB 11.8 (ERPNext does not support PostgreSQL) |
| Site | `frontend`, port 8080 · server scripts **enabled** |
| Files | scripts and seed data in `D:\MSCAST\erpnext-poc`; the app in `D:\MSCAST\mscast_erp` |
| Memory | WSL capped at 8 GB; the stack idles at about 1.5–2.5 GB |

**The configuration is an installable app.** `mscast_erp` carries every custom document, report, print format, workflow, control and the desk theme. That is what makes this rebuildable on a server rather than only on this laptop. If something has to be clicked in by hand after an install, that is a defect in the app, not a step in a runbook.

**WSL note:** WSL shuts its VM down when idle and that stops the containers. Keeping any WSL terminal open holds the VM up; `demo-up.ps1` does this for you.

## 2. Day-to-day commands

```powershell
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/start-poc.sh    # start
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/status-poc.sh   # status + URL check
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/stop-poc.sh     # stop (data kept)
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/snapshot.sh <label>   # backup before anything risky
```

Re-run any seed step (they are safe to repeat):

```powershell
wsl -d Ubuntu -e bash /mnt/d/MSCAST/erpnext-poc/scripts/run-seed.sh 102_test_harness
```

| Script | What it does |
|---|---|
| `run-seed.sh 102_test_harness` | the 31 build checks — **run this after any change** |
| `run-harness.sh` | the same thing, with the output filtered to the result lines |
| `run-seed.sh 127_exception_engine` | run the overnight rule sweep by hand |
| `run-seed.sh 160_omni_test` | prove the AI briefing end to end |
| `run-seed.sh 177_census` | one authoritative count of everything |
| `doc-facts.sh` | print what the documents assert — roles, workflows, schedules — straight from the running system |
| `audit-sod.sh` | the segregation-of-duties audit in full, including create-permission overlaps |
| `snapshot.sh <label>` | database + files backup, copied out to `backups\` |
| `reset-poc.sh` | wipe and rebuild from every seed script (~30 min). **Reproduces the system, not the demo data — see below** |
| `reset-poc-run.sh` | run the above unattended, from a snapshot, logging to `reset-run.log` |
| `deploy-app.sh` | build the image and redeploy after an app code change, then prove `/login` answers |
| `backup-out.sh` | copy a backup set out of the Docker volume onto `D:` |
| `restore-test.sh` | restore a backup into a **separate** site and count what came back |
| `restore-live.sh` | restore a backup **over** the live site |
| `verify-site.sh` | count what is in a site |
| `status.sh` | sites, bench processes, local and public HTTP status, containers, age of the last backup |
| `new-mscast-site.sh` | **the production install path**: a fresh site with the six apps and MSCAST's configuration, no demo data; refuses to report success unless the 13 system checks pass |
| `backup-nightly.sh` | backup, copy off the volume onto `D:`, verify, prune (14 newest + monthly for a year). Refuses if the site cannot decrypt its own secrets. Scheduled as Windows task *MSCAST nightly backup*, 02:30 |
| `restore-key.sh` | put a backup's `encryption_key` back on a site - without it every stored password is unreadable after a restore |
| `build-base-image.sh` | build the base image (Frappe + erpnext, hrms, india_compliance, india_payroll) from `apps.json` via frappe_docker |
| `app-versions.sh` | print every app's version in an image |
| `upgrade-test.sh` | restore a backup into a **separate** stack on :8090 running a candidate image, `bench migrate`, run all checks, tear down. Mail muted, scheduler off |
| `build-mscast-image.sh` | rebuild `mscast/erpnext:v16-app` with the current app baked in — **the real way to ship a code change** |
| `push-app.sh` | copy the app into the running containers and restart them, for fast iteration only. The image is the source of truth; a container recreation discards anything pushed this way |
| `pull-fixtures.sh` | copy exported fixtures out of the container into the app |
| `test-stale-deploy.sh` | reproduce the stale-deploy failure and watch the guard catch it |

**Two traps worth knowing.**

The container's copy of the app is a *copy*, not a mount. Editing `D:\MSCAST\mscast_erp` changes nothing until the image is rebuilt, or `push-app.sh` runs for a quick iteration. Installing the app from a stale container copy is how the approval rules silently reverted once — see section 9.

And the one that cost a day: **`apps/` comes from the image.** For most of this POC the app was not in the image at all — it had been copied into the backend container by hand — so exactly one container had it. The web workers could not import it, and the site served HTTP 500 on every request while every script and every build check passed, because `bench console` and `bench execute` start a fresh python each time. The scheduler and the queue workers could not import it either, so **four of the five scheduled jobs had never run once**. `T9f` now checks `last_execution` on each of them.

## 3. Exposing the demo to clients in India

**Public URL: https://mscast.carobar.net** — own domain, valid certificate, no VPN and no client software.

| Piece | Detail |
|---|---|
| Route | Cloudflare Tunnel `mscast-demo` |
| DNS | CNAME `mscast.carobar.net` in the Cloudflare zone |
| Origin | `http://<WSL IP>:8080` — rewritten each time `demo-up.ps1` runs, because the IP changes |
| Credentials | `%USERPROFILE%\.cloudflared\` — keep these private |

```powershell
powershell -ExecutionPolicy Bypass -File D:\MSCAST\erpnext-poc\scripts\demo-up.ps1
```

It starts the stack, pins the WSL VM up, rewrites the tunnel config with the current WSL IP, restarts the tunnel and verifies the public URL. A Startup shortcut brings the demo back after a reboot.

**Taking it offline:** `Get-Process cloudflared | Stop-Process`. Remove the Startup shortcut to stop it returning; `cloudflared tunnel delete mscast-demo` revokes it permanently.

*Rejected earlier: Tailscale Funnel (503 at the ingress, and every client would need Tailscale) and `networkingMode=mirrored` (broke Docker's embedded DNS).*

## 4. MSCAST's own forms

25 document types in the MSCAST module, 8 of them child tables.

| Form | Purpose |
|---|---|
| **MSCAST PCC** + items | Purchase Cost Calculation: component-wise estimate, revision, approval; the baseline for PO control and MIS |
| **MSCAST Drawing** + revisions | Drawing register with revision history — **driven by a workflow**, see below |
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
| **MSCAST Installed Machine** | The installed base — 14 machines, 2009–2024 |
| **MSCAST Bid Outcome** | Won and lost bids with reasons — the basis for a win/loss view |
| **MSCAST Exception** | What the overnight checks found. Written by the system, cleared by people |
| **MSCAST Archival Log** | Monthly archival run record with the 8-year retention note |

### Workflows — five, all active

| Workflow | On | The control |
|---|---|---|
| **MSCAST PCC Approval** | MSCAST PCC | Approve and Send Back are a **director's** |
| **MSCAST Purchase Order Approval** | Purchase Order | Sent for approval by `Purchase User`, **approved by a director**. Nobody holds both roles |
| **MSCAST BRM Certification** | MSCAST BRM | Purchase prepares, a **director certifies**, Accounts marks paid |
| **MSCAST Project Kick-off** | MSCAST Project Kickoff | Accounts verify the customer PO, a **director approves**. Cannot be approved with the checklist unticked |
| **MSCAST Drawing Release** | MSCAST Drawing | *Released for Manufacture* is reachable **only** from *Approved by Customer*, and only by a Projects Manager |

**Read the BRM row with section 9's second warning next to it.** The workflow says three roles. It does not follow that three *people* are involved, because both directors hold roles that can create a BRM as well as the role that certifies one and the role that marks it paid.

### Other controls

- **BRM payment block** — application code (`mscast_erp.controls.brm_payment`, wired on `before_submit`) refuses a supplier payment unless a certified BRM exists for that bill and covers the amount. It guards **Payment Entry and Journal Entry**, and refuses an advance with no invoice reference. Verified live in the harness on every run, on six routes (`T6a`). Absolute, and applies to everyone. The only exception is a supplier ticked *Exempt from BRM certification* — for electricity, water, rent, telephone and statutory bills, which cannot be certified against a purchase order.
- **Overnight exception sweep** — 16 rules at 06:00 comparing documents against each other and the calendar. Writes to MSCAST Exception. No model, no network.
- **AI morning briefing** — 08:35, turns the findings plus the management summary into a few sentences naming what matters most today, emailed to the directors with every item linked. Falls back to a plain list if the model is unreachable, so a missing model never means a missing email.
- **Post-deploy verification** — after every install and upgrade, six control transitions are checked and repaired, loudly. Section 9.
- **Monthly archival job** writing an MSCAST Archival Log entry.

### Roles

**Correction to earlier versions of this file:** `MSCAST Director` was described as a *read-only* role. It is the opposite — it is the **approving** role, and it is where PCC approval, purchase order approval, BRM certification and kick-off approval now sit.

Read-only belongs to **Auditor**, held by the external CA: read, report, print, export including version history, and no write anywhere.

Full detail, one page per role, is in *Role Cards*.

## 5. Print formats

16 custom formats on MSCAST letterhead, A4. Every one that has a sample document is rendered as part of the build checks — 15 on the current data set — so a format broken by a field change is caught before anyone prints it in front of a customer.

`MSCAST PCC Sheet` · `MSCAST MDF Sheet` · `MSCAST Material Dispatch Memo` · `MSCAST Delivery Instruction Print` (Annexure-I) · `MSCAST Billing Routing Memo` · `MSCAST Inspection Report` · `MSCAST Project Certificate Print` · `MSCAST Proforma Invoice` · `MSCAST Project Schedule (Client)` · `MSCAST Project Status Report` · `MSCAST Transmittal Note` · `MSCAST Commissioning Report Print` · `MSCAST Spares Handover Note` · `MSCAST Client Claim Print`

All client-facing formats carry a demonstration watermark. Remove it for production.

## 6. Reports — 28 custom

The eight originals: `Project MIS` · `PO vs PCC Variance` · `Drawing Register` · `Free Issue at Vendor` · `Dispatch Schedule` · `Retention and Certificates` · `BRM Register` · `Inspection Status`

| Report | What it answers |
|---|---|
| **MSME 45-Day Dues** | Which MSME bills are past 45 days and what is at risk under s.43B(h) |
| **SO – PO – Invoice Tracker** | Per order: value, billed, collected, PO committed, % delivered, % billed |
| **Project Closure Report** | Contract vs PCC vs actual, receivable, certificates, open claims — with a verdict |
| **Balance Sheet (Schedule III)** | Ledger balances mapped to the statutory vertical format |
| **Statement of P&L (Schedule III)** | Revenue through to tax and EPS |
| **Daily Management Summary** | 20 indicators with an OK / WATCH / ACT column and the reason spelled out |
| **Expense Analysis** | Growth and margin against last year |
| **Installed Base** and **Bid Outcomes** | The machines in the field, and why bids were won or lost |

## 7. Accounting depth

Schedule III statements that balance to the rupee and tie to the ledger; 25 notes to accounts including the MSMED s.22 disclosure, related party, contingent liabilities from live bank guarantees, and the 2021 negative disclosures; the eleven prescribed ratios, guarded so an immaterial denominator shows `n/a` rather than a nonsense percentage; current and deferred tax; project WIP; landed cost, credit and debit notes, TDS 194C, dunning, retention reclassification, gratuity provision, four assets including CWIP and an intangible.

## 8. GST, HR and mail

- **GST** — company and all parties carry GSTIN, state and category; every invoiced item has an HSN; intra-state and inter-state invoices both present; MCA audit trail on and non-disableable; four suppliers tagged Micro/Small with Udyam numbers feeding the MSME report. GSTIN check digits and pincode-to-state are validated on entry.
- **HR** — 6 employees, holiday list, 150 attendance records, leave, expense claim, salary structure and submitted salary slips; Gratuity Rule and provision. **The biometric pull is switched off** — 72 punches and the reconciliation report are real, the automation behind them is not running.
- **Mail** — live via Purelymail on `uattech@carobar.net`; SPF, DKIM and DMARC all pass at Gmail. The daily summary goes at **08:30** and the AI briefing at **08:35**, both Asia/Kolkata, driven by a cron server script rather than Frappe's midnight job.

**Indian dates.** MariaDB runs UTC inside the container while the site runs Asia/Kolkata, so every raw-SQL `curdate()` was comparing against the previous day for 5.5 hours out of 24. All custom reports use `date(convert_tz(utc_timestamp(),'+00:00','+05:30'))`, and the harness fails if any new report does not. Not cosmetic: the MSMED 45-day clock hangs off it.

## 9. Deploying, and the trap in it

**Read this before installing or upgrading anything.**

Installing or upgrading the app **re-imports its configuration and overwrites the database**. Proved by experiment: a workflow role changed in the database was reset to the packaged value by a plain `bench migrate`.

Two consequences:

1. **Deploying from a stale copy reverts business rules** to whatever that copy contained. This happened: an install from a stale container copy moved PCC approval back to System Manager and BRM certification back to Purchase Manager. Everything still worked, all 23 checks still passed, and nothing said a word.
2. **Anything changed through the ERPNext screens is reverted at the next upgrade.** Business rules live in git.

**The guard.** After every install and migrate, six control transitions are verified and repaired, with a banner and an Error Log entry naming each one. A banner means the package and the agreed configuration have diverged — reconcile them, do not just note it. `test-stale-deploy.sh` reproduces the whole thing.

### The check that found the silent failure

**`T9f` — has each enabled MSCAST scheduled job actually run?** Not "is it configured", not "is the scheduler alive", but does it have a real `last_execution`. Every other check asked the first question and all of them passed while four jobs had never executed. T9f failed the moment it was written, naming the monthly archival job. All five have since been enqueued through the real scheduler path and picked up by a worker.

### The two expected warnings

`T6d` asserts the approval matrix. Two further checks ask whether the separation of duties is real, from two different angles, and **both warn on purpose**. Neither is a defect to chase; both are positions somebody has taken.

- **`T6e` — can an ordinary user both raise and approve the same document?** Yes, for the PCC and the kick-off: both directors hold the preparing roles as well as the director role, so either can prepare and approve alone. Accepted for a company this size, and documented in the SOPs.
- **`T6f` — does anyone outside the administrators hold `System Manager`?** Currently no. It warns if that changes.
- **`T6g` — can one person *create* a document and then approve it?** Yes, and this is the one worth understanding. `T6e` compares workflow *transition* roles, but creating a document is a permission, not a transition. Both directors hold `Projects Manager`, which can create a BRM; `MSCAST Director`, which certifies one; and `Accounts Manager`, which marks it paid. **A director can therefore take a supplier bill from creation to paid alone.** `T6e` never saw it, because "prepare a BRM" is not a workflow transition at all.

`T6g` was added on 20 September after three delivered documents were found claiming a separation that does not exist. The documents have been corrected. **The payment block itself is unaffected** — no certified BRM, no payment, for anyone, including a director. It was moved out of a Server Script and into the app on 21 September, after a probe found three routes round it; see `T6a`.

## 10. What is not production yet

- Demo data throughout; the watermark on client-facing prints
- The Administrator password must be rotated before real data goes on a server
- Previous-year comparatives are blank until Tally opening balances are migrated
- Biometric attendance pull switched off
- Hosting: VPS in India, HTTPS, daily India-resident backups (Companies (Accounts) Rules r.3(5))
- The AI briefing points at a model router on this laptop; a server needs a hosted endpoint — three config lines, no code change
- **`reset-poc.sh` was run end to end on 21 September, and it does not reproduce the demo data.** The result was 23 PASS, 3 WARN, 5 FAIL of 31, against 29/2/0 on the live site. Two causes:

  - *Fixed.* The compose `create-site` step installs **only** `erpnext`. The other four apps had been installed by hand and never written down, so 83 seed steps failed on tables that did not exist. `reset-poc.sh` now installs all four in dependency order and aborts if any is missing.
  - *Not fixed, and a known limitation.* With all six apps present, 76 seed steps still failed in a cascade — masters created by scripts numbered 150+ are referenced by scripts numbered 25. The seed scripts are a record of how this POC was explored, not a designed build order, which is also why a dozen of them are named `*_fix`, `*_fix2`, `*_fix3`.

  **What reproduces and what does not.** Every *configuration* check passed on the rebuilt site — 28 reports, 5 workflows, print formats, roles and permissions, the BRM payment control, the approval matrix (T2, T6b, T6c, T6d, T6h, T6i, T6j, T7b). Every failure was *data*. So the app and its fixtures do reproduce the system; the demonstration dataset does not replay. A production install wants the former and not the latter.

  **Use the right mechanism for each.** A fresh MSCAST system: create the site, install the six apps, let the fixtures configure it. *This* system with its data: restore a backup — tested the same day, restored into a separate site and passed all 31 checks identically, and put the live demo back in under three minutes when the rebuild broke it.

- **The permission matrix now ships in the app** (`mscast_erp.controls.permissions`, run on every install and migrate). Before 21 September it lived in seed 183, so a real install never got it, and 183 itself was wrong: inserting one custom permission row replaces *all* of a doctype's standard rows, and on five doctypes every other role lost access - the managing director, named as kick-off approver, could not open a kick-off. Checks `T6k` (whoever can approve can open) and `T6l` (no role silently dropped) now guard it.
- **Restores carry the encryption key.** A restore on 21 September brought the data back under a different key; mail stopped and nothing said so. `restore-key.sh`, and check `T9g`.
- **Backups are now tested, not asserted.** `backup-out.sh` copies a set out of the Docker volume onto `D:` — which matters, because `reset-poc.sh` runs `docker compose down -v` and the backups live *in* that volume. `restore-test.sh` then restores into a separate site and the harness is run against it. Two defects in the restore path were found only by doing it: the db root password is in `compose.yaml` as `MYSQL_ROOT_PASSWORD`, not in `common_site_config.json`, and `--no-mariadb-socket` is deprecated in favour of `--mariadb-user-host-login-scope`

Six accounting and scope assumptions are still awaiting MSCAST and the CA. They are listed in the implementation report and written into the narration of the affected vouchers, so whoever reviews the books meets the assumption where it matters.

## 11. Suggested 15-minute walkthrough

1. **Workspace** `/app/mscast` — KPIs and charts on one screen
2. **MSCAST Exception** — what the overnight checks found this morning
3. **MSCAST Project Kickoff** for PROJ-0002 — the checklist, parked in *PO Query Raised*
4. **Project MIS** — contract vs PCC vs committed vs billed
5. **PCC-2026-00001** — the cost sheet; print it
6. **PO vs PCC Variance** — what is committed against the estimate
7. **A Drawing in Draft** — try to release it for manufacture; the system will not offer it
8. **Drawing register + Transmittal** — revision history and what was issued, acknowledged
9. **Free Issue at Vendor** — material lying with the fabricator
10. **BRM** — then try a Payment Entry against an uncertified bill and watch it refused
11. **MDM → Delivery Instruction** — print shows the dispatch list and Annexure-I
12. **Commissioning report and spares handover** — print both
13. **MSME 45-Day Dues** and **Daily Management Summary**
14. **Schedule III balance sheet and P&L**, then **Project Closure Report**
15. **Run the harness** — 34 checks, 32 pass, 2 expected warnings

## 12. Files

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
  ERP Plan\                      the documents, .docx plus markdown under markdown\
~/mscast-poc\                    compose.yaml, apps.json, frappe_docker checkout (inside WSL)
```

Everything in `_archive\` can be deleted without affecting the POC or a rebuild.

**Current documents.** `ERP Plan\` holds the .docx and markdown; the ERP-MSCAST project on claude.ai holds the same content. *Client Setup Guide v2.2* · *SOPs and Use Cases v2.1* · *Role Cards v1.2* · *Production Cutover Runbook* · *Independent Review* · *Requirements Traceability* · *Implementation Report* · *Data Request Covering Note*.
