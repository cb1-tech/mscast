#!/usr/bin/env bash
set -euo pipefail
cd /mnt/d/MSCAST
git add -A erpnext-poc/seed/102_test_harness.py erpnext-poc/scripts/
git commit -F- <<'MSG'
T6g: ask the segregation question in the form an auditor would

T6e compares workflow TRANSITION roles. Creating a document is a permission,
not a transition, so a user can hold create rights on a document and the
approval role for that same document and never appear in T6e at all.

That is not hypothetical. Both directors hold Projects Manager, which can
create a BRM, and MSCAST Director, which certifies one. They also hold
Accounts Manager, which marks it paid. One person can therefore take a
supplier bill from creation to paid without anybody else touching it, and
T6e saw no overlap because "prepare a BRM" is not a workflow transition.

Three delivered documents said the opposite - "Purchase prepare, a director
certifies, Accounts pay. Three different hands" - and said the person who
prepares a BRM cannot certify it. Both claims were wrong. The documents are
being corrected to state what is actually true.

The hard controls are unaffected and still pass: a bill with no certified BRM
cannot be paid (T6a), the drawing release sequence holds, and the kick-off
checklist holds. What is weaker than claimed is the separation of duties
around who may certify, not the payment block itself.

T6g warns rather than fails: for a company this size, directors holding
preparing roles is a decision, not a defect. But it is now a decision someone
has made rather than one nobody knew they were making.

Harness 25 PASS, 2 WARN, 0 FAIL of 27.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01G3y6MpPfn3Nhms7B2xeYDR
MSG
git log --oneline -1
