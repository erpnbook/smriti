# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/verify_security.py
# @description: Automated sanity-check runner for the SMRITI Security & Workflow Center APIs.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#


import sys
import os

import frappe
from smriti_retail_os.security_api import (
    list_users, save_user, set_user_status, reset_user_password,
    list_roles, create_role, delete_role,
    list_role_profiles, save_role_profile, delete_role_profile,
    list_user_permissions, add_user_permission, remove_user_permission,
    list_workflows, get_workflow_details, save_workflow, delete_workflow,
    list_workflow_states, save_workflow_state,
    get_pending_approvals, apply_workflow_action, get_user_metrics,
    _get_smriti_admin_email
)

def run_tests():
    print("\n[SMRITI SECURITY] Starting Automated Sanity Checks...")
    errors = 0
    
    # 1. Force context to Administrator
    frappe.set_user("Administrator")
    
    # 2. Test User Management
    print("\n1. Testing User Management Controllers:")
    try:
        users = list_users()
        print(f"  [OK] list_users() successfully fetched {len(users)} users.")
        
        # Test creating a user
        test_email = "sanity_check_mgr@gmail.com"
        save_user(test_email, "Sanity", "Manager")
        if frappe.db.exists("User", test_email):
            print(f"  [OK] save_user() successfully inserted '{test_email}'.")
        else:
            print(f"  [ERROR] User '{test_email}' was not created!")
            errors += 1
            
        # Test disabling user
        set_user_status(test_email, 0)
        status = frappe.db.get_value("User", test_email, "enabled")
        if status == 0:
            print("  [OK] set_user_status() successfully disabled the user.")
        else:
            print("  [ERROR] User status did not change!")
            errors += 1
            
        # Test password reset
        reset_user_password(test_email, "SanityPassword123!")
        print("  [OK] reset_user_password() successfully updated password.")
        
        # Clean up user
        frappe.delete_doc("User", test_email, ignore_permissions=True)
        print("  [OK] User cleanup successful.")
    except Exception as e:
        print(f"  [ERROR] User APIs crashed: {str(e)}")
        errors += 1
        
    # 3. Test Roles
    print("\n2. Testing Role Management Controllers:")
    try:
        roles = list_roles()
        print(f"  [OK] list_roles() successfully returned {len(roles)} roles.")
        
        test_role = "SMRITI Sanity Role"
        create_role(test_role)
        if frappe.db.exists("Role", test_role):
            print(f"  [OK] create_role() successfully inserted role.")
        else:
            print("  [ERROR] Role was not created!")
            errors += 1
            
        delete_role(test_role)
        if not frappe.db.exists("Role", test_role):
            print("  [OK] delete_role() successfully removed role.")
        else:
            print("  [ERROR] Role deletion failed!")
            errors += 1
    except Exception as e:
        print(f"  [ERROR] Role APIs crashed: {str(e)}")
        errors += 1

    # 4. Test Role Profiles
    print("\n3. Testing Role Profile Controllers:")
    try:
        profiles = list_role_profiles()
        print(f"  [OK] list_role_profiles() successfully returned {len(profiles)} profiles.")
        
        import random, string
        rand_suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=4))
        test_profile = f"SMRITI Sanity Profile {rand_suffix}"
        save_role_profile(test_profile, ["System Manager"])
        if frappe.db.exists("Role Profile", test_profile):
            print(f"  [OK] save_role_profile() successfully created role profile.")
        else:
            print("  [ERROR] Role Profile creation failed!")
            errors += 1
            
        delete_role_profile(test_profile)
        if not frappe.db.exists("Role Profile", test_profile):
            print("  [OK] delete_role_profile() successfully deleted role profile.")
        else:
            print("  [ERROR] Role Profile deletion failed!")
            errors += 1
    except Exception as e:
        print(f"  [ERROR] Role Profile APIs crashed: {str(e)}")
        errors += 1

    # 5. Test User Permissions
    print("\n4. Testing User Permission Row Scoping Controllers:")
    try:
        companies = frappe.get_all("Company", limit=1, pluck="name")
        if companies:
            comp = companies[0]
            test_user = "sanity_perm@gmail.com"
            save_user(test_user, "Sanity", "Perm")
            
            add_user_permission(test_user, "Company", comp, is_default=1)
            
            perms = list_user_permissions(test_user)
            if len(perms) > 0 and perms[0].for_value == comp:
                print("  [OK] add_user_permission() successfully created row-level rule.")
            else:
                print("  [ERROR] Permission was not created or resolved!")
                errors += 1
                
            remove_user_permission(perms[0].name)
            perms = list_user_permissions(test_user)
            if len(perms) == 0:
                print("  [OK] remove_user_permission() successfully removed permission row.")
            else:
                print("  [ERROR] Permission removal failed!")
                errors += 1
                
            frappe.delete_doc("User", test_user, ignore_permissions=True)
            print("  [OK] User Permission cleanup complete.")
        else:
            print("  [SKIP] No companies found to test row level permissions.")
    except Exception as e:
        print(f"  [ERROR] Permission APIs crashed: {str(e)}")
        errors += 1

    # 6. Test Workflow
    print("\n5. Testing Workflow Engine Controllers:")
    try:
        workflows = list_workflows()
        print(f"  [OK] list_workflows() returned {len(workflows)} workflows.")
        
        # Test creating custom Workflow State
        test_state = "SMRITI Sanity State"
        save_workflow_state(test_state, "Success")
        if frappe.db.exists("Workflow State", test_state):
            print("  [OK] save_workflow_state() successfully created state.")
        else:
            print("  [ERROR] Workflow State creation failed!")
            errors += 1
            
        # Test creating custom Workflow
        test_wf = "SMRITI Sanity Flow"
        states = [
            {"state": test_state, "doc_status": 0, "allow_edit": "SMRITI Store Manager"}
        ]
        transitions = []
        save_workflow(test_wf, "POS Invoice", 1, states, transitions)
        if frappe.db.exists("Workflow", test_wf):
            print("  [OK] save_workflow() successfully saved Workflow.")
            
            wf_details = get_workflow_details(test_wf)
            if wf_details and len(wf_details.get("states", [])) > 0:
                print("  [OK] get_workflow_details() successfully resolved child rows.")
            else:
                print("  [ERROR] get_workflow_details() returned invalid details!")
                errors += 1
        else:
            print("  [ERROR] save_workflow() failed to write configuration!")
            errors += 1
            
        delete_workflow(test_wf)
        frappe.delete_doc("Workflow State", test_state, ignore_permissions=True)
        print("  [OK] Workflow and state cleanup successful.")
    except Exception as e:
        print(f"  [ERROR] Workflow APIs crashed: {str(e)}")
        errors += 1

    # 7. Test Approvals Inbox
    print("\n6. Testing Approvals Inbox Resolution:")
    try:
        approvals = get_pending_approvals()
        print(f"  [OK] get_pending_approvals() successfully resolved {len(approvals)} open approvals.")
    except Exception as e:
        print(f"  [ERROR] Approvals Inbox crashed: {str(e)}")
        errors += 1

    # 8. Test Administrator Isolation and Operational Metrics
    print("\n7. Testing Administrator Isolation & Operational Metrics:")
    try:
        # Create a Store Manager session for isolation testing
        test_mgr = "sanity_mgr_iso@gmail.com"
        save_user(test_mgr, "Sanity", "MgrIso", roles=["SMRITI Store Manager"])
        
        frappe.set_user(test_mgr)
        
        # Test 1: list_users must filter out Administrator and its email
        users = list_users()
        admin_emails = ["Administrator"]
        admin_email = frappe.db.get_value("User", "Administrator", "email")
        if admin_email:
            admin_emails.append(admin_email)
            
        found_admin = any(u.email in admin_emails or u.name in admin_emails for u in users)
        if not found_admin:
            print("  [OK] list_users() successfully filtered out Administrator account.")
        else:
            print("  [ERROR] list_users() leaked the Administrator account!")
            errors += 1
            
        # Test 2: list_user_permissions must filter out Administrator
        perms = list_user_permissions()
        found_admin_perm = any(p.user in admin_emails for p in perms)
        if not found_admin_perm:
            print("  [OK] list_user_permissions() successfully filtered out Administrator permissions.")
        else:
            print("  [ERROR] list_user_permissions() leaked Administrator permissions!")
            errors += 1
            
        # Test 3: Block editing Administrator Details
        try:
            save_user("Administrator", "Hack", "Admin")
            print("  [ERROR] save_user() allowed non-Admin to edit Administrator details!")
            errors += 1
        except frappe.PermissionError:
            print("  [OK] save_user() successfully blocked non-Admin from editing Administrator details.")
        except Exception as e:
            print(f"  [ERROR] save_user() raised unexpected exception for Administrator edit: {e}")
            errors += 1
            
        # Test 4: Block setting Administrator Status
        try:
            set_user_status("Administrator", 0)
            print("  [ERROR] set_user_status() allowed non-Admin to modify Administrator status!")
            errors += 1
        except frappe.PermissionError:
            print("  [OK] set_user_status() successfully blocked non-Admin from modifying Administrator status.")
        except Exception as e:
            print(f"  [ERROR] set_user_status() raised unexpected exception for Administrator status change: {e}")
            errors += 1
            
        # Test 5: Block resetting Administrator Password
        try:
            reset_user_password("Administrator", "HackPassword123!")
            print("  [ERROR] reset_user_password() allowed non-Admin to reset Administrator password!")
            errors += 1
        except frappe.PermissionError:
            print("  [OK] reset_user_password() successfully blocked non-Admin from resetting Administrator password.")
        except Exception as e:
            print(f"  [ERROR] reset_user_password() raised unexpected exception for Administrator password reset: {e}")
            errors += 1
            
        # Test 6: Block adding Administrator Permissions
        try:
            companies = frappe.get_all("Company", limit=1, pluck="name")
            comp = companies[0] if companies else "SMRITI Company"
            add_user_permission("Administrator", "Company", comp)
            print("  [ERROR] add_user_permission() allowed non-Admin to add permission to Administrator!")
            errors += 1
        except frappe.PermissionError:
            print("  [OK] add_user_permission() successfully blocked non-Admin from adding permission to Administrator.")
        except Exception as e:
            print(f"  [ERROR] add_user_permission() raised unexpected exception: {e}")
            errors += 1

        # Test 7: Block Admin (Business Owner) from security features but allow metrics
        _admin_email = _get_smriti_admin_email()
        frappe.set_user(_admin_email)
        try:
            list_users()
            print("  [ERROR] list_users() allowed Admin (Business Owner) to access user list!")
            errors += 1
        except frappe.PermissionError:
            print("  [OK] list_users() successfully blocked Admin (Business Owner) from user list.")
        except Exception as e:
            print(f"  [ERROR] list_users() raised unexpected exception for Admin: {e}")
            errors += 1
            
        # Test 8: Fetch operational metrics successfully
        try:
            metrics = get_user_metrics()
            if "total_users" in metrics and "store_managers" in metrics and "cashiers" in metrics:
                print(f"  [OK] get_user_metrics() successfully returned counts for Admin: {metrics}")
            else:
                print("  [ERROR] get_user_metrics() returned invalid data structure!")
                errors += 1
        except Exception as e:
            print(f"  [ERROR] get_user_metrics() crashed for Admin: {e}")
            errors += 1

        # Reset user back to Administrator
        frappe.set_user("Administrator")
        frappe.delete_doc("User", test_mgr, ignore_permissions=True)
        print("  [OK] Isolation test cleanup successful.")
        
    except Exception as e:
        print(f"  [ERROR] Isolation tests crashed: {e}")
        errors += 1

    print(f"\n[SMRITI SECURITY] Sanity Checks Complete. Total Errors: {errors}")
    if errors == 0:
         print("[SMRITI SECURITY] ALL API ENDPOINTS STABLE AND VALIDATED.")
    else:
         print("[SMRITI SECURITY] Validation failed. Please check logs.")

if __name__ == "__main__":
    # Initialize frappe session manually if executing direct python shell
    frappe.init(site="smriti_retail", sites_path="/home/frappe/frappe-bench/sites")
    frappe.connect()
    run_tests()
