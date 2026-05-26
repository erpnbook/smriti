import frappe
import unittest
from frappe.utils import flt, cint, now_datetime
from smriti_retail_os.billing_api import (
    add_item_by_barcode,
    search_customer,
    hold_bill,
    recall_bill,
    search_items,
    load_held_invoice,
    validate_manager_override,
    submit_bill
)

class TestSmritiRetailBillingAPI(unittest.TestCase):
    
    def setUp(self):
        # 1. Resolve or Create basic link dependencies for the isolated test DB
        self.uom = frappe.db.exists("UOM", "Nos") or frappe.db.get_value("UOM", {}, "name")
        if not self.uom:
            uom_doc = frappe.new_doc("UOM")
            uom_doc.uom_name = "Nos"
            uom_doc.insert(ignore_permissions=True)
            self.uom = uom_doc.name

        self.item_group = frappe.db.exists("Item Group", "All Item Groups") or frappe.db.get_value("Item Group", {}, "name")
        if not self.item_group:
            ig = frappe.new_doc("Item Group")
            ig.item_group_name = "All Item Groups"
            ig.is_group = 0
            ig.insert(ignore_permissions=True)
            self.item_group = ig.name

        self.company = frappe.db.get_value("Company", {}, "name")
        if not self.company:
            comp = frappe.new_doc("Company")
            comp.company_name = "_Test Company"
            comp.country = "India"
            comp.default_currency = "INR"
            comp.insert(ignore_permissions=True)
            self.company = comp.name

        # Create valid GST HSN Code record for India Compliance
        self.hsn_code = frappe.db.exists("GST HSN Code", "998311") or frappe.db.get_value("GST HSN Code", {}, "name")
        if not self.hsn_code:
            hsn = frappe.new_doc("GST HSN Code")
            hsn.hsn_code = "998311"
            hsn.description = "Test Services"
            hsn.insert(ignore_permissions=True)
            self.hsn_code = hsn.name

        # Resolve Warehouse
        self.warehouse = frappe.db.get_value("Warehouse", {"company": self.company}, "name")
        if not self.warehouse:
            w = frappe.new_doc("Warehouse")
            w.warehouse_name = "Test Warehouse"
            w.company = self.company
            w.warehouse_type = "Transit"
            w.insert(ignore_permissions=True)
            self.warehouse = w.name
            
        # Set cashier user default warehouse to the Transit warehouse to bypass negative stock checks in unit tests
        frappe.defaults.set_user_default("warehouse", self.warehouse, frappe.session.user)

        # Resolve Cost Center robustly
        self.cost_center = frappe.db.get_value("Company", self.company, "cost_center")
        if not self.cost_center:
            self.cost_center = frappe.db.get_value("Cost Center", {"company": self.company, "is_group": 0}, "name")
        if not self.cost_center:
            # Check if root group cost center exists or create it
            # The root cost center name MUST equal company name to pass parent_cost_center check!
            parent_cc = frappe.db.get_value("Cost Center", {"cost_center_name": self.company}, "name")
            if not parent_cc:
                pcc = frappe.new_doc("Cost Center")
                pcc.cost_center_name = self.company
                pcc.company = self.company
                pcc.is_group = 1
                pcc.flags.ignore_mandatory = True # Bypass parent_cost_center check on Root CC!
                pcc.insert(ignore_permissions=True)
                parent_cc = pcc.name
                
            cc = frappe.new_doc("Cost Center")
            cc.cost_center_name = "Test Cost Center"
            cc.company = self.company
            cc.is_group = 0
            cc.parent_cost_center = parent_cc
            cc.insert(ignore_permissions=True)
            self.cost_center = cc.name

        # Resolve Income Account robustly
        self.income_account = frappe.db.get_value("Account", {"company": self.company, "root_type": "Income", "is_group": 0}, "name")
        if not self.income_account:
            parent_account = frappe.db.get_value("Account", {"company": self.company, "root_type": "Income", "is_group": 1}, "name")
            if not parent_account:
                p_acc = frappe.new_doc("Account")
                p_acc.account_name = "Root Income Group"
                p_acc.company = self.company
                p_acc.root_type = "Income"
                p_acc.is_group = 1
                p_acc.insert(ignore_permissions=True)
                parent_account = p_acc.name
                
            acc = frappe.new_doc("Account")
            acc.account_name = "Sales"
            acc.company = self.company
            acc.root_type = "Income"
            acc.account_type = "Income Account"
            acc.parent_account = parent_account
            acc.insert(ignore_permissions=True)
            self.income_account = acc.name
            
        # Configure Round Off and Cash details on the test Company to support payments precision rounding
        comp_doc = frappe.get_doc("Company", self.company)
        comp_doc.round_off_cost_center = self.cost_center
        comp_doc.round_off_account = frappe.db.get_value("Account", {"company": self.company, "account_type": "Round Off"}, "name") or self.income_account
        comp_doc.default_cash_account = frappe.db.get_value("Account", {"company": self.company, "account_type": "Cash"}, "name") or frappe.db.get_value("Account", {"company": self.company, "account_name": "Cash"}, "name")
        comp_doc.save(ignore_permissions=True)
        frappe.db.commit()

        # Resolve Mode of Payment
        self.mode_of_payment = frappe.db.get_value("Mode of Payment", {}, "name")
        if not self.mode_of_payment:
            mop = frappe.new_doc("Mode of Payment")
            mop.mode_of_payment = "Cash"
            mop.type = "Cash"
            mop.insert(ignore_permissions=True)
            self.mode_of_payment = mop.name

        # Ensure Mode of Payment has standard account linked for our test Company
        mop_doc = frappe.get_doc("Mode of Payment", self.mode_of_payment)
        has_company_account = False
        for acc_row in mop_doc.accounts:
            if acc_row.company == self.company:
                has_company_account = True
                break
        if not has_company_account:
            cash_account = frappe.db.get_value("Account", {"company": self.company, "account_type": "Cash"}, "name") or frappe.db.get_value("Account", {"company": self.company, "account_name": "Cash"}, "name")
            if cash_account:
                mop_doc.append("accounts", {
                    "company": self.company,
                    "default_account": cash_account
                })
                mop_doc.save(ignore_permissions=True)
                frappe.db.commit()

        # Create test POS Profile for saving Draft POS Invoices
        self.pos_profile_name = "Test POS Profile"
        if not frappe.db.exists("POS Profile", self.pos_profile_name):
            pos_prof = frappe.new_doc("POS Profile")
            pos_prof.name = self.pos_profile_name # Explicitly assign name because of Prompt naming strategy!
            pos_prof.pos_profile_name = self.pos_profile_name
            pos_prof.company = self.company
            pos_prof.warehouse = self.warehouse
            pos_prof.cost_center = self.cost_center
            pos_prof.income_account = self.income_account
            pos_prof.selling_price_list = "Standard Selling"
            pos_prof.currency = "INR"
            pos_prof.append("payments", {
                "mode_of_payment": self.mode_of_payment,
                "default": 1
            })
            pos_prof.append("applicable_for_users", {
                "user": frappe.session.user
            })
            pos_prof.flags.ignore_mandatory = True # Bypass write_off_account/write_off_cost_center checks!
            pos_prof.insert(ignore_permissions=True)

        # Clean up potential old test records including barcodes child table orphans, tax templates and tax account
        frappe.db.delete("Item Price", {"item_code": "TEST-ITEM-BAR"})
        frappe.db.delete("Item Barcode", {"barcode": "8901234567890"})
        frappe.db.delete("Item", {"item_code": "TEST-ITEM-BAR"})
        frappe.db.delete("Customer", {"customer_name": "Test Billing Customer"})
        frappe.db.delete("POS Invoice", {"customer": "Test Billing Customer"})
        frappe.db.delete("Comment", {"reference_doctype": "POS Invoice"})
        
        # Clean up tax templates via delete_doc to ensure child tables are fully purged
        for item in frappe.db.get_all("Item Tax Template", filters={"title": "18% GST"}):
            frappe.delete_doc("Item Tax Template", item.name, ignore_missing=True, force=True)
        for item in frappe.db.get_all("Sales Taxes and Charges Template", filters={"title": "18% GST Template"}):
            frappe.delete_doc("Sales Taxes and Charges Template", item.name, ignore_missing=True, force=True)
            
        frappe.db.delete("Account", {"account_name": "GST 9+9", "company": self.company})
        frappe.db.commit()

        # Resolve or create a single non-group Tax account
        self.tax_account = "GST 9+9 - _C"
        if not frappe.db.exists("Account", self.tax_account):
            acc = frappe.new_doc("Account")
            acc.account_name = "GST 9+9"
            acc.company = self.company
            acc.root_type = "Liability"
            acc.account_type = "Tax"
            acc.parent_account = "Duties and Taxes - _C"
            acc.insert(ignore_permissions=True)

        # Create test Item Tax Template for 18% GST
        self.item_tax_template_name = "18% GST"
        if not frappe.db.exists("Item Tax Template", self.item_tax_template_name):
            itt = frappe.new_doc("Item Tax Template")
            itt.title = self.item_tax_template_name
            itt.company = self.company
            itt.gst_rate = 18.0
            itt.append("taxes", {
                "tax_type": self.tax_account,
                "tax_rate": 18.0
            })
            itt.insert(ignore_permissions=True)

        # Create test Sales Taxes and Charges Template for 18% GST
        self.sales_tax_template_name = "18% GST Template"
        if not frappe.db.exists("Sales Taxes and Charges Template", self.sales_tax_template_name):
            stct = frappe.new_doc("Sales Taxes and Charges Template")
            stct.title = self.sales_tax_template_name
            stct.company = self.company
            stct.is_default = 1
            stct.append("taxes", {
                "charge_type": "On Net Total",
                "account_head": self.tax_account,
                "description": "GST 18%",
                "rate": 18.0
            })
            stct.insert(ignore_permissions=True)
        else:
            frappe.db.set_value("Sales Taxes and Charges Template", self.sales_tax_template_name, "is_default", 1)

        # 2. Setup a test Retail Item
        self.item = frappe.new_doc("Item")
        self.item.item_code = "TEST-ITEM-BAR"
        self.item.item_name = "Test Retail Product"
        self.item.item_group = self.item_group
        self.item.stock_uom = self.uom
        self.item.custom_is_retail_item = 1
        self.item.custom_mrp = 150.0
        self.item.standard_rate = 100.0
        self.item.custom_gst_percentage = "18"
        self.item.gst_hsn_code = self.hsn_code
        self.item.append("barcodes", {
            "barcode": "8901234567890",
            "uom": self.uom
        })
        self.item.insert(ignore_permissions=True)

        # Trigger hook manually to sync prices and taxes
        from smriti_retail_os.hooks_logic import sync_item_taxes_and_prices, after_item_save
        sync_item_taxes_and_prices(self.item, None)
        after_item_save(self.item, None)
        # 3. Setup a test Customer
        self.cust = frappe.new_doc("Customer")
        self.cust.customer_name = "Test Billing Customer"
        self.cust.customer_type = "Individual"
        self.cust.mobile_no = "9988776655"
        self.cust.insert(ignore_permissions=True)

        # 4. Setup a test Manager PIN / Password
        # Assign Password to current user so we can test validation easily
        from frappe.utils.password import update_password
        update_password(frappe.session.user, "4321")
        
        # Ensure current user has SMRITI Store Manager role in DB
        if not frappe.db.exists("Has Role", {"parent": frappe.session.user, "role": "SMRITI Store Manager"}):
            role_doc = frappe.new_doc("Has Role")
            role_doc.parent = frappe.session.user
            role_doc.parenttype = "User"
            role_doc.parentfield = "roles"
            role_doc.role = "SMRITI Store Manager"
            role_doc.insert(ignore_permissions=True)
        
        frappe.db.commit()

    def tearDown(self):
        # Clean up test records
        frappe.db.delete("Item", {"item_code": "TEST-ITEM-BAR"})
        frappe.db.delete("Item Barcode", {"barcode": "8901234567890"})
        frappe.db.delete("Item Price", {"item_code": "TEST-ITEM-BAR"})
        frappe.db.delete("Customer", {"customer_name": "Test Billing Customer"})
        frappe.db.delete("POS Invoice", {"customer": "Test Billing Customer"})
        frappe.db.delete("Comment", {"reference_doctype": "POS Invoice"})
        
        # Clean up test roles
        frappe.db.delete("Has Role", {"parent": frappe.session.user, "role": "SMRITI Store Manager"})
        
        # Clean up test tax templates via delete_doc to ensure child tables are fully purged
        for item in frappe.db.get_all("Item Tax Template", filters={"title": "18% GST"}):
            frappe.delete_doc("Item Tax Template", item.name, ignore_missing=True, force=True)
        for item in frappe.db.get_all("Sales Taxes and Charges Template", filters={"title": "18% GST Template"}):
            frappe.delete_doc("Sales Taxes and Charges Template", item.name, ignore_missing=True, force=True)
            
        frappe.db.delete("Account", {"account_name": "GST 9+9", "company": self.company})
        
        frappe.db.commit()

    def test_add_item_by_barcode(self):
        """
        Verifies barcode scanning fetches standard rates, MRP, and GST correctly.
        """
        # Test by scanned barcode
        res = add_item_by_barcode("8901234567890")
        self.assertIsNotNone(res)
        self.assertEqual(res["item_code"], "TEST-ITEM-BAR")
        self.assertEqual(flt(res["rate"]), 100.0)
        self.assertEqual(flt(res["mrp"]), 150.0)
        self.assertEqual(res["gst_percentage"], 18)

        # Test fallback directly matching item_code
        res_direct = add_item_by_barcode("TEST-ITEM-BAR")
        self.assertIsNotNone(res_direct)
        self.assertEqual(res_direct["item_code"], "TEST-ITEM-BAR")

    def test_search_customer(self):
        """
        Verifies customer lookup by mobile or name.
        """
        # Search by mobile
        res = search_customer("9988776655")
        self.assertTrue(len(res) > 0)
        self.assertEqual(res[0]["customer_name"], "Test Billing Customer")

        # Search by name
        res_name = search_customer("Billing Customer")
        self.assertTrue(len(res_name) > 0)

    def test_hold_and_recall_bill(self):
        """
        Verifies holding and recalling a bill creates and reads draft POS invoices.
        """
        items_payload = [{
            "item_code": "TEST-ITEM-BAR",
            "stock_uom": self.uom,
            "qty": 2,
            "rate": 100.0,
            "mrp": 150.0,
            "gst_percentage": 18,
            "tax_template": ""
        }]

        # Hold current active bill
        res_hold = hold_bill(
            cashier=frappe.session.user,
            customer="Test Billing Customer",
            items=frappe.as_json(items_payload)
        )
        self.assertIsNotNone(res_hold)
        invoice_name = res_hold["invoice_name"]
        self.assertTrue(frappe.db.exists("POS Invoice", invoice_name))

        # Check in DB that custom hold fields are populated
        inv = frappe.get_doc("POS Invoice", invoice_name)
        self.assertEqual(inv.docstatus, 0)
        self.assertEqual(inv.custom_is_held, 1)
        self.assertEqual(inv.custom_held_by, frappe.session.user)

        # Recall held bills
        recalled_list = recall_bill(frappe.session.user)
        self.assertTrue(len(recalled_list) > 0)
        held_names = [r["name"] for r in recalled_list]
        self.assertIn(invoice_name, held_names)

        # Load specific held invoice items
        loaded = load_held_invoice(invoice_name)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded["customer"], "Test Billing Customer")
        self.assertEqual(len(loaded["items"]), 1)
        self.assertEqual(loaded["items"][0]["item_code"], "TEST-ITEM-BAR")
        self.assertEqual(flt(loaded["items"][0]["qty"]), 2.0)

    def test_search_items(self):
        """
        Verifies catalog query search.
        """
        res = search_items("Retail Product")
        self.assertTrue(len(res) > 0)
        self.assertEqual(res[0]["item_code"], "TEST-ITEM-BAR")

    def test_manager_override(self):
        """
        Verifies security override and audit comments logging.
        """
        items_payload = [{
            "item_code": "TEST-ITEM-BAR",
            "qty": 1,
            "rate": 100.0,
            "mrp": 150.0
        }]
        res_hold = hold_bill(
            cashier=frappe.session.user,
            customer="Test Billing Customer",
            items=frappe.as_json(items_payload)
        )
        invoice_name = res_hold["invoice_name"]

        # 1. Invalid PIN check
        res_invalid = validate_manager_override("9999", "Void Row Override", invoice_name)
        self.assertFalse(res_invalid["authorized"])

        # 2. Valid PIN check
        res_valid = validate_manager_override("4321", "Void Row Override", invoice_name)
        self.assertTrue(res_valid["authorized"])
        self.assertEqual(res_valid["manager"], frappe.session.user)

        # 3. Check comment audit log creation
        comments = frappe.db.get_all(
            "Comment",
            filters={
                "reference_doctype": "POS Invoice",
                "reference_name": invoice_name
            },
            fields=["content"]
        )
        self.assertTrue(len(comments) > 0)
        self.assertIn("Manager Override approved", comments[0]["content"])

    def test_submit_bill_sales_invoice_fallback(self):
        """
        Verifies that when no cashier shift is open, submit_bill successfully
        submits a standard Sales Invoice directly, bypassing shift checks.
        """
        # Ensure no open shift exists for the cashier
        frappe.db.delete("POS Opening Entry", {"user": frappe.session.user})
        frappe.db.commit()

        items_payload = [{
            "item_code": "TEST-ITEM-BAR",
            "stock_uom": self.uom,
            "qty": 3,
            "rate": 100.0,
            "mrp": 150.0,
            "gst_percentage": 18,
            "tax_template": ""
        }]

        payments_payload = [
            {"mode_of_payment": self.mode_of_payment, "amount": 354.0} # Qty 3 * Rate 100 * 1.18 Tax = 354.0
        ]

        # Submit bill
        res = submit_bill(
            cashier=frappe.session.user,
            customer="Test Billing Customer",
            items=frappe.as_json(items_payload),
            payments=frappe.as_json(payments_payload)
        )

        self.assertIsNotNone(res)
        invoice_name = res["invoice"]
        self.assertTrue(frappe.db.exists("Sales Invoice", invoice_name))
        
        # Verify it is a standard Sales Invoice and submitted (docstatus=1)
        invoice = frappe.get_doc("Sales Invoice", invoice_name)
        self.assertEqual(invoice.docstatus, 1)
        self.assertEqual(invoice.is_pos, 0)
        self.assertEqual(flt(invoice.grand_total), 354.0)

        # Clean up created Sales Invoice
        frappe.db.delete("Sales Invoice", {"name": invoice_name})
        frappe.db.commit()
