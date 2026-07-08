# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/discount_service.py
# @description: Decoupled discount adjustment calculator and permission validation service.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.9.0 — Migrated to smriti.core.platform (SPC-012)
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
#

import frappe                  # whitelist decorator only
from frappe import _           # i18n only
from frappe.utils import cint  # framework utility
from smriti_retail_os import smriti

@frappe.whitelist()
def validate_discount_limit(discount_percentage, is_offline=False, company=None):
    """
    Validates if the applied discount percentage exceeds the allowed threshold.
    Returns a dict with 'approved' status and warning/error details.
    """
    discount_percentage = float(discount_percentage or 0.0)
    if discount_percentage <= 0.0:
        return {"approved": True}

    settings = get_company_discount_settings(company)
    max_offline = float(settings.get("max_offline_cashier_discount") or 5.0)
    approval_limit = float(settings.get("discount_approval_limit") or 10.0)

    if is_offline:
        if discount_percentage > max_offline:
            return {
                "approved": False,
                "reason": "OFFLINE_LIMIT_EXCEEDED",
                "message": _("Offline discount limit of {0}% exceeded. Manager override is unavailable when offline.").format(max_offline)
            }
    else:
        if discount_percentage > approval_limit:
            return {
                "approved": False,
                "reason": "APPROVAL_REQUIRED",
                "message": _("Discount of {0}% exceeds cashier limit of {1}%. Requires manager PIN approval.").format(discount_percentage, approval_limit)
            }

    return {"approved": True}

@frappe.whitelist()
def get_company_discount_settings(company=None):
    """
    Safely retrieves discount config parameters from SMRITI Company Settings.
    """
    if not company:
        company = smriti.db.get_single("GlobalDefaults", "default_company")

    settings = {
        "discount_mode": "Both",
        "mandatory_discount_reason": 0,
        "discount_approval_limit": 10.0,
        "max_offline_cashier_discount": 5.0
    }

    if not company:
        return settings

    try:
        doc = smriti.documents.get("CompanySettings", company)
        settings["discount_mode"] = doc.custom_discount_mode or "Both"
        settings["mandatory_discount_reason"] = cint(doc.custom_mandatory_discount_reason)
        settings["discount_approval_limit"] = float(doc.custom_discount_approval_limit or 10.0)
        settings["max_offline_cashier_discount"] = float(doc.custom_max_offline_cashier_discount or 5.0)
    except smriti.errors.NotFoundError:
        pass

    return settings

def calculate_item_discount(rate, qty, discount_type, discount_value):
    """
    Returns the absolute discount amount for a single item row.
    """
    qty = float(qty or 0.0)
    rate = float(rate or 0.0)
    discount_value = float(discount_value or 0.0)
    
    if qty <= 0 or rate <= 0 or discount_value <= 0:
        return 0.0

    if discount_type == "%":
        return round((rate * qty) * (discount_value / 100.0), 4)
    else:
        # absolute amount per row or per unit? standard POS is absolute amount per row
        return round(discount_value, 4)
