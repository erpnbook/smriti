# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/repositories/theme_repository.py
# @description: Repository module for theme defaults persistence.
# @author: Jawahar R. Mallah
#

import frappe

def save_theme_defaults(user, theme_id=None, density=None, accent_color=None, high_contrast=False, reduced_motion=False):
    """
    Persists user theme defaults using Frappe DB operations.
    """
    if theme_id:
        frappe.db.set_default("smriti_theme_style", theme_id, parent=user)
    if density:
        frappe.db.set_default("smriti_ui_density", density, parent=user)
    if accent_color:
        frappe.db.set_default("smriti_accent_color", accent_color, parent=user)
    
    frappe.db.set_default("smriti_high_contrast", "1" if high_contrast else "0", parent=user)
    frappe.db.set_default("smriti_reduced_motion", "1" if reduced_motion else "0", parent=user)
    frappe.db.commit()
