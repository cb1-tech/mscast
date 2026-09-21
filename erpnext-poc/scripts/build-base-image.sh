#!/usr/bin/env bash
# Build the BASE image - Frappe plus erpnext, hrms, india_compliance and
# india_payroll - from erpnext-poc/apps.json, using frappe_docker's layered build.
#
# This is how mscast/erpnext:v16 was made on 18 Sep 2026, but it was never
# written down: apps.json lived only in ~/mscast-poc and the command only in a
# build log. It is here now so an upgrade is a repeatable step, not an
# archaeology exercise.
#
# The apps track the moving `version-16` branches, so each build picks up that
# day's patch releases. CACHE_BUST forces the fetch; without it Docker reuses the
# cached clone and "upgrading" silently rebuilds the old versions.
#
# usage: build-base-image.sh [tag]      default mscast/erpnext:v16-next
set -euo pipefail
TAG=${1:-mscast/erpnext:v16-next}
FD=${FRAPPE_DOCKER:-$HOME/mscast-poc/frappe_docker}
APPS=/mnt/d/MSCAST/erpnext-poc/apps.json
[ -d "$FD/images/layered" ] || { echo "frappe_docker not found at $FD" >&2; exit 1; }

cd "$FD"
echo "building $TAG from $APPS (frappe_docker $(git log -1 --format='%h %cs'))"
docker build \
  --secret=id=apps_json,src="$APPS" \
  --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
  --build-arg=FRAPPE_BRANCH=version-16 \
  --build-arg=CACHE_BUST="$(date +%s)" \
  --tag="$TAG" \
  --file=images/layered/Containerfile . 2>&1 | tail -5

echo
bash /mnt/d/MSCAST/erpnext-poc/scripts/app-versions.sh "$TAG"
