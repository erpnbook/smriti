# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/report/psv_reorder_report/psv_reorder_report.py
# @description: Backend logic for the PSV Reorder Recommendation Report.
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

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from smriti_retail_os.balance_engine import get_bulk_party_balances, get_reorder_recommendation

def execute(filters=None):
	columns = get_columns()
	data = get_data(filters)
	return columns, data

def get_columns():
	return [
		{
			"fieldname": "location",
			"label": "Location",
			"fieldtype": "Link",
			"options": "SMRITI Party Stock Account",
			"width": 180
		},
		{
			"fieldname": "zone",
			"label": "Zone",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"fieldname": "item_code",
			"label": "Item Variant",
			"fieldtype": "Link",
			"options": "Item",
			"width": 150
		},
		{
			"fieldname": "current_balance",
			"label": "Current Balance",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "weekly_sale_avg",
			"label": "Weekly Sale Avg",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "days_cover",
			"label": "Days Cover",
			"fieldtype": "Float",
			"width": 100
		},
		{
			"fieldname": "reorder_level",
			"label": "Reorder Level",
			"fieldtype": "Float",
			"width": 120
		},
		{
			"fieldname": "recommended_qty",
			"label": "Recommended Qty",
			"fieldtype": "Float",
			"width": 130
		},
		{
			"fieldname": "priority",
			"label": "Priority",
			"fieldtype": "Data",
			"width": 100
		}
	]

def get_data(filters):
	if not filters:
		filters = {}

	company = filters.get("company")
	zone = filters.get("zone")
	priority_filter = filters.get("priority")
	show_zero = filters.get("show_zero")

	# Fetch matching PSAs
	psa_filters = {"active": 1}
	if company:
		psa_filters["company"] = company
	if zone:
		psa_filters["zone"] = zone

	psas = smriti.db.get_list("SMRITI Party Stock Account",
		filters=psa_filters,
		fields=["name", "zone"]
	)

	data = []

	priority_weight = {
		"Critical": 4,
		"High": 3,
		"Medium": 2,
		"Low": 1
	}

	for psa in psas:
		psa_name = psa.name
		psa_zone = psa.zone

		# Get items from ledger entries + reorder rules
		balances = get_bulk_party_balances(psa_name)
		item_codes = set(balances.keys())

		rule_items = smriti.db.get_list("SMRITI PSV Reorder Rule",
			filters={
				"company": company,
				"party_stock_account": psa_name,
				"item_variant": ["is", "set"],
				"active": 1
			},
			fields=["item_variant"]
		)
		for r in rule_items:
			item_codes.add(r.item_variant)

		for item_code in sorted(item_codes):
			reco = get_reorder_recommendation(company, psa_name, item_code)
			if not reco:
				continue

			rec_qty = reco.get("recommended_qty", 0.0)
			prio = reco.get("priority", "Low")

			# Filter by show_zero
			if not show_zero and rec_qty <= 0:
				continue

			# Filter by priority
			if priority_filter and prio != priority_filter:
				continue

			data.append({
				"location": psa_name,
				"zone": psa_zone,
				"item_code": item_code,
				"current_balance": reco.get("current_balance", 0.0),
				"weekly_sale_avg": reco.get("weekly_sale_avg", 0.0),
				"days_cover": reco.get("days_cover", 0.0),
				"reorder_level": reco.get("reorder_level", 0.0),
				"recommended_qty": rec_qty,
				"priority": prio,
				"priority_weight": priority_weight.get(prio, 0)
			})

	# Sort data by priority (Critical first) then recommended_qty descending
	data.sort(key=lambda x: (x["priority_weight"], x["recommended_qty"]), reverse=True)

	# Strip sorting weight
	for row in data:
		row.pop("priority_weight", None)

	return data
