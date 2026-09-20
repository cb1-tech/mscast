# Rebuilding the MSCAST POC from scratch

`scripts/reset-poc.sh` wipes the database and replays the seed scripts below in order.
Allow roughly 25 minutes: about 8 for the containers and site creation, the rest for the seeds.

The scripts are numbered in the order they were written, and that is the order they must run in -
several later scripts correct or extend what an earlier one created. Scripts that only inspect or
print, and iterations that a later script fully replaced, have been moved to `seed/_archive/` and
are not part of the rebuild.

## Order

| Stage | Scripts | What it creates |
|---|---|---|
| Base | `00_setup_wizard` `01_company_masters` `02_custom_doctypes` `03b_transactions` `04b_reports_workspace` | Company, chart of accounts, parties, items, the 15 MSCAST doctypes, the order-to-dispatch chain, the first reports and workspace |
| GST | `05_gst_setup` `05b_gst_fix` `12_gst_pi` `13_gst_pi2` | HSN codes, tax templates, GSTIN addresses, the intra/inter-state invoices and the input-GST purchase invoice |
| HR and payroll | `06_hr_payroll` `06b_hr_fix` `06c_hr_fix2` `06d_hr_fix3` `06e_hr_fix4` `06f_hr_fix5` `17_payroll_fix` `18_statutory` `19_statutory2` `20_payroll_final` | Employees, holiday list, attendance, leave, salary structure and the August payroll run |
| Prints and branding | `07_print_formats` `21b_branding_dashboard` `22_polish` | MSCAST letterhead and print formats, logo, dark theme, KPI cards and charts |
| Gap fill | `25_gapfill` `26_gapfill2` `27_gapfill3` `28_gapfill4` `29_assets` `30_assets2` `31_assets3` `32_assets4` | MSME supplier flags, delivery note, quality inspections, bank guarantees, fixed assets |
| Batch A - accounting depth | `40_batch_a` `41_batch_a2` `42_batch_a3` `43_dunning` | COA heads, journal vouchers, landed cost, credit/debit notes, TDS 194C, dunning, payment request |
| Batch B - quick builds | `44_batch_b` `45_batch_b2` `47_cwip_asset2` `48_asset_tidy` | RFQ, proforma print, client claims, intangibles and CWIP, customer assets, share register |
| Batch C - the rest | `51_batch_c1` `53_batch_c2b` `54_batch_c3` `55_batch_c3b` `56_batch_c4` `57_batch_c4b` `58_batch_c4c` | Auditor/director roles, MSME 45-day report, transmittal, commissioning, spares, kick-off workflow, retention, supplementary invoice, gratuity, daily summary, archival job, BRM payment block |
| Email | `61_email_account` `62_email_digest` `68_email_incoming` `69_mail_polish` `70_footer_flag` `73_send_summary2` `76_demo_user_mail` `77_nobounce2` `78_notify_recipients` | Outgoing account, digest, footer, report formats, bounce protection, notification recipients |
| Daily summary | `80_summary_v2` `81_summary_fix` `82_ist_dates` `87_morning_batch2` | The 20-indicator summary, the Indian-date fix across every report, the 08:30 IST cron batch |
| Full implementation | `90_gaps_config` `91_tax_wip_gst` `92_schedule3` `93_schedule3_fix` `97_schedule3_v4` `98_ppe_fix` `99_ppe_split` `100_biometric_scaling` `101_workflows_users` | Billing schedule, receipt print, tax provisions, WIP, GST on stock, Schedule III statements, ageing, ratios, PPE opening, biometric attendance, finance scaling, workflows and department users |
| Notes and fixes | `103_test_fixes` `104_notes_accounts` `105_data_fixes` | Notes to accounts, cost-centre fill, share allocation, bank-guarantee validity |
| Verify | `102_test_harness` `59_verify` | 23 automated checks, then a full inventory |

## Two things the rebuild will not restore by itself

1. **The mail password.** `61_email_account` recreates the Purelymail account but deliberately
   leaves the password blank - open `/app/email-account/mscast-test`, enter it, save. Until then
   the steps that send mail log an error and carry on.
2. **`server_script_enabled`.** The scheduled jobs are Server Scripts (the BRM payment block is no longer one - it moved into the app on 21 September),
   which Frappe refuses to create unless the flag is set:
   ```
   docker exec mscast-poc-backend-1 bash -c 'cd /home/frappe/frappe-bench && bench set-config -g server_script_enabled true'
   docker restart mscast-poc-backend-1 mscast-poc-queue-short-1 mscast-poc-queue-long-1 mscast-poc-scheduler-1
   ```
   `reset-poc.sh` does this for you before the seeds run.

## Honest caveat

This order is derived from the order the scripts were written and run, not from an end-to-end
rebuild test - that would destroy the working POC. If you ever do run it, expect one or two scripts
to need a nudge, and note that `97` posts a fixed-asset entry that `98` then cancels and reposts,
which is correct but looks odd in the log.

## The home page, navigation and theme

Three seed scripts build the user interface layer, and `reset-poc.sh` runs them in order:

| Script | What it creates |
|---|---|
| `112_home_api` | Server Script (API) **`mscast_home_data`**. It runs the stored SQL of the *MSCAST Daily Management Summary* report and returns those indicators, the open projects with contract / PCC cost / margin / billed, and the counts behind the card badges. The page and the 08:30 e-mail therefore read the same numbers by construction. |
| `114_home_block` | Custom HTML Block **MSCAST Home** — the landing page markup, its stylesheet and the script that calls the API and renders. |
| `115_workspaces` | Turns the `MSCAST` workspace into *Home* (the block, nothing else), creates the nine role-scoped spaces, and hides the 31 stock workspaces. |

### How the desk theme is applied, and its one limit

Frappe renders a Custom HTML Block inside a **shadow root**, so the block's own
stylesheet cannot reach the rest of the desk. The block's script therefore injects
the MSCAST palette and fonts into `document.head` (ids `mscast-theme` and
`mscast-fonts`) the first time it runs. Because the desk is a single-page
application, the theme then holds for the whole session.

The limit: if somebody opens a deep link cold — a bookmark straight to a form —
without passing through Home, that tab keeps stock ERPNext styling until they do.
Home is the first workspace in the sidebar, so in practice this is rare.

**For production**, replace the injection with a one-file custom app:

```
bench new-app mscast_theme
# mscast_theme/hooks.py
app_include_css = "/assets/mscast_theme/css/mscast.css"
```

Put the same CSS in that file, add the app to the image and to `apps.txt`,
and delete the `theme()` function from the block script. The theme then loads
with every page, including cold deep links.
