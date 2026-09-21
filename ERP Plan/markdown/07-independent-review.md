---
title: "MSCAST ERP — Independent Review and Verification"
---

# MSCAST ERP — Independent Review and Verification

**Version 3.0 · 21 September 2026**

**What this is:** everything two outside reviews found wrong (or possibly wrong) with the POC, plus what our own testing found later. For each item: what was wrong, whether it is fixed, and who has to act next.

**How to read it:**

- **Status:** *Fixed* · *Not a problem* (the review was mistaken) · *Waiting on MSCAST* · *Waiting on the CA* · *Parked* (the implementer decided to leave it for now) · *Open*.
- **Ref** is the reviewer's label (A = confirmed by test, B = to be checked, C = big-picture). Other documents quote these labels, e.g. "B6". Items found by our own testing have no label.
- Every fix is also re-tested automatically every night by the system's 42 built-in checks. The technical list is in the POC README, section "Build checks".
- The work is unpaid, done for a family friend, and is not in competition with ERPens.

# 1. What the reviewers found

| What was wrong | Status | What was done | Who acts next | Ref |
|------------------------------|------------|----------------------------------|-----------------|-------|
| The public site accepted the default administrator password, and logins stay valid for 7 days | Parked | Default passwords no longer work. A new password and shorter login settings are due before real data or a server | The implementer, before go-live | A1 |
| The public demo shows MSCAST's real GST number and real director names | Fixed | Shareholders shown as "Promoter A / B / C". Every printed document carries a large DEMONSTRATION mark | — | A2 |
| "A machine was commissioned that was never dispatched" | Not a problem | It was dispatched (delivery note DN-26-00002) before commissioning. The other delivery note is a spares sale with no project | — | A3 |
| A draft payment reminder contradicted "nothing overdue" | Fixed | No reminders exist and no invoice is overdue | — | A4 |
| Retention money was booked against the wrong customer | Fixed | Wrong entry reversed; retention now booked against Ambika Steel Rolling Mills, whose contract has 10% retention | — | A5 |
| Different documents gave different counts of reports | Fixed | All documents say 28 custom reports, and a script checks the count | — | A6 |
| The rule "no supplier payment without a certified BRM" could be bypassed (by journal entry, by advance payment, by paying more than certified) — and it blocked electricity bills too | Fixed | The rule now covers every way of paying. Utilities, rent and statutory payees can be marked exempt | MSCAST: say which suppliers are exempt | B1 |
| Nobody had tested that a purchase order needs two people | Fixed | Tested: Purchase sends it, a director approves it; nobody can do both | — | B1 |
| A director can create a BRM, certify it and pay it — all alone | Waiting on MSCAST | Flagged every night as a warning. It is question Q21 | MSCAST: answer Q21 | B1 |
| A director can prepare a cost sheet (PCC), or check a customer PO, and then approve it alone | Waiting on MSCAST | Flagged every night as a warning. It is question Q20 | MSCAST: answer Q20 | B1 |
| "The director role is read-only, so every approval is broken" | Not a problem | Directors do approve; only the CA's login is read-only. The documents had described it wrongly and were corrected | — | B2 |
| The 45-day MSME payment clock may start on the wrong date | Waiting on the CA | Needs MSCAST's supplier terms and the CA's view | CA | B3 |
| Material sent free to fabricators is recorded as a stock transfer, not as job work under GST | Waiting on the CA | Needs MSCAST's practice and the CA's view | CA | B4 |
| The method for valuing unfinished project work may not meet accounting standards | Waiting on the CA | The CA must choose the method | CA | B5 |
| Tax and payroll may assume laws that do not apply to MSCAST | Waiting on the CA | PF is not deducted (removed on MSCAST's instruction: under 20 staff). ESI and gratuity stay. The CA must confirm there is no continuing PF registration, the 25.168% tax option and the lease heading | CA | B6 |
| Tax deducted by customers (2%) is not tracked | Waiting on the CA | Needs confirmation that customers deduct it | CA | B7 |
| A ₹24.7 lakh "stock adjustment" wrongly increased profit | Fixed | Opening stock moved to the correct account. Tax recalculated: ₹15,32,737 on profit before tax of ₹60,90,022 | — | B8 |
| Two numbering series for sales invoices | Fixed | One series now | — | B9 |
| "Tax deducted on one supplier bill doesn't add up" | Not a problem | The reviewer's arithmetic was wrong; the figures reconcile | — | B10 |
| Every MSCAST-specific form is our guess from the requirement document, because we have no real samples | Waiting on MSCAST | Samples requested in doc 10 (questions Q2–Q5). Present the POC as "our reading of your requirements" | MSCAST: send real PCC, Project MIS, BRM, MDM, DI and Annexure-I | C1 |
| Delivery was being measured against the ERPens proposal, with no signed scope or fee | Not a problem | This is unpaid work for a family friend, not a competing bid | — | C2 |
| The system needs more people to run it than MSCAST has, and shared logins would destroy the audit trail | Open | The role cards (doc 09) spread the work. MSCAST must name who does the monthly jobs | MSCAST | C3 |
| There was no way to move the POC to a real server | Fixed | Everything is packaged in an installable app. A clean system can be built in one step, and a backup restores in under 3 minutes (tested) | — | C4 |
| No support agreement | Not a problem | There is no commercial relationship to formalise | — | C5 |
| MSCAST depends on one person and his home equipment (PC in Japan, his domain, his mail) | Open | Reduced by the app, the nightly backups and checks, the documents and the DEV copy. Moving to a server in India is parked for now | MSCAST: name who runs the system; the implementer: server move later | C5 |
| The accounting set-up is ahead of the CA's decisions | Waiting on the CA | See B3–B7. Until the CA agrees, the books stay in Tally | CA; MSCAST to give the CA's contact | C6 |

# 2. What our own testing found later — all fixed

These were found by using the system the way MSCAST's staff would: logging in as each person, trying each step, installing it fresh, restoring backups. Each one now has a nightly check.

| What was wrong | What was done |
|--------------------------------------------------------------|--------------------------------------|
| A project kick-off could be approved even when the customer PO did not match the offer (one route skipped the check) | Every route into "approved" now requires the PO checklist to be complete |
| Four roles could not do their jobs: the drawing office could not open a drawing; Stores, Quality and the Purchase Executive had similar gaps | Each role can now do exactly what its role card says |
| The CA's read-only login could change or delete some records | The CA's login is read-only everywhere |
| Directors could not open some documents they are meant to approve (e.g. Mustaque could not open a kick-off) | Whoever approves a document can always open it |
| The app would have overwritten other components' settings when installed | The app now carries only MSCAST's own settings |
| The DEMONSTRATION mark disappeared after an upgrade | The mark is now part of the app and is checked every night |
| A fresh install was missing the drawing office role, one email alert, and the CA's access to the books | All added to the app; a script compares a fresh install with the running system |
| After restoring a backup, the saved email password stopped working | The restore now also puts back the key that unlocks saved passwords |
| After restoring onto another machine, MSCAST's custom rules were silently switched off | The restore now switches them on; a check confirms it |
| Links in emails did not open (they pointed to an internal address) | Links now use the public address |
| Eight demo customers were not marked as demo | Each now ends in "(DEMO)" |
| The MSCAST colours and styling did not load | Fixed, and the deploy script now refuses to finish unless they load |
| The drawing office could not open the Drawing Register | Fixed |
| Three reports crashed because of a "/" in their names | Renamed |
| Six reports failed when opened from the screen | Fixed |
| The home page always showed zero pending BRMs and zero open claims | Fixed |
| A BRM could be marked "Certified" without ticking quantity, rate, inspection and delivery | Not allowed any more: all four must be ticked |
| Printed documents showed login emails instead of people's names | Prints show full names |

# 3. Still open

- **MSCAST:** send real samples (PCC, Project MIS, BRM, MDM with DI and Annexure-I); answer Q20 and Q21; list suppliers exempt from the BRM rule; name who does the monthly jobs; send the Tally export; give the CA's contact. The request is doc 10.
- **The CA:** B3, B4, B5, B7; B6 (confirm no continuing PF registration; the tax option; the lease heading); C6.
- **Parked by the implementer:** new administrator password and shorter login settings (until real data or a server); the move to a server in India; the fix that lets screens refresh by themselves over the public link.
- **Before go-live:** a data migration plan from Tally, training material, and a named person at MSCAST who looks after the system.

# 4. Rules we now follow because of these findings

- A finding is tested on the running system, logged in as the real person, before it is accepted or rejected.
- Every fix gets a nightly check, and the check must be seen to fail before the fix.
- Every setting lives in the installable app, never only in the database, so a fresh install is identical.
- A restore also puts back the three settings that are not in the database backup (the password key, the custom-rules switch, the public address).
- Permissions are written as a complete set for every role, never one row at a time.
