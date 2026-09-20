#!/usr/bin/env bash
# Quick state of the stack. Kept as a file because the outer shell is PowerShell
# and anything with nested quotes gets mangled on the way through.
C=mscast-poc-backend-1
echo "=== sites in the bench ==="
docker exec "$C" bash -c 'ls -1 /home/frappe/frappe-bench/sites | grep -v assets' 2>/dev/null
echo
echo "=== bench processes running in the backend ==="
docker exec "$C" bash -c "ps -eo args | grep '[b]ench' | head -5" 2>/dev/null || echo "  none"
echo
echo "=== live site ==="
printf '  localhost/login   %s\n' "$(curl -s -o /dev/null -w '%{http_code}' --max-time 10 http://localhost:8080/login)"
printf '  public /login     %s\n' "$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 https://mscast.carobar.net/login)"
echo
echo "=== containers ==="
docker ps --format '{{.Names}}\t{{.Status}}' | grep mscast
