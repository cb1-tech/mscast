# -*- coding: utf-8 -*-
"""Tell someone when the safety net fails.

Two halves, because each covers the other's blind spot:

  nightly.sh (outside the site, Windows task 02:30 JST)
      backs up, runs the build checks, records the outcome in site config
      (mscast_last_backup, mscast_last_checks) and calls alert() on failure.

  daily_check() (inside the site, scheduler, 09:00 IST)
      reads what the nightly job recorded. If it has not run in 26 hours, or
      its last run failed, it says so. This is what catches the case the
      nightly job cannot report on itself: the Windows task quietly stopping.

Recipients: site config mscast_alerts_to (a list). Nothing is sent if it is not
set, so a scratch or restored copy stays quiet. Before 21 Sep 2026 a failed
backup wrote a line to a log file that nobody reads.
"""
import time
import frappe

STALE_HOURS = 26


def _recipients():
    r = frappe.conf.get("mscast_alerts_to") or []
    return [r] if isinstance(r, str) else list(r)


def alert(subject, body):
    """Send now, not via the queue: an alert that waits for the scheduler is
    useless on the night the scheduler is the thing that broke."""
    to = _recipients()
    if not to:
        print("mscast_erp: alert not sent - mscast_alerts_to is not set")
        return False
    frappe.sendmail(recipients=to, subject="[MSCAST ERP] " + subject,
                    message="<pre style='font-family:monospace'>%s</pre>"
                            % frappe.utils.escape_html(body), now=True)
    print("mscast_erp: alert sent to %s" % ", ".join(to))
    return True


def alert_from_file(subject, path):
    return alert(subject, open(path).read())


def daily_check():
    now = time.time()
    problems = []
    last = frappe.conf.get("mscast_last_backup") or {}
    checks = frappe.conf.get("mscast_last_checks") or {}
    if not last.get("at"):
        problems.append("No off-site backup has ever been recorded for this site.")
    else:
        age = (now - float(last["at"])) / 3600
        if age > STALE_HOURS:
            problems.append("The last verified backup is %.0f hours old (set %s). The nightly job "
                            "has stopped running - check the Windows task 'MSCAST nightly backup' "
                            "and that the PC was on." % (age, last.get("set", "?")))
        if last.get("ok") is False:
            problems.append("The last nightly backup FAILED: %s" % last.get("detail", "?"))
    if checks.get("fail"):
        problems.append("The last nightly build checks reported %s failure(s): %s"
                        % (checks["fail"], checks.get("detail", "")))
    if problems:
        alert("Nightly safety net needs attention", "\n\n".join(problems))
    else:
        print("mscast_erp: watchdog - last backup and checks are current")
    return problems
