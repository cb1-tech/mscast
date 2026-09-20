#!/usr/bin/env bash
# Build a custom ERPNext v16 image with India Compliance, HRMS and India Payroll.
set -euo pipefail
cd "$HOME/mscast-poc"

cat > apps.json <<'JSON'
[
  {"url": "https://github.com/frappe/erpnext",              "branch": "version-16"},
  {"url": "https://github.com/frappe/hrms",                 "branch": "version-16"},
  {"url": "https://github.com/resilient-tech/india-compliance", "branch": "version-16"},
  {"url": "https://github.com/frappe/india-payroll",        "branch": "version-16"}
]
JSON

cd frappe_docker
nohup docker build \
  --secret id=apps_json,src="$HOME/mscast-poc/apps.json" \
  --build-arg FRAPPE_BRANCH=version-16 \
  --build-arg FRAPPE_PATH=https://github.com/frappe/frappe \
  -t mscast/erpnext:v16 \
  -f images/layered/Containerfile . > "$HOME/mscast-poc/build.log" 2>&1 &
disown
sleep 3
echo "build started; log: ~/mscast-poc/build.log"
