#!/usr/bin/env bash
set -euo pipefail
cd "$HOME/mscast-poc"
docker compose -p mscast-poc -f compose.yaml up -d
echo "waiting for site..."
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/api/method/ping || true)
  [ "$code" = "200" ] && { echo "ready: http://localhost:8080  (Administrator / admin)"; exit 0; }
  sleep 5
done
echo "site did not answer in 150s; check: docker compose -p mscast-poc logs --tail 50"
