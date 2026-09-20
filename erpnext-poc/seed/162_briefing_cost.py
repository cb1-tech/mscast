# -*- coding: utf-8 -*-
"""What will the morning briefing cost once it runs against a paid endpoint?

Measures one real briefing - the same prompt the 08:35 job sends - and prices a
year of it against the candidate models. Run it whenever the prompt or the
number of exception rules changes, because both move the input token count.
"""
import frappe, json, sys

sys.path.insert(0, "/home/frappe/frappe-bench/apps/mscast_erp")
from mscast_erp.agents import briefing

base = (frappe.conf.get("omniroute_base_url") or briefing.DEFAULT_BASE_URL).rstrip("/")
model = frappe.conf.get("omniroute_model") or briefing.DEFAULT_MODEL

data = briefing.collect()
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

import requests

response = requests.post(
    base + "/chat/completions",
    headers=briefing.auth_headers(),
    json={
        "model": model,
        "messages": [
            {"role": "system", "content": briefing.SYSTEM},
            {"role": "user", "content": "Here is this morning's material:\n\n" + material},
        ],
        "temperature": 0.2,
        "max_tokens": 700,
    },
    timeout=briefing.TIMEOUT,
)
response.raise_for_status()
payload = response.json()
usage = payload.get("usage") or {}

prompt_tokens = usage.get("prompt_tokens", 0)
completion_tokens = usage.get("completion_tokens", 0)

print("one briefing, measured against the live endpoint")
print("  exceptions on hand    :", len(data["exceptions"]))
print("  indicators flagged    :", len(data["watch"]))
print("  headline figures      :", len(data["figures"]))
print("  prompt tokens         :", prompt_tokens)
print("  completion tokens     :", completion_tokens)
print()

# input $/M, output $/M - from ai.google.dev pricing, September 2026
PRICES = [
    ("gemini-2.5-flash-lite", 0.10, 0.40),
    ("gemini-3.1-flash-lite", 0.25, 1.50),
    ("gemini-3.5-flash-lite", 0.30, 2.50),
    ("gemini-3-flash", 0.50, 3.00),
]
RUNS_PER_YEAR = 365
USD_INR = 88  # indicative; for a sense of scale only

print("a year of one briefing a day (%d runs)" % RUNS_PER_YEAR)
print("  %-24s %10s %12s %12s" % ("model", "per run", "per year", "per year"))
print("  %-24s %10s %12s %12s" % ("", "USD", "USD", "INR"))
for name, pin, pout in PRICES:
    per_run = prompt_tokens / 1e6 * pin + completion_tokens / 1e6 * pout
    per_year = per_run * RUNS_PER_YEAR
    print("  %-24s %10.5f %12.2f %12.0f" % (name, per_run, per_year, per_year * USD_INR))

print()
print("note: the exception sweep itself is a Server Script - no tokens, no network.")
print("      only the judgement half costs anything, and only once a day.")
