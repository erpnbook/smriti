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
	# reviewed-ignore-permissions: bypass for whitelisted api endpoint
	doc.save(ignore_permissions=True)
	frappe.db.commit()
	return {"status": "Success", "message": _("Tally Settings saved successfully.")}

@frappe.whitelist()
def get_pending_vouchers(from_date, to_date, voucher_type="Sales"):
	"""Retrieves vouchers (Sales, Purchase, Debit/Credit Notes, Receipt/Payment entries) with sync status."""
	if voucher_type in ("Receipt", "Payment"):
		doctype = "Payment Entry"
		ptype = "Receive" if voucher_type == "Receipt" else "Pay"
		party_type = "Customer" if voucher_type == "Receipt" else "Supplier"
		filters = {
			"posting_date": ["between", [from_date, to_date]],
			"docstatus": 1,
			"payment_type": ptype,
			"party_type": party_type
		}
		invoices = frappe.db.get_all(
			doctype,
			filters=filters,
			fields=["name", "posting_date", "party as customer", "paid_amount as grand_total", "0 as is_pos"],
			order_by="posting_date asc, name asc"
		)
	else:
		doctype = "Sales Invoice" if voucher_type in ("Sales", "Credit Note") else "Purchase Invoice"
		is_return = 1 if voucher_type in ("Credit Note", "Debit Note") else 0
		filters = {
			"posting_date": ["between", [from_date, to_date]],
			"docstatus": 1,
			"is_return": is_return
		}
		party_field = "customer" if doctype == "Sales Invoice" else "supplier"
		invoices = frappe.db.get_all(
			doctype,
			filters=filters,
			fields=["name", "posting_date", f"{party_field} as customer", "grand_total", "is_pos" if doctype == "Sales Invoice" else "0 as is_pos"],
			order_by="posting_date asc, name asc"
		)

	# Fetch existing success logs to mark them
	synced_names = frappe.db.get_all(
		"SMRITI Tally Sync Log",
		filters={"status": "Success", "posting_date": ["between", [from_date, to_date]], "voucher_type": voucher_type},
		fields=["reference_name"],
		pluck="reference_name"
	)

	for inv in invoices:
		inv["status"] = "Synced" if inv["name"] in synced_names else "Pending"
		inv["voucher_type"] = voucher_type
	
	return invoices

@frappe.whitelist()
def export_bulk_xml(from_date, to_date, invoice_names=None, voucher_type="Sales"):
	"""Generates bulk Tally-compliant XML voucher payload for the date range."""
	if isinstance(invoice_names, str):
		import json
		invoice_names = json.loads(invoice_names)

	if voucher_type in ("Receipt", "Payment"):
		doctype = "Payment Entry"
		ptype = "Receive" if voucher_type == "Receipt" else "Pay"
		party_type = "Customer" if voucher_type == "Receipt" else "Supplier"
		filters = {
			"posting_date": ["between", [from_date, to_date]],
			"docstatus": 1,
			"payment_type": ptype,
			"party_type": party_type
		}
	else:
		doctype = "Sales Invoice" if voucher_type in ("Sales", "Credit Note") else "Purchase Invoice"
		is_return = 1 if voucher_type in ("Credit Note", "Debit Note") else 0
		filters = {
			"posting_date": ["between", [from_date, to_date]],
			"docstatus": 1,
			"is_return": is_return
		}

	if invoice_names:
		filters["name"] = ["in", invoice_names]

	invoices = frappe.db.get_all(doctype, filters=filters, pluck="name")
	if not invoices:
		frappe.throw(_("No submitted vouchers found for the selected criteria."))

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
		inv_xml = tally_service.generate_voucher_xml(doctype, name, settings)
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
	
	frappe.response.filename = f"Tally_{voucher_type}_Import_{from_date}_to_{to_date}.xml"
	frappe.response.filecontent = bulk_xml
	frappe.response.type = "download"

@frappe.whitelist()
def sync_to_tally(from_date, to_date, invoice_names=None, voucher_type="Sales", force=0):
	"""Directly posts selected/all vouchers for a date range to the Tally HTTP port."""
	if isinstance(invoice_names, str):
		import json
		invoice_names = json.loads(invoice_names)

	if voucher_type in ("Receipt", "Payment"):
		doctype = "Payment Entry"
		ptype = "Receive" if voucher_type == "Receipt" else "Pay"
		party_type = "Customer" if voucher_type == "Receipt" else "Supplier"
		filters = {
			"posting_date": ["between", [from_date, to_date]],
			"docstatus": 1,
			"payment_type": ptype,
			"party_type": party_type
		}
	else:
		doctype = "Sales Invoice" if voucher_type in ("Sales", "Credit Note") else "Purchase Invoice"
		is_return = 1 if voucher_type in ("Credit Note", "Debit Note") else 0
		filters = {
			"posting_date": ["between", [from_date, to_date]],
			"docstatus": 1,
			"is_return": is_return
		}

	if invoice_names:
		filters["name"] = ["in", invoice_names]

	invoices = frappe.db.get_all(doctype, filters=filters, fields=["name", "posting_date"])
	if not invoices:
		return {"status": "Failed", "message": _("No submitted vouchers found to sync.")}

	settings = tally_service.get_settings()
	
	# Auto-create mapped settings ledgers in Tally if enabled
	if settings.get("auto_create_ledgers"):
		if settings.get("sales_ledger"):
			tally_service.create_ledger_in_tally(settings.get("sales_ledger"), "Sales Accounts", settings)
		if settings.get("purchase_ledger"):
			tally_service.create_ledger_in_tally(settings.get("purchase_ledger"), "Purchase Accounts", settings)
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
		if not frappe.utils.cint(force):
			if frappe.db.exists("SMRITI Tally Sync Log", {"reference_name": inv.name, "status": "Success"}):
				continue

		# Check for zero-value vouchers
		total_amt = 0.0
		if doctype == "Payment Entry":
			total_amt = float(frappe.db.get_value("Payment Entry", inv.name, "paid_amount") or 0.0)
		else:
			total_amt = float(frappe.db.get_value(doctype, inv.name, "grand_total") or 0.0)

		if total_amt == 0.0:
			log_doc = frappe.new_doc("SMRITI Tally Sync Log")
			log_doc.posting_date = inv.posting_date
			log_doc.voucher_type = voucher_type
			log_doc.reference_doctype = doctype
			log_doc.reference_name = inv.name
			log_doc.status = "Success"
			log_doc.response = "Success (Skipped: Zero-value voucher)"
			# reviewed-ignore-permissions: bypass for whitelisted api endpoint
			log_doc.insert(ignore_permissions=True)
			success_count += 1
			continue

		# Auto-create missing customer/supplier ledgers in Tally if enabled
		if settings.get("auto_create_ledgers"):
			if doctype == "Sales Invoice":
				is_pos = frappe.db.get_value("Sales Invoice", inv.name, "is_pos")
				if not is_pos:
					customer_name = frappe.db.get_value("Sales Invoice", inv.name, "customer")
					tally_service.create_ledger_in_tally(customer_name, "Sundry Debtors", settings)
			elif doctype == "Purchase Invoice":
				supplier_name = frappe.db.get_value("Purchase Invoice", inv.name, "supplier")
				tally_service.create_ledger_in_tally(supplier_name, "Sundry Creditors", settings)
			elif doctype == "Payment Entry":
				pe_party_type = frappe.db.get_value("Payment Entry", inv.name, "party_type")
				pe_party = frappe.db.get_value("Payment Entry", inv.name, "party")
				parent_group = "Sundry Debtors" if pe_party_type == "Customer" else "Sundry Creditors"
				tally_service.create_ledger_in_tally(pe_party, parent_group, settings)

		xml_payload = tally_service.generate_voucher_xml(doctype, inv.name, settings)
		res = tally_service.post_to_tally(xml_payload, settings)

		# Create Sync Log Entry
		log_doc = frappe.new_doc("SMRITI Tally Sync Log")
		log_doc.posting_date = inv.posting_date
		log_doc.voucher_type = voucher_type
		log_doc.reference_doctype = doctype
		log_doc.reference_name = inv.name
		log_doc.status = res["status"]
		log_doc.response = res["response"]
		# reviewed-ignore-permissions: bypass for whitelisted api endpoint
		log_doc.insert(ignore_permissions=True)
		
		if res["status"] == "Success":
			success_count += 1
		else:
			failed_count += 1
			last_error = res["response"]

	frappe.db.commit()

	msg = _("Synced {0} voucher(s) successfully.").format(success_count)
	if failed_count > 0:
		msg += " " + _("Failed to sync {0} voucher(s).").format(failed_count)

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

@frappe.whitelist()
def compare_sync_status(from_date, to_date, voucher_type="Sales"):
	"""Compares ERPNext transactions with SMRITI Tally Sync Logs to find missing vouchers."""
	# 1. Fetch pending vouchers using get_pending_vouchers
	all_vouchers = get_pending_vouchers(from_date, to_date, voucher_type)
	
	# 2. Extract their names
	voucher_names = [v["name"] for v in all_vouchers] if all_vouchers else []
	
	if not voucher_names:
		return {
			"total": 0,
			"synced": 0,
			"missing": 0,
			"missing_list": []
		}
	
	# 3. Find which ones are successfully logged in SMRITI Tally Sync Log
	synced_logs = frappe.db.get_all(
		"SMRITI Tally Sync Log",
		filters={"reference_name": ["in", voucher_names], "status": "Success"},
		fields=["reference_name"]
	)
	synced_names = {log.reference_name for log in synced_logs}
	
	missing_list = [v for v in all_vouchers if v["name"] not in synced_names]
	
	return {
		"total": len(all_vouchers),
		"synced": len(synced_names),
		"missing": len(missing_list),
		"missing_list": missing_list
	}
