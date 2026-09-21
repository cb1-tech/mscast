#!/usr/bin/env bash
# Build mscast/erpnext:v16-app - the base image with mscast_erp baked in.
#
# The build context is the repo root, because the Containerfile copies mscast_erp
# from there. The base image is not touched, so a bad build costs nothing: the
# stack keeps running on whatever tag compose currently names.
set -euo pipefail

REPO=/mnt/d/MSCAST
TAG=${1:-mscast/erpnext:v16-app}

echo "building $TAG"
echo "  context : $REPO"
echo "  app     : $REPO/mscast_erp"
echo

if [ ! -f "$REPO/mscast_erp/pyproject.toml" ]; then
  echo "app not found at $REPO/mscast_erp - wrong context?" >&2
  exit 1
fi

cd "$REPO"
BASE=${BASE:-mscast/erpnext:v16}
echo "  base    : $BASE"
docker build \
  --build-arg BASE="$BASE" \
  -t "$TAG" \
  -f erpnext-poc/Containerfile.mscast \
  . 2>&1 | tail -30

echo
echo "=== verify the app is in the image, in a throwaway container ==="
docker run --rm --entrypoint bash "$TAG" -c \
  'cd /home/frappe/frappe-bench && ./env/bin/python -c "import mscast_erp, os; print(\"   import OK:\", mscast_erp.__file__)" && ls apps/ && grep -c . sites/apps.txt'

echo
echo "built: $TAG"
docker images --format '{{.Repository}}:{{.Tag}}\t{{.Size}}\t{{.CreatedSince}}' | grep -E "^${TAG}\s|mscast/erpnext"
