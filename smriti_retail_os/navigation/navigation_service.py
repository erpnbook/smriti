# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/navigation/navigation_service.py
# @description: SMRITI Navigation Manager (SNM) Resolver & Cache Engine.
# @author: Jawahar R. Mallah
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
import json
import hashlib
import os

CANONICAL_NAV = {
    "sections": [
        # ── 1. MASTERS ────────────────────────────────────────────────────────
        {
            "id": "masters",
            "label": "Masters",
            "status": "active",
            "items": [
                { "id": "product_catalog",  "label": "Product Catalog",   "route": "/products",         "standalone_route": "/products",         "status": "active" },
                { "id": "brand_master",     "label": "Brand Master",      "route": "/brand_master",     "standalone_route": "/brand_master",     "status": "active" },
                { "id": "item_master",      "label": "Item Master",       "route": "/item_master",      "standalone_route": "/item_master",      "status": "active" },
                { "id": "category_master",  "label": "Category Master",   "route": "/category_master",  "standalone_route": "/category_master",  "status": "active" },
                { "id": "scheme_creator",   "label": "Scheme Creator",    "route": "/scheme_creator",   "standalone_route": "/scheme_creator",   "status": "active" },
                { "id": "customers",        "label": "Customers",         "route": "/customers",        "standalone_route": "/customers",        "status": "active" },
                { "id": "suppliers",        "label": "Suppliers",         "route": "/suppliers",        "standalone_route": "/suppliers",        "status": "active" },
                { "id": "sfm_master",       "label": "Store Format",      "route": "/smriti-sfm",       "standalone_route": "/smriti-sfm",       "status": "active" },
                { "id": "sfc_catalog",      "label": "Format Catalog",    "route": "/smriti-sfc",       "standalone_route": "/smriti-sfc",       "status": "active" }
            ]
        },
        # ── 2. CGE ────────────────────────────────────────────────────────────
        {
            "id": "cge",
            "label": "CGE",
            "status": "active",
            "items": [
                { "id": "cge_dashboard",                    "label": "Dashboard",                "route": "/smriti-cge",  "standalone_route": "/smriti-cge",  "status": "active" },
                { "id": "cge_setup_hdr",                    "label": "Setup",                    "type": "header" },
                { "id": "cge_benefit_instruments",          "label": "Benefit Instruments",      "route": "/smriti-cge#benefit-instruments",      "standalone_route": "/smriti-cge#benefit-instruments",      "status": "coming_soon", "badge": "SOON" },
                { "id": "cge_membership_tiers",             "label": "Membership Tiers",         "route": "/smriti-cge#membership-tiers",         "standalone_route": "/smriti-cge#membership-tiers",         "status": "coming_soon", "badge": "SOON" },
                { "id": "cge_loyalty_programs",             "label": "Loyalty Programs",         "route": "/smriti-cge#loyalty-programs",         "standalone_route": "/smriti-cge#loyalty-programs",         "status": "coming_soon", "badge": "SOON" },
                { "id": "cge_marketing_hdr",                "label": "Marketing",                "type": "header" },
                { "id": "cge_campaigns",                    "label": "Campaigns",                "route": "/smriti-cge#campaigns",                "standalone_route": "/smriti-cge#campaigns",                "status": "coming_soon", "badge": "SOON" },
                { "id": "cge_promotion_rules",              "label": "Promotion Rules",          "route": "/smriti-cge#promotion-rules",          "standalone_route": "/smriti-cge#promotion-rules",          "status": "coming_soon", "badge": "SOON" },
                { "id": "cge_coupon_rules",                 "label": "Coupon Rules",             "route": "/smriti-cge#coupon-rules",             "standalone_route": "/smriti-cge#coupon-rules",             "status": "coming_soon", "badge": "SOON" },
                { "id": "cge_loyalty_rules",                "label": "Loyalty Rules",            "route": "/smriti-cge#loyalty-rules",            "standalone_route": "/smriti-cge#loyalty-rules",            "status": "coming_soon", "badge": "SOON" },
                { "id": "cge_operations_hdr",               "label": "Operations",               "type": "header" },
                { "id": "cge_benefit_wallets",              "label": "Benefit Wallets",          "route": "/smriti-cge#benefit-wallets",          "standalone_route": "/smriti-cge#benefit-wallets",          "status": "coming_soon", "badge": "SOON" },
                { "id": "cge_customer_benefit_profiles",    "label": "Customer Benefit Profiles","route": "/smriti-cge#customer-benefit-profiles","standalone_route": "/smriti-cge#customer-benefit-profiles","status": "coming_soon", "badge": "SOON" },
                { "id": "cge_governance_hdr",               "label": "Governance",               "type": "header" },
                { "id": "cge_benefit_resolution_policies",  "label": "Resolution Policies",      "route": "/smriti-cge#resolution-policies",      "standalone_route": "/smriti-cge#resolution-policies",      "status": "coming_soon", "badge": "SOON" },
                { "id": "cge_liability_snapshots",          "label": "Liability Snapshots",      "route": "/smriti-cge#liability-snapshots",      "standalone_route": "/smriti-cge#liability-snapshots",      "status": "coming_soon", "badge": "SOON" },
                { "id": "cge_benefit_audit_logs",           "label": "Audit Logs",               "route": "/smriti-cge#audit-logs",               "standalone_route": "/smriti-cge#audit-logs",               "status": "coming_soon", "badge": "SOON" }
            ]
        },
        # ── 3. PSV ────────────────────────────────────────────────────────────
        {
            "id": "psv",
            "label": "PSV",
            "status": "active",
            "items": [
                { "id": "psv_dashboard",        "label": "Dashboard",            "route": "/psv-dashboard",          "standalone_route": "/psv-dashboard",          "status": "active" },
                { "id": "sales_uploads",        "label": "Sales Uploads",        "route": "/sales-upload",           "standalone_route": "/sales-upload",           "status": "active" },
                { "id": "stock_uploads",        "label": "Stock Uploads",        "route": "/stock-audit",            "standalone_route": "/stock-audit",            "status": "active" },
                { "id": "reconciliation",       "label": "Reconciliation",       "route": "/psv_reconciliation",     "standalone_route": "/psv_reconciliation",     "status": "active" },
                { "id": "exception_analysis",   "label": "Exception Analysis",   "route": "/psv_exception_analysis", "standalone_route": "/psv_exception_analysis", "status": "active" },
                { "id": "psv_opening_balance",  "label": "PSV Opening Balance",  "route": "/psv-opening-balance",    "standalone_route": "/psv-opening-balance",    "status": "active" },
                { "id": "distributor_accounts", "label": "Channel Partners",     "route": "/smriti-coming-soon",     "standalone_route": "/smriti-coming-soon",     "status": "coming_soon", "badge": "SOON" },
                { "id": "stock_aging",          "label": "Stock Aging",          "route": "/smriti-coming-soon",     "standalone_route": "/smriti-coming-soon",     "status": "coming_soon", "badge": "SOON" }
            ]
        },
        # ── 4. SALES ──────────────────────────────────────────────────────────
        {
            "id": "sales",
            "label": "Sales",
            "status": "active",
            "items": [
                { "id": "pos_billing",      "label": "POS Billing",            "route": "/billing",              "standalone_route": "/billing",              "status": "active" },
                { "id": "sizewise_invoice", "label": "Sizewise Billing",       "route": "/sizewise_invoice",     "standalone_route": "/sizewise_invoice",     "status": "active" },
                { "id": "quotation",        "label": "Quotations",             "route": "/smriti-quotation",     "standalone_route": "/smriti-quotation",     "status": "active" },
                { "id": "sales_orders",     "label": "Sales Orders",           "route": "/sales_orders",         "standalone_route": "/sales_orders",         "status": "active" },
                { "id": "tax_invoice",      "label": "Tax Invoice",            "route": "/sales_invoices",       "standalone_route": "/sales_invoices",       "status": "active" },
                { "id": "sales_return",     "label": "Sales Return",           "route": "/sales_return",         "standalone_route": "/sales_return",         "status": "active" },
                { "id": "delivery_challan", "label": "Delivery Challan",       "route": "/delivery_challan",     "standalone_route": "/delivery_challan",     "status": "active" },
                { "id": "eway_bill",        "label": "E-Way Bill Management",  "route": "/eway_bill",            "standalone_route": "/eway_bill",            "status": "active" },
                { "id": "clienteling",      "label": "Clienteling Studio",     "route": "/smriti-clienteling",   "standalone_route": "/smriti-clienteling",   "status": "active" }
            ]
        },
        # ── 5. PURCHASE STUDIO ────────────────────────────────────────────────
        {
            "id": "purchase",
            "label": "Purchase Studio",
            "status": "active",
            "items": [
                { "id": "purchase_dashboard",   "label": "Dashboard",           "route": "/smriti-purchase",                 "standalone_route": "/smriti-purchase",                 "status": "active" },
                { "id": "purchase_orders",      "label": "Purchase Orders",     "route": "/smriti-purchase#orders",          "standalone_route": "/smriti-purchase#orders",          "status": "active" },
                { "id": "grn_receipts",         "label": "GRN / Receipts",      "route": "/smriti-grn",                      "standalone_route": "/smriti-grn",                      "status": "active" },
                { "id": "purchase_invoice_pg",  "label": "Purchase Invoices",   "route": "/purchase_invoice",                "standalone_route": "/purchase_invoice",                "status": "active" },
                { "id": "purchase_receipt_pg",  "label": "Purchase Receipts",   "route": "/purchase_receipt",                "standalone_route": "/purchase_receipt",                "status": "active" },
                { "id": "purchase_returns",     "label": "Supplier Returns",    "route": "/supplier_returns",                "standalone_route": "/supplier_returns",                "status": "active" },
                { "id": "supplier_ledger",      "label": "Supplier Ledger",     "route": "/smriti-purchase#supplier-ledger", "standalone_route": "/smriti-purchase#supplier-ledger", "status": "active" },
                { "id": "purchase_analytics",   "label": "Analytics",           "route": "/smriti-purchase#analytics",       "standalone_route": "/smriti-purchase#analytics",       "status": "active" },
                { "id": "purchase_settings",    "label": "Settings",            "route": "/smriti-purchase#settings",        "standalone_route": "/smriti-purchase#settings",        "status": "active" }
            ]
        },
        # ── 6. INVENTORY ──────────────────────────────────────────────────────
        {
            "id": "inventory",
            "label": "Inventory",
            "status": "active",
            "items": [
                { "id": "warehouses",        "label": "Warehouses",        "route": "/inventory?tab=warehouses",   "standalone_route": "/inventory?tab=warehouses",   "status": "active" },
                { "id": "stock_transfer",    "label": "Stock Transfer",    "route": "/inventory?tab=transfer",     "standalone_route": "/inventory?tab=transfer",     "status": "active" },
                { "id": "stock_adjustments", "label": "Stock Adjustments", "route": "/inventory?tab=adjustments",  "standalone_route": "/inventory?tab=adjustments",  "status": "active" },
                { "id": "stock_audit",       "label": "Stock Audit",       "route": "/stock-audit",                "standalone_route": "/stock-audit",                "status": "active" },
                { "id": "opening_stock",     "label": "Opening Stock",     "route": "/smriti-coming-soon",         "standalone_route": "/smriti-coming-soon",         "status": "coming_soon", "badge": "SOON" },
                { "id": "stock_operations",  "label": "Stock Operations",  "route": "/smriti-coming-soon",         "standalone_route": "/smriti-coming-soon",         "status": "coming_soon", "badge": "SOON" }
            ]
        },
        # ── 7. BARCODE STUDIO ─────────────────────────────────────────────────
        {
            "id": "barcode_studio",
            "label": "Barcode Studio",
            "status": "active",
            "items": [
                { "id": "label_studio",    "label": "Label Studio",       "route": "/barcode",          "standalone_route": "/barcode",          "status": "active" },
                { "id": "print_templates", "label": "Print Templates",    "route": "/print_templates",  "standalone_route": "/print_templates",  "status": "active" },
                { "id": "sizewise_item",   "label": "Sizewise Item CRUD", "route": "/sizewise_item",    "standalone_route": "/sizewise_item",    "status": "active" }
            ]
        },
        # ── 8. FINANCE ────────────────────────────────────────────────────────
        {
            "id": "finance",
            "label": "Finance",
            "status": "active",
            "items": [
                { "id": "payments",       "label": "Payments",              "route": "/payments",         "standalone_route": "/payments",         "status": "active" },
                { "id": "tally",          "label": "Tally Integration",     "route": "/smriti-tally",     "standalone_route": "/smriti-tally",     "status": "active" },
                { "id": "safe_cash",      "label": "Safe / Cash",           "route": "/smriti-safe",      "standalone_route": "/smriti-safe",      "status": "active" },
                { "id": "uie_integration","label": "Integration Center",    "route": "/smriti-uie",       "standalone_route": "/smriti-uie",       "status": "active" },
                { "id": "receipts",       "label": "Receipts",              "route": "/smriti-coming-soon","standalone_route": "/smriti-coming-soon","status": "coming_soon", "badge": "SOON" },
                { "id": "advances",       "label": "Advances",              "route": "/smriti-coming-soon","standalone_route": "/smriti-coming-soon","status": "coming_soon", "badge": "SOON" }
            ]
        },
        # ── 9. REPORTS ────────────────────────────────────────────────────────
        {
            "id": "reports",
            "label": "Reports",
            "status": "active",
            "items": [
                { "id": "sas_hdr",                    "label": "Analytics Studio",          "type": "header" },
                { "id": "analytics_studio",           "label": "Analytics Studio",          "route": "/smriti-analytics-studio",                                           "standalone_route": "/smriti-analytics-studio",                                           "status": "active", "badge": "NEW" },
                { "id": "analytics_dashboard",        "label": "Analytics Dashboard",       "route": "/analytics",                                                         "standalone_route": "/analytics",                                                         "status": "active" },
                { "id": "reports_hdr",                "label": "Classic Reports",           "type": "header" },
                { "id": "sales_reports",              "label": "Sales Reports",             "route": "/reports?section=sales",                                             "standalone_route": "/reports?section=sales",                                             "status": "active" },
                { "id": "inventory_reports",          "label": "Inventory Reports",         "route": "/reports?section=inventory",                                         "standalone_route": "/reports?section=inventory",                                         "status": "active" },
                { "id": "finance_reports",            "label": "Finance Reports",           "route": "/reports?section=finance",                                           "standalone_route": "/reports?section=finance",                                           "status": "active" },
                { "id": "gst_reports",                "label": "GST Reports",               "route": "/reports?section=gst",                                               "standalone_route": "/reports?section=gst",                                               "status": "active" },
                { "id": "psv_reports",                "label": "PSV Reports",               "route": "/reports?section=psv",                                               "standalone_route": "/reports?section=psv",                                               "status": "active" },
                { "id": "purchase_reports_hdr",       "label": "Purchase Reports",          "type": "header" },
                { "id": "purchase_order_summary",     "label": "Purchase Order Summary",    "route": "/smriti-analytics-studio?report=purchase_order_summary",             "standalone_route": "/smriti-analytics-studio?report=purchase_order_summary",             "status": "active" },
                { "id": "grn_register",               "label": "GRN Register",              "route": "/smriti-analytics-studio?report=grn_register",                       "standalone_route": "/smriti-analytics-studio?report=grn_register",                       "status": "active" },
                { "id": "purchase_invoice_register",  "label": "Purchase Invoice Register", "route": "/smriti-analytics-studio?report=purchase_invoice_register",          "standalone_route": "/smriti-analytics-studio?report=purchase_invoice_register",          "status": "active" },
                { "id": "supplier_purchase_summary",  "label": "Supplier Purchase Summary", "route": "/smriti-analytics-studio?report=supplier_purchase_summary",          "standalone_route": "/smriti-analytics-studio?report=supplier_purchase_summary",          "status": "active" },
                { "id": "item_wise_purchase",         "label": "Item-wise Purchase",        "route": "/smriti-analytics-studio?report=item_wise_purchase",                 "standalone_route": "/smriti-analytics-studio?report=item_wise_purchase",                 "status": "active" },
                { "id": "purchase_return_register",   "label": "Purchase Return Register",  "route": "/smriti-analytics-studio?report=purchase_return_register",           "standalone_route": "/smriti-analytics-studio?report=purchase_return_register",           "status": "active" },
                { "id": "billing_metrics",            "label": "Billing Metrics",           "route": "/smriti-analytics-studio?report=billing_metrics",                    "standalone_route": "/smriti-analytics-studio?report=billing_metrics",                    "status": "active" },
                { "id": "audit_reports",              "label": "Audit Reports",             "route": "/smriti-security-log",                                               "standalone_route": "/smriti-security-log",                                               "status": "active" }
            ]
        },
        # ── 10. ADMINISTRATION ────────────────────────────────────────────────
        {
            "id": "administration",
            "label": "Administration",
            "status": "active",
            "items": [
                { "id": "shift_register",    "label": "Day / Shift Register",     "route": "/shift",                   "standalone_route": "/shift",                   "status": "active" },
                { "id": "pos_profiles",      "label": "POS Profiles",             "route": "/smriti-pos-profiles",     "standalone_route": "/smriti-pos-profiles",     "status": "active" },
                { "id": "user_management",   "label": "User Management",          "route": "/security?tab=users",      "standalone_route": "/security?tab=users",      "status": "active" },
                { "id": "roles_permissions", "label": "Roles & Permissions",      "route": "/security?tab=roles",      "standalone_route": "/security?tab=roles",      "status": "active" },
                { "id": "security_workflows","label": "Security & Workflows",     "route": "/security",                "standalone_route": "/security",                "status": "active" },
                { "id": "audit_logs",        "label": "Audit Logs",               "route": "/smriti-security-log",     "standalone_route": "/smriti-security-log",     "status": "active" },
                { "id": "config_portal",     "label": "Config Portal",            "route": "/configure",               "standalone_route": "/configure",               "status": "active" },
                { "id": "platform_center",   "label": "Platform Center",          "route": "/platform_center",         "standalone_route": "/platform_center",         "status": "active" },
                { "id": "platform_admin",    "label": "Platform Admin",           "route": "/smriti-platform-admin",   "standalone_route": "/smriti-platform-admin",   "status": "active" },
                { "id": "nav_health",        "label": "Nav Health Monitor",       "route": "/smriti-nav-health",       "standalone_route": "/smriti-nav-health",       "status": "active" },
                { "id": "field_explorer",    "label": "Field Explorer",           "route": "/smriti-field-explorer",   "standalone_route": "/smriti-field-explorer",   "status": "active" },
                { "id": "smriti_license",    "label": "License & Registration",   "route": "/smriti-license",          "standalone_route": "/smriti-license",          "status": "active" },
                { "id": "backup_restore",    "label": "Backup & Restore",         "route": "/backup",                  "standalone_route": "/backup",                  "status": "active" },
                { "id": "go_live",           "label": "Go Live Checklist",        "route": "/smriti-go-live",          "standalone_route": "/smriti-go-live",          "status": "active" },
                { "id": "setup_wizard",      "label": "Setup Wizard",             "route": "/setup_wizard",            "standalone_route": "/setup_wizard",            "status": "active" }
            ]
        },
        # ── 11. HELP DESK ─────────────────────────────────────────────────────
        {
            "id": "help_desk",
            "label": "Help Desk",
            "status": "active",
            "items": [
                { "id": "knowledge_studio",    "label": "Knowledge Studio",   "route": "/smriti-knowledge-studio", "standalone_route": "/smriti-knowledge-studio", "status": "active" },
                { "id": "knowledge_center",    "label": "Knowledge Center",   "route": "/smriti-help",             "standalone_route": "/smriti-help",             "status": "active" },
                { "id": "formula_registry",    "label": "Formula Registry",   "route": "/smriti-formula-registry", "standalone_route": "/smriti-formula-registry", "status": "active" },
                { "id": "business_dictionary", "label": "Business Dictionary","route": "/smriti-dictionary",       "standalone_route": "/smriti-dictionary",       "status": "active" },
                { "id": "release_notes",       "label": "Release Notes",      "route": "/release_notes",           "standalone_route": "/release_notes",           "status": "active" },
                { "id": "support",             "label": "Support",            "route": "/smriti_support",          "standalone_route": "/smriti_support",          "status": "active" }
            ]
        },
        # ── 12. AI HUB ────────────────────────────────────────────────────────
        {
            "id": "ai_hub",
            "label": "AI Hub",
            "status": "active",
            "items": [
                { "id": "pdt_dashboard",      "label": "PDT Dashboard",       "route": "/smriti-pdt",         "standalone_route": "/smriti-pdt",         "status": "active" },
                { "id": "simulation_sandbox", "label": "Simulation Sandbox",  "route": "/smriti-coming-soon", "standalone_route": "/smriti-coming-soon", "status": "coming_soon", "progress": 60, "eta": "Q3 2026", "badge": "SOON" },
                { "id": "demand_forecasts",   "label": "Demand Forecasts",    "status": "hidden" },
                { "id": "cashier_performance","label": "Cashier Performance", "status": "hidden" }
            ]
        },
        # ── 13. COMMERCIAL ────────────────────────────────────────────────────
        {
            "id": "commercial",
            "label": "Commercial",
            "status": "active",
            "items": [
                { "id": "smriti_pricing", "label": "Pricing Plans",     "route": "/smriti-pricing",        "standalone_route": "/smriti-pricing",        "status": "active" },
                { "id": "roi_calculator", "label": "ROI Calculator",    "route": "/smriti-roi-calculator", "standalone_route": "/smriti-roi-calculator", "status": "active" },
                { "id": "trial_signup",   "label": "Start Free Trial",  "route": "/smriti-trial",          "standalone_route": "/smriti-trial",          "status": "active" },
                { "id": "trial_leads",    "label": "Trial Leads CRM",   "route": "/smriti-trial-leads",    "standalone_route": "/smriti-trial-leads",    "status": "active" }
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
    
    cached_val = smriti.cache().get_value(cache_key)
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
    smriti.cache().set_value(cache_key, json.dumps(resolved_nav), expires_in_sec=86400)
    return resolved_nav

def invalidate_navigation_cache(user=None, company=None):
    """
    Invalidates navigation cache patterns.
    """
    # Simple invalidation strategy: delete keys matching smriti:navigation:*
    # In Redis context, we can delete keys or clear user specific entries
    if user and company:
        cache_hash = _get_navigation_version_hash(user, company)
        smriti.cache().delete_value(f"smriti:navigation:{user}:{company}:{cache_hash}")
    else:
        # Clear all
        keys = smriti.cache().get_keys("smriti:navigation:*")
        for k in keys:
            smriti.cache().delete_value(k)

def _get_navigation_version_hash(user, company):
    """
    Generates a version hash from SMRITI Navigation Profile and Override states.
    """
    last_mod = smriti.db.get("SMRITI Navigation Profile", {}, "modified", order_by="modified desc") or "default"
    last_override_mod = smriti.db.get("SMRITI Navigation Override", {}, "modified", order_by="modified desc") or "default"
    last_assignment_mod = smriti.db.get("SMRITI Navigation Assignment", {}, "modified", order_by="modified desc") or "default"
    
    combined = f"{last_mod}:{last_override_mod}:{last_assignment_mod}"
    return hashlib.md5(combined.encode("utf-8")).hexdigest()


def _resolve_navigation_tree(user, company):
    """
    Resolves permissions, assignments, and structural overrides on top of canonical config.
    """
    # Fallback immediately if SMRITI Navigation Profile is empty
    if not smriti.db.count("SMRITI Navigation Profile"):
        return CANONICAL_NAV

    # Find highest priority assignment
    user_roles = frappe.get_roles(user)
    assignments = smriti.db.get_list(
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
    profile_doc = smriti.documents.get("SMRITI Navigation Profile", resolved_profile)
    
    # Load overrides
    overrides = smriti.db.get_list(
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
    overridden_ids = smriti.db.get_list("SMRITI Navigation Override", fields=["menu_id", "navigation_profile"])
    
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
