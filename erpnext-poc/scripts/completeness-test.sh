#!/usr/bin/env bash
# Does a fresh install from the package reproduce ALL of the live configuration?
#
# Builds a fresh site with new-mscast-site.sh, then compares it with the live site
# record by record - custom fields, property setters, workflows, reports, print
# formats, roles, notifications - and every EFFECTIVE permission row. Anything
# live has that the fresh site lacks is configuration that exists only in the
# database, and a rebuild or a new install would lose it.
#
# Written after the first comparison on 21 Sep 2026 found the drawing office's
# role, a notification, and the directors' and auditor's read access to the books
# all living only on the live site.
#
# usage: completeness-test.sh            (drops its scratch site afterwards)
set -uo pipefail
S=/mnt/d/MSCAST/erpnext-poc/scripts; C=${C:-mscast-poc-backend-1}; export C; E=/mnt/d/MSCAST/erpnext-poc/evidence
SITE=completeness
bash $S/new-mscast-site.sh $SITE > $E/completeness-fresh-install.log 2>&1
tail -3 $E/completeness-fresh-install.log
echo "  full harness for the fresh site: evidence/completeness-fresh-install.log"
for s in $SITE frontend; do
  SITE=$s bash $S/run-seed.sh conf_dump 2>&1 | grep dumped | sed "s/^/  $s: /"
  docker cp $C:/tmp/conf-$s.json /tmp/conf-$s.json
done
python3 - $SITE <<'PY'
import json, sys
f = json.load(open("/tmp/conf-%s.json" % sys.argv[1])); l = json.load(open("/tmp/conf-frontend.json"))
lost = 0
print("\n  ON LIVE BUT NOT PRODUCED BY A FRESH INSTALL:")
for k in l:
    miss = sorted(set(l[k]) - set(f.get(k, [])))
    lost += len(miss)
    print("    %-28s %3d" % (k, len(miss)))
    for m in miss[:8]: print("        " + m)
    if len(miss) > 8: print("        ... +%d" % (len(miss) - 8))
print("\n  %s" % ("COMPLETE - a fresh install reproduces all live configuration" if not lost
                   else "INCOMPLETE - %d item(s) exist only in the live database" % lost))
PY
ROOTPW=$(grep -m1 -E '^\s*MYSQL_ROOT_PASSWORD:' ~/${C%-backend-1}/compose.yaml | sed -E 's/.*:[[:space:]]*//')
docker exec $C bash -c "cd /home/frappe/frappe-bench && bench drop-site $SITE --db-root-password '$ROOTPW' --force --no-backup" >/dev/null 2>&1 && echo "  scratch site dropped"
