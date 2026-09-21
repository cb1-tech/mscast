# MSCAST ERP

ERP for **MSCAST Engineering Pvt Ltd** (Pune, continuous-casting machines), built on **ERPNext v16** (Frappe v16) with India Compliance, Frappe HR and India Payroll, plus MSCAST's own app `mscast_erp`.

- MSCAST's requirement document lists 97 requirements; all 97 are built. 23 further additions (safeguards, backups, automation) make it a working system. Both lists are in `ERP Plan/MSCAST ERP - Requirements Traceability Matrix.xlsx`.
- 42 automated build checks run every night against the running system.

## What is in this repository

| Folder | Contents |
|---|---|
| `mscast_erp/` | The Frappe app: MSCAST's forms (25 doctypes), 28 reports, 15 print formats, workflows, the payment and approval controls, permissions, scheduled jobs. Every setting ships here as fixtures or code; nothing lives only in a database |
| `erpnext-poc/` | How the system is built and run in Docker: `apps.json` (the base image's apps), `Containerfile.mscast` (bakes `mscast_erp` into the image), `compose.yaml`, `scripts/` (build, install, backup, restore, checks) and `seed/` (demonstration data and the build checks, `seed/102_test_harness.py`). Technical manual: `erpnext-poc/README.md` |
| `ERP Plan/` | The project documents (Word). `ERP Plan/markdown/` holds the same documents as markdown, the editable source |

Not in the repository (see `.gitignore`): database backups, site data and site config (they hold client data and keys).

## Install

**On any Frappe v16 bench** (the portable path, used for production):

```bash
# the four upstream apps, branch version-16 (listed in erpnext-poc/apps.json)
bench get-app erpnext --branch version-16
bench get-app hrms --branch version-16
bench get-app https://github.com/resilient-tech/india-compliance --branch version-16
bench get-app https://github.com/frappe/india-payroll --branch version-16

# MSCAST's app, from a tagged release of this repository. The app sits in a
# subfolder, so `bench get-app` cannot fetch it; install it the way the image does
# (erpnext-poc/Containerfile.mscast). Run from the frappe-bench folder:
git clone <this repository> /opt/mscast && git -C /opt/mscast checkout <release tag>
cp -r /opt/mscast/mscast_erp apps/mscast_erp
./env/bin/pip install --editable apps/mscast_erp
grep -qx mscast_erp sites/apps.txt || echo mscast_erp >> sites/apps.txt
ln -sfn "$PWD/apps/mscast_erp/mscast_erp/public" assets/mscast_erp   # the MSCAST theme and logo

bench new-site <site> --install-app erpnext
bench --site <site> install-app india_compliance hrms india_payroll   # dependency order
bench --site <site> install-app mscast_erp
bench set-config -g server_script_enabled true
bench --site <site> set-config server_script_enabled true
bench --site <site> set-config host_name https://<public-address>
bench --site <site> enable-scheduler
bench --site <site> migrate
```

The full, ordered procedure, with sizing, backups and cutover, is `ERP Plan/MSCAST ERP - Production Cutover Runbook.docx` (section 2).

**With Docker** (how the POC runs):

1. Build the base image with [frappe_docker](https://github.com/frappe/frappe_docker)'s layered build from `erpnext-poc/apps.json` (`scripts/build-base-image.sh`; set `FRAPPE_DOCKER` to your frappe_docker checkout).
2. Build the app image: `scripts/build-mscast-image.sh` → `mscast/erpnext:v16-app`.
3. Start the stack from `erpnext-poc/compose.yaml`.
4. Create a clean MSCAST site with `scripts/new-mscast-site.sh <site>`. It installs the apps and MSCAST's configuration (no demo data) and refuses to report success unless 19 system checks pass.

## Settings a backup does not carry

A database backup restores the data but not these three settings. Set them on every new machine:

- `encryption_key`: from the backup's `site_config_backup.json` (`scripts/restore-key.sh`). Without it, saved passwords such as the mail account's cannot be read.
- `server_script_enabled`: bench-wide. Without it, MSCAST's scheduled jobs and home page are silently off.
- `host_name`: the public address. Without it, links in emails do not open.

## Known limits of the helper scripts

The scripts in `erpnext-poc/scripts/` were written for the machine the POC was built on. Before using them elsewhere, check and adjust:

- **Paths:** many assume the repository is at `/mnt/d/MSCAST`, and the running compose project is in `~/mscast-poc` (DEV in `~/mscast-dev`).
- **Names:** containers `mscast-poc-*` and `mscast-dev-*`, site `frontend`, ports 8080 and 8081. Several scripts accept `C=<backend container>` and `SITE=<site>`.
- **Windows-only pieces:** `demo-up.ps1`, `tunnel-add-dev.ps1` (Cloudflare tunnel) and the nightly backup (a Windows scheduled task running `nightly.sh`).
- **Demo data does not replay from scratch.** The `seed/` scripts are the record of how the demonstration data was made. To get the demo system, restore a backup (see `erpnext-poc/REBUILD.md`).

The `bench` install path above has none of these limits.

## Documents

| Document | For |
|---|---|
| Strategy and Phased Plan · Research Appendix | Why ERPNext, the options assessed, the roadmap |
| Requirements Traceability (+ the .xlsx workbook) | Each MSCAST requirement → how it is met → where to see it |
| Implementation Report | What exists today, in one page |
| Client Setup Guide · Production Cutover Runbook | Setting it up for real use; moving to production |
| SOPs and Use Cases · Role Cards · Operating Recommendations | How MSCAST's staff use it day to day |
| Independent Review | Everything reviewers and testing found, and its status |
| Data Request Covering Note · Demo Run-sheet | What MSCAST still has to send; the demo walkthrough |
