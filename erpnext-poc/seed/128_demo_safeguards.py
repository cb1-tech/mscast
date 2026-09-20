# -*- coding: utf-8 -*-
"""Two safeguards for a demo that carries MSCAST's real branding on a public URL.

The company identity (name, GSTIN, CIN, letterhead) stays as it is - the POC is
meant to look like MSCAST's own system. These two fixes only remove the parts
that state invented facts about named individuals, or that could be mistaken for
a genuine statutory document.
"""
import frappe

# ---------------------------------------------------------------- 1. shareholders
# Real directors were carrying invented shareholdings. The company is real; the
# split is not, and nobody has confirmed it. Neutral placeholders until MSCAST
# supplies the actual register.
RENAME = {
    "Mustaque Ahmed N. Chandankeri": "Promoter A (DEMO)",
    "Aiqaz M. Chandankeri": "Promoter B (DEMO)",
    "Zameer Alam Chandankeri": "Promoter C (DEMO)",
}

if frappe.db.exists("DocType", "Shareholder"):
    for old, new in RENAME.items():
        if frappe.db.exists("Shareholder", old):
            frappe.rename_doc("Shareholder", old, new, force=True, ignore_permissions=True)
            frappe.db.set_value("Shareholder", new, "title", new, update_modified=False)
            print("renamed shareholder:", old, "->", new)
        elif frappe.db.exists("Shareholder", new):
            print("already a placeholder:", new)
        else:
            print("not found:", old)
    frappe.db.commit()
    print("shareholders now:", [s.name for s in frappe.get_all("Shareholder", fields=["name"])])

# ---------------------------------------------------------------- 2. watermark
WATERMARK = """
/* demo watermark - remove for production */
.print-format { position: relative; }
.print-format::before {
  content: "DEMONSTRATION \\2014 NOT A STATUTORY DOCUMENT";
  position: fixed;
  top: 42%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-24deg);
  font-size: 34px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: rgba(155, 28, 28, 0.13);
  white-space: nowrap;
  pointer-events: none;
  z-index: 0;
}
.print-format > * { position: relative; z-index: 1; }
"""

MARKER = "demo watermark - remove for production"
done, skipped = [], []
for pf in frappe.get_all("Print Format", filters={"standard": "No"}, fields=["name", "css", "disabled"]):
    css = pf.css or ""
    if MARKER in css:
        skipped.append(pf.name)
        continue
    frappe.db.set_value("Print Format", pf.name, "css", css + "\n" + WATERMARK, update_modified=False)
    done.append(pf.name)

frappe.db.commit()
frappe.clear_cache()
print()
print("watermarked %d print formats:" % len(done))
for n in done:
    print("   ", n)
if skipped:
    print("already watermarked:", skipped)
