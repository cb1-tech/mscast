# -*- coding: utf-8 -*-
"""Pick the model for the morning briefing on evidence, not on the spec sheet.

Sends the identical prompt the 08:35 job sends through each candidate exposed
by the local OmniRoute, and prints what came back alongside latency and tokens.

The job is narrow: read the exception rows and say which one the director acts
on first. So the thing to judge in the output below is the ORDERING and whether
every document number is real - not the prose.
"""
import frappe, json, sys, time

sys.path.insert(0, "/home/frappe/frappe-bench/apps/mscast_erp")
from mscast_erp.agents import briefing

import requests

base = (frappe.conf.get("omniroute_base_url") or briefing.DEFAULT_BASE_URL).rstrip("/")

CANDIDATES = [
    ("hermes-antigravity", "current setting - a combo, picks for us"),
    ("antigravity/gemini-3.1-flash-lite", "cheapest named Gemini"),
    ("antigravity/gemini-3.7-flash-medium", "newer Flash, more thinking"),
]
# dropped after the first run, with reasons, so they are not tried again by habit:
#   antigravity/gemini-3.7-flash-low  - returned 39 tokens and stopped mid-sentence
#   antigravity/gemini-3.1-pro-low    - 26s
#   antigravity/gemini-pro-agent      - 42s
# Both Pro tiers wrote well but a briefing does not need a minute of thinking,
# and the scheduler holds a worker for the duration.

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
messages = [
    {"role": "system", "content": briefing.SYSTEM},
    {"role": "user", "content": "Here is this morning's material:\n\n" + material},
]

# the document numbers the rules half actually found - anything else is invented
real_docs = set()
for e in data["exceptions"]:
    if e.get("ref_name"):
        real_docs.add(str(e["ref_name"]))
if not real_docs:
    raise SystemExit("refusing to judge citations: no ref_name found on any "
                     "exception row, so every number would look invented")

print("material: %d exceptions, %d flagged indicators, %d figures"
      % (len(data["exceptions"]), len(data["watch"]), len(data["figures"])))
print("documents the rules found:", ", ".join(sorted(real_docs)) or "(none)")
print()

rows = []
for model, why in CANDIDATES:
    print("=" * 78)
    print("%s  -  %s" % (model, why))
    print("=" * 78)
    started = time.time()
    try:
        r = requests.post(
            base + "/chat/completions",
            headers=briefing.auth_headers(),
            json={"model": model, "messages": messages,
                  "temperature": 0.2, "max_tokens": 700},
            timeout=120,
        )
        took = round(time.time() - started, 2)
        if r.status_code != 200:
            print("  HTTP %s  %s" % (r.status_code, r.text[:200]))
            rows.append((model, "HTTP %s" % r.status_code, took, 0, 0, "-"))
            print()
            continue
        p = r.json()
        note = (p["choices"][0]["message"]["content"] or "").strip()
        u = p.get("usage") or {}
        served = p.get("model") or "?"
        # every MSCAST-looking document id the note mentions must be one we found
        import re
        cited = set(re.findall(r"\b[A-Z][A-Z0-9-]{4,}-\d{3,}\b", note))
        invented = sorted(c for c in cited if c not in real_docs)
        print("  served by : %s   %.2fs   %s in / %s out"
              % (served, took, u.get("prompt_tokens", "?"), u.get("completion_tokens", "?")))
        print("  invented document numbers:", ", ".join(invented) if invented else "none")
        print("  raw floats left unformatted:",
              ", ".join(sorted(set(re.findall(r"\b\d+\.0\b", note)))) or "none")
        if frappe.conf.get("bakeoff_quiet"):
            print("  (note suppressed)")
        else:
            print()
            print(note)
        print()
        rows.append((model, served, took, u.get("prompt_tokens", 0),
                     u.get("completion_tokens", 0),
                     ("%d INVENTED" % len(invented)) if invented else "clean"))
    except Exception as exc:
        print("  failed:", str(exc)[:200])
        rows.append((model, "failed", round(time.time() - started, 2), 0, 0, "-"))
        print()

print("=" * 78)
print("%-38s %-22s %7s %6s %6s %s" % ("model", "served by", "secs", "in", "out", "citations"))
for model, served, took, pin, pout, verdict in rows:
    print("%-38s %-22s %7.2f %6s %6s %s" % (model, str(served)[:22], took, pin, pout, verdict))
