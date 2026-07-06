# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_branding_integrity.py
# @description: Branding integrity tests — SMRITI UI consistency checks.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
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
        expected_hashes = {
            "public/images/smriti_logo.svg": "95cd6bee993beb532f27cca5556123fe4fd0104ca4f8aa3284f1ccf8a1bab0a2",
            "public/images/logo.svg": "9a06a98016c515f5fc8c488f6393c810f6793f1714f236a6f927c6ddf9079666",
            "public/logo.svg": "9a06a98016c515f5fc8c488f6393c810f6793f1714f236a6f927c6ddf9079666",
        }

        for rel_path, expected_hash in expected_hashes.items():
            self.assertEqual(
                self.get_file_hash(rel_path),
                expected_hash,
                f"Branding asset altered or compromised: {rel_path}",
            )

    def test_wallpaper_integrity(self):
        """Verify that the SMRITI login background wallpaper SVG is locked and unaltered"""
        expected_hash = (
            "782838ff063e3a9f5a8e38dace91b7a0a2230f002b8b8c928c6b8f6ba87bf49a"
        )
        self.assertEqual(
            self.get_file_hash("public/images/login_wallpaper.svg"),
            expected_hash,
            "Wallpaper asset altered or compromised",
        )

    def test_login_page_integrity(self):
        """Verify that the SMRITI login page template is locked and unaltered"""
        expected_hash = (
            "77246de97da926e61c18a5a90de270a3c692d5a0db31924afe22bf14e29380ec"
        )
        self.assertEqual(
            self.get_file_hash("www/smriti-login.html"),
            expected_hash,
            "Login template altered or compromised",
        )

    def test_error_pages_integrity(self):
        """Verify that SMRITI custom error page templates are locked and unaltered"""
        expected_404 = (
            "d90c3fddc69a225c2cb429004d41dfa5bcd4d81d7aa5df8c6d2ab6de8027a071"
        )
        expected_smriti_404 = (
            "d62346a25bd3e8f9cf2a79b224df185b1f56426007dc474a6d5b4e10fa1a043e"
        )

        expected_403 = (
            "5c852babf55c88fea48eb40bdaf214f89aaf659280efb5046ee9cf2714cd08d2"
        )
        expected_smriti_403 = (
            "8b7ab25917c9d02a64298635016c898bebc599d6533da021a0014694b60bd313"
        )

        self.assertEqual(
            self.get_file_hash("www/404.html"),
            expected_404,
            "404 HTML template altered or compromised",
        )
        self.assertEqual(
            self.get_file_hash("www/smriti-404.html"),
            expected_smriti_404,
            "smriti-404 HTML template altered or compromised",
        )

        self.assertEqual(
            self.get_file_hash("www/403.html"),
            expected_403,
            "403 HTML template altered or compromised",
        )
        self.assertEqual(
            self.get_file_hash("www/smriti-403.html"),
            expected_smriti_403,
            "smriti-403 HTML template altered or compromised",
        )

    def test_routing_rules_integrity(self):
        """Verify that SMRITI hooks.py contains all critical brand redirect routes"""
        hooks_path = os.path.join(self.app_path, "hooks.py")
        self.assertTrue(os.path.exists(hooks_path))
        with open(hooks_path, "r", encoding="utf-8") as f:
            content = f.read()

        normalized_content = (
            content.replace("'", '"')
            .replace(" ", "")
            .replace("\n", "")
            .replace("\r", "")
            .replace("\t", "")
        )
        self.assertIn(
            '{"from_route":"/404","to_route":"smriti-404"}', normalized_content
        )
        self.assertIn(
            '{"from_route":"/403","to_route":"smriti-403"}', normalized_content
        )
        self.assertIn(
            '{"from_route":"/login","to_route":"smriti-login"}', normalized_content
        )

    def test_raw_templates_no_js_comments(self):
        """Verify that raw HTML templates do not contain JS-style comments /** ... */ outside script/style tags"""
        import glob
        import re

        www_path = os.path.join(self.app_path, "www")
        templates_path = os.path.join(self.app_path, "templates")

        html_files = []
        for path in [www_path, templates_path]:
            if os.path.exists(path):
                html_files.extend(
                    glob.glob(os.path.join(path, "**", "*.html"), recursive=True)
                )

        for filepath in html_files:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Strip style and script blocks from raw template
            stripped = re.sub(r"<script.*?>.*?</script>", "", content, flags=re.DOTALL)
            stripped = re.sub(r"<style.*?>.*?</style>", "", stripped, flags=re.DOTALL)
            # Skip Jinja comments
            stripped = re.sub(r"{#.*?#}", "", stripped, flags=re.DOTALL)

            # Check if /** is in the remaining template content (outside script/style tags)
            if "/**" in stripped:
                idx = stripped.find("/**")
                snippet = stripped[max(0, idx - 50) : min(len(stripped), idx + 100)]
                self.fail(
                    f"JS-style block comment '/**' found outside script/style block in raw template '{os.path.basename(filepath)}'.\n"
                    f"Snippet: ... {snippet.strip()} ..."
                )

            # Check if metadata or block comments leak outside HTML comments
            stripped_all = re.sub(r"<!--.*?-->", "", stripped, flags=re.DOTALL)
            leak_markers = ["@file:", "@author:", "@license:", "Copyright", "/**"]
            for marker in leak_markers:
                if marker in stripped_all:
                    idx = stripped_all.find(marker)
                    snippet = stripped_all[
                        max(0, idx - 50) : min(len(stripped_all), idx + 100)
                    ]
                    self.fail(
                        f"Metadata marker '{marker}' found outside HTML/Jinja comment in raw template '{os.path.basename(filepath)}'.\n"
                        f"Snippet: ... {snippet.strip()} ..."
                    )

    def test_rendered_pages_no_leaked_comments(self):
        """Verify that rendered HTML pages do not leak comment blocks, metadata tags, or debugging artifacts"""
        import re
        import werkzeug.test
        from werkzeug.wrappers import Request
        from frappe.website.serve import get_response_content

        routes = [
            "/cge_generic",
            "/smriti-cge",
            "/smriti-dictionary",
            "/smriti-formula-registry",
            "/smriti-pdt",
            "/smriti-presentation",
        ]

        leak_markers = ["@file:", "@author:", "@license:", "Copyright", "/**"]

        regex_markers = {
            "TODO": r"\bTODO\b",
            "FIXME": r"\bFIXME\b",
            "DEBUG": r"\b(DEBUG_MARKER|TEMP_TESTING|DEBUG)\b",
            "console.log": r"\bconsole\.log\s*\(",
            "alert": r"\balert\s*\(",
        }

        # Save original session and request state
        orig_request = getattr(frappe.local, "request", None)
        orig_user = frappe.session.user

        try:
            frappe.set_user("Administrator")
            for route in routes:
                # Mock a request environment to bypass redirection/authentication checks and werkzeug request issues
                environ = werkzeug.test.EnvironBuilder(path=route).get_environ()
                frappe.local.request = Request(environ)

                try:
                    html = get_response_content(route)
                except Exception as e:
                    self.fail(f"Failed to render route {route}: {e}")

                # Strip HTML comments, script tags, style tags
                cleaned_html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
                cleaned_html = re.sub(
                    r"<script.*?>.*?</script>", "", cleaned_html, flags=re.DOTALL
                )
                cleaned_html = re.sub(
                    r"<style.*?>.*?</style>", "", cleaned_html, flags=re.DOTALL
                )

                # Check if any literal leak markers are present in the clean body/content
                for marker in leak_markers:
                    if marker in cleaned_html:
                        idx = cleaned_html.find(marker)
                        snippet = cleaned_html[
                            max(0, idx - 50) : min(len(cleaned_html), idx + 100)
                        ]
                        self.fail(
                            f"Leaked source comment/debugging marker '{marker}' found in rendered page for route '{route}'.\n"
                            f"Snippet: ... {snippet.strip()} ..."
                        )

                # Check if any regex debugging markers are present
                for label, pattern in regex_markers.items():
                    match = re.search(
                        pattern,
                        cleaned_html,
                        re.IGNORECASE if label in ["TODO", "FIXME", "DEBUG"] else 0,
                    )
                    if match:
                        idx = match.start()
                        snippet = cleaned_html[
                            max(0, idx - 50) : min(len(cleaned_html), idx + 100)
                        ]
                        self.fail(
                            f"Leaked debugging artifact '{label}' found in rendered page for route '{route}'.\n"
                            f"Snippet: ... {snippet.strip()} ..."
                        )
        finally:
            # Restore original session and request state
            frappe.set_user(orig_user)
            if orig_request:
                frappe.local.request = orig_request
            elif hasattr(frappe.local, "request"):
                delattr(frappe.local, "request")

    def test_no_debug_artifacts_in_templates(self):
        """Scan all raw HTML templates for debug artifacts (TODO, FIXME, DEBUG, console.log, alert) outside script/style blocks and valid comments"""
        import glob
        import re

        www_path = os.path.join(self.app_path, "www")
        templates_path = os.path.join(self.app_path, "templates")

        html_files = []
        for path in [www_path, templates_path]:
            if os.path.exists(path):
                html_files.extend(
                    glob.glob(os.path.join(path, "**", "*.html"), recursive=True)
                )

        for filepath in html_files:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            # Strip style and script blocks from raw template
            stripped = re.sub(r"<script.*?>.*?</script>", "", content, flags=re.DOTALL)
            stripped = re.sub(r"<style.*?>.*?</style>", "", stripped, flags=re.DOTALL)
            # Skip Jinja comments
            stripped = re.sub(r"{#.*?#}", "", stripped, flags=re.DOTALL)
            # Skip HTML comments
            stripped = re.sub(r"<!--.*?-->", "", stripped, flags=re.DOTALL)

            # Check for TODO/FIXME in the entire file
            todo_matches = re.findall(r"\b(TODO|FIXME)\b", content, re.IGNORECASE)
            if todo_matches:
                self.fail(
                    f"Unresolved TODO/FIXME markers found in template '{os.path.basename(filepath)}': {set(todo_matches)}"
                )

            # Check for DEBUG outside script/style/comments
            debug_matches = re.findall(
                r"\b(DEBUG_MARKER|TEMP_TESTING|DEBUG)\b", stripped, re.IGNORECASE
            )
            if debug_matches:
                self.fail(
                    f"Unresolved DEBUG/TESTING markers found outside script/style/comments in template '{os.path.basename(filepath)}': {set(debug_matches)}"
                )

            # Check for console.log / alert outside script/style/comments
            for statement in ["console.log", "alert"]:
                if statement == "alert":
                    match = re.search(r"\balert\s*\(", stripped.lower())
                    if not match:
                        continue
                    idx = match.start()
                else:
                    if statement not in stripped.lower():
                        continue
                    idx = stripped.lower().find(statement)

                snippet = stripped[max(0, idx - 50) : min(len(stripped), idx + 100)]
                self.fail(
                    f"'{statement}' statement found outside script block in template '{os.path.basename(filepath)}'.\n"
                    f"Snippet: ... {snippet.strip()} ..."
                )
