#!/usr/bin/env bash
# Re-measure which configuration records the OTHER apps create by themselves, by
# building a scratch site with erpnext, india_compliance, hrms and india_payroll
# and NOT mscast_erp. Writes evidence/baseline-without-mscast.json.
#
# Run it after upgrading any of those apps: if one of them starts creating a
# record our fixtures also carry, our copy would overwrite theirs on every
# migrate. Compare with mscast_erp/fixtures - anything in both is theirs.
set -euo pipefail
C=mscast-poc-backend-1; B=/home/frappe/frappe-bench; S=baseline
R=/mnt/d/MSCAST/erpnext-poc/scripts/run-seed.sh
ROOTPW=$(grep -m1 -E '^\s*MYSQL_ROOT_PASSWORD:' ~/mscast-poc/compose.yaml | sed -E 's/.*:[[:space:]]*//')
docker exec $C bash -c "cd $B && bench drop-site $S --db-root-password '$ROOTPW' --force --no-backup" >/dev/null 2>&1 || true
docker exec $C bash -c "cd $B && bench new-site $S --db-root-password '$ROOTPW' --admin-password x$RANDOM$RANDOM --mariadb-user-host-login-scope='%' --install-app erpnext" 2>&1 | tail -1
for a in india_compliance hrms india_payroll; do echo "  $a"; docker exec $C bash -c "cd $B && bench --site $S install-app $a" 2>&1 | tail -1; done
SITE=$S bash $R 00f_fresh_setup 2>&1 | grep fresh-00
docker exec $C bash -c "cd $B && bench --site $S migrate" 2>&1 | tail -1
SITE=$S bash $R baseline_dump 2>&1 | grep -vE 'Warning|copied|====|ALL'
docker cp $C:/tmp/baseline.json /mnt/d/MSCAST/erpnext-poc/evidence/baseline-without-mscast.json
docker exec $C bash -c "cd $B && bench drop-site $S --db-root-password '$ROOTPW' --force --no-backup" >/dev/null 2>&1
echo "written: evidence/baseline-without-mscast.json"
