# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/tests/test_ui_sidebar_regression.py
# @desc:    Automated UI regression assertions for sidebar layout, developer bypass, and permissions.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 2.1.0
# @license: MIT
#

import frappe
import unittest
import os

class TestUISidebarRegression(unittest.TestCase):
    def setUp(self):
        self.app_path = frappe.get_app_path("smriti_retail_os")

    def test_developer_bypass_configuration(self):
        """Assert that SMRITI_DEVELOPER_MODE is correctly injected from frappe.conf."""
        loader_path = os.path.join(self.app_path, "templates", "includes", "smriti_token_loader.html")
        self.assertTrue(os.path.exists(loader_path), "smriti_token_loader.html template is missing")

        with open(loader_path, "r", encoding="utf-8") as f:
            content = f.read()

        # Statically assert that the developer mode injection script block exists
        self.assertIn("window.SMRITI_DEVELOPER_MODE", content)
        self.assertIn("frappe.conf.developer_mode", content)

    def test_sidebar_includes_and_layout(self):
        """Verify purchase_layout.html uses the unified dynamic SMRITI sidebar include."""
        layout_path = os.path.join(self.app_path, "templates", "purchase_layout.html")
        self.assertTrue(os.path.exists(layout_path), "purchase_layout.html template is missing")

        with open(layout_path, "r", encoding="utf-8") as f:
            content = f.read()

        # The hardcoded navigation must be completely gone, replaced by the unified sidebar include
        self.assertIn('{%- include "smriti_retail_os/templates/includes/smriti_sidebar.html" -%}', content)
        self.assertNotIn('<nav id="nav">', content)
        self.assertNotIn('<div id="nav-links">', content)

    def test_sidebar_js_hashchange_and_popout(self):
        """Statically assert that sidebar scripts contain hashchange and popout elements."""
        for js_file in ["smriti_sidebar.js", "smriti_sidebar_standalone.js"]:
            js_path = os.path.join(self.app_path, "public", "js", js_file)
            self.assertTrue(os.path.exists(js_path), f"{js_file} script is missing")

            with open(js_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Confirm hashchange listener exists to refresh highlighting
            self.assertIn("hashchange", content, f"hashchange listener missing in {js_file}")
            
            # Confirm activeRoute includes window.location.hash
            self.assertIn("window.location.hash", content, f"window.location.hash logic missing in {js_file}")
            
            # Confirm popout action buttons are rendered
            self.assertIn("smriti-popout-icon-btn", content, f"smriti-popout-icon-btn rendering missing in {js_file}")
            self.assertIn("smriti-sidebar-item-actions", content, f"smriti-sidebar-item-actions rendering missing in {js_file}")

    def test_sidebar_css_classes(self):
        """Verify CSS contains correct responsive positioning and popout classes."""
        for css_file in ["smriti_sidebar.css", "smriti_sidebar_standalone.css"]:
            css_path = os.path.join(self.app_path, "public", "css", css_file)
            self.assertTrue(os.path.exists(css_path), f"{css_file} stylesheet is missing")

            with open(css_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Assert positioning classes and popout buttons styles exist
            self.assertIn(".smriti-pos-bar", content)
            self.assertIn(".smriti-sidebar-item-actions", content)
            self.assertIn(".smriti-popout-icon-btn", content)

    def test_page_access_registry_policy(self):
        """Verify that security policies require proper role check for restricted SMRITI pages."""
        # Simple import validation
        from smriti_retail_os.security_api import check_page_access
        
        # Test anonymous access failure
        original_user = frappe.session.user
        try:
            frappe.set_user("Guest")
            # Restricted pages like billing-center should deny anonymous access
            with self.assertRaises(frappe.PermissionError):
                check_page_access("billing-center")
        finally:
            frappe.set_user(original_user)
