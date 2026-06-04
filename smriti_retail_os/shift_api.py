# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/shift_api.py
# @description: Backend API for SMRITI Day Open/Close Shift management.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import flt, cint, nowdate, now_datetime, get_datetime
from frappe import _

# ---------------------------------------------------------------------------
# Day Open
# ---------------------------------------------------------------------------

@frappe.whitelist()
def open_shift(cashier, pos_profile, opening_entries):
    """
    Opens a cashier shift by creating a standard POS Opening Entry.
    Uses existing ERPNext POS Opening Entry DocType — no new DocTypes.

    Args:
        cashier         : User ID of the cashier
        pos_profile     : Name of the POS Profile
        opening_entries : JSON list of {mode_of_payment, opening_amount}
    """
    # Check if this cashier already has an open shift
    existing = _get_open_shift(cashier, pos_profile)
    if existing:
        frappe.throw(
            _("Cashier {0} already has an open shift: {1}. Please close it first.").format(
                cashier, existing
            )
        )

    entries = frappe.parse_json(opening_entries)

    company = (
        frappe.db.get_value("POS Profile", pos_profile, "company")
        or frappe.defaults.get_user_default("company")
        or frappe.get_all("Company", limit=1)[0].name
    )

    opening = frappe.new_doc("POS Opening Entry")
    opening.user = cashier
    opening.pos_profile = pos_profile
    opening.company = company
    opening.period_start_date = now_datetime()
    opening.posting_date = nowdate()
    opening.status = "Open"

    for entry in entries:
        if flt(entry.get("opening_amount")) >= 0:
            opening.append("balance_details", {
                "mode_of_payment": entry.get("mode_of_payment"),
                "opening_amount": flt(entry.get("opening_amount"))
            })

    opening.flags.ignore_permissions = True
    opening.insert()
    opening.submit()
    frappe.db.commit()

    return {
        "opening_entry": opening.name,
        "message": _("Shift opened successfully for {0}").format(cashier)
    }


@frappe.whitelist()
def get_active_shift(cashier, pos_profile=None):
    """
    Returns the currently open POS Opening Entry for this cashier.
    """
    filters = {
        "user": cashier,
        "status": "Open",
        "docstatus": 1
    }
    if pos_profile:
        filters["pos_profile"] = pos_profile

    opening = frappe.db.get_all(
        "POS Opening Entry",
        filters=filters,
        fields=["name", "pos_profile", "period_start_date", "posting_date", "company"],
        order_by="period_start_date desc",
        limit=1
    )

    if not opening:
        return None

    oe = opening[0]
    # Fetch opening balance details
    balance_details = frappe.db.get_all(
        "POS Opening Entry Detail",
        filters={"parent": oe.name},
        fields=["mode_of_payment", "opening_amount"]
    )
    oe["balance_details"] = balance_details

    return oe


@frappe.whitelist()
def get_shift_summary(opening_entry_name):
    """
    Calculates shift totals from submitted POS Invoices linked to the opening entry.
    Returns breakdown by payment mode + total expected closing balances.
    """
    if not frappe.db.exists("POS Opening Entry", opening_entry_name):
        frappe.throw(_("POS Opening Entry {0} not found.").format(opening_entry_name))

    oe = frappe.get_doc("POS Opening Entry", opening_entry_name)

    # Get all submitted POS Invoices for this shift
    invoices = frappe.db.get_all(
        "POS Invoice",
        filters={
            "pos_profile": oe.pos_profile,
            "owner": oe.user,
            "docstatus": 1,
            "posting_date": [">=", oe.posting_date]
        },
        fields=["name", "grand_total", "posting_date"]
    )

    invoice_names = [inv.name for inv in invoices]
    total_sales = sum(flt(inv.grand_total) for inv in invoices)
    invoice_count = len(invoices)

    # Payment mode breakdown from Sales Invoice Payment rows
    mode_totals = {}
    if invoice_names:
        payments = frappe.db.get_all(
            "Sales Invoice Payment",
            filters={"parent": ["in", invoice_names]},
            fields=["mode_of_payment", "amount"]
        )
        for p in payments:
            mode = p.mode_of_payment
            mode_totals[mode] = flt(mode_totals.get(mode, 0)) + flt(p.amount)

    # Build expected closing amounts (opening + sales by mode)
    opening_map = {}
    for bd in oe.balance_details:
        opening_map[bd.mode_of_payment] = flt(bd.opening_amount)

    closing_summary = []
    all_modes = set(list(opening_map.keys()) + list(mode_totals.keys()))
    for mode in all_modes:
        opening_amt = flt(opening_map.get(mode, 0))
        sales_amt = flt(mode_totals.get(mode, 0))
        closing_summary.append({
            "mode_of_payment": mode,
            "opening_amount": opening_amt,
            "sales_amount": sales_amt,
            "expected_amount": opening_amt + sales_amt
        })

    return {
        "opening_entry": opening_entry_name,
        "pos_profile": oe.pos_profile,
        "cashier": oe.user,
        "period_start_date": str(oe.period_start_date),
        "total_sales": flt(total_sales),
        "invoice_count": cint(invoice_count),
        "closing_summary": closing_summary
    }


@frappe.whitelist()
def close_shift(opening_entry_name, closing_entries, manager_pin=None, notes=None):
    """
    Closes the cashier shift by creating a standard POS Closing Entry.
    If the cash difference exceeds threshold, requires manager_pin override.

    Args:
        opening_entry_name : Name of the POS Opening Entry to close
        closing_entries    : JSON list of {mode_of_payment, closing_amount}
        manager_pin        : Optional manager password for override on large variance
        notes              : Optional closing remarks
    """
    if not frappe.db.exists("POS Opening Entry", opening_entry_name):
        frappe.throw(_("POS Opening Entry {0} not found.").format(opening_entry_name))

    oe = frappe.get_doc("POS Opening Entry", opening_entry_name)

    if oe.status != "Open":
        frappe.throw(_("This shift is already closed."))

    entries = frappe.parse_json(closing_entries)

    # Get shift summary to populate closing entry
    summary = get_shift_summary(opening_entry_name)
    expected_map = {row["mode_of_payment"]: row["expected_amount"] for row in summary["closing_summary"]}

    # Validate cash difference if manager_pin provided threshold check
    DIFFERENCE_THRESHOLD = flt(
        frappe.db.get_single_value("POS Settings", "pos_closing_entry_validation_amount") or 500
    )

    closing_map = {e.get("mode_of_payment"): flt(e.get("closing_amount", 0)) for e in entries}
    cash_diff = flt(closing_map.get("Cash", 0)) - flt(expected_map.get("Cash", 0))

    if abs(cash_diff) > DIFFERENCE_THRESHOLD and not manager_pin:
        return {
            "requires_override": True,
            "cash_difference": cash_diff,
            "message": _("Cash difference of Rs.{0:.2f} exceeds threshold. Manager approval required.").format(abs(cash_diff))
        }

    # If manager_pin provided, validate it
    if manager_pin:
        override_result = _validate_manager_pin(manager_pin, "Shift Close Override", opening_entry_name)
        if not override_result.get("authorized"):
            frappe.throw(_("Manager authorization failed. Invalid PIN."))

    # Build and submit POS Closing Entry
    closing = frappe.new_doc("POS Closing Entry")
    closing.pos_profile = oe.pos_profile
    closing.user = oe.user
    closing.company = oe.company
    closing.period_start_date = oe.period_start_date
    closing.period_end_date = now_datetime()
    closing.posting_date = nowdate()
    closing.pos_opening_entry = opening_entry_name

    # Build per-mode opening amount lookup
    opening_by_mode = {bd.mode_of_payment: flt(bd.opening_amount) for bd in oe.balance_details}

    # Add payment mode closing rows
    for e in entries:
        mode = e.get("mode_of_payment")
        closing_amt = flt(e.get("closing_amount", 0))
        expected_amt = flt(expected_map.get(mode, 0))
        opening_amt = flt(opening_by_mode.get(mode, 0))
        closing.append("payment_reconciliation", {
            "mode_of_payment": mode,
            "opening_amount": opening_amt,
            "expected_amount": expected_amt,
            "closing_amount": closing_amt,
            "difference": closing_amt - expected_amt
        })

    # Add invoice references
    invoices = frappe.db.get_all(
        "POS Invoice",
        filters={
            "pos_profile": oe.pos_profile,
            "owner": oe.user,
            "docstatus": 1,
            "posting_date": [">=", oe.posting_date]
        },
        fields=["name", "grand_total", "customer", "posting_date"]
    )

    for inv in invoices:
        closing.append("pos_transactions", {
            "pos_invoice": inv.name,
            "posting_date": inv.posting_date,
            "customer": inv.customer,
            "grand_total": flt(inv.grand_total)
        })

    if notes:
        closing.closing_note = notes

    closing.flags.ignore_permissions = True
    closing.insert()
    closing.submit()

    frappe.db.commit()

    return {
        "closing_entry": closing.name,
        "total_sales": flt(summary["total_sales"]),
        "invoice_count": cint(summary["invoice_count"]),
        "cash_difference": cash_diff,
        "message": _("Shift closed successfully.")
    }


@frappe.whitelist()
def get_pos_profiles():
    """
    Returns available POS Profiles for the current user.
    """
    user_profiles = frappe.db.get_all(
        "POS Profile User",
        filters={"user": frappe.session.user, "default": 1},
        fields=["parent"]
    )
    if user_profiles:
        return [frappe.db.get_value("POS Profile", p.parent, ["name", "company", "currency"], as_dict=True)
                for p in user_profiles]

    # Fallback: return all active profiles
    return frappe.db.get_all(
        "POS Profile",
        filters={"disabled": 0},
        fields=["name", "company", "currency"],
        limit=10
    )


@frappe.whitelist()
def get_payment_modes():
    """
    Returns active modes of payment for shift opening/closing entry.
    """
    modes = frappe.db.get_all(
        "Mode of Payment",
        filters={"enabled": 1},
        fields=["name", "type"],
        order_by="name asc"
    )
    return modes


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_open_shift(cashier, pos_profile):
    result = frappe.db.get_value(
        "POS Opening Entry",
        {"user": cashier, "pos_profile": pos_profile, "status": "Open", "docstatus": 1},
        "name"
    )
    return result


def _validate_manager_pin(pin, action_type, reference_name=None):
    """
    Validates manager password and logs override as a Comment.
    Checks custom_smriti_pin first, then falls back to primary password.
    Mirrors billing_api.validate_manager_override logic.
    """
    from frappe.utils.password import check_password as check_smriti_pin
    import frappe.auth

    managers = frappe.db.get_all(
        "Has Role",
        filters={"role": ["in", ["SMRITI Store Manager", "System Manager"]]},
        pluck="parent"
    )

    for mgr in set(managers):
        if not frappe.db.get_value("User", mgr, "enabled"):
            continue
        
        authenticated = False
        try:
            # 1. Try SMRITI Dedicated PIN first
            if frappe.db.get_value("User", mgr, "custom_smriti_pin"):
                try:
                    check_smriti_pin(mgr, pin, fieldname="custom_smriti_pin")
                    authenticated = True
                except frappe.AuthenticationError:
                    pass
            
            # 2. Fallback to primary password
            if not authenticated:
                frappe.auth.check_password(mgr, pin)
                authenticated = True

            if authenticated:
                roles = frappe.get_roles(mgr)
                if "SMRITI Store Manager" in roles or "System Manager" in roles:
                    if reference_name:
                        frappe.get_doc({
                            "doctype": "Comment",
                            "comment_type": "Comment",
                            "reference_doctype": "POS Opening Entry",
                            "reference_name": reference_name,
                            "content": f"Manager Override approved by {mgr} for: {action_type}",
                            "comment_email": frappe.session.user,
                            "comment_by": frappe.session.user
                        }).insert(ignore_permissions=True)
                    return {"authorized": True, "manager": mgr}
        except frappe.AuthenticationError:
            pass
        except Exception:
            frappe.log_error(title="SMRITI Shift Manager Override Error", message=frappe.get_traceback())

    return {"authorized": False}


@frappe.whitelist()
def get_shift_status():
    cashier = frappe.session.user
    active_shift = get_active_shift(cashier)
    if active_shift:
        return {
            "status": "Open",
            "cashier": cashier,
            "shift_name": active_shift.name
        }
    else:
        return {
            "status": "Closed",
            "cashier": cashier
        }

