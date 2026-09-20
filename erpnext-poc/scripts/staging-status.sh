#!/usr/bin/env bash
C=mscast-poc-backend-1
docker exec "$C" bash -c 'ls -la /home/frappe/frappe-bench/sites/staging.localhost/ 2>/dev/null | head'
echo "--- installed apps on staging ---"
docker exec "$C" bash -c 'cd /home/frappe/frappe-bench && bench --site staging.localhost list-apps 2>&1 | tail -10'
