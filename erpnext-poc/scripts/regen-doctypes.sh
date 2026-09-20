#!/usr/bin/env bash
set -e
bash /mnt/d/MSCAST/erpnext-poc/scripts/run-seed.sh 141_doctypes_to_app 2>&1 | tail -3
rm -rf /mnt/d/MSCAST/mscast_erp/mscast_erp/mscast/doctype/mscast_*
docker cp mscast-poc-backend-1:/tmp/mscast_doctypes/. /mnt/d/MSCAST/mscast_erp/mscast_erp/mscast/doctype/
python3 - <<'PY'
import json
d = json.load(open('/mnt/d/MSCAST/mscast_erp/mscast_erp/mscast/doctype/mscast_pcc/mscast_pcc.json'))
print("sample:", d["name"], "| modified:", d.get("modified"), "| custom:", d.get("custom"), "| module:", d.get("module"))
PY
