#!/usr/bin/env bash
# Latest released v16 tag of each app upstream - to see whether an upgrade exists.
for r in frappe/frappe frappe/erpnext frappe/hrms resilient-tech/india-compliance frappe/india-payroll; do
  t=$(git ls-remote --tags --refs "https://github.com/$r" 'v16.*' 2>/dev/null | awk -F/ '{print $NF}' | sort -V | tail -1)
  printf '  %-34s %s\n' "$r" "${t:-no v16 tags}"
done
