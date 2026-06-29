# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/negative_stock/service/hooks.py
# @description: Document event hooks for SMRITI Negative Stock Management.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-29
# @version: 1.9.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from smriti_retail_os.negative_stock.service.recovery_service import SMRITINegativeStockRecoveryService

def handle_transaction_submit(doc, method=None):
	"""
	Hook executed on_submit of Purchase Receipt, Stock Entry, and Stock Reconciliation.
	"""
	# Extract items and warehouses from the submitted transaction
	if not hasattr(doc, "items"):
		return

	# Set of unique (item_code, warehouse) tuples in this transaction
	item_warehouses = set()
	for item in doc.items:
		if getattr(item, "item_code", None) and getattr(item, "warehouse", None):
			item_warehouses.add((item.item_code, item.warehouse))

	# Trigger check and recovery for each matched item + warehouse
	for item_code, warehouse in item_warehouses:
		srv = SMRITINegativeStockRecoveryService(item_code, warehouse)
		srv.check_and_recover(
			source_doctype=doc.doctype,
			source_name=doc.name,
			recovery_type="Auto"
		)
