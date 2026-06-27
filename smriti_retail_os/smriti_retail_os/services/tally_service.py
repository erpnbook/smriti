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
	"""Generates a Tally-compliant XML Voucher payload for a Sales Invoice."""
	if not settings:
		settings = get_settings()

	invoice_doc = frappe.get_doc("Sales Invoice", invoice) if isinstance(invoice, str) else invoice
	date_str = get_tally_date_format(invoice_doc.posting_date)
	
	company_name = settings.tally_company or "SMRITI Company"
	sales_ledger = settings.sales_ledger or "Sales Account"
	cgst_ledger = settings.cgst_ledger or "CGST"
	sgst_ledger = settings.sgst_ledger or "SGST"
	igst_ledger = settings.igst_ledger or "IGST"

	# Determine customer ledger (for POS, it could be Cash/Bank, or standard Customer)
	party_ledger = invoice_doc.customer
	if invoice_doc.is_pos:
		# If POS, check mode of payment to resolve Cash or Bank ledger mapping
		if invoice_doc.payments:
			first_pay = invoice_doc.payments[0]
			if "cash" in (first_pay.mode_of_payment or "").lower():
				party_ledger = settings.cash_ledger or "Cash"
			else:
				party_ledger = settings.bank_ledger or "Bank"
		else:
			party_ledger = settings.cash_ledger or "Cash"

	# Calculate tax breakdowns
	cgst_amt = 0.0
	sgst_amt = 0.0
	igst_amt = 0.0
	for tax in invoice_doc.get("taxes", []):
		lbl = (tax.description or tax.account_head or "").lower()
		if "cgst" in lbl:
			cgst_amt += float(tax.tax_amount or 0.0)
		elif "sgst" in lbl:
			sgst_amt += float(tax.tax_amount or 0.0)
		elif "igst" in lbl:
			igst_amt += float(tax.tax_amount or 0.0)

	total_amount = float(invoice_doc.grand_total or 0.0)
	net_amount = float(invoice_doc.net_total or 0.0)

	# Format amounts:
	# Debit (Party/Customer): ISDEEMEDPOSITIVE = Yes, AMOUNT = -Total
	# Credit (Sales): ISDEEMEDPOSITIVE = No, AMOUNT = Net
	# Credit (Taxes): ISDEEMEDPOSITIVE = No, AMOUNT = Tax

	# XML Template for Voucher Import
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
		f'          <VOUCHER VCHTYPE="Sales" ACTION="Create" OBJVIEW="Invoice">',
		f"            <DATE>{date_str}</DATE>",
		f"            <VOUCHERNUMBER>{invoice_doc.name}</VOUCHERNUMBER>",
		f"            <PARTYLEDGERNAME>{party_ledger}</PARTYLEDGERNAME>",
		f"            <EFFECTIVEDATE>{date_str}</EFFECTIVEDATE>",
		# Debit Entry (Customer / Cash / Bank)
		"            <ALLLEDGERENTRIES.LIST>",
		f"              <LEDGERNAME>{party_ledger}</LEDGERNAME>",
		"              <ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>",
		f"              <AMOUNT>-{total_amount:.2f}</AMOUNT>",
		"            </ALLLEDGERENTRIES.LIST>",
		# Credit Entry (Sales)
		"            <ALLLEDGERENTRIES.LIST>",
		f"              <LEDGERNAME>{sales_ledger}</LEDGERNAME>",
		"              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>",
		f"              <AMOUNT>{net_amount:.2f}</AMOUNT>",
		"            </ALLLEDGERENTRIES.LIST>"
	]

	# Add CGST Credit if present
	if cgst_amt > 0:
		xml_lines.extend([
			"            <ALLLEDGERENTRIES.LIST>",
			f"              <LEDGERNAME>{cgst_ledger}</LEDGERNAME>",
			"              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>",
			f"              <AMOUNT>{cgst_amt:.2f}</AMOUNT>",
			"            </ALLLEDGERENTRIES.LIST>"
		])

	# Add SGST Credit if present
	if sgst_amt > 0:
		xml_lines.extend([
			"            <ALLLEDGERENTRIES.LIST>",
			f"              <LEDGERNAME>{sgst_ledger}</LEDGERNAME>",
			"              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>",
			f"              <AMOUNT>{sgst_amt:.2f}</AMOUNT>",
			"            </ALLLEDGERENTRIES.LIST>"
		])

	# Add IGST Credit if present
	if igst_amt > 0:
		xml_lines.extend([
			"            <ALLLEDGERENTRIES.LIST>",
			f"              <LEDGERNAME>{igst_ledger}</LEDGERNAME>",
			"              <ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>",
			f"              <AMOUNT>{igst_amt:.2f}</AMOUNT>",
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
