# -*- coding: utf-8 -*-
"""
smriti_retail_os/user_studio/api/smriti_user_api.py
SMRITI User Studio API — profile, preferences, activity.
Author: Jawahar R. Mallah <jawahar.mallah@gmail.com>
"""
import frappe
from frappe.utils import now_datetime

# Cache TTL constants
ONE_YEAR_SECONDS = 60 * 60 * 24 * 365



@frappe.whitelist()
def get_my_profile():
    """Get current user's profile information."""
    user = frappe.session.user
    try:
        doc = frappe.get_doc("User", user)
        roles = frappe.get_roles(user)
        # Determine display role
        if "System Manager" in roles:
            display_role = "System Manager"
        elif "SMRITI Store Manager" in roles:
            display_role = "Store Manager"
        elif "SMRITI Cashier" in roles:
            display_role = "Cashier"
        else:
            display_role = "User"

        return {
            "user": user,
            "full_name": doc.full_name or doc.first_name,
            "first_name": doc.first_name or "",
            "last_name": doc.last_name or "",
            "email": doc.email,
            "phone": doc.phone or doc.mobile_no or "",
            "display_role": display_role,
            "roles": list(roles),
            "language": doc.language or "en",
            "time_zone": doc.time_zone or "Asia/Kolkata",
            "user_type": doc.user_type,
            "last_login": str(doc.last_login) if doc.last_login else None,
            "last_ip": doc.last_ip or "",
            "creation": str(doc.creation)
        }
    except Exception as e:
        frappe.log_error(str(e), "get_my_profile")
        return {"error": str(e)}


@frappe.whitelist()
def update_my_profile(first_name=None, last_name=None, phone=None, language=None, time_zone=None):
    """Update allowed profile fields for the current user."""
    user = frappe.session.user
    try:
        doc = frappe.get_doc("User", user)
        if first_name is not None:
            doc.first_name = first_name
        if last_name is not None:
            doc.last_name = last_name
        if phone is not None:
            doc.mobile_no = phone
        if language is not None:
            doc.language = language
        if time_zone is not None:
            doc.time_zone = time_zone
        # reviewed-ignore-permissions: user profile self-update, restricted to the logged-in user
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return {"status": "ok", "message": "Profile updated successfully."}
    except Exception as e:
        frappe.log_error(str(e), "update_my_profile")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def change_password(old_password, new_password):
    """Change current user password — uses Frappe's built-in password handler."""
    user = frappe.session.user
    try:
        from frappe.utils.password import check_password, update_password
        # Verify old password
        check_password(user, old_password)
        # Set new password
        update_password(user, new_password)
        frappe.db.commit()
        return {"status": "ok", "message": "Password changed successfully."}
    except frappe.AuthenticationError:
        return {"status": "error", "message": "Current password is incorrect."}
    except Exception as e:
        frappe.log_error(str(e), "change_password")
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def get_my_activity(limit=20):
    """Get recent login/activity log for current user."""
    user = frappe.session.user
    try:
        rows = frappe.db.sql("""
            SELECT name, subject, creation, ip_address,
                   reference_doctype, reference_name
            FROM `tabActivity Log`
            WHERE user = %(user)s
            ORDER BY creation DESC
            LIMIT %(limit)s
        """, {"user": user, "limit": int(limit)}, as_dict=True)
        return rows
    except Exception as e:
        frappe.log_error(str(e), "get_my_activity")
        return []


@frappe.whitelist()
def logout():
    """Log out the current user via Frappe's session manager."""
    frappe.local.login_manager.logout()
    frappe.db.commit()
    return {"status": "ok", "redirect": "/smriti-login"}


@frappe.whitelist()
def get_smriti_preferences():
    """Get SMRITI-specific user preferences stored in localStorage keys (server fallback)."""
    user = frappe.session.user
    try:
        # Store SMRITI prefs as User Permission or in a simple key-value via frappe.db
        pref_key = f"smriti_prefs_{user.replace('@', '_').replace('.', '_')}"
        val = frappe.cache().get_value(pref_key) or {}
        return val
    except Exception:
        return {}


@frappe.whitelist()
def save_smriti_preferences(preferences):
    """Save SMRITI-specific preferences for the user."""
    import json
    user = frappe.session.user
    try:
        if isinstance(preferences, str):
            preferences = json.loads(preferences)
        pref_key = f"smriti_prefs_{user.replace('@', '_').replace('.', '_')}"
        frappe.cache().set_value(pref_key, preferences, expires_in_sec=ONE_YEAR_SECONDS)
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
