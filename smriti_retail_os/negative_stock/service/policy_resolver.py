# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/negative_stock/service/policy_resolver.py
# @description: Hierarchical policy resolver for SMRITI Negative Stock Management.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-29
# @version: 1.9.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from frappe.utils import today

class SMRITINegativeStockPolicyResolver(object):
	"""
	Resolves negative stock policy hierarchically:
	Item -> Item Group -> Warehouse -> Company -> Global
	Within same level: highest priority wins.
	"""

	def __init__(self, item_code, warehouse, company):
		self.item_code = item_code
		self.warehouse = warehouse
		self.company = company
		self.today_date = today()
		self.item_doc = None

	def get_item_group(self):
		if not self.item_doc and self.item_code:
			self.item_doc = smriti.db.get("Item", self.item_code, ["item_group"], as_dict=True)
		return self.item_doc.item_group if self.item_doc else None

	def resolve(self):
		"""
		Evaluates and returns the matching policy document.
		If no policy is found, returns a default fallback policy dictionary.
		"""
		item_group = self.get_item_group()
		policies = self.get_active_policies()

		# Organize policies by scope level to enforce hierarchy specificity
		matched_groups = {
			"Item": [],
			"Item Group": [],
			"Warehouse": [],
			"Company": [],
			"Global": []
		}

		for p in policies:
			if p.apply_to == "Item" and p.item_code == self.item_code:
				matched_groups["Item"].append(p)
			elif p.apply_to == "Item Group" and p.item_group == item_group:
				matched_groups["Item Group"].append(p)
			elif p.apply_to == "Warehouse" and p.warehouse == self.warehouse:
				matched_groups["Warehouse"].append(p)
			elif p.apply_to == "Company" and p.company == self.company:
				matched_groups["Company"].append(p)
			elif p.apply_to == "Global":
				matched_groups["Global"].append(p)

		# Evaluate in priority order: Item -> Item Group -> Warehouse -> Company -> Global
		for level in ["Item", "Item Group", "Warehouse", "Company", "Global"]:
			candidates = matched_groups[level]
			if candidates:
				# Sort by priority desc, modified desc
				candidates.sort(key=lambda x: (x.priority or 0, x.modified), reverse=True)
				return candidates[0]

		# Default fallback policy if none matching
		return frappe._dict({
			"name": "Fallback Global Default",
			"apply_to": "Global",
			"policy_mode": "Block",
			"priority": 0,
			"approval_required": 0,
			"is_active": 1
		})

	def get_active_policies(self):
		"""
		Fetches all active policies from the database.
		"""
		# Build query filters for active policies with date bounds
		filters = {
			"is_active": 1
		}

		# Retrieve all policies and filter dates in Python to handle empty/null dates properly
		policies = smriti.db.get_list("SMRITI Negative Stock Policy", fields=[
			"name", "apply_to", "company", "warehouse", "item_group", "item_code", 
			"policy_mode", "priority", "approval_required", "approval_flow", 
			"effective_from", "effective_to", "modified"
		], filters=filters)

		valid_policies = []
		for p in policies:
			# Check date validity
			if p.effective_from and p.effective_from > self.today_date:
				continue
			if p.effective_to and p.effective_to < self.today_date:
				continue
			valid_policies.append(p)

		return valid_policies
