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
    },
    "backup_security": {
        "title": _("Backup Security & Key Recovery"),
        "category": "Administration Guides",
        "description": _("Guide to GPG AES-256 backup encryption, security banners, and dual-custodian recovery."),
        "content": _(
            "SMRITI Retail OS v1.8.3 features an enterprise-grade Backup Security system to ensure database backups are encrypted at rest and protected against unauthorized access.\n\n"
            "1. AES-256 Symmetric Encryption\n"
            "All database backups are encrypted symmetrically using GPG with a strong 32-character key generated when the feature is enabled. Passphrases are piped to GPG via secure input streams rather than CLI arguments, preventing process sniffing.\n\n"
            "2. Dual-Custodian Split Key Recovery\n"
            "To prevent single-point-of-failure or unauthorized restores, encryption recovery is governed by two registered Key Custodians. The system splits the active key at its midpoint and sends the individual fragments to the verified custodians' emails only when SMTP outgoing is properly configured and custodians are verified.\n\n"
            "3. Real-time Restoration Logs\n"
            "When restoring a backup, Socket.io events stream live decryption and database rebuilding progress directly to the administrator's restore modal, keeping operations fully transparent."
        ),
        "faqs": [
            {
                "question": _("What do the different Security Banner colors mean?"),
                "answer": _("RED: Backup encryption is disabled (Vulnerable).\nAMBER: Encryption is enabled, but dual-custodian recovery is not fully verified (Partially Secured).\nGREEN: Encryption is enabled and dual-custodian recovery is configured and verified (Fully Secured).")
            },
            {
                "question": _("How is the decryption temporary file handled?"),
                "answer": _("During restore, the encrypted backup is decrypted to a temporary location. Upon success or failure, the system securely overwrites and deletes the file using the UNIX 'shred' utility (with a zero-overwrite fallback if shred is absent) to leave zero traces on disk.")
            },
            {
                "question": _("Can I rotate the encryption key safely?"),
                "answer": _("Yes. The system supports key versioning. Previous keys are retained in the system configuration, allowing historical backups postfixed with key version (e.g. '-v1.smriti.enc') to be decrypted seamlessly.")
            }
        ]
    },
    "audit_reports_guide": {
        "title": _("System Security & Audit Reports"),
        "category": "Administration Guides",
        "description": _("How to access and interpret SMRITI Security Audit Logs and Address Change Logs."),
        "content": _(
            "SMRITI Retail OS v1.9.2 includes a dedicated Audit Reports module under Administration to track security events and metadata changes without exposing raw backend tables.\n\n"
            "1. SMRITI Security Audit Log\n"
            "This log records all high-impact actions taken by users in SMRITI. It tracks the creation datetime, user account, specific operation (e.g. template changes, print queue cleanup), subject/details of the change, and source IP address. Security logs are fetched directly from the Activity Log system of record.\n\n"
            "2. SMRITI Address Change Log\n"
            "Tracks changes to warehouse, customer, supplier, and company addresses. It records the date/time of modification, the user who changed it, the company, the specific field modified, and a clear comparison of the old value vs the new value."
        ),
        "faqs": [
            {
                "question": _("Who has permission to view these audit logs?"),
                "answer": _("Only users assigned the 'System Manager' or 'SMRITI Store Manager' roles are permitted to access SMRITI Audit Reports.")
            },
            {
                "question": _("How far back do the logs query by default?"),
                "answer": _("You can filter logs by any date range using the 'From Date' and 'To Date' selectors. The page includes standard presets ('Today', 'This Week', 'This Month', 'Last Month') for quick querying, capped at a maximum retrieval limit of 10,000 records for performance protection.")
            }
        ]
    },
    "pivot_matrix_builder": {
        "title": _("Pivot Matrix Builder & Custom Reports"),
        "category": "Analytics Guides",
        "description": _("Guide to using the drag-and-drop Pivot Matrix Builder and column reordering in SMRITI Reports."),
        "content": _(
            "SMRITI Retail OS features a dynamic drag-and-drop reporting workspace designed to give users maximum control over data visualization.\n\n"
            "1. Column Reordering\n"
            "In any standard report, columns can be rearranged dynamically by clicking and dragging the column headers left or right. Once the desired sequence is established, click 'Save View' to persist this layout in the database under your customized SMRITI Saved Views.\n\n"
            "2. Pivot Matrix Builder\n"
            "Toggle the 'Pivot View' button next to the filter bar to open the Pivot Builder panel. This workspace contains: \n"
            "- Available Fields: A list of tags representing all columns present in the report.\n"
            "- Rows Zone: Drag field tags here to define the row-wise categories of your matrix.\n"
            "- Columns Zone: Drag field tags here to define the column-wise headers of your matrix.\n"
            "- Values Zone: Drag field tags here to choose the numeric metrics. Each metric can be aggregated using Sum, Count, or Average functions.\n\n"
            "3. Dynamic Re-aggregation\n"
            "The client-side rendering engine automatically aggregates raw data, merges headers, and computes row and column Grand Totals in real-time."
        ),
        "faqs": [
            {
                "question": _("Can I save a pivot configuration for future use?"),
                "answer": _("Pivot matrix configurations are currently temporary. To save a column sequence for standard reports, use the 'Save View' feature.")
            },
            {
                "question": _("Which fields can be used in the Values zone?"),
                "answer": _("While any field can be dragged into the Values zone, numeric fields (such as Quantities, Values, and Amounts) default to the 'Sum' aggregation, while text or status fields default to 'Count'.")
            }
        ]
    },
    "dashboard_customization": {
        "title": _("Dashboard Customization & Layouts"),
        "category": "Analytics Guides",
        "description": _("Learn how to personalize your SMRITI Home and PSV dashboards using drag-and-drop layouts."),
        "content": _(
            "SMRITI Retail OS provides a customizable dashboard framework where users can reorder widgets to prioritize their primary business metrics.\n\n"
            "1. Toggling Edit Mode\n"
            "Click the 'Customize Layout' (dashboard icon) button in the topbar of the SMRITI Home or PSV Dashboard. This activates the layout customizer, displaying dashed blue borders and '⠿' drag handles on all adjustable widget cards.\n\n"
            "2. Drag-and-Drop Reordering\n"
            "Hover over any widget card's drag handle or title, click and drag it to a new location within the grid. The other cards will dynamically shift to accommodate the new placement.\n\n"
            "3. Layout Persistence\n"
            "After rearranging cards, click 'Customize Layout' again to exit edit mode and save. The custom layout sequence is serialized and saved in your browser's local storage (`localStorage`), meaning your personalized layout will persist across page reloads and browser sessions."
        ),
        "faqs": [
            {
                "question": _("Why do some widgets take up the full width?"),
                "answer": _("Specific widgets, such as the Trend Chart or SKU Productivity matrix, are designated as 'span-full' to render wide charts and detailed tables properly. These can be reordered vertically but will always occupy the full grid width.")
            },
            {
                "question": _("Is my custom layout shared with other users?"),
                "answer": _("No. Since dashboard layout configurations are stored in the browser's local storage (`localStorage`), the customization is user-specific and device-specific.")
            }
        ]
    }
}

@frappe.whitelist()
def get_help_article(article_key=None):
    """
    Returns structured article content for SMRITI Help Center.
    If 'provider' is specified, calls the provider function to get content.
    """
    if not article_key:
        article_key = frappe.form_dict.get("article_key") or frappe.form_dict.get("article")

    if not article_key:
        frappe.throw(_("Help article key is required"), frappe.ValidationError)

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
