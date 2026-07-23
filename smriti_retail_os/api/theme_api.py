# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/theme_api.py
# @description: Enterprise Theme Management System API — discovery, registry, & user appearance settings.
# @author: Jawahar R. Mallah
#

import frappe
from frappe import _
from smriti_retail_os.services.theme_service import discover_installed_themes, update_user_appearance

@frappe.whitelist()
def get_installed_themes():
    """
    Discovers all theme packages installed in smriti_retail_os/public/themes/
    """
    return discover_installed_themes()

@frappe.whitelist()
def save_user_appearance(theme_id=None, density=None, accent_color=None, high_contrast=False, reduced_motion=False):
    """
    Saves user appearance configuration.
    """
    if frappe.session.user == "Guest":
        return {"status": "guest", "message": _("Session guest mode — saved locally.")}

    user = frappe.session.user
    update_user_appearance(
        user=user,
        theme_id=theme_id,
        density=density,
        accent_color=accent_color,
        high_contrast=high_contrast,
        reduced_motion=reduced_motion
    )

    return {
        "status": "success",
        "theme_id": theme_id,
        "density": density,
        "accent_color": accent_color,
        "high_contrast": high_contrast,
        "reduced_motion": reduced_motion
    }
