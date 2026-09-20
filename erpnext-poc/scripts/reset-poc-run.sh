#!/usr/bin/env bash
# Run reset-poc.sh unattended, with a log, because it takes ~30 minutes and the
# caller cannot hold a shell open that long. Answers the confirmation prompt.
#
# DO NOT run this without a backup that has been copied OUT of the Docker volume
# (backup-out.sh) and proven restorable (restore-test.sh). reset-poc.sh runs
# `docker compose down -v`, which deletes the volume the backups live in.
set -euo pipefail
LOG=/mnt/d/MSCAST/erpnext-poc/reset-run.log
: > "$LOG"
echo "started $(date -Is)" >> "$LOG"
yes y | bash /mnt/d/MSCAST/erpnext-poc/scripts/reset-poc.sh >> "$LOG" 2>&1
echo "finished $(date -Is) rc=$?" >> "$LOG"
