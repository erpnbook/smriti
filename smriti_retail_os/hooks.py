# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/hooks.py
# @description: Frappe application hooks — event bindings, scheduler jobs, and app metadata.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.2.10
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

app_name = "smriti_retail_os"
app_title = "SMRITI Retail OS"
app_publisher = "PrathamOne / AITDL"
app_description = "SMRITI Retail OS — Intelligent Indian Retail Platform"
app_email = "support@erpnbook.com"
app_license = "mit"
brand_html = "<b style='color:#e94560;font-family:Inter,sans-serif'>SMRITI Retail OS</b>"

# Branding Configs
app_logo_url = "/assets/smriti_retail_os/images/smriti_logo.png"
favicon = "/assets/smriti_retail_os/images/smriti_favicon.ico"

# Email notifications whitelabeling
sender_name = "SMRITI Retail OS"
email_brand_image = "/assets/smriti_retail_os/images/smriti_logo.png"

# Footer suppression
footer_items = []
disable_built_with = 1

# Email Whitelabeling templates
email_header = "smriti_retail_os/templates/emails/smriti_email_header.html"
email_footer = "smriti_retail_os/templates/emails/smriti_email_footer.html"

# Support Link Overrides
help_links = [
    {"title": "SMRITI Support Desk", "url": "https://support.erpnbook.com"},
    {"title": "User Manual", "url": "/app/smriti_desk#user-manual"}
]

# ── Setup Wizard — Bypass completely ─────────────────────────────
setup_wizard_requires_login = True
setup_wizard_complete       = True      # Frappe v14+ supported
setup_wizard_stages         = []        # Empty list = no stages


# Apps
# ------------------

required_apps = ["frappe", "erpnext", "india_compliance"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "smriti_retail_os",
# 		"logo": "/assets/smriti_retail_os/logo.png",
# 		"title": "SMRITI Retail OS",
# 		"route": "/smriti_retail_os",
# 		"has_permission": "smriti_retail_os.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
    "/assets/smriti_retail_os/css/smriti_theme.css",
    "/assets/smriti_retail_os/css/smriti_sidebar.css",
    "/assets/smriti_retail_os/css/smriti_branding.css",
    "/assets/smriti_retail_os/css/smriti-reports.css",
    "/assets/smriti_retail_os/css/smriti_sales_invoice.css",
    "/assets/smriti_retail_os/css/smriti_desk_override.css",
]
app_include_js = [
    "/assets/smriti_retail_os/js/smriti_sidebar.js",
    "/assets/smriti_retail_os/js/smriti_reports.js",
    "/assets/smriti_retail_os/js/main.js",
    "/assets/smriti_retail_os/js/smriti_payload_bridge.js",
    # PWA — Service Worker registration, install prompt, offline detection
    "/assets/smriti_retail_os/js/smriti_offline_store.js",
    "/assets/smriti_retail_os/js/smriti_pwa.js",
    "/assets/smriti_retail_os/js/smriti_boot.js",
]

# website page context override for whitelabel branding
update_website_context = ["smriti_retail_os.website_context.get_context"]

# ─── SMRITI Route Aliases — ARCH-004 ────────────────────────────────────────
# All Channel Stock (PSV) pages are accessible via SMRITI-convention /smriti-*
# routes as required by GEMINI.md Rule 7. The legacy short routes still work
# so existing bookmarks / sidebar links are not broken.
website_route_rules = [
    # Channel Stock — main SMRITI-convention routes
    {"from_route": "/smriti-channel-accounts",  "to_route": "psa"},
    {"from_route": "/smriti-sales-upload",       "to_route": "sales-upload"},
    {"from_route": "/smriti-opening-balance",    "to_route": "psv-opening-balance"},
    {"from_route": "/smriti-channel-stock",      "to_route": "psa"},   # Alias entry point

    # Channel Stock — canonical module landing alias
    {"from_route": "/channel-stock",             "to_route": "psa"},
]


# include js, css files in header of web template
web_include_css = [
    "/assets/smriti_retail_os/css/smriti_branding.css",
    "/assets/smriti_retail_os/css/smriti_web.css",
]
web_include_js = [
    "/assets/smriti_retail_os/js/main.js",
    "/assets/smriti_retail_os/js/smriti_payload_bridge.js",
    # PWA — load on every SMRITI web page
    "/assets/smriti_retail_os/js/smriti_offline_store.js",
    "/assets/smriti_retail_os/js/smriti_pwa.js",
    "/assets/smriti_retail_os/js/smriti_web_boot.js",
]

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "smriti_retail_os/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js entries removed — each page's JS file lives inside its own
# page directory (e.g. page/smriti-billing/smriti-billing.js) and is
# auto-loaded by Frappe's standard page loading mechanism.
# page_js = {}

# include js in doctype views
doctype_js = {
    "Item": "public/js/item.js",
    "Customer": "public/js/customer.js",
    "Supplier": "public/js/supplier.js",
    "Sales Invoice": "public/js/sales_invoice.js",
    "Purchase Order": "public/js/purchase_order.js",
    "Purchase Receipt": "public/js/purchase_receipt.js"
}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "smriti_retail_os/public/icons.svg"

# Home Pages
# ----------

# application home page — use Frappe default (login screen)
# Port 9000 Nginx block handles the SMRITI POS redirect to /billing
home_page = "index"

# website user home page (by Role)
# Desk users (System Manager, Store Manager) land on ERPNext /app on port 8080.
# Cashiers land on SMRITI Billing terminal. Port 9000 root redirects to /billing via Nginx.
role_home_page = {
    "SMRITI Cashier": "billing",          # → Standalone billing terminal at /billing
    "SMRITI Store Manager": "app",        # → ERPNext Desk on port 8080
    "System Manager": "app"               # → ERPNext Desk on port 8080
}

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "smriti_retail_os.utils.jinja_methods",
# 	"filters": "smriti_retail_os.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "smriti_retail_os.install.before_install"
after_install = "smriti_retail_os.setup.after_install"
after_migrate = [
    "smriti_retail_os.setup.setup_smriti_retail_os",
    "smriti_retail_os.sync_assets.sync_assets",
]

extend_bootinfo = "smriti_retail_os.boot.extend_bootinfo"
on_session_creation = "smriti_retail_os.boot.on_session_creation"
before_request = ["smriti_retail_os.boot.check_desk_access"]

# Uninstallation
# ------------

# before_uninstall = "smriti_retail_os.uninstall.before_uninstall"
# after_uninstall = "smriti_retail_os.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "smriti_retail_os.utils.before_app_install"
# after_app_install = "smriti_retail_os.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "smriti_retail_os.utils.before_app_uninstall"
# after_app_uninstall = "smriti_retail_os.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "smriti_retail_os.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "smriti_retail_os.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

doc_events = {
    "Item": {
        "before_save": "smriti_retail_os.hooks_logic.sync_item_taxes_and_prices",
        "on_update": "smriti_retail_os.hooks_logic.after_item_save"
    },
    "Customer": {
        "on_update": "smriti_retail_os.hooks_logic.sync_customer_address"
    },
    "Supplier": {
        "on_update": "smriti_retail_os.hooks_logic.sync_supplier_address_and_credit_days"
    },
    "POS Invoice": {
        "before_validate": [
            "smriti_retail_os.hooks_logic.initialize_item_wise_tax_details",
            "smriti_retail_os.hooks_logic.validate_and_reconcile_retail_invoice"
        ]
    },
    "Sales Invoice": {
        "before_validate": [
            "smriti_retail_os.hooks_logic.initialize_item_wise_tax_details",
            "smriti_retail_os.hooks_logic.validate_and_reconcile_retail_invoice"
        ],
        "before_cancel": [
            "smriti_retail_os.psv_service.validate_sales_invoice_cancel"
        ],
        "on_submit": [
            "smriti_retail_os.psv_service.process_sales_invoice_submit"
        ],
        "on_cancel": [
            "smriti_retail_os.psv_service.process_sales_invoice_cancel"
        ]
    },
    "Purchase Receipt": {
        "before_validate": "smriti_retail_os.hooks_logic.initialize_item_wise_tax_details"
    },
    "Purchase Invoice": {
        "before_validate": "smriti_retail_os.hooks_logic.initialize_item_wise_tax_details"
    },
    "Purchase Order": {
        "before_validate": "smriti_retail_os.hooks_logic.initialize_item_wise_tax_details"
    },
    "Sales Order": {
        "before_validate": "smriti_retail_os.hooks_logic.initialize_item_wise_tax_details"
    },
    "Delivery Note": {
        "before_validate": "smriti_retail_os.hooks_logic.initialize_item_wise_tax_details",
        "on_submit": "smriti_retail_os.smriti_retail_os.psv_integration.handle_delivery_note_submit",
        "on_cancel": "smriti_retail_os.smriti_retail_os.psv_integration.handle_delivery_note_cancel"
    },
    "Stock Entry": {
        "on_submit": "smriti_retail_os.smriti_retail_os.psv_integration.handle_sales_return_submit",
        "on_cancel": "smriti_retail_os.smriti_retail_os.psv_integration.handle_sales_return_cancel"
    },
    "Quotation": {
        "before_validate": "smriti_retail_os.hooks_logic.initialize_item_wise_tax_details"
    },
    "Supplier Quotation": {
        "before_validate": "smriti_retail_os.hooks_logic.initialize_item_wise_tax_details"
    },
    "Company": {
        "after_insert": "smriti_retail_os.company_api.ensure_company_settings",
        "on_update": "smriti_retail_os.company_api.ensure_company_settings"
    },
    "Address": {
        "on_update": "smriti_retail_os.hooks_logic.after_address_save"
    }
}


# Scheduled Tasks
# ---------------

scheduler_events = {
    "daily": [
        "smriti_retail_os.backup_api.run_scheduled_backup",
        "smriti_retail_os.psv_service.run_psv_daily_health_check"
    ]
}

# Testing
# -------

# before_tests = "smriti_retail_os.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "smriti_retail_os.custom.task.CustomTaskMixin"
# }

override_whitelisted_methods = {
    "frappe.utils.change_log.get_versions": "smriti_retail_os.branding_api.get_versions"
}
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "smriti_retail_os.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["smriti_retail_os.utils.before_request"]
# after_request = ["smriti_retail_os.utils.after_request"]

# Job Events
# ----------
# before_job = ["smriti_retail_os.utils.before_job"]
# after_job = ["smriti_retail_os.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"smriti_retail_os.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

# Login page override + Billing terminal standalone route
website_route_rules = [
    {
        # PWA Service Worker — must be served from root for full-scope control
        # sw.js lives in public/js/ but is exposed at /sw.js
        "from_route": "/sw.js",
        "to_route": "sw"
    },
    {
        # PWA offline fallback page — served at /offline
        "from_route": "/offline",
        "to_route": "offline"
    },
    {
        "from_route": "/setup-wizard",
        "to_route": "setup_wizard"
    },
    {
        "from_route": "/login",
        "to_route": "smriti-login"
    },
    {
        "from_route": "/smriti",
        "to_route": "smriti-home"
    },
    {
        "from_route": "/smriti/<path:subpath>",
        "to_route": "smriti-home"
    },
    {
        # Standalone billing terminal — served from www/billing.html + www/billing.py
        # Zero Frappe chrome. Frappe used as pure REST API backend.
        "from_route": "/billing",
        "to_route": "billing"
    },
    {
        # Standalone Purchase Manager — served from www/purchase.html + www/purchase.py
        # Zero Frappe chrome. GRN, New PO, all via REST API.
        "from_route": "/purchase",
        "to_route": "purchase"
    },
    {
        # Standalone Control Center (Manager Desk) — served from www/desk.html + www/desk.py
        # Zero Frappe chrome. Fully custom SMRITI dashboard.
        "from_route": "/desk",
        "to_route": "desk"
    },
    {
        # Standalone Inventory Operations — served from www/inventory.html + www/inventory.py
        # Zero Frappe chrome. Custom stock transfer & adjustment.
        "from_route": "/inventory",
        "to_route": "inventory"
    },
    {
        # Standalone Shift Management — served from www/shift.html + www/shift.py
        # Zero Frappe chrome. Custom cashier open & close shift.
        "from_route": "/shift",
        "to_route": "shift"
    },
    {
        # Standalone Barcode Generator — served from www/barcode.html + www/barcode.py
        # Zero Frappe chrome. Custom barcode generation & label printer.
        "from_route": "/barcode",
        "to_route": "barcode"
    },
    {
        # Standalone Products Manager — served from www/products.html + www/products.py
        "from_route": "/products",
        "to_route": "products"
    },
    {
        # Standalone Customer Directory — served from www/customers.html + www/customers.py
        "from_route": "/customers",
        "to_route": "customers"
    },
    {
        # Standalone Supplier Registry — served from www/suppliers.html + www/suppliers.py
        "from_route": "/suppliers",
        "to_route": "suppliers"
    },
    {
        # Standalone SMRITI Party Stock Accounts — served from www/psa.html + www/psa.py
        "from_route": "/psa",
        "to_route": "psa"
    },
    {
        # Standalone Billing Invoices — served from www/sales_invoices.html + www/sales_invoices.py
        "from_route": "/sales_invoices",
        "to_route": "sales_invoices"
    },
    {
        # Standalone Item Master Import — served from www/item_master.html + www/item_master.py
        "from_route": "/item_master",
        "to_route": "item_master"
    },
    {
        # Standalone E-way Bill Management — served from www/eway_bill.html + www/eway_bill.py
        "from_route": "/eway_bill",
        "to_route": "eway_bill"
    },
    {
        # Standalone Dedicated Sizewise Item Master CRUD — served from www/sizewise_item.html + www/sizewise_item.py
        "from_route": "/sizewise_item",
        "to_route": "sizewise_item"
    },
    {
        # Standalone Security & Workflow Center — served from www/security.html + www/security.py
        # Zero Frappe chrome. Custom security, permissions & workflows.
        "from_route": "/security",
        "to_route": "security"
    },
    {
        # Standalone Platform Center (Technical Admin Portal) — served from www/platform_center.html + www/platform_center.py
        "from_route": "/platform_center",
        "to_route": "platform_center"
    },
    {
        # Standalone Reports Dashboard — served from www/reports.html + www/reports.py
        "from_route": "/reports",
        "to_route": "reports"
    },
    {
        # Standalone Print Templates — served from www/print_templates.html + www/print_templates.py
        "from_route": "/print_templates",
        "to_route": "print_templates"
    },
    {
        # Standalone Delivery Challans — served from www/delivery_challan.html + www/delivery_challan.py
        "from_route": "/delivery_challan",
        "to_route": "delivery_challan"
    },
    {
        # Standalone Sales Return & Credit Notes — served from www/sales_return.html + www/sales_return.py
        "from_route": "/sales_return",
        "to_route": "sales_return"
    },
    {
        # Standalone Purchase Receipts (GRN) — served from www/purchase_receipt.html + www/purchase_receipt.py
        "from_route": "/purchase_receipt",
        "to_route": "purchase_receipt"
    },
    {
        # Standalone Purchase Invoices — served from www/purchase_invoice.html + www/purchase_invoice.py
        "from_route": "/purchase_invoice",
        "to_route": "purchase_invoice"
    },
    {
        # Standalone Payments / Receipts Ledger — served from www/payments.html + www/payments.py
        "from_route": "/payments",
        "to_route": "payments"
    },
    {
        # Standalone Backup & Restore Center — served from www/backup.html + www/backup.py
        "from_route": "/backup",
        "to_route": "backup"
    }
]




