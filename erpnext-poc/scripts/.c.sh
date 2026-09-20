#!/usr/bin/env bash
set -euo pipefail
rm -f "/mnt/d/MSCAST/ERP Plan/.wb-backup.xlsx"
rm -f /mnt/d/MSCAST/erpnext-poc/scripts/.wb.sh /mnt/d/MSCAST/erpnext-poc/scripts/.pipwb.sh
cd /mnt/d/MSCAST
git add -A erpnext-poc
git commit -F - <<'MSG'
Workbook sheet 14: name the real roles, drop the imaginary limit

The users sheet asked MSCAST to describe what each person may approve, and
its worked example said "Purchase orders up to INR 5 lakh". There are no
approval limits by value anywhere in the system - approval follows the role.
Asking the client to think in rupee thresholds invites them to send back a
structure the system cannot honour, and then somebody has to explain that
after they have already done the work.

The example now names a real role and gives a truthful answer in the approve
column: "No - raises purchase orders, a director approves them".

Added a roles reference beside the table: eleven roles, what each does, what
each may approve, and the three things the system refuses whoever asks. Plus
the honest note that one person holding several roles works and is normal at
this size, but removes the separation - and to say in Notes where that is
intended.

Placed in columns H:K, clear of the COUNTA ranges the checklist counts over
A6:A205. Verified afterwards: the 15 other sheets are byte-identical and all
17 checklist formulas survive.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G3y6MpPfn3Nhms7B2xeYDR
MSG
git push -q origin HEAD
git log --oneline -1
