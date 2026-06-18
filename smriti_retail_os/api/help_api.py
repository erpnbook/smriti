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
        "about": _("This guide explains SMRITI's FIFO-based inventory aging model, aging buckets, and automatic health alert triggers."),
        "author": {
            "name": "Jawahar R Mallah",
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
            "name": "Jawahar R Mallah",
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
            "name": "Jawahar R Mallah",
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
            "name": "Jawahar R Mallah",
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
            "name": "Jawahar R Mallah",
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
            "name": "Jawahar R Mallah",
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
            "name": "Jawahar R Mallah",
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
            "name": "Jawahar R Mallah",
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
            "A global corporate styling sheet is loaded on all views. This enforces the Navy Blue (#1A2B5C) and Royal Blue (#2563EB) color palette, standardizes typography, hides default platform logos, and styles custom desktop shortcuts."
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
            "name": "Jawahar R Mallah",
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
            "name": "Jawahar R Mallah",
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
            "name": "Jawahar R Mallah",
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
            "name": "Jawahar R Mallah",
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
            "name": "Jawahar R Mallah",
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
            "name": "Jawahar R Mallah",
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
