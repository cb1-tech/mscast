#!/usr/bin/env bash
set -euo pipefail
cd /mnt/d/MSCAST
git add -A
git commit -F- <<'MSG'
push-app.sh: restart the python, and copy to the containers that actually exist

The site returned HTTP 500 on every request with
"ModuleNotFoundError: No module named 'mscast_erp'", while the container's own
python imported it fine and every build check passed. Two bugs in this script,
both silent.

It never restarted anything. bench console and bench execute spawn a fresh
python each time, so they always saw the new code. gunicorn and the queue
workers are long-running and keep whatever they imported at start - and gunicorn
had been up 28 hours, since before the app folder existed. So the web front end
was serving 500s for hours while every script, every harness run and every
demonstration-by-console worked perfectly. Nothing in the system said so, and
the first person to find out was the one who opened a browser.

The container filter was 'backend|worker|scheduler'. The queue containers are
named queue-short and queue-long, so they matched nothing.

Now: copy to backend|queue|scheduler|websocket, restart them, then prove
/login answers 200 and no import error is left in the log. It exits non-zero if
the site does not come back, so a bad push fails loudly instead of quietly.

This also exposed something bigger, not fixed here: the scheduler and queue
containers have no copy of mscast_erp at all, so four of the five MSCAST
scheduled jobs have never run. last_execution is NEVER for the 06:00 exception
sweep and the 08:35 briefing. They work when run by hand in the backend
container, which is how they were built and demonstrated. Raised separately.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G3y6MpPfn3Nhms7B2xeYDR
MSG
git log --oneline -1
