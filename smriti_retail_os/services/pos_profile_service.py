# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/pos_profile_service.py
# @description: Business logic and validation layer for SMRITI POS Profile Management.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-25
# @version: 1.9.0 — Migrated to smriti.core.platform (SPC-012)
# @sprint: 3C — POS Profile Custom Manager
#

import frappe                  # frappe.throw — framework utility (permitted)
from frappe import _           # i18n only
from smriti_retail_os import smriti
from smriti_retail_os.repositories import pos_profile_repository

def get_active_shift_for_profile(pos_profile):
    """
    Checks if there is an active (Open) shift for the given POS Profile.
    Returns the POS Opening Entry name and user if found, else None.
    """
    open_shifts = smriti.db.get_list(
        "POSOpeningEntry",
        filters={
            "pos_profile": pos_profile,
            "status": "Open",
            "docstatus": 1
        },
        fields=["name", "user"],
        limit=1
    )
    return open_shifts[0] if open_shifts else None

def validate_profile_modification(name, new_data):
    """
    Validates that critical configurations (Warehouse, Payments, Cashiers) are not
    modified while there is an active open shift on this POS Profile.
    """
    active_shift = get_active_shift_for_profile(name)
    if not active_shift:
        return

    # Load existing profile to compare
    old_doc = pos_profile_repository.get_profile_by_name(name)
    if not old_doc:
        return

    # 1. Check Warehouse Change
    if new_data.get("warehouse") != old_doc.get("warehouse"):
        _raise_shift_lock_error(active_shift["name"], _("Warehouse"))

    # 2. Check Payments Table Change
    old_payments = {(p.get("mode_of_payment"), p.get("default_account")) for p in old_doc.get("payments", [])}
    new_payments = {(p.get("mode_of_payment"), p.get("default_account")) for p in new_data.get("payments", [])}
    if old_payments != new_payments:
        _raise_shift_lock_error(active_shift["name"], _("Payment Modes/Accounts"))

    # 3. Check Cashier Removal (Addition is allowed, removal is blocked)
    old_cashiers = {u.get("user") for u in old_doc.get("applicable_for_users", [])}
    new_cashiers = {u.get("user") for u in new_data.get("applicable_for_users", [])}
    removed_cashiers = old_cashiers - new_cashiers
    if removed_cashiers:
        _raise_shift_lock_error(active_shift["name"], _("Cashier Mapping (removal)"))

def _raise_shift_lock_error(shift_name, field_label):
    frappe.throw(
        _("ⓘ Operation Blocked: Shift <strong>{0}</strong> is currently open on this terminal. "
          "{1} cannot be modified while a shift is active. "
          "Please close the cashier shift before saving changes.").format(shift_name, field_label),
        frappe.ValidationError
    )

def clone_profile(source_name, target_name):
    """
    Clones all configuration settings from a source POS Profile to a new one.
    """
    if not source_name or not target_name:
        frappe.throw(_("Source and Target Profile names are required for cloning."))

    if smriti.db.exists("POSProfile", target_name):
        frappe.throw(_("Target POS Profile '{0}' already exists.").format(target_name))

    source_doc = pos_profile_repository.get_profile_by_name(source_name)
    if not source_doc:
        frappe.throw(_("Source POS Profile '{0}' not found.").format(source_name))

    # Construct the clone payload
    clone_data = {
        "name": target_name,
        "company": source_doc.get("company"),
        "warehouse": source_doc.get("warehouse"),
        "selling_price_list": source_doc.get("selling_price_list"),
        "currency": source_doc.get("currency"),
        "disabled": 0,
        "write_off_account": source_doc.get("write_off_account"),
        "write_off_cost_center": source_doc.get("write_off_cost_center"),
        "payments": [
            {
                "mode_of_payment": p.get("mode_of_payment"),
                "default_account": p.get("default_account"),
                "default": p.get("default")
            }
            for p in source_doc.get("payments", [])
        ],
        "applicable_for_users": [
            {"user": u.get("user")}
            for u in source_doc.get("applicable_for_users", [])
        ]
    }

    return pos_profile_repository.save_profile(clone_data)

def get_dropdown_data():
    """
    Aggregates dropdown option data lists for Companies, Warehouses, Price Lists,
    Payment Modes, Accounts, and Users to send to the UI.
    """
    # Fetch active ledgers in Chart of Accounts for payments mapping
    accounts = smriti.db.get_list(
        "Account",
        filters={"is_group": 0, "disabled": 0},
        fields=["name", "company"],
        limit=5000
    )

    users = smriti.db.get_list(
        "User",
        filters={"enabled": 1},
        fields=["name", "first_name", "last_name"],
        limit=2000
    )
    user_list = [
        {
            "value": u["name"],
            "label": f"{u['first_name'] or ''} {u['last_name'] or ''} ({u['name']})".strip()
        }
        for u in users
    ]

    return {
        "companies":     smriti.db.get_list("Company",       fields=["name"]),
        "warehouses":    smriti.db.get_list("Warehouse",     filters={"is_group": 0, "disabled": 0}, fields=["name"]),
        "price_lists":   smriti.db.get_list("PriceList",     filters={"enabled": 1}, fields=["name"]),
        "payment_modes": smriti.db.get_list("PaymentMode",   filters={"disabled": 0}, fields=["name"]),
        "accounts": accounts,
        "users": user_list
    }
