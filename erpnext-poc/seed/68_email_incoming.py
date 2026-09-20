"""MSCAST POC - 68: fill the incoming (IMAP) fields so the form saves whatever the toggles do.
Incoming stays OFF; the values are only there to satisfy validation."""
import socket, ssl
import frappe

log = lambda m: print("[mail5] " + m, flush=True)
IMAP = "imap.purelymail.com"

for host, port in ((IMAP, 993), ("imap.purelymail.com", 143)):
    try:
        s = socket.create_connection((host, port), 8)
        if port == 993:
            s = ssl.create_default_context().wrap_socket(s, server_hostname=host)
        log("%s:%d OK  %s" % (host, port, s.recv(200).decode("utf-8", "replace").strip()[:110]))
        s.close()
    except Exception as e:
        log("%s:%d FAILED %s" % (host, port, repr(e)[:140]))

d = frappe.get_doc("Email Account", "mscast-test")
log("auth_method = %r" % d.get("auth_method"))
d.email_server = IMAP
d.use_imap = 1
d.use_ssl = 1
d.incoming_port = 993
d.use_starttls = 0
d.enable_incoming = 0          # stays off - outgoing only for now
if d.meta.get_field("auth_method") and not d.get("auth_method"):
    d.auth_method = "Basic"
if d.meta.get_field("imap_folder") and not d.get("imap_folder"):
    d.append("imap_folder", {"folder_name": "INBOX", "append_to": "Communication"})
d.flags.ignore_permissions = True
d.flags.ignore_validate = True
d.flags.ignore_mandatory = True
d.save()
frappe.db.commit()

vals = frappe.db.get_value("Email Account", "mscast-test",
                           ["email_id", "auth_method", "enable_incoming", "email_server", "use_imap",
                            "use_ssl", "incoming_port", "enable_outgoing", "smtp_server", "smtp_port",
                            "use_ssl_for_outgoing", "default_outgoing"], as_dict=True)
for k, v in vals.items():
    log("  %-22s = %r" % (k, v))
log("imap folders: %s" % frappe.get_all("IMAP Folder", filters={"parent": "mscast-test"},
                                        fields=["folder_name", "append_to"]))
log("DONE - reload the form (Ctrl+Shift+R) and enter the password")
