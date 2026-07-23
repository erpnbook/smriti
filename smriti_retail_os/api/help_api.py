# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/help_api.py
# @description: Whitelisted API endpoints for SMRITI Help Center registry.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-11
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti

DOCUMENT_REGISTRY = {
    "volume_1_daily_operations": {
        "name": "volume_1_daily_operations",
        "title": _("Vol 1: Daily Operations"),
        "category": "User Manuals",
        "file_name": "volume_1_daily_operations.md",
        "document_type": "user_manual",
        "audience": "customer",
        "visibility": "all",
        "searchable": True
    },
    "volume_2_manager_guide": {
        "name": "volume_2_manager_guide",
        "title": _("Vol 2: Manager Guide"),
        "category": "User Manuals",
        "file_name": "volume_2_manager_guide.md",
        "document_type": "user_manual",
        "audience": "customer",
        "visibility": "all",
        "searchable": True
    },
    "volume_3_executive_guide": {
        "name": "volume_3_executive_guide",
        "title": _("Vol 3: Executive Guide"),
        "category": "User Manuals",
        "file_name": "volume_3_executive_guide.md",
        "document_type": "user_manual",
        "audience": "customer",
        "visibility": "all",
        "searchable": True
    },
    "volume_4_troubleshooting_faq": {
        "name": "volume_4_troubleshooting_faq",
        "title": _("Vol 4: Support & FAQs"),
        "category": "User Manuals",
        "file_name": "volume_4_troubleshooting_faq.md",
        "document_type": "user_manual",
        "audience": "customer",
        "visibility": "all",
        "searchable": True
    },
    "volume_5_training_workbook": {
        "name": "volume_5_training_workbook",
        "title": _("Vol 5: Training Workbook"),
        "category": "User Manuals",
        "file_name": "volume_5_training_workbook.md",
        "document_type": "user_manual",
        "audience": "customer",
        "visibility": "all",
        "searchable": True
    },
    "about_smriti": {
        "name": "about_smriti",
        "title": _("About SMRITI (Legacy)"),
        "category": "User Manuals",
        "file_name": "about_smriti.md",
        "document_type": "user_manual",
        "audience": "customer",
        "visibility": "all",
        "searchable": True
    },
    "ABOUT_SMRITI": {
        "name": "ABOUT_SMRITI",
        "title": _("About SMRITI"),
        "category": "about",
        "file_name": "about_smriti_dup.md",
        "document_type": "about",
        "audience": "customer",
        "visibility": "all",
        "searchable": True
    },
    "ABOUT_AITDL": {
        "name": "ABOUT_AITDL",
        "title": _("About AITDL"),
        "category": "about",
        "file_name": "about_aitdl.md",
        "document_type": "about",
        "audience": "customer",
        "visibility": "all",
        "searchable": True
    },
    "ABOUT_AUTHOR": {
        "name": "ABOUT_AUTHOR",
        "title": _("About the Author"),
        "category": "about",
        "file_name": "about_author.md",
        "document_type": "about",
        "audience": "customer",
        "visibility": "all",
        "searchable": True
    },
    "BRD-01_BRANDING_ATTRIBUTION_DOCUMENTATION": {
        "name": "BRD-01_BRANDING_ATTRIBUTION_DOCUMENTATION",
        "title": _("BRD-01: Branding & Attributions"),
        "category": "Governance",
        "file_name": "branding_attribution.md",
        "document_type": "governance",
        "audience": "internal",
        "visibility": "admin",
        "searchable": False
    },
    "AI_CONTENT_POLICY": {
        "name": "AI_CONTENT_POLICY",
        "title": _("AI Content Policy"),
        "category": "Governance",
        "file_name": "ai_content_policy.md",
        "document_type": "governance",
        "audience": "internal",
        "visibility": "admin",
        "searchable": False
    }
}

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
        "about": _("This guide explains SMRITI's FIFO-based inventory aging model, aging buckets, and automatic health alert triggers."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI Inventory Planner"),
            "quote": _("Knowing the age of your inventory is the first step to unlocking tied-up working capital.")
        },
        "content": _(
            "SMRITI Retail OS features a real-time FIFO stock aging snapshot engine to track inventory velocity and highlight capital risks.\n\n"
            "1. FIFO-Based Quantity Allocation\n"
            "Quantity is allocated to aging buckets by scanning historical positive ledger entries (e.g. Purchase Receipts, Stock Entries) in reverse chronological order (FIFO logic). Any remaining stock not matched to a positive ledger entry is automatically assigned to the oldest bucket (180+ days).\n\n"
            "2. Aging Buckets\n"
            "Stock is grouped into five aging intervals:\n"
            "- 0-30 Days: Fresh inventory, high sales probability.\n"
            "- 31-60 Days: Standard shelf inventory.\n"
            "- 61-90 Days: Slow-moving inventory starting to lock capital.\n"
            "- 91-180 Days: High-risk inventory requiring promotional intervention.\n"
            "- 180+ Days (Critical): Dead stock requiring immediate liquidation.\n\n"
            "3. Stock Health Classification\n"
            "The system automatically flags stock lines with a health status:\n"
            "- Critical: If there is any quantity in the 180+ Days bucket, or if more than 50% of the item's total inventory lies in the 91-180 and 180+ Days buckets.\n"
            "- Warning: If more than 25% of the total inventory lies in 91-180 and 180+ Days buckets, or if there is any quantity in the 61-90 Days bucket.\n"
            "- Healthy: All other inventory lines."
        ),
        "faqs": [
            {
                "question": _("How often are the stock aging snapshots updated?"),
                "answer": _("Snapshots are generated incrementally using background tasks scheduled via PSV System Settings, preventing database locks during high-traffic store hours.")
            },
            {
                "question": _("What happens to negative stock entries in aging calculations?"),
                "answer": _("Negative stock entries represent sales and outflows, which consume stock according to FIFO. The aging engine only scans positive entries (receipts) to trace the origin date of the remaining balance.")
            },
            {
                "question": _("Can I filter aging reports by store zones or categories?"),
                "answer": _("Yes. The SMRITI Reports Center allows filtering by warehouse, zone, item group, and supplier to isolate aging bottlenecks.")
            }
        ]
    },
    "reorder_engine": {
        "title": _("Automated Reorder Engine"),
        "category": "Analytics Guides",
        "description": _("How the reorder engine triggers replenishment recommendations based on lead times and safety stock."),
        "about": _("This guide explains the SMRITI reorder engine calculations, lookback windows, and priority recommendation cascade."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI Supply Chain Planner"),
            "quote": _("Precision replenishment prevents stockouts while avoiding over-stocking and locked capital.")
        },
        "content": _(
            "The SMRITI Reorder Engine automates store replenishment by calculating optimal reorder points and purchase quantities based on live sales velocity and current inventory balances.\n\n"
            "1. Three-Level Parameter Cascade\n"
            "To define replenishment rules, the engine checks settings in a strict hierarchy:\n"
            "- Level 1 (Highest): Variant-Specific Reorder Rules (e.g. rule for a specific size/color SKU).\n"
            "- Level 2: Item Group Reorder Rules (e.g. rule for the Footwear category).\n"
            "- Level 3 (Fallback): Global defaults configured in SMRITI PSV Settings.\n\n"
            "2. Sales Velocity Calculation\n"
            "The engine reviews sales history over a lookback window (default 4 weeks). It computes the weekly sales average (total sold divided by actual weeks of availability) and derives the average daily sales rate.\n\n"
            "3. Formulas and Rules\n"
            "- Days Cover: How many days the current stock will last based on daily sales (current balance / daily sales).\n"
            "- Reorder Level (Point): The threshold below which replenishment triggers. Calculated as: (Lead Time Days * Daily Sales) + Safety Stock.\n"
            "- Recommended Qty: Calculated as: Reorder Level - Current Balance. If a Maximum Stock cap is defined, the quantity is capped at: Max Stock - Current Balance.\n\n"
            "4. Recommendation Priorities\n"
            "- Critical: Current balance is zero, or Days Cover is less than 3 days.\n"
            "- High: Days Cover is less than 7 days.\n"
            "- Medium: Days Cover is less than 14 days.\n"
            "- Low: Days Cover is 14 days or more."
        ),
        "faqs": [
            {
                "question": _("What if a SKU has no historical sales data?"),
                "answer": _("If no sales are found within the lookback window, the daily sales rate defaults to 0. In this case, replenishment will trigger if the current stock is below the safety stock setting, recommending a quantity up to the safety stock level.")
            },
            {
                "question": _("Does the engine automatically place Purchase Orders?"),
                "answer": _("No. SMRITI constitution requires human approval for all business actions. Recommendations are populated in the Purchase Terminal where managers can review and submit them.")
            },
            {
                "question": _("Where do I configure Lead Time and Safety Stock?"),
                "answer": _("Go to the SMRITI Master Data page and open SMRITI PSV Reorder Rules to set up rules for specific variants, item groups, or companies.")
            }
        ]
    },
    "dead_stock_recovery": {
        "title": _("Dead Stock Recovery Workflows"),
        "category": "Analytics Guides",
        "description": _("Strategies and system tools to recover capital locked in dead inventory."),
        "about": _("This guide explains the SMRITI stock redistribution engine, and how it matches slow-moving excess stock with high-velocity shortage zones."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI Capital Optimizer"),
            "quote": _("Dead stock is simply inventory in the wrong place. Redistribution brings it back to life.")
        },
        "content": _(
            "SMRITI Retail OS includes an intelligent Redistribution Engine to recover capital locked in slow-moving or dead stock by transferring it to branches experiencing active demand.\n\n"
            "1. Weeks of Cover (WoC) Classification\n"
            "The engine analyzes sales velocity over the past 28 days for each SKU at each warehouse/location to determine Weeks of Cover (WoC = current balance / weekly sales average).\n\n"
            "2. Identifying Sources and Sinks\n"
            "- Sources (Excess Stock): Locations where WoC exceeds the configured 'Healthy WoC' threshold (default 8 weeks). The excess qty is: balance - (Healthy WoC * velocity).\n"
            "- Sinks (Shortage Stock): Locations where WoC falls below the 'Critical WoC' threshold (default 2 weeks). The shortage qty is: (Healthy WoC * velocity) - balance.\n\n"
            "3. Geographic Matching Scope\n"
            "To minimize freight costs and logistical friction, the redistribution engine matches sources and sinks within a configured geographic scope in SMRITI PSV Settings:\n"
            "- Same Territory: Source and sink must share the exact same territory.\n"
            "- Same Region: Source and sink must share the same region.\n"
            "- All: Matches globally across all company warehouses.\n\n"
            "4. Suggested Transfers\n"
            "The engine matches excess sources with shortage sinks for the same SKU. The suggested transfer quantity is the minimum of the source's excess and the sink's shortage (min(source_excess, sink_shortage)), sorted by quantity in descending order."
        ),
        "faqs": [
            {
                "question": _("How do I execute a suggested redistribution transfer?"),
                "answer": _("Managers can view suggestions in the PSV Dashboard. Clicking 'Initiate Transfer' generates a pre-filled Stock Entry (Material Transfer) in Draft state for manager review.")
            },
            {
                "question": _("Can I exclude certain stores from being sources of excess stock?"),
                "answer": _("Yes. Warehouses marked as inactive or designated as showroom/flagship locations in SMRITI settings can be excluded from redistribution scans.")
            },
            {
                "question": _("What if a SKU has zero sales velocity everywhere?"),
                "answer": _("If velocity is 0 globally, the WoC becomes 999 days, classifying it as dead stock. The engine will not suggest transfers since there is no sink. Instead, the SKU will be highlighted for clearance promotions.")
            }
        ]
    },
    # Operations Guides
    "store_opening_closing": {
        "title": _("Store Opening & Closing Checklist"),
        "category": "Operations Guides",
        "description": _("Daily operational procedures for opening and closing store registers."),
        "about": _("This guide explains daily cashier shifts opening, cash drawer reconciliation, sales tracking, and manager PIN override protocols during shift closure."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI Store Operations Director"),
            "quote": _("Tight cash drawer controls and manager audit trails ensure daily financial integrity at the POS.")
        },
        "content": _(
            "SMRITI Retail OS enforces disciplined cashier shift management. Every day begins and ends with cash drawer reconciliation and shift logging.\n\n"
            "1. Shift Opening Checklist\n"
            "At start of shift, the cashier selects their POS Profile and logs the opening amount in the drawer for each payment mode (e.g. Cash, Card, UPI). Submitting the opening checklist creates a submitted POS Opening Entry, which activates the billing terminal.\n\n"
            "2. Shift Summary and Sales Tracking\n"
            "During the shift, the system tracks all sales transactions. When the cashier clicks 'Close Shift', SMRITI compiles a shift summary detailing:\n"
            "- Total sales value and invoice count.\n"
            "- Expected closing amounts per payment mode (calculated as: Opening Amount + Sales Amount).\n\n"
            "3. Shift Closing Reconciliation\n"
            "The cashier performs a physical count of cash and receipts and enters the actual closing amounts. The system calculates the variance (actual amount - expected amount).\n\n"
            "4. Manager PIN Override\n"
            "If the cash variance exceeds the configured validation threshold (e.g., Rs. 500), the cashier terminal locks. A Store Manager or System Manager must enter their dedicated PIN (`custom_smriti_pin`) to authorize the override. The override is saved as an audit comment on the shift record."
        ),
        "faqs": [
            {
                "question": _("Where is the cash variance threshold configured?"),
                "answer": _("Managers can set the variance threshold via the POS Settings page in the system console, using the 'pos_closing_entry_validation_amount' parameter.")
            },
            {
                "question": _("What happens if a manager enters an incorrect PIN multiple times?"),
                "answer": _("To prevent brute-force attacks, the manager PIN verification system limits overrides to 5 failed attempts, after which it locks out the user for 10 minutes and logs an error.")
            },
            {
                "question": _("Can a cashier open multiple shifts simultaneously?"),
                "answer": _("No. The system strictly restricts cashiers to a single open shift per POS profile. Active shifts must be formally closed before a new shift can be opened.")
            }
        ]
    },
    "billing_cashier_workflows": {
        "title": _("Billing & Cashier Workflows"),
        "category": "Operations Guides",
        "description": _("Standard operating procedures for billing, POS operations, and customer checkouts."),
        "about": _("This guide details the SMRITI billing terminal, item scanning, hold/recall functionality, manager overrides, and tax compliance workflows."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI POS Expert"),
            "quote": _("A fast, secure checkout experience is the final and most critical point of contact with the customer.")
        },
        "content": _(
            "The SMRITI Billing Terminal provides an optimized interface for cashiers to process transactions, manage customer profiles, and apply returns.\n\n"
            "1. Scanned Barcode Handling\n"
            "Scanning a barcode fetches the retail product's details instantly, including standard rate, MRP, GST rate, and standard unit of measure (UOM). If a barcode is not available, the system allows searching by item code or description.\n\n"
            "2. Hold and Recall Bills\n"
            "If a customer needs to pause checkout, the cashier can hold the bill. The cart is saved as a Draft POS Invoice (flagged as 'custom_is_held' and linked to the cashier's user ID). This frees up the terminal for the next customer. Held bills can be recalled and loaded back into the active cart at any time.\n\n"
            "3. Invoice Submissions and Fallback\n"
            "- If a shift is open: Submitting a bill creates a POS Invoice linked to the current shift.\n"
            "- If no shift is open: The system falls back to creating a standard Sales Invoice with stock updates enabled (`update_stock = 1`), allowing back-office sales without drawer limits.\n"
            "- Credit Sales: Selecting the 'On Credit' payment option submits the invoice without immediate payment, logging the total amount under Customer Outstanding.\n\n"
            "4. Voiding and Manager Override\n"
            "Security-sensitive actions—such as voiding a scanned item row, clearing the entire cart, or applying custom discounts—require manager verification via the manager PIN overlay."
        ),
        "faqs": [
            {
                "question": _("How are sales returns processed at the register?"),
                "answer": _("Cashiers can select 'Sales Return', enter the original invoice number, and create a return invoice. This automatically processes stock receipts back into the warehouse and issues a credit note or cash refund.")
            },
            {
                "question": _("Does SMRITI support multiple payment modes for a single invoice?"),
                "answer": _("Yes. Split payments are fully supported. Cashiers can distribute the grand total across cash, card, and digital wallets within the checkout panel.")
            },
            {
                "question": _("How are prices retrieved in the billing terminal?"),
                "answer": _("The terminal checks the selling price list linked to the cashier's active POS Profile. MRP and standard retail rates are synchronized directly from the Item Price records.")
            }
        ]
    },
    # Purchasing Guides
    "vendor_management_po": {
        "title": _("Vendor Management & Purchase Orders"),
        "category": "Purchasing Guides",
        "description": _("How to manage vendors, purchase agreements, and issue Purchase Orders."),
        "about": _("This guide explains the SMRITI purchase terminal, self-healing item variant auto-creation, GRN submissions, batch tracking, and supplier returns."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI Procurement Specialist"),
            "quote": _("Automating variant creation and batch tracking reduces administrative workload and supplier disputes.")
        },
        "content": _(
            "SMRITI Retail OS streamlines procurement via the Purchase Terminal, facilitating purchase order creation, goods receipt notes (GRN), and purchase returns.\n\n"
            "1. Role Restrictions\n"
            "While cashiers can view open POs and GRNs, only users with 'SMRITI Store Manager' or 'System Manager' roles are permitted to submit purchase transactions.\n\n"
            "2. Self-Healing Variant Auto-Creation\n"
            "When creating a Purchase Order, if a footwear variant SKU is entered (following the 'Style-Color-Size' naming convention) that does not exist in the database, the system automatically creates the Item record. It configures standard attributes:\n"
            "- Sets standard rate and default MRP (1.5x cost).\n"
            "- Links selling price lists (Standard Selling and MRP).\n"
            "- Attaches default HSN codes and 18% GST tax templates.\n"
            "- Associates any uploaded variant product images.\n\n"
            "3. Goods Receipt Note (GRN)\n"
            "Creating a Purchase Receipt registers stock inflow. GRNs can be created against a specific Purchase Order (which updates the PO's received quantity) or as standalone receipts. If the item requires batches, SMRITI automatically creates or links a Batch record, supporting batch numbers and expiry dates.\n\n"
            "4. Purchase Returns\n"
            "If stock is damaged or incorrect, managers can submit a Purchase Return directly linked to the original GRN, reversing stock balances and updating ledger balances."
        ),
        "faqs": [
            {
                "question": _("How does the system calculate the pending quantity on a Purchase Order?"),
                "answer": _("Pending quantity is computed as: PO Quantity - Received Quantity. Once the pending quantity for all item lines reaches zero, the PO status automatically updates to 'Completed'.")
            },
            {
                "question": _("Where are uploaded variant images stored?"),
                "answer": _("Images uploaded during PO creation are saved in the system's files module and linked directly to the newly created Item variant card.")
            },
            {
                "question": _("Can I return a partial quantity from a GRN?"),
                "answer": _("Yes. SMRITI allows editing the return document's items list to specify the exact quantity being returned to the vendor.")
            }
        ]
    },
    # Administration Guides
    "user_roles_permissions": {
        "title": _("User Roles & Operational Permissions"),
        "category": "Administration Guides",
        "description": _("Managing users, roles, and functional permissions in SMRITI OS."),
        "about": _("This guide explains user roles, route restrictions, manager approval flows, and custom PIN security controls."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI Security Director"),
            "quote": _("Granular role boundaries protect sensitive reports and ensure accountability at all operational levels.")
        },
        "content": _(
            "SMRITI Retail OS employs a strict role-based access control (RBAC) framework to restrict access to sensitive configurations, financial reports, and high-impact transaction submissions.\n\n"
            "1. Core Roles and Scope\n"
            "- SMRITI Cashier: Granted access to POS billing, shift opening/closing, product catalogs, payments, and sales invoices. Restricted from administrative and purchasing functions.\n"
            "- SMRITI Store Manager: Full access to store operations, including stock audits, supplier management, purchase orders, GRNs, sales uploads, schemes, and PSV analytics.\n"
            "- System Manager: Global superuser permission to manage backups, GPG security, user accounts, system hooks, and database settings.\n\n"
            "2. Route and Page Access Enforcements\n"
            "Access is enforced at the router layer. For example:\n"
            "- SMRITI Reports Center and PSV Dashboard are restricted to Store Managers and System Managers.\n"
            "- Opening Balances and Security settings are restricted to Store Managers and System Managers.\n"
            "If an unauthorized user attempts to access these routes, the system intercepts the request and displays an 'Access Denied' alert.\n\n"
            "3. Manager PIN Controls (`custom_smriti_pin`)\n"
            "Instead of sharing login passwords at the POS terminal, SMRITI implements dedicated manager PIN verification. Store Managers and System Managers set a 4\u20136 digit numeric PIN via the Security Center (/security → Users tab → \ud83d\udd22 Set PIN button). This PIN is used exclusively for POS override actions (voiding rows, applying discounts, closing shifts with variance). The PIN is:\n"
            "- Stored as a hashed credential in the Frappe __Auth table (fieldname: custom_smriti_pin), separate from the login password.\n"
            "- Validated using Frappe's check_password() with constant-time comparison.\n"
            "- Rate-limited to 5 failed attempts per 10-minute window (Redis-backed).\n"
            "- Audited: every successful override is logged as a Comment on the target invoice with the manager's identity.\n\n"
            "4. PIN Management in Security Center\n"
            "The Security Center (Administration → Security & Workflow Center → Users tab) provides three action buttons per user row:\n"
            "- \u270f\ufe0f Edit Roles: Modify role assignments and role profiles.\n"
            "- \ud83d\udd11 Reset Login Password: Change the user's login password.\n"
            "- \ud83d\udd22 Set POS Override PIN: Opens a dedicated modal with PIN entry, confirmation, and show/hide toggle. Only visible for users with SMRITI Store Manager or System Manager roles. Administrators can also clear a manager's PIN to revoke override access."
        ),
        "faqs": [
            {
                "question": _("How do I assign a role to a new store employee?"),
                "answer": _("System Managers can open the User master page in the system console, select the user account, and check the desired role (e.g., 'SMRITI Cashier' or 'SMRITI Store Manager') in the Roles table.")
            },
            {
                "question": _("How does a manager set or change their POS Override PIN?"),
                "answer": _("Go to Security & Workflow Center → Users tab. Find the manager's row and click the \ud83d\udd22 (PIN) button. Enter a 4\u20136 digit numeric PIN, confirm it, and click 'Set PIN'. The PIN is hashed and stored securely. Only users with SMRITI Store Manager or System Manager roles will see the PIN button.")
            },
            {
                "question": _("Can an Administrator revoke a manager's PIN?"),
                "answer": _("Yes. Administrators can click the \ud83d\udd22 PIN button on any manager row and use the 'Clear PIN' option in the modal footer. This removes the PIN hash, preventing the manager from performing PIN-based overrides until a new PIN is set.")
            },
            {
                "question": _("How are unauthorized page access attempts handled?"),
                "answer": _("SMRITI logs all access denied exceptions under SMRITI Security Logs, capturing the username, target page route, timestamp, and client IP address.")
            }
        ]
    },
    "branding_theme_setup": {
        "title": _("Branding & Store Theme Setup"),
        "category": "Administration Guides",
        "description": _("Customizing store themes, logos, receipt templates, and local branding settings."),
        "about": _("This guide explains SMRITI whitelabel configuration, website context branding overrides, about dialog patching, and custom css overrides."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI Whitelabel Coordinator"),
            "quote": _("A unified corporate brand builds professionalism and trust with clients and franchise partners.")
        },
        "content": _(
            "SMRITI Retail OS is designed for full whitelabeling, ensuring that all user-facing interfaces, portals, and print formats are branded under SMRITI with zero system framework mentions.\n\n"
            "1. Website Context Override (`website_context.py`)\n"
            "The system overrides website context generation. When any portal or web page renders, Jinja templates are injected with:\n"
            "- Custom brand name: 'SMRITI Retail OS'.\n"
            "- Logo assets: Logo and favicon URL pointing to '/assets/smriti_retail_os/images/logo.svg'.\n"
            "- Footers and links: External platform footer references are completely disabled.\n\n"
            "2. Versioning and About Dialog Overrides (`branding_api.py`)\n"
            "To prevent exposure in support dialogues, server-side methods intercept version queries. It maps default system modules to SMRITI product names:\n"
            "- ERPNbook is displayed as: 'SMRITI Retail OS'.\n"
            "- Frappe Framework is displayed as: 'SMRITI Framework'.\n"
            "- HRMS is displayed as: 'SMRITI HR'.\n"
            "- Payments is displayed as: 'SMRITI Payments'.\n\n"
            "3. Styling Overrides (`smriti_branding.css`)\n"
            "A global corporate styling sheet is loaded on all views. This enforces the Navy Blue (#1A2B5C) and Royal Blue (#2563EB) color palette, standardizes typography, hides default platform logos, and styles custom desktop shortcuts.\n\n"
            "4. Footer Branding Cleanup\n"
            "To comply with SMRITI UI-first policies, user-facing standalone routes (such as the Formula Registry and Business Dictionary) have been stripped of footer branding mentioning external platform names, ensuring a clean, fully whitelabeled interface."
        ),
        "faqs": [
            {
                "question": _("Where are print receipt formats configured?"),
                "answer": _("Receipt print templates can be customized via the SMRITI Print Templates page, where managers can edit HTML/CSS templates, add logos, and define field placements.")
            },
            {
                "question": _("Do branding overrides affect API payloads or developers?"),
                "answer": _("No. Overrides are purely presentational at the UI and versioning layers. The underlying database schemas, DocTypes, and API routes remain stable and fully standard.")
            },
            {
                "question": _("How can I change the primary company logo?"),
                "answer": _("The logo is resolved from `/assets/smriti_retail_os/images/logo.svg`. To update it, replace the logo file in the assets directory and run asset synchronization.")
            }
        ]
    },
    "backup_security": {
        "title": _("Backup Security & Key Recovery"),
        "category": "Administration Guides",
        "description": _("Guide to GPG AES-256 backup encryption, security banners, and dual-custodian recovery."),
        "about": _("This guide explains the SMRITI enterprise backup security system, GPG AES-256 encryption, and dual-custodian key recovery protocol."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI Security Officer"),
            "quote": _("Protecting customer and transaction history is as critical as securing the physical store inventory.")
        },
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
        "about": _("This guide outlines the SMRITI Audit Reports framework, including user activity tracking and address modification history logging."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI Security Officer"),
            "quote": _("Complete transparency and auditability build the foundation of reliable retail scaling.")
        },
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
            },
            {
                "question": _("What is tracked in the Address Change Log?"),
                "answer": _("It tracks all creations, updates, or deletions of Company, Customer, Supplier, and Warehouse addresses, showing the modified field, the old value, and the new value.")
            },
            {
                "question": _("Can I export these logs for external auditing?"),
                "answer": _("Yes, you can click the 'Export' button on the SMRITI Reports toolbar to download the current filtered view in CSV or Excel format.")
            }
        ]
    },
    "license_key_management": {
        "title": _("License Key Management & Activation"),
        "category": "Administration Guides",
        "description": _("How SMRITI license keys work, offline validation, and the activation workflow."),
        "about": _("This guide explains the SMRITI License Key format (SMRT keys), offline HMAC-SHA256 validation, tier extraction, and the Registration tab activation flow."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI Licensing Authority"),
            "quote": _("Self-describing signed keys eliminate server dependencies while maintaining cryptographic integrity.")
        },
        "content": _(
            "SMRITI Retail OS uses structured, self-describing license keys that embed all activation metadata and are cryptographically signed for offline validation.\n\n"
            "1. SMRITI Key Format\n"
            "License keys follow the format: SMRT-{VERSION}-{PAYLOAD}-{SIGNATURE}\n"
            "- VERSION: Key format version (currently '1').\n"
            "- PAYLOAD: Base64URL-encoded JSON containing: customer_id (cid), license tier (tier: Starter/Professional/Enterprise), expiry date (exp: YYYY-MM-DD), installation binding (iid: UUID or '*' for floating), and issuer tag (iss: ERPNBOOK).\n"
            "- SIGNATURE: First 16 hex characters of HMAC-SHA256(secret, 'SMRT|version|payload').\n\n"
            "2. Offline Validation Flow\n"
            "When a key is entered in the Registration tab and 'Activate License' is clicked:\n"
            "- Step 1: Format check — key must match the SMRT-{v}-{payload}-{sig} regex pattern.\n"
            "- Step 2: Signature verification — HMAC-SHA256 is computed using the server's license secret and compared (constant-time) to the embedded signature.\n"
            "- Step 3: Payload decode — the base64url JSON is decoded and validated (required fields, valid tier, ERPNBOOK issuer).\n"
            "- Step 4: Expiry check — the embedded expiry date is compared against today's date.\n"
            "- Step 5: Installation binding — if the key specifies a UUID (not '*'), it must match this installation's installation_id.\n"
            "- Step 6: Metadata extraction — tier, expiry_date, and customer_id are extracted from the key and applied to the license record, overriding form fields.\n\n"
            "3. Secret Management\n"
            "The HMAC signing secret is resolved in order:\n"
            "- Production: 'smriti_license_secret' in site_config.json (recommended).\n"
            "- Container/CI: SMRITI_LICENSE_SECRET environment variable.\n"
            "- Development: Built-in fallback secret (logged as a warning).\n\n"
            "4. Activation Results\n"
            "On successful activation, the license record is updated with the embedded tier, expiry, and customer_id. The state machine recalculates license_status (Active/Warning/Grace Period) and license_health automatically. Activity and validation history entries are appended for audit."
        ),
        "faqs": [
            {
                "question": _("Where do I get a SMRITI license key?"),
                "answer": _("License keys are issued by ERPNBook.com. Contact support@erpnbook.com or your account manager to receive a signed key for your subscription tier.")
            },
            {
                "question": _("Can I use the same license key on multiple installations?"),
                "answer": _("Only if the key was issued as a floating key (installation binding = '*'). Keys bound to a specific installation UUID will be rejected on other installations.")
            },
            {
                "question": _("What happens if my license key expires?"),
                "answer": _("The system enters a Grace Period (default 7 days) with restricted feature access. After the grace period, the license status changes to 'Expired' and full system access is blocked until a renewed key is activated.")
            },
            {
                "question": _("How do I set the production license secret?"),
                "answer": _("Add 'smriti_license_secret' to your site_config.json file: {\"smriti_license_secret\": \"your-secret-here\"}. This must match the secret used by ERPNBook to generate your keys.")
            },
            {
                "question": _("Is an internet connection required for license activation?"),
                "answer": _("No. Phase-1 validation is entirely offline. The HMAC signature is verified locally using the shared secret. Phase-2 will add optional online PKI verification for enhanced security.")
            }
        ]
    },
    "pivot_matrix_builder": {
        "title": _("Pivot Matrix Builder & Custom Reports"),
        "category": "Analytics Guides",
        "description": _("Guide to using the drag-and-drop Pivot Matrix Builder and column reordering in SMRITI Reports."),
        "about": _("This guide outlines the SMRITI Pivot Matrix Builder and drag-and-drop report layout personalization engine."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI Analytics Coordinator"),
            "quote": _("Dynamic data visibility transforms raw transactions into actionable store decisions.")
        },
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
            },
            {
                "question": _("How do I clear the active pivot layout and return to the standard report grid?"),
                "answer": _("Simply toggle the 'Pivot View' button off in the report toolbar, or click the 'Reset Pivot' button within the builder panel to clear all active dropzones.")
            },
            {
                "question": _("Can I apply multiple fields to Rows or Columns?"),
                "answer": _("Yes. You can drag multiple tags into the Rows or Columns zones. The builder will group them sequentially, creating a hierarchical multi-level pivot grid.")
            }
        ]
    },
    "dashboard_customization": {
        "title": _("Dashboard Customization & Layouts"),
        "category": "Analytics Guides",
        "description": _("Learn how to personalize your SMRITI Home and PSV dashboards using drag-and-drop layouts."),
        "about": _("This guide explains the SMRITI Dashboard Customization framework and widget order persistence model."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI UI-UX Designer"),
            "quote": _("An interface tailored to a manager's immediate focus dramatically improves daily store productivity.")
        },
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
            },
            {
                "question": _("How do I reset the dashboard back to the default system layout?"),
                "answer": _("While in edit mode (after clicking 'Customize Layout'), click the 'Reset Layout' button that appears in the topbar. This will clear the customization from local storage and restore the standard sequence.")
            },
            {
                "question": _("Does layout customization work on mobile devices?"),
                "answer": _("Yes. SMRITI dashboards support touch drag-and-drop events on mobile. However, due to limited screen width, all widget cards stack vertically on small viewports by default.")
            }
        ]
    },
    "go_live_readiness": {
        "title": _("Go-Live Readiness Checklist"),
        "category": "Administration Guides",
        "description": _("Verify and resolve system prerequisites, product catalogue requirements, and tax configurations before launch."),
        "about": _("This guide explains SMRITI's real-time system readiness checklist, required parameters, and how to resolve catalogue and tax configuration blockers."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI Release Manager"),
            "quote": _("A disciplined go-live validation checks all operational vectors so store billing works flawlessly on day one.")
        },
        "content": _(
            "SMRITI Retail OS implements a rigorous Go-Live Readiness Checklist under Administration to verify all store prerequisites and operational configurations before launching production operations.\n\n"
            "1. Real-Time Validation Modules\n"
            "The check engine scans 14 distinct system checks grouped into five core areas:\n"
            "- Licensing: Validates SMRITI License Activation and verifies the License Signing Secret in site_config.json.\n"
            "- Store Setup: Verifies Default Company configuration, Store Warehouses, and active POS Profiles.\n"
            "- Users & Security: Ensures SMRITI Cashier and Store Manager roles are assigned, Manager PINs are set, and validates Backup Encryption.\n"
            "- Catalogue & Pricing: Checks Selling Price Lists, Customer Masters, active Product Catalogue, and GST / Tax Templates.\n"
            "- Infrastructure: Confirms Outgoing Email SMTP accounts are configured for billing notifications.\n\n"
            "2. Critical Catalog Blockers\n"
            "To prevent checkout failures, the system blocks go-live if the Product Catalogue contains zero sellable items. To satisfy this check, you must load at least 5 sellable products in the Item Master, ensuring:\n"
            "- Disabled is set to 'No'.\n"
            "- Is Sales Item and Maintain Stock are set appropriately.\n"
            "- Selling Prices are assigned via a valid Selling Price List.\n"
            "- Item Groups are configured.\n\n"
            "3. India GST Compliance Setup\n"
            "For automated GST calculations at POS, the system checks for tax templates. If none are found, a warning is raised. Ensure you:\n"
            "- Create standard GST templates (5%, 12%, 18%, 28%) via Sales Taxes and Charges Templates.\n"
            "- Map item-wise GST rates using the India Compliance HSN codes.\n"
            "- Assign the default tax templates in the active POS Profile.\n\n"
            "4. Backup Encryption & Security\n"
            "To secure store history, SMRITI checks for backup encryption. While categorized as a recommended INFO warning (non-blocking), configuring GPG AES-256 backup encryption under Security Settings is recommended before final production cutover."
        ),
        "faqs": [
            {
                "question": _("What constitutes a critical go-live blocker?"),
                "answer": _("A status of 'FAIL' in any check (such as 0 sellable items or missing POS profiles) will block go-live, marking the overall status as 'NOT READY'. Warnings ('WARN') display a status of 'CAUTION', while 'INFO' items do not block pilot rollout.")
            },
            {
                "question": _("How is the Go-Live Readiness Score computed?"),
                "answer": _("The score represents the percentage of passed checks relative to the total number of validation checks. A score of 90%+ with zero critical failures is required for production cutover approval.")
            },
            {
                "question": _("Why does the system require at least 5 items to pass the catalogue check?"),
                "answer": _("A standard retail rollout requires a verified product catalogue. Finding less than 5 items flags a caution warning ('WARN') suggesting you import the full catalogue, while 0 items triggers a critical 'FAIL' blocker.")
            },
            {
                "question": _("How do I re-run the readiness checks after fixing an issue?"),
                "answer": _("Open the Go-Live Readiness page under Administration and click the 'Re-run Checks' button in the topbar. The backend will re-evaluate all system parameters in real-time.")
            }
        ]
    },
    "cge_explorer": {
        "title": _("Customer Growth Engine (CGE) Explorer & Console"),
        "category": "Administration Guides",
        "description": _("Detailed guide to managing promotional campaigns, loyalty rules, benefit instruments, and wallets using the dynamic config-driven explorer."),
        "about": _("This guide explains the dynamic schema-driven CGE Explorer console, role-based access controls, child table structures, audit logs, and delete protection."),
        "author": {
            "name": "SMRITI Documentation Team",
            "title": _("Lead Architect & SMRITI Loyalty Optimizer"),
            "quote": _("Dynamic configuration-driven loyalty models decouple operational rules from code, allowing rapid retail scaling.")
        },
        "content": _(
            "The SMRITI Customer Growth Engine (CGE) Explorer provides a unified console to manage 12 distinct configuration and transactional modules without exposing raw backend database views or standard ERPNext desk layouts. This design keeps the retail experience fully whitelabeled and aligned with the SMRITI UI/UX constitution.\n\n"
            "1. Decoupled Architecture & Route Mapping\n"
            "Each of the 12 CGE modules maps to the canonical standalone template `/cge_generic.html` via route aliases configured in `hooks.py`. The frontend routes are: \n"
            "- /cge-benefit-instruments: Manage loyalty points, cashback, vouchers, and store credits.\n"
            "- /cge-membership-tiers: Configure customer tiers based on spending thresholds.\n"
            "- /cge-loyalty-programs: Track overall program configurations.\n"
            "- /cge-campaigns: Track marketing campaigns, budget allocations, and caps.\n"
            "- /cge-promotion-rules: Edit promotional rules and logic.\n"
            "- /cge-coupon-rules: Manage discount codes and coupon rules.\n"
            "- /cge-loyalty-rules: Configure points earn/redeem multipliers.\n"
            "- /cge-benefit-wallets: Operational view of customer wallet balances.\n"
            "- /cge-customer-benefit-profiles: View customer loyalty registrations.\n"
            "- /cge-benefit-resolution-policies: Map order-of-precedence rules.\n"
            "- /cge-liability-snapshots: System-generated snapshots of outstanding financial liabilities.\n"
            "- /cge-benefit-audit-logs: Detailed records of manual adjustments and state changes.\n\n"
            "2. Whitelisted API Security Layer\n"
            "All CRUD actions are routed through whitelisted Python controllers in `cge_api.py` (`get_cge_generic_fields`, `get_cge_generic_list`, `get_cge_generic_doc`, `save_cge_generic_doc`, and `delete_cge_generic_doc`). To protect against SQL injection and unauthorized schema exploitation, the backend strictly validates requests against an allowlist of permitted CGE DocTypes. Any attempt to query or edit a DocType outside this list triggers a validation error and aborts immediately.\n\n"
            "3. Config-Driven Dynamic Form Renderer\n"
            "SMRITI reads active field metadata dynamically to construct form views. It automatically handles inputs for fields like Link dropdowns, Select values, Numbers, Strings, and Dates. When a field type is identified as a Table, the console automatically renders an interactive editable grid. This allows administrators to manage complex sub-records like sequence priorities and multiplier details in a simple, streamlined interface.\n\n"
            "4. Role Enforcement & Delete Protection\n"
            "To prevent tampering with promotional budgets and loyalty balances, access is restricted to SMRITI Store Manager, System Manager, and Administrator roles. Every record creation, modification, or deletion triggers a secure log in SMRITI's global audit trail. Deleting active configurations is safeguarded by backend referential check logic to prevent orphan records or data inconsistencies."
        ),
        "faqs": [
            {
                "question": _("Who has permission to access the CGE Explorer and make changes?"),
                "answer": _("Only users assigned the 'SMRITI Store Manager', 'System Manager', or 'Administrator' roles can access these explorers. Cashiers and standard staff are blocked from loading these routes.")
            },
            {
                "question": _("How are child tables (like Benefit Resolution Sequence Details) managed in the form?"),
                "answer": _("The console dynamically reads child table schemas and renders them as editable grids. Users can add, edit, or delete rows in the grid. When saving, the entire parent-child hierarchy is validated and sent as a single transaction-isolated payload to prevent partial updates.")
            },
            {
                "question": _("What happens if a user tries to delete a CGE configuration doc?"),
                "answer": _("When a delete request is submitted, the backend validates if the record is linked to other active transactions (e.g., active campaigns or wallets). If referential integrity checks pass, the record is removed, and a SMRITI Audit event is logged containing the operator's ID, timestamp, and details. If it is linked to active transactions, deletion is blocked to prevent data corruption.")
            },
            {
                "question": _("Is my transaction data safe from unauthorized API queries?"),
                "answer": _("Yes. The generic API endpoints strictly check the target DocType against the ALLOWED_CGE_DOCTYPES whitelist. If an attacker tries to pass a non-CGE DocType (like 'User' or 'Sales Invoice') to the generic CRUD endpoint, it throws an Access Denied exception and terminates the request.")
            },
            {
                "question": _("Does updating a campaign budget affect active checkouts instantly?"),
                "answer": _("Yes. The CGE Checkout validation engine reads campaign configuration and budget balances in real-time. Once a budget cap is reached, or if a campaign is disabled in the explorer, the checkout engine will automatically stop applying that discount at the POS registers.")
            }
        ]
    },
    "formula_registry": {
        "title": _("Formula Registry (DOC-02)"),
        "category": "Governance Guides",
        "description": _("Central repository for managing mathematical and forecasting formulas used in SMRITI OS."),
        "about": _("This guide explains the SMRITI Formula Registry, how to register new mathematical formulas, and the audit and caching layers."),
        "author": {
            "name": "Jawahar R. Mallah",
            "title": _("Founder & Chief Architect, AITDL"),
            "quote": _("Standardized formulas prevent black-box decision making and build absolute operational trust.")
        },
        "content": _(
            "The SMRITI Formula Registry is the core mathematical ledger of SMRITI Retail OS. It maps all key calculated metrics (like Weeks of Cover, Sales Velocity, and Dead Stock Score) to cryptographically traceable definitions.\n\n"
            "1. Config-Driven Formula Schema\n"
            "Each formula definition is managed under the `SMRITI Formula Definition` DocType. Records contain the formula ID, mathematical expression, variables map, business meaning, worked example, and interpretation bands.\n\n"
            "2. Redis Caching Layer\n"
            "To support high-concurrency and sub-second load times, formulas are cached in Redis under the key `smriti:explain:{formula_id}:{version}` with a TTL of 3600 seconds (1 hour). Subsequent loads bypass database queries.\n\n"
            "3. Access Auditing\n"
            "Every request to fetch a formula (hit or miss) is recorded in the `SMRITI PSV Activity Log` with `event_type = 'FORMULA_EXPLAINED'` to trace operational usage."
        ),
        "faqs": [
            {
                "question": _("Can store managers modify active formulas?"),
                "answer": _("No. SMRITI Constitution restricts formula changes to Administrator and AITDL Chief Architect accounts to prevent tampering with core metrics.")
            },
            {
                "question": _("What happens if a formula is missing in the registry?"),
                "answer": _("The dashboard rendering engine enforces strict validation checks. Any computed KPI must exist in the registry, or the system blocks execution to prevent untraceable math.")
            }
        ]
    },
    "business_dictionary": {
        "title": _("Business Dictionary (DOC-04)"),
        "category": "Governance Guides",
        "description": _("Searchable business glossary mapping key retail terms, relationships, and Hinglish definitions."),
        "about": _("This guide describes the SMRITI Business Dictionary, the glossary schema, seeding, and relationships mapping."),
        "author": {
            "name": "Jawahar R. Mallah",
            "title": _("Founder & Chief Architect, AITDL"),
            "quote": _("When teams speak the same language, from cashiers to executives, operational errors drop to zero.")
        },
        "content": _(
            "The SMRITI Business Dictionary is the central glossary mapping all critical retail operational terms (such as PSA, PSV, PDT, WOC, and Size Curves).\n\n"
            "1. Localized Hinglish Explanations\n"
            "To assist ground-level operators who may find pure English technical definitions confusing, the glossary includes localized Hinglish descriptions blending English retail vocabulary with Hindi sentence syntax.\n\n"
            "2. Relational Lineage Maps\n"
            "Glossary terms are mapped to related terms and related formulas via custom child doctypes `SMRITI Related Term` and `SMRITI Related Formula`, building a comprehensive lineage network.\n\n"
            "3. Search & Category Filters\n"
            "The standalone dictionary UI (/smriti-dictionary) features category-based filters and real-time fuzzy search to quickly locate terms, common mistakes, and FAQs."
        ),
        "faqs": [
            {
                "question": _("How are terms seeded into the dictionary?"),
                "answer": _("SMRITI seeds 20 default retail terms using a 2-phase migration patch `seed_default_terms.py` to prevent validation errors from forward-referenced relationship links.")
            },
            {
                "question": _("How are glossary accesses logged?"),
                "answer": _("Every glossary detail lookup logs a `DICTIONARY_ACCESSED` activity event in the SMRITI PSV Activity Log for compliance audits.")
            }
        ]
    },
    "pdt_dashboard": {
        "title": _("Product Digital Twin (PDT) Dashboard"),
        "category": "Analytics Guides",
        "description": _("Predictive stock status tracking, sales velocity, and weeks of cover calculations per SKU."),
        "about": _("This guide explains the SMRITI Product Digital Twin (PDT), state machine definitions, and replenishment matching."),
        "author": {
            "name": "Jawahar R. Mallah",
            "title": _("Founder & Chief Architect, AITDL"),
            "quote": _("Moving store operations from reactive stock tracking to predictive inventory planning.")
        },
        "content": _(
            "The SMRITI Product Digital Twin (PDT) tracks the lifecycle and health of every SKU in the network, utilizing a predictive state machine.\n\n"
            "1. Predictive PDT States\n"
            "Each SKU Twin is classified dynamically based on inventory levels and sales velocity:\n"
            "- Stockout: Current stock is 0 or less.\n"
            "- Dead Stock: High risk of absolute stagnation based on inactivity period.\n"
            "- Overstock: Weeks of Cover (WoC) exceeds 12 weeks.\n"
            "- Critical: Weeks of Cover is less than 2 weeks.\n"
            "- Replenish Soon: Weeks of Cover is between 2 and 4 weeks.\n"
            "- Monitor: Weeks of Cover is between 4 and 6 weeks.\n"
            "- Healthy: Optimal stock cover of 6 to 12 weeks.\n\n"
            "2. Read Model & Redis Cache Layer\n"
            "To support high-frequency queries, PDT stats are cached in Redis at key `smriti:pdt:{company}:{party_stock_account}:{item_code}` with a 1-hour TTL, ensuring fast dashboard load times.\n\n"
            "3. State Transition Logs\n"
            "Every twin recalculation triggers state machine evaluations and logs transitions for audit trace validation."
        ),
        "faqs": [
            {
                "question": _("How often does the PDT recalculate?"),
                "answer": _("Recalculation is triggered automatically by downstream transactions (e.g. Sales Uploads, Physical Counts) or via the daily scheduled sweep. System managers can trigger a manual rebuild via the UI.")
            },
            {
                "question": _("What mathematical inputs drive the Weeks of Cover calculation?"),
                "answer": _("It divides current SKU stock by the weekly sales velocity. The velocity is computed using a 4-week lookback window to normalize seasonal or weekly demand variance.")
            }
        ]
    },
    "simulation_sandbox": {
        "title": _("Simulation Sandbox & Scenario Planning"),
        "category": "Analytics Guides",
        "description": _("Risk-free in-memory scenario modeling for discounts, velocity spikes, and lead time changes."),
        "about": _("Understand how to run simulation scenarios without altering active database ledger records."),
        "author": {
            "name": "Jawahar R. Mallah",
            "title": _("Founder & Chief Architect, AITDL"),
            "quote": _("Model business decisions before executing them on live ledger databases.")
        },
        "content": _(
            "The SMRITI Simulation Sandbox enables executives to model 'what-if' scenarios in-memory, analyzing how operational changes impact supply chain metrics.\n\n"
            "1. Sandbox Inputs\n"
            "Users can tweak three primary parameters:\n"
            "- Velocity Multiplier: Simulate demand spikes (e.g., 1.5x increase for holiday seasons).\n"
            "- Lead Time Days Override: Model supply chain disruptions or shipping delays.\n"
            "- Promotions & Pricing: Adjust pricing structures to see immediate impact on predicted stockout dates.\n\n"
            "2. Pure In-Memory Calculations\n"
            "The simulation runs entirely in memory without writing to active ledger tables (e.g., Stock Ledger Entries), protecting financial and inventory data from corruption.\n\n"
            "3. Actionable Recommendations\n"
            "The sandbox outputs simulated Weeks of Cover, expected stock-out dates, and recommended transfer/replenishment quantities."
        ),
        "faqs": [
            {
                "question": _("Can cashier users access the Simulation Sandbox?"),
                "answer": _("No. The sandbox is restricted to SMRITI Store Manager and System Manager roles due to its strategic and planning nature.")
            },
            {
                "question": _("How do I execute a simulation?"),
                "answer": _("Navigate to SMRITI Home → Operations → Simulation Sandbox, set your multipliers and targets, and click 'Execute Simulation'.")
            }
        ]
    },
    "cge_engine": {
        "title": _("Customer Grace Engine (CGE) Setup & Workflows"),
        "category": "Governance Guides",
        "description": _("Campaign management, promotion rules, coupon rules, loyalty rules, and liability snapshot auditing."),
        "about": _("Detailed operational guide for managing benefit instruments, membership tiers, wallets, and liability reconciliation."),
        "author": {
            "name": "Jawahar R. Mallah",
            "title": _("Founder & Chief Architect, AITDL"),
            "quote": _("Transparent promotions, predictable loyalty programs, and fully auditable liabilities.")
        },
        "content": _(
            "The Customer Grace Engine (CGE) is SMRITI's loyalty and promotions subsystem. It decouples complex marketing campaigns from ERPNext core ledgers.\n\n"
            "1. Key Components\n"
            "- Benefit Instruments: Coupons, loyalty points, cashback, and direct discounts.\n"
            "- Membership Tiers: Dynamic customer leveling (Silver, Gold, Platinum) with reward accelerators.\n"
            "- Benefit Wallets: Custodial store value trackers for customer loyalty points and pre-funded balances.\n\n"
            "2. Budget Reservation\n"
            "CGE locks loyalty point/coupon liabilities before invoice submission. The points/coupons are formalised when the invoice is submitted, or released back to the budget if the draft invoice is trashed.\n\n"
            "3. Liability Snapshots & Auditing\n"
            "To comply with financial disclosure requirements, CGE runs a daily job reconciling wallet balances and generating liability snapshots."
        ),
        "faqs": [
            {
                "question": _("How are CGE rules evaluated during checkout?"),
                "answer": _("The checkout payload bridge transmits the draft cart to the CGE rules engine, which evaluates eligible coupons and returns discounts to the register in real-time.")
            },
            {
                "question": _("Where are CGE liability reports accessed?"),
                "answer": _("Go to the CGE section in the SMRITI sidebar and click 'Liability Snapshots' or run CGE reports in the Reports Center.")
            }
        ]
    },
    "knowledge_center": {
        "title": _("Knowledge Center Portal"),
        "category": "Governance Guides",
        "description": _("Unified interface mapping user manuals, the business dictionary, formula registry, training center, and release notes."),
        "about": _("Understand the unified portal design for Sprint 4 and knowledge access governance."),
        "author": {
            "name": "Jawahar R. Mallah",
            "title": _("Founder & Chief Architect, AITDL"),
            "quote": _("Knowledge is power only when it is organized, transparent, and discoverable.")
        },
        "content": _(
            "The SMRITI Knowledge Center (/knowledge-center) is the unified discovery portal planned for Sprint 4.\n\n"
            "1. Core Purpose\n"
            "Instead of navigating separate pages for formulas, terms, and troubleshooting, the Knowledge Center will serve as a single hub to consume all documentation and reference tools.\n\n"
            "2. Consolidated Hub Components\n"
            "The portal will group and display:\n"
            "- Business Dictionary (DOC-04): Term search and definitions.\n"
            "- Formula Registry (DOC-02): Math expressions and worked examples.\n"
            "- Training Center: Interactive exercises and SOPs.\n"
            "- User Manuals: Multipage manuals and training guides.\n"
            "- Release Notes: Version change histories and feature logs."
        ),
        "faqs": [
            {
                "question": _("When will the unified Knowledge Center be fully built?"),
                "answer": _("The unified Knowledge Center portal is scheduled for deployment during Sprint 4 (Q3 2026). The menu item is currently reserved in the navigation sidebar.")
            }
        ]
    },
    "barcode_studio": {
        "title": _("Barcode Studio V2.4a Operations"),
        "category": "Operations Guides",
        "description": _("Warehouse barcode printing workspace, range loading, variant expansion, and print queue management."),
        "about": _("Detailed guide for SMRITI Barcode Studio V2.4a enhancements, including worksheet grids, mapping previews, and box modes."),
        "author": {
            "name": "Jawahar R. Mallah",
            "title": _("Founder & Chief Architect, AITDL"),
            "quote": _("High-volume warehouse operations demand frictionless barcode labeling and zero-touch variant generation.")
        },
        "content": _(
            "SMRITI Barcode Studio V2.4a introduces a widescreen 3-panel warehouse barcode printing workspace designed for high-throughput retail fulfillment.\n\n"
            "1. Article Range Loader & Variant Expansion\n"
            "Warehouse operators can load a range of sequential style codes (e.g., BBM-0001 to BBM-0100) using the Range Loader. For fashion retail, styles automatically expand into their size-color variant combinations (e.g., BBM-001 expands to S, M, L, XL variants) by scanning existing database records.\n\n"
            "2. Interactive Worksheet Grid\n"
            "The center worksheet presents an always-visible grid featuring:\n"
            "- Select checkbox: Mark rows for printing.\n"
            "- Article/Barcode/MRP/Color/Size columns.\n"
            "- Qty input and dynamic Labels counter.\n\n"
            "3. Dynamic Mapping Preview & Fallbacks\n"
            "The sidebar renders real-time mappings showing how layout tags (such as {barcode}, {brand}, and {mrp}) map to actual values (e.g., Barcode -> 8901234567890). If a variant lacks pricing, fallback logic queries price lists and template parameters to prevent blank labels.\n\n"
            "4. Box/Carton Mode & Reprint Queue\n"
            "Box Mode calculates labels based on carton capacity multiplier limits. The Reprint Queue caches recent jobs for instant re-execution without re-querying transactions."
        ),
        "faqs": [
            {
                "question": _("How does the system handle missing prices during barcode layout mapping?"),
                "answer": _("It triggers the fallback price resolution rule: checking Variant Price, standard Price Lists, and finally Parent Template prices in order.")
            },
            {
                "question": _("Can I reprint labels without searching for the transaction again?"),
                "answer": _("Yes. The persistent Reprint Queue holds history data of recent print jobs, enabling one-click re-printing from the toolbar.")
            },
            {
                "question": _("What selection options are available for transaction imports?"),
                "answer": _("When importing a Purchase Receipt or PO, the expansion modal allows you to choose 'Select All', 'Only Missing Labels', or 'Only New SKUs' to optimize print volume.")
            }
        ]
    },
    "barcode_telemetry": {
        "title": _("Barcode Scan Telemetry Framework"),
        "category": "Operations Guides",
        "description": _("Real-time scan event tracking, daily aggregations, and the Scan Reliability Score (SRS)."),
        "about": _("Detailed guide for SMRITI Barcode Scan Telemetry (ACP-BARCODE-002A) covering event types, retention rules, and formula transparency."),
        "author": {
            "name": "Jawahar R. Mallah",
            "title": _("Founder & Chief Architect, AITDL"),
            "quote": _("Explainable telemetry turns checkout noise into actionable print-quality intelligence.")
        },
        "content": _(
            "SMRITI Retail OS features the Barcode Scan Telemetry Collection Framework (ACP-BARCODE-002A) to monitor and optimize physical scanning reliability.\n\n"
            "1. Seeded Governance Event Definitions\n"
            "Scanning events are automatically classified into three standard event codes to avoid magic numbers:\n"
            "- SCAN-EVT-001 (Success): Scanned and decoded successfully on the very first try.\n"
            "- SCAN-EVT-002 (Retry): Scanned successfully but required multiple attempts (retry scanning).\n"
            "- SCAN-EVT-003 (Failure): Failed to decode or bypassed by manually typing the barcode digits.\n\n"
            "2. Raw Event Logging and Immutability\n"
            "Cashier scan attempts are logged to SMRITI Barcode Scan Event records. Each record includes scan attempts, barcode family, scanner type, and a unique UUID to filter network retries. Once inserted, events are strictly read-only and immutable; saving or editing existing events throws a validation error.\n\n"
            "3. Scan Reliability Score (SRS)\n"
            "The system evaluates physical scan usability using the KGF-registered formula (SMRITI-SCAN-REL-01):\n"
            "SRS = ((FirstPassSuccesses + 0.5 * RetrySuccesses) / TotalScans) * 100\n"
            "Scores below 85% trigger store alerts recommending layout revision or printhead cleaning.\n\n"
            "4. Retention Policy\n"
            "Raw logs are kept for 90 days and pruned daily by delete_expired_scan_events. Aggregated Telemetry Snapshots are saved permanently for performance trends and training."
        ),
        "faqs": [
            {
                "question": _("What roles are allowed to submit barcode scan telemetry?"),
                "answer": _("Only logged-in, authenticated sessions matching POS Cashier, POS User, Store Manager, or System Manager roles can log scan events.")
            },
            {
                "question": _("Are raw barcode scan events backed up?"),
                "answer": _("Yes. Raw telemetry is included in regular backups for audit and forensics. However, live tables are kept light by pruning logs older than 90 days.")
            },
            {
                "question": _("When are scan snapshots computed?"),
                "answer": _("Aggregations run daily at 03:00 AM local time via background scheduler to prevent database locks during store hours.")
            }
        ]
    },
    "clienteling_intelligence": {
        "title": _("Clienteling & Customer Intelligence Graph"),
        "category": "Analytics Guides",
        "description": _("Detailed guide explaining SMRITI Customer Intelligence Graph (CIG) architecture, settings, and the Explainability UI workflow."),
        "about": _("This guide explains SMRITI's Customer Intelligence Graph (CIG), settings-based thresholds, and how to verify calculations via the Explainability UI."),
        "author": {
            "name": "Jawahar R. Mallah",
            "title": _("Founder & Chief Architect, AITDL"),
            "quote": _("Dynamic clienteling converts raw transaction data into personalized customer relationships.")
        },
        "content": _(
            "SMRITI Customer Intelligence Graph (CIG) is the core analytical engine for modern retail clienteling, enabling stores to dynamically evaluate customer loyalty, risk profiles, and next-purchase affinity.\n\n"
            "1. CIG Architecture & Flow\n"
            "Adhering to SMRITI's Service-First constitution, frontend clients never manipulate the database directly. All operations route through service controllers. The data flow is:\n"
            "Customer Checkout Event → SMRITI Customer Graph → CIG Calculation → SMRITI Customer Profile Update.\n\n"
            "2. Settings-Based Thresholds\n"
            "Calculations avoid hardcoded values by retrieving limits dynamically from SMRITI Clienteling Settings:\n"
            "- vip_threshold (default 80.0): Min candidate score required to auto-flag a profile as VIP (is_vip = 1).\n"
            "- dormancy_days (default 90): Number of days since last visit after which a customer is flagged as dormant.\n"
            "- enable_predictions (default 1): Enforces or disables execution of predictive model calculations for next-visit and product recommendations.\n\n"
            "3. Why did this customer receive this score? (Explainability Workflow)\n"
            "To understand any intelligence metric (such as Churn Risk or VIP Candidate Score) on the SMRITI UI, use the following transparency workflow:\n"
            "Open Customer Profile\n"
            "↓\n"
            "Click ⓘ Explain next to the metric\n"
            "↓\n"
            "View active Formula ID (resolves to central SMRITI Formula Registry)\n"
            "↓\n"
            "View Formula Version\n"
            "↓\n"
            "View Inputs (shows customer's actual live transaction variables)\n"
            "↓\n"
            "View Output (displays step-by-step arithmetic worked example)\n\n"
            "4. Dynamic Formula Resolution\n"
            "CIG retrieves mathematical expressions from the central SMRITI Formula Registry. It executes formulas using Churn Risk Score (TST-CHURN), VIP Candidate Score (TST-VIP), and Campaign Affinity Score (TST-AFFINITY). See the Formula Registry for active expressions."
        ),
        "faqs": [
            {
                "question": _("Who has permission to change Clienteling settings?"),
                "answer": _("SMRITI Clienteling Settings is restricted. Only users with the 'SMRITI Store Manager' or 'System Manager' roles are permitted to modify thresholds and toggle predictions.")
            },
            {
                "question": _("What happens if a formula definition is modified?"),
                "answer": _("Because CIG resolves expressions dynamically, any update to active formulas in the Formula Registry immediately applies to subsequent customer profile recalculations, avoiding documentation drift.")
            },
            {
                "question": _("Does CIG affect standard ERPNext stock or financial ledgers?"),
                "answer": _("No. SMRITI constitution prohibits CIG from altering stock ledger entries or general ledger entries. It writes exclusively to SMRITI shadow tables and Customer Profile fields.")
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


@frappe.whitelist()
def search_knowledge(query=None):
    """
    Exposes SMRITI Knowledge Center search endpoint to query the Redis index.
    Filters out Governance results for non-System Manager users.
    """
    if not query:
        query = frappe.form_dict.get("query")
    if not query:
        return []
    
    from smriti_retail_os.services.knowledge_service import search_knowledge_index
    results = search_knowledge_index(query)
    
    # Filter results by visibility
    is_sys_admin = "System Manager" in frappe.get_roles(frappe.session.user)
    if not is_sys_admin:
        results = [r for r in results if r.get("type") != "Governance" and r.get("metadata", {}).get("visibility") != "admin"]
        
    return results


@frappe.whitelist()
def rebuild_index_cache():
    """
    Manually rebuilds the persistent SMRITI search cache index in Redis.
    Restricted to SMRITI Store Manager or System Manager role.
    """
    from smriti_retail_os.inventory_api import check_store_manager_role
    try:
        check_store_manager_role()
    except Exception:
        frappe.throw(_("Not permitted to rebuild search index"), frappe.PermissionError)
        
    from smriti_retail_os.services.knowledge_service import rebuild_knowledge_index
    count = rebuild_knowledge_index()
    return {"status": "Success", "indexed_items": count}


@frappe.whitelist()
def get_governance_data():
    """
    Returns aggregated metrics and view statistics for the KGF Governance tab.
    """
    from smriti_retail_os.services.knowledge_service import get_governance_stats
    return get_governance_stats()


def _get_unfiltered_document_registry():
    combined = DOCUMENT_REGISTRY.copy()
    from smriti_retail_os.services.knowledge_service import get_assets
    try:
        dynamic_assets = get_assets(module="PSV", category="Enablement")
        for asset in dynamic_assets:
            combined[asset["name"]] = asset
    except Exception:
        pass
    return combined


@frappe.whitelist()
def get_document_registry():
    """
    Exposes SMRITI DOCUMENT_REGISTRY combined with dynamic assets.
    Filters out visibility: admin documents for non-System Managers.
    """
    is_sys_admin = "System Manager" in frappe.get_roles(frappe.session.user)
    
    unfiltered = _get_unfiltered_document_registry()
    filtered_registry = {}
    for key, doc in unfiltered.items():
        if doc.get("visibility") == "admin" and not is_sys_admin:
            continue
        filtered_registry[key] = doc
        
    return filtered_registry


@frappe.whitelist()
def get_manual_html(volume_name=None):
    """
    Reads the target manual markdown file and returns compiled HTML.
    Enforces role-based visibility restrictions via the DOCUMENT_REGISTRY.
    """
    import os
    from frappe.utils import md_to_html
    
    if not volume_name:
        volume_name = frappe.form_dict.get("volume_name")
        
    if not volume_name:
        frappe.throw(_("Document name is required"), frappe.ValidationError)
        
    registry_entry = _get_unfiltered_document_registry().get(volume_name)
    if not registry_entry:
        frappe.throw(_("Document '{0}' is not registered").format(volume_name), frappe.DoesNotExistError)
        
    # Check System Manager role for admin-only documents
    if registry_entry.get("visibility") == "admin":
        if "System Manager" not in frappe.get_roles(frappe.session.user):
            frappe.throw(_("Not permitted to view governance documents"), frappe.PermissionError)
            
    docs_root = os.path.abspath(os.path.join(frappe.get_app_path("smriti_retail_os"), "..", "docs"))
    
    # Determine the directory based on the document type
    doc_type = registry_entry.get("document_type")
    if doc_type == "about":
        sub_dir = "about"
    elif doc_type == "governance":
        sub_dir = "governance"
    elif doc_type == "enablement":
        sub_dir = "enablement"
    elif doc_type == "certification":
        sub_dir = "certification"
    else:
        sub_dir = "user_manual"
        
    file_path = os.path.join(docs_root, sub_dir, registry_entry.get("file_name"))
    if not os.path.exists(file_path):
        # Fallback to search recursively if folder structures differ
        found_path = None
        for root, dirs, files in os.walk(docs_root):
            if registry_entry.get("file_name") in files:
                found_path = os.path.join(root, registry_entry.get("file_name"))
                break
        if found_path:
            file_path = found_path
        else:
            frappe.throw(_("Document file not found: {0}").format(registry_entry.get("file_name")), frappe.DoesNotExistError)
            
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    # Strip YAML frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2]
            
    return md_to_html(content)


@frappe.whitelist()
def get_knowledge_assets():
    """
    Returns lists of all active SMRITI Formula Definitions and Business Terms.
    """
    import json
    
    formulas = smriti.db.get_list(
        "SMRITI Formula Definition",
        filters={"is_active": 1, "status": "Approved"},
        fields=["formula_id", "formula_name", "formula_category", "formula_expression", "business_meaning", "worked_example", "interpretation_guide", "recommended_action", "business_owner"]
    )
    
    terms = smriti.db.get_list(
        "SMRITI Business Term",
        filters={"is_active": 1, "status": "Approved"},
        fields=["name", "term_id", "term_name", "term_category", "definition", "hinglish_definition", "faq", "common_mistakes", "manual_reference", "training_reference", "business_owner"]
    )
    
    # Enrich terms with relationships
    for t in terms:
        t.faq = json.loads(t.faq) if t.faq else []
        t.common_mistakes = json.loads(t.common_mistakes) if t.common_mistakes else []
        t.related_formulas = [rf.formula_id for rf in smriti.db.get_list("SMRITI Related Formula", filters={"parent": t.name}, fields=["formula_id"])]
        t.related_terms = [rt.related_term_id for rt in smriti.db.get_list("SMRITI Related Term", filters={"parent": t.name}, fields=["related_term_id"])]
        
    return {
        "formulas": formulas,
        "terms": terms
    }


# =============================================================================
# SMRITI Certification Engine & Enablement Downloads APIs
# =============================================================================

QUESTION_CHAPTER_MAP = {
    1: {"chapter_number": 1, "chapter_title": "Understanding the Distribution Visibility Gap", "section_slug": "chapter-1-understanding-the-distribution-visibility-gap"},
    2: {"chapter_number": 1, "chapter_title": "Understanding the Distribution Visibility Gap", "section_slug": "chapter-1-understanding-the-distribution-visibility-gap"},
    3: {"chapter_number": 2, "chapter_title": "Understanding Weeks of Cover (WOC)", "section_slug": "chapter-2-understanding-weeks-of-cover-woc"},
    4: {"chapter_number": 2, "chapter_title": "Understanding Weeks of Cover (WOC)", "section_slug": "chapter-2-understanding-weeks-of-cover-woc"},
    5: {"chapter_number": 2, "chapter_title": "Understanding Weeks of Cover (WOC)", "section_slug": "chapter-2-understanding-weeks-of-cover-woc"},
    6: {"chapter_number": 3, "chapter_title": "Understanding Sell-Through %", "section_slug": "chapter-3-understanding-sell-through"},
    7: {"chapter_number": 3, "chapter_title": "Understanding Sell-Through %", "section_slug": "chapter-3-understanding-sell-through"},
    8: {"chapter_number": 4, "chapter_title": "Reorder Planning", "section_slug": "chapter-4-reorder-planning"},
    9: {"chapter_number": 4, "chapter_title": "Reorder Planning", "section_slug": "chapter-4-reorder-planning"},
    10: {"chapter_number": 5, "chapter_title": "Stock Transfer Decisions", "section_slug": "chapter-5-stock-transfer-decisions"},
    11: {"chapter_number": 6, "chapter_title": "Exception Handling", "section_slug": "chapter-6-exception-handling"},
    12: {"chapter_number": 6, "chapter_title": "Exception Handling", "section_slug": "chapter-6-exception-handling"},
    13: {"chapter_number": 7, "chapter_title": "Capital Efficiency", "section_slug": "chapter-7-capital-efficiency"},
    14: {"chapter_number": 7, "chapter_title": "Capital Efficiency", "section_slug": "chapter-7-capital-efficiency"},
    15: {"chapter_number": 6, "chapter_title": "Exception Handling", "section_slug": "chapter-6-exception-handling"},
    16: {"chapter_number": 6, "chapter_title": "Exception Handling", "section_slug": "chapter-6-exception-handling"},
    17: {"chapter_number": 7, "chapter_title": "Capital Efficiency", "section_slug": "chapter-7-capital-efficiency"},
    18: {"chapter_number": 1, "chapter_title": "Understanding the Distribution Visibility Gap", "section_slug": "chapter-1-understanding-the-distribution-visibility-gap"},
    19: {"chapter_number": 4, "chapter_title": "Reorder Planning", "section_slug": "chapter-4-reorder-planning"},
    20: {"chapter_number": 4, "chapter_title": "Reorder Planning", "section_slug": "chapter-4-reorder-planning"}
}

def _parse_answer_key(file_key):
    """
    Parses the answer key from the markdown guide file.
    """
    import os
    import re
    docs_root = os.path.abspath(os.path.join(frappe.get_app_path("smriti_retail_os"), "..", "docs"))
    
    file_name = f"{file_key}.md"
    file_path = None
    for sub in ["certification", "enablement", "user_manual", "governance"]:
        p = os.path.join(docs_root, sub, file_name)
        if os.path.exists(p):
            file_path = p
            break
            
    if not file_path:
        for root, dirs, files in os.walk(docs_root):
            if file_name in files:
                file_path = os.path.join(root, file_name)
                break
                
    if not file_path or not os.path.exists(file_path):
        frappe.throw(_("Source guide not found for answer key parsing: {0}").format(file_key), frappe.DoesNotExistError)
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    answers = {}
    match = re.search(r"Answer Key:\s*(.*?)(?:\n\n|\n---|---|$)", content, re.IGNORECASE | re.DOTALL)
    if match:
        raw_key = match.group(1).strip()
        pairs = re.findall(r"(\d+)-([A-D])", raw_key)
        for num, ans in pairs:
            answers[int(num)] = ans
            
    return answers

def _parse_questions(file_key):
    """
    Parses questions and choices dynamically from the guide markdown file.
    """
    import os
    import re
    
    docs_root = os.path.abspath(os.path.join(frappe.get_app_path("smriti_retail_os"), "..", "docs"))
    file_name = f"{file_key}.md"
    file_path = None
    for sub in ["certification", "enablement", "user_manual", "governance"]:
        p = os.path.join(docs_root, sub, file_name)
        if os.path.exists(p):
            file_path = p
            break
            
    if not file_path:
        for root, dirs, files in os.walk(docs_root):
            if file_name in files:
                file_path = os.path.join(root, file_name)
                break
                
    if not file_path or not os.path.exists(file_path):
        frappe.throw(_("Source guide not found for questions parsing: {0}").format(file_key), frappe.DoesNotExistError)
        
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        
    q_section_match = re.search(r"### Questions:\s*(.*?)(?:\n\n###|\n---|---|$)", content, re.IGNORECASE | re.DOTALL)
    if not q_section_match:
        return []
        
    q_section = q_section_match.group(1).strip()
    
    questions = []
    lines = q_section.split("\n")
    current_q = None
    
    for line in lines:
        line_str = line.strip()
        if not line_str:
            continue
            
        q_match = re.match(r"^(\d+)\.\s*(?:\*\*)?([^\*]+)(?:\*\*)?", line_str)
        if q_match:
            if current_q:
                questions.append(current_q)
            q_num = int(q_match.group(1))
            q_text = q_match.group(2).strip().rstrip("**").strip()
            current_q = {
                "question_number": q_num,
                "question_text": q_text,
                "choices": []
            }
            continue
            
        choice_match = re.match(r"^\*\s+([A-D])\.\s*(.+)", line_str)
        if choice_match and current_q:
            opt = choice_match.group(1)
            txt = choice_match.group(2).strip().rstrip("**").strip()
            current_q["choices"].append({
                "key": opt,
                "text": txt
            })
            
    if current_q:
        questions.append(current_q)
        
    return questions

@frappe.whitelist()
def start_psv_exam(exam_id=None):
    """
    Checks for active attempts, restricts roles, and returns questions with answers omitted.
    """
    if not exam_id:
        exam_id = frappe.form_dict.get("exam_id")
        
    if not exam_id:
        frappe.throw(_("Exam ID is required"), frappe.ValidationError)
        
    user_roles = frappe.get_roles(frappe.session.user)
    if "Guest" in user_roles and len(user_roles) == 1:
        frappe.throw(_("Guest is not permitted to take exams"), frappe.PermissionError)
        
    # Check if there is already an active attempt
    active_attempt_name = smriti.db.get(
        "SMRITI PSV Exam Attempt",
        filters={
            "user": frappe.session.user,
            "exam_id": exam_id,
            "status": "In Progress"
        },
        fieldname="name"
    )
    
    if active_attempt_name:
        attempt_doc = smriti.documents.get("SMRITI PSV Exam Attempt", active_attempt_name)
    else:
        attempt_doc = smriti.documents.new("PSVExamAttempt")
        attempt_doc.update({
            "user": frappe.session.user,
            "exam_id": exam_id,
            "start_time": frappe.utils.now_datetime(),
            "status": "In Progress"
        })
        # reviewed-ignore-permissions: user taking their own exam attempt, guest check enforced
        attempt_doc.insert(ignore_permissions=True)
        smriti.db.commit()
        
    source_document = smriti.db.get("SMRITI Certification Exam", exam_id, "source_document")
    if not source_document:
        frappe.throw(_("Exam source document not configured"), frappe.ValidationError)
        
    questions = _parse_questions(source_document)
    duration_minutes = smriti.db.get("SMRITI Certification Exam", exam_id, "duration_minutes") or 60
    
    return {
        "status": "In Progress",
        "attempt_id": attempt_doc.name,
        "questions": questions,
        "start_time": attempt_doc.start_time,
        "duration_minutes": duration_minutes
    }

@frappe.whitelist()
def submit_psv_exam(attempt_id=None, answers_json=None):
    """
    Performs grading, checks timeout, generates hash, and compiles feedback maps.
    """
    import json
    if not attempt_id:
        attempt_id = frappe.form_dict.get("attempt_id")
    if not answers_json:
        answers_json = frappe.form_dict.get("answers_json")
        
    if not attempt_id or not answers_json:
        frappe.throw(_("Attempt ID and Answers are required"), frappe.ValidationError)
        
    attempt_doc = smriti.documents.get("SMRITI PSV Exam Attempt", attempt_id)
    if attempt_doc.status in ("Passed", "Failed"):
        frappe.throw(_("This exam attempt has already been graded and closed."), frappe.ValidationError)
        
    # Check for expiration
    elapsed_seconds = (frappe.utils.now_datetime() - attempt_doc.start_time).total_seconds()
    duration_limit_minutes = smriti.db.get("SMRITI Certification Exam", attempt_doc.exam_id, "duration_minutes") or 60
    is_expired = elapsed_seconds > (duration_limit_minutes * 60)
    
    source_document = smriti.db.get("SMRITI Certification Exam", attempt_doc.exam_id, "source_document")
    answer_key = _parse_answer_key(source_document)
    
    if is_expired:
        attempt_doc.end_time = frappe.utils.now_datetime()
        attempt_doc.score = 0.0
        attempt_doc.correct_answers = 0
        attempt_doc.total_questions = len(answer_key)
        attempt_doc.status = "Failed"
        attempt_doc.submitted_answers_json = answers_json
        # reviewed-ignore-permissions: no role restriction — any authenticated user may evaluate exam attempts, by design
        attempt_doc.save(ignore_permissions=True)
        smriti.db.commit()
        return {
            "status": "Failed",
            "score": 0.0,
            "correct_answers": 0,
            "total_questions": len(answer_key),
            "reason": "Time limit exceeded. The exam session expired.",
            "incorrect_feedback": []
        }
        
    submitted = json.loads(answers_json)
    
    correct_count = 0
    total_count = len(answer_key)
    for q_num_str, ans in submitted.items():
        q_num = int(q_num_str)
        if answer_key.get(q_num) == ans:
            correct_count += 1
            
    score = (correct_count / total_count) * 100.0 if total_count > 0 else 0.0
    passing_score = smriti.db.get("SMRITI Certification Exam", attempt_doc.exam_id, "passing_score") or 80.0
    
    passed = score >= passing_score
    status = "Passed" if passed else "Failed"
    
    certificate_hash = None
    if passed:
        import hashlib
        hash_input = f"{attempt_doc.user}|{attempt_doc.exam_id}|{attempt_doc.start_time}|{score}"
        certificate_hash = hashlib.sha256(hash_input.encode('utf-8')).hexdigest()
        
    incorrect_feedback = []
    for q_num, corr_ans in answer_key.items():
        user_ans = submitted.get(str(q_num))
        if user_ans != corr_ans:
            chapter_info = QUESTION_CHAPTER_MAP.get(q_num, {
                "chapter_number": 1,
                "chapter_title": "Understanding the Distribution Visibility Gap",
                "section_slug": "chapter-1-understanding-the-distribution-visibility-gap"
            })
            incorrect_feedback.append({
                "question_number": q_num,
                "user_answer": user_ans or "No Answer",
                "correct_answer": corr_ans,
                "chapter_title": chapter_info["chapter_title"],
                "chapter_number": chapter_info["chapter_number"],
                "section_slug": chapter_info["section_slug"]
            })
            
    incorrect_feedback.sort(key=lambda x: x["question_number"])
            
    attempt_doc.end_time = frappe.utils.now_datetime()
    attempt_doc.score = score
    attempt_doc.correct_answers = correct_count
    attempt_doc.total_questions = total_count
    attempt_doc.status = status
    attempt_doc.submitted_answers_json = answers_json
    attempt_doc.certificate_hash = certificate_hash
    # reviewed-ignore-permissions: no role restriction — any authenticated user may evaluate exam attempts, by design
    attempt_doc.save(ignore_permissions=True)
    smriti.db.commit()
    
    return {
        "status": status,
        "score": score,
        "correct_answers": correct_count,
        "total_questions": total_count,
        "certificate_hash": certificate_hash,
        "incorrect_feedback": incorrect_feedback
    }

@frappe.whitelist()
def get_psv_exam_status(exam_id=None):
    """
    Returns active, best, and past attempts for the logged-in user and exam.
    """
    if not exam_id:
        exam_id = frappe.form_dict.get("exam_id")
        
    if not exam_id:
        frappe.throw(_("Exam ID is required"), frappe.ValidationError)
        
    user = frappe.session.user
    
    attempts = smriti.db.get_list(
        "SMRITI PSV Exam Attempt",
        filters={"user": user, "exam_id": exam_id},
        fields=["name", "start_time", "score", "status", "end_time"],
        order_by="start_time desc"
    )
    
    mapped_attempts = []
    for att in attempts:
        mapped_attempts.append({
            "attempt_id": att.name,
            "start_time": att.start_time,
            "end_time": att.end_time,
            "score": att.score,
            "status": att.status
        })
        
    active_attempt = None
    for att in mapped_attempts:
        if att["status"] == "In Progress":
            elapsed_seconds = (frappe.utils.now_datetime() - att["start_time"]).total_seconds()
            duration_limit_minutes = smriti.db.get("SMRITI Certification Exam", exam_id, "duration_minutes") or 60
            if elapsed_seconds > (duration_limit_minutes * 60):
                doc = smriti.documents.get("SMRITI PSV Exam Attempt", att["attempt_id"])
                doc.status = "Failed"
                doc.score = 0.0
                doc.end_time = frappe.utils.now_datetime()
                # reviewed-ignore-permissions: no role restriction — any authenticated user may retrieve exam status, by design
                doc.save(ignore_permissions=True)
                smriti.db.commit()
                att["status"] = "Failed"
                att["score"] = 0.0
            else:
                active_attempt = att
                break
                
    best_attempt = None
    passed_attempts = [att for att in mapped_attempts if att["status"] == "Passed"]
    if passed_attempts:
        passed_attempts.sort(key=lambda x: (x["score"], -x["start_time"].timestamp() if x["start_time"] else 0), reverse=True)
        best_attempt = passed_attempts[0]
        
    return {
        "active_attempt": active_attempt,
        "best_attempt": best_attempt,
        "attempts": mapped_attempts
    }

@frappe.whitelist(allow_guest=True)
def get_certified_registry():
    """
    Returns a list of certified planners without leaking internal IDs or emails.
    """
    attempts = smriti.db.get_list(
        "SMRITI PSV Exam Attempt",
        filters={"status": "Passed"},
        fields=["user", "exam_id", "end_time", "certificate_hash"],
        order_by="end_time desc"
    )
    
    registry = []
    user_names = {}
    exam_titles = {}
    
    for att in attempts:
        if not att.certificate_hash:
            continue
            
        user = att.user
        if user not in user_names:
            user_names[user] = smriti.db.get("User", user, "full_name") or user
            
        exam_id = att.exam_id
        if exam_id not in exam_titles:
            exam_titles[exam_id] = smriti.db.get("SMRITI Certification Exam", exam_id, "title") or exam_id
            
        registry.append({
            "candidate_name": user_names[user],
            "exam_title": exam_titles[exam_id],
            "completion_date": frappe.utils.format_date(att.end_time) if att.end_time else "",
            "certificate_hash": att.certificate_hash
        })
        
    return registry

@frappe.whitelist()
def download_psv_certificate(attempt_id=None):
    """
    Renders certificate HTML page for viewing/printing.
    """
    if not attempt_id:
        attempt_id = frappe.form_dict.get("attempt_id")
        
    if not attempt_id:
        frappe.throw(_("Attempt ID is required"), frappe.ValidationError)
        
    attempt = smriti.documents.get("SMRITI PSV Exam Attempt", attempt_id)
    if attempt.status != "Passed":
        frappe.throw(_("Certificate is only available for passed attempts."), frappe.ValidationError)
        
    candidate_name = smriti.db.get("User", attempt.user, "full_name") or attempt.user
    exam_title = smriti.db.get("SMRITI Certification Exam", attempt.exam_id, "title") or attempt.exam_id
    completion_date = frappe.utils.format_date(attempt.end_time) if attempt.end_time else ""
    score = attempt.score
    certificate_hash = attempt.certificate_hash
    
    html_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SMRITI Certified Planner Certificate</title>
    <style>
        body {{
            font-family: 'Arial', sans-serif;
            background-color: #F8FAFC;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }}
        .certificate-container {{
            width: 800px;
            height: 550px;
            padding: 40px;
            border: 20px solid #1A2B5C;
            background-color: #FFFFFF;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
            position: relative;
            text-align: center;
            box-sizing: border-box;
        }}
        .certificate-border-inner {{
            border: 2px solid #2563EB;
            height: 100%;
            padding: 30px;
            box-sizing: border-box;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }}
        .logo {{
            font-size: 24px;
            font-weight: bold;
            color: #1A2B5C;
            letter-spacing: 2px;
        }}
        .title {{
            font-size: 38px;
            font-weight: bold;
            color: #1A2B5C;
            margin-top: 10px;
        }}
        .subtitle {{
            font-size: 16px;
            color: #64748B;
            text-transform: uppercase;
            letter-spacing: 3px;
        }}
        .recipient-label {{
            font-size: 18px;
            color: #334155;
            margin-top: 20px;
        }}
        .recipient-name {{
            font-size: 32px;
            font-weight: bold;
            color: #2563EB;
            border-bottom: 2px solid #E2E8F0;
            display: inline-block;
            padding: 5px 40px;
            margin: 10px 0;
        }}
        .achievement-text {{
            font-size: 15px;
            color: #475569;
            max-width: 550px;
            margin: 0 auto;
        }}
        .footer-section {{
            display: flex;
            justify-content: space-between;
            align-items: flex-end;
            margin-top: 30px;
        }}
        .signature-block {{
            text-align: center;
            width: 200px;
        }}
        .signature-line {{
            border-top: 1px solid #94A3B8;
            margin-top: 5px;
            font-size: 12px;
            color: #64748B;
            padding-top: 5px;
        }}
        .signature-name {{
            font-weight: bold;
            color: #1A2B5C;
            font-size: 14px;
        }}
        .verify-info {{
            text-align: left;
            font-size: 10px;
            color: #94A3B8;
            max-width: 300px;
        }}
        .hash-code {{
            font-family: monospace;
            font-size: 10px;
            word-break: break-all;
            color: #64748B;
        }}
        @media print {{
            body {{
                background: none;
                margin: 0;
            }}
            .certificate-container {{
                box-shadow: none;
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="certificate-container">
        <div class="certificate-border-inner">
            <div class="logo">SMRITI RETAIL OS</div>
            <div>
                <div class="subtitle">Certificate of Achievement</div>
                <div class="title">Certified Planner</div>
            </div>
            <div>
                <div class="recipient-label">This credential is proudly presented to</div>
                <div class="recipient-name">{candidate_name}</div>
                <div class="achievement-text">
                    for successfully passing the <strong>{exam_title}</strong> with a score of <strong>{score}%</strong>, demonstrating mastery of weeks of cover calculations, sell-through velocity analytics, and network stock distribution planning.
                </div>
            </div>
            <div class="footer-section">
                <div class="verify-info">
                    <strong>Verification Registry Details:</strong><br>
                    Date Issued: {completion_date}<br>
                    Verification Hash:<br>
                    <span class="hash-code">{certificate_hash}</span>
                </div>
                <div class="signature-block">
                    <div class="signature-name">Jawahar R. Mallah</div>
                    <div class="signature-line">Founder & Chief Architect, AITDL</div>
                </div>
            </div>
        </div>
    </div>
    <script>
        window.onload = function() {{
            if (window.location.search.includes("print=1")) {{
                window.print();
            }}
        }}
    </script>
</body>
</html>"""
    
    html_content = html_template.format(
        candidate_name=candidate_name,
        exam_title=exam_title,
        completion_date=completion_date,
        score=score,
        certificate_hash=certificate_hash
    )
    
    frappe.response.type = "binary"
    frappe.response.filecontent = html_content
    frappe.response.filename = None
    
    frappe.local.response.setdefault('headers', {})
    frappe.local.response.headers['Content-Type'] = 'text/html; charset=utf-8'

@frappe.whitelist(allow_guest=True)
def verify_psv_certificate(certificate_hash=None):
    """
    Public validation endpoint for certificate hashes.
    """
    if not certificate_hash:
        certificate_hash = frappe.form_dict.get("certificate_hash")
        
    if not certificate_hash:
        return {"valid": False, "error": "Missing certificate hash"}
        
    attempt = smriti.db.get_list(
        "SMRITI PSV Exam Attempt",
        filters={"certificate_hash": certificate_hash, "status": "Passed"},
        fields=["name", "user", "exam_id", "end_time", "score"]
    )
    
    if not attempt:
        return {"valid": False, "error": "Invalid or non-existent certificate hash"}
        
    attempt_doc = attempt[0]
    candidate_name = smriti.db.get("User", attempt_doc.user, "full_name") or attempt_doc.user
    exam_title = smriti.db.get("SMRITI Certification Exam", attempt_doc.exam_id, "title") or attempt_doc.exam_id
    
    return {
        "valid": True,
        "attempt_id": attempt_doc.name,
        "user": attempt_doc.user,
        "candidate_name": candidate_name,
        "exam_id": attempt_doc.exam_id,
        "exam_title": exam_title,
        "completion_date": frappe.utils.format_datetime(attempt_doc.end_time, "yyyy-MM-dd HH:mm:ss"),
        "score": attempt_doc.score
    }

@frappe.whitelist()
def download_enablement_file(file_key=None):
    """
    Allows permitted users to download enablement resources and zip bundles.
    """
    if not file_key:
        file_key = frappe.form_dict.get("file_key")
        
    if not file_key:
        frappe.throw(_("File key is required"), frappe.ValidationError)
        
    user_roles = frappe.get_roles(frappe.session.user)
    if "Guest" in user_roles and len(user_roles) == 1:
        frappe.throw(_("Guest is not permitted to download files"), frappe.PermissionError)
        
    if ".." in file_key or "/" in file_key or "\\" in file_key:
        frappe.throw(_("Invalid file key formatting"), frappe.ValidationError)
        
    import os
    docs_root = os.path.abspath(os.path.join(frappe.get_app_path("smriti_retail_os"), "..", "docs"))
    
    if file_key == "zip_bundle":
        import io
        import zipfile
        
        enablement_dir = os.path.join(docs_root, "enablement")
        if not os.path.exists(enablement_dir):
            frappe.throw(_("Enablement pack directory not found"), frappe.DoesNotExistError)
            
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(enablement_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, enablement_dir)
                    zip_file.write(file_path, rel_path)
                    
        frappe.local.response.filename = "SMRITI_PSV_Enablement_Pack.zip"
        frappe.local.response.filecontent = zip_buffer.getvalue()
        frappe.local.response.type = "download"
        return
        
    registry = get_document_registry()
    asset = registry.get(file_key)
    if not asset:
        frappe.throw(_("Asset '{0}' is not registered or accessible.").format(file_key), frappe.DoesNotExistError)
        
    file_name = asset.get("file_name")
    if not file_name or ".." in file_name or "/" in file_name or "\\" in file_name:
        frappe.throw(_("Invalid filename associated with asset"), frappe.ValidationError)
        
    doc_type = asset.get("document_type")
    if doc_type == "enablement":
        sub_dir = "enablement"
    elif doc_type == "certification":
        sub_dir = "certification"
    else:
        sub_dir = "user_manual"
        
    allowed_dir = os.path.join(docs_root, sub_dir)
    file_path = os.path.abspath(os.path.join(allowed_dir, file_name))
    
    if not file_path.startswith(allowed_dir):
        frappe.throw(_("Access denied: path traversal detected"), frappe.ValidationError)
        
    if not os.path.exists(file_path):
        frappe.throw(_("File not found: {0}").format(file_name), frappe.DoesNotExistError)
        
    with open(file_path, "rb") as f:
        file_content = f.read()
        
    frappe.local.response.filename = file_name
    frappe.local.response.filecontent = file_content
    frappe.local.response.type = "download"
