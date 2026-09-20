# MSCAST ERP

The MSCAST configuration for ERPNext v16 as an installable app: custom
documents, reports, print formats, workflows, controls and the desk theme.

Everything here is **configuration**. No demo or company data is included.
Installing this app on an empty ERPNext site reproduces the system; the
business data is loaded separately.

## What it contains

| Area | What ships |
|---|---|
| Custom documents | PCC (Purchase Cost Calculation), MDF, BRM, MDM, Delivery Instruction, Drawing + revisions, Inspection Plan, Transmittal, Spares Handover, Commissioning Report, Project Certificate, Client Claim, Customer Asset, Project Kickoff, Archival Log, Bid Outcome, Installed Machine, Exception |
| Reports | 28 query reports including the Schedule III statements, the eleven ratios, ageing, notes to accounts, MSME 45-day dues, PO vs PCC variance, project MIS, WIP valuation and the daily management summary |
| Controls | 4 workflows (PCC approval, PO approval, BRM certification, project kick-off) and the server script that refuses a payment against an uncertified supplier bill |
| Agents | The nightly exception sweep - cross-document rules that look for states that cannot both be true |
| Interface | The MSCAST home page, role-scoped workspaces, and the desk theme |

## Requirements

- Frappe v16, ERPNext v16
- India Compliance, Frappe HR, India Payroll (installed separately)

## Install

```bash
bench get-app https://github.com/cb1-tech/mscast
bench --site <site> install-app mscast_erp
bench --site <site> migrate
```

The `migrate` is not optional. Installing the app creates the MSCAST documents
from the JSON definitions under `mscast/doctype/`, and `migrate` is what creates
their tables and then imports the fixtures that depend on them - custom fields,
workflows and notifications that hang off those documents. Run it once and check
the counts; a fixture file that mentions a document type which did not exist yet
is skipped as a whole file, not row by row.

Two things to know if something does not appear:

- Every doctype JSON carries a `modified` timestamp. The framework compares it
  against the database to decide whether to import the file. Strip it and the
  file is silently skipped.
- Fixtures are imported in filename order, which is why the documents ship as
  app doctypes rather than as a `DocType` fixture.

`after_install` hides the stock workspaces MSCAST does not use and points the
site root at the MSCAST home workspace. Neither step deletes anything: every
hidden workspace's forms and reports still open from search.

## Changing configuration

Change it on a site, then export it back:

```bash
bench --site <site> export-fixtures --app mscast_erp
```

Commit the diff. Anything configured by hand on production and not exported
does not survive a rebuild.
