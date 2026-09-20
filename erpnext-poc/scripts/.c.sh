#!/usr/bin/env bash
set -euo pipefail
cd /mnt/d/MSCAST
git add -A mscast_erp erpnext-poc/seed erpnext-poc/scripts
git commit -F - <<'MSG'
Install the app on the POC site, and fix the two things that broke

Installing mscast_erp on the WSL site is what registers the 08:35 job. It
also flushed out two defects that had been hiding, both of which would
have shipped to the VPS.

1. Every controller class was named wrong.

   Frappe builds the class name from the DocType name verbatim:

       classname = doctype.replace(" ", "").replace("-", "")

   so "MSCAST Transmittal" must be MSCASTTransmittal. The generator that
   first wrote these used title case and produced MscastTransmittal for
   all 26. It never surfaced because the DocType rows carried custom=1,
   and get_controller returns a plain Document for a custom doctype
   without importing anything. Installing the app set custom=0, the
   imports started running for real, and 11 print formats died with
   ImportError. fix-controller-classes.sh derives the right name from
   each doctype's own JSON instead of guessing. 26 renamed, T4 back to
   15 rendered / 0 problems.

2. The briefing could not reach anyone.

   "bench set-config mscast_briefing_to '[...]'" stores the argument as a
   string unless given --parse. send() wrapped that whole string as one
   recipient, and the send failed with "Invalid email address" in the
   Error Log - where nobody looks. It now accepts a JSON array, a
   comma-separated string or a real list, and drops anything without an @.

   Before the fix it had also been falling back to "first enabled System
   User", which after the user rework is a draughtsman on a domain that
   receives no mail.

Proven end to end rather than assumed: daily_briefing() called exactly as
the scheduler calls it, two Email Queue rows, both Sent, to both
directors.

State now: scheduler active; MSCAST Exception Sweep at 06:00;
mscast_erp.agents.briefing.daily_briefing registered at 08:35, not
stopped; harness 23 PASS / 0 FAIL; sweep 4 open items.

snapshot.sh / push-app.sh added - the database backup taken before the
install is in erpnext-poc/backups and was not needed.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G3y6MpPfn3Nhms7B2xeYDR
MSG
git push -q origin HEAD
git log --oneline -1
