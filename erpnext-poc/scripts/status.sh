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

echo
echo "=== last backup on D: ==="
L=/mnt/d/MSCAST/backups/backup.log
if [ -f "$L" ]; then
  tail -1 "$L" | sed 's/^/  /'
  last=$(ls -1 /mnt/d/MSCAST/backups | grep -E '^[0-9]{8}_[0-9]{6}$' | sort | tail -1)
  age_h=$(( ( $(date +%s) - $(date -d "${last:0:8} ${last:9:2}:${last:11:2} IST" +%s) ) / 3600 ))
  [ "$age_h" -gt 26 ] && echo "  WARNING: newest set is ${age_h}h old - the nightly job is not running" \
                      || echo "  newest set ${last} (${age_h}h old)"
else
  echo "  no backup log - the nightly job has never run"
fi
