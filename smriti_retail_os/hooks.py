app_name = "smriti_retail_os"
app_title = "SMRITI Retail OS"
app_publisher = "SMRITI Retail OS"
app_description = "Retail Experience Layer"
app_email = "admin@smriti.io"
app_license = "mit"
brand_html = "<b style='color:#e94560;font-family:Inter,sans-serif'>SMRITI Retail OS</b>"

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
    "/assets/smriti_retail_os/css/smriti-reports.css"
]
app_include_js = [
    "/assets/smriti_retail_os/js/smriti_sidebar.js",
    "/assets/smriti_retail_os/js/smriti_reports.js",
    "/assets/smriti_retail_os/js/main.js"
]

# website page context override for whitelabel branding
update_website_context = ["smriti_retail_os.website_context.get_context"]

# include js, css files in header of web template
web_include_css = "/assets/smriti_retail_os/css/smriti_branding.css"
web_include_js = "/assets/smriti_retail_os/js/main.js"

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

# application home page (will override Website Settings)
home_page = "smriti-home"

# website user home page (by Role)
# Note: role_home_page is for non-desk/website users.
# Desk users are handled via bootinfo.default_route in boot.py
role_home_page = {
    "SMRITI Cashier": "smriti-billing",
    "SMRITI Store Manager": "smriti-desk",
    "System Manager": "smriti-desk"
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
after_migrate = ["smriti_retail_os.setup.setup_smriti_retail_os"]
boot_session = "smriti_retail_os.boot.boot_session"
extend_bootinfo = "smriti_retail_os.boot.extend_bootinfo"

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
    }
}

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"smriti_retail_os.tasks.all"
# 	],
# 	"daily": [
# 		"smriti_retail_os.tasks.daily"
# 	],
# 	"hourly": [
# 		"smriti_retail_os.tasks.hourly"
# 	],
# 	"weekly": [
# 		"smriti_retail_os.tasks.weekly"
# 	],
# 	"monthly": [
# 		"smriti_retail_os.tasks.monthly"
# 	],
# }

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

# Login page override
website_route_rules = [
    {
        "from_route": "/login",
        "to_route": "login"
    }
]

