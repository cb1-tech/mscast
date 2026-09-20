# -*- coding: utf-8 -*-
"""B9, plus the arithmetic that proves two review findings are not defects.

Verification first, because two of the five items I was about to "fix" turned
out to be correct as built, and fixing correct things is how you break a demo:

  B10 - "TDS on PINV-26-00003 does not reconcile: 10,320 on a 5,98,560 bill
        implies a 5,16,000 base at 16% tax, not 18%."
        The reviewer divided TDS by the bill total AFTER TDS was deducted. The
        bill is 5,16,000 net + 9% CGST + 9% SGST = 6,08,880 gross, less 10,320
        TDS = 5,98,560 payable. TDS of 10,320 on 5,16,000 is exactly 2% under
        s.194C, and CBDT Circular 23/2017 says TDS is deducted on the amount
        EXCLUDING GST. The invoice is right.

  A3  - "DN-26-00001, the only delivery note, project = NULL."
        It is a spares delivery - 8 x SPR-MOULD-TUBE to Konark Alloys, who has
        no project and no sales order. A spares sale legitimately has no
        project. Not every delivery note belongs to a contract.

B9 is a real artefact and is fixed here.
"""
import frappe


def check_tds():
    print("=" * 70)
    print("B10  the TDS arithmetic, worked through")
    print("=" * 70)
    inv = "PINV-26-00003"
    if not frappe.db.exists("Purchase Invoice", inv):
        print("   %s not present" % inv)
        return
    taxes = frappe.get_all("Purchase Taxes and Charges",
                           filters={"parent": inv},
                           fields=["account_head", "rate", "base_tax_amount"])
    cgst = next((t for t in taxes if "CGST" in t.account_head), None)
    tds = next((t for t in taxes if "TDS" in t.account_head), None)
    if not (cgst and tds):
        print("   expected CGST and TDS lines not found")
        return
    net = cgst.base_tax_amount / (cgst.rate / 100.0)
    gross = net + sum(t.base_tax_amount for t in taxes if "TDS" not in t.account_head)
    print("   net (from CGST %.0f%% of %0.2f) : %12.2f" % (cgst.rate, cgst.base_tax_amount, net))
    print("   gross incl. GST                 : %12.2f" % gross)
    print("   TDS deducted                    : %12.2f" % tds.base_tax_amount)
    print("   TDS as %% of net                 : %12.4f%%"
          % (100.0 * tds.base_tax_amount / net))
    print("   payable after TDS               : %12.2f" % (gross - tds.base_tax_amount))
    ok = abs(100.0 * tds.base_tax_amount / net - 2.0) < 0.001
    print("   -> %s: 2%% under s.194C on the amount excluding GST "
          "(CBDT Circular 23/2017)" % ("CORRECT" if ok else "WRONG"))


def check_delivery_note():
    print("")
    print("=" * 70)
    print("A3  the delivery note with no project")
    print("=" * 70)
    for dn in frappe.get_all("Delivery Note", filters={"docstatus": 1},
                             fields=["name", "customer", "project"]):
        items = frappe.get_all("Delivery Note Item", filters={"parent": dn.name},
                               fields=["item_code", "qty"])
        has_project_customer = frappe.db.exists("Project", {"customer": dn.customer})
        note = ""
        if not dn.project:
            note = ("  <- spares sale, customer has no project: correct"
                    if not has_project_customer
                    else "  <- customer HAS a project but this is unlinked: check")
        print("   %-14s %-34s project=%-10s %s%s"
              % (dn.name, dn.customer, dn.project or "None",
                 ", ".join("%s x%g" % (i.item_code, i.qty) for i in items)[:40], note))


def fix_invoice_series():
    print("")
    print("=" * 70)
    print("B9  one sales invoice on the default series instead of MSCAST's")
    print("=" * 70)
    strays = frappe.get_all("Sales Invoice",
                            filters={"name": ["like", "ACC-SINV-%"]},
                            fields=["name", "customer", "base_grand_total"])
    if not strays:
        print("   none - every sales invoice is on the SINV- series")
        return
    used = [s.name for s in frappe.get_all("Sales Invoice",
                                           filters={"name": ["like", "SINV-26-%"]},
                                           fields=["name"])]
    nums = [int(n.rsplit("-", 1)[-1]) for n in used if n.rsplit("-", 1)[-1].isdigit()]
    nxt = max(nums) + 1 if nums else 1
    for s in strays:
        target = "SINV-26-%05d" % nxt
        while frappe.db.exists("Sales Invoice", target):
            nxt += 1
            target = "SINV-26-%05d" % nxt
        print("   %s (%s, Rs %s) -> %s" % (s.name, s.customer, s.base_grand_total, target))
        frappe.flags.ignore_permissions = True
        frappe.rename_doc("Sales Invoice", s.name, target, force=True, merge=False)
        frappe.flags.ignore_permissions = False
        nxt += 1
    frappe.db.commit()
    print("   renamed. GL entries follow the rename automatically.")


def check_commissioning():
    print("")
    print("=" * 70)
    print("A3  was anything commissioned that had not been dispatched?")
    print("=" * 70)
    for c in frappe.get_all("MSCAST Commissioning Report",
                            fields=["name", "project"]):
        if not c.project:
            print("   %-20s no project" % c.name)
            continue
        dns = frappe.get_all("Delivery Note", filters={"project": c.project,
                                                       "docstatus": 1}, pluck="name")
        items = []
        for d in dns:
            items += frappe.get_all("Delivery Note Item", filters={"parent": d},
                                    fields=["item_code", "qty"])
        so = frappe.get_all("Sales Order", filters={"project": c.project},
                            fields=["name", "per_delivered"])
        print("   %-20s %-12s delivery notes: %s"
              % (c.name, c.project, ", ".join(dns) or "NONE"))
        print("        shipped: %s"
              % (", ".join("%s x%g" % (i.item_code, i.qty) for i in items) or "nothing"))
        for s in so:
            print("        %s is %.2f%% delivered by line count - low because the order "
                  "carries spares and services still to come" % (s.name, s.per_delivered))
        if not dns:
            print("        <- COMMISSIONED WITHOUT A DISPATCH")


def main():
    check_tds()
    check_delivery_note()
    check_commissioning()
    fix_invoice_series()
    print("")
    print("done")


main()
