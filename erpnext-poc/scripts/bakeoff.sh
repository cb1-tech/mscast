#!/usr/bin/env bash
# Run the model bake-off detached, so the device bridge's short call limit
# does not cut it off. Poll /tmp/bakeoff.log for progress.
LOG=/tmp/bakeoff.log
: > "$LOG"
nohup bash /mnt/d/MSCAST/erpnext-poc/scripts/run-seed.sh 163_model_bakeoff \
  >> "$LOG" 2>&1 &
echo "started pid $!, log $LOG"
