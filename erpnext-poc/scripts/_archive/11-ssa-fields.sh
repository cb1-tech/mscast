#!/usr/bin/env bash
C=mscast-poc-backend-1
echo "=== SSA custom fields defined by india_payroll ==="
docker exec "$C" bash -c "grep -n 'Salary Structure Assignment' -A 60 apps/india_payroll/india_payroll/install.py | grep -E 'fieldname|fieldtype|label|default|options' | head -80"
