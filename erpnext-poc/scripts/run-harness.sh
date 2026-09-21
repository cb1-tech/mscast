#!/usr/bin/env bash
# usage: run-harness.sh [site]    (default: frontend)
#
# No `tail` on the output. It used to keep the last 45 lines, and once the harness
# grew past that on a site with failures, the FIRST check (T1) was silently cut
# off - new-mscast-site.sh then reported it as MISSING. A filter that drops lines
# is how a report lies without anyone noticing.
set -euo pipefail
export SITE=${1:-frontend}
echo "harness against site: $SITE"
TAIL=100000 bash /mnt/d/MSCAST/erpnext-poc/scripts/run-seed.sh 102_test_harness 2>&1 \
  | grep -E '^\[T\]|Traceback|Error:'
