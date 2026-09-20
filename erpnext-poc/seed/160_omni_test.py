# -*- coding: utf-8 -*-
"""Prove the ERP can reach OmniRoute and get an answer back."""
import frappe, json

key = frappe.conf.get("omniroute_api_key")
print("endpoint:", frappe.conf.get("omniroute_base_url"))
print("combo   :", frappe.conf.get("omniroute_model"))
print("key     :", "set (%d chars)" % len(key) if key else "NOT SET - waiting on it")

if not key:
    raise SystemExit

import sys
sys.path.insert(0, "/home/frappe/frappe-bench/apps/mscast_erp")
from mscast_erp.agents import briefing

print()
print("=== handshake ===")
result = briefing.test_connection()
print(json.dumps(result, indent=1, default=str))

if result.get("ok"):
    print()
    print("=== the real thing: this morning's briefing ===")
    data = briefing.collect()
    print("exceptions on hand:", len(data["exceptions"]), "| flagged indicators:", len(data["watch"]))
    note, model_used = briefing.write_note(data)
    print("written by:", model_used)
    print()
    print(note)
