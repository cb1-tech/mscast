#!/usr/bin/env bash
C=mscast-poc-backend-1
docker exec "$C" bash -c "grep -n 'def setup_complete' -A 30 apps/frappe/frappe/desk/page/setup_wizard/setup_wizard.py" | head -45
echo "=== erpnext setup wizard stages ==="
docker exec "$C" bash -c "grep -rn 'def setup_complete\|def stage_fixtures\|def setup_defaults' apps/erpnext/erpnext/setup/setup_wizard/setup_wizard.py" | head -10
