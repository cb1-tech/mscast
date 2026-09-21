---
title: "MSCAST ERP — Production Cutover Runbook"
---

# MSCAST ERP — Production Cutover Runbook

**For:** MSCAST Engineering Pvt Ltd · **Target:** self-managed VPS in India · **Version:** 2.3 · **Date:** 21 September 2026

This is the sequence from "the POC works on a laptop in Japan" to "MSCAST runs its business on this". It assumes the `mscast_erp` app — the configuration as an installable package — because nothing here works if the system can only be rebuilt by hand.

> **What changed in version 2.0.** An install during the build silently reverted the approval rules and nothing noticed. Section 2 now deploys from a tagged release, section 5a is new and covers what a deploy actually does to configuration, and the monitoring and upgrade sections check that the controls survived. This is the most important change in the document.
>
> **What changed in version 2.3.** Every step below was run for real on 21 September against a copy of the system, and four of them were wrong or missing. **The encryption key is part of the backup**: a restore without it left the mail password unreadable and mail silently stopped. **A new site starts with its scheduler off**, so no scheduled job would ever have run. **A restored staging copy sends real email** unless it is muted. And **installing the app did not install the permission matrix** - roles, the auditor's read-only access and the kick-off checklist lived in a setup script that a real install never runs; they now ship in the app. The install is scripted and self-checking (`new-mscast-site.sh`), and the build checks are now 37.
>
> **What changed in version 2.2.** The POC's own app was never in its image. `apps/` comes from the image and only `sites` and `logs` are volumes, so an app copied into one container existed in that container alone. The web workers could not import it — the site served HTTP 500 on every request while every build check passed — and neither could the scheduler or the queue workers, so **four of the five scheduled jobs had never run once**. Section 2 now builds the image with the app baked in, section 4 monitors whether jobs actually execute, and a new check, `T9f`, asks whether each one has a real `last_execution`. The build checks are now 28.
>
> **What changed in version 2.1.** The build checks went from 25 to 27 and now report **two** expected warnings rather than one. The second, `T6g`, found that a director can create a supplier-bill certificate, certify it and mark it paid alone — a separation three documents had claimed existed. Section 8 carries the decision to MSCAST. The administrator-account item in section 6 is closed, and the figure in it was wrong: the account held 41 roles, not fourteen.

---

## 0. What the server has to satisfy

Three of these are legal requirements, not preferences.

| Requirement | Where it comes from | What it means in practice |
|---|---|---|
| Books accessible in India | Companies (Accounts) Rules, r.3(5) | The server and its daily backups are both physically in India. A backup in Singapore does not satisfy it. |
| Eight-year retention | Companies Act, s.128(5) | Backups older than a year cannot be rotated away. Plan the storage cost for eight years of monthlies. |
| Audit trail always on | MCA audit trail rule, from 1 Apr 2023 | The auditor must be able to say it was operative and untampered all year. That means controlling who has database and console access, not just leaving the setting on. |
| HTTPS with a real certificate | — | The POC's Cloudflare tunnel terminates TLS for you. A VPS does not: Let's Encrypt with auto-renewal. |

---

## 1. Sizing

The current POC runs ten containers on an 8 GB WSL allocation and does not strain it. With real data and up to ten concurrent users:

- **4 vCPU, 8 GB RAM, 100 GB SSD** is comfortable, with room for the database to grow and for backups to stage locally before shipping off-site.
- 2 vCPU / 4 GB will run it, but MariaDB plus five Frappe apps plus the scheduler leaves nothing spare when a report and a payroll run collide.
- Storage grows mainly from attachments — drawings, scanned bills, PDFs. Budget on MSCAST's document volume, not on transaction count.

**Providers to quote** (Indian regions, self-managed): AWS Mumbai, DigitalOcean Bangalore, Akamai/Linode Mumbai, E2E Networks, CtrlS. Get a current quote — prices move, and the ERPens proposal's ₹10,000/month AWS line should be re-tested against what is actually needed.

One thing worth pricing honestly against a VPS: managed Frappe hosting in Mumbai costs more per month but removes patching, backup verification and upgrade breakage from a one-person consultancy operating from a different time zone. The decision is self-managed, so the rest of this runbook assumes it — but the operational load below is the real price.

---

## 2. Build the server

1. Provision the VPS in an Indian region. Ubuntu LTS.
2. Harden before anything else: SSH keys only, root login disabled, `ufw` allowing 22, 80, 443, automatic security updates on, a non-root user for the stack.
3. Install Docker and the compose plugin.
4. Copy the existing `compose.yaml` from the POC. It already defines the whole stack; what changes is the image tag, the domain, and that ports are behind a reverse proxy rather than a tunnel.
5. Bring up the stack with an empty site — **not** a copy of the POC database. The POC contains demo data and demo users; nothing from it carries across except the configuration, which arrives as the app.

**Deploy from a tag, never from a copied folder.** This is not pedantry — see 5a.

```bash
git clone git@github.com:cb1-tech/mscast.git
cd mscast
git checkout v1.0.0            # the release being deployed. Write it down.
git rev-parse --short HEAD     # record this in the deployment log

bench get-app ./mscast_erp
bench new-site erp.mscast.co.in --install-app erpnext
bench --site erp.mscast.co.in install-app india_compliance hrms india_payroll
bench --site erp.mscast.co.in install-app mscast_erp
bench --site erp.mscast.co.in set-config server_script_enabled true
bench --site erp.mscast.co.in enable-scheduler     # new sites start with it OFF
bench --site erp.mscast.co.in migrate
```

**Never set `mscast_demo` on a production site.** It is the switch that stamps DEMONSTRATION on every print; on any other site the app actively removes the mark, and check `T4b` fails if a production print carries it.

The order of the four `install-app` steps is a dependency order, not a preference: `india_payroll` extends `hrms`, and `mscast_erp` carries `india_compliance`'s custom fields. `erpnext-poc/scripts/new-mscast-site.sh` does all of this and then runs the build checks that measure the system itself; it refuses to report success unless all thirteen pass. Tested 21 September on an empty site.

**Read the output of the last two commands.** They should end with:

```
mscast_erp: 26 document definitions synced
mscast_erp: NN configuration records imported, 0 could not be
mscast_erp: permission matrix verified, no change
mscast_erp: workflow guards verified
mscast_erp: approval authority verified, 6 transitions correct

Any line that says **REPAIRED** or **applied** on a second run means the package and the live configuration disagree - reconcile before the next deploy.
```

If instead you see a row of exclamation marks and *"THE DEPLOY CHANGED WHO MAY APPROVE"*, stop and read section 5a before going further. The system will have repaired itself, but something is wrong with what you deployed.

A migrate also prints `Deleting entity Workspace MSCAST ...` partway through and then recreates them in the `after_migrate` step. That is expected and self-healing; it is not a failure.

6. HTTPS: Let's Encrypt via the reverse proxy, with renewal on a timer and an alert if renewal fails. A certificate that silently expires takes the business offline on a Sunday.

7. Run the build checks before telling anyone the site exists. Expect **37 checks, 0 failures**. Two warnings are expected and documented (see the SOPs, Part C, and Q20/Q21 in the traceability matrix). Anything else is a stop.

**A note on the image, learned the hard way.** In the POC the application was not in the image at all — it had been copied into the running backend container by hand. Because `apps/` comes from the image and only `sites` and `logs` are volumes, that gave the app to exactly one container. The web workers could not import it, so the site returned HTTP 500 on every request while every script and every build check passed, because `bench console` and `bench execute` spawn a fresh python each time. Worse, the scheduler and both queue workers could not import it either, so the 06:00 exception sweep, the 08:35 briefing and the monthly archival **had never executed once**. They worked perfectly when run by hand, which is how they were built and demonstrated.

On a server, install the app properly with `bench get-app` as above, or deploy an image that carries it. Then prove it, because "installed" and "runs" are different claims:

```bash
# every container, not just the one you happen to be in
for c in backend scheduler queue-short queue-long; do
  docker exec <project>-$c-1 bash -c \
    'cd /home/frappe/frappe-bench && ./env/bin/python -c "import mscast_erp"' \
      && echo "$c ok" || echo "$c CANNOT IMPORT THE APP"
done
```

---

## 3. Backups

The part most likely to be skipped and most likely to matter.

- **Daily** database and file backups, `bench backup --with-files`, scheduled.
- **Off the server**, to India-resident object storage. A backup on the same disk is not a backup.
- **Monthly copies kept for eight years** (s.128(5)). Dailies can rotate at 30 days; monthlies cannot.
- **Encrypted at rest**, because they contain employee salary data and customer commercials.
- **The site's `encryption_key` travels with every backup, and is protected like a password.** It lives in `site_config.json`, outside the database. Frappe encrypts every stored secret with it - mail passwords, API keys. `bench restore` brings back the database and keeps whatever key the target site has, so a restore without the original key produces a system whose mail silently stops. This happened in testing on 21 September. `restore-key.sh` puts the key back; build check `T9g` fails if any stored secret cannot be decrypted.
- **A failed backup must reach a person.** In the POC the nightly job backs up, runs every build check, and emails a named address if either fails; a watchdog inside the ERP emails the same address if the nightly job has not run for 26 hours. Before this, a failed backup wrote a line to a log nobody read. Set `mscast_alerts_to` in production, and send a test alert (`SIMULATE_FAIL=1`) to prove it arrives.
- **A backup that the site cannot itself read is not a backup.** The nightly job refuses to bless a set if the site cannot decrypt its own secrets - an archive can be intact and still wrong.
- **Restore tested** before go-live, and then annually. Write down the actual time it took to get a working system from a backup — that number is what MSCAST is really buying. An untested backup is a belief, not a control.
- **Before every install or upgrade**, take one. Not as a formality — restore it if the checks fail.

---

## 4. Monitoring

Minimal, but it has to exist, because the failures are silent:

- Is the site answering? (uptime check from outside)
- **Has each MSCAST job actually run?** Check `last_execution` on every Scheduled Job Type, not just that the scheduler process is alive. This is `T9f` in the build checks, and it exists because four jobs sat at `last_execution = NULL` for the life of the POC while everything around them looked healthy. A job that is enabled, correctly scheduled and has never executed is the failure mode to watch for.
- Is the **scheduler** running? This is the one that fails quietly — the daily summary, the overnight checks, the morning note and every notification stop, and the first symptom is a director noticing the 08:30 email hasn't arrived for a week.
- **Did the morning note actually go out?** Check the Email Queue, not just that the job ran. A job that succeeds and reaches nobody is the worst kind of green light.
- **Is there an Error Log entry titled "approval authority repaired after deploy"?** If one appears, a deploy changed who may approve something. Section 5a.
- Disk above 80%.
- Did last night's backup complete, and did it leave the server?
- Certificate expiry inside 21 days.

Route all of it somewhere the implementation partner reads, and put the scheduler check on the daily summary itself so a missing email is itself the signal.

---

## 5a. What a deploy actually does to the configuration

**Read this before the first upgrade.** It is here because of something that happened during the build, not as a theoretical risk.

### What happened

The app was installed onto a working system from a directory that was slightly out of date. The approval rules silently went backwards: cost sheet approval returned to a system role, and bill certification returned to the purchase manager. The system still worked. The 23-check harness still passed, because it checked that workflows were *active and complete* and never checked *who they gave authority to*. Nobody would have noticed until an audit — or until the wrong person approved something.

### The mechanism, established by experiment

Installing or upgrading the app re-imports its configuration files and **overwrites what is in the database**. This was tested directly: a workflow role changed in the database was reset to the packaged value by a plain `bench migrate`.

Two consequences:

1. **Deploying from a stale copy reverts the business rules** to whatever that copy contained.
2. **Anything an administrator changes in the ERPNext screens is reverted at the next upgrade.** A workflow role, a notification recipient, a print format — changed in the interface, gone at the next deploy.

### The rules

- **Business rules live in the package, not in the screens.** If an approval must change, it changes in the repository and is deployed. Never through the interface on production.
- **Deploy from a tagged release.** If you cannot say which version is running, you cannot say what the approval rules are. Record the tag and the commit hash in a deployment log.
- **Never copy the application folder onto a server.** That is exactly how the stale install happened.

### The safety net

After every install and every upgrade, the system verifies six control transitions — the five that must sit with a director, plus drawing release — and **repairs any that are wrong**. It repairs rather than aborting, because a half-finished migrate is worse than a wrong approval role. But it never repairs quietly:

```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
MSCAST: THE DEPLOY CHANGED WHO MAY APPROVE. Repaired, but read this.
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
  - MSCAST BRM Certification / Certify was Purchase Manager, restored to MSCAST Director
  - MSCAST PCC Approval / Approve was System Manager, restored to MSCAST Director
```

**A banner is not "handled".** It means the package you deployed and the configuration MSCAST agreed have diverged. Find out why and reconcile them, or it repeats at every upgrade and one day the repair list will contain something the guard does not cover.

The same assertion runs in the build checks, so a drift is caught twice.

---

## 5. Keeping it patched

ERPNext v16 releases frequently and India Compliance ships GST changes on statutory deadlines. The risk is not the upgrade; it is the 28 custom reports written in raw SQL against tables that can change — and the configuration overwrite described in 5a.

A monthly routine:

1. Restore last night's production backup onto a staging site - **with its encryption key, and with email muted and the scheduler off.** A restored copy carries the live mail account and an enabled scheduler, and left alone it sends the morning report to real people.
2. `bench update` there.
3. Run the build checks. **37 checks, 0 failures**, two expected warnings. They exist precisely for this. `upgrade-test.sh` does steps 1-3 on a fully separate stack and tears it down afterwards.
4. Read the deploy output for an approval-authority banner.
5. Only then upgrade production, in a window MSCAST agrees to, from a tagged release.
6. Re-run the checks on production afterwards. Do not announce the system is available until they pass.

**What an upgrade overwrites, and why that is now safe.** `bench migrate` re-imports every fixture and overwrites the live rows. Until 21 September the app's fixtures included 663 custom fields, 344 property setters and 7 email templates that belong to India Compliance, ERPNext and HRMS, and because `mscast_erp` migrates last, our frozen copies would have reverted their updates - including GST changes India Compliance ships on statutory deadlines. One had already gone stale. The fixtures now carry only MSCAST's own records, measured against a site built without the app, and check `T6m` fails if a foreign record creeps back in or an MSCAST one is left out.

Never upgrade production directly. The harness on a staging site is the difference between finding a broken Schedule III report yourself and hearing about it from the auditor.

---

## 6. Cutover day

Pick a date at a month end, ideally a quarter end, so the opening balances line up with something MSCAST already reconciles.

**The week before**

- Masters loaded and checked: customers, suppliers, items, employees (sheets 1–5 of the data collection workbook)
- Users created, roles assigned, everyone has logged in once and changed their password
- **The setup-wizard administrator cut back to `System Manager` alone.** In the POC that account had collected **41** roles, including every manager role, on a login nobody had ever used. A fresh install creates the same thing, so this is a step on every deployment, not a one-off
- **No operational user holds `System Manager`.** It bypasses every control in this document. In the POC an ordinary staff account was found carrying it and nothing had reported it
- Each person has walked their own process on the system with real-looking data, **holding their role card**
- The CA has signed off the accounting decisions — WIP method, tax regime, MSME rules, retention posting
- A director has **received** the morning note, not just had it sent

**Cutover day**

1. Tally is closed for new entries. Announce the exact time.
2. Strike the trial balance as at the cutover date.
3. Load opening balances: trial balance, then receivables invoice by invoice, payables bill by bill, then stock.
4. Load open sales orders and purchase orders so work in progress carries across.
5. Reconcile: the ERPNext trial balance must equal Tally's to the rupee. Receivable and payable totals must agree invoice by invoice, not just in total.
6. Run the build checks one final time.
7. Only when it reconciles, open the system for transactions.

**Rollback**

Tally stays available and unchanged for at least one full month. If the reconciliation does not agree, or something material is wrong in week one, MSCAST goes back to Tally and the cutover is re-planned. Do not delete or archive anything in Tally until a month of parallel running has closed cleanly.

---

## 7. The first month

- **Parallel running.** Critical transactions go into both systems for one month. It is tedious and it is the only way to find the difference between what the system does and what MSCAST does.
- **Month-end close** performed in ERPNext and compared to Tally, line by line.
- **The morning note read every day** for the first fortnight, and the exception list cleared. Early on it finds data-entry habits, not defects — and that is exactly when to correct them. An exception appearing six mornings running means a procedure is not being followed, not that a document needs fixing.
- **A named MSCAST owner** for the system. Not the implementation partner. Someone inside the company who answers "why is this number wrong" first.

---

## 8. What still has to be settled before any of this starts

These are not runbook steps; they are decisions without which the runbook builds the wrong thing.

| Open item | Who answers | Why it blocks |
|---|---|---|
| The real PCC, BRM, MDM/DI and MIS formats | MSCAST | Every control and SOP is built on our reading of them |
| Accounting basis, tax regime, WIP method | The CA | They are in the financial statements already |
| PF, ESI, gratuity applicability | The CA | Provisions and salary slips assume them |
| Whether PCC and kick-off self-approval stays | MSCAST directors | Currently a director can prepare and approve both. Accepted and documented — but it is a live choice, not a default (Q20) |
| **Whether a director may certify a supplier bill they created** | **MSCAST directors** | **A director holds roles that can create a BRM, certify it and mark it paid. One person, the whole route, on the step that releases money to an outside party. Either accept it explicitly or take `Projects Manager` off the director accounts so preparing a BRM requires Purchase (Q21)** |
| Support arrangement and scope | MSCAST and the implementation partner | The client documents currently name one person as the owner of backups, users, upgrades and alerts, indefinitely and unpriced |
| Who holds System Manager and database access | MSCAST | The audit trail claim depends on the answer |
| Whether the biometric attendance pull is enabled | MSCAST | It is switched off. Payroll assumes attendance from somewhere |

---

## 9. Deployment log

Keep this on the server and in the repository. It is two minutes per deploy and it is the first thing anyone asks for when something is wrong.

| Date | Tag | Commit | Who | Checks passed | Approval banner? | Notes |
|---|---|---|---|---|---|---|
| | | | | | | |

If the "approval banner" column is ever anything but *no*, the row above it is where to start looking.
