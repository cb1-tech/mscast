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
# Run from a COPY, not from the file in the repo.
#
# bash reads a script lazily, by byte offset, as it executes. Editing
# reset-poc.sh while a run is in progress makes bash resume at the old offset in
# the new file and execute whatever now happens to be there - which on 21 Sep
# 2026 killed a 25-minute run at the halfway point with "app: unbound variable".
# Copying first makes the run immune to edits.
SNAP=$(mktemp /tmp/reset-poc.XXXXXX.sh)
cp /mnt/d/MSCAST/erpnext-poc/scripts/reset-poc.sh "$SNAP"
echo "running snapshot $SNAP" >> "$LOG"
yes y | bash "$SNAP" >> "$LOG" 2>&1
rm -f "$SNAP"
echo "finished $(date -Is) rc=$?" >> "$LOG"
