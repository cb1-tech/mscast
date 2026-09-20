#!/usr/bin/env bash
# Reproduce the failure that started this, and prove the guard catches it.
#
# Simulates deploying from a stale checkout: corrupts the workflow fixture in
# the container's app directory the way an old commit would have it, runs a
# migrate, and shows what the post-deploy verification did about it.
set -euo pipefail
C=mscast-poc-backend-1
F=/home/frappe/frappe-bench/apps/mscast_erp/mscast_erp/fixtures/workflow.json

echo "=== 1. backing up the good fixture ==="
docker exec $C cp "$F" "$F.good"

echo "=== 2. planting a stale one (BRM Certify back to Purchase Manager) ==="
docker exec $C python3 - <<PY
import json
p = "$F"
d = json.load(open(p))
for wf in d:
    if wf.get("name") == "MSCAST BRM Certification":
        for t in wf.get("transitions", []):
            if t.get("action") == "Certify":
                print("   fixture Certify:", t["allowed"], "-> Purchase Manager")
                t["allowed"] = "Purchase Manager"
json.dump(d, open(p, "w"), indent=1)
PY

echo "=== 3. migrating (this is what a deploy does) ==="
docker exec $C bench --site frontend migrate 2>&1 \
  | grep -viE 'updating|progress|\] [0-9]+%' | grep -A 14 -iE 'after_migrate|mscast_erp:|!!!!' || true

echo
echo "=== 4. restoring the good fixture ==="
docker exec $C mv "$F.good" "$F"
echo "done"
