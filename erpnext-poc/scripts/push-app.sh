#!/usr/bin/env bash
# Copy the app from the repo into the running bench so a code change takes effect
# without a rebuild.
#
# This script caused an outage on 20 Sep 2026 and the two reasons are worth
# knowing, because both failures are silent:
#
#   1. It did not restart anything. `bench console` and `bench execute` spawn a
#      fresh python each time, so they always saw the new code - but gunicorn and
#      the queue workers are long-running processes that keep whatever they
#      imported at start. The first time the app was copied in, gunicorn had
#      already been running for 28 hours without it, so every web request died on
#      `ModuleNotFoundError: No module named 'mscast_erp'` while every script and
#      every build check passed. The site was down for hours and nothing said so.
#
#   2. The container filter was `grep -E 'backend|worker|scheduler'`, and the
#      queue containers are named `queue-short` and `queue-long`. They matched
#      nothing, so the background workers ran stale code indefinitely.
#
# Hence: copy everywhere, restart the python, then prove the site answers.
set -euo pipefail
SRC=/mnt/d/MSCAST/mscast_erp/mscast_erp
DEST=/home/frappe/frappe-bench/apps/mscast_erp/mscast_erp

MATCH='backend|queue|scheduler|websocket'
targets=$(docker ps --format '{{.Names}}' | grep -E "$MATCH" || true)
if [ -z "$targets" ]; then
  echo "no running bench containers matched /$MATCH/ - is the stack up?" >&2
  exit 1
fi

for C in $targets; do
  if docker exec "$C" test -d "$DEST" 2>/dev/null; then
    docker cp "$SRC"/. "$C":"$DEST"/
    docker exec "$C" bash -c \
      "find $DEST -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true"
    echo "  updated  $C"
  else
    echo "  skipped  $C (no app directory)"
  fi
done

docker exec mscast-poc-backend-1 bench --site frontend clear-cache >/dev/null 2>&1 || true
echo "  cache cleared"

# The part that was missing. Without this the copy above changes nothing for
# anyone using a browser.
echo "  restarting python processes..."
docker restart $targets >/dev/null
echo "  restarted: $(echo $targets | tr '\n' ' ')"

echo "  waiting for the site to answer..."
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://localhost:8080/login || echo 000)
  if [ "$code" = "200" ]; then
    echo "  site answering (HTTP 200 on /login after ${i} attempt(s))"
    if docker logs --tail 200 mscast-poc-backend-1 2>&1 | grep -q "No module named 'mscast_erp'"; then
      echo "  WARNING: an mscast_erp import error is still in the log - check it" >&2
      exit 1
    fi
    exit 0
  fi
  sleep 5
done

echo "  SITE DID NOT COME BACK (last HTTP $code). Check: docker logs mscast-poc-backend-1" >&2
exit 1
