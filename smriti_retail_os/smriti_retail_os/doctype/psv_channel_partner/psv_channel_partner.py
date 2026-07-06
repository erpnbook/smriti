# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/psv_channel_partner/psv_channel_partner.py
# @description: SMRITI DocType controller — Frappe document lifecycle handlers.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class PSVChannelPartner(Document):
	def validate(self):
		self.primary_brand = ""
		if self.brands:
			for b in self.brands:
				if b.is_primary:
					self.primary_brand = b.brand
					break
			# If no brand is explicitly marked primary but brands exist, default to the first one
			if not self.primary_brand and len(self.brands) > 0:
				self.primary_brand = self.brands[0].brand
