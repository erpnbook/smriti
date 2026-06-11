# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/help_api.py
# @description: Whitelisted API endpoints for SMRITI Help Center registry.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-11
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _

HELP_CENTER_REGISTRY = {
    # Analytics Guides
    "inventory_productivity": {
        "title": _("Inventory Productivity & SKU Rationalization"),
        "category": "Analytics Guides",
        "description": _("Detailed guide explaining GMROI, Productivity Score calculations, and SKU classification rules."),
        "provider": "smriti_retail_os.psv_service.get_inventory_productivity_methodology"
    },
    "inventory_aging": {
        "title": _("Inventory Aging Analysis"),
        "category": "Analytics Guides",
        "description": _("Understand how SMRITI tracks FIFO inventory aging and days of inventory (DOI)."),
        "content": _("Coming Soon: Inventory Aging Analysis guide details how the stock aging snapshot tracks FIFO inventory aging buckets (0-30, 31-60, 61-90, 90+ days) and computes average age.")
    },
    "reorder_engine": {
        "title": _("Automated Reorder Engine"),
        "category": "Analytics Guides",
        "description": _("How the reorder engine triggers replenishment recommendations based on lead times and safety stock."),
        "content": _("Coming Soon: Automated Reorder Engine guide details how the system calculates reorder points and order quantities.")
    },
    "dead_stock_recovery": {
        "title": _("Dead Stock Recovery Workflows"),
        "category": "Analytics Guides",
        "description": _("Strategies and system tools to recover capital locked in dead inventory."),
        "content": _("Coming Soon: Dead Stock Recovery Workflows details liquidation workflows and promotions for slow-moving stock.")
    },
    # Operations Guides
    "store_opening_closing": {
        "title": _("Store Opening & Closing Checklist"),
        "category": "Operations Guides",
        "description": _("Daily operational procedures for opening and closing store registers."),
        "content": _("Coming Soon: Detailed guide on cash drawer reconciliation, store opening checks, end-of-day register closure, and store manager checklists.")
    },
    "billing_cashier_workflows": {
        "title": _("Billing & Cashier Workflows"),
        "category": "Operations Guides",
        "description": _("Standard operating procedures for billing, POS operations, and customer checkouts."),
        "content": _("Coming Soon: Learn how to scan items, apply discounts, select loyalty cards, handle payments, and issue bills.")
    },
    # Purchasing Guides
    "vendor_management_po": {
        "title": _("Vendor Management & Purchase Orders"),
        "category": "Purchasing Guides",
        "description": _("How to manage vendors, purchase agreements, and issue Purchase Orders."),
        "content": _("Coming Soon: Guide explaining supplier onboarding, price catalogs, auto PO generation, and purchase cycle verification.")
    },
    # Administration Guides
    "user_roles_permissions": {
        "title": _("User Roles & Operational Permissions"),
        "category": "Administration Guides",
        "description": _("Managing users, roles, and functional permissions in SMRITI OS."),
        "content": _("Coming Soon: System administrator guide for setting up roles, branch restrictions, custom approval limits, and security controls.")
    },
    "branding_theme_setup": {
        "title": _("Branding & Store Theme Setup"),
        "category": "Administration Guides",
        "description": _("Customizing store themes, logos, receipt templates, and local branding settings."),
        "content": _("Coming Soon: Guide on custom CSS injection, receipt print formatting, logo uploads, and multi-tenant branding settings.")
    }
}

@frappe.whitelist()
def get_help_article(article_key):
    """
    Returns structured article content for SMRITI Help Center.
    If 'provider' is specified, calls the provider function to get content.
    """
    article = HELP_CENTER_REGISTRY.get(article_key)
    if not article:
        frappe.throw(_("Help article '{0}' not found").format(article_key), frappe.DoesNotExistError)
        
    if "provider" in article:
        # Resolve dynamically
        provider_method = article["provider"]
        content = frappe.get_attr(provider_method)()
        article_data = dict(article)
        article_data.update(content)
        return article_data
        
    return article

@frappe.whitelist()
def get_help_toc():
    """
    Returns the Help Center Table of Contents grouped by Category.
    """
    categories = {}
    for key, article in HELP_CENTER_REGISTRY.items():
        cat = article.get("category", "General")
        categories.setdefault(cat, []).append({
            "key": key,
            "title": article["title"],
            "description": article.get("description", "")
        })
    
    # Sort categories to match the requested architecture order
    ordered_categories = {}
    preferred_order = ["Analytics Guides", "Operations Guides", "Purchasing Guides", "Administration Guides"]
    for cat in preferred_order:
        if cat in categories:
            ordered_categories[cat] = categories[cat]
            
    for cat in sorted(categories.keys()):
        if cat not in ordered_categories:
            ordered_categories[cat] = categories[cat]
            
    return ordered_categories
