#!/usr/bin/env bash
# Start the DEV instance (after a reboot / wsl --shutdown). Live is start-poc.sh.
set -euo pipefail
docker compose -p mscast-dev -f "$HOME/mscast-dev/compose.yaml" up -d 2>&1 | tail -2
for i in $(seq 1 30); do
  code=$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8081/api/method/ping || true)
  [ "$code" = "200" ] && { echo "dev ready: http://localhost:8081"; exit 0; }
  sleep 5
done
echo "dev did not answer in 150s; check: docker compose -p mscast-dev logs --tail 50"
