# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/psv_ledger_entry/psv_ledger_entry.py
# @description: SMRITI DocType controller — Frappe document lifecycle handlers.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import hashlib
import frappe
from frappe.model.document import Document

class PSVLedgerEntry(Document):
	def validate(self):
		if not self.is_new():
			frappe.throw(
				"PSV Ledger entries are immutable. Use a reversal entry to correct.",
				frappe.ValidationError
			)
		
		# Generate unique hash if not already set
		if not self.unique_hash:
			self.hash_version = 1
			# Ensure fields are string values
			company = self.company or ""
			posting_datetime = str(self.posting_datetime or "")
			channel_partner = self.channel_partner or ""
			item_variant = self.item_variant or ""
			qty = str(self.qty or 0.0)
			transaction_type = self.transaction_type or ""
			voucher_type = self.voucher_type or ""
			voucher_no = self.voucher_no or ""
			
			raw_string = f"{company}{posting_datetime}{channel_partner}{item_variant}{qty}{transaction_type}{voucher_type}{voucher_no}"
			self.unique_hash = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

	def on_trash(self):
		frappe.throw(
			"PSV Ledger entries cannot be deleted. Use a reversal entry to correct.",
			frappe.ValidationError
		)
