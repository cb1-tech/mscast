# -*- coding: utf-8 -*-
"""The BRM payment control: no money leaves without a certified certificate.

This replaces the `MSCAST BRM payment block` Server Script, which guarded
exactly one door and was proven on 21 Sep 2026 to have four ways round it:

  1. A JOURNAL ENTRY paying the supplier was not guarded at all. The script sat
     on Payment Entry, so a JV debiting Creditors paid an uncertified bill
     straight through. Tested: ACC-JV-2026-00023 went through without a murmur.
  2. An ADVANCE Payment Entry with no invoice reference passed silently,
     because the script looped over `doc.references` and an empty list means
     the loop body never runs. Tested: Rs 50,000 paid with no BRM anywhere.
  3. AMOUNTS were never compared. The script checked that a BRM existed and was
     certified; a BRM certified for 9 units let you pay for 10.
  4. It was also too WIDE in the other direction: any purchase invoice without
     a certified BRM was refused, with no exemption, so an electricity or rent
     bill would be blocked when no BRM is appropriate for it.

It lives in the app rather than in a Server Script because a control that
matters should be version-controlled, deployed with the release, and testable.
"""
import frappe
from frappe.utils import flt

EXEMPT_FIELD = "mscast_brm_exempt"
TOLERANCE = 1.0          # rupees, to absorb rounding on allocation


def _exempt(supplier):
    """Utilities, rent, statutory and petty suppliers do not route through a BRM."""
    if not supplier:
        return False
    if not frappe.db.has_column("Supplier", EXEMPT_FIELD):
        return False
    return bool(frappe.db.get_value("Supplier", supplier, EXEMPT_FIELD))


def _brm_for(supplier, bill_no):
    return frappe.db.get_value(
        "MSCAST BRM",
        {"supplier": supplier, "supplier_invoice_no": bill_no},
        ["name", "status", "amount"], as_dict=True)


def _check_invoice(supplier, pi_name, allocated):
    """Raise unless a certified BRM covers `allocated` on this invoice."""
    bill = frappe.db.get_value("Purchase Invoice", pi_name, "bill_no")
    brm = _brm_for(supplier, bill)
    if not brm:
        frappe.throw(
            "Payment blocked: no Billing Routing Memo (BRM) has been raised for "
            "supplier bill {0} of {1}. Raise and certify a BRM before releasing "
            "payment.".format(bill, supplier))
    if brm.status == "Paid":
        frappe.throw(
            "Payment blocked: BRM {0} for supplier bill {1} is already marked Paid. "
            "Paying against it again would pay the same bill twice. If this is a "
            "balance or a second instalment, raise a fresh BRM for it."
            .format(brm.name, bill))
    if brm.status != "Certified":
        frappe.throw(
            "Payment blocked: BRM {0} for supplier bill {1} is in status '{2}'. "
            "Only a certified BRM (quantity, rate, inspection and delivery "
            "checked) can be paid.".format(brm.name, bill, brm.status))
    certified = flt(brm.amount)
    if certified and flt(allocated) > certified + TOLERANCE:
        frappe.throw(
            "Payment blocked: BRM {0} certifies Rs {1:,.2f} for supplier bill "
            "{2}, but this payment allocates Rs {3:,.2f}. Certify the balance "
            "before paying it.".format(brm.name, certified, bill, flt(allocated)))


def payment_entry(doc, method=None):
    if doc.payment_type != "Pay" or doc.party_type != "Supplier":
        return
    if _exempt(doc.party):
        return

    refs = [r for r in (doc.references or [])
            if r.reference_doctype == "Purchase Invoice"]

    # An advance with no invoice behind it. MSCAST's own requirement routes PO
    # advances through a BRM against the proforma, so this is not an exception -
    # it is the case the old script silently let through.
    if not refs:
        frappe.throw(
            "Payment blocked: this pays {0} with no supplier invoice referenced. "
            "An advance still needs a certified BRM against the proforma or the "
            "purchase order. Raise one, or mark the supplier as BRM-exempt if no "
            "certificate is appropriate.".format(doc.party))

    for r in refs:
        _check_invoice(doc.party, r.reference_name,
                       flt(r.allocated_amount) or flt(doc.paid_amount))


def journal_entry(doc, method=None):
    """The door the old control did not guard at all."""
    payable_accounts = set(frappe.get_all(
        "Account", filters={"account_type": "Payable"}, pluck="name"))

    for row in (doc.accounts or []):
        # Paying a supplier means debiting the payable.
        if row.party_type != "Supplier" or not row.party:
            continue
        if flt(row.debit_in_account_currency) <= 0:
            continue
        if row.account not in payable_accounts:
            continue
        if _exempt(row.party):
            continue

        if row.reference_type == "Purchase Invoice" and row.reference_name:
            _check_invoice(row.party, row.reference_name,
                           flt(row.debit_in_account_currency))
        else:
            frappe.throw(
                "Payment blocked: row {0} debits {1} against supplier {2} with no "
                "purchase invoice referenced. Pay supplier bills through a Payment "
                "Entry against a certified BRM, or reference the invoice here so "
                "the certificate can be checked.".format(
                    row.idx, row.account, row.party))
