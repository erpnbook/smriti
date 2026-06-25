# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/pos_profile_api.py
# @description: Whitelisted API layer for SMRITI POS Profile Management.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-25
# @version: 1.0.0
# @sprint: 3C — POS Profile Custom Manager
# @authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL
#

import frappe
from frappe import _
from smriti_retail_os.services import pos_profile_service
from smriti_retail_os.repositories import pos_profile_repository

def _check_permissions():
    """
    Enforces that only System Managers or Administrators can access the POS Profile APIs.
    """
    if frappe.session.user == "Guest":
        frappe.throw(_("Authentication Required: Please log in to continue."), frappe.AuthenticationError)
    
    roles = frappe.get_roles(frappe.session.user)
    allowed = {"System Manager", "Administrator"}
    if not (allowed & set(roles)) and frappe.session.user != "Administrator":
        frappe.throw(_("Access Denied: You do not have permissions to manage POS Profiles."), frappe.PermissionError)

@frappe.whitelist()
def get_profiles():
    _check_permissions()
    return pos_profile_repository.get_profiles()

@frappe.whitelist()
def get_details(name):
    _check_permissions()
    details = pos_profile_repository.get_profile_by_name(name)
    if not details:
        frappe.throw(_("POS Profile '{0}' not found.").format(name), frappe.DoesNotExistError)
    return details

@frappe.whitelist()
def save_profile(doc_data):
    _check_permissions()
    import json
    if isinstance(doc_data, str):
        doc_data = json.loads(doc_data)

    name = doc_data.get("name")
    if not name:
        frappe.throw(_("POS Profile Name is required."))

    # Validate shift lock before modification
    if frappe.db.exists("POS Profile", name):
        pos_profile_service.validate_profile_modification(name, doc_data)

    return pos_profile_repository.save_profile(doc_data)

@frappe.whitelist()
def clone_profile(source_name, target_name):
    _check_permissions()
    return pos_profile_service.clone_profile(source_name, target_name)

@frappe.whitelist()
def archive_profile(name):
    _check_permissions()
    # Check shift lock before archiving/disabling
    active_shift = pos_profile_service.get_active_shift_for_profile(name)
    if active_shift:
        frappe.throw(
            _("ⓘ Operation Blocked: Shift <strong>{0}</strong> is currently open on this terminal. "
              "Close the shift before archiving or disabling this POS Profile.").format(active_shift["name"]),
            frappe.ValidationError
        )
    return pos_profile_repository.disable_profile(name)

@frappe.whitelist()
def get_dropdowns():
    _check_permissions()
    return pos_profile_service.get_dropdown_data()

@frappe.whitelist()
def validate_profile(name):
    """
    Checks if a profile can be edited or deleted and returns shift information.
    """
    _check_permissions()
    active_shift = pos_profile_service.get_active_shift_for_profile(name)
    return {
        "is_locked": True if active_shift else False,
        "active_shift": active_shift
    }
