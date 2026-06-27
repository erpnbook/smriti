# -*- coding: utf-8 -*-
# Copyright (c) 2026, AITDL NETWORK & ERPNbook.com and contributors
# For license information, please see license.txt

import frappe
from smriti_retail_os.smriti_retail_os.services.coordination.sync_coordinator import SyncCoordinator
from smriti_retail_os.smriti_retail_os.services.adapters.tally_builders.accounting_builder import (
	generate_voucher_xml as _gen_xml,
	get_tally_date_format as _get_date_fmt
)

def get_settings():
	"""Retrieves the SMRITI Tally Settings doc."""
	if not frappe.db.exists("DocType", "SMRITI Tally Settings"):
		return frappe._dict({
			"tally_url": "http://localhost:9000",
			"tally_company": "SMRITI Company",
			"cash_ledger": "Cash",
			"bank_ledger": "Bank",
			"sales_ledger": "Sales Account",
			"cgst_ledger": "CGST",
			"sgst_ledger": "SGST",
			"igst_ledger": "IGST"
		})
	return frappe.get_doc("SMRITI Tally Settings")

def get_tally_date_format(date_val):
	"""Converts Date or Datetime to YYYYMMDD format."""
	return _get_date_fmt(date_val)

def generate_sales_voucher_xml(invoice, settings=None):
	"""Backward compatibility wrapper for Sales Invoice XML generation."""
	return generate_voucher_xml("Sales Invoice", invoice, settings)

def generate_voucher_xml(doctype, doc_name, settings=None):
	"""Generates a Tally-compliant XML Voucher payload."""
	if not settings:
		settings = get_settings()
	return _gen_xml(doctype, doc_name, settings)

def post_to_tally(xml_payload, settings=None):
	"""Sends the XML payload to Tally Prime Server."""
	if not settings:
		settings = get_settings()
	from smriti_retail_os.smriti_retail_os.services.adapters.tally_transport import TallyTransport
	status_code, res_text = TallyTransport.send_request(settings.tally_url, xml_payload)
	return {
		"status": "Success" if status_code == 200 and "LINEERROR" not in res_text else "Failed",
		"response": res_text
	}

def create_ledger_in_tally(ledger_name, parent_group="Sundry Debtors", settings=None):
	"""Auto-creates a Ledger in Tally."""
	if not settings:
		settings = get_settings()
	coordinator = SyncCoordinator()
	if hasattr(coordinator.adapter, "create_ledger_in_tally"):
		return coordinator.adapter.create_ledger_in_tally(ledger_name, parent_group, settings)
	return False
