# -*- coding: utf-8 -*-
"""Bring sheet 14 of the data collection workbook in line with the real roles.

Two problems with it as written:

  - the example row said "Purchase orders up to INR 5 lakh", implying approval
    limits by value. There are none. Approval is by role, and a value threshold
    is not configured anywhere. Asking MSCAST to think in limits invites them to
    send back something the system cannot honour.

  - the Role column was free text with no list to choose from, so whatever came
    back would need translating anyway.

The roles reference goes in columns H onward, clear of the COUNTA ranges on the
checklist sheet, which count A6:A205 and must not be disturbed.
"""
import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill

PATH = "/mnt/d/MSCAST/ERP Plan/MSCAST ERP - Data Collection Workbook.xlsx"
wb = openpyxl.load_workbook(PATH)
ws = wb["14 Users"]

# --- the subtitle, and the example row -------------------------------------
ws["A2"] = ("Who gets a login and what they are allowed to do. Keep it to people who will "
            "actually use the system. Pick a role from the list on the right - approval "
            "follows the role, not the person.")

# data starts at row 6; row 5 carries the grey example
ws["A5"] = "R. Deshmukh"
ws["B5"] = "r.deshmukh@mscast.example"
ws["C5"] = "Purchase Manager"
ws["D5"] = "No - raises purchase orders, a director approves them"
ws["E5"] = "<- example row, delete before sending back"

# --- the roles reference ----------------------------------------------------
HEAD = Font(bold=True, color="FFFFFF")
BAND = PatternFill("solid", fgColor="1F3864")
SUB = Font(bold=True)

ws["H1"] = "The roles, and what each one may approve"
ws["H1"].font = Font(bold=True, size=12)
ws["H2"] = ("Give each person exactly one of these. If someone genuinely does two jobs, "
            "put both and say so in Notes - but read the last block first.")
ws["H2"].alignment = Alignment(wrap_text=True, vertical="top")
ws.merge_cells("H2:K2")

rows = [
    ("Role", "What they do", "What they may approve"),
    ("MSCAST Director", "Runs the company", "Cost sheets, purchase orders, kick-offs, bill certification"),
    ("Projects Manager", "Cost sheets, kick-offs, project schedule", "Customer approval and release of drawings"),
    ("Design User", "Drawing office - drawings, transmittals, MDF", "Issue a drawing for customer approval (not release it)"),
    ("Purchase Manager", "RFQs, purchase orders, supplier masters, prepares bills", "Reject a PO or a bill. Cannot approve either"),
    ("Purchase User", "Material requests, RFQs, raises purchase orders", "Nothing"),
    ("Accounts Manager", "Invoices, payments, GST, month end", "Verify a customer PO; release a certified bill for payment"),
    ("Accounts User", "Enters invoices, prepares payments", "Nothing"),
    ("Stock User", "Receipts, issues, free issue, dispatch", "Nothing"),
    ("Quality Manager", "Inspection plans and results, commissioning", "Inspection results, including accepted deviations"),
    ("HR Manager", "Employees, attendance, leave, payroll", "Leave"),
    ("Auditor", "Your CA. Reads everything, writes nothing", "Nothing - read only, by design"),
]
start = 4
for i, (a, b, c) in enumerate(rows):
    r = start + i
    ws.cell(r, 8, a); ws.cell(r, 9, b); ws.cell(r, 10, c)
    if i == 0:
        for col in (8, 9, 10):
            ws.cell(r, col).font = HEAD
            ws.cell(r, col).fill = BAND
    ws.cell(r, 8).font = SUB if i else HEAD
    for col in (8, 9, 10):
        ws.cell(r, col).alignment = Alignment(wrap_text=True, vertical="top")

note_at = start + len(rows) + 1
ws.cell(note_at, 8, "Three things the system will refuse, whoever asks")
ws.cell(note_at, 8).font = Font(bold=True, size=11)
notes = [
    "A supplier bill with no certified Billing Routing Memo cannot be paid.",
    "The person who raises a purchase order cannot approve it.",
    "A drawing cannot be released for manufacture until the customer has approved it.",
    "",
    "There are no approval limits by value. Approval follows the role. If MSCAST wants "
    "a rupee threshold, say so and it can be built - but it does not exist today, so "
    "please do not assume one when filling this in.",
    "",
    "One person, several roles: this works, and in a company this size it is normal. "
    "Be aware that it removes the separation above - someone holding both Purchase User "
    "and MSCAST Director can raise a purchase order and approve it. Say in Notes where "
    "that is intended.",
]
for j, text in enumerate(notes):
    c = ws.cell(note_at + 1 + j, 8, text)
    c.alignment = Alignment(wrap_text=True, vertical="top")
    ws.merge_cells(start_row=note_at + 1 + j, start_column=8,
                   end_row=note_at + 1 + j, end_column=11)

for col, width in (("H", 20), ("I", 42), ("J", 52), ("K", 14)):
    ws.column_dimensions[col].width = width

wb.save(PATH)
print("sheet 14 updated")
print("  example row now names a real role and a truthful approval answer")
print("  roles reference added in H:K, %d roles" % (len(rows) - 1))
print("  COUNTA ranges on the checklist sheet (A6:A205) untouched")
