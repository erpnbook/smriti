# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_psv_ledger.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, Smriti Retail OS and contributors
# For license information, please see license.txt

import frappe
from smriti_retail_os.tests.test_psv import TestPSV
from smriti_retail_os.balance_engine import get_party_balance
from smriti_retail_os.psv_ledger_service import create_transaction, reverse_transaction

class TestPSVLedger(TestPSV):
    def make_stock_receipt(self, item_code, qty):
        se = frappe.new_doc("Stock Entry")
        se.purpose = "Material Receipt"
        se.stock_entry_type = "Material Receipt"
        se.company = self.company
        se.append("items", {
            "item_code": item_code,
            "qty": qty,
            "t_warehouse": self.warehouse,
            "rate": 100.0,
            "basic_rate": 100.0,
            "valuation_rate": 100.0,
            "allow_zero_valuation_rate": 1,
            "set_basic_rate_manually": 1,
            "cost_center": self.cost_center
        })
        se.insert(ignore_permissions=True)
        se.submit()

    def test_immutability(self):
        # Create a transaction
        from smriti_retail_os.psv_service import create_psv_transaction
        tx_name = create_psv_transaction(
            psa=self.account_name,
            transaction_type="TRANSFER_OUT",
            items=[{"item_code": self.item, "qty": 10.0}],
            company=self.company
        )
        
        # Assert that trying to edit a SMRITI PSV Transaction document raises ValidationError
        tx = frappe.get_doc("SMRITI PSV Transaction", tx_name)
        tx.remarks = "Edited"
        self.assertRaises(frappe.ValidationError, tx.save)

        # Assert that attempting to delete a SMRITI Party Stock Ledger Entry directly raises ValidationError
        entries = frappe.get_all("SMRITI Party Stock Ledger Entry", filters={"voucher_no": tx_name}, fields=["name"])
        self.assertTrue(entries)
        entry_doc = frappe.get_doc("SMRITI Party Stock Ledger Entry", entries[0].name)
        self.assertRaises(frappe.ValidationError, entry_doc.delete)

    def test_delivery_note_dispatch(self):
        # Provision warehouse stock to prevent NegativeStockError
        self.make_stock_receipt(self.item, 100.0)

        # 1. Create a Delivery Note referencing custom_party_stock_account
        dn = frappe.new_doc("Delivery Note")
        dn.company = self.company
        dn.customer = self.customer
        dn.custom_party_stock_account = self.account_name
        dn.append("items", {
            "item_code": self.item,
            "qty": 50.0,
            "rate": 1000.0,
            "uom": self.uom,
            "warehouse": self.warehouse
        })
        dn.insert(ignore_permissions=True)
        dn.submit()

        # 2. Assert that SMRITI PSV Transaction was created with type TRANSFER_OUT
        tx_name = frappe.db.get_value("SMRITI PSV Transaction", {
            "reference_doctype": "Delivery Note",
            "reference_name": dn.name,
            "docstatus": 1
        })
        self.assertTrue(tx_name)
        tx = frappe.get_doc("SMRITI PSV Transaction", tx_name)
        self.assertEqual(tx.transaction_type, "TRANSFER_OUT")

        # 3. Assert that SMRITI Party Stock Ledger Entry was created with positive qty 50.0
        ledger_entries = frappe.get_all("SMRITI Party Stock Ledger Entry", filters={
            "voucher_no": tx_name,
            "item_code": self.item
        }, fields=["qty"])
        self.assertEqual(len(ledger_entries), 1)
        self.assertEqual(ledger_entries[0].qty, 50.0)

        # 4. Check balance reflects 50.0
        bal = get_party_balance(self.account_name, self.item)
        self.assertEqual(bal, 50.0)

    def test_delivery_note_cancellation_reversal(self):
        # Provision warehouse stock to prevent NegativeStockError
        self.make_stock_receipt(self.item, 100.0)

        # 1. Create and submit Delivery Note
        dn = frappe.new_doc("Delivery Note")
        dn.company = self.company
        dn.customer = self.customer
        dn.custom_party_stock_account = self.account_name
        dn.append("items", {
            "item_code": self.item,
            "qty": 30.0,
            "rate": 1000.0,
            "uom": self.uom,
            "warehouse": self.warehouse
        })
        dn.insert(ignore_permissions=True)
        dn.submit()

        # Check balance
        bal_before = get_party_balance(self.account_name, self.item)
        self.assertEqual(bal_before, 30.0)

        # 2. Cancel Delivery Note
        dn.cancel()

        # 3. Assert SMRITI PSV Transaction is cancelled (docstatus = 2)
        tx_name = frappe.db.get_value("SMRITI PSV Transaction", {
            "reference_doctype": "Delivery Note",
            "reference_name": dn.name
        })
        tx = frappe.get_doc("SMRITI PSV Transaction", tx_name)
        self.assertEqual(tx.docstatus, 2)

        # 4. Assert reversal entry is written to SMRITI Party Stock Ledger Entry (qty = -30.0)
        reversal_entries = frappe.get_all("SMRITI Party Stock Ledger Entry", filters={
            "voucher_no": f"VOID-{tx_name}",
            "item_code": self.item
        }, fields=["qty"])
        self.assertEqual(len(reversal_entries), 1)
        self.assertEqual(reversal_entries[0].qty, -30.0)

        # 5. Check balance is back to 0.0
        bal_after = get_party_balance(self.account_name, self.item)
        self.assertEqual(bal_after, 0.0)

    def test_duplicate_dispatch_prevention(self):
        # Provision warehouse stock to prevent NegativeStockError
        self.make_stock_receipt(self.item, 100.0)

        # 1. Create and submit Delivery Note
        dn = frappe.new_doc("Delivery Note")
        dn.company = self.company
        dn.customer = self.customer
        dn.custom_party_stock_account = self.account_name
        dn.append("items", {
            "item_code": self.item,
            "qty": 20.0,
            "rate": 1000.0,
            "uom": self.uom,
            "warehouse": self.warehouse
        })
        dn.insert(ignore_permissions=True)
        dn.submit()

        tx_name_1 = frappe.db.get_value("SMRITI PSV Transaction", {
            "reference_doctype": "Delivery Note",
            "reference_name": dn.name,
            "docstatus": 1
        })
        self.assertTrue(tx_name_1)

        # Count ledger entries before replay
        entries_before = frappe.db.count("SMRITI Party Stock Ledger Entry", {
            "voucher_no": tx_name_1,
            "item_code": self.item
        })
        self.assertEqual(entries_before, 1)

        # 2. Replay submit (explicitly call hook handle_delivery_note_submit again)
        from smriti_retail_os.psv_integration import handle_delivery_note_submit
        handle_delivery_note_submit(dn)

        # 3. Assert no duplicate ledger entry is created
        entries_after = frappe.db.count("SMRITI Party Stock Ledger Entry", {
            "voucher_no": tx_name_1,
            "item_code": self.item
        })
        self.assertEqual(entries_after, 1, "Duplicate dispatch ledger entry created on replay!")
