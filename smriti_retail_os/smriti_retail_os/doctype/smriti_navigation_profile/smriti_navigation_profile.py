# -*- coding: utf-8 -*-
# Copyright (c) 2026, AITDL NETWORK & ERPNbook.com and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SMRITINavigationProfile(Document):
	def on_update(self):
		from smriti_retail_os.navigation.navigation_service import invalidate_navigation_cache
		invalidate_navigation_cache()

	def on_trash(self):
		from smriti_retail_os.navigation.navigation_service import invalidate_navigation_cache
		invalidate_navigation_cache()
