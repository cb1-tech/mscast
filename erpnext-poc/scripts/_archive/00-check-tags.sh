#!/usr/bin/env bash
set -euo pipefail
echo "== frappe/erpnext tags =="
curl -fsSL "https://hub.docker.com/v2/repositories/frappe/erpnext/tags?page_size=25&ordering=last_updated" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);[print(t['name'], t['last_updated'][:10]) for t in d['results']]"
echo "== mariadb 11.8 tags =="
curl -fsSL "https://hub.docker.com/v2/repositories/library/mariadb/tags?page_size=50&name=11.8" \
  | python3 -c "import sys,json;d=json.load(sys.stdin);[print(t['name']) for t in d['results'][:10]]"
echo "== redis 8 tags =="
curl -fsSL "https://hub.docker.com/v2/repositories/library/redis/tags?page_size=30&name=8." \
  | python3 -c "import sys,json;d=json.load(sys.stdin);[print(t['name']) for t in d['results'][:10]]"
