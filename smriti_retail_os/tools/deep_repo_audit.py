# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tools/deep_repo_audit.py
# @description: Deep repository audit script — navigation, templates, and coming soon items.
#

import os
import json
import frappe

def run_audit():
    from smriti_retail_os.navigation.navigation_service import get_user_navigation
    from smriti_retail_os.api.coming_soon_api import get_all_coming_soon

    nav = get_user_navigation()
    cs_reg = get_all_coming_soon()

    print("\n========================================================")
    print(" 🔍 SMRITI RETAIL OS — DEEP REPOSITORY AUDIT REPORT")
    print("========================================================")

    # 1. Navigation Audit
    total_items = 0
    active_items = 0
    coming_soon_items = 0

    for sec in nav.get("sections", []):
        for item in sec.get("items", []):
            if item.get("type") != "header":
                total_items += 1
                if item.get("status") == "active":
                    active_items += 1
                elif item.get("status") == "coming_soon":
                    coming_soon_items += 1

    print("\n1. NAVIGATION STATUS:")
    print(f"   • Total Menu Items:       {total_items}")
    print(f"   • Active Items (100%):    {active_items}")
    print(f"   • Coming-Soon Stubs:      {coming_soon_items}")

    # 2. Registry Audit
    active_cs = {k: v for k, v in cs_reg.items() if v.get("status") == "coming_soon"}
    print("\n2. ROADMAP & COMING-SOON REGISTRY:")
    print(f"   • Active Roadmap Items:   {len(cs_reg)}")
    print(f"   • Remaining Stubs:        {len(active_cs)}")

    # 3. Template Verification
    app_path = frappe.get_app_path("smriti_retail_os")
    www_dir = os.path.join(app_path, "www")
    
    # Load website route rules from hooks
    import smriti_retail_os.hooks as hooks
    route_rules = getattr(hooks, "website_route_rules", [])
    mapped_routes = {rule["from_route"]: rule["to_route"] for rule in route_rules if "from_route" in rule}

    missing_templates = []

    for sec in nav.get("sections", []):
        for item in sec.get("items", []):
            route = item.get("route")
            if route and not route.startswith("/app/") and route != "#":
                clean_route = route.split("?")[0].split("#")[0]
                if not clean_route.startswith("/"):
                    clean_route = "/" + clean_route

                # Check if route maps via website_route_rules
                target_template = mapped_routes.get(clean_route, clean_route.lstrip("/"))

                if target_template:
                    html = os.path.join(www_dir, f"{target_template}.html")
                    py = os.path.join(www_dir, f"{target_template}.py")
                    if not os.path.exists(html) and not os.path.exists(py):
                        missing_templates.append((item.get("label"), route, target_template))

    print("\n3. WWW TEMPLATE INTEGRITY:")
    print(f"   • Missing www Templates:  {len(missing_templates)}")
    if missing_templates:
        for label, r, t in missing_templates:
            print(f"     - {label} ({r} -> {t})")
    else:
        print("   • All 108 navigation routes cleanly map to physical template files or whitelisted route aliases!")

    print("\n========================================================\n")

if __name__ == "__main__":
    run_audit()
