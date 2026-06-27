# -*- coding: utf-8 -*-
import frappe
import unittest
from smriti_retail_os.tests.test_billing_api import TestSmritiRetailBillingAPI
from smriti_retail_os.services.billing_summary_engine import calculate_billing_summary
from smriti_retail_os.billing_api import submit_bill

class TestBillingDiscountsSalesperson(TestSmritiRetailBillingAPI):
    def setUp(self):
        # Clear company doc cache and request-local document cache to avoid TimestampMismatchError
        frappe.clear_cache(doctype="Company")
        if hasattr(frappe.local, "document_cache"):
            frappe.local.document_cache.clear()
        super().setUp()
        
        # Configure Selling Settings to allow multiple rows of the same item
        selling_settings = frappe.get_doc("Selling Settings")
        selling_settings.allow_multiple_items = 1
        selling_settings.save(ignore_permissions=True)
        frappe.db.commit()
        # Seed test Salespersons
        for sp_name in ["Rahul Sharma", "Anita Deshmukh", "Sameer Verma"]:
            if not frappe.db.exists("Sales Person", sp_name):
                sp = frappe.new_doc("Sales Person")
                sp.sales_person_name = sp_name
                sp.commission_rate = 5.0
                sp.insert(ignore_permissions=True)
        
        # Configure test discount settings on SMRITI Company Settings
        settings_name = frappe.db.exists("SMRITI Company Settings", self.company)
        if not settings_name:
            settings = frappe.new_doc("SMRITI Company Settings")
            settings.company = self.company
            settings.discount_mode = "Both"
            settings.mandatory_discount_reason = 1
            settings.discount_approval_limit = 10.0
            settings.max_offline_cashier_discount = 5.0
            settings.insert(ignore_permissions=True)
        else:
            settings = frappe.get_doc("SMRITI Company Settings", settings_name)
            settings.discount_mode = "Both"
            settings.mandatory_discount_reason = 1
            settings.discount_approval_limit = 10.0
            settings.max_offline_cashier_discount = 5.0
            settings.save(ignore_permissions=True)
        frappe.db.commit()

    def test_calculation_order_and_dual_discounts(self):
        """
        Verify the calculation hierarchy:
        Item Price -> Item Discount -> Subtotal -> Bill Discount -> GST -> Grand Total
        """
        items = [
            {
                "item_code": "TEST-ITEM-BAR",
                "qty": 2,
                "rate": 100.0, # base price
                "discount_type": "%",
                "discount_value": 10.0, # 10% item discount
                "gst_percentage": 18.0
            }
        ]
        
        # Calculate summary with bill-level discount of Rs 20
        summary = calculate_billing_summary(
            items=items,
            bill_discount_percentage=0.0,
            bill_discount_amount=20.0,
            tax_inclusive=True
        )
        
        # Step-by-step verification:
        # Item base subtotal: 2 * 100 = 200
        # Item discount: 200 * 10% = 20
        # Item net subtotal: 200 - 20 = 180
        # Bill discount: Rs 20
        # Final net total: 180 - 20 = 160
        # Tax base is 160. GST is tax-inclusive.
        # GST = 160 * (18 / 118) = 24.41
        # Grand total (rounded) = 160
        
        self.assertEqual(summary["subtotal"], 200.0)
        self.assertEqual(summary["total_item_discount"], 20.0)
        self.assertEqual(summary["bill_discount"], 20.0)
        self.assertEqual(summary["net_total"], 180.0)
        self.assertEqual(summary["final_net_total"], 160.0)
        self.assertAlmostEqual(summary["total_tax"], 160.0 * 18.0 / 118.0, places=2)
        self.assertEqual(summary["rounded_grand_total"], 160.0)

    def test_salesperson_inheritance_and_override(self):
        """
        Verify default bill salesperson inheritance and row-level overrides.
        """
        items_payload = [
            {
                "item_code": "TEST-ITEM-BAR",
                "qty": 1,
                "rate": 100.0,
                "discount_type": "%",
                "discount_value": 0.0,
                "gst_percentage": 18.0,
                "custom_sales_person": "Anita Deshmukh" # Override row-level salesperson
            },
            {
                "item_code": "TEST-ITEM-BAR",
                "qty": 1,
                "rate": 100.0,
                "discount_type": "%",
                "discount_value": 0.0,
                "gst_percentage": 18.0,
                "custom_sales_person": "" # Inherit bill-level salesperson (Rahul Sharma)
            }
        ]
        
        payments = [{"mode_of_payment": "Cash", "amount": 200.0}]
        
        # Submit bill
        invoice_res = submit_bill(
            cashier=frappe.session.user,
            customer="Walk-In Customer",
            items=items_payload,
            payments=payments,
            sales_staff="Rahul Sharma", # Default salesperson for the bill
            billing_session_id="test_sess_sp_override"
        )
        
        self.assertIsNotNone(invoice_res.get("invoice"))
        dt = "Sales Invoice" if frappe.db.exists("Sales Invoice", invoice_res["invoice"]) else "POS Invoice"
        doc = frappe.get_doc(dt, invoice_res["invoice"])
        
        # Check sales team allocations:
        # Row 1 salesperson should be Anita Deshmukh
        self.assertEqual(doc.items[0].custom_sales_person, "Anita Deshmukh")
        # Row 2 salesperson should be Rahul Sharma (inherited)
        self.assertEqual(doc.items[1].custom_sales_person, "Rahul Sharma")
        
        # Validate general Sales Team table on the invoice has both salesperson mappings
        salesperson_list = [d.sales_person for d in doc.sales_team]
        self.assertIn("Anita Deshmukh", salesperson_list)
        self.assertIn("Rahul Sharma", salesperson_list)

    def test_manager_pin_approval_required(self):
        """
        Verify that cashier cannot submit discount exceeding approval limit without Manager PIN.
        """
        items_payload = [
            {
                "item_code": "TEST-ITEM-BAR",
                "qty": 1,
                "rate": 100.0,
                "discount_type": "%",
                "discount_value": 15.0, # 15% discount (exceeds cashier limit of 10%)
                "discount_reason": "Festival",
                "gst_percentage": 18.0
            }
        ]
        
        payments = [{"mode_of_payment": "Cash", "amount": 85.0}]
        
        # Call submit without manager PIN -> must fail with PermissionError
        with self.assertRaises(frappe.PermissionError):
            submit_bill(
                cashier=frappe.session.user,
                customer="Walk-In Customer",
                items=items_payload,
                payments=payments,
                billing_session_id="test_sess_limit_fail"
            )
            
        # Create a User with Pin
        mgr_email = "testmanager@smriti.com"
        if not frappe.db.exists("User", mgr_email):
            user = frappe.new_doc("User")
            user.email = mgr_email
            user.first_name = "Test Manager"
            user.insert(ignore_permissions=True)
            
        # Assign SMRITI Store Manager role
        if not frappe.db.exists("Has Role", {"parent": mgr_email, "role": "SMRITI Store Manager"}):
            user_doc = frappe.get_doc("User", mgr_email)
            user_doc.append("roles", {"role": "SMRITI Store Manager"})
            user_doc.save(ignore_permissions=True)
            
        # Update custom_smriti_pin securely
        from frappe.utils.password import update_password
        update_password(mgr_email, "9876", doctype="User", fieldname="custom_smriti_pin")
        frappe.db.set_value("User", mgr_email, "custom_smriti_pin", "1")
            
        # Submit with manager pin -> must pass
        invoice_res = submit_bill(
            cashier=frappe.session.user,
            customer="Walk-In Customer",
            items=items_payload,
            payments=payments,
            billing_session_id="test_sess_limit_success",
            manager_pin="9876"
        )
        self.assertIsNotNone(invoice_res.get("invoice"))
