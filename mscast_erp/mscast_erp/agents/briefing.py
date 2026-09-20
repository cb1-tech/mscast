# -*- coding: utf-8 -*-
"""The judgement half of the exception agent.

The rules half runs as a Server Script inside ERPNext at 06:00 and needs no
network and no model. This module wakes afterwards, reads what the rules found,
and writes the few sentences a director can act on.

Design rules it keeps to:
  - it never writes to the ledger, never submits a document, never changes a master
  - it never contacts anyone outside MSCAST - the recipient list is configuration
  - if the model is unreachable, the briefing still goes out as a plain list.
    A missing model must never mean a missing morning email.

It talks to any OpenAI-compatible endpoint. Here that is OmniRoute, which fronts
several providers behind one combo name and falls back between them itself - so
the ERP knows one address and the routing decisions live where they belong.

Configuration, in site_config.json (never in the repo). Every line is optional -
the defaults below are what a local OmniRoute needs, and a local OmniRoute takes
/v1/chat/completions without credentials, so there is no key to set until the
endpoint is swapped for a hosted one:

    bench --site <site> set-config omniroute_api_key "..."   # only if required
    bench --site <site> set-config omniroute_base_url "http://host.docker.internal:20128/v1"
    bench --site <site> set-config omniroute_model "hermes-antigravity"
    bench --site <site> set-config mscast_briefing_to '["director@mscast.co.in"]'

Cost: the model sees a few thousand tokens a day.
"""

import json

import frappe
from frappe.utils import get_url

DEFAULT_BASE_URL = "http://host.docker.internal:20128/v1"
DEFAULT_MODEL = "hermes-antigravity"
TIMEOUT = 90

SYSTEM = """You are writing the morning note for the director of MSCAST Engineering,
a Pune company of under ten people that builds continuous casting machines to order.

You are given exceptions raised overnight by rules that compare documents in the
company's ERP against each other, plus the headline figures from the same morning's
management summary.

Write at most three short paragraphs in plain English.

- Open with the single thing that most needs doing today, and why.
- Group exceptions that are the same underlying mistake seen more than once.
- Say plainly if nothing needs attention. Do not manufacture urgency.
- Name documents exactly as given. Never invent a figure, a document or a name.
- No headings, no bullet lists, no greeting, no sign-off. Just the paragraphs.
- British English. No jargon the shop floor would not use."""


def daily_briefing():
    """Scheduled. Reads the overnight exceptions and emails the note."""
    data = collect()
    if not data["exceptions"] and not data["watch"]:
        body = "Nothing needs attention this morning. The overnight checks found no contradictions and no figure outside its normal range."
        model_used = "none needed"
    else:
        body, model_used = write_note(data)

    send(body, data, model_used)


def rupees(amount):
    """Money the way a Pune office says it out loud.

    The headline figures arrive from the report already worded this way; the
    exception rows arrive as bare floats. Handing the model both shapes is how
    a briefing ends up saying "285600.0" to a director, so both are worded here
    before anything is sent."""
    try:
        value = float(amount or 0)
    except (TypeError, ValueError):
        return None
    if not value:
        return None
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1e7:
        return "%sRs %.2f Cr" % (sign, value / 1e7)
    if value >= 1e5:
        return "%sRs %.2f L" % (sign, value / 1e5)
    return "%sRs %s" % (sign, "{:,.0f}".format(value))


def collect():
    """Everything the note is allowed to mention, and nothing else."""
    today = frappe.db.sql(
        "select date(convert_tz(utc_timestamp(),'+00:00','+05:30'))"
    )[0][0]

    exceptions = frappe.db.sql(
        """select rule_code, title, severity, owner_area, ref_doctype, ref_name,
                  details, suggested_action, amount, times_seen
           from `tabMSCAST Exception`
           where status in ('Open', 'Acknowledged')
           order by field(severity,'High','Medium','Low'), times_seen desc""",
        as_dict=True,
    )
    for row in exceptions:
        row["amount"] = rupees(row.get("amount"))

    watch, figures = [], []
    try:
        query = frappe.db.get_value("Report", "MSCAST Daily Management Summary", "query")
        for row in frappe.db.sql(query, as_dict=True):
            vals = list(row.values())
            area, indicator, value = vals[0], vals[1], vals[2]
            attention = vals[3] if len(vals) > 3 else ""
            figures.append({"area": area, "indicator": indicator, "value": value})
            if (attention or "").upper().startswith(("WATCH", "ACT")):
                watch.append({"indicator": indicator, "value": value, "why": attention})
    except Exception:
        frappe.log_error(frappe.get_traceback(), "MSCAST briefing: summary unavailable")

    return {"date": str(today), "exceptions": exceptions, "watch": watch, "figures": figures}


def auth_headers():
    """OmniRoute runs on the operator's own machine and takes /v1/chat/completions
    without credentials, so the key is optional. A hosted endpoint put in its place
    will need one - set it with:

        bench --site <site> set-config omniroute_api_key "..."

    and it is sent only if it is there."""
    headers = {"Content-Type": "application/json"}
    key = frappe.conf.get("omniroute_api_key")
    if key:
        headers["Authorization"] = "Bearer " + key
    return headers


def write_note(data):
    """Ask the model. Fall back to a plain list if it cannot be reached."""
    model = frappe.conf.get("omniroute_model") or DEFAULT_MODEL
    base = (frappe.conf.get("omniroute_base_url") or DEFAULT_BASE_URL).rstrip("/")

    material = json.dumps(
        {
            "date": data["date"],
            "exceptions": data["exceptions"],
            "indicators_flagged": data["watch"],
            "headline_figures": data["figures"],
        },
        indent=1,
        default=str,
    )

    try:
        import requests

        response = requests.post(
            base + "/chat/completions",
            headers=auth_headers(),
            json={
                "model": model,
                "messages": [
                    {"role": "system", "content": SYSTEM},
                    {"role": "user", "content": "Here is this morning's material:\n\n" + material},
                ],
                "temperature": 0.2,
                "max_tokens": 700,
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        text = (payload["choices"][0]["message"]["content"] or "").strip()
        if not text:
            raise ValueError("empty response")
        served = payload.get("model") or model
        label = model if served == model else "%s (served by %s)" % (model, served)
        return text, label
    except Exception:
        frappe.log_error(frappe.get_traceback(), "MSCAST briefing: model unavailable")
        return plain(data), "model unavailable - plain list sent instead"


@frappe.whitelist()
def test_connection():
    """One small request, so the wiring can be proved without waiting for 08:35."""
    model = frappe.conf.get("omniroute_model") or DEFAULT_MODEL
    base = (frappe.conf.get("omniroute_base_url") or DEFAULT_BASE_URL).rstrip("/")
    import time

    import requests

    started = time.time()
    response = requests.post(
        base + "/chat/completions",
        headers=auth_headers(),
        json={
            "model": model,
            "messages": [{"role": "user", "content": "Reply with exactly: MSCAST link up"}],
            "max_tokens": 24,
        },
        timeout=TIMEOUT,
    )
    took = round(time.time() - started, 2)
    if response.status_code != 200:
        return {"ok": False, "status": response.status_code, "endpoint": base,
                "combo": model, "detail": response.text[:400]}
    payload = response.json()
    return {
        "ok": True,
        "endpoint": base,
        "combo": model,
        "served_by": payload.get("model"),
        "reply": (payload["choices"][0]["message"]["content"] or "").strip(),
        "seconds": took,
        "usage": payload.get("usage"),
    }


def plain(data):
    """The fallback. Never pretty, always sent."""
    lines = []
    if data["exceptions"]:
        lines.append("Open exceptions this morning:")
        for e in data["exceptions"]:
            lines.append("  [%s] %s - %s %s" % (e.severity, e.title, e.ref_doctype or "", e.ref_name or ""))
    if data["watch"]:
        lines.append("")
        lines.append("Figures worth watching:")
        for w in data["watch"]:
            lines.append("  %s: %s (%s)" % (w["indicator"], w["value"], w["why"]))
    return "\n".join(lines) or "Nothing to report."


def send(body, data, model_used):
    recipients = frappe.conf.get("mscast_briefing_to")
    if isinstance(recipients, str):
        recipients = [recipients]
    if not recipients:
        recipients = [
            u.email
            for u in frappe.get_all(
                "User",
                filters={"enabled": 1, "user_type": "System User"},
                fields=["email"],
            )
            if u.email and "@" in u.email
        ][:1]
    if not recipients:
        return

    high = len([e for e in data["exceptions"] if e.severity == "High"])
    subject = "MSCAST: %s" % (
        "%d item%s need attention" % (len(data["exceptions"]), "" if len(data["exceptions"]) == 1 else "s")
        if data["exceptions"]
        else "nothing needs attention"
    )
    if high:
        subject += " (%d urgent)" % high

    rows = "".join(
        "<tr><td style='padding:6px 10px;border-bottom:1px solid #eee'>%s</td>"
        "<td style='padding:6px 10px;border-bottom:1px solid #eee'>%s</td>"
        "<td style='padding:6px 10px;border-bottom:1px solid #eee;white-space:nowrap'>%s %s</td></tr>"
        % (e.severity, frappe.utils.escape_html(e.title or ""), e.ref_doctype or "", e.ref_name or "")
        for e in data["exceptions"]
    )

    html = """
    <div style="font-family:'IBM Plex Sans',Arial,sans-serif;color:#1b1d21;max-width:720px">
      <p style="font-size:12px;color:#5b606b;margin:0 0 14px">%s</p>
      <div style="font-size:14.5px;line-height:1.55;white-space:pre-line">%s</div>
      %s
      <p style="font-size:11.5px;color:#5b606b;margin-top:22px;border-top:1px solid #e3e1db;padding-top:10px">
        Written by the overnight checks (%s). Every item above links to a document you can open.
        <a href="%s/app/mscast-exception">Open the full list</a>.
      </p>
    </div>
    """ % (
        data["date"],
        frappe.utils.escape_html(body),
        (
            "<table style='border-collapse:collapse;margin-top:18px;font-size:13px;width:100%%'>"
            "<tr><th align='left' style='padding:6px 10px;border-bottom:2px solid #1f3864'>Severity</th>"
            "<th align='left' style='padding:6px 10px;border-bottom:2px solid #1f3864'>Finding</th>"
            "<th align='left' style='padding:6px 10px;border-bottom:2px solid #1f3864'>Document</th></tr>"
            + rows
            + "</table>"
        )
        if rows
        else "",
        model_used,
        get_url(),
    )

    frappe.sendmail(recipients=recipients, subject=subject, message=html, now=True)
