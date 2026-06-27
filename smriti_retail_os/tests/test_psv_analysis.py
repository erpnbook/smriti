# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_psv_analysis.py
# @description: Unit tests for PSV analytics — coverage, aging, and health score.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, Smriti Retail OS and contributors
# For license information, please see license.txt

import frappe
from smriti_retail_os.tests.test_psv import TestPSV
from smriti_retail_os.balance_engine import get_party_balance
from smriti_retail_os.psv_analysis_service import get_broken_sizes, generate_reorder_suggestions

class TestPSVAnalysis(TestPSV):
    def test_broken_size_detection_logic(self):
        # Ensure Item Attribute "Test Attribute Analysis" exists with correct values
        if frappe.db.exists("Item Attribute", "Test Attribute Analysis"):
            frappe.delete_doc("Item Attribute", "Test Attribute Analysis", force=True)

        attr = frappe.new_doc("Item Attribute")
        attr.attribute_name = "Test Attribute Analysis"
        attr.append("item_attribute_values", {"attribute_value": "7", "abbr": "7"})
        attr.append("item_attribute_values", {"attribute_value": "8", "abbr": "8"})
        attr.insert(ignore_permissions=True)

        # 1. Create a template item
        template_item = "TEST-STYLE-TEMPLATE"
        if not frappe.db.exists("Item", template_item):
            itm = frappe.new_doc("Item")
            itm.item_code = template_item
            itm.item_name = "Test Style Template"
            itm.item_group = self.item_group
            itm.stock_uom = self.uom
            itm.gst_hsn_code = self.hsn_code
            itm.has_variants = 1
            itm.append("attributes", {"attribute": "Test Attribute Analysis"})
            itm.insert(ignore_permissions=True)

        # 2. Create variant items
        var_7 = "TEST-STYLE-7"
        if not frappe.db.exists("Item", var_7):
            itm = frappe.new_doc("Item")
            itm.item_code = var_7
            itm.item_name = "Test Style 7"
            itm.item_group = self.item_group
            itm.stock_uom = self.uom
            itm.gst_hsn_code = self.hsn_code
            itm.variant_of = template_item
            itm.append("attributes", {"attribute": "Test Attribute Analysis", "attribute_value": "7"})
            itm.insert(ignore_permissions=True)

        var_8 = "TEST-STYLE-8"
        if not frappe.db.exists("Item", var_8):
            itm = frappe.new_doc("Item")
            itm.item_code = var_8
            itm.item_name = "Test Style 8"
            itm.item_group = self.item_group
            itm.stock_uom = self.uom
            itm.gst_hsn_code = self.hsn_code
            itm.variant_of = template_item
            itm.append("attributes", {"attribute": "Test Attribute Analysis", "attribute_value": "8"})
            itm.insert(ignore_permissions=True)

        # 3. Create a Reorder Rule for var_7
        rule = frappe.new_doc("SMRITI PSV Reorder Rule")
        rule.company = self.company
        rule.party_stock_account = self.account_name
        rule.item_variant = var_7
        rule.min_stock = 10
        rule.active = 1
        rule.insert(ignore_permissions=True)

        # 4. Set balance of var_7 to 5.0 (var_8 has 0.0 balance)
        from smriti_retail_os.psv_service import import_opening_balances
        import_opening_balances(self.company, self.account_name, [{"item_code": var_7, "qty": 5.0}])

        # 5. Call get_broken_sizes and assert style is stranded
        broken = get_broken_sizes(self.customer)
        self.assertEqual(len(broken), 1)
        self.assertEqual(broken[0]["style"], template_item)
        self.assertEqual(broken[0]["stranded_qty"], 5.0)
        self.assertIn(var_8, broken[0]["missing_core"])

    def test_reconciliation_variance_posting(self):
        # 1. Set Balance to 10.0
        from smriti_retail_os.psv_service import import_opening_balances
        import_opening_balances(self.company, self.account_name, [{"item_code": self.item, "qty": 10.0}])

        bal_before = get_party_balance(self.account_name, self.item)
        self.assertEqual(bal_before, 10.0)

        # 2. Create physical stock snapshot with physical count 8.0 (variance is -2.0)
        snap = frappe.new_doc("SMRITI Party Physical Snapshot")
        snap.company = self.company
        snap.party_stock_account = self.account_name
        snap.audit_date = frappe.utils.today()
        snap.append("items", {
            "item_code": self.item,
            "physical_qty": 8.0,
            "variance_reason": "Theft"
        })
        snap.insert(ignore_permissions=True)

        # Approve and submit
        snap.status = "Approved"
        snap.save()
        snap.submit()

        # 3. Assert Balance is updated to 8.0
        bal_after = get_party_balance(self.account_name, self.item)
        self.assertEqual(bal_after, 8.0)

        # 4. Assert that the SMRITI PSV Transaction has transaction_type = AUDIT_ADJUSTMENT
        tx_name = frappe.db.get_value("SMRITI PSV Transaction", {
            "reference_doctype": "SMRITI Party Physical Snapshot",
            "reference_name": snap.name,
            "docstatus": 1
        })
        self.assertTrue(tx_name)
        tx = frappe.get_doc("SMRITI PSV Transaction", tx_name)
        self.assertEqual(tx.transaction_type, "AUDIT_ADJUSTMENT")
