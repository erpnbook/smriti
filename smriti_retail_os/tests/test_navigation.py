# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_navigation.py
# @description: Unit tests verifying SMRITI Navigation Manager (SNM) resolution, overrides, and caching.
# @author: Jawahar R. Mallah
#

import unittest
import frappe
from smriti_retail_os.navigation.navigation_service import (
    get_user_navigation,
    invalidate_navigation_cache,
    CANONICAL_NAV
)

class TestSMRITINavigation(unittest.TestCase):
    def setUp(self):
        # Clean up database records first
        frappe.db.delete("SMRITI Navigation Assignment")
        frappe.db.delete("SMRITI Navigation Override")
        frappe.db.delete("SMRITI Navigation Profile")
        invalidate_navigation_cache()
        
    def tearDown(self):
        frappe.db.delete("SMRITI Navigation Assignment")
        frappe.db.delete("SMRITI Navigation Override")
        frappe.db.delete("SMRITI Navigation Profile")
        invalidate_navigation_cache()

    def test_canonical_fallback(self):
        """
        Verifies that when no profiles/overrides exist, resolution defaults to CANONICAL_NAV.
        """
        nav = get_user_navigation("Administrator")
        self.assertEqual(nav["sections"][0]["id"], "masters")
        self.assertEqual(len(nav["sections"]), len(CANONICAL_NAV["sections"]))

    def test_profile_overrides(self):
        """
        Verifies overrides are successfully merged on top of the canonical structure.
        """
        # 1. Create a Navigation Profile
        profile = frappe.get_doc({
            "doctype": "SMRITI Navigation Profile",
            "profile_name": "Test Manager Profile",
            "version": "1.0.0"
        }).insert()
        
        # 2. Create Override
        frappe.get_doc({
            "doctype": "SMRITI Navigation Override",
            "menu_id": "masters",
            "navigation_profile": "Test Manager Profile",
            "override_state": "Override",
            "label_override": "Core Masters Setup",
            "display_order": 99
        }).insert()
        
        # Disable item under masters
        frappe.get_doc({
            "doctype": "SMRITI Navigation Override",
            "menu_id": "brand_master",
            "navigation_profile": "Test Manager Profile",
            "override_state": "Disabled"
        }).insert()

        # 3. Create User Assignment
        frappe.get_doc({
            "doctype": "SMRITI Navigation Assignment",
            "assignment_type": "User",
            "assign_to": "Administrator",
            "navigation_profile": "Test Manager Profile",
            "priority": 100
        }).insert()
        
        # Resolve
        nav = get_user_navigation("Administrator")
        
        # Locate resolved sections
        sec_map = {s["id"]: s for s in nav["sections"]}
        
        # Verify Section level label override and order shift
        self.assertIn("masters", sec_map)
        self.assertEqual(sec_map["masters"]["label"], "Core Masters Setup")
        self.assertEqual(sec_map["masters"]["display_order"], 99)
        
        # Verify Item level disable override
        masters_items = {item["id"]: item for item in sec_map["masters"]["items"]}
        self.assertNotIn("brand_master", masters_items)

    def test_cache_invalidation(self):
        """
        Verifies cache is updated dynamically when custom assignments shift.
        """
        # Initial canonical resolution
        nav1 = get_user_navigation("Administrator")
        self.assertEqual(nav1["sections"][0]["label"], "Masters")

        # Create Profile
        profile = frappe.get_doc({
            "doctype": "SMRITI Navigation Profile",
            "profile_name": "Cache Test Profile",
            "version": "1.0.0"
        }).insert()
        
        # Create Override
        frappe.get_doc({
            "doctype": "SMRITI Navigation Override",
            "menu_id": "masters",
            "navigation_profile": "Cache Test Profile",
            "override_state": "Override",
            "label_override": "Modified Label"
        }).insert()

        # Create Assignment (triggers cache clear automatically on insert hooks)
        frappe.get_doc({
            "doctype": "SMRITI Navigation Assignment",
            "assignment_type": "User",
            "assign_to": "Administrator",
            "navigation_profile": "Cache Test Profile",
            "priority": 50
        }).insert()

        # Re-resolve and verify cache was updated
        nav2 = get_user_navigation("Administrator")
        sec_map = {s["id"]: s for s in nav2["sections"]}
        self.assertEqual(sec_map["masters"]["label"], "Modified Label")
