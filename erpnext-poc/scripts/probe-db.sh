#!/usr/bin/env bash
echo "--- db env ---"
docker inspect mscast-poc-db-1 --format '{{range .Config.Env}}{{println .}}{{end}}' | grep -iE 'pass|root'
echo "--- compose config files ---"
docker inspect mscast-poc-backend-1 --format '{{index .Config.Labels "com.docker.compose.project.config_files"}}'
echo "--- working dir label ---"
docker inspect mscast-poc-backend-1 --format '{{index .Config.Labels "com.docker.compose.project.working_dir"}}'
echo "--- disk ---"
df -h / | tail -2
echo "--- bench apps ---"
docker exec mscast-poc-backend-1 bash -c 'ls /home/frappe/frappe-bench/apps; cat /home/frappe/frappe-bench/sites/apps.txt'
echo "--- node/yarn present? ---"
docker exec mscast-poc-backend-1 bash -c 'which node yarn 2>/dev/null; node -v 2>/dev/null'
