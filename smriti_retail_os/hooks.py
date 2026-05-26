app_name = "smriti_retail_os"
app_title = "SMRITI Retail OS"
app_publisher = "Antigravity"
app_description = "Retail Experience Layer"
app_email = "admin@smriti.io"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

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
# app_include_css = "/assets/smriti_retail_os/css/smriti_retail_os.css"
# app_include_js = "/assets/smriti_retail_os/js/smriti_retail_os.js"

# include js, css files in header of web template
# web_include_css = "/assets/smriti_retail_os/css/smriti_retail_os.css"
# web_include_js = "/assets/smriti_retail_os/js/smriti_retail_os.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "smriti_retail_os/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
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
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

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
# after_install = "smriti_retail_os.install.after_install"

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

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

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

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "smriti_retail_os.event.get_events"
# }
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

