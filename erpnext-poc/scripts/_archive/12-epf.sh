#!/usr/bin/env bash
C=mscast-poc-backend-1
echo "=== epf.py head ==="
docker exec "$C" bash -c "sed -n '1,80p' apps/india_payroll/india_payroll/india_payroll/epf.py"
echo "=== hooks doc_events ==="
docker exec "$C" bash -c "grep -n 'doc_events' -A 30 apps/india_payroll/india_payroll/hooks.py"
