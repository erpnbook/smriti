# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti-tally.py
# @description: Legacy compatibility redirect for Tally Sync. Deprecated since UIE v1.0.
#

import frappe

def get_context(context):
	# Log deprecation warning
	frappe.logger().warning("Accessing deprecated route /smriti-tally. Redirecting to /smriti-uie.")
	# Perform standard HTTP 302 redirect to new UIE Integration Center
	frappe.local.flags.redirect_location = "/smriti-uie"
	raise frappe.Redirect
