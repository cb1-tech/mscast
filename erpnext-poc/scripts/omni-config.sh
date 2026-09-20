#!/usr/bin/env bash
C=mscast-poc-backend-1
B=/home/frappe/frappe-bench
S=frontend
docker exec "$C" rm -rf $B/apps/mscast_erp/mscast_erp/agents
docker cp /mnt/d/MSCAST/mscast_erp/mscast_erp/agents "$C":$B/apps/mscast_erp/mscast_erp/agents
echo "agent code refreshed in the bench"
docker exec "$C" bash -c "cd $B && bench --site $S set-config omniroute_base_url 'http://host.docker.internal:20128/v1' >/dev/null && bench --site $S set-config omniroute_model 'hermes-antigravity' >/dev/null && echo 'endpoint and combo set'"
echo "--- keys present on the site (values not shown) ---"
docker exec "$C" bash -c "python3 -c \"
import json
c = json.load(open('$B/sites/$S/site_config.json'))
for k in sorted(c):
    if 'omniroute' in k or 'briefing' in k:
        v = c[k]
        print('   ', k, '=', ('<set, %d chars>' % len(str(v))) if 'key' in k else v)
\""
