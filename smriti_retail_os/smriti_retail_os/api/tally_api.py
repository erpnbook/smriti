# -*- coding: utf-8 -*-
# Copyright (c) 2026, AITDL NETWORK & ERPNbook.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from smriti_retail_os.smriti_retail_os.services import tally_service

@frappe.whitelist()
def get_settings():
	"""Retrieves or creates SMRITI Tally Settings."""
	if not frappe.db.exists("DocType", "SMRITI Tally Settings"):
		return {}
	
	doc = frappe.get_single("SMRITI Tally Settings")
	return doc.as_dict()

@frappe.whitelist()
def save_settings(settings_dict):
	"""Saves the SMRITI Tally Settings document."""
	if isinstance(settings_dict, str):
		import json
		settings_dict = json.loads(settings_dict)

	doc = frappe.get_single("SMRITI Tally Settings")
	doc.update(settings_dict)
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"status": "Success", "message": _("Tally Settings saved successfully.")}

@frappe.whitelist()
def get_pending_vouchers(from_date, to_date):
	"""Retrieves Sales Invoices for the date range along with sync status."""
	invoices = frappe.db.get_all(
		"Sales Invoice",
		filters={"posting_date": ["between", [from_date, to_date]], "docstatus": 1},
		fields=["name", "posting_date", "customer", "grand_total", "is_pos"],
		order_by="posting_date asc, name asc"
	)

	# Fetch existing success logs to mark them
	synced_names = frappe.db.get_all(
		"SMRITI Tally Sync Log",
		filters={"status": "Success", "posting_date": ["between", [from_date, to_date]]},
		fields=["reference_name"],
		pluck="reference_name"
	)

	for inv in invoices:
		inv["status"] = "Synced" if inv["name"] in synced_names else "Pending"
	
	return invoices

@frappe.whitelist()
def export_bulk_xml(from_date, to_date, invoice_names=None):
	"""Generates bulk Tally-compliant XML voucher payload for the date range."""
	if isinstance(invoice_names, str):
		import json
		invoice_names = json.loads(invoice_names)

	filters = {"posting_date": ["between", [from_date, to_date]], "docstatus": 1}
	if invoice_names:
		filters["name"] = ["in", invoice_names]

	invoices = frappe.db.get_all("Sales Invoice", filters=filters, pluck="name")
	if not invoices:
		frappe.throw(_("No submitted Sales Invoices found for the selected criteria."))

	settings = tally_service.get_settings()
	company_name = settings.tally_company or "SMRITI Company"

	# Build bulk import structure
	xml_lines = [
		"<ENVELOPE>",
		"  <HEADER>",
		"    <TALLYREQUEST>Import Data</TALLYREQUEST>",
		"  </HEADER>",
		"  <BODY>",
		"    <IMPORTDATA>",
		"      <REQUESTDESC>",
		"        <REPORTNAME>Vouchers</REPORTNAME>",
		"        <STATICVARIABLES>",
		f"          <SVCOMPANYNAME>{company_name}</SVCOMPANYNAME>",
		"        </STATICVARIABLES>",
		"      </REQUESTDESC>",
		"      <REQUESTDATA>"
	]

	for name in invoices:
		# Extract only voucher body message
		inv_xml = tally_service.generate_sales_voucher_xml(name, settings)
		# Parse out the TALLYMESSAGE block
		start_idx = inv_xml.find("<TALLYMESSAGE")
		end_idx = inv_xml.find("</TALLYMESSAGE>")
		if start_idx != -1 and end_idx != -1:
			msg_block = inv_xml[start_idx:end_idx + len("</TALLYMESSAGE>")]
			xml_lines.append(msg_block)

	xml_lines.extend([
		"      </REQUESTDATA>",
		"    </IMPORTDATA>",
		"  </BODY>",
		"</ENVELOPE>"
	])

	bulk_xml = "\r\n".join(xml_lines)
	
	# Set download headers
	frappe.response.filename = f"Tally_Import_{from_date}_to_{to_date}.xml"
	frappe.response.filecontent = bulk_xml
	frappe.response.type = "download"

@frappe.whitelist()
def sync_to_tally(from_date, to_date, invoice_names=None):
	"""Directly posts selected/all invoices for a date range to the Tally HTTP port."""
	if isinstance(invoice_names, str):
		import json
		invoice_names = json.loads(invoice_names)

	filters = {"posting_date": ["between", [from_date, to_date]], "docstatus": 1}
	if invoice_names:
		filters["name"] = ["in", invoice_names]

	invoices = frappe.db.get_all("Sales Invoice", filters=filters, fields=["name", "posting_date"])
	if not invoices:
		return {"status": "Failed", "message": _("No submitted Sales Invoices found to sync.")}

	settings = tally_service.get_settings()
	
	# Auto-create mapped settings ledgers in Tally if enabled
	if settings.get("auto_create_ledgers"):
		if settings.get("sales_ledger"):
			tally_service.create_ledger_in_tally(settings.get("sales_ledger"), "Sales Accounts", settings)
		if settings.get("cash_ledger"):
			tally_service.create_ledger_in_tally(settings.get("cash_ledger"), "Cash-in-Hand", settings)
		if settings.get("bank_ledger"):
			tally_service.create_ledger_in_tally(settings.get("bank_ledger"), "Bank Accounts", settings)
		if settings.get("cgst_ledger"):
			tally_service.create_ledger_in_tally(settings.get("cgst_ledger"), "Duties & Taxes", settings)
		if settings.get("sgst_ledger"):
			tally_service.create_ledger_in_tally(settings.get("sgst_ledger"), "Duties & Taxes", settings)
		if settings.get("igst_ledger"):
			tally_service.create_ledger_in_tally(settings.get("igst_ledger"), "Duties & Taxes", settings)

	success_count = 0
	failed_count = 0
	last_error = ""

	for inv in invoices:
		# Check if already synced successfully
		if frappe.db.exists("SMRITI Tally Sync Log", {"reference_name": inv.name, "status": "Success"}):
			continue

		# Auto-create missing customer ledgers in Tally if enabled and it is a non-POS invoice
		if settings.get("auto_create_ledgers"):
			is_pos = frappe.db.get_value("Sales Invoice", inv.name, "is_pos")
			if not is_pos:
				customer_name = frappe.db.get_value("Sales Invoice", inv.name, "customer")
				tally_service.create_ledger_in_tally(customer_name, "Sundry Debtors", settings)

		xml_payload = tally_service.generate_sales_voucher_xml(inv.name, settings)
		res = tally_service.post_to_tally(xml_payload, settings)

		# Create Sync Log Entry
		log_doc = frappe.new_doc("SMRITI Tally Sync Log")
		log_doc.posting_date = inv.posting_date
		log_doc.voucher_type = "Sales"
		log_doc.reference_doctype = "Sales Invoice"
		log_doc.reference_name = inv.name
		log_doc.status = res["status"]
		log_doc.response = res["response"]
		log_doc.insert(ignore_permissions=True)
		
		if res["status"] == "Success":
			success_count += 1
		else:
			failed_count += 1
			last_error = res["response"]

	frappe.db.commit()

	msg = _("Synced {0} invoice(s) successfully.").format(success_count)
	if failed_count > 0:
		msg += " " + _("Failed to sync {0} invoice(s).").format(failed_count)

	return {
		"status": "Success" if failed_count == 0 else "Failed",
		"message": msg,
		"last_error": last_error
	}

@frappe.whitelist()
def get_sync_logs(limit=50):
	"""Retrieves the latest Tally sync logs."""
	return frappe.db.get_all(
		"SMRITI Tally Sync Log",
		fields=["name", "posting_date", "voucher_type", "reference_name", "status", "response"],
		order_by="creation desc",
		limit=limit
	)
