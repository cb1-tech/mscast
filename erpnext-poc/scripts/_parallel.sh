setsid nohup bash /mnt/d/MSCAST/erpnext-poc/scripts/build-base-image.sh mscast/erpnext:v16-next </dev/null > /mnt/d/MSCAST/erpnext-poc/base-build.log 2>&1 &
ROOTPW=$(grep -m1 -E '^\s*MYSQL_ROOT_PASSWORD:' ~/mscast-poc/compose.yaml | sed -E 's/.*:[[:space:]]*//')
docker exec mscast-poc-backend-1 bash -c "cd /home/frappe/frappe-bench && bench drop-site freshtest --db-root-password '$ROOTPW' --force --no-backup" >/dev/null 2>&1
setsid nohup bash /mnt/d/MSCAST/erpnext-poc/scripts/new-mscast-site.sh freshtest </dev/null > /mnt/d/MSCAST/erpnext-poc/fresh-run.log 2>&1 &
sleep 3; echo launched
