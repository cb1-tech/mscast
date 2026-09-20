"""MSCAST POC - 106: what UI customisation levers exist in this install?"""
import frappe
log = lambda m: print("[ui] " + m, flush=True)

log("=== workspaces (the sidebar = the 'cluttered navigation') ===")
ws = frappe.get_all("Workspace", fields=["name", "title", "module", "public", "is_hidden",
                                         "for_user", "parent_page", "sequence_id"],
                    order_by="sequence_id asc")
log("total workspaces: %d  (public: %d, hidden: %d)"
    % (len(ws), sum(1 for w in ws if w.public), sum(1 for w in ws if w.is_hidden)))
for w in ws[:40]:
    log("  %-28s module=%-18s public=%s hidden=%s parent=%s"
        % (w.title[:28], (w.module or "-")[:18], w.public, w.is_hidden, w.parent_page or "-"))

log("=== mechanisms available ===")
for dt in ["Custom HTML Block", "Workspace Custom Block", "Website Theme", "Page", "Dashboard",
           "Dashboard Chart", "Number Card", "Portal Menu Item", "Navbar Settings", "Website Settings",
           "Workspace Shortcut", "Workspace Link", "Client Script", "Website Script"]:
    log("  %-26s %s" % (dt, "AVAILABLE (%d records)" % frappe.db.count(dt)
                        if frappe.db.exists("DocType", dt) else "not in this build"))

log("=== workspace building blocks on the Workspace doctype ===")
m = frappe.get_meta("Workspace")
log("  fields: %s" % [f.fieldname for f in m.fields if f.fieldtype in ("Table", "Code", "Check", "Data")][:24])

log("=== current MSCAST workspace content ===")
if frappe.db.exists("Workspace", "MSCAST"):
    w = frappe.get_doc("Workspace", "MSCAST")
    log("  shortcuts: %d, links: %d, number_cards: %d, charts: %d"
        % (len(w.get("shortcuts") or []), len(w.get("links") or []),
           len(w.get("number_cards") or []), len(w.get("charts") or [])))
    log("  content blocks: %s" % (len(w.content or "")))

log("=== branding / theme ===")
for k in ("app_name", "app_logo_url", "banner_image"):
    try:
        log("  Navbar/Website %s = %s" % (k, frappe.db.get_single_value("Website Settings", k)))
    except Exception:
        pass
log("  theme default: %s" % frappe.db.get_single_value("Website Settings", "app_name"))
log("DONE")
