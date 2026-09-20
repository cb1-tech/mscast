#!/usr/bin/env bash
# Frappe builds a doctype's controller class name by stripping spaces and
# hyphens from the DocType name itself (base_document.import_controller):
#
#     classname = doctype.replace(" ", "").replace("-", "")
#
# so "MSCAST Transmittal" must be MSCASTTransmittal, not MscastTransmittal.
# The generator that first wrote these controllers used title case and got it
# wrong for all 26. It stayed hidden while the DocType rows carried custom=1,
# because get_controller returns a plain Document for a custom doctype and
# never imports anything. Installing the app set custom=0, and every print
# format and form for those doctypes started raising ImportError.
#
# This derives the correct name from each doctype's own JSON rather than
# guessing, and rewrites the class statement in place.
set -euo pipefail

ROOT=/mnt/d/MSCAST/mscast_erp/mscast_erp/mscast/doctype
python3 - "$ROOT" <<'PY'
import json, os, re, sys

root = sys.argv[1]
changed = 0
for folder in sorted(os.listdir(root)):
    d = os.path.join(root, folder)
    js, py = os.path.join(d, folder + ".json"), os.path.join(d, folder + ".py")
    if not (os.path.isfile(js) and os.path.isfile(py)):
        continue
    name = json.load(open(js, encoding="utf-8")).get("name")
    if not name:
        continue
    want = name.replace(" ", "").replace("-", "")
    src = open(py, encoding="utf-8").read()
    m = re.search(r"^class\s+(\w+)\s*\(", src, re.M)
    if not m:
        print("  %-34s no class statement found" % folder)
        continue
    have = m.group(1)
    if have == want:
        continue
    src = re.sub(r"^class\s+%s\s*\(" % re.escape(have), "class %s(" % want, src, flags=re.M)
    open(py, "w", encoding="utf-8").write(src)
    print("  %-34s %s -> %s" % (name, have, want))
    changed += 1
print("\n%d controller%s renamed" % (changed, "" if changed == 1 else "s"))
PY
