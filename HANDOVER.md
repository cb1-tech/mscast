# MSCAST ERP — Session Handover

**As at:** 21 September 2026, end of session · **Owner:** Sanjay (the implementer) · **Repo:** github.com/cb1-tech/mscast (branch `main`, last commit "Live: Stores/Accounts access fix deployed…", all pushed)

Read this first in any new session. Keep it current: update it at the end of each session.

## 1. What exists

| Thing | Where | State |
|---|---|---|
| **Live POC** | https://mscast.carobar.net · local :8080 · compose project `mscast-poc` (`~/mscast-poc` in WSL) | MSCAST staff trying it with their own logins. **Build checks 40 PASS, 2 WARN, 0 FAIL** |
| **DEV** | https://mscastdev.carobar.net · local :8081 · compose project `mscast-dev` (`~/mscast-dev`) | Full demo cast, orange DEV banner, backup alerts off. 40/2/0. Use for demos, screenshots, testing |
| App | `mscast_erp/` in the repo; image `mscast/erpnext:v16-app` (both stacks). Rollback image `mscast/erpnext:v16-app-prev` | ERPNext/Frappe v16 + India Compliance, HRMS, India Payroll |
| Build checks | `erpnext-poc/seed/102_test_harness.py` (42). Run: `scripts/run-harness.sh` (prefix `C=mscast-dev-backend-1` for DEV) | The 2 warnings (T6e, T6g) clear only when MSCAST answers Q20/Q21 |
| Nightly | Windows task "MSCAST nightly backup" 02:30 JST → `nightly.sh` (backup + checks, email on failure) · watchdog 09:00 IST | Backups in `D:\MSCAST\backups` (self-pruning). DEV seed backup in `D:\MSCAST\backups-dev-seed` |
| Tunnel | Cloudflare tunnel `mscast-demo`, two hostnames. `scripts/demo-up.ps1` restores both stacks + tunnel after reboot | Screens don't auto-refresh over the tunnel (socket.io): known, parked |
| Documents | `D:\MSCAST\ERP Plan\` — `For MSCAST\` (6, shareable), `Internal\` (8), `markdown\` (sources), `demo-screens\` (41 PNGs). `ERP Plan\README.md` says which is which | Audited 21 Sep: current state only, no history. Project copies in sync |

## 2. Decisions the owner has made (do not re-ask)

- Unpaid work for a family friend; not competing with ERPens. Owner keeps the codebase in cb1-tech/mscast.
- **Nobody changes live without the owner's say-so.** Test on DEV first, then deploy to live with backup first + checks after (as done 21 Sep).
- No Administrator password rotation, no VPS move, no tunnel fix — parked until real data / a server.
- DEV: mail not muted (except backup alerts). Live: the 08:35 AI briefing goes to waseemraj@mcast.co.in (deliberate, set in `mscast_briefing_to`). Nightly alerts go to autoelectron.jp@gmail.com only.
- MSCAST's own admins (Aiqaz, Arham Chandankeri) accepted: site config `mscast_admins`. Demo biometric punches removed on live; T10c accepts "no punches yet".
- PF removed from payroll on MSCAST's instruction (under 20 staff); CA to confirm no continuing EPF coverage.
- Format preference: **bullets, short; no long essays.** Confirm before long jobs. Research/verify before asserting.

## 3. Open items

**Waiting on MSCAST** (message sent via WhatsApp with the Drive folder, 21 Sep):
- Real formats: PCC, Project MIS, BRM, MDM with DI and Annexure-I (every custom screen is our reading until then)
- Answers to Q20, Q21 (director self-approval) — the 2 standing warnings
- Suppliers exempt from the BRM rule; owners of monthly jobs; Tally export; CA contact
- Data Collection Workbook filled in

**Waiting on the CA:** B3 (MSME clock), B4 (job-work challan), B5 (WIP valuation), B7 (TDS 194C), B6 (EPF basis), s.115BAA election, Ind AS 116 lease head.

**Optional, not started:** AI showcase (invoice capture into a BRM; ask-the-books). Owner said "not now".

**Known limits:** helper scripts assume this PC's paths (`/mnt/d/MSCAST`, `~/mscast-poc`); root README says so. Making them portable was offered and declined for now.

## 4. How to work on this machine (lessons that cost time)

- Reach WSL through Desktop Commander: write a `.sh` into `D:\MSCAST\erpnext-poc\scripts\_name.sh` (underscore = scratch, git-ignored), run `wsl -d Ubuntu -- bash /mnt/d/MSCAST/erpnext-poc/scripts/_name.sh`. Delete scratch files when done.
- Run python against a site: put `seed/_x.py`, run `C=<container> SITE=frontend bash scripts/run-seed.sh _x`.
- Long jobs: `setsid nohup … & disown; sleep 20` in a launcher script, then poll the log. Never edit a script while it runs.
- Commit from WSL (git identity lives there): write the message to `erpnext-poc/_commitmsg.log`, commit, push with `GIT_SSH_COMMAND="ssh -o BatchMode=yes"`. **Check nothing secret is staged** (a site_config backup nearly reached GitHub on 21 Sep).
- Screenshots: cloud Playwright against DEV with a minted `sid` cookie (`seed/_mint.py` pattern, DEV only), `locale="en-IN"`, hide `.announcement-widget`. Clear DEV sessions afterwards (`bench --site frontend destroy-all-sessions`). Each user allows only 2 sessions — never mint on live while people are using it.
- Word files: pandoc with `mscast-ref.docx`, then strip `title=""` from `<wp:docPr>` or older Word refuses to open files with images. Weight table column widths (dash counts) or evidence columns collapse.
- Settings a restore does not carry: `encryption_key` (`restore-key.sh`), `server_script_enabled` (bench-wide), `host_name`.
- Permissions: never add a single Custom DocPerm row; declare in `controls/permissions.py` (GRANT, REPORT_USERS, FORM_NEEDS, oversight.json) and let `enforce()` write the whole set on migrate. Every fix gets a check that is seen to fail first.
- Deploy app to live: `scripts/backup-nightly.sh` → `docker tag …:v16-app …:v16-app-prev` → `scripts/deploy-app.sh` → `bench --site frontend migrate` → `run-harness.sh`.

## 5. Where to look

- Technical manual: `erpnext-poc/README.md` (also project `poc/MSCAST-ERPNext-POC-README.md`) — commands, the 42-check table, DEV section.
- Rebuild options: `erpnext-poc/REBUILD.md`. Production: `ERP Plan\Internal\… Production Cutover Runbook`.
- Status of every finding: `ERP Plan\Internal\… Independent Review` (project `review/07-…`).
