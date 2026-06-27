# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/golive_api.py
# @description: SMRITI Go-Live API — setup completion and onboarding checks.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/api/golive_api.py
# @description: Go-Live Readiness Checklist API for SMRITI Retail OS.
#               Each check returns a status: PASS | WARN | FAIL | INFO
#               with a human-readable message and an optional action link.
# @authority: SMRITI Architecture Constitution — Rule 2 (Service-First)
# @version: 1.8.6
#

import frappe
from frappe import _
from frappe.utils import cint


# ── Permission guard ──────────────────────────────────────────────────────────

def _require_admin():
    roles = set(frappe.get_roles(frappe.session.user))
    if not ({"SMRITI System Admin", "System Manager", "Administrator"} & roles):
        frappe.throw(_("Access restricted to System Manager."), frappe.PermissionError)


# ── Individual check functions ────────────────────────────────────────────────

def _check_license():
    try:
        doc = frappe.get_single("SMRITI License")
        status = doc.license_status or "Unregistered"
        health  = doc.license_health or "Unregistered"
        if status == "Active" and health == "Healthy":
            return {"id": "license", "label": "License Activated",
                    "status": "PASS", "message": f"Active — {doc.license_type or 'Unknown'} tier. Expires {doc.expiry_date or 'N/A'}.",
                    "action": "/smriti-license"}
        elif status in ("Active",):
            return {"id": "license", "label": "License Activated",
                    "status": "WARN", "message": f"License is {health}. Check expiry.",
                    "action": "/smriti-license"}
        else:
            return {"id": "license", "label": "License Activated",
                    "status": "FAIL", "message": f"License status: {status}. Activate a valid license key.",
                    "action": "/smriti-license"}
    except Exception:
        return {"id": "license", "label": "License Activated",
                "status": "FAIL", "message": "License DocType not found or not initialized.",
                "action": "/smriti-license"}


def _check_company():
    company = frappe.db.get_value("Company", {}, "name")
    if company:
        return {"id": "company", "label": "Default Company",
                "status": "PASS", "message": f"Company '{company}' is configured."}
    return {"id": "company", "label": "Default Company",
            "status": "FAIL", "message": "No Company found. Create a company in ERPNext before going live."}


def _check_warehouse():
    count = frappe.db.count("Warehouse", {"is_group": 0, "disabled": 0})
    if count >= 1:
        return {"id": "warehouse", "label": "Store Warehouse",
                "status": "PASS", "message": f"{count} active warehouse(s) configured."}
    return {"id": "warehouse", "label": "Store Warehouse",
            "status": "FAIL", "message": "No active warehouses found. At least one store warehouse is required."}


def _check_pos_profile():
    count = frappe.db.count("POS Profile", {"disabled": 0})
    if count >= 1:
        return {"id": "pos_profile", "label": "POS Profile",
                "status": "PASS", "message": f"{count} active POS Profile(s) configured."}
    return {"id": "pos_profile", "label": "POS Profile",
            "status": "FAIL", "message": "No active POS Profiles found. Create a POS Profile for each billing terminal."}


def _check_cashier_users():
    users = frappe.db.get_all(
        "Has Role",
        filters={"role": "SMRITI Cashier"},
        pluck="parent"
    )
    active = [u for u in set(users) if frappe.db.get_value("User", u, "enabled")]
    if active:
        return {"id": "cashier_users", "label": "Cashier Users",
                "status": "PASS", "message": f"{len(active)} user(s) with SMRITI Cashier role.",
                "action": "/security"}
    return {"id": "cashier_users", "label": "Cashier Users",
            "status": "WARN", "message": "No active Cashier users found. Assign SMRITI Cashier role to store staff.",
            "action": "/security"}


def _check_manager_users():
    users = frappe.db.get_all(
        "Has Role",
        filters={"role": "SMRITI Store Manager"},
        pluck="parent"
    )
    active = [u for u in set(users) if frappe.db.get_value("User", u, "enabled")]
    if active:
        return {"id": "manager_users", "label": "Store Manager Users",
                "status": "PASS", "message": f"{len(active)} user(s) with SMRITI Store Manager role.",
                "action": "/security"}
    return {"id": "manager_users", "label": "Store Manager Users",
            "status": "FAIL", "message": "No Store Managers found. At least one manager is required for POS overrides.",
            "action": "/security"}


def _check_manager_pins():
    managers = frappe.db.get_all(
        "Has Role",
        filters={"role": ["in", ["SMRITI Store Manager", "System Manager"]]},
        pluck="parent"
    )
    active_managers = [u for u in set(managers)
                       if frappe.db.get_value("User", u, "enabled")
                       and u not in ("Administrator", "Guest")]
    with_pin = [u for u in active_managers
                if frappe.db.get_value("User", u, "custom_smriti_pin")]
    if not active_managers:
        return {"id": "manager_pins", "label": "Manager POS Override PINs",
                "status": "WARN", "message": "No active managers to check. Add manager users first.",
                "action": "/security"}
    if with_pin:
        return {"id": "manager_pins", "label": "Manager POS Override PINs",
                "status": "PASS", "message": f"{len(with_pin)}/{len(active_managers)} manager(s) have a POS PIN set.",
                "action": "/security"}
    return {"id": "manager_pins", "label": "Manager POS Override PINs",
            "status": "WARN",
            "message": "No managers have a POS Override PIN set. Cashiers won't be able to perform overrides.",
            "action": "/security"}


def _check_backup_security():
    try:
        from smriti_retail_os.backup_api import get_settings
        settings = get_settings()
        enabled  = cint(settings.get("enable_backup_encryption", 0))
        if enabled:
            verified = frappe.get_all("SMRITI Key Custodian", filters={"status": "Verified", "verified": 1})
            if len(verified) >= 2:
                return {"id": "backup", "label": "Backup Encryption",
                        "status": "PASS", "message": "AES-256 encryption enabled. Dual-custodian recovery verified.",
                        "action": "/security"}
            return {"id": "backup", "label": "Backup Encryption",
                    "status": "WARN",
                    "message": "Encryption enabled but dual-custodian recovery not fully verified.",
                    "action": "/security"}
        return {"id": "backup", "label": "Backup Encryption",
                "status": "WARN", "message": "Backup encryption is disabled. Enable GPG AES-256 for production.",
                "action": "/security"}
    except Exception:
        return {"id": "backup", "label": "Backup Encryption",
                "status": "INFO", "message": "Security Settings not found. Configure backup encryption before go-live.",
                "action": "/security"}


def _check_outgoing_email():
    try:
        count = frappe.db.count("Email Account", {"enable_outgoing": 1})
        if count:
            return {"id": "email", "label": "Outgoing Email (SMTP)",
                    "status": "PASS", "message": f"{count} outgoing email account(s) configured."}
        return {"id": "email", "label": "Outgoing Email (SMTP)",
                "status": "WARN", "message": "No outgoing email configured. Receipts and alerts won't be emailed."}
    except Exception:
        return {"id": "email", "label": "Outgoing Email (SMTP)",
                "status": "WARN", "message": "Could not check email configuration."}


def _check_price_list():
    count = frappe.db.count("Price List", {"selling": 1, "enabled": 1})
    if count:
        return {"id": "price_list", "label": "Selling Price List",
                "status": "PASS", "message": f"{count} active selling price list(s) configured."}
    return {"id": "price_list", "label": "Selling Price List",
            "status": "FAIL", "message": "No active selling price lists found. Items won't have prices at POS."}


def _check_tax_templates():
    count = frappe.db.count("Sales Taxes and Charges Template", {"disabled": 0})
    if count:
        return {"id": "tax", "label": "GST / Tax Templates",
                "status": "PASS", "message": f"{count} tax template(s) configured."}
    return {"id": "tax", "label": "GST / Tax Templates",
            "status": "WARN", "message": "No tax templates found. GST won't apply automatically at POS."}


def _check_items():
    count = frappe.db.count("Item", {"disabled": 0, "is_sales_item": 1})
    if count >= 5:
        return {"id": "items", "label": "Product Catalogue",
                "status": "PASS", "message": f"{count} sellable items loaded in system."}
    elif count > 0:
        return {"id": "items", "label": "Product Catalogue",
                "status": "WARN", "message": f"Only {count} item(s) found. Import your full catalogue before go-live."}
    return {"id": "items", "label": "Product Catalogue",
            "status": "FAIL", "message": "No sellable items found. Upload your product catalogue first."}


def _check_customers():
    count = frappe.db.count("Customer", {"disabled": 0})
    if count >= 1:
        return {"id": "customers", "label": "Customer Master",
                "status": "PASS", "message": f"{count} active customer(s) in system."}
    return {"id": "customers", "label": "Customer Master",
            "status": "INFO", "message": "No customers yet. A walk-in customer is sufficient for POS operations."}


def _check_license_secret():
    secret = getattr(frappe.conf, "smriti_license_secret", None)
    if secret and secret != "SMRITI-DEV-SECRET-DO-NOT-USE-IN-PRODUCTION":
        return {"id": "license_secret", "label": "License Signing Secret",
                "status": "PASS", "message": "smriti_license_secret is set in site_config.json."}
    elif secret:
        return {"id": "license_secret", "label": "License Signing Secret",
                "status": "WARN", "message": "Using development fallback secret. Set smriti_license_secret in site_config.json for production."}
    return {"id": "license_secret", "label": "License Signing Secret",
            "status": "WARN", "message": "smriti_license_secret not set. Add to site_config.json before go-live."}


# ── Ordered check groups ──────────────────────────────────────────────────────

_CHECKS = [
    # Critical
    {"fn": _check_license,        "group": "Licensing"},
    {"fn": _check_license_secret, "group": "Licensing"},
    # Store Setup
    {"fn": _check_company,        "group": "Store Setup"},
    {"fn": _check_warehouse,      "group": "Store Setup"},
    {"fn": _check_pos_profile,    "group": "Store Setup"},
    # Users & Security
    {"fn": _check_cashier_users,  "group": "Users & Security"},
    {"fn": _check_manager_users,  "group": "Users & Security"},
    {"fn": _check_manager_pins,   "group": "Users & Security"},
    {"fn": _check_backup_security,"group": "Users & Security"},
    # Data
    {"fn": _check_price_list,     "group": "Catalogue & Pricing"},
    {"fn": _check_tax_templates,  "group": "Catalogue & Pricing"},
    {"fn": _check_items,          "group": "Catalogue & Pricing"},
    {"fn": _check_customers,      "group": "Catalogue & Pricing"},
    # Infrastructure
    {"fn": _check_outgoing_email, "group": "Infrastructure"},
]


# ── Public API ────────────────────────────────────────────────────────────────

@frappe.whitelist()
def get_checklist():
    """
    Runs all go-live readiness checks and returns grouped results.
    Accessible to System Manager / SMRITI System Admin only.
    """
    _require_admin()

    groups = {}
    totals = {"PASS": 0, "WARN": 0, "FAIL": 0, "INFO": 0}

    for check_def in _CHECKS:
        try:
            result = check_def["fn"]()
        except Exception:
            result = {
                "id":      check_def["fn"].__name__,
                "label":   check_def["fn"].__name__,
                "status":  "WARN",
                "message": "Check encountered an error: " + frappe.get_traceback().split("\n")[-2],
            }

        result["group"] = check_def["group"]
        totals[result["status"]] = totals.get(result["status"], 0) + 1
        groups.setdefault(check_def["group"], []).append(result)

    # Overall readiness
    if totals["FAIL"] == 0 and totals["WARN"] == 0:
        overall = "READY"
        overall_msg = "All checks passed. System is ready for go-live."
    elif totals["FAIL"] == 0:
        overall = "CAUTION"
        overall_msg = f"{totals['WARN']} warning(s) found. Review before going live."
    else:
        overall = "NOT_READY"
        overall_msg = f"{totals['FAIL']} critical issue(s) must be resolved before go-live."

    return {
        "overall":     overall,
        "overall_msg": overall_msg,
        "totals":      totals,
        "groups":      groups,
        "group_order": [c["group"] for c in _CHECKS if c["group"] not in
                        [g for i, g in enumerate([c2["group"] for c2 in _CHECKS[:_CHECKS.index(c)]]) if g == c["group"]]],
    }
