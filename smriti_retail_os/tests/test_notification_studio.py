# -*- coding: utf-8 -*-
"""
smriti_retail_os/tests/test_notification_studio.py
Unit tests for SMRITI Notification Studio triggers and scheduled daily checks.
"""
import frappe
import unittest
from frappe.utils import today, add_days
from smriti_retail_os.notification_studio.service.notification_triggers import (
    trigger_purchase_approval, trigger_grn_received, trigger_sales_notification
)
from smriti_retail_os.notification_studio.service.scheduled_checks import (
    run_low_stock_checks, run_due_invoice_checks
)

class TestNotificationStudio(unittest.TestCase):
    def setUp(self):
        # Create a test customer if not exists
        if not frappe.db.exists("Customer", "Test Notification Customer"):
            doc = frappe.get_doc({
                "doctype": "Customer",
                "customer_name": "Test Notification Customer",
                "customer_type": "Individual",
                "customer_group": "All Customer Groups",
                "territory": "All Territories"
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()

        # Create a test supplier if not exists
        if not frappe.db.exists("Supplier", "Test Notification Supplier"):
            doc = frappe.get_doc({
                "doctype": "Supplier",
                "supplier_name": "Test Notification Supplier",
                "supplier_type": "Individual",
                "supplier_group": "All Supplier Groups"
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()

        # Clear existing logs for tests to avoid noise
        frappe.db.delete("SMRITI Notification Log")
        frappe.db.commit()

    def test_trigger_purchase_approval(self):
        po = frappe.get_doc({
            "doctype": "Purchase Order",
            "supplier": "Test Notification Supplier",
            "transaction_date": today(),
            "items": [{
                "item_code": "TEST-SFM-ITEM-01",
                "qty": 5,
                "rate": 100,
                "uom": "Nos",
                "schedule_date": today()
            }]
        })
        # Simulate on_submit
        trigger_purchase_approval(po, "on_submit")
        
        # Verify notification was generated for purchase_approval
        logs = frappe.get_all("SMRITI Notification Log", filters={"notif_type": "purchase_approval"})
        self.assertTrue(len(logs) > 0)
        self.assertIn("Test Notification Supplier", logs[0].message or "")

    def test_trigger_grn_received(self):
        pr = frappe.get_doc({
            "doctype": "Purchase Receipt",
            "supplier": "Test Notification Supplier",
            "items": [{
                "item_code": "TEST-SFM-ITEM-01",
                "qty": 10,
                "rate": 100,
                "uom": "Nos"
            }]
        })
        # Simulate on_submit
        trigger_grn_received(pr, "on_submit")
        
        # Verify notification was generated for grn_received
        logs = frappe.get_all("SMRITI Notification Log", filters={"notif_type": "grn_received"})
        self.assertTrue(len(logs) > 0)

    def test_trigger_sales_notification(self):
        si = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": "Test Notification Customer",
            "due_date": today(),
            "grand_total": 500.0,
            "is_pos": 0,
            "items": [{
                "item_code": "TEST-SFM-ITEM-01",
                "qty": 2,
                "rate": 250,
                "uom": "Nos"
            }]
        })
        # Simulate on_submit
        trigger_sales_notification(si, "on_submit")
        
        # Verify notification was generated for sales
        logs = frappe.get_all("SMRITI Notification Log", filters={"notif_type": "sales"})
        self.assertTrue(len(logs) > 0)

    def test_scheduled_low_stock_checks(self):
        # Trigger scheduled low stock check
        run_low_stock_checks()
        # Verify it runs without exception

    def test_scheduled_due_invoice_checks(self):
        # Trigger scheduled due invoice check
        run_due_invoice_checks()
        # Verify it runs without exception
