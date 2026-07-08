# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Connectivity Framework (SCF) contributors
# For license information, please see license.txt

import frappe
from smriti_retail_os import smriti
import datetime

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

def generate_voucher_xml(doctype, doc_name, settings):
	"""Generates a Tally-compliant XML Voucher payload for Sales, Purchase, Debit/Credit Notes, and Receipt/Payment entries."""
	doc = smriti.documents.get(doctype, doc_name) if isinstance(doc_name, str) else doc_name
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
			acc_type = smriti.db.get("Account", account_head, "account_type")
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

	# Document details (Sales/Purchase Invoices, Debit/Credit Notes)
	vch_type = "Sales"
	party_ledger = doc.get("customer") or doc.get("supplier")
	total_amount = float(doc.grand_total or 0.0)

	# Map Voucher Types
	if doctype == "Sales Invoice":
		vch_type = "Credit Note" if doc.is_return else "Sales"
	elif doctype == "Purchase Invoice":
		vch_type = "Debit Note" if doc.is_return else "Purchase"

	# Deemed Positive Logic:
	# Sales (Standard): Debit Party (Yes, -Total), Credit Income (No, +Sales), Credit Taxes (No, +Tax)
	# Credit Note (Sales Return): Credit Party (No, +Total), Debit Income (Yes, -Sales), Debit Taxes (Yes, -Tax)
	# Purchase (Standard): Credit Party (No, +Total), Debit Expense (Yes, -Purchase), Debit Taxes (Yes, -Tax)
	# Debit Note (Purchase Return): Debit Party (Yes, -Total), Credit Expense (No, +Purchase), Credit Taxes (No, +Tax)
	
	if vch_type == "Sales":
		party_deemed = "Yes"
		party_amt = f"-{total_amount:.2f}"
		contra_deemed = "No"
		tax_deemed = "No"
		sign_mult = 1.0
	elif vch_type == "Credit Note":
		party_deemed = "No"
		party_amt = f"{total_amount:.2f}"
		contra_deemed = "Yes"
		tax_deemed = "Yes"
		sign_mult = -1.0
	elif vch_type == "Purchase":
		party_deemed = "No"
		party_amt = f"{total_amount:.2f}"
		contra_deemed = "Yes"
		tax_deemed = "Yes"
		sign_mult = -1.0
	else: # Debit Note
		party_deemed = "Yes"
		party_amt = f"-{total_amount:.2f}"
		contra_deemed = "No"
		tax_deemed = "No"
		sign_mult = 1.0

	contra_ledger = sales_ledger if doctype == "Sales Invoice" else purchase_ledger
	net_amount = float(doc.total or 0.0)
	cgst_amount = float(doc.get("total_cgst") or 0.0)
	sgst_amount = float(doc.get("total_sgst") or 0.0)
	igst_amount = float(doc.get("total_igst") or 0.0)

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
		# Contra/Income/Expense Entry
		"            <ALLLEDGERENTRIES.LIST>",
		f"              <LEDGERNAME>{contra_ledger}</LEDGERNAME>",
		f"              <ISDEEMEDPOSITIVE>{contra_deemed}</ISDEEMEDPOSITIVE>",
		f"              <AMOUNT>{(net_amount * sign_mult):.2f}</AMOUNT>",
		"            </ALLLEDGERENTRIES.LIST>"
	]

	# Taxes (Skip zero values)
	if cgst_amount > 0:
		xml_lines.extend([
			"            <ALLLEDGERENTRIES.LIST>",
			f"              <LEDGERNAME>{cgst_ledger}</LEDGERNAME>",
			f"              <ISDEEMEDPOSITIVE>{tax_deemed}</ISDEEMEDPOSITIVE>",
			f"              <AMOUNT>{(cgst_amount * sign_mult):.2f}</AMOUNT>",
			"            </ALLLEDGERENTRIES.LIST>"
		])
	if sgst_amount > 0:
		xml_lines.extend([
			"            <ALLLEDGERENTRIES.LIST>",
			f"              <LEDGERNAME>{sgst_ledger}</LEDGERNAME>",
			f"              <ISDEEMEDPOSITIVE>{tax_deemed}</ISDEEMEDPOSITIVE>",
			f"              <AMOUNT>{(sgst_amount * sign_mult):.2f}</AMOUNT>",
			"            </ALLLEDGERENTRIES.LIST>"
		])
	if igst_amount > 0:
		xml_lines.extend([
			"            <ALLLEDGERENTRIES.LIST>",
			f"              <LEDGERNAME>{igst_ledger}</LEDGERNAME>",
			f"              <ISDEEMEDPOSITIVE>{tax_deemed}</ISDEEMEDPOSITIVE>",
			f"              <AMOUNT>{(igst_amount * sign_mult):.2f}</AMOUNT>",
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
