# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/psv_api.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe
from smriti_retail_os.balance_engine import (
	get_party_balance,
	get_bulk_party_balances,
	get_reorder_recommendation
)

@frappe.whitelist()
def get_dashboard_summary(company):
	"""
	Returns a dict with key operational metrics for the PSV Dashboard:
	- total_units: SUM of all positive balances across all PSAs for the company
	- total_locations: count of active PSAs
	- negative_count: count of active PSAs with any item having negative balance
	- open_exceptions: count of exception records with status 'Pending Reconciliation'
	- critical_alerts: count of exception records with severity 'Critical' and status 'Pending Reconciliation'
	"""
	# 1. Total units across all positive balances
	total_units_res = frappe.db.sql("""
		SELECT COALESCE(SUM(item_bal), 0)
		FROM (
			SELECT SUM(ple.qty) as item_bal
			FROM `tabSMRITI Party Stock Ledger Entry` ple
			INNER JOIN `tabSMRITI Party Stock Account` psa ON ple.party_stock_account = psa.name
			WHERE psa.company = %s
			GROUP BY ple.party_stock_account, ple.item_code
		) t WHERE item_bal > 0
	""", (company,))
	total_units = float(total_units_res[0][0]) if total_units_res else 0.0

	# 2. Total active locations (PSAs)
	total_locations = frappe.db.count("SMRITI Party Stock Account", {
		"company": company,
		"active": 1
	})

	# 3. Locations with negative balances
	negative_count_res = frappe.db.sql("""
		SELECT COUNT(DISTINCT party_stock_account)
		FROM (
			SELECT ple.party_stock_account, SUM(ple.qty) as item_bal
			FROM `tabSMRITI Party Stock Ledger Entry` ple
			INNER JOIN `tabSMRITI Party Stock Account` psa ON ple.party_stock_account = psa.name
			WHERE psa.company = %s AND psa.active = 1
			GROUP BY ple.party_stock_account, ple.item_code
		) t WHERE item_bal < 0
	""", (company,))
	negative_count = negative_count_res[0][0] if negative_count_res else 0

	# 4. Open exceptions (Pending Reconciliation)
	open_exceptions = frappe.db.sql("""
		SELECT COUNT(*)
		FROM `tabSMRITI PSV Exception Record` er
		INNER JOIN `tabSMRITI Party Stock Account` psa ON er.party_stock_account = psa.name
		WHERE psa.company = %s AND er.status = 'Pending Reconciliation'
	""", (company,))[0][0]

	# 5. Critical alerts (Severity 'Critical' and Pending Reconciliation)
	critical_alerts = frappe.db.sql("""
		SELECT COUNT(*)
		FROM `tabSMRITI PSV Exception Record` er
		INNER JOIN `tabSMRITI Party Stock Account` psa ON er.party_stock_account = psa.name
		WHERE psa.company = %s AND er.status = 'Pending Reconciliation' AND er.severity = 'Critical'
	""", (company,))[0][0]

	return {
		"total_units": total_units,
		"total_locations": total_locations,
		"negative_count": negative_count,
		"open_exceptions": open_exceptions,
		"critical_alerts": critical_alerts
	}

@frappe.whitelist()
def get_party_balance_detail(company, party_stock_account):
	"""
	Returns list of dicts with item_code and balance for all items at a location.
	Uses a single aggregate SQL GROUP BY query.
	"""
	result = frappe.db.sql("""
		SELECT ple.item_code, SUM(ple.qty) as balance
		FROM `tabSMRITI Party Stock Ledger Entry` ple
		INNER JOIN `tabSMRITI Party Stock Account` psa ON ple.party_stock_account = psa.name
		WHERE psa.company = %s AND ple.party_stock_account = %s
		GROUP BY ple.item_code
	""", (company, party_stock_account), as_dict=True)

	for r in result:
		r["balance"] = float(r["balance"]) if r["balance"] is not None else 0.0

	return result

@frappe.whitelist()
def get_reorder_dashboard_data(company):
	"""
	Returns Top 10 replenishment needs across all active PSAs.
	Sorted by priority order (Critical -> High -> Medium -> Low) and recommended_qty descending.
	"""
	# Get all active PSAs for the company
	psas = frappe.get_all("SMRITI Party Stock Account",
		filters={"company": company, "active": 1},
		fields=["name"]
	)

	all_recommendations = []

	# Priority weighting for sorting
	priority_weight = {
		"Critical": 4,
		"High": 3,
		"Medium": 2,
		"Low": 1
	}

	for psa in psas:
		psa_name = psa.name
		balances = get_bulk_party_balances(psa_name)

		# For each item, retrieve reorder recommendation
		for item_code in balances.keys():
			reco = get_reorder_recommendation(company, psa_name, item_code)
			if reco and reco.get("recommended_qty", 0) > 0:
				all_recommendations.append({
					"location": psa_name,
					"item_code": item_code,
					"current_balance": reco.get("current_balance", 0.0),
					"weekly_sale_avg": reco.get("weekly_sale_avg", 0.0),
					"days_cover": reco.get("days_cover", 0.0),
					"reorder_level": reco.get("reorder_level", 0.0),
					"recommended_qty": reco.get("recommended_qty", 0.0),
					"priority": reco.get("priority", "Low"),
					"priority_weight": priority_weight.get(reco.get("priority", "Low"), 0)
				})

	# Sort by priority weight desc, then by recommended_qty desc
	all_recommendations.sort(key=lambda x: (x["priority_weight"], x["recommended_qty"]), reverse=True)

	# Clean up priority weight field
	for item in all_recommendations:
		item.pop("priority_weight", None)

	return all_recommendations[:10]
