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
        
    def get_file_hash(self, relative_path):
        full_path = os.path.join(self.app_path, relative_path)
        self.assertTrue(os.path.exists(full_path), f"Asset missing: {relative_path}")
        with open(full_path, "r", encoding="utf-8") as f:
            content = f.read()
        # Normalize line endings to \n to ensure cross-platform hash consistency
        normalized = content.replace("\r\n", "\n").replace("\r", "\n")
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    def test_logo_integrity(self):
        """Verify that the SMRITI global logo SVG is locked and unaltered"""
        expected_hash = "53c5c6bdfb824a580aed8119e2301bc29783a2a5d7bb6dbd2a774027c9d030c5"
        
        logo_paths = [
            "public/images/smriti_logo.svg",
            "public/images/logo.svg",
            "public/logo.svg"
        ]
        
        for rel_path in logo_paths:
            self.assertEqual(self.get_file_hash(rel_path), expected_hash, f"Branding asset altered or compromised: {rel_path}")
            
    def test_wallpaper_integrity(self):
        """Verify that the SMRITI login background wallpaper SVG is locked and unaltered"""
        expected_hash = "782838ff063e3a9f5a8e38dace91b7a0a2230f002b8b8c928c6b8f6ba87bf49a"
        self.assertEqual(self.get_file_hash("public/images/login_wallpaper.svg"), expected_hash, "Wallpaper asset altered or compromised")
        
    def test_login_page_integrity(self):
        """Verify that the SMRITI login page template is locked and unaltered"""
        expected_hash = "8aac6091f698573d3dae519fdf5557279c59e784531afc615545bcd866a0176b"
        self.assertEqual(self.get_file_hash("www/smriti-login.html"), expected_hash, "Login template altered or compromised")

    def test_error_pages_integrity(self):
        """Verify that SMRITI custom error page templates are locked and unaltered"""
        expected_404 = "d04c14f1947bacdd34388517aab29a605f23f0a967ac5f5bb1742e8638442add"
        expected_smriti_404 = "5333a7967c1636b90c4bab2768e2a9860c7b686f58f8ef7f3088beeb966abd80"
        
        expected_403 = "57c8d3c11d897f9bfd607ffb09957b7f9cf54cd36aaa346bcd5d831c540c4653"
        expected_smriti_403 = "a81ff41d00d871b7f9e4c42b2950acfe608a2c184c7de1eba042ad849d7ab105"
        
        self.assertEqual(self.get_file_hash("www/404.html"), expected_404, "404 HTML template altered or compromised")
        self.assertEqual(self.get_file_hash("www/smriti-404.html"), expected_smriti_404, "smriti-404 HTML template altered or compromised")
        
        self.assertEqual(self.get_file_hash("www/403.html"), expected_403, "403 HTML template altered or compromised")
        self.assertEqual(self.get_file_hash("www/smriti-403.html"), expected_smriti_403, "smriti-403 HTML template altered or compromised")

    def test_routing_rules_integrity(self):
        """Verify that SMRITI hooks.py contains all critical brand redirect routes"""
        hooks_path = os.path.join(self.app_path, "hooks.py")
        self.assertTrue(os.path.exists(hooks_path))
        with open(hooks_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        normalized_content = content.replace("'", '"').replace(" ", "").replace("\n", "").replace("\r", "").replace("\t", "")
        self.assertIn('{"from_route":"/404","to_route":"smriti-404"}', normalized_content)
        self.assertIn('{"from_route":"/403","to_route":"smriti-403"}', normalized_content)
        self.assertIn('{"from_route":"/login","to_route":"smriti-login"}', normalized_content)
