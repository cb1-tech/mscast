#!/usr/bin/env bash
set -euo pipefail
bash /mnt/d/MSCAST/erpnext-poc/scripts/run-seed.sh 102_test_harness 2>&1 \
  | grep -E '^\[T\]|PASS|WARN|FAIL|Traceback|Error' | tail -45
