#!/usr/bin/env bash
# Copy the fixtures written by seed/140_export_fixtures.py out of the backend
# container and into the installable app, so a clean build carries them.
#
# Two of the exported files are deliberately NOT shipped:
#   custom_doctype.json      - the 26 MSCAST doctypes ship as real app doctypes
#                              under mscast_erp/mscast/doctype/, not as fixtures
#   _hidden_workspaces.json  - a list of names for reference only; install.py
#                              carries its own HIDE list
# install.py imports every .json it finds in fixtures/, so leaving either one
# there would break a clean build.
set -euo pipefail

APP_FIXTURES=/mnt/d/MSCAST/mscast_erp/mscast_erp/fixtures
SKIP=(custom_doctype.json _hidden_workspaces.json)

C=$(docker ps --format '{{.Names}}' | grep backend | head -1)
if [ -z "$C" ]; then
  echo "no backend container running" >&2
  exit 1
fi

echo "container: $C"
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT
docker cp "$C":/tmp/mscast_fixtures/. "$TMP"/

for f in "${SKIP[@]}"; do
  if [ -e "$TMP/$f" ]; then
    rm -f "$TMP/$f"
    echo "  skipped $f (not shipped)"
  fi
  rm -f "$APP_FIXTURES/$f"
done

cp "$TMP"/*.json "$APP_FIXTURES"/
echo
ls -la --time-style=+%Y-%m-%d\ %H:%M "$APP_FIXTURES"
