# -*- coding: utf-8 -*-
"""Mark every client-facing print as a demonstration.

Review finding A2. The demo is on a public URL and carries MSCAST's real GSTIN,
so a fictional invoice printed from it looks like a real tax document. The GSTIN
itself is a separate decision; this makes the prints say what they are.

Idempotent: a format already carrying the marker is left alone.
"""
import frappe

MARK = "mscast-demo-watermark"

BANNER = """
<style>
  .%s-bar {
    background: #7a1f1f; color: #fff; font-family: Arial, sans-serif;
    font-size: 11px; letter-spacing: .06em; text-transform: uppercase;
    padding: 5px 10px; margin: 0 0 10px 0; text-align: center; font-weight: bold;
  }
  .%s-dia {
    position: fixed; top: 38%%; left: 0; width: 100%%; text-align: center;
    transform: rotate(-24deg); font-family: Arial, sans-serif; font-size: 62px;
    font-weight: bold; color: rgba(122,31,31,0.10); z-index: 9999;
    pointer-events: none; letter-spacing: .08em;
  }
</style>
<div class="%s-bar">Demonstration system &mdash; not a tax invoice, not a legal document</div>
<div class="%s-dia">DEMONSTRATION</div>
""" % (MARK, MARK, MARK, MARK)


def main():
    formats = frappe.get_all("Print Format",
                             filters={"custom_format": 1},
                             fields=["name", "html", "doc_type"])
    done = skipped = empty = 0
    for pf in formats:
        if not pf.name.startswith("MSCAST"):
            continue
        html = pf.html or ""
        if MARK in html:
            print("   already marked : %s" % pf.name)
            skipped += 1
            continue
        if not html.strip():
            print("   no html        : %s" % pf.name)
            empty += 1
            continue
        frappe.db.set_value("Print Format", pf.name, "html", BANNER + html,
                            update_modified=False)
        print("   marked         : %-40s (%s)" % (pf.name, pf.doc_type))
        done += 1

    frappe.db.commit()
    print("")
    print("   %d marked, %d already had it, %d had no html" % (done, skipped, empty))

    left = [pf.name for pf in frappe.get_all("Print Format",
                                             filters={"custom_format": 1},
                                             fields=["name", "html"])
            if pf.name.startswith("MSCAST") and MARK not in (pf.html or "")]
    print("   MSCAST formats still unmarked: %s" % (left or "none"))


main()
