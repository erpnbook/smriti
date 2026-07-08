# -*- coding: utf-8 -*-
# Copyright (c) 2026, AITDL NETWORK & ERPNbook.com and contributors
# For license information, please see license.txt

import frappe
from smriti_retail_os import smriti
import unittest
from smriti_retail_os.smriti_retail_os.services import tally_service
from smriti_retail_os.smriti_retail_os.api import tally_api

class TestTallyIntegration(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		from smriti_retail_os.setup import setup_smriti_retail_os
		setup_smriti_retail_os()
		smriti.db.commit()

	def _ensure_fiscal_year_for_company(self, company):
		fy_name = "2026-2027"
		if not smriti.db.exists("Fiscal Year", fy_name):
			fy = smriti.documents.new("Fiscal Year")
			fy.year = fy_name
			fy.year_start_date = "2026-04-01"
			fy.year_end_date = "2027-03-31"
			fy.insert(ignore_permissions=True)
		else:
			fy = smriti.documents.get("Fiscal Year", fy_name)
		
		if fy.companies:
			company_names = [c.company for c in fy.companies]
			if company not in company_names:
				fy.append("companies", {"company": company})
				fy.save(ignore_permissions=True)
		else:
			fy.append("companies", {"company": company})
			fy.save(ignore_permissions=True)
			
		smriti.db.commit()

	def setUp(self):
		# Provision test Company if it doesn't exist
		self.company = "Test SMRITI Company"
		if not smriti.db.exists("Company", self.company):
			comp = smriti.documents.new("Company")
			comp.company_name = self.company
			comp.default_currency = "INR"
			comp.country = "India"
			comp.insert(ignore_permissions=True)
			smriti.db.commit()
		self._ensure_fiscal_year_for_company(self.company)

		cust_group = smriti.db.get("Customer Group", {"is_group": 0}) or "Individual"
		territory = smriti.db.get("Territory", {"is_group": 0}) or "All Territories"

		# Create a dummy customer
		if not smriti.db.exists("Customer", "Tally Test Customer"):
			cust = smriti.documents.new("Customer")
			cust.customer_name = "Tally Test Customer"
			cust.customer_group = cust_group
			cust.territory = territory
			cust.insert(ignore_permissions=True)

		# Find a valid sales item (excluding template items with variants)
		item_code = smriti.db.get("Item", {"is_sales_item": 1, "disabled": 0, "has_variants": 0})

		if not item_code:
			# Create a dummy item
			item = smriti.documents.new("Item")
			item.item_code = "Tally Test Item"
			item.item_name = "Tally Test Item"
			item.item_group = smriti.db.get("Item Group", {"is_group": 0}) or "All Item Groups"
			item.is_stock_item = 0
			item.insert(ignore_permissions=True)
			item_code = "Tally Test Item"

		# Get income account
		income_account = smriti.db.get("Account", {"company": self.company, "account_type": "Income"})
		if not income_account:
			income_account = smriti.db.get("Account", {"company": self.company, "is_group": 0})

		# Get warehouse
		warehouse = smriti.db.get("Warehouse", {"company": self.company})
		if not warehouse:
			wh = smriti.documents.new("Warehouse")
			wh.warehouse_name = "Test WH"
			wh.company = self.company
			wh.insert(ignore_permissions=True)
			warehouse = wh.name
			smriti.db.commit()

		# Ensure cost center exists for the test company
		cost_center = smriti.db.get("Company", self.company, "cost_center")
		if not cost_center:
			cost_center = smriti.db.get("Cost Center", {"company": self.company, "is_group": 0}, "name")
		if not cost_center:
			# The root cost center name MUST equal company name to pass parent_cost_center check!
			parent_cc = smriti.db.get("Cost Center", {"cost_center_name": self.company}, "name")
			if not parent_cc:
				pcc = smriti.documents.new("Cost Center")
				pcc.cost_center_name = self.company
				pcc.company = self.company
				pcc.is_group = 1
				pcc.flags.ignore_mandatory = True # Bypass parent_cost_center check on Root CC!
				pcc.insert(ignore_permissions=True)
				parent_cc = pcc.name
			
			cc = smriti.documents.new("Cost Center")
			cc.cost_center_name = "Test Cost Center"
			cc.company = self.company
			cc.is_group = 0
			cc.parent_cost_center = parent_cc
			cc.insert(ignore_permissions=True)
			cost_center = cc.name

		# Ensure cost center and round off account are set on Company
		round_off_account = smriti.db.get("Account", {"company": self.company, "account_name": "Round Off", "is_group": 0})
		if not round_off_account:
			parent_exp = smriti.db.get("Account", {"company": self.company, "root_type": "Expense", "is_group": 1})
			if not parent_exp:
				parent_exp = smriti.db.get("Account", {"company": self.company, "is_group": 1})
			acc = smriti.documents.new("Account")
			acc.account_name = "Round Off"
			acc.parent_account = parent_exp
			acc.company = self.company
			acc.insert(ignore_permissions=True)
			round_off_account = acc.name
		
		smriti.db.set_value("Company", self.company, {
			"round_off_cost_center": cost_center,
			"round_off_account": round_off_account
		})

		# Create a dummy Sales Invoice
		self.invoice = smriti.documents.new("Sales Invoice")
		self.invoice.customer = "Tally Test Customer"
		self.invoice.company = self.company
		self.invoice.posting_date = "2026-06-27"
		
		# Add a dummy item
		self.invoice.append("items", {
			"item_code": item_code,
			"qty": 1,
			"rate": 100.0,
			"income_account": income_account,
			"warehouse": warehouse,
			"cost_center": cost_center
		})
		
		# Insert and submit
		self.invoice.insert(ignore_permissions=True)
		self.invoice.submit()

	def tearDown(self):
		# Cancel and delete the test invoice
		if hasattr(self, "invoice") and self.invoice:
			try:
				self.invoice.cancel()
				frappe.delete_doc("Sales Invoice", self.invoice.name, ignore_permissions=True)
			except Exception:
				pass

	def test_get_save_settings(self):
		"""Tests retrieving and saving settings."""
		settings = tally_api.get_settings()
		self.assertIsNotNone(settings)
		
		# Save new values
		test_url = "http://localhost:9999"
		test_company = "Test Tally Company Ltd"
		
		res = tally_api.save_settings({
			"tally_url": test_url,
			"tally_company": test_company,
			"cash_ledger": "Cash",
			"bank_ledger": "Bank",
			"sales_ledger": "Sales Account"
		})
		self.assertEqual(res["status"], "Success")
		
		updated = tally_api.get_settings()
		self.assertEqual(updated["tally_url"], test_url)
		self.assertEqual(updated["tally_company"], test_company)

	def test_xml_generation(self):
		"""Tests generating Tally XML format from a Sales Invoice."""
		settings = smriti.documents.get_single("TallySettings")
		settings.tally_company = "Unit Test Tally Company"
		settings.sales_ledger = "Test Sales Account"
		settings.cash_ledger = "Test Cash Ledger"
		settings.save(ignore_permissions=True)
		
		xml_output = tally_service.generate_sales_voucher_xml(self.invoice.name, settings)
		
		# Verify Tally Prime XML structure
		self.assertIn("<ENVELOPE>", xml_output)
		self.assertIn("<TALLYREQUEST>Import Data</TALLYREQUEST>", xml_output)
		self.assertIn(f"<SVCOMPANYNAME>{settings.tally_company}</SVCOMPANYNAME>", xml_output)
		self.assertIn(f"<VOUCHERNUMBER>{self.invoice.name}</VOUCHERNUMBER>", xml_output)
		self.assertIn(f"<LEDGERNAME>{settings.sales_ledger}</LEDGERNAME>", xml_output)
		self.assertIn("<ISDEEMEDPOSITIVE>Yes</ISDEEMEDPOSITIVE>", xml_output)
		self.assertIn("<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>", xml_output)

	def test_get_pending_vouchers(self):
		"""Tests loading pending vouchers inside date range."""
		posting_date = self.invoice.posting_date
		vouchers = tally_api.get_pending_vouchers(posting_date, posting_date)
		names = [v.name for v in vouchers]
		self.assertIn(self.invoice.name, names)

	def test_get_sync_logs(self):
		"""Tests getting sync logs list."""
		logs = tally_api.get_sync_logs(limit=5)
		self.assertIsNotNone(logs)

	def test_purchase_voucher_xml(self):
		"""Tests generating Tally XML for a Purchase Invoice."""
		settings = smriti.documents.get_single("TallySettings")
		settings.tally_company = "Purchase Test Company"
		settings.purchase_ledger = "Test Purchase Account"
		
		# In-memory Purchase Invoice doc
		mock_doc = smriti.documents.new("PurchaseInvoice")
		mock_doc.update({
			"name": "PINV-26-00001",
			"posting_date": "2026-06-27",
			"supplier": "Test Supplier",
			"grand_total": 500.0,
			"net_total": 500.0,
			"is_return": 0,
			"taxes": []
		})
		
		xml_output = tally_service.generate_voucher_xml("Purchase Invoice", mock_doc, settings)
		self.assertIn("<VOUCHER VCHTYPE=\"Purchase\"", xml_output)
		self.assertIn("<PARTYLEDGERNAME>Test Supplier</PARTYLEDGERNAME>", xml_output)
		self.assertIn("<LEDGERNAME>Test Purchase Account</LEDGERNAME>", xml_output)

	def test_credit_note_xml(self):
		"""Tests generating Tally XML for a Credit Note."""
		settings = smriti.documents.get_single("TallySettings")
		settings.sales_ledger = "Test Sales Account"
		
		mock_doc = smriti.documents.new("SalesInvoice")
		mock_doc.update({
			"name": "SINV-26-CN001",
			"posting_date": "2026-06-27",
			"customer": "Test Customer",
			"grand_total": 200.0,
			"net_total": 200.0,
			"is_return": 1,
			"taxes": []
		})
		
		xml_output = tally_service.generate_voucher_xml("Sales Invoice", mock_doc, settings)
		self.assertIn("<VOUCHER VCHTYPE=\"Credit Note\"", xml_output)
		self.assertIn("<PARTYLEDGERNAME>Test Customer</PARTYLEDGERNAME>", xml_output)
		self.assertIn("<ISDEEMEDPOSITIVE>No</ISDEEMEDPOSITIVE>", xml_output) # Credit note credit party

	def test_debit_note_xml(self):
		"""Tests generating Tally XML for a Debit Note."""
		settings = smriti.documents.get_single("TallySettings")
		settings.purchase_ledger = "Test Purchase Account"
		
		mock_doc = smriti.documents.new("PurchaseInvoice")
		mock_doc.update({
			"name": "PINV-26-DN001",
			"posting_date": "2026-06-27",
			"supplier": "Test Supplier",
			"grand_total": 300.0,
			"net_total": 300.0,
			"is_return": 1,
			"taxes": []
		})
		
		xml_output = tally_service.generate_voucher_xml("Purchase Invoice", mock_doc, settings)
		self.assertIn("<VOUCHER VCHTYPE=\"Debit Note\"", xml_output)
		self.assertIn("<PARTYLEDGERNAME>Test Supplier</PARTYLEDGERNAME>", xml_output)

	def test_payment_entry_xml(self):
		"""Tests generating Tally XML for Payment Entry Receipt & Payment."""
		settings = smriti.documents.get_single("TallySettings")
		settings.cash_ledger = "Tally Cash"
		settings.bank_ledger = "Tally Bank"
		
		# Receipt (Receive Advance)
		receipt_doc = smriti.documents.new("PaymentEntry")
		receipt_doc.update({
			"name": "PE-26-00001",
			"posting_date": "2026-06-27",
			"payment_type": "Receive",
			"party_type": "Customer",
			"party": "Test Customer",
			"paid_amount": 1000.0,
			"paid_to": "Cash"
		})
		
		xml_receipt = tally_service.generate_voucher_xml("Payment Entry", receipt_doc, settings)
		self.assertIn("<VOUCHER VCHTYPE=\"Receipt\"", xml_receipt)
		self.assertIn("<PARTYLEDGERNAME>Test Customer</PARTYLEDGERNAME>", xml_receipt)
		self.assertIn("<LEDGERNAME>Tally Cash</LEDGERNAME>", xml_receipt)
		
		# Payment (Pay Supplier)
		payment_doc = smriti.documents.new("PaymentEntry")
		payment_doc.update({
			"name": "PE-26-00002",
			"posting_date": "2026-06-27",
			"payment_type": "Pay",
			"party_type": "Supplier",
			"party": "Test Supplier",
			"paid_amount": 2500.0,
			"paid_from": "Bank"
		})
		
		xml_payment = tally_service.generate_voucher_xml("Payment Entry", payment_doc, settings)
		self.assertIn("<VOUCHER VCHTYPE=\"Payment\"", xml_payment)
		self.assertIn("<PARTYLEDGERNAME>Test Supplier</PARTYLEDGERNAME>", xml_payment)
		self.assertIn("<LEDGERNAME>Tally Bank</LEDGERNAME>", xml_payment)
