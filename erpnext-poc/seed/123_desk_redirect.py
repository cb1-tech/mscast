import frappe
ws = frappe.get_doc("Website Settings")
keep = [(r.source, r.target) for r in (ws.get("route_redirects") or [])
        if r.source not in ("/", "/desk", "/app")]
ws.set("route_redirects", [])
for s, t in keep:
    ws.append("route_redirects", {"source": s, "target": t})
for s in ["/", "/desk", "/app"]:
    ws.append("route_redirects", {"source": s, "target": "/desk/mscast"})
ws.flags.ignore_mandatory = True
ws.save(ignore_permissions=True)
frappe.db.commit()
frappe.clear_cache()
print("redirects:", [(r.source, r.target) for r in ws.get("route_redirects")])
from frappe.website.path_resolver import PathResolver
for p in ["", "/", "/desk", "/app", "/desk/mscast", "/desk/mscast-accounts", "/login"]:
    try:
        r = PathResolver(p).resolve()
        print("  %-22s -> %s" % (p, r[0]))
    except Exception as e:
        print("  %-22s -> %s: %s" % (p, type(e).__name__, str(e)[:60]))
