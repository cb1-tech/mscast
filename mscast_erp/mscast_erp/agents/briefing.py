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

Configuration, in site_config.json (never in the repo):

    bench --site <site> set-config gemini_api_key "..."
    bench --site <site> set-config mscast_briefing_to '["director@mscast.co.in"]'
    bench --site <site> set-config gemini_model "gemini-3.1-flash-lite"

Cost: the model sees a few thousand tokens a day. At Flash-Lite rates that is a
few rupees a year, and the free tier covers it outright.
"""

import json

import frappe
from frappe.utils import get_url

DEFAULT_MODEL = "gemini-3.1-flash-lite"
ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
TIMEOUT = 45

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


def write_note(data):
    """Ask the model. Fall back to a plain list if it cannot be reached."""
    key = frappe.conf.get("gemini_api_key")
    if not key:
        return plain(data), "no API key configured"

    model = frappe.conf.get("gemini_model") or DEFAULT_MODEL
    prompt = SYSTEM + "\n\nHere is this morning's material:\n\n" + json.dumps(
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
            ENDPOINT.format(model=model),
            headers={"x-goog-api-key": key, "Content-Type": "application/json"},
            json={
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2, "maxOutputTokens": 700},
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        payload = response.json()
        text = payload["candidates"][0]["content"]["parts"][0]["text"].strip()
        if not text:
            raise ValueError("empty response")
        return text, model
    except Exception:
        frappe.log_error(frappe.get_traceback(), "MSCAST briefing: model unavailable")
        return plain(data), "model unavailable - plain list sent instead"


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
