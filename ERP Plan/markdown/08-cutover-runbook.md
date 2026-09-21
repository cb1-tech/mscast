---
title: "MSCAST ERP — Production Cutover Runbook"
---

# MSCAST ERP — Production Cutover Runbook

**For:** MSCAST Engineering Pvt Ltd · **Target:** self-managed VPS in India · **Version:** 3.0 · **Date:** 21 September 2026

Purpose: the steps from the POC (running on the implementer's laptop in Japan) to MSCAST running its business on a production server. Everything assumes the `mscast_erp` app (repository github.com/cb1-tech/mscast): the whole configuration installs as a package, never by hand.

---

## 0. What the server must satisfy

Rows 1–3 are legal requirements.

| Requirement | Source | In practice |
|-----------------------|-----------------------|-------------------------------------------------------|
| Books accessible in India | Companies (Accounts) Rules, r.3(5) | Server **and** daily backups physically in India. A backup in Singapore does not satisfy it. |
| Eight-year retention | Companies Act, s.128(5) | Monthly backups kept 8 years; cannot be rotated away after a year. Budget storage for 8 years of monthlies. |
| Audit trail always on | MCA audit-trail rule, from 1 Apr 2023 | The auditor must be able to say it was operative and untampered all year: control who has database and console access, not only the setting. |
| HTTPS with a real certificate | — | The POC's Cloudflare tunnel terminates TLS; a VPS does not. Use Let's Encrypt with auto-renewal. |

---

## 1. Sizing

- POC today: ten containers on an 8 GB WSL allocation, not strained.
- Production (real data, up to 10 concurrent users): **4 vCPU, 8 GB RAM, 100 GB SSD**. Leaves room for database growth and for backups to stage locally before going off-site.
- Minimum: 2 vCPU / 4 GB runs it, but MariaDB + five Frappe apps + scheduler leave no headroom when a report and a payroll run coincide.
- Storage grows mainly from attachments (drawings, scanned bills, PDFs). Size it on MSCAST's document volume, not transaction count.
- **Providers to quote** (Indian regions, self-managed): AWS Mumbai, DigitalOcean Bangalore, Akamai/Linode Mumbai, E2E Networks, CtrlS. Get current quotes; re-test the ERPens proposal's ₹10,000/month AWS line against actual need.
- **Decision: self-managed.** Managed Frappe hosting in Mumbai costs more per month but would take patching, backup verification and upgrade breakage off a single implementer in another time zone. The operational load in sections 3–6 is the cost of the self-managed choice.

---

## 2. Build the server

1. Provision the VPS in an Indian region, Ubuntu LTS.
2. Harden first: SSH keys only, root login disabled, `ufw` allowing 22, 80, 443, automatic security updates on, a non-root user for the stack.
3. Install Docker and the compose plugin.
4. Copy `compose.yaml` from the POC. Change only: image tag, domain, and ports behind a reverse proxy instead of a tunnel.
5. Bring up the stack with an **empty site**, not a copy of the POC database. Nothing from the POC carries across (no demo data, no demo users) except the configuration, which arrives as the app.
6. Install from a **tagged release**, never a copied folder (see section 5):

```bash
git clone git@github.com:cb1-tech/mscast.git
cd mscast
git checkout v1.0.0            # the release being deployed. Write it down.
git rev-parse --short HEAD     # record this in the deployment log

bench get-app ./mscast_erp
bench new-site erp.mscast.co.in --install-app erpnext
bench --site erp.mscast.co.in install-app india_compliance hrms india_payroll
bench --site erp.mscast.co.in install-app mscast_erp
bench set-config -g server_script_enabled true   # bench-wide: a restore does NOT carry it
bench --site erp.mscast.co.in set-config server_script_enabled true
bench --site erp.mscast.co.in set-config host_name https://erp.mscast.co.in   # else emailed links say http://<container>
bench --site erp.mscast.co.in enable-scheduler     # new sites start with it OFF
bench --site erp.mscast.co.in migrate
```

- **Install order is a dependency order:** `india_payroll` extends `hrms`; `mscast_erp` carries `india_compliance`'s custom fields.
- **Installing `mscast_erp` installs the permission matrix** (roles, the auditor's read-only access, the kick-off checklist). No setup script is needed.
- **`erpnext-poc/scripts/new-mscast-site.sh` does all of the above**, then runs the system build checks; it reports success only if all **19** pass. Tested 21 September 2026 on an empty site.
- **Never set `mscast_demo` on a production site.** It stamps DEMONSTRATION on every print; on any other site the app removes the mark. Check `T4b` fails if a production print carries it.
- **Three settings live outside the database; a restore does not carry them:**
  - `server_script_enabled` — also bench-wide (`common_site_config.json`). Without it every MSCAST server script (home page, BRM rules, morning batch) is off while everything else works. Check `T1c`.
  - `host_name` — makes email links use the public address; without it they point at the container's internal name and do not open. Check `T9i`.
  - `encryption_key` — see section 3.

7. **Read the output of `install-app mscast_erp` and `migrate`.** Expected:

```
mscast_erp: 26 document definitions synced
mscast_erp: NN configuration records imported, 0 could not be
mscast_erp: permission matrix verified, no change
mscast_erp: workflow guards verified
mscast_erp: approval authority verified, 6 transitions correct
```

   - Any line saying **REPAIRED** or **applied** on a second run: the package and live configuration disagree. Reconcile before the next deploy.
   - A row of exclamation marks and *"THE DEPLOY CHANGED WHO MAY APPROVE"*: stop and read section 5.
   - `Deleting entity Workspace MSCAST ...` during migrate is expected; `after_migrate` recreates the workspaces. Not a failure.

8. **Prove every container can import the app.** `apps/` comes from the image; only `sites` and `logs` are volumes. An app present in one container only gives HTTP 500 on the web and silent non-running scheduled jobs, while `bench console`/`bench execute` (fresh python each time) and the build checks still pass. Install with `bench get-app` as above, or deploy an image that carries the app, then:

```bash
# every container, not just the one you happen to be in
for c in backend scheduler queue-short queue-long; do
  docker exec <project>-$c-1 bash -c \
    'cd /home/frappe/frappe-bench && ./env/bin/python -c "import mscast_erp"' \
      && echo "$c ok" || echo "$c CANNOT IMPORT THE APP"
done
```

9. HTTPS: Let's Encrypt via the reverse proxy, renewal on a timer, alert if renewal fails. An expired certificate takes the business offline.
10. Run the build checks before telling anyone the site exists. Expect **42 checks: 40 pass, 2 expected warnings (T6e, T6g — awaiting MSCAST's answers to Q20/Q21), 0 fail.** Anything else is a stop. Warnings explained in doc 06 (SOPs), Part C, and doc 03 (Q20/Q21).

---

## 3. Backups

- **Daily** database + files: `bench backup --with-files`, scheduled.
- **Off the server**, to India-resident object storage. A backup on the same disk is not a backup.
- **Retention:** dailies rotate at 30 days; **monthlies kept 8 years** (s.128(5)).
- **Encrypted at rest** (salary data, customer commercials).
- **The site's `encryption_key` travels with every backup and is protected like a password.**
  - It lives in `site_config.json`, outside the database; Frappe encrypts every stored secret (mail passwords, API keys) with it.
  - `bench restore` keeps the target site's key, so a restore without the original key leaves mail silently stopped.
  - `restore-key.sh` puts the key back. Check `T9g` fails if any stored secret cannot be decrypted.
- **A failed backup must reach a person.**
  - Nightly job: backup + all build checks; emails `mscast_alerts_to` if either fails.
  - Watchdog inside the ERP emails the same address if the nightly job has not run for 26 hours.
  - Set `mscast_alerts_to` in production; send a test alert with `SIMULATE_FAIL=1` and confirm it arrives.
- **The nightly job refuses to bless a backup set if the site cannot decrypt its own secrets** (an intact archive can still be unusable).
- **Restore test** before go-live, then annually. Record the actual time from backup to working system.
- **Before every install or upgrade**, take a backup; restore it if the checks fail.

---

## 4. Monitoring

Failures here are silent, so each item needs an active check:

- Site answering (uptime check from outside).
- **Each MSCAST job has actually run:** `last_execution` on every Scheduled Job Type, not only "scheduler process alive". An enabled, correctly scheduled job with `last_execution = NULL` is the failure to watch for. Check `T9f`.
- **Scheduler running.** If it stops, the daily summary, overnight checks, morning note and all notifications stop. Put the scheduler check on the daily summary itself, so a missing email is the signal.
- **Morning note actually sent:** check the Email Queue, not only that the job ran.
- **Error Log entry "approval authority repaired after deploy"** — a deploy changed who may approve. See section 5.
- Disk above 80%.
- Last night's backup completed and left the server.
- Certificate expiry within 21 days.

Route all alerts to an address the implementer reads.

---

## 5. What a deploy does to the configuration

**Read before the first upgrade.**

- **Installing or upgrading the app re-imports its configuration and overwrites the database.** Tested: a workflow role changed in the database was reset to the packaged value by a plain `bench migrate`.
- Consequence 1: **deploying from a stale copy reverts business rules** to that copy (this happened in the build: PCC approval went back to a system role, BRM certification to Purchase Manager, and no check noticed).
- Consequence 2: **anything an administrator changes in the ERPNext screens is reverted at the next upgrade** (workflow role, notification recipient, print format).

**Rules**

- Business rules live in the package. An approval change goes into the repository and is deployed; never through the interface on production.
- Deploy from a tagged release. Record tag and commit hash in the deployment log (section 10).
- Never copy the application folder onto a server.

**Safety net**

- After every install and upgrade the app verifies six control transitions (the five that must sit with a director, plus drawing release) and **repairs any that are wrong**. It repairs rather than aborting, because a half-finished migrate is worse than a wrong approval role. It always reports the repair:

```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
MSCAST: THE DEPLOY CHANGED WHO MAY APPROVE. Repaired, but read this.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  - MSCAST BRM Certification / Certify was Purchase Manager, restored to MSCAST Director
  - MSCAST PCC Approval / Approve was System Manager, restored to MSCAST Director
```

- **A banner is not "handled".** The deployed package and the configuration MSCAST agreed have diverged: find out why and reconcile, or it repeats at every upgrade.
- The same assertion runs in the build checks, so drift is caught twice.

---

## 6. Keeping it patched

ERPNext v16 releases frequently; India Compliance ships GST changes on statutory deadlines. Risks: 28 custom reports in raw SQL against tables that can change, and the configuration overwrite in section 5.

**Monthly routine**

1. Restore last night's production backup onto a staging site — **with its encryption key, email muted, scheduler off.** A restored copy carries the live mail account and an enabled scheduler and would send the morning report to real people.
2. `bench update` there.
3. Run the build checks: **42 checks, 0 failures, 2 expected warnings.** `upgrade-test.sh` does steps 1–3 on a fully separate stack and tears it down afterwards.
4. Read the deploy output for an approval-authority banner.
5. Upgrade production only then, in a window MSCAST agrees, from a tagged release.
6. Re-run the checks on production. Do not announce the system available until they pass.

- **Never upgrade production directly.**
- **The app's fixtures carry only MSCAST's own records** (measured against a site built without the app), so `bench migrate` does not revert India Compliance, ERPNext or HRMS updates. Check `T6m` fails if a foreign record creeps in or an MSCAST record is left out.

---

## 7. Cutover day

Pick a month end, ideally a quarter end, so opening balances match something MSCAST already reconciles.

**The week before**

- [ ] Masters loaded and checked: customers, suppliers, items, employees (sheets 1–5 of the data collection workbook).
- [ ] Users created, roles assigned; everyone has logged in once and changed their password.
- [ ] **Setup-wizard administrator cut back to `System Manager` alone.** A fresh install gives it every role (41 in the POC); do this on every deployment.
- [ ] **No operational user holds `System Manager`** (it bypasses every control). Check `T6f`.
- [ ] Administrator password rotated (parked by the owner until real data / a real server).
- [ ] Each person has walked their own process with real-looking data, **holding their role card** (doc 09).
- [ ] The CA has signed off the accounting decisions: WIP method, tax regime, MSME rules, retention posting.
- [ ] A director has **received** the morning note (not just had it sent).

**Cutover day**

1. Close Tally for new entries. Announce the exact time.
2. Strike the trial balance as at the cutover date.
3. Load opening balances: trial balance, then receivables invoice by invoice, payables bill by bill, then stock.
4. Load open sales orders and purchase orders.
5. Reconcile: ERPNext trial balance equals Tally's to the rupee; receivable and payable totals agree invoice by invoice, not only in total.
6. Run the build checks one final time.
7. Open the system for transactions only when it reconciles.

**Rollback**

- Tally stays available and unchanged for at least one full month.
- If reconciliation fails, or something material is wrong in week one, MSCAST returns to Tally and cutover is re-planned.
- Delete or archive nothing in Tally until a month of parallel running has closed cleanly.

---

## 8. The first month

- **Parallel running:** critical transactions into both systems for one month.
- **Month-end close** in ERPNext, compared to Tally line by line.
- **Morning note read daily** for the first fortnight and the exception list cleared. An exception recurring six mornings running means a procedure is not being followed, not a document defect.
- **A named MSCAST owner** for the system (not the implementer), who answers "why is this number wrong" first.

---

## 9. Decisions needed before any of this starts

| Open item | Who answers | Why it blocks |
|---------------------------------|----------------------|---------------------------------------------|
| Real PCC, Project MIS, BRM, MDM (with DI and Annexure-I) formats | MSCAST | Every control and SOP is built on the implementer's reading of them |
| Accounting basis, tax regime (s.115BAA), WIP method | The CA | Already in the financial statements |
| EPF: confirm no continuing coverage under s.1(5) (PF is removed from payroll); ESI and gratuity applicability | The CA | Salary slips and provisions assume this |
| PCC and kick-off self-approval (Q20) | MSCAST directors | A director can prepare and approve both. Accepted and documented, but an explicit choice |
| **Director certifying a supplier bill they created (Q21)** | **MSCAST directors** | **A director holds roles that can create a BRM, certify it and mark it paid — one person, whole route, on the step that releases money. Accept explicitly, or remove `Projects Manager` from director accounts so preparing a BRM requires Purchase** |
| Suppliers to mark *Exempt from BRM certification* | MSCAST | Utilities, rent and statutory bills cannot be paid otherwise |
| Tally export for opening balances | MSCAST | Needed for cutover day steps 2–4 |
| Support arrangement and scope | MSCAST and the implementer | Documents name one person (the implementer) as owner of backups, users, upgrades and alerts, with no end date |
| Who holds System Manager and database access | MSCAST | The audit-trail claim depends on it |
| Biometric attendance pull on or off | MSCAST | Switched off; payroll assumes attendance from somewhere |

Full open-question list: see doc 03, Q-list.

---

## 10. Deployment log

Keep on the server and in the repository. Two minutes per deploy.

| Date | Tag | Commit | Who | Checks passed | Approval banner? | Notes |
|-------------|-----------|----------------|-----------|----------------|-------------------|--------------|
| | | | | | | |

If "Approval banner?" is ever anything but *no*, start investigating from that row.
