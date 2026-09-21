#!/usr/bin/env bash
# Create a FRESH MSCAST system: a new site with the six apps and MSCAST's
# configuration, and no demonstration data. This is the production install path.
#
# It is not reset-poc.sh. That script replays ~80 exploratory seed scripts to
# rebuild the demonstration and, tested on 21 Sep 2026, does not reproduce the
# demo data. It did reproduce every piece of configuration - because that comes
# from the mscast_erp app and its fixtures, not from the seeds. This script uses
# only that part, and then proves it.
#
# usage: new-mscast-site.sh <site>          (runs in the existing bench)
#        ADMIN_PASSWORD=... new-mscast-site.sh <site>
# The live site is never touched. Re-running on an existing site is refused.
set -euo pipefail
SITE=${1:?usage: new-mscast-site.sh <site>}
C=${C:-mscast-poc-backend-1}
BENCH=/home/frappe/frappe-bench
SCRIPTS=/mnt/d/MSCAST/erpnext-poc/scripts
ROOTPW=${DB_ROOT_PASSWORD:-$(grep -m1 -E '^\s*MYSQL_ROOT_PASSWORD:' "$HOME/mscast-poc/compose.yaml" \
                            | sed -E 's/.*:[[:space:]]*//' | tr -d '"'"'"'\r')}
ADMIN_PASSWORD=${ADMIN_PASSWORD:-$(head -c 18 /dev/urandom | base64 | tr -d '/+=' | cut -c1-16)}

[ "$SITE" = "frontend" ] && { echo "refusing: '$SITE' is the live site" >&2; exit 1; }
if docker exec "$C" test -d "$BENCH/sites/$SITE"; then
  echo "refusing: site '$SITE' already exists. Drop it first:" >&2
  echo "  docker exec $C bench drop-site $SITE --db-root-password <pw> --force" >&2
  exit 1
fi

b() { docker exec "$C" bash -c "cd $BENCH && $*"; }
installed_apps() { b "bench --site $SITE list-apps" 2>/dev/null | awk 'NF {print $1}'; }

echo "=== 1/5  create site '$SITE' with erpnext ==="
b "bench new-site $SITE --db-root-password '$ROOTPW' --admin-password '$ADMIN_PASSWORD' \
   --mariadb-user-host-login-scope='%' --install-app erpnext" 2>&1 | tail -2

echo
echo "=== 2/5  install the other four, in dependency order ==="
# india_payroll extends hrms; mscast_erp declares erpnext as required and its
# fixtures carry india_compliance's custom fields - so this order, and last.
for app in india_compliance hrms india_payroll mscast_erp; do
  echo "  $app"
  b "bench --site $SITE install-app $app" 2>&1 | tail -1 | sed 's/^/    /'
done
for app in frappe erpnext india_compliance hrms india_payroll mscast_erp; do
  installed_apps | grep -qx "$app" || { echo "FATAL: $app is not installed" >&2; exit 1; }
done
echo "  all six apps confirmed"

echo
echo "=== 3/5  site settings ==="
# Server Scripts carry the scheduled jobs. Global in the bench, but set it so a
# brand-new bench does not silently skip them.
b "bench set-config -g server_script_enabled true" >/dev/null
b "bench --site $SITE set-config server_script_enabled true" >/dev/null
echo "  server scripts enabled"
# new-site leaves the scheduler OFF. On a fresh system that means the overnight
# exception sweep, the morning report and the archival job simply never run,
# and nothing says so. Found on the first test run of this script.
b "bench --site $SITE enable-scheduler" >/dev/null
echo "  scheduler enabled"
# The address people reach the site on. Without it every link the system emails
# is built as http://<container name> and leads nowhere (T9i).
if [ -n "${HOST_NAME:-}" ]; then
  b "bench --site $SITE set-config host_name '$HOST_NAME'" >/dev/null
  echo "  host_name $HOST_NAME"
else
  echo "  WARNING: HOST_NAME not given - emailed links will not work until host_name is set"
fi

echo
echo "=== 4/5  company, chart of accounts, fiscal year - then migrate ==="
SITE=$SITE bash "$SCRIPTS/run-seed.sh" 00f_fresh_setup 2>&1 | grep -E '\[fresh-00\]|Error|Traceback'
# after_migrate re-runs the app's configure() now that a company exists, and
# asserts the approval authority - the same step every future upgrade runs.
b "bench --site $SITE migrate" 2>&1 | grep -iE 'MSCAST|repair|error' | tail -5 || true

echo
echo "=== 5/5  prove it: the checks that measure the SYSTEM must all pass ==="
# The harness also checks demo data (invoices to render, payments to block,
# payroll loaded). A fresh system has none, so those are reported but not
# required. These are the ones that say the system itself is right.
SYSTEM="T1 T1b T1c T2 T2b T3 T4b T6b T6c T6d T6f T6h T6i T6j T6k T6l T6m T6n T7b"
OUT=$(bash "$SCRIPTS/run-harness.sh" "$SITE")
echo "$OUT" | grep -iE "crash|Traceback" | sed "s/^/  /" || true   # no match is the good case
echo "$OUT" | grep -E '^\[T\] T[0-9]'
fail=0
echo
echo "  system checks:"
for t in $SYSTEM; do
  st=$(echo "$OUT" | awk -v t="$t" '$2==t {print $3; exit}')
  printf '    %-5s %s\n' "$t" "${st:-MISSING}"
  [ "$st" = "PASS" ] || fail=1
done

echo
if [ $fail -eq 0 ]; then
  echo "FRESH SYSTEM OK - site '$SITE'"
  echo "  Administrator password: $ADMIN_PASSWORD"
  echo "  (shown once; change it at first login)"
else
  echo "FRESH SYSTEM NOT OK - a system check did not pass" >&2
  exit 1
fi
