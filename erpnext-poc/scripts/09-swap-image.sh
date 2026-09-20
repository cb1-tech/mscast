#!/usr/bin/env bash
# Point the compose stack at the custom image and install the extra apps on the site.
set -euo pipefail
cd "$HOME/mscast-poc"

cp -f compose.yaml compose.yaml.bak
sed -i 's|image: frappe/erpnext:v16.35.0|image: mscast/erpnext:v16|g' compose.yaml
grep -c "mscast/erpnext:v16" compose.yaml

docker compose -p mscast-poc -f compose.yaml up -d
echo "waiting for backend..."
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/api/method/ping || true)
  [ "$code" = "200" ] && break
  sleep 5
done
echo "site http: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/api/method/ping)"

docker exec mscast-poc-backend-1 bash -c "cd /home/frappe/frappe-bench && ls apps"
docker exec mscast-poc-backend-1 bash -c "cd /home/frappe/frappe-bench && bench --site frontend install-app india_compliance" 2>&1 | tr -d '\r' | grep -viE 'updating|%' | tail -5
docker exec mscast-poc-backend-1 bash -c "cd /home/frappe/frappe-bench && bench --site frontend install-app hrms" 2>&1 | tr -d '\r' | grep -viE 'updating|%' | tail -5
docker exec mscast-poc-backend-1 bash -c "cd /home/frappe/frappe-bench && bench --site frontend install-app india_payroll" 2>&1 | tr -d '\r' | grep -viE 'updating|%' | tail -5
docker exec mscast-poc-backend-1 bash -c "cd /home/frappe/frappe-bench && bench --site frontend list-apps"
