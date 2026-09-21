# Getting an MSCAST system

Three ways, depending on what you need. Script paths and container names are those of the build machine; see "Known limits of the helper scripts" in the root README.

| You need | Do this | Time |
|---|---|---|
| **A clean system** (production: MSCAST's configuration, no demo data) | `scripts/new-mscast-site.sh <site>`, or the `bench` steps in the root README | ~10 min |
| **The demonstration system** (with its demo data) | Restore a backup: `scripts/restore-test.sh <backup dir> [site]` into a new site, or `scripts/restore-live.sh <backup dir>` over the running one (destructive) | ~3 min |
| **A DEV copy** beside the live one (own database, port 8081) | `scripts/dev-create.sh [backup dir]` | ~10 min |

## After any restore

A backup carries the data, not these three settings. The scripts above set them; if you restore by hand, set them yourself:

- `encryption_key`: `scripts/restore-key.sh <backup dir> [site]` copies it from the backup's `site_config_backup.json`. Without it, saved passwords (the mail account's) cannot be read.
- `server_script_enabled`: `bench set-config -g server_script_enabled true`. Without it, MSCAST's scheduled jobs and home page are silently off.
- `host_name`: `bench --site <site> set-config host_name https://<public-address>`. Without it, email links do not open.

Then run the build checks: `scripts/run-harness.sh [site]` (prefix `C=<backend container>` for another stack). A demonstration copy passes 40 of 42, with 2 warnings that wait on MSCAST's answers to Q20 and Q21.

## On a clean system, before real use

- Enter the outgoing mail account's password (Email Account). It is never stored in the repository.
- Load MSCAST's masters and opening balances: Client Setup Guide, steps 1–10.

## The seed scripts

`seed/` holds the numbered scripts that created the demonstration data, in the order they were written. They are a record, not a supported rebuild: `scripts/reset-poc.sh` replays them, but tested on 21 September 2026 it did not reproduce the demo data (the configuration it did reproduce comes from the app). Use a backup for the demo system.

`seed/102_test_harness.py` is not demo data: it is the 42 build checks.
