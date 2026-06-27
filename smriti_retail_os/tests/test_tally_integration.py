# -*- coding: utf-8 -*-
# Copyright (c) 2026, AITDL NETWORK & ERPNbook.com and contributors
# For license information, please see license.txt

import frappe
import unittest
from smriti_retail_os.smriti_retail_os.services import tally_service
from smriti_retail_os.smriti_retail_os.api import tally_api

class TestTallyIntegration(unittest.TestCase):
	@classmethod
	def setUpClass(cls):
		super().setUpClass()
		from smriti_retail_os.setup import setup_smriti_retail_os
		setup_smriti_retail_os()
		frappe.db.commit()

	def setUp(self):
		# Provision test Company if it doesn't exist
		self.company = "Test SMRITI Company"
		if not frappe.db.exists("Company", self.company):
			comp = frappe.new_doc("Company")
			comp.company_name = self.company
			comp.default_currency = "INR"
			comp.country = "India"
			comp.insert(ignore_permissions=True)
			frappe.db.commit()

		cust_group = frappe.db.get_value("Customer Group", {"is_group": 0}) or "Individual"
		territory = frappe.db.get_value("Territory", {"is_group": 0}) or "All Territories"

		# Create a dummy customer
		if not frappe.db.exists("Customer", "Tally Test Customer"):
			cust = frappe.new_doc("Customer")
			cust.customer_name = "Tally Test Customer"
			cust.customer_group = cust_group
			cust.territory = territory
			cust.insert(ignore_permissions=True)

		# Find a valid sales item
		item_code = frappe.db.get_value("Item", {"is_sales_item": 1, "disabled": 0})
		if not item_code:
			# Create a dummy item
			item = frappe.new_doc("Item")
			item.item_code = "Tally Test Item"
			item.item_name = "Tally Test Item"
			item.item_group = frappe.db.get_value("Item Group", {"is_group": 0}) or "All Item Groups"
			item.is_stock_item = 0
			item.insert(ignore_permissions=True)
			item_code = "Tally Test Item"

		# Get income account
		income_account = frappe.db.get_value("Account", {"company": self.company, "account_type": "Income"})
		if not income_account:
			income_account = frappe.db.get_value("Account", {"company": self.company, "is_group": 0})

		# Get warehouse
		warehouse = frappe.db.get_value("Warehouse", {"company": self.company})
		if not warehouse:
			wh = frappe.new_doc("Warehouse")
			wh.warehouse_name = "Test WH"
			wh.company = self.company
			wh.insert(ignore_permissions=True)
			warehouse = wh.name
			frappe.db.commit()

		# Create a dummy Sales Invoice
		self.invoice = frappe.new_doc("Sales Invoice")
		self.invoice.customer = "Tally Test Customer"
		self.invoice.company = self.company
		self.invoice.posting_date = "2026-06-27"
		
		# Add a dummy item
		self.invoice.append("items", {
			"item_code": item_code,
			"qty": 1,
			"rate": 100.0,
			"income_account": income_account,
			"warehouse": warehouse
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
		settings = frappe.get_doc("SMRITI Tally Settings")
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
