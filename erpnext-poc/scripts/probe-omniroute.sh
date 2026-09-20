#!/usr/bin/env bash
C=mscast-poc-backend-1
echo "=== from WSL ==="
curl -s -m 6 -o /dev/null -w "localhost:20128 -> %{http_code}\n" http://localhost:20128/ || echo "  no answer on localhost"
for h in 127.0.0.1 host.docker.internal; do
  curl -s -m 6 -o /dev/null -w "$h:20128 -> %{http_code}\n" http://$h:20128/ 2>/dev/null || echo "  $h no answer"
done
echo "--- windows host ip as seen from wsl ---"
ip route show default | awk '{print $3}'
WINIP=$(ip route show default | awk '{print $3}')
curl -s -m 6 -o /dev/null -w "$WINIP:20128 -> %{http_code}\n" http://$WINIP:20128/ 2>/dev/null || echo "  $WINIP no answer"

echo
echo "=== from inside the ERPNext container ==="
for h in host.docker.internal 172.17.0.1 $WINIP; do
  docker exec "$C" bash -c "curl -s -m 6 -o /dev/null -w '$h:20128 -> %{http_code}\n' http://$h:20128/ 2>/dev/null || echo '  $h no answer'"
done

echo
echo "=== does it speak OpenAI? ==="
curl -s -m 8 http://localhost:20128/v1/models 2>/dev/null | head -c 600; echo
