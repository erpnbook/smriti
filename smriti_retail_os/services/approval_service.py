# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/approval_service.py
# @description: Decoupled manager PIN override and approval validation service.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.9.0 — Migrated to smriti.core.platform (SPC-012)

import frappe                                              # whitelist decorator only
from frappe import _                                       # i18n only — no platform coupling
from smriti_retail_os.services.discount_service import get_company_discount_settings

@frappe.whitelist()
def validate_approval_override(manager_pin, action_type, discount_percentage=0.0, is_offline=False, company=None, invoice_name=None):
    """
    Centrally handles all manager approval and override logic for transaction limits.
    """
    discount_percentage = float(discount_percentage or 0.0)

    # 1. Handle offline validation limits
    if is_offline:
        settings = get_company_discount_settings(company)
        max_offline = float(settings.get("max_offline_cashier_discount") or 5.0)
        if discount_percentage > max_offline:
            return {
                "authorized": False,
                "reason": "OFFLINE_LIMIT_EXCEEDED",
                "message": _("Offline discount of {0}% exceeds limit of {1}% and manager validation is offline.").format(discount_percentage, max_offline)
            }
        else:
            return {"authorized": True, "message": _("Approved under offline threshold limits.")}

    # 2. Online: validate Manager PIN
    if not manager_pin:
        return {"authorized": False, "message": _("Manager PIN is required for this action.")}

    from smriti_retail_os.billing_api import validate_manager_override
    res = validate_manager_override(manager_pin, action_type, invoice_name)
    if isinstance(res, dict) and res.get("authorized"):
        return {"authorized": True, "manager": res.get("manager")}
    
    return {"authorized": False, "message": _("Invalid Manager PIN or unauthorized role.")}
