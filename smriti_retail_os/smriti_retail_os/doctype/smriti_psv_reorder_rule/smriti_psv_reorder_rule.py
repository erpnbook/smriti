# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_psv_reorder_rule/smriti_psv_reorder_rule.py
# @description: DocType controller for SMRITI PSV Reorder Rule.
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
from frappe import _
from frappe.model.document import Document


class SMRITIPSVReorderRule(Document):
	def validate(self):
		self.validate_item_scope()
		self.validate_lead_time()
		self.validate_safety_stock()
		self.validate_stock_range()

	def validate_item_scope(self):
		"""Ensure at least one of item_group or item_variant is set."""
		if not self.item_group and not self.item_variant:
			frappe.throw(
				_("Either {0} or {1} must be set.").format(
					frappe.bold(_("Item Group")),
					frappe.bold(_("Item Variant")),
				)
			)

	def validate_lead_time(self):
		"""Lead Time (Days) must be greater than zero."""
		if (self.lead_time_days or 0) <= 0:
			frappe.throw(_("Lead Time (Days) must be greater than 0."))

	def validate_safety_stock(self):
		"""Safety Stock must be non-negative."""
		if (self.safety_stock or 0) < 0:
			frappe.throw(_("Safety Stock cannot be negative."))

	def validate_stock_range(self):
		"""If max_stock is set, it must exceed min_stock."""
		if self.max_stock and self.max_stock > 0:
			if self.max_stock <= (self.min_stock or 0):
				frappe.throw(
					_("Maximum Stock ({0}) must be greater than Minimum Stock ({1}).").format(
						self.max_stock, self.min_stock or 0
					)
				)
