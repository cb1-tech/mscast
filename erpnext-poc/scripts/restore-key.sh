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
python3 - "$CFG" <<'PY2' | while IFS=$'\t' read -r k v; do
import json, sys
for k, v in json.load(open(sys.argv[1])).items():
    if k.startswith("mscast_"):
        print("%s\t%s" % (k, json.dumps(v)))
PY2
  docker exec "$C" bash -c "cd /home/frappe/frappe-bench && bench --site $SITE set-config --parse $k '$v'" >/dev/null
  echo "  restored $k"
done
