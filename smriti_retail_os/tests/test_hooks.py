import frappe
import unittest
from frappe.utils import flt, cint

class TestSmritiRetailHooks(unittest.TestCase):
    
    def setUp(self):
        # Clean up any test records
        frappe.db.delete("Item", {"item_code": "TEST-SHIRT"})
        frappe.db.delete("Customer", {"customer_name": "Test Rajesh Kumar"})
        frappe.db.delete("Supplier", {"supplier_name": "Test ABC Wholesalers"})
        frappe.db.delete("Address", {"address_title": ["like", "Test%"]})
        frappe.db.commit()

        # Ensure a default Supplier Group exists and fetch it
        self.supplier_group = frappe.db.get_value("Supplier Group", {}, "name")
        if not self.supplier_group:
            sg = frappe.new_doc("Supplier Group")
            sg.supplier_group_name = "Test Local"
            sg.insert(ignore_permissions=True)
            self.supplier_group = sg.name

    def tearDown(self):
        # Clean up test records
        frappe.db.delete("Item", {"item_code": "TEST-SHIRT"})
        frappe.db.delete("Customer", {"customer_name": "Test Rajesh Kumar"})
        frappe.db.delete("Supplier", {"supplier_name": "Test ABC Wholesalers"})
        frappe.db.delete("Address", {"address_title": ["like", "Test%"]})
        frappe.db.commit()

    def test_customer_address_sync(self):
        """
        Tests that saving a Customer with custom_address_text auto-generates
        a standard linked Address record.
        """
        cust = frappe.new_doc("Customer")
        cust.customer_name = "Test Rajesh Kumar"
        cust.customer_type = "Individual"
        cust.primary_mobile_no = "9876543210"
        cust.tax_id = "29AABCR1718E1ZL" # Mathematically valid Karnataka GSTIN from India Compliance
        cust.custom_address_text = "Flat 402, Green Glen Layout\nBangalore\n560103"
        cust.insert(ignore_permissions=True)
        
        # Verify that Address record was created in the database and linked
        addr_name = frappe.db.get_value(
            "Address", 
            {
                "links.link_doctype": "Customer",
                "links.link_name": cust.name,
                "address_type": "Billing"
            }, 
            "name"
        )
        self.assertIsNotNone(addr_name)
        
        addr = frappe.get_doc("Address", addr_name)
        self.assertEqual(addr.address_line1, "Flat 402, Green Glen Layout")
        self.assertEqual(addr.address_line2, "Bangalore, 560103")
        self.assertEqual(addr.country, "India")
        self.assertEqual(addr.state, "Karnataka") # Resolved from GSTIN!

    def test_supplier_address_and_credit_days(self):
        """
        Tests that saving a Supplier auto-generates linked Address
        and creates/links a Payment Terms Template matching custom_credit_days.
        """
        supp = frappe.new_doc("Supplier")
        supp.supplier_name = "Test ABC Wholesalers"
        supp.supplier_group = self.supplier_group
        supp.gstin = "29AABCR1718E1ZL"
        supp.custom_address_text = "Shed 4B, Peenya Industrial Area\nBangalore"
        supp.custom_credit_days = 45
        supp.insert(ignore_permissions=True)
        
        # 1. Verify address sync
        addr_name = frappe.db.get_value(
            "Address", 
            {
                "links.link_doctype": "Supplier",
                "links.link_name": supp.name,
                "address_type": "Billing"
            }, 
            "name"
        )
        self.assertIsNotNone(addr_name)
        addr = frappe.get_doc("Address", addr_name)
        self.assertEqual(addr.address_line1, "Shed 4B, Peenya Industrial Area")
        self.assertEqual(addr.state, "Karnataka") # Resolved from GSTIN!
        
        # 2. Verify Payment Term generation & linking
        supp_reload = frappe.get_doc("Supplier", supp.name)
        self.assertEqual(supp_reload.payment_terms, "Credit Term - 45 Days")
        
        # Verify Payment Term template exists
        ptt_exists = frappe.db.exists("Payment Terms Template", "Credit Term - 45 Days")
        self.assertTrue(ptt_exists)
        
        # Inspect terms
        ptt = frappe.get_doc("Payment Terms Template", "Credit Term - 45 Days")
        self.assertEqual(len(ptt.terms), 1)
        self.assertEqual(ptt.terms[0].credit_days, 45)
