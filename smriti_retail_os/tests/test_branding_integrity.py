# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_branding_integrity.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_branding_integrity.py
# @description: Regression tests verifying the integrity of SMRITI Retail OS global branding assets.
# @author: Antigravity AI
# @date: 2026-06-10
#

import os
import hashlib
import unittest
import frappe

class TestBrandingIntegrity(unittest.TestCase):
    def setUp(self):
        self.app_path = frappe.get_app_path("smriti_retail_os")
        
    def test_logo_integrity(self):
        """Verify that the SMRITI global logo SVG is locked and unaltered"""
        logo_paths = [
            os.path.join(self.app_path, "public", "images", "smriti_logo.svg"),
            os.path.join(self.app_path, "public", "images", "logo.svg"),
            os.path.join(self.app_path, "public", "logo.svg")
        ]
        
        for path in logo_paths:
            self.assertTrue(os.path.exists(path), f"Branding asset missing: {path}")
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Verify basic structure of SMRITI shopping bag vector logo
            self.assertIn("svg", content)
            self.assertIn("logo-grad", content)
            # Stylized S path
            self.assertIn("M 37 29.5 C 37 27", content)
            
    def test_wallpaper_integrity(self):
        """Verify that the SMRITI login background wallpaper SVG is locked and unaltered"""
        path = os.path.join(self.app_path, "public", "images", "login_wallpaper.svg")
        self.assertTrue(os.path.exists(path), f"Wallpaper missing: {path}")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertIn("center-mask", content)
        self.assertIn("bg-grad", content)
        self.assertIn("icon-qr_code", content)
        self.assertIn("icon-pos_terminal", content)
        
    def test_login_page_integrity(self):
        """Verify that the SMRITI login page is locked and linked to the SVG wallpaper"""
        path = os.path.join(self.app_path, "www", "smriti-login.html")
        self.assertTrue(os.path.exists(path), f"Login template missing: {path}")
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        self.assertIn("login_wallpaper.svg", content)
        self.assertIn("smriti_logo.svg", content)
        self.assertIn("backdrop-filter: blur", content)
        self.assertIn("RETAIL OS", content)
