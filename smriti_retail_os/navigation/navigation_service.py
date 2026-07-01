# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/navigation/navigation_service.py
# @description: SMRITI Navigation Manager (SNM) Resolver & Cache Engine.
# @author: Jawahar R. Mallah
#

import frappe
import json
import hashlib
import os

CANONICAL_NAV = {
    "sections": [
        {
            "id": "masters",
            "label": "Masters",
            "status": "active",
            "items": [
                { "id": "product_catalog", "label": "Product Catalog", "route": "/products", "standalone_route": "/products", "status": "active" },
                { "id": "brand_master", "label": "Brand Master", "route": "/brand-master", "standalone_route": "/brand-master", "status": "active" },
                { "id": "item_master", "label": "Item Master", "route": "/item-master", "standalone_route": "/item-master", "status": "active" },
                { "id": "category_master", "label": "Category Master", "route": "/category-master", "standalone_route": "/category-master", "status": "active" },
                { "id": "scheme_creator", "label": "Scheme Creator", "route": "/scheme-creator", "standalone_route": "/scheme-creator", "status": "active" },
                { "id": "cge_studio", "label": "CGE Studio", "route": "/smriti-cge", "standalone_route": "/smriti-cge", "status": "hidden" },
                { "id": "customers", "label": "Customers", "route": "/customers", "standalone_route": "/customers", "status": "active" },
                { "id": "suppliers", "label": "Suppliers", "route": "/suppliers", "standalone_route": "/suppliers", "status": "active" }
            ]
        },
        {
            "id": "cge",
            "label": "CGE",
            "status": "active",
            "items": [
                { "id": "cge_dashboard", "label": "Dashboard", "route": "/smriti-cge", "standalone_route": "/smriti-cge", "status": "active" },
                { "id": "cge_setup_hdr", "label": "Setup", "type": "header" },
                { "id": "cge_benefit_instruments", "label": "Benefit Instruments", "route": "/cge-benefit-instruments", "standalone_route": "/cge-benefit-instruments", "status": "active" },
                { "id": "cge_membership_tiers", "label": "Membership Tiers", "route": "/cge-membership-tiers", "standalone_route": "/cge-membership-tiers", "status": "active" },
                { "id": "cge_loyalty_programs", "label": "Loyalty Programs", "route": "/cge-loyalty-programs", "standalone_route": "/cge-loyalty-programs", "status": "active" },
                { "id": "cge_marketing_hdr", "label": "Marketing", "type": "header" },
                { "id": "cge_campaigns", "label": "Campaigns", "route": "/cge-campaigns", "standalone_route": "/cge-campaigns", "status": "active" },
                { "id": "cge_promotion_rules", "label": "Promotion Rules", "route": "/cge-promotion-rules", "standalone_route": "/cge-promotion-rules", "status": "active" },
                { "id": "cge_coupon_rules", "label": "Coupon Rules", "route": "/cge-coupon-rules", "standalone_route": "/cge-coupon-rules", "status": "active" },
                { "id": "cge_loyalty_rules", "label": "Loyalty Rules", "route": "/cge-loyalty-rules", "standalone_route": "/cge-loyalty-rules", "status": "active" },
                { "id": "cge_operations_hdr", "label": "Operations", "type": "header" },
                { "id": "cge_benefit_wallets", "label": "Benefit Wallets", "route": "/cge-benefit-wallets", "standalone_route": "/cge-benefit-wallets", "status": "active" },
                { "id": "cge_customer_benefit_profiles", "label": "Customer Benefit Profiles", "route": "/cge-customer-benefit-profiles", "standalone_route": "/cge-customer-benefit-profiles", "status": "active" },
                { "id": "cge_governance_hdr", "label": "Governance", "type": "header" },
                { "id": "cge_benefit_resolution_policies", "label": "Resolution Policies", "route": "/cge-benefit-resolution-policies", "standalone_route": "/cge-benefit-resolution-policies", "status": "active" },
                { "id": "cge_liability_snapshots", "label": "Liability Snapshots", "route": "/cge-liability-snapshots", "standalone_route": "/cge-liability-snapshots", "status": "active" },
                { "id": "cge_benefit_audit_logs", "label": "Audit Logs", "route": "/cge-benefit-audit-logs", "standalone_route": "/cge-benefit-audit-logs", "status": "active" }
            ]
        },
        {
            "id": "psv",
            "label": "PSV",
            "status": "active",
            "items": [
                { "id": "distributor_accounts", "label": "Distributor Accounts", "route": "/psv-channel-partner", "standalone_route": "/psv-channel-partner", "status": "active" },
                { "id": "sales_uploads", "label": "Sales Uploads", "route": "/sales-upload", "standalone_route": "/sales-upload", "status": "active" },
                { "id": "stock_uploads", "label": "Stock Uploads", "route": "/stock-audit", "standalone_route": "/stock-audit", "status": "active" },
                { "id": "reconciliation", "label": "Reconciliation", "route": "/psv-reconciliation", "standalone_route": "/psv-reconciliation", "status": "active" },
                { "id": "psv_dashboard", "label": "Dashboard", "route": "/psv-dashboard", "standalone_route": "/psv-dashboard", "status": "active" },
                { "id": "stock_aging", "label": "Stock Aging", "route": "/psv-aging", "standalone_route": "/psv-aging", "status": "active" },
                { "id": "exception_analysis", "label": "Exception Analysis", "route": "/psv-exception-analysis", "standalone_route": "/psv-exception-analysis", "status": "active" },
                { "id": "psv_opening_balance", "label": "PSV Opening Balance", "route": "/psv-opening-balance", "standalone_route": "/psv-opening-balance", "status": "active" }
            ]
        },
        {
            "id": "sales",
            "label": "Sales",
            "status": "active",
            "items": [
                { "id": "pos_billing", "label": "POS Billing", "route": "/billing", "standalone_route": "/billing", "status": "active" },
                { "id": "clienteling", "label": "Clienteling Studio", "route": "/smriti-clienteling", "standalone_route": "/smriti-clienteling", "status": "active" },
                { "id": "sales_orders", "label": "Sales Orders", "route": "/sales-orders", "standalone_route": "/sales-orders", "status": "active" },
                { "id": "tax_invoice", "label": "Tax Invoice", "route": "/sales-invoices", "standalone_route": "/sales-invoices", "status": "active" },
                { "id": "sales_return", "label": "Sales Return", "route": "/sales-returns", "standalone_route": "/sales-returns", "status": "active" },
                { "id": "delivery_challan", "label": "Delivery Challan", "route": "/delivery-challans", "standalone_route": "/delivery-challans", "status": "active" },
                { "id": "credit_notes", "label": "Credit Notes", "route": "/sales-invoices", "standalone_route": "/sales-invoices", "status": "active" },
                { "id": "eway_bill", "label": "E-Way Bill Management", "route": "/eway_bill", "standalone_route": "/eway_bill", "status": "active" }
            ]
        },
        {
            "id": "purchase",
            "label": "Purchase",
            "status": "active",
            "items": [
                { "id": "purchase_orders", "label": "Purchase Orders", "route": "/purchase?tab=new-po", "standalone_route": "/purchase?tab=new-po", "status": "active" },
                { "id": "grn_receipts", "label": "GRN / Receipts", "route": "/grn-receipts", "standalone_route": "/grn-receipts", "status": "active" },
                { "id": "purchase_invoice", "label": "Purchase Invoice", "route": "/purchase-invoices", "standalone_route": "/purchase-invoices", "status": "active" },
                { "id": "supplier_returns", "label": "Supplier Returns", "route": "/supplier-returns", "standalone_route": "/supplier-returns", "status": "active" }
            ]
        },
        {
            "id": "inventory",
            "label": "Inventory",
            "status": "active",
            "items": [
                { "id": "warehouses", "label": "Warehouses", "route": "/inventory?tab=warehouses", "standalone_route": "/inventory?tab=warehouses", "status": "active" },
                { "id": "opening_stock", "label": "Opening Stock", "route": "/opening-stock", "standalone_route": "/opening-stock", "status": "active" },
                { "id": "stock_operations", "label": "Stock Operations", "route": "/inventory-ops", "standalone_route": "/inventory-ops", "status": "active" },
                { "id": "stock_transfer", "label": "Stock Transfer", "route": "/inventory?tab=transfer", "standalone_route": "/inventory?tab=transfer", "status": "active" },
                { "id": "stock_adjustments", "label": "Stock Adjustments", "route": "/inventory?tab=adjustments", "standalone_route": "/inventory?tab=adjustments", "status": "active" },
                { "id": "stock_audit", "label": "Stock Audit", "route": "/stock-audit", "standalone_route": "/stock-audit", "status": "active" }
            ]
        },
        {
            "id": "barcode_studio",
            "label": "Barcode Studio",
            "status": "active",
            "items": [
                { "id": "label_studio", "label": "Label Studio", "route": "/barcode", "standalone_route": "/barcode", "status": "active" },
                { "id": "print_templates", "label": "Print Templates", "route": "/print-templates", "standalone_route": "/print-templates", "status": "active" },
                { "id": "sizewise_item", "label": "Sizewise Item CRUD", "route": "/sizewise_item", "standalone_route": "/sizewise_item", "status": "active" },
                { "id": "sizewise_invoice", "label": "Sizewise Invoice", "route": "/sizewise_invoice", "standalone_route": "/sizewise_invoice", "status": "active" }
            ]
        },
        {
            "id": "finance",
            "label": "Finance",
            "status": "active",
            "items": [
                { "id": "receipts", "label": "Receipts", "route": "/receipts", "standalone_route": "/receipts", "status": "active" },
                { "id": "payments", "label": "Payments", "route": "/payments", "standalone_route": "/payments", "status": "active" },
                { "id": "advances", "label": "Advances", "route": "/advances", "standalone_route": "/advances", "status": "active" },
                { "id": "uie_integration", "label": "Integration Center", "route": "/smriti-uie", "standalone_route": "/smriti-uie", "status": "active" }
            ]
        },
        {
            "id": "reports",
            "label": "Reports",
            "status": "active",
            "items": [
                { "id": "sales_reports", "label": "Sales Reports", "route": "/reports/sales", "standalone_route": "/reports/sales", "status": "active" },
                { "id": "inventory_reports", "label": "Inventory Reports", "route": "/reports/inventory", "standalone_route": "/reports/inventory", "status": "active" },
                { "id": "finance_reports", "label": "Finance Reports", "route": "/reports/finance", "standalone_route": "/reports/finance", "status": "active" },
                { "id": "gst_reports", "label": "GST Reports", "route": "/reports/gst", "standalone_route": "/reports/gst", "status": "active" },
                { "id": "psv_reports", "label": "PSV Reports", "route": "/reports/psv", "standalone_route": "/reports/psv", "status": "active" },
                { "id": "billing_metrics", "label": "Billing Metrics", "route": "/billing-metrics", "standalone_route": "/billing-metrics", "status": "active" },
                { "id": "audit_reports", "label": "Audit Reports", "route": "/reports?report=security_audit_log", "standalone_route": "/reports?report=security_audit_log", "status": "active" },
                { "id": "analytics_dashboard", "label": "Analytics Dashboard", "route": "/analytics", "standalone_route": "/analytics", "status": "active" }
            ]
        },
        {
            "id": "administration",
            "label": "Administration",
            "status": "active",
            "items": [
                { "id": "day_open", "label": "Day Open", "route": "/shift", "standalone_route": "/shift", "status": "active" },
                { "id": "day_close", "label": "Day Close", "route": "/shift", "standalone_route": "/shift", "status": "active" },
                { "id": "shift_register", "label": "Shift / Register", "route": "/shift", "standalone_route": "/shift", "status": "active" },
                { "id": "user_management", "label": "User Management", "route": "/security-workflows?tab=users", "standalone_route": "/security-workflows?tab=users", "status": "active" },
                { "id": "roles_permissions", "label": "Roles & Permissions", "route": "/security-workflows?tab=roles", "standalone_route": "/security-workflows?tab=roles", "status": "active" },
                { "id": "config_portal", "label": "Config Portal", "route": "/config-portal", "standalone_route": "/config-portal", "status": "active" },
                { "id": "security_workflows", "label": "Security & Workflows", "route": "/security-workflows", "standalone_route": "/security-workflows", "status": "active" },
                { "id": "audit_logs", "label": "Audit Logs", "route": "/smriti-security-log", "standalone_route": "/smriti-security-log", "status": "active" },
                { "id": "smriti_license", "label": "License & Registration", "route": "/smriti-license", "standalone_route": "/smriti-license", "status": "active" },
                { "id": "backup_restore", "label": "Backup & Restore", "route": "/backup", "standalone_route": "/backup", "status": "active" },
                { "id": "platform_center", "label": "Platform Center", "route": "/platform_center", "standalone_route": "/platform_center", "status": "active" },
                { "id": "pos_profiles", "label": "POS Profiles", "route": "/smriti-pos-profiles", "standalone_route": "/smriti-pos-profiles", "status": "active" }
            ]
        },
        {
            "id": "help_desk",
            "label": "Help Desk",
            "status": "active",
            "items": [
                { "id": "knowledge_studio", "label": "Knowledge Studio", "route": "/smriti-knowledge-studio", "standalone_route": "/smriti-knowledge-studio", "status": "active" },
                { "id": "knowledge_center", "label": "Knowledge Center", "route": "/smriti-help", "standalone_route": "/smriti-help", "status": "active" },
                { "id": "formula_registry", "label": "Formula Registry", "route": "/smriti-formula-registry", "standalone_route": "/smriti-formula-registry", "status": "active" },
                { "id": "business_dictionary", "label": "Business Dictionary", "route": "/smriti-dictionary", "standalone_route": "/smriti-dictionary", "status": "active" },
                { "id": "user_manual", "label": "User Manual", "route": "/smriti-help", "standalone_route": "/smriti-help", "status": "active" },
                { "id": "release_notes", "label": "Release Notes", "route": "/release-notes", "standalone_route": "/release-notes", "status": "active" },
                { "id": "support", "label": "Support", "route": "/support", "standalone_route": "/support", "status": "active" }
            ]
        },
        {
            "id": "ai_hub",
            "label": "AI Hub",
            "status": "active",
            "items": [
                { "id": "pdt_dashboard", "label": "PDT Dashboard", "route": "/smriti-pdt", "standalone_route": "/smriti-pdt", "status": "active" },
                { "id": "simulation_sandbox", "label": "Simulation Sandbox", "route": "/coming-soon", "standalone_route": "/coming-soon", "status": "coming_soon", "progress": 60, "eta": "Q3 2026" },
                { "id": "demand_forecasts", "label": "Demand Forecasts", "status": "hidden" },
                { "id": "cashier_performance", "label": "Cashier Performance", "status": "hidden" }
            ]
        },
        {
            "id": "commercial",
            "label": "Commercial",
            "status": "active",
            "items": [
                { "id": "smriti_pricing", "label": "Pricing Plans", "route": "/smriti-pricing", "standalone_route": "/smriti-pricing", "status": "active" },
                { "id": "roi_calculator", "label": "ROI Calculator", "route": "/smriti-roi-calculator", "standalone_route": "/smriti-roi-calculator", "status": "active" },
                { "id": "trial_signup", "label": "Start Free Trial", "route": "/smriti-trial", "standalone_route": "/smriti-trial", "status": "active" },
                { "id": "trial_leads", "label": "Trial Leads CRM", "route": "/smriti-trial-leads", "standalone_route": "/smriti-trial-leads", "status": "active" }
            ]
        }
    ]
}

@frappe.whitelist()
def get_user_navigation(user=None):
    """
    Computes user specific navigation structure with override priority and redis caching.
    """
    if not user:
        user = frappe.session.user
    active_company = frappe.defaults.get_user_default("Company") or ""
    
    # 1. Resolve cache keys
    cache_hash = _get_navigation_version_hash(user, active_company)
    cache_key = f"smriti:navigation:{user}:{active_company}:{cache_hash}"
    
    cached_val = frappe.cache().get_value(cache_key)
    if cached_val:
        return json.loads(cached_val)
        
    # 2. Compute navigation tree
    resolved_nav = _resolve_navigation_tree(user, active_company)
    
    # Add versioning metadata
    resolved_nav["cache_hash"] = cache_hash
    resolved_nav["generated_time"] = frappe.utils.now()
    resolved_nav["navigation_version"] = "2.0.0"
    resolved_nav["schema_version"] = "1.0.0"
    
    # 3. Save to cache
    frappe.cache().set_value(cache_key, json.dumps(resolved_nav), expires_in_sec=86400)
    return resolved_nav

def invalidate_navigation_cache(user=None, company=None):
    """
    Invalidates navigation cache patterns.
    """
    # Simple invalidation strategy: delete keys matching smriti:navigation:*
    # In Redis context, we can delete keys or clear user specific entries
    if user and company:
        cache_hash = _get_navigation_version_hash(user, company)
        frappe.cache().delete_value(f"smriti:navigation:{user}:{company}:{cache_hash}")
    else:
        # Clear all
        keys = frappe.cache().get_keys("smriti:navigation:*")
        for k in keys:
            frappe.cache().delete_value(k)

def _get_navigation_version_hash(user, company):
    """
    Generates a version hash from SMRITI Navigation Profile and Override states.
    """
    last_mod = frappe.db.get_value("SMRITI Navigation Profile", {}, "modified", order_by="modified desc") or "default"
    last_override_mod = frappe.db.get_value("SMRITI Navigation Override", {}, "modified", order_by="modified desc") or "default"
    last_assignment_mod = frappe.db.get_value("SMRITI Navigation Assignment", {}, "modified", order_by="modified desc") or "default"
    
    combined = f"{last_mod}:{last_override_mod}:{last_assignment_mod}"
    return hashlib.md5(combined.encode("utf-8")).hexdigest()


def _resolve_navigation_tree(user, company):
    """
    Resolves permissions, assignments, and structural overrides on top of canonical config.
    """
    # Fallback immediately if SMRITI Navigation Profile is empty
    if not frappe.db.count("SMRITI Navigation Profile"):
        return CANONICAL_NAV

    # Find highest priority assignment
    user_roles = frappe.get_roles(user)
    assignments = frappe.get_all(
        "SMRITI Navigation Assignment",
        filters=[
            ["docstatus", "=", 0]
        ],
        fields=["assignment_type", "assign_to", "navigation_profile", "priority"]
    )
    
    resolved_profile = None
    max_priority = -1
    
    for ass in assignments:
        matched = False
        if ass.assignment_type == "User" and ass.assign_to == user:
            matched = True
        elif ass.assignment_type == "Role" and ass.assign_to in user_roles:
            matched = True
        elif ass.assignment_type == "Company" and ass.assign_to == company:
            matched = True
        elif ass.assignment_type == "Global":
            matched = True
            
        if matched and ass.priority > max_priority:
            max_priority = ass.priority
            resolved_profile = ass.navigation_profile
            
    if not resolved_profile:
        return CANONICAL_NAV
        
    # Load profile details
    profile_doc = frappe.get_doc("SMRITI Navigation Profile", resolved_profile)
    
    # Load overrides
    overrides = frappe.get_all(
        "SMRITI Navigation Override",
        filters={"navigation_profile": resolved_profile},
        fields=["name", "menu_id", "override_state", "label_override", "icon_override", "display_order", "feature_flag", "badge", "tooltip"]
    )
    
    override_map = {ov.menu_id: ov for ov in overrides}
    
    # Clone canonical navigation dict
    resolved = json.loads(json.dumps(CANONICAL_NAV))
    
    # Process and merge overrides
    new_sections = []
    for section in resolved.get("sections", []):
        sec_id = section.get("id")
        
        # Merge section level override
        if sec_id in override_map:
            sec_ov = override_map[sec_id]
            if sec_ov.override_state == "Disabled":
                continue
            if sec_ov.override_state == "Override":
                if sec_ov.label_override: section["label"] = sec_ov.label_override
                if sec_ov.display_order is not None: section["display_order"] = sec_ov.display_order
                if sec_ov.feature_flag: section["feature_flag"] = sec_ov.feature_flag
                
        new_items = []
        for item in section.get("items", []):
            item_id = item.get("id")
            
            # Check override status
            if item_id in override_map:
                item_ov = override_map[item_id]
                if item_ov.override_state == "Disabled":
                    continue
                if item_ov.override_state == "Override":
                    if item_ov.label_override: item["label"] = item_ov.label_override
                    if item_ov.icon_override: item["icon"] = item_ov.icon_override
                    if item_ov.display_order is not None: item["display_order"] = item_ov.display_order
                    if item_ov.feature_flag: item["feature_flag"] = item_ov.feature_flag
                    if item_ov.badge: item["badge"] = item_ov.badge
                    if item_ov.tooltip: item["tooltip"] = item_ov.tooltip
                    
            new_items.append(item)
            
        # Re-sort items if custom display_order weights exist
        new_items.sort(key=lambda x: x.get("display_order", 0))
        section["items"] = new_items
        new_sections.append(section)
        
    # Re-sort sections
    new_sections.sort(key=lambda x: x.get("display_order", 0))
    resolved["sections"] = new_sections
    
    return resolved


def generate_upgrade_merge_report():
    """
    Compares the canonical configuration with custom database overrides and flags deprecated/new IDs.
    """
    canonical_ids = set()
    for section in CANONICAL_NAV.get("sections", []):
        canonical_ids.add(section["id"])
        for item in section.get("items", []):
            canonical_ids.add(item["id"])
            
    # Find all overridden menu IDs
    overridden_ids = frappe.get_all("SMRITI Navigation Override", fields=["menu_id", "navigation_profile"])
    
    merge_report = {
        "new_menus": [],
        "deprecated_menus": [],
        "conflicts": []
    }
    
    for ov in overridden_ids:
        if ov.menu_id not in canonical_ids:
            merge_report["deprecated_menus"].append(ov.menu_id)
            merge_report["conflicts"].append({
                "menu_id": ov.menu_id,
                "profile": ov.navigation_profile,
                "reason": "Referenced Menu ID is missing or deprecated in canonical configuration."
            })
            
    return merge_report


@frappe.whitelist()
def run_navigation_health_check():
    """
    Executes the modular SMRITI Navigation Validator Engine.
    Compiles structured diagnostics across all registered validation rules.
    """
    # Import registry to load the rules dynamically
    from smriti_retail_os.navigation.validator import VALIDATOR_REGISTRY
    
    warnings = []
    for validator in VALIDATOR_REGISTRY:
        try:
            rule_warnings = validator.validate(CANONICAL_NAV)
            if rule_warnings:
                warnings.extend(rule_warnings)
        except Exception as e:
            warnings.append({
                "rule_id": validator.rule_id,
                "severity": "CRITICAL",
                "module": "Validator Engine",
                "menu": validator.title,
                "route": "",
                "source": "navigation_service.py",
                "file": "navigation_service.py",
                "line": 0,
                "recommendation": f"Validation execution failure: {str(e)}",
                "auto_fix": False
            })
            
    # Track historical snapshot in a JSON log file under public/files for trend tracking
    log_health_snapshot(warnings)
    
    return {
        "status": "Healthy" if not warnings else "Warnings",
        "total_warnings": len(warnings),
        "diagnostics": warnings
    }

def log_health_snapshot(warnings):
    """
    Appends a new diagnostic health snapshot to files/smriti_nav_health_history.json.
    """
    log_dir = frappe.get_site_path("public", "files")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
        
    log_file = os.path.join(log_dir, "smriti_nav_health_history.json")
    
    # Calculate counts by severity
    critical_count = sum(1 for w in warnings if w["severity"] == "CRITICAL")
    high_count = sum(1 for w in warnings if w["severity"] == "HIGH")
    medium_count = sum(1 for w in warnings if w["severity"] == "MEDIUM")
    low_count = sum(1 for w in warnings if w["severity"] == "LOW")
    
    snapshot = {
        "timestamp": frappe.utils.now(),
        "total_warnings": len(warnings),
        "critical": critical_count,
        "high": high_count,
        "medium": medium_count,
        "low": low_count
    }
    
    history = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r") as f:
                history = json.load(f)
        except Exception:
            pass
            
    # Keep only the last 30 runs
    history.append(snapshot)
    history = history[-30:]
    
    try:
        with open(log_file, "w") as f:
            json.dump(history, f, indent=4)
    except Exception:
        pass


@frappe.whitelist()
def get_navigation_health_history():
    """
    Returns the last 30 navigation health snapshots for trend chart display.
    """
    log_file = frappe.get_site_path("public", "files", "smriti_nav_health_history.json")
    if not os.path.exists(log_file):
        return []
    try:
        with open(log_file, "r") as f:
            return json.load(f)
    except Exception:
        return []
