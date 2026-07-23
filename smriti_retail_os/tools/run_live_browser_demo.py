# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tools/run_live_browser_demo.py
# @description: Runs a live Playwright browser session inside Docker container,
#               logs in, interacts with Barcode Studio and Appearance settings,
#               and saves live screenshots into artifacts directory.
#

import os
import time
from playwright.sync_api import sync_playwright

def run_demo():
    print("Starting Playwright live demo session inside container...")
    artifact_dir = "/home/frappe/frappe-bench/apps/smriti_retail_os/public/images"
    os.makedirs(artifact_dir, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=["--no-sandbox", "--disable-setuid-sandbox"])
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # 1. Login
        print("Navigating to http://127.0.0.1:8000/login...")
        page.goto("http://127.0.0.1:8000/login", wait_until="networkidle")

        # Fill credentials if login form present
        if page.locator("#usr").is_visible():
            page.fill("#usr", "Administrator")
        elif page.locator("#email").is_visible():
            page.fill("#email", "Administrator")
        elif page.locator("#login_email").is_visible():
            page.fill("#login_email", "Administrator")

        if page.locator("#pwd").is_visible():
            page.fill("#pwd", "Admin@123")
        elif page.locator("#password").is_visible():
            page.fill("#password", "Admin@123")
        elif page.locator("#login_password").is_visible():
            page.fill("#login_password", "Admin@123")

        login_btn = page.locator("button[type='submit'], #login-btn, .btn-primary")
        if login_btn.is_visible():
            login_btn.first.click()
            page.wait_for_timeout(3000)

        # 2. Barcode Studio
        print("Navigating to http://127.0.0.1:8000/barcode...")
        page.goto("http://127.0.0.1:8000/barcode", wait_until="networkidle")
        page.wait_for_timeout(2000)
        print(f"Current URL: {page.url}")
        print(f"Page Title: {page.title()}")

        # Test switching theme to Light Mode in browser context
        print("Testing theme switching on /barcode...")
        page.evaluate("window.SMRITI = window.SMRITI || window.smriti || {}; if (window.SMRITI.switchTheme) window.SMRITI.switchTheme('hybrid-light');")
        page.wait_for_timeout(1000)

        shot_light_path = "/home/frappe/frappe-bench/apps/smriti_retail_os/public/images/barcode_hybrid_light.png"
        page.screenshot(path=shot_light_path)
        print(f" [OK] Saved hybrid-light screenshot: {shot_light_path}")

        # Test switching theme back to Sleek Compact (Midnight)
        print("Testing SMRITI.switchTheme('sleek-compact') on /barcode...")
        page.evaluate("if (window.SMRITI && window.SMRITI.switchTheme) window.SMRITI.switchTheme('sleek-compact');")
        page.wait_for_timeout(1000)

        shot1_path = "/home/frappe/frappe-bench/apps/smriti_retail_os/public/images/live_barcode_studio.png"
        page.screenshot(path=shot1_path)
        print(f" [OK] Saved sleek-compact screenshot: {shot1_path}")

        # 3. Appearance Control Center
        print("Navigating to http://127.0.0.1:8000/smriti-appearance...")
        page.goto("http://127.0.0.1:8000/smriti-appearance", wait_until="networkidle")
        page.wait_for_timeout(2000)

        shot2_path = "/home/frappe/frappe-bench/apps/smriti_retail_os/public/images/live_smriti_appearance.png"
        page.screenshot(path=shot2_path)
        print(f" [OK] Saved screenshot: {shot2_path}")

        browser.close()
        print("Playwright demo completed successfully!")

if __name__ == "__main__":
    run_demo()
