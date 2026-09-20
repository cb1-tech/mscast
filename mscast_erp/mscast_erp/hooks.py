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

# Every customisation ships as a fixture. Nothing is configured by hand on a
# production site; if it is not in this list it does not survive a rebuild.
fixtures = [
    # The custom documents are no longer fixtures - they are app doctypes under
    # mscast/doctype/, so migrate creates their tables and upgrades keep them.
    {"dt": "Custom Field"},
    {"dt": "Property Setter"},
    {"dt": "Role", "filters": [["name", "like", "MSCAST%"]]},
    {"dt": "Workflow State"},
    {"dt": "Workflow Action Master"},
    {"dt": "Workflow"},
    {"dt": "Report", "filters": [["is_standard", "=", "No"]]},
    {"dt": "Print Format", "filters": [["standard", "=", "No"]]},
    {"dt": "Letter Head", "filters": [["name", "like", "MSCAST%"]]},
    {"dt": "Server Script"},
    {"dt": "Client Script"},
    {"dt": "Notification", "filters": [["is_standard", "=", 0]]},
    {"dt": "Email Template"},
    {"dt": "Custom HTML Block"},
    {"dt": "Dashboard Chart", "filters": [["is_standard", "=", 0]]},
    {"dt": "Workspace", "filters": [["name", "like", "MSCAST%"]]},
]

# The agent layer. The rules half is a Server Script inside the site and needs
# no network; this is the judgement half, which calls a model and emails the note.
# Times are the site's timezone (Asia/Kolkata in production).
scheduler_events = {
    "cron": {
        "35 8 * * *": ["mscast_erp.agents.briefing.daily_briefing"],
    }
}
