#!/usr/bin/env bash
cd /mnt/d/MSCAST
F=$(ls erpnext-poc/seed/102*.py | head -1)
echo "harness file: $F"
echo "=================================================="
sed -n '258,330p' "$F"
