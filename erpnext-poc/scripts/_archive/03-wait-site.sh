#!/usr/bin/env bash
for i in $(seq 1 30); do
  s=$(docker inspect -f '{{.State.Status}}:{{.State.ExitCode}}' mscast-poc-create-site-1 2>/dev/null)
  echo "$i $s"
  case "$s" in exited*) break;; esac
  sleep 20
done
docker logs mscast-poc-create-site-1 2>&1 | tr -d '\r' | grep -viE 'updating|%' | tail -8
docker exec mscast-poc-backend-1 bash -c "ls sites/frontend/site_config.json && cd /home/frappe/frappe-bench && bench --site frontend list-apps"
curl -s -o /dev/null -w 'http:%{http_code}\n' http://localhost:8080/api/method/ping
