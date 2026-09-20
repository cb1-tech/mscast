#!/usr/bin/env bash
for r in frappe/erpnext frappe/hrms resilient-tech/india-compliance frappe/india-payroll; do
  echo "== $r"
  git ls-remote --heads "https://github.com/$r.git" 2>/dev/null | awk '{print $2}' | sed 's|refs/heads/||' | grep -E '^(version-1[56]|main|master|develop)$' | tr '\n' ' '
  echo
done
