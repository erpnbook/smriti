# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_navigation_sync.py
# @description: CI test verifying synchronization between Python and JS navigation configs.
# @author: Antigravity AI Pair Programmer
# @date: 2026-07-01
# @version: 1.8.6
# @license: MIT
#

import os
import json
import subprocess
import unittest
import frappe

class TestNavigationSync(unittest.TestCase):
    def test_navigation_sync(self):
        """Verify that Python CANONICAL_NAV and JS SMRITI_NAV structures remain in sync"""
        # 1. Load CANONICAL_NAV from Python service layer
        from smriti_retail_os.navigation.navigation_service import CANONICAL_NAV

        # 2. Path to the JS config file
        app_path = frappe.get_app_path("smriti_retail_os")
        js_path = os.path.join(app_path, "public", "js", "smriti_nav_config.js")
        self.assertTrue(os.path.exists(js_path), f"JS nav config not found at {js_path}")

        # 3. Use Node to serialize the SMRITI_NAV variable to JSON
        # Replace backslashes for safe path handling inside Node
        safe_js_path = js_path.replace("\\", "/")
        node_code = (
            "const fs = require('fs'); "
            f"const content = fs.readFileSync('{safe_js_path}', 'utf8'); "
            "eval(content + '; console.log(JSON.stringify(SMRITI_NAV));');"
        )
        
        try:
            output = subprocess.check_output(
                ["node", "-e", node_code],
                stderr=subprocess.STDOUT,
                text=True
            )
            js_nav = json.loads(output.strip())
        except subprocess.CalledProcessError as e:
            self.fail(f"Failed to load smriti_nav_config.js via Node:\n{e.output}")
        except json.JSONDecodeError as e:
            self.fail(f"Failed to parse Node JSON output:\n{output}\nError: {e}")

        # 4. Compare structures
        py_sections = {s["id"]: s for s in CANONICAL_NAV.get("sections", [])}
        js_sections = {s["id"]: s for s in js_nav.get("sections", [])}

        # Check section existence
        self.assertEqual(
            set(py_sections.keys()), 
            set(js_sections.keys()), 
            "Navigation sections do not match between Python CANONICAL_NAV and JS SMRITI_NAV"
        )

        for sec_id, py_sec in py_sections.items():
            js_sec = js_sections[sec_id]
            # Compare section attributes
            self.assertEqual(py_sec.get("label"), js_sec.get("label"), f"Section '{sec_id}' label mismatch")
            self.assertEqual(py_sec.get("status"), js_sec.get("status"), f"Section '{sec_id}' status mismatch")

            # Compare items within section
            py_items = {i["id"]: i for i in py_sec.get("items", [])}
            js_items = {i["id"]: i for i in js_sec.get("items", [])}

            self.assertEqual(
                set(py_items.keys()), 
                set(js_items.keys()), 
                f"Items in section '{sec_id}' do not match between Python and JS configs"
            )

            for item_id, py_item in py_items.items():
                js_item = js_items[item_id]
                self.assertEqual(py_item.get("label"), js_item.get("label"), f"Item '{sec_id}.{item_id}' label mismatch")
                self.assertEqual(py_item.get("status"), js_item.get("status"), f"Item '{sec_id}.{item_id}' status mismatch")
                
                # Check routes (if active)
                if py_item.get("status") == "active" and js_item.get("status") == "active":
                    self.assertEqual(py_item.get("route"), js_item.get("route"), f"Item '{sec_id}.{item_id}' route mismatch")
                    self.assertEqual(py_item.get("standalone_route"), js_item.get("standalone_route"), f"Item '{sec_id}.{item_id}' standalone_route mismatch")
