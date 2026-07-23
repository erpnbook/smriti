# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/theme_service.py
# @description: Service layer for theme discovery and user appearance management.
# @author: Jawahar R. Mallah
#

import os
import json
import frappe
from smriti_retail_os.repositories.theme_repository import save_theme_defaults

def discover_installed_themes():
    """
    Discovers all theme packages installed in smriti_retail_os/public/themes/
    """
    app_path = frappe.get_app_path("smriti_retail_os")
    themes_dir = os.path.join(app_path, "public", "themes")
    installed_themes = []

    if not os.path.exists(themes_dir):
        return installed_themes

    for entry in os.listdir(themes_dir):
        theme_path = os.path.join(themes_dir, entry)
        manifest_path = os.path.join(theme_path, "manifest.json")
        if os.path.isdir(theme_path) and os.path.exists(manifest_path):
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    manifest = json.load(f)
                    manifest["path"] = f"/assets/smriti_retail_os/themes/{entry}/"
                    installed_themes.append(manifest)
            except Exception as e:
                frappe.logger().error(f"[Theme Service] Failed to parse manifest for theme '{entry}': {str(e)}")

    return installed_themes

def update_user_appearance(user, theme_id=None, density=None, accent_color=None, high_contrast=False, reduced_motion=False):
    """
    Business logic for updating user appearance defaults.
    """
    save_theme_defaults(
        user=user,
        theme_id=theme_id,
        density=density,
        accent_color=accent_color,
        high_contrast=high_contrast,
        reduced_motion=reduced_motion
    )
