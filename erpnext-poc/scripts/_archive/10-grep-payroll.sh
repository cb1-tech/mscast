#!/usr/bin/env bash
C=mscast-poc-backend-1
echo "=== india_payroll tree ==="
docker exec "$C" bash -c "find apps/india_payroll -name '*.py' | head -40"
echo "=== hooks ==="
docker exec "$C" bash -c "sed -n '1,120p' apps/india_payroll/india_payroll/hooks.py"
echo "=== where Provident Fund is referenced ==="
docker exec "$C" bash -c "grep -rn 'Provident Fund' apps/india_payroll --include=*.py | head -20"
echo "=== payroll settings child field ==="
docker exec "$C" bash -c "grep -rn 'India Payroll Company Setting' apps/india_payroll --include=*.json --include=*.py | head -20"
