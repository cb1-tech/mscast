#!/usr/bin/env bash
set -euo pipefail
cd /mnt/d/MSCAST
rm -f erpnext-poc/scripts/cleanup.sh
git add -A
git commit -F- <<'MSG'
Rebuild the document set against the running system, and record what it got wrong

Every document is regenerated from the live configuration rather than from the
previous document. The .docx set on disk was three versions behind and the
traceability workbook was still at v1.5, claiming 15 doctypes where there are 25
and 23 build checks where there are 27.

The substantive change is not a version bump. Three delivered documents claimed
a separation of duties that does not exist - "Purchase prepare, a director
certifies, Accounts pay. Three different hands" - and it is not true. A director
holds a role that can create a BRM, the role that certifies one and the role
that marks it paid. T6g now reports it, and the documents say what the system
actually does. The decision goes to MSCAST as Q21.

The independent review is left unedited and gains a status section. Doc 01 is
marked superseded from section 5 onward rather than rewritten, because it is a
pre-build strategy record and revising it would destroy that. Its one hard
error - describing MSCAST Director as a read-only role - is corrected in place.

Also closed: the repo and the project had drifted into two different READMEs.
One source now.

Documents: Client Setup Guide v2.2, SOPs v2.1, Role Cards v1.2, Traceability
v1.7 (+ workbook), Cutover Runbook v2.1, Data Request Note v1.1, Implementation
Report and Independent Review restated, Strategy marked superseded in part.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G3y6MpPfn3Nhms7B2xeYDR
MSG
git log --oneline -1
echo
git status --short | head -5
echo "(clean if nothing above)"
