#!/usr/bin/env bash
# WARNING: destroys the POC database and rebuilds it from every seed script (~25 min).
# The order below is documented in D:\MSCAST\erpnext-poc\REBUILD.md
set -euo pipefail
cd "$HOME/mscast-poc"
read -r -p "Wipe the MSCAST POC and rebuild? [y/N] " a
[ "$a" = "y" ] || exit 1

# The stack runs mscast/erpnext:v16-app - the base image with mscast_erp baked in.
# It has to exist before the containers start, because `apps/` comes from the
# image and only `sites` and `logs` are volumes. When the app was missing from
# the image, the scheduler and the queue workers could not import it at all and
# four of the five MSCAST scheduled jobs silently never ran.
IMG=$(grep -m1 -oE 'mscast/erpnext:[A-Za-z0-9._-]+' compose.yaml)
if ! docker image inspect "$IMG" >/dev/null 2>&1; then
  echo "image $IMG is missing - building it first"
  bash /mnt/d/MSCAST/erpnext-poc/scripts/build-mscast-image.sh "$IMG"
fi
echo "using image: $IMG"

docker compose -p mscast-poc -f compose.yaml down -v --remove-orphans
docker compose -p mscast-poc -f compose.yaml up -d

echo "waiting for site creation (several minutes)..."
for i in $(seq 1 60); do
  s=$(docker inspect -f '{{.State.Status}}:{{.State.ExitCode}}' mscast-poc-create-site-1 2>/dev/null || echo none)
  case "$s" in exited:0) break;; exited:*) echo "site creation failed: $s"; exit 1;; esac
  sleep 20
done

# server scripts (BRM payment block, scheduled jobs) will not install without this
echo "enabling server scripts..."
docker exec mscast-poc-backend-1 bash -c \
  'cd /home/frappe/frappe-bench && bench set-config -g server_script_enabled true'
docker restart mscast-poc-backend-1 mscast-poc-queue-short-1 \
                mscast-poc-queue-long-1 mscast-poc-scheduler-1 >/dev/null
sleep 25

R=/mnt/d/MSCAST/erpnext-poc/scripts/run-seed.sh

bash $R 00_setup_wizard 01_company_masters 02_custom_doctypes 03b_transactions 04b_reports_workspace
bash $R 05_gst_setup 05b_gst_fix 12_gst_pi 13_gst_pi2
bash $R 06_hr_payroll 06b_hr_fix 06c_hr_fix2 06d_hr_fix3 06e_hr_fix4 06f_hr_fix5
bash $R 17_payroll_fix 18_statutory 19_statutory2 20_payroll_final
bash $R 07_print_formats 21b_branding_dashboard 22_polish
bash $R 25_gapfill 26_gapfill2 27_gapfill3 28_gapfill4
bash $R 29_assets 30_assets2 31_assets3 32_assets4
bash $R 40_batch_a 41_batch_a2 42_batch_a3 43_dunning
bash $R 44_batch_b 45_batch_b2 47_cwip_asset2 48_asset_tidy
bash $R 51_batch_c1 53_batch_c2b 54_batch_c3 55_batch_c3b
bash $R 56_batch_c4 57_batch_c4b 58_batch_c4c
bash $R 61_email_account 62_email_digest 68_email_incoming 69_mail_polish 70_footer_flag
bash $R 73_send_summary2 76_demo_user_mail 77_nobounce2 78_notify_recipients
bash $R 80_summary_v2 81_summary_fix 82_ist_dates 87_morning_batch2
bash $R 90_gaps_config 91_tax_wip_gst 92_schedule3 93_schedule3_fix
bash $R 97_schedule3_v4 98_ppe_fix 99_ppe_split
bash $R 100_biometric_scaling 101_workflows_users
bash $R 103_test_fixes 104_notes_accounts 105_data_fixes
# --- the MSCAST home page, role-scoped navigation and desk theme ---
bash $R 112_home_api 114_home_block 115_workspaces 116_fix_bounce
bash $R 119_default_workspace 123_desk_redirect
bash $R 127_exception_engine 128_demo_safeguards 129_shareholder_names
# --- a fuller MSCAST: more of the business, real people, a job at each stage ---
bash $R 150_masters_expand 151_installed_and_bids 155_project_three
bash $R 153_real_users 154_fix_approvals
bash $R 156_repair_after_expand 158_notif_roles 159_mail_reachable
# --- segregation of duties: preparers prepare, the two directors approve ---
bash $R 161_approval_authority 172_drawing_workflow
bash $R 127_exception_engine 179_exception_doctype_align 181_admin_cutback 182_no_operational_admins
bash $R 10_test_reports 102_test_harness

cat <<'NOTE'

Rebuild finished. Manual steps that remain:
  1. Enter the mail password at http://localhost:8080/app/email-account/mscast-test
  2. Re-check the harness above - it should read 25 PASS, 1 WARN, 0 FAIL of 26.
     The one warning is known, not a defect:
       T6e both directors can prepare and approve a PCC and a kick-off.
           An accepted position for a company this size - see the SOPs.
  3. If this site will run the agent, install the app so the 08:35 job is
     registered, and set who receives it:
        bench --site <site> install-app mscast_erp
        bench --site <site> set-config mscast_briefing_to '["a@x","b@y"]'
NOTE
