# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_company_api.py
# @description: Unit tests for SMRITI Company Settings, resolution helpers, and provision hooks.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-31
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
import json
from smriti_retail_os.company_api import (
    get_active_company,
    get_company_settings,
    save_company_settings,
    ensure_company_settings,
    get_setting,
    get_size_groups,
    get_destinationwise_taxes,
    get_backup_settings,
)

class TestSmritiCompanyAPI(unittest.TestCase):
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from smriti_retail_os.setup import setup_smriti_retail_os
        setup_smriti_retail_os()
        frappe.db.commit()

        # Clean up any residual test companies
        frappe.db.delete("Company", {"company_name": "Test Company Ltd"})
        if frappe.db.exists("DocType", "SMRITI Company Settings"):
            frappe.db.delete("SMRITI Company Settings", {"company": "Test Company Ltd"})
        frappe.db.commit()

    def setUp(self):
        # Create a clean test company
        self.company_name = "Test Company Ltd"
        self.company = frappe.new_doc("Company")
        self.company.company_name = self.company_name
        self.company.default_currency = "INR"
        self.company.country = "India"
        self.company.insert(ignore_permissions=True)
        frappe.db.commit()

    def tearDown(self):
        # Remove the test company and settings
        frappe.db.delete("Company", {"company_name": self.company_name})
        frappe.db.delete("SMRITI Company Settings", {"company": self.company_name})
        frappe.db.commit()

    def test_active_company_resolution(self):
        """Tests that get_active_company returns a valid company when defaults are set/unset."""
        active = get_active_company()
        self.assertIsNotNone(active)

        # Set user default and verify it resolves to that first
        frappe.defaults.set_user_default("company", self.company_name)
        self.assertEqual(get_active_company(), self.company_name)

        # Clean default
        frappe.defaults.clear_user_default("company")

    def test_ensure_company_settings_hook(self):
        """Tests that ensure_company_settings hook auto-provisions settings for new companies."""
        # Check that settings exist for self.company_name (created during insert in setUp)
        settings_exist = frappe.db.exists("SMRITI Company Settings", {"company": self.company_name})
        self.assertTrue(settings_exist)

        # If deleted, ensure_company_settings should restore it when called manually
        frappe.db.delete("SMRITI Company Settings", {"company": self.company_name})
        frappe.db.commit()
        self.assertFalse(frappe.db.exists("SMRITI Company Settings", {"company": self.company_name}))

        ensure_company_settings(self.company)
        self.assertTrue(frappe.db.exists("SMRITI Company Settings", {"company": self.company_name}))

    def test_get_company_settings_defaults(self):
        """Tests that get_company_settings returns in-memory defaults if settings record is missing."""
        temp_company = "Temp In Memory Company"
        # Verify no database record exists
        self.assertFalse(frappe.db.exists("SMRITI Company Settings", {"company": temp_company}))

        # Load settings and verify default fields are present
        settings = get_company_settings(temp_company)
        self.assertEqual(settings.get("company"), temp_company)
        self.assertEqual(settings.get("brand_color"), "#1a73e8")
        self.assertEqual(settings.get("invoice_series_prefix"), "SINV-")
        self.assertEqual(settings.get("receipt_footer_text"), "Thank you for shopping with us!")
        self.assertEqual(settings.get("loyalty_enabled"), 0)

    def test_save_and_retrieve_settings(self):
        """Tests that saving company settings persists to database and getters fetch values correctly."""
        # Set administrator session to bypass role permission check in save_company_settings
        orig_user = frappe.session.user
        frappe.session.user = "Administrator"
        try:
            settings_payload = {
                "store_trade_name": "Tattly Outlet",
                "brand_color": "#ff00ff",
                "invoice_series_prefix": "TT-INV-",
                "receipt_footer_text": "Come back soon!",
                "loyalty_enabled": 1,
                "loyalty_points_per_rupee": 2.5,
                "size_groups_json": json.dumps([{"id": "test_sizes", "sizes": ["S", "M", "L"]}]),
                "destinationwise_taxes_json": json.dumps([{"state_code": "29", "tax_type": "intrastate"}]),
                "backup_settings_json": json.dumps({"freq": "daily"})
            }
            
            saved = save_company_settings(self.company_name, settings_payload)
            self.assertEqual(saved.get("store_trade_name"), "Tattly Outlet")
            self.assertEqual(saved.get("brand_color"), "#ff00ff")
            self.assertEqual(saved.get("invoice_series_prefix"), "TT-INV-")
            self.assertEqual(saved.get("loyalty_enabled"), 1)
            self.assertEqual(saved.get("loyalty_points_per_rupee"), 2.5)

            # Retrieve using convenience getters
            self.assertEqual(get_setting("brand_color", self.company_name), "#ff00ff")
            self.assertEqual(get_setting("store_trade_name", self.company_name), "Tattly Outlet")
            
            size_groups = get_size_groups(self.company_name)
            self.assertEqual(len(size_groups), 1)
            self.assertEqual(size_groups[0]["id"], "test_sizes")
            
            tax_map = get_destinationwise_taxes(self.company_name)
            self.assertEqual(len(tax_map), 1)
            self.assertEqual(tax_map[0]["state_code"], "29")
            
            backup = get_backup_settings(self.company_name)
            self.assertEqual(backup.get("freq"), "daily")

        finally:
            frappe.session.user = orig_user
