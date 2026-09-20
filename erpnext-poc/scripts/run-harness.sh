#!/usr/bin/env bash
# usage: run-harness.sh [site]    (default: frontend)
set -euo pipefail
export SITE=${1:-frontend}
echo "harness against site: $SITE"
bash /mnt/d/MSCAST/erpnext-poc/scripts/run-seed.sh 102_test_harness 2>&1 \
  | grep -E '^\[T\]|PASS|WARN|FAIL|Traceback|Error' | tail -45
