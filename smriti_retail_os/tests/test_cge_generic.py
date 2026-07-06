# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_cge_generic.py
# @description: Generic CGE test cases — edge cases and boundary conditions.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/tests/test_cge_generic.py
# @description: Hardened unit tests for SMRITI CGE Generic CRUD APIs & Route Resolution.
# @author: Antigravity AI
# @date: 2026-06-19
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
import json

from smriti_retail_os.cge.api.cge_api import (
    get_cge_generic_fields,
    get_cge_generic_list,
    get_cge_generic_doc,
    save_cge_generic_doc,
    delete_cge_generic_doc
)
from smriti_retail_os.www.cge_generic import get_context

class TestCGEGenericAPI(unittest.TestCase):
    def setUp(self):
        # Default test user: Administrator (Full Access)
        self.set_user_and_clear_roles("Administrator")
        self.test_doctype = "SMRITI Membership Tier"
        self.test_tier_name = "_Test API Tier"
        self.test_employee_email = "test_employee@erpnbook.com"
        
        # Clean up any residual test tiers & resolution policies & users (prevent test contamination)
        frappe.db.delete(self.test_doctype, {"tier_name": self.test_tier_name})
        frappe.db.delete("SMRITI Benefit Resolution Policy", {"policy_name": "_Test Resolution Policy"})
        if frappe.db.exists("User", self.test_employee_email):
            frappe.delete_doc("User", self.test_employee_email, ignore_permissions=True)
        else:
            frappe.db.delete("Has Role", {"parent": self.test_employee_email})
        frappe.db.commit()

    def tearDown(self):
        # Restore user session and clean up
        self.set_user_and_clear_roles("Administrator")
        frappe.db.delete(self.test_doctype, {"tier_name": self.test_tier_name})
        frappe.db.delete("SMRITI Benefit Resolution Policy", {"policy_name": "_Test Resolution Policy"})
        if frappe.db.exists("User", self.test_employee_email):
            frappe.delete_doc("User", self.test_employee_email, ignore_permissions=True)
        else:
            frappe.db.delete("Has Role", {"parent": self.test_employee_email})
        frappe.db.commit()

    def set_user_and_clear_roles(self, user):
        """Switches the current user and clears request-local roles cache to ensure re-evaluation."""
        frappe.set_user(user)
        for key in ["roles", "all_roles", "role_profile"]:
            if hasattr(frappe.local, key):
                delattr(frappe.local, key)

    def test_get_cge_generic_fields(self):
        """Verify we can retrieve fields metadata for CGE DocTypes."""
        fields = get_cge_generic_fields(self.test_doctype)
        self.assertTrue(isinstance(fields, list))
        self.assertTrue(any(f["fieldname"] == "tier_name" for f in fields))

    def test_get_cge_generic_fields_unauthorized_doctype(self):
        """Verify invalid DocType check blocks access."""
        with self.assertRaises(frappe.PermissionError):
            get_cge_generic_fields("User")

    def test_cge_crud_operations(self):
        """Verify we can list, save, view, and delete documents via the generic endpoints."""
        doc_data = {
            "tier_name": self.test_tier_name,
            "min_points": 1000.0,
            "min_lifetime_spend": 50000.0,
            "tier_multiplier": 1.5,
            "active": 1
        }
        
        doc_name = save_cge_generic_doc(self.test_doctype, doc_data)
        self.assertTrue(doc_name)
        self.assertTrue(frappe.db.exists(self.test_doctype, doc_name))

        doc_details = get_cge_generic_doc(self.test_doctype, doc_name)
        self.assertEqual(doc_details.get("tier_name"), self.test_tier_name)

        records = get_cge_generic_list(self.test_doctype)
        self.assertTrue(any(r["name"] == doc_name for r in records))

        res = delete_cge_generic_doc(self.test_doctype, doc_name)
        self.assertTrue(res)
        self.assertFalse(frappe.db.exists(self.test_doctype, doc_name))

    # --- CGE-TEST-04: Permission Enforcement ---
    def test_cge_permission_enforcement(self):
        """Verify Guest and unauthorized Employee roles are blocked from CGE configuration."""
        # Test 1: Guest is blocked
        self.set_user_and_clear_roles("Guest")
        with self.assertRaises(frappe.PermissionError):
            get_cge_generic_list(self.test_doctype)

        # Test 2: Standard non-manager User is blocked
        self.set_user_and_clear_roles("Administrator")
        user = frappe.new_doc("User")
        user.email = self.test_employee_email
        user.first_name = "Test Employee"
        # Give cashier access (not manager access)
        user.append("roles", {"role": "SMRITI Cashier"})
        user.insert(ignore_permissions=True)
        frappe.db.commit()
            
        frappe.clear_cache(user=self.test_employee_email)
        self.set_user_and_clear_roles(self.test_employee_email)
        with self.assertRaises(frappe.PermissionError):
            get_cge_generic_list(self.test_doctype)

        # Test 3: SMRITI Store Manager is allowed
        self.set_user_and_clear_roles("Administrator")
        frappe.get_doc("User", self.test_employee_email).append("roles", {"role": "SMRITI Store Manager"}).save(ignore_permissions=True)
        frappe.clear_cache(user=self.test_employee_email)
        frappe.db.commit()
        
        self.set_user_and_clear_roles(self.test_employee_email)
        # Should execute without throwing PermissionError
        records = get_cge_generic_list(self.test_doctype)
        self.assertTrue(isinstance(records, list))

        # Cleanup handled in tearDown
        self.set_user_and_clear_roles("Administrator")

    # --- CGE-TEST-05: Child Table Save Integrity ---
    def test_cge_child_table_integrity(self):
        """Verify dynamic child table rows can be inserted, edited, deleted, and reload correctly."""
        policy_doctype = "SMRITI Benefit Resolution Policy"
        child_fieldname = "sequence_details"
        
        # 1. Insert with child rows
        policy_data = {
            "policy_name": "_Test Resolution Policy",
            "is_active": 1,
            child_fieldname: [
                {"benefit_type": "Loyalty", "execution_order": 1, "allow_stacking": 1, "exclusive_rule": 0},
                {"benefit_type": "Cashback", "execution_order": 2, "allow_stacking": 0, "exclusive_rule": 1}
            ]
        }
        
        doc_name = save_cge_generic_doc(policy_doctype, policy_data)
        self.assertTrue(doc_name)

        # 2. Reload and verify child rows
        doc = get_cge_generic_doc(policy_doctype, doc_name)
        child_rows = doc.get(child_fieldname) or []
        self.assertEqual(len(child_rows), 2)
        self.assertEqual(child_rows[0]["benefit_type"], "Loyalty")
        self.assertEqual(int(child_rows[0]["execution_order"]), 1)
        self.assertEqual(child_rows[1]["benefit_type"], "Cashback")

        # 3. Edit one child row and delete the other
        edited_rows = [
            # Keep first and edit it
            {"benefit_type": "Loyalty", "execution_order": 3, "allow_stacking": 0, "exclusive_rule": 0},
            # Append a new one
            {"benefit_type": "Voucher", "execution_order": 4, "allow_stacking": 1, "exclusive_rule": 0}
            # Cashback row deleted (omitted)
        ]
        policy_data["name"] = doc_name
        policy_data[child_fieldname] = edited_rows

        save_cge_generic_doc(policy_doctype, policy_data)

        # 4. Reload and verify child rows modifications
        reloaded_doc = get_cge_generic_doc(policy_doctype, doc_name)
        reloaded_rows = reloaded_doc.get(child_fieldname) or []
        self.assertEqual(len(reloaded_rows), 2)
        self.assertEqual(reloaded_rows[0]["benefit_type"], "Loyalty")
        self.assertEqual(int(reloaded_rows[0]["execution_order"]), 3)
        self.assertEqual(reloaded_rows[1]["benefit_type"], "Voucher")
        self.assertTrue(all(r["benefit_type"] != "Cashback" for r in reloaded_rows))

        # Cleanup
        delete_cge_generic_doc(policy_doctype, doc_name)

    # --- CGE-TEST-06: Route Resolution ---
    def test_cge_route_resolution(self):
        """Verify that all 12 CGE URLs resolve to their correct SMRITI DocTypes."""
        route_mappings = {
            "/cge-benefit-instruments": "SMRITI Benefit Instrument",
            "/cge-membership-tiers": "SMRITI Membership Tier",
            "/cge-loyalty-programs": "SMRITI Loyalty Program",
            "/cge-campaigns": "SMRITI Campaign",
            "/cge-promotion-rules": "SMRITI Promotion Rule",
            "/cge-coupon-rules": "SMRITI Coupon Rule",
            "/cge-loyalty-rules": "SMRITI Loyalty Rule",
            "/cge-benefit-wallets": "SMRITI Benefit Wallet",
            "/cge-customer-benefit-profiles": "SMRITI Customer Benefit Profile",
            "/cge-benefit-resolution-policies": "SMRITI Benefit Resolution Policy",
            "/cge-liability-snapshots": "SMRITI Benefit Liability Snapshot",
            "/cge-benefit-audit-logs": "SMRITI Benefit Audit Log"
        }

        # Backup current local request if any
        orig_request = getattr(frappe.local, 'request', None)

        for route, expected_dt in route_mappings.items():
            # Mock request path in local context
            frappe.local.request = frappe._dict(path=route)
            
            ctx = get_context(frappe._dict())
            self.assertEqual(ctx.target_doctype, expected_dt, f"Route {route} resolved to {ctx.target_doctype} instead of {expected_dt}!")

        # Restore request context
        if orig_request:
            frappe.local.request = orig_request
        else:
            del frappe.local.request

    # --- CGE-TEST-07: Delete Protection ---
    def test_cge_delete_protection_referential_integrity(self):
        """Verify that referential integrity is preserved and deleting linked records is blocked."""
        instrument_doctype = "SMRITI Benefit Instrument"
        wallet_doctype = "SMRITI Benefit Wallet"
        
        test_inst = "_Test Linked Instrument"
        test_cust = "_Test Linked Customer"
        test_comp = frappe.get_all("Company", limit=1)[0].name

        # 1. Setup Customer & Instrument
        if not frappe.db.exists("Customer", test_cust):
            frappe.get_doc({
                "doctype": "Customer",
                "customer_name": test_cust,
                "customer_group": "Individual"
            }).insert(ignore_permissions=True)

        if not frappe.db.exists("SMRITI Benefit Instrument Type", "CASHBACK"):
            frappe.get_doc({
                "doctype": "SMRITI Benefit Instrument Type",
                "type_name": "CASHBACK"
            }).insert(ignore_permissions=True)

        inst_doc = frappe.get_doc({
            "doctype": instrument_doctype,
            "instrument_name": test_inst,
            "instrument_type": "CASHBACK",
            "validity_days": 90,
            "allow_negative_balance": 0
        })
        inst_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # 2. Setup Wallet referencing the Instrument
        wallet_doc = frappe.get_doc({
            "doctype": wallet_doctype,
            "customer": test_cust,
            "company": test_comp,
            "benefit_instrument": test_inst,
            "balance": 150.0
        })
        wallet_doc.insert(ignore_permissions=True)
        frappe.db.commit()

        # 3. Attempt to delete the Instrument while Wallet references it
        # This must raise a LinkExistsError (standard Frappe deletion safety check)
        with self.assertRaises(frappe.LinkExistsError):
            delete_cge_generic_doc(instrument_doctype, test_inst)

        # Cleanup
        frappe.db.delete(wallet_doctype, {"benefit_instrument": test_inst})
        frappe.db.delete(instrument_doctype, {"instrument_name": test_inst})
        frappe.db.delete("Customer", {"name": test_cust})
        frappe.db.commit()
