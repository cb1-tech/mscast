# -*- coding: utf-8 -*-
"""Demonstration mode - the watermark on every MSCAST print.

Switched by site config, never by data:  bench --site <site> set-config mscast_demo 1

  demo site        every enabled MSCAST print format carries a DEMONSTRATION
                   banner and diagonal mark (review finding A2: the demo is on a
                   public URL and carries a real GSTIN);
  any other site   none does - a production invoice must never say DEMONSTRATION,
                   so the mark is actively removed if it is found.

It lives here, and runs from configure() after the fixtures, because it used to
be a seed script (186) and `bench migrate` re-imports the print-format fixtures:
an upgrade test on 21 Sep 2026 showed the watermark going from 15 formats to 0,
which would have put the real GSTIN on unmarked invoices on the public demo.
"""
import re
import frappe

MARK = "mscast-demo-watermark"
BANNER = """<!--%(m)s-->
<style>
  .%(m)s-bar {
    background: #7a1f1f; color: #fff; font-family: Arial, sans-serif;
    font-size: 11px; letter-spacing: .06em; text-transform: uppercase;
    padding: 5px 10px; margin: 0 0 10px 0; text-align: center; font-weight: bold;
  }
  .%(m)s-dia {
    position: fixed; top: 38%%; left: 0; width: 100%%; text-align: center;
    transform: rotate(-24deg); font-family: Arial, sans-serif; font-size: 62px;
    font-weight: bold; color: rgba(122,31,31,0.10); z-index: 9999;
    pointer-events: none; letter-spacing: .08em;
  }
</style>
<div class="%(m)s-bar">Demonstration system &mdash; not a tax invoice, not a legal document</div>
<div class="%(m)s-dia">DEMONSTRATION</div>
<!--/%(m)s-->
""" % {"m": MARK}

# Everything from the first marker to the closing one - or, for formats marked by
# the old seed script (no closing comment), from its <style> to the diagonal div.
_BLOCK = re.compile(r"<!--%s-->.*?<!--/%s-->\s*" % (MARK, MARK), re.S)
_LEGACY = re.compile(r"\s*<style>\s*\.%s-bar.*?<div class=\"%s-dia\">DEMONSTRATION</div>\s*"
                     % (MARK, MARK), re.S)


def is_demo():
    return bool(frappe.conf.get("mscast_demo"))


def _formats():
    return [p for p in frappe.get_all("Print Format",
                                      filters={"custom_format": 1, "disabled": 0},
                                      fields=["name", "html"])
            if p.name.startswith("MSCAST") and (p.html or "").strip()]


def strip(html):
    return _LEGACY.sub("", _BLOCK.sub("", html or ""))


def apply():
    demo, changed = is_demo(), []
    for p in _formats():
        clean = strip(p.html)
        want = (BANNER + clean) if demo else clean
        if want != p.html:
            frappe.db.set_value("Print Format", p.name, "html", want, update_modified=False)
            changed.append(p.name)
    frappe.db.commit()
    state = "demonstration site - watermark on" if demo else "not a demonstration site - no watermark"
    print("mscast_erp: %s%s" % (state, (", %d format(s) updated" % len(changed)) if changed else ", verified"))
    return changed
