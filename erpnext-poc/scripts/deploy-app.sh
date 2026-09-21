#!/usr/bin/env bash
# Build the app into the image and redeploy the stack, properly.
#
# Use this when application CODE changes - hooks, controls, doctypes - because
# the app is baked into the image and a running container keeps the copy it
# started with. `push-app.sh` hot-copies into running containers and is fine for
# iterating; this is the one that produces a stack you could hand to someone.
#
# The frontend restart at the end is not optional, and the reason is worth
# knowing. nginx resolves `backend` and `websocket` once, at start, and caches
# the container IPs. Recreating those containers gives them new IPs, so nginx
# keeps proxying to addresses that no longer answer and every page returns
# **502 while every container reports healthy**. That happened on 21 Sep 2026
# after a by-hand `docker compose up --force-recreate`: the harness passed, the
# containers were up, and the site was down.
#
# Order matters: build first, because a failed build must cost nothing. The
# stack keeps running on the old image until the new one exists.
set -euo pipefail

REPO=/mnt/d/MSCAST
STACK=${STACK:-$HOME/mscast-poc}
TAG=${TAG:-mscast/erpnext:v16-app}
# The frontend (nginx) runs the same image and serves /assets from it, so it
# must be recreated too - restarting it kept the OLD image and the old assets.
SERVICES="backend queue-short queue-long scheduler websocket frontend"

echo "=== 1/4  build $TAG ==="
bash "$REPO/erpnext-poc/scripts/build-mscast-image.sh" "$TAG" | tail -8

echo
echo "=== 2/4  recreate the python containers ==="
cd "$STACK"
docker compose up -d --force-recreate $SERVICES 2>&1 | grep -E 'Started|Error' || true

echo
echo "=== 3/4  restart the frontend so nginx re-resolves the new containers ==="
docker compose restart frontend 2>&1 | grep -E 'Started|Error' || true

echo
echo "=== 4/4  prove the site answers ==="
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 \
         http://localhost:8080/login || echo 000)
  if [ "$code" = "200" ]; then
    echo "  site answering (HTTP 200 on /login after ${i} attempt(s))"
    if docker logs --tail 200 mscast-poc-backend-1 2>&1 \
       | grep -q "No module named 'mscast_erp'"; then
      echo "  WARNING: an mscast_erp import error is still in the log" >&2
      exit 1
    fi
    # The app's own static files must be served, or the desk theme silently
    # disappears (it did, from 20 to 21 Sep 2026).
    css=$(curl -s -o /dev/null -w '%{http_code} %{content_type}' http://localhost:8080/assets/mscast_erp/css/mscast.css)
    case "$css" in
      "200 text/css"*) echo "  app assets served (mscast.css: $css)";;
      *) echo "  APP ASSETS NOT SERVED - mscast.css returned: $css" >&2; exit 1;;
    esac
    echo
    echo "Deployed. Now run the build checks:"
    echo "  bash $REPO/erpnext-poc/scripts/run-harness.sh"
    exit 0
  fi
  sleep 5
done

echo "  SITE DID NOT COME BACK (last HTTP $code)." >&2
echo "  Check: docker compose logs --tail 50 backend frontend" >&2
exit 1
