app_name = "mscast_erp"
app_title = "MSCAST ERP"
app_publisher = "MSCAST Engineering Pvt Ltd"
app_description = "Configuration, custom documents, reports and controls for an engineer-to-order casting machine builder"
app_email = "it@mscast.co.in"
app_license = "mit"
required_apps = ["erpnext"]

# The desk theme. Loading it here is what makes it apply on every page,
# including a cold deep link, rather than only after the home page has run.
app_include_css = "/assets/mscast_erp/css/mscast.css"

after_install = "mscast_erp.install.after_install"
after_migrate = "mscast_erp.install.after_migrate"

# Every customisation that is MSCAST's ships as a fixture - and ONLY what is
# MSCAST's. Fixtures are re-imported on every `bench migrate` and overwrite the
# live rows, and mscast_erp migrates last. So a fixture that captures another
# app's record freezes it: when that app ships a change, our stale copy puts the
# old one back. Until 21 Sep 2026 these filters were catch-alls and the app
# shipped 663 of India Compliance's, ERPNext's and HRMS's custom fields, 344 of
# their property setters, and 7 of their email templates. One had already gone
# stale - India Compliance had reordered the GST rate list on Company since the
# export. Measured against a site built WITHOUT this app; see
# erpnext-poc/evidence/baseline-without-mscast.json.
#
# Ownership is recorded in the `module` field (MSCAST) for custom fields and
# property setters, and in the name for everything else. Anything created for
# MSCAST must follow that, or it will not be exported - which is the safe
# failure: a missing record shows up in the build checks, a captured one does not.
_OURS = [["module", "=", "MSCAST"]]
_STANDARD_STATES = ["Approved", "Pending", "Rejected"]
_STANDARD_ACTIONS = ["Approve", "Reject", "Review"]

fixtures = [
    # The custom documents are app doctypes under mscast/doctype/, not fixtures.
    {"dt": "Custom Field", "filters": _OURS},
    {"dt": "Property Setter", "filters": _OURS},
    # Design User is ours but not MSCAST-prefixed: it was left out of the package
    # and a fresh install had no drawing office (found 21 Sep 2026).
    {"dt": "Role", "or_filters": [["name", "like", "MSCAST%"], ["name", "=", "Design User"]]},
    {"dt": "Workflow State", "filters": [["name", "not in", _STANDARD_STATES]]},
    {"dt": "Workflow Action Master", "filters": [["name", "not in", _STANDARD_ACTIONS]]},
    {"dt": "Workflow"},
    {"dt": "Report", "filters": [["is_standard", "=", "No"]]},
    {"dt": "Print Format", "filters": [["standard", "=", "No"]]},
    {"dt": "Letter Head", "filters": [["name", "like", "MSCAST%"]]},
    {"dt": "Server Script"},
    {"dt": "Client Script"},
    {"dt": "Notification", "filters": [["name", "like", "MSCAST%"]]},
    {"dt": "Email Template", "filters": [["name", "like", "MSCAST%"]]},
    {"dt": "Custom HTML Block"},
    {"dt": "Dashboard Chart", "filters": [["is_standard", "=", 0]]},
    {"dt": "Workspace", "filters": [["name", "like", "MSCAST%"]]},
]

# The controls. A rule that decides whether money leaves the company belongs in
# version control and in the release, not in a Server Script edited in the desk:
# it has to be reviewable, diffable and testable. `before_submit` is the right
# hook because it fires on the real submit path whatever raised the document -
# desk, API or background job - and a throw there leaves nothing half-posted.
doc_events = {
    "Payment Entry": {
        "before_submit": "mscast_erp.controls.brm_payment.payment_entry",
    },
    "Journal Entry": {
        "before_submit": "mscast_erp.controls.brm_payment.journal_entry",
    },
}

# The agent layer. The rules half is a Server Script inside the site and needs
# no network; this is the judgement half, which calls a model and emails the note.
# Times are the site's timezone (Asia/Kolkata in production).
scheduler_events = {
    "cron": {
        "35 8 * * *": ["mscast_erp.agents.briefing.daily_briefing"],
    }
}
