#!/usr/bin/env bash
tr -d '\r' < /mnt/d/MSCAST/erpnext-poc/staging-build.log 2>/dev/null \
  | grep -vE 'Updating DocTypes|\] +[0-9]+%|^\s*$' \
  | tail -${1:-25}
