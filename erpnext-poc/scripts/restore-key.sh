#!/usr/bin/env bash
# Put a backup's encryption key back on a site.
#
# Frappe encrypts stored secrets (mail passwords, API keys) with `encryption_key`
# from site_config.json - which lives OUTSIDE the database. `bench restore` brings
# the database back and leaves the site's current key in place, so every secret
# in the restored data becomes undecryptable. Found 21 Sep 2026: after a reset
# and restore, the live site's mail password could not be decrypted and the
# daily digest failed with "Encryption key is invalid". The backup set carries
# the right key in *-site_config_backup.json.
#
# usage: restore-key.sh <backup dir> [site]
set -euo pipefail
DIR=${1:?usage: restore-key.sh <backup dir> [site]}
SITE=${2:-frontend}
C=${C:-mscast-poc-backend-1}
CFG=$(ls "$DIR"/*site_config_backup.json)
KEY=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1])).get('encryption_key',''))" "$CFG")
[ -n "$KEY" ] || { echo "no encryption_key in $CFG" >&2; exit 1; }
docker exec "$C" bash -c "cd /home/frappe/frappe-bench && bench --site $SITE set-config encryption_key '$KEY'" >/dev/null
echo "  encryption key restored on '$SITE' from $(basename "$CFG") (${KEY:0:6}...)"

# MSCAST's own site settings (mscast_demo, mscast_briefing_to, ...) live in the
# same file and are lost the same way. mscast_demo decides whether prints carry
# the DEMONSTRATION watermark, so losing it on a restored demo removes the mark.
# Written through update_site_config from a JSON file, NOT `bench set-config
# --parse`: --parse rejects JSON booleans (true/false), so a nested value such as
# mscast_last_backup {"ok": true} failed and, under set -e, silently aborted any
# caller (found 21 Sep 2026 building the dev instance).
T=$(mktemp -d)
python3 - "$CFG" > "$T/mscast.json" <<'PY2'
import json, sys
print(json.dumps({k: v for k, v in json.load(open(sys.argv[1])).items() if k.startswith("mscast_")}))
PY2
docker cp "$T/mscast.json" "$C:/tmp/mscast-cfg.json" >/dev/null
docker exec "$C" bash -c "cd /home/frappe/frappe-bench/sites && ../env/bin/python -c \"
import json, frappe
from frappe.installer import update_site_config
frappe.init(site='$SITE')
for k, v in json.load(open('/tmp/mscast-cfg.json')).items():
    update_site_config(k, v); print('  restored ' + k)
\"" 2>&1 | grep -vE 'RuntimeWarning|sys.prefix|sys.exec_prefix|frozen site'
rm -rf "$T"
