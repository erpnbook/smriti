# -*- coding: utf-8 -*-
"""
smriti_retail_os/tests/test_notification_studio.py
Unit tests for SMRITI Notification Studio triggers and scheduled daily checks.
"""
import frappe
from smriti_retail_os import smriti
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
        if not smriti.db.exists("Customer", "Test Notification Customer"):
            customer_group = smriti.db.get("Customer Group", {"is_group": 0}, "name") or "Individual"
            territory = smriti.db.get("Territory", {"is_group": 0}, "name") or "All Territories"
            doc = smriti.documents.new("Customer")
            doc.update({
                "customer_name": "Test Notification Customer",
                "customer_type": "Individual",
                "customer_group": customer_group,
                "territory": territory
            })
            doc.insert(ignore_permissions=True)
            smriti.db.commit()

        # Create a test supplier if not exists
        if not smriti.db.exists("Supplier", "Test Notification Supplier"):
            supplier_group = smriti.db.get("Supplier Group", {"is_group": 0}, "name") or "All Supplier Groups"
            doc = smriti.documents.new("Supplier")
            doc.update({
                "supplier_name": "Test Notification Supplier",
                "supplier_type": "Individual",
                "supplier_group": supplier_group
            })
            doc.insert(ignore_permissions=True)
            smriti.db.commit()

        # Clear existing logs for tests to avoid noise
        smriti.db.delete("SMRITI Notification Log")
        smriti.db.commit()

    def test_trigger_purchase_approval(self):
        po = smriti.documents.new("PurchaseOrder")
        po.update({
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
        logs = smriti.db.get_list("SMRITI Notification Log", filters={"notif_type": "purchase_approval"}, fields=["message"])
        self.assertTrue(len(logs) > 0)
        self.assertIn("Test Notification Supplier", logs[0].get("message") or "")

    def test_trigger_grn_received(self):
        pr = smriti.documents.new("PurchaseReceipt")
        pr.update({
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
        logs = smriti.db.get_list("SMRITI Notification Log", filters={"notif_type": "grn_received"})
        self.assertTrue(len(logs) > 0)

    def test_trigger_sales_notification(self):
        si = smriti.documents.new("SalesInvoice")
        si.update({
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
        logs = smriti.db.get_list("SMRITI Notification Log", filters={"notif_type": "sales"})
        self.assertTrue(len(logs) > 0)

    def test_scheduled_low_stock_checks(self):
        # Trigger scheduled low stock check
        run_low_stock_checks()
        # Verify it runs without exception

    def test_scheduled_due_invoice_checks(self):
        # Trigger scheduled due invoice check
        run_due_invoice_checks()
        # Verify it runs without exception
