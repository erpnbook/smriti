# -*- coding: utf-8 -*-
# Copyright (c) 2026, AITDL NETWORK & ERPNbook.com and contributors
# For license information, please see license.txt

import frappe
from frappe import _
import requests
import datetime

def get_settings():
	"""Retrieves the SMRITI Tally Settings doc."""
	if not frappe.db.exists("DocType", "SMRITI Tally Settings"):
		# Fallback if not migrated yet
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
	if not date_val:
		return datetime.date.today().strftime("%Y%m%d")
	if isinstance(date_val, str):
		try:
			date_val = datetime.datetime.strptime(date_val.split(" ")[0], "%Y-%m-%d").date()
		except Exception:
			return datetime.date.today().strftime("%Y%m%d")
	return date_val.strftime("%Y%m%d")

def generate_sales_voucher_xml(invoice, settings=None):
	"""Backward compatibility wrapper for Sales Invoice XML generation."""
	return generate_voucher_xml("Sales Invoice", invoice, settings)

def generate_voucher_xml(doctype, doc_name, settings=None):
	"""Generates a Tally-compliant XML Voucher payload for Sales, Purchase, Debit/Credit Notes, and Receipt/Payment entries."""
	if not settings:
		settings = get_settings()

	doc = frappe.get_doc(doctype, doc_name) if isinstance(doc_name, str) else doc_name
	date_str = get_tally_date_format(doc.posting_date)

	# Resolve Voucher Number and Reference Number
	vch_number = doc.name
	ref_number = doc.name
	if doctype == "Purchase Invoice" and doc.get("bill_no"):
		vch_number = doc.bill_no
		ref_number = doc.bill_no
	elif doctype == "Payment Entry" and doc.get("reference_no"):
		ref_number = doc.reference_no
	
	# Narration: Mention it is posted from SMRITI Retail OS
	narration = f"Posted from SMRITI Retail OS. Ref: {doc.name}"
	if doc.get("remarks"):
		narration += f" | {doc.remarks}"
	
	company_name = settings.tally_company or "SMRITI Company"
	sales_ledger = settings.sales_ledger or "Sales Account"
	purchase_ledger = settings.purchase_ledger or "Purchase Account"
	cgst_ledger = settings.cgst_ledger or "CGST"
	sgst_ledger = settings.sgst_ledger or "SGST"
	igst_ledger = settings.igst_ledger or "IGST"

	if doctype == "Payment Entry":
		vch_type = "Receipt" if doc.payment_type == "Receive" else "Payment"
		party_ledger = doc.party
		
		# Resolve Cash/Bank Ledger
		account_fieldname = "paid_to" if vch_type == "Receipt" else "paid_from"
		account_head = doc.get(account_fieldname)
		is_cash = False
		if account_head:
			acc_type = frappe.db.get_value("Account", account_head, "account_type")
			if acc_type == "Cash" or "cash" in account_head.lower():
				is_cash = True
		cash_bank_ledger = settings.cash_ledger if is_cash else settings.bank_ledger
		cash_bank_ledger = cash_bank_ledger or ("Cash" if is_cash else "Bank")
		
		total_amount = float(doc.paid_amount or 0.0)
		
		# Decide Sign and Deemed Positive flag:
		# Receipt: Debit Cash/Bank (Yes, -Total), Credit Party (No, +Total)
		# Payment: Debit Party (Yes, -Total), Credit Cash/Bank (No, +Total)
		if vch_type == "Receipt":
			party_deemed = "No"
			party_amt = f"{total_amount:.2f}"
			cb_deemed = "Yes"
			cb_amt = f"-{total_amount:.2f}"
		else:
			party_deemed = "Yes"
			party_amt = f"-{total_amount:.2f}"
			cb_deemed = "No"
			cb_amt = f"{total_amount:.2f}"

		# Build XML lines for Payment Entry
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
			"      <REQUESTDATA>",
			'        <TALLYMESSAGE xmlns:UDF="TallyUDF">',
			f'          <VOUCHER VCHTYPE="{vch_type}" ACTION="Create" OBJVIEW="Invoice">',
			f"            <DATE>{date_str}</DATE>",
			f"            <VOUCHERTYPENAME>{vch_type}</VOUCHERTYPENAME>",
			f"            <VOUCHERNUMBER>{vch_number}</VOUCHERNUMBER>",
			f"            <REFERENCE>{ref_number}</REFERENCE>",
			f"            <PARTYLEDGERNAME>{party_ledger}</PARTYLEDGERNAME>",
			f"            <EFFECTIVEDATE>{date_str}</EFFECTIVEDATE>",
			f"            <NARRATION>{narration}</NARRATION>",
			# Party Entry
			"            <ALLLEDGERENTRIES.LIST>",
			f"              <LEDGERNAME>{party_ledger}</LEDGERNAME>",
			f"              <ISDEEMEDPOSITIVE>{party_deemed}</ISDEEMEDPOSITIVE>",
			f"              <AMOUNT>{party_amt}</AMOUNT>",
			"            </ALLLEDGERENTRIES.LIST>",
			# Cash/Bank Entry
			"            <ALLLEDGERENTRIES.LIST>",
			f"              <LEDGERNAME>{cash_bank_ledger}</LEDGERNAME>",
			f"              <ISDEEMEDPOSITIVE>{cb_deemed}</ISDEEMEDPOSITIVE>",
			f"              <AMOUNT>{cb_amt}</AMOUNT>",
			"            </ALLLEDGERENTRIES.LIST>",
			"          </VOUCHER>",
			"        </TALLYMESSAGE>",
			"      </REQUESTDATA>",
			"    </IMPORTDATA>",
			"  </BODY>",
			"</ENVELOPE>"
		]
		return "\r\n".join(xml_lines)

	# Determine Voucher Type & Debit/Credit direction for Invoice Doctypes
	is_return = doc.get("is_return") or 0
	
	if doctype == "Sales Invoice":
		vch_type = "Credit Note" if is_return else "Sales"
	else:
		vch_type = "Debit Note" if is_return else "Purchase"

	# Resolve party ledger (Customer or Supplier)
	if doctype == "Sales Invoice":
		party_ledger = doc.customer
		if doc.is_pos:
			if doc.payments:
				first_pay = doc.payments[0]
				if "cash" in (first_pay.mode_of_payment or "").lower():
					party_ledger = settings.cash_ledger or "Cash"
				else:
					party_ledger = settings.bank_ledger or "Bank"
			else:
				party_ledger = settings.cash_ledger or "Cash"
	else:
		party_ledger = doc.supplier

	# Calculate tax breakdowns
	cgst_amt = 0.0
	sgst_amt = 0.0
	igst_amt = 0.0
	for tax in doc.get("taxes", []):
		lbl = (tax.description or tax.account_head or "").lower()
		if "cgst" in lbl:
			cgst_amt += float(tax.tax_amount or 0.0)
		elif "sgst" in lbl:
			sgst_amt += float(tax.tax_amount or 0.0)
		elif "igst" in lbl:
			igst_amt += float(tax.tax_amount or 0.0)

	total_amount = float(doc.grand_total or 0.0)
	net_amount = float(doc.net_total or 0.0)

	# Decide Sign and Deemed Positive flag:
	# Party:
	# - Sales: Debited (Yes, -Total)
	# - Credit Note: Credited (No, +Total)
	# - Purchase: Credited (No, +Total)
	# - Debit Note: Debited (Yes, -Total)
	if (vch_type == "Sales") or (vch_type == "Debit Note"):
		party_deemed = "Yes"
		party_amt = f"-{total_amount:.2f}"
	else:
		party_deemed = "No"
		party_amt = f"{total_amount:.2f}"

	# Revenue (Sales / Purchase):
	# - Sales: Credited (No, +Net)
	# - Credit Note: Debited (Yes, -Net)
	# - Purchase: Debited (Yes, -Net)
	# - Debit Note: Credited (No, +Net)
	rev_ledger = sales_ledger if doctype == "Sales Invoice" else purchase_ledger
	if (vch_type == "Sales") or (vch_type == "Debit Note"):
		rev_deemed = "No"
		rev_amt = f"{net_amount:.2f}"
	else:
		rev_deemed = "Yes"
		rev_amt = f"-{net_amount:.2f}"

	# Taxes (GST):
	# - Sales: Credited (No, +Tax)
	# - Credit Note: Debited (Yes, -Tax)
	# - Purchase: Debited (Yes, -Tax)
	# - Debit Note: Credited (No, +Tax)
	if (vch_type == "Sales") or (vch_type == "Debit Note"):
		tax_deemed = "No"
		tax_sign = ""
	else:
		tax_deemed = "Yes"
		tax_sign = "-"

	# Build XML lines
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
		"      <REQUESTDATA>",
		'        <TALLYMESSAGE xmlns:UDF="TallyUDF">',
		f'          <VOUCHER VCHTYPE="{vch_type}" ACTION="Create" OBJVIEW="Invoice">',
		f"            <DATE>{date_str}</DATE>",
		f"            <VOUCHERTYPENAME>{vch_type}</VOUCHERTYPENAME>",
		f"            <VOUCHERNUMBER>{vch_number}</VOUCHERNUMBER>",
		f"            <REFERENCE>{ref_number}</REFERENCE>",
		f"            <PARTYLEDGERNAME>{party_ledger}</PARTYLEDGERNAME>",
		f"            <EFFECTIVEDATE>{date_str}</EFFECTIVEDATE>",
		f"            <NARRATION>{narration}</NARRATION>",
		# Party Entry
		"            <ALLLEDGERENTRIES.LIST>",
		f"              <LEDGERNAME>{party_ledger}</LEDGERNAME>",
		f"              <ISDEEMEDPOSITIVE>{party_deemed}</ISDEEMEDPOSITIVE>",
		f"              <AMOUNT>{party_amt}</AMOUNT>",
		"            </ALLLEDGERENTRIES.LIST>",
		# Revenue Entry (Sales / Purchase)
		"            <ALLLEDGERENTRIES.LIST>",
		f"              <LEDGERNAME>{rev_ledger}</LEDGERNAME>",
		f"              <ISDEEMEDPOSITIVE>{rev_deemed}</ISDEEMEDPOSITIVE>",
		f"              <AMOUNT>{rev_amt}</AMOUNT>",
		"            </ALLLEDGERENTRIES.LIST>"
	]

	# Add CGST Credit if present
	if cgst_amt > 0:
		xml_lines.extend([
			"            <ALLLEDGERENTRIES.LIST>",
			f"              <LEDGERNAME>{cgst_ledger}</LEDGERNAME>",
			f"              <ISDEEMEDPOSITIVE>{tax_deemed}</ISDEEMEDPOSITIVE>",
			f"              <AMOUNT>{tax_sign}{cgst_amt:.2f}</AMOUNT>",
			"            </ALLLEDGERENTRIES.LIST>"
		])

	# Add SGST Credit if present
	if sgst_amt > 0:
		xml_lines.extend([
			"            <ALLLEDGERENTRIES.LIST>",
			f"              <LEDGERNAME>{sgst_ledger}</LEDGERNAME>",
			f"              <ISDEEMEDPOSITIVE>{tax_deemed}</ISDEEMEDPOSITIVE>",
			f"              <AMOUNT>{tax_sign}{sgst_amt:.2f}</AMOUNT>",
			"            </ALLLEDGERENTRIES.LIST>"
		])

	# Add IGST Credit if present
	if igst_amt > 0:
		xml_lines.extend([
			"            <ALLLEDGERENTRIES.LIST>",
			f"              <LEDGERNAME>{igst_ledger}</LEDGERNAME>",
			f"              <ISDEEMEDPOSITIVE>{tax_deemed}</ISDEEMEDPOSITIVE>",
			f"              <AMOUNT>{tax_sign}{igst_amt:.2f}</AMOUNT>",
			"            </ALLLEDGERENTRIES.LIST>"
		])

	xml_lines.extend([
		"          </VOUCHER>",
		"        </TALLYMESSAGE>",
		"      </REQUESTDATA>",
		"    </IMPORTDATA>",
		"  </BODY>",
		"</ENVELOPE>"
	])

	return "\r\n".join(xml_lines)

def post_to_tally(xml_payload, settings=None):
	"""Sends the XML payload to Tally Prime Server."""
	if not settings:
		settings = get_settings()

	headers = {
		"Content-Type": "text/xml; charset=utf-8",
		"charset": "utf-8"
	}
	
	try:
		res = requests.post(settings.tally_url, data=xml_payload.encode("utf-8"), headers=headers, timeout=10)
		return {
			"status": "Success" if res.status_code == 200 and "LINEERROR" not in res.text else "Failed",
			"response": res.text
		}
	except Exception as e:
		return {
			"status": "Failed",
			"response": str(e)
		}

def create_ledger_in_tally(ledger_name, parent_group="Sundry Debtors", settings=None):
	"""Auto-creates a Ledger in Tally if auto_create_ledgers is enabled."""
	if not settings:
		settings = get_settings()

	xml_lines = [
		"<ENVELOPE>",
		"  <HEADER>",
		"    <TALLYREQUEST>Import Data</TALLYREQUEST>",
		"  </HEADER>",
		"  <BODY>",
		"    <IMPORTDATA>",
		"      <REQUESTDESC>",
		"        <REPORTNAME>All Masters</REPORTNAME>",
		"        <STATICVARIABLES>",
		f"          <SVCOMPANYNAME>{settings.tally_company or 'SMRITI Company'}</SVCOMPANYNAME>",
		"        </STATICVARIABLES>",
		"      </REQUESTDESC>",
		"      <REQUESTDATA>",
		'        <TALLYMESSAGE xmlns:UDF="TallyUDF">',
		f'          <LEDGER NAME="{ledger_name}" ACTION="Create">',
		"            <NAME.LIST>",
		f"              <NAME>{ledger_name}</NAME>",
		"            </NAME.LIST>",
		f"            <PARENT>{parent_group}</PARENT>",
		"          </LEDGER>",
		"        </TALLYMESSAGE>",
		"      </REQUESTDATA>",
		"    </IMPORTDATA>",
		"  </BODY>",
		"</ENVELOPE>"
	]
	xml_payload = "\r\n".join(xml_lines)
	return post_to_tally(xml_payload, settings)

