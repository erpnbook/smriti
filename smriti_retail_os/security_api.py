# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/security_api.py
# @description: Backend controller for SMRITI Security and Workflow Center.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import secrets
from frappe import _
from frappe.utils import cint
from frappe.utils.password import update_password


def _get_smriti_admin_email():
    """Returns the SMRITI Admin (Business Owner) email.
    Reads from site_config['smriti_admin_email'] if set, otherwise falls back
    to 'admin@<site_name>' so deployments without explicit config still work.
    """
    return frappe.conf.get("smriti_admin_email") or f"admin@{frappe.local.site}"


# ─── Security Governance Guards ──────────────────────────────────────────────

def check_administrator_only():
    """Raises PermissionError if caller is not the system Administrator."""
    if frappe.session.user != "Administrator" and "Administrator" not in frappe.get_roles():
        frappe.throw(
            _("Access Denied: This operation is restricted to the Security Architect (Administrator)."),
            frappe.PermissionError
        )

def check_store_manager_or_admin():
    """Raises PermissionError if caller is not a Store Manager, System Manager, or Administrator."""
    # Strict Default Security Model - Admin (Business Owner) Blockage
    _admin_email = _get_smriti_admin_email()
    if frappe.session.user in ("Admin", _admin_email):
        frappe.throw(
            _("Access Denied: The Admin (Business Owner) account is blocked from accessing the Security Center and User Administration."),
            frappe.PermissionError
        )

    if frappe.session.user == "Administrator":
        return
    roles = set(frappe.get_roles())
    allowed = {"SMRITI Store Manager", "System Manager", "Administrator"}
    if not (roles & allowed):
        frappe.throw(
            _("Access Denied: You do not have permissions to access SMRITI Security Center."),
            frappe.PermissionError
        )

def check_administrator_protection(email):
    """Raises PermissionError if trying to modify the Administrator account or any System Manager by a non-Administrator/System Manager."""
    if frappe.session.user == "Administrator" or "System Manager" in frappe.get_roles(frappe.session.user):
        return

    is_admin_target = False
    if email == "Administrator":
        is_admin_target = True
    else:
        admin_email = frappe.db.get_value("User", "Administrator", "email")
        if admin_email and email == admin_email:
            is_admin_target = True

    target_roles = []
    if frappe.db.exists("User", email):
        target_roles = frappe.get_roles(email)

    if is_admin_target or "System Manager" in target_roles or "Administrator" in target_roles:
        frappe.throw(
            _("Access Denied: Store Managers cannot modify System Manager or Administrator accounts."),
            frappe.PermissionError
        )

# ─── User Management ─────────────────────────────────────────────────────────

@frappe.whitelist()
def list_users():
    """Lists all standard users, their role profile, status and individual roles."""
    check_store_manager_or_admin()
    
    exclude_users = ["Guest"]
    if frappe.session.user != "Administrator" and "Administrator" not in frappe.get_roles():
        exclude_users.append("Administrator")
        admin_email = frappe.db.get_value("User", "Administrator", "email")
        if admin_email:
            exclude_users.append(admin_email)
            
    users = frappe.get_all(
        "User",
        filters={"name": ["not in", exclude_users], "user_type": "System User"},
        fields=["name", "email", "first_name", "last_name", "enabled", "role_profile_name"],
        order_by="first_name asc"
    )
    
    # Fetch all assigned roles to optimize N+1 queries
    has_roles = frappe.get_all(
        "Has Role",
        filters={"parenttype": "User"},
        fields=["parent", "role"]
    )
    
    user_roles_map = {}
    for r in has_roles:
        if r.parent not in user_roles_map:
            user_roles_map[r.parent] = []
        user_roles_map[r.parent].append(r.role)
        
    for u in users:
        u["roles"] = user_roles_map.get(u.name, [])
        
    return users

@frappe.whitelist()
def save_user(email, first_name, last_name=None, roles=None, role_profile=None):
    """Creates or updates a standard User document."""
    check_store_manager_or_admin()
    check_administrator_protection(email)
    
    if isinstance(roles, str):
        import json
        roles = json.loads(roles)
        
    if not email:
        frappe.throw(_("Email address is mandatory."))
        
    is_new = not frappe.db.exists("User", email)
    
    if is_new:
        user = frappe.new_doc("User")
        user.email = email
        user.send_welcome_email = 0
        user.first_name = first_name
        user.last_name = last_name
        user.role_profile_name = role_profile
        # SEC-02: Generate a cryptographically random one-time password.
        # This is NEVER exposed to the caller — the admin must send a password
        # reset email via the Security Centre "Send Reset Link" button.
        # Using secrets.token_urlsafe(16) guarantees uniqueness per user creation.
        user.new_password = secrets.token_urlsafe(16)
        # Force password reset on first login
        user.reset_password_key = frappe.generate_hash()

        if roles:
            user.set("roles", [{"role": r} for r in roles])

        user.insert(ignore_permissions=True)
        # Notify admin to send a reset link — the user cannot log in until they set a password
        frappe.log_error(
            title="SMRITI: New user created — password reset required",
            message=(
                f"User '{email}' was created with a random temporary password.\n"
                f"Go to Security Centre → Users → '{email}' → Send Reset Link "
                f"so the user can set their own password before first login."
            )
        )
    else:
        user = frappe.get_doc("User", email)
        user.first_name = first_name
        user.last_name = last_name
        user.role_profile_name = role_profile
        
        if roles is not None:
            user.set("roles", [{"role": r} for r in roles])
            
        user.save(ignore_permissions=True)
        
    frappe.db.commit()
    return {"success": True, "message": _("User saved successfully."), "email": email}

@frappe.whitelist()
def set_user_status(email, enabled):
    """Enables or disables a standard User."""
    check_store_manager_or_admin()
    check_administrator_protection(email)
    
    if not frappe.db.exists("User", email):
        frappe.throw(_("User {0} not found.").format(email))
        
    frappe.db.set_value("User", email, "enabled", cint(enabled))
    frappe.db.commit()
    
    status_str = _("activated") if cint(enabled) else _("deactivated")
    return {"success": True, "message": _("User {0} successfully {1}.").format(email, status_str)}

@frappe.whitelist()
def reset_user_password(email, password):
    """Updates standard user password securely."""
    check_store_manager_or_admin()
    check_administrator_protection(email)

    if not frappe.db.exists("User", email):
        frappe.throw(_("User {0} not found.").format(email))

    # SEC-01: Governance Guard - Prevent privilege escalation
    # If requester is not a System Manager or Administrator, restrict target selection
    if "Administrator" not in frappe.get_roles() and "System Manager" not in frappe.get_roles():
        target_roles = frappe.get_roles(email)

        # Block if target is a System Manager or Administrator
        if "System Manager" in target_roles or "Administrator" in target_roles:
            frappe.throw(
                _("Access Denied: Store Managers cannot reset passwords for System Managers or Administrators."),
                frappe.PermissionError
            )

        # Block if target has any desk-access roles other than SMRITI Cashier
        desk_roles = frappe.get_all("Role", filters={"desk_access": 1}, pluck="name")
        for role in target_roles:
            if role in desk_roles and role != "SMRITI Cashier":
                frappe.throw(
                    _("Access Denied: Store Managers can only reset passwords for Cashiers (users without administrative Desk access)."),
                    frappe.PermissionError
                )

    if not password or len(password) < 8:
        frappe.throw(_("Password must be at least 8 characters long."))

    update_password(email, password)
    frappe.db.commit()
    return {"success": True, "message": _("Password reset successfully for {0}.").format(email)}

@frappe.whitelist()
def set_user_pin(email, pin):
    """Sets the dedicated SMRITI POS PIN for a manager user.

    SEC-02: Managers use this 4–6 digit PIN for POS override actions, keeping
    their full login password hidden from cashiers at the counter.

    Rules:
    - Caller must be a Store Manager or Administrator.
    - PIN must be 4–6 numeric digits only.
    - Target user must have SMRITI Store Manager or System Manager role.
    - The Administrator account itself cannot have a PIN set via this endpoint.
    """
    check_store_manager_or_admin()
    check_administrator_protection(email)

    if not frappe.db.exists("User", email):
        frappe.throw(_("User {0} not found.").format(email))

    # Validate PIN format: 4–6 numeric digits
    import re
    if not pin or not re.fullmatch(r"\d{4,6}", str(pin)):
        frappe.throw(_("PIN must be 4 to 6 numeric digits only (e.g. 1234 or 123456)."))

    # Ensure target user is a manager (PINs are only for manager override accounts)
    target_roles = frappe.get_roles(email)
    if "SMRITI Store Manager" not in target_roles and "System Manager" not in target_roles:
        frappe.throw(
            _("POS Override PIN can only be set for users with SMRITI Store Manager or System Manager role."),
            frappe.PermissionError
        )

    from frappe.utils.password import update_password as _update_pw
    _update_pw(email, pin, fieldname="custom_smriti_pin")
    frappe.db.commit()

    frappe.log_error(
        title="SMRITI: Manager PIN Set",
        message=f"POS Override PIN was set for '{email}' by '{frappe.session.user}'."
    )
    return {"success": True, "message": _("POS Override PIN set successfully for {0}.").format(email)}

@frappe.whitelist()
def clear_user_pin(email):
    """Clears the SMRITI POS PIN for a manager user.

    Use this to revoke a manager's PIN access without changing their login password.
    Restricted to Administrator.
    """
    check_administrator_only()
    check_administrator_protection(email)

    if not frappe.db.exists("User", email):
        frappe.throw(_("User {0} not found.").format(email))

    # Clear the password hash by setting an empty sentinel value via DB
    frappe.db.set_value("User", email, "custom_smriti_pin", "")
    frappe.db.commit()

    frappe.log_error(
        title="SMRITI: Manager PIN Cleared",
        message=f"POS Override PIN was cleared for '{email}' by '{frappe.session.user}'."
    )
    return {"success": True, "message": _("POS Override PIN cleared for {0}.").format(email)}

@frappe.whitelist()
def get_user_metrics():
    """
    Returns user metrics/counts excluding Administrator:
    - total_users
    - store_managers
    - cashiers
    """
    # Access Check: Allow Admin (Business Owner) as well as standard Store Manager, System Manager, Administrator
    roles = set(frappe.get_roles())
    allowed = {"SMRITI Store Manager", "System Manager", "Administrator"}
    _admin_email = _get_smriti_admin_email()
    is_allowed = bool(roles & allowed) or frappe.session.user in ("Admin", _admin_email)
    if not is_allowed:
        frappe.throw(
            _("Access Denied: You do not have permissions to access User Metrics."),
            frappe.PermissionError
        )
        
    exclude_users = ["Guest"]
    admin_email = frappe.db.get_value("User", "Administrator", "email")
    if admin_email:
        exclude_users.append(admin_email)
    exclude_users.append("Administrator")
    
    total_users = frappe.db.count("User", filters={"name": ["not in", exclude_users], "user_type": "System User"})
    
    # Count SMRITI Store Manager
    # H-03 FIX: Do NOT use duplicate 'name' keys in a filters dict.
    # Python silently discards the first key, so the "not in exclude_users" filter
    # was being dropped, causing Administrator to be included in the count.
    # Fix: resolve eligible users first, then filter by role membership.
    store_manager_users = frappe.get_all(
        "Has Role",
        filters={"role": "SMRITI Store Manager", "parenttype": "User"},
        pluck="parent"
    )
    eligible_sm = [u for u in store_manager_users if u not in exclude_users]
    store_managers = frappe.db.count(
        "User",
        filters={
            "name": ["in", eligible_sm] if eligible_sm else ["in", ["__NONE__"]],
            "user_type": "System User"
        }
    ) if eligible_sm else 0
    
    # Count SMRITI Cashier
    cashier_users = frappe.get_all(
        "Has Role",
        filters={"role": "SMRITI Cashier", "parenttype": "User"},
        pluck="parent"
    )
    eligible_cashier = [u for u in cashier_users if u not in exclude_users]
    cashiers = frappe.db.count(
        "User",
        filters={
            "name": ["in", eligible_cashier] if eligible_cashier else ["in", ["__NONE__"]],
            "user_type": "System User"
        }
    ) if eligible_cashier else 0
    
    return {
        "total_users": total_users,
        "store_managers": store_managers,
        "cashiers": cashiers
    }

# ─── Role & Role Profile Management ──────────────────────────────────────────

@frappe.whitelist()
def list_roles():
    """Lists all available standard Roles."""
    check_store_manager_or_admin()
    return frappe.get_all("Role", fields=["name", "disabled"], order_by="name asc")

@frappe.whitelist()
def create_role(role_name):
    """Creates a new standard Role. Restricted to Security Architect."""
    check_administrator_only()
    
    if not role_name:
        frappe.throw(_("Role Name is mandatory."))
        
    if frappe.db.exists("Role", role_name):
        frappe.throw(_("Role {0} already exists.").format(role_name))
        
    doc = frappe.new_doc("Role")
    doc.role_name = role_name
    doc.insert(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "role": role_name}

@frappe.whitelist()
def delete_role(role_name):
    """Deletes a standard Role. Restricted to Security Architect."""
    check_administrator_only()
    
    if not frappe.db.exists("Role", role_name):
        frappe.throw(_("Role {0} not found.").format(role_name))
        
    frappe.delete_doc("Role", role_name, ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "message": _("Role {0} deleted successfully.").format(role_name)}

@frappe.whitelist()
def list_role_profiles():
    """Lists standard Role Profiles and their associated child roles."""
    check_store_manager_or_admin()
    
    profiles = frappe.get_all("Role Profile", fields=["name"], order_by="name asc")
    
    has_roles = frappe.get_all(
        "Has Role",
        filters={"parenttype": "Role Profile"},
        fields=["parent", "role"]
    )
    
    profile_roles_map = {}
    for r in has_roles:
        if r.parent not in profile_roles_map:
            profile_roles_map[r.parent] = []
        profile_roles_map[r.parent].append(r.role)
        
    for p in profiles:
        p["roles"] = profile_roles_map.get(p.name, [])
        
    return profiles

@frappe.whitelist()
def save_role_profile(name, roles):
    """Creates or updates a standard Role Profile. Restricted to Security Architect."""
    check_administrator_only()
    
    if isinstance(roles, str):
        import json
        roles = json.loads(roles)
        
    if not name:
        frappe.throw(_("Profile Name is mandatory."))
        
    is_new = not frappe.db.exists("Role Profile", name)
    
    if is_new:
        doc = frappe.new_doc("Role Profile")
        doc.role_profile = name
    else:
        doc = frappe.get_doc("Role Profile", name)
        
    doc.set("roles", [{"role": r} for r in (roles or [])])
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "name": name}

@frappe.whitelist()
def delete_role_profile(name):
    """Deletes standard Role Profile. Restricted to Security Architect."""
    check_administrator_only()
    
    if not frappe.db.exists("Role Profile", name):
        frappe.throw(_("Role Profile {0} not found.").format(name))
        
    frappe.delete_doc("Role Profile", name, ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "message": _("Role Profile {0} deleted successfully.").format(name)}

# ─── User Permission Management ──────────────────────────────────────────────

@frappe.whitelist()
def list_user_permissions(user=None):
    """Lists standard User Permissions, optionally filtered by user."""
    check_store_manager_or_admin()
    
    filters = {}
    if user:
        if user == "Administrator" or user == frappe.db.get_value("User", "Administrator", "email"):
            if frappe.session.user != "Administrator" and "Administrator" not in frappe.get_roles():
                return []
        filters["user"] = user
    else:
        if frappe.session.user != "Administrator" and "Administrator" not in frappe.get_roles():
            admin_email = frappe.db.get_value("User", "Administrator", "email")
            exclude_perms = ["Administrator"]
            if admin_email:
                exclude_perms.append(admin_email)
            filters["user"] = ["not in", exclude_perms]
            
    return frappe.get_all(
        "User Permission",
        filters=filters,
        fields=["name", "user", "allow", "for_value", "is_default"],
        order_by="user asc"
    )

@frappe.whitelist()
def add_user_permission(user, doctype, docname, is_default=0):
    """Creates a standard User Permission. Enforces Store Manager scoping."""
    check_store_manager_or_admin()
    
    # Block modifying Administrator permissions
    if user == "Administrator" or user == frappe.db.get_value("User", "Administrator", "email"):
        if frappe.session.user != "Administrator" and "Administrator" not in frappe.get_roles():
            frappe.throw(
                _("Access Denied: User Permissions for the Administrator account cannot be modified by non-Administrators."),
                frappe.PermissionError
            )
            
    # Store Manager Governance scoping block:
    if frappe.session.user != "Administrator" and "Administrator" not in frappe.get_roles():
        if doctype not in ("Company", "Warehouse"):
            frappe.throw(
                _("Access Denied: Store Managers can only assign Company and Warehouse permissions."),
                frappe.PermissionError
            )
            
    from frappe.permissions import add_user_permission as frappe_add_perm
    frappe_add_perm(doctype, docname, user, is_default=cint(is_default))
    frappe.db.commit()
    return {"success": True}

@frappe.whitelist()
def remove_user_permission(name):
    """Removes standard User Permission row. Enforces Store Manager scoping."""
    check_store_manager_or_admin()
    
    perm = frappe.get_value("User Permission", name, ["user", "allow", "for_value"], as_dict=1)
    if not perm:
        frappe.throw(_("User Permission row not found."))
        
    # Block modifying Administrator permissions
    if perm.user == "Administrator" or perm.user == frappe.db.get_value("User", "Administrator", "email"):
        if frappe.session.user != "Administrator" and "Administrator" not in frappe.get_roles():
            frappe.throw(
                _("Access Denied: User Permissions for the Administrator account cannot be modified by non-Administrators."),
                frappe.PermissionError
            )
            
    # Store Manager Governance scoping block:
    if frappe.session.user != "Administrator" and "Administrator" not in frappe.get_roles():
        if perm.allow not in ("Company", "Warehouse"):
            frappe.throw(
                _("Access Denied: Store Managers can only remove Company or Warehouse permissions."),
                frappe.PermissionError
            )
            
    from frappe.permissions import remove_user_permission as frappe_remove_perm
    frappe_remove_perm(perm.allow, perm.for_value, perm.user)
    frappe.db.commit()
    return {"success": True}

# ─── Workflow Engine & States ────────────────────────────────────────────────

@frappe.whitelist()
def list_workflows():
    """Lists standard workflow configurations."""
    check_store_manager_or_admin()
    return frappe.get_all("Workflow", fields=["name", "document_type", "is_active", "workflow_state_field"])

@frappe.whitelist()
def get_workflow_details(workflow_name):
    """Retrieves full workflow details (states and transitions child tables)."""
    check_store_manager_or_admin()
    
    if not frappe.db.exists("Workflow", workflow_name):
        frappe.throw(_("Workflow {0} not found.").format(workflow_name))
        
    doc = frappe.get_doc("Workflow", workflow_name)
    return {
        "name": doc.name,
        "document_type": doc.document_type,
        "is_active": doc.is_active,
        "workflow_state_field": doc.workflow_state_field,
        "states": [s.as_dict() for s in doc.states],
        "transitions": [t.as_dict() for t in doc.transitions]
    }

@frappe.whitelist()
def save_workflow(name, document_type, is_active, states, transitions):
    """Upserts standard Workflow. Restricted to Security Architect."""
    check_administrator_only()
    
    import json
    if isinstance(states, str):
        states = json.loads(states)
    if isinstance(transitions, str):
        transitions = json.loads(transitions)
        
    if not name or not document_type:
        frappe.throw(_("Workflow Name and Target Document Type are mandatory."))
        
    if frappe.db.exists("Workflow", name):
        doc = frappe.get_doc("Workflow", name)
        doc.document_type = document_type
        doc.is_active = cint(is_active)
        doc.states = []
        doc.transitions = []
    else:
        doc = frappe.new_doc("Workflow")
        doc.workflow_name = name
        doc.document_type = document_type
        doc.is_active = cint(is_active)
        doc.workflow_state_field = "workflow_state"
        
    # Append child states
    for s in (states or []):
        doc.append("states", {
            "state": s.get("state"),
            "doc_status": cint(s.get("doc_status", 0)),
            "allow_edit": s.get("allow_edit", "SMRITI Store Manager") or "SMRITI Store Manager"
        })
        
    # Append child transitions
    for t in (transitions or []):
        doc.append("transitions", {
            "state": t.get("state"),
            "action": t.get("action"),
            "next_state": t.get("next_state"),
            "allowed": t.get("allowed")
        })
        
    doc.save(ignore_permissions=True)
    frappe.db.commit()
    return {"success": True, "name": name}

@frappe.whitelist()
def delete_workflow(name):
    """Deletes standard Workflow. Restricted to Security Architect."""
    check_administrator_only()
    
    if not frappe.db.exists("Workflow", name):
        frappe.throw(_("Workflow {0} not found.").format(name))
        
    frappe.delete_doc("Workflow", name, ignore_permissions=True)
    frappe.db.commit()
    return {"success": True}

@frappe.whitelist()
def list_workflow_states():
    """Lists standard Workflow States."""
    check_store_manager_or_admin()
    return frappe.get_all("Workflow State", fields=["name", "style"], order_by="name asc")

@frappe.whitelist()
def save_workflow_state(name, style):
    """Creates or updates standard Workflow State. Restricted to Security Architect."""
    check_administrator_only()
    
    if not name:
        frappe.throw(_("State Name is mandatory."))
        
    if frappe.db.exists("Workflow State", name):
        doc = frappe.get_doc("Workflow State", name)
        doc.style = style
        doc.save(ignore_permissions=True)
    else:
        doc = frappe.new_doc("Workflow State")
        doc.workflow_state_name = name
        doc.style = style
        doc.insert(ignore_permissions=True)
        
    frappe.db.commit()
    return {"success": True, "name": name}

# ─── Actionable Approval Inbox ───────────────────────────────────────────────

@frappe.whitelist()
def get_pending_approvals():
    """
    Fetches active workflow documents needing session user's role approval.
    Direct integration with the standard Frappe workflow transitions.
    """
    check_store_manager_or_admin()
    user = frappe.session.user
    user_roles = frappe.get_roles(user)
    
    # Resolve all active standard Workflows
    workflows = frappe.get_all(
        "Workflow",
        filters={"is_active": 1},
        fields=["name", "document_type", "workflow_state_field"]
    )
    
    approvals = []
    for wf in workflows:
        try:
            wf_doc = frappe.get_doc("Workflow", wf.name)
        except Exception:
            continue
            
        allowed_states = set()
        state_actions = {}
        
        # Identify transitions available to this user's roles
        for t in wf_doc.transitions:
            if t.allowed in user_roles or user == "Administrator":
                allowed_states.add(t.state)
                if t.state not in state_actions:
                    state_actions[t.state] = []
                state_actions[t.state].append({
                    "action": t.action,
                    "next_state": t.next_state
                })
                
        if not allowed_states:
            continue
            
        state_field = wf.workflow_state_field or "workflow_state"
        
        try:
            # Query standard documents currently in allowed starting states
            docs = frappe.get_all(
                wf.document_type,
                filters={
                    state_field: ["in", list(allowed_states)],
                    "docstatus": ["<", 2]  # Exclude cancelled docs
                },
                fields=["name", "owner", "creation", state_field]
            )
            
            for d in docs:
                state = d.get(state_field)
                approvals.append({
                    "doctype": wf.document_type,
                    "name": d.name,
                    "owner": d.owner,
                    "creation": d.creation,
                    "state": state,
                    "actions": state_actions.get(state, [])
                })
        except Exception as e:
            frappe.log_error(f"[SMRITI] Error querying approvals for {wf.document_type}: {e}")
            
    return approvals

@frappe.whitelist()
def apply_workflow_action(doctype, docname, action):
    """Applies workflow transitions using standard frappe.model.workflow engine."""
    check_store_manager_or_admin()
    
    if not doctype or not docname or not action:
        frappe.throw(_("DocType, Document Name, and Action are all mandatory."))
        
    doc = frappe.get_doc(doctype, docname)
    
    from frappe.model.workflow import apply_workflow
    apply_workflow(doc, action)
    frappe.db.commit()
    return {"success": True, "message": _("Action '{0}' successfully applied.").format(action)}


# ── Session Lock: Password Verification ──────────────────────────────────────

@frappe.whitelist()
def verify_user_password(password):
    """
    Verifies the current session user's login password.
    Used by the SMRITI Session Lock overlay to allow the cashier to unlock
    the terminal with their own credentials.

    Returns { success: True } on match, raises PermissionError on failure.
    Intentionally uses Frappe's check_password() for constant-time comparison.
    """
    if not password:
        frappe.throw(_("Password is required."), frappe.ValidationError)

    user = frappe.session.user
    if user in ("Guest", ""):
        frappe.throw(_("Not authenticated."), frappe.PermissionError)

    try:
        from frappe.utils.password import check_password
        check_password(user, password)
        return {"success": True}
    except frappe.AuthenticationError:
        # Do not reveal whether user exists — just reject
        frappe.throw(
            _("Incorrect password. Please try again or use manager PIN override."),
            frappe.AuthenticationError
        )


# ── Session Lock: Manager List for Dropdown ───────────────────────────────────

@frappe.whitelist()
def get_managers_list():
    """
    Returns a list of active users with SMRITI Store Manager or System Manager roles
    who have a POS Override PIN set. Used to populate the manager dropdown on the
    Session Lock overlay.
    """
    manager_roles = ["SMRITI Store Manager", "System Manager"]

    users = frappe.db.get_all(
        "Has Role",
        filters={"role": ["in", manager_roles]},
        pluck="parent"
    )
    unique_users = list(set(users) - {"Administrator", "Guest"})

    result = []
    for u in unique_users:
        user_doc = frappe.db.get_value(
            "User",
            u,
            ["name", "full_name", "enabled", "custom_smriti_pin"],
            as_dict=True
        )
        if user_doc and user_doc.get("enabled") and user_doc.get("custom_smriti_pin"):
            result.append({
                "name":      user_doc["name"],
                "full_name": user_doc.get("full_name") or user_doc["name"],
            })

    result.sort(key=lambda x: x["full_name"])
    return result

