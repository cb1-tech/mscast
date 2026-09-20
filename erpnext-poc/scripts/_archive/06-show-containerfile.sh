#!/usr/bin/env bash
echo "===== layered/Containerfile ====="
sed -n '1,60p' ~/mscast-poc/frappe_docker/images/layered/Containerfile
echo "===== custom/Containerfile (args only) ====="
grep -n "ARG\|FROM\|apps.json\|APPS_JSON" ~/mscast-poc/frappe_docker/images/custom/Containerfile | head -30
