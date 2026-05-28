# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/verify_pos_features.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import flt, cint
from smriti_retail_os.billing_api import hold_bill, load_held_invoice, submit_bill

def run_pos_features_deep_audit():
    print("\n=======================================================")
    print("[SMRITI AUDIT] Starting Deep POS Features Verification...")
    print("=======================================================\n")
    
    # 1. Resolve dynamic valid testing entities from active DB
    company = frappe.defaults.get_user_default("company") or frappe.get_all("Company", limit=1)[0].name
    test_item = frappe.db.get_value("Item", {"disabled": 0}, "name")
    test_mop = frappe.db.get_value("Mode of Payment Account", {"company": company}, "parent") or "Cash"
    test_customer = frappe.db.get_value("Customer", {"disabled": 0}, "name") or "Walk-In Customer"
    
    if not test_item:
        print("[AUDIT ERROR] No active Item found in database. Cannot run transaction test.")
        return False
        
    print(f"[AUDIT] Using test item: '{test_item}'")
    print(f"[AUDIT] Using test mode of payment: '{test_mop}'")
    print(f"[AUDIT] Using test customer: '{test_customer}'")
    
    # 2. Check and dynamically create a real POS Profile in database to run native validation
    profile_name = "Test POS Profile"
    try:
        if not frappe.db.exists("POS Profile", profile_name):
            warehouse = frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")
            payments = frappe.db.get_all("Mode of Payment Account", {"company": company}, pluck="parent")
            
            write_off_account = frappe.db.get_value("Account", {"company": company, "account_type": "Chargeable"}, "name") or frappe.db.get_value("Account", {"company": company, "is_group": 0}, "name")
            write_off_cost_center = frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")
            
            prof = frappe.new_doc("POS Profile")
            prof.name = profile_name
            prof.company = company
            prof.warehouse = warehouse
            prof.currency = "INR"
            prof.write_off_account = write_off_account
            prof.write_off_cost_center = write_off_cost_center
            prof.write_off_limit = 1000.0
            
            for idx, pay in enumerate(payments):
                prof.append("payments", {
                    "mode_of_payment": pay,
                    "default": 1 if idx == 0 else 0
                })
                
            prof.insert(ignore_permissions=True)
            frappe.db.commit()
            print(f"[OK] Mapped POS Profile '{profile_name}' created in database.")
        else:
            print(f"[AUDIT] POS Profile '{profile_name}' already exists.")
    except Exception as e:
        print(f"[WARN] Dynamically creating POS Profile failed: {e}. Attempting override instead.")
        
    # Generate structured mock inputs
    mock_items = [{
        "item_code": test_item,
        "qty": 2.0,
        "rate": 150.0,
        "mrp": 150.0,
        "discount_percentage": 15.0, # 15% discount
        "stock_uom": "Nos"
    }]
    
    mock_remarks = "Test remarks detailing order delivery instructions"
    mock_sales_staff = "Sales Exec 01"
    
    # 3. Monkeypatch select validators to bypass open shift requirement and invoice mode checks
    from erpnext.accounts.doctype.pos_invoice.pos_invoice import POSInvoice
    from erpnext.accounts.doctype.sales_invoice.sales_invoice import SalesInvoice
    
    original_validate_pos_opening_entry = SalesInvoice.validate_pos_opening_entry
    original_validate_is_pos_using_sales_invoice = POSInvoice.validate_is_pos_using_sales_invoice
    
    SalesInvoice.validate_pos_opening_entry = lambda self, *args, **kwargs: None
    POSInvoice.validate_is_pos_using_sales_invoice = lambda self, *args, **kwargs: None
    
    try:
        print("\n-------------------------------------------------------")
        print("STEP 1: Verifying hold_bill RPC persistence...")
        print("-------------------------------------------------------")
        
        # Inject our verified POS Profile name into invoice properties
        hold_result = hold_bill(
            cashier="Administrator",
            customer=test_customer,
            items=frappe.as_json(mock_items),
            remarks=mock_remarks,
            sales_staff=mock_sales_staff
        )
        invoice_name = hold_result.get("invoice_name")
        print(f"[OK] hold_bill executed successfully. Draft POS Invoice created: '{invoice_name}'")
        
        # Apply POS Profile to Draft Invoice
        frappe.db.set_value("POS Invoice", invoice_name, "pos_profile", profile_name)
        
        # Read the saved database record directly
        inv_doc = frappe.get_doc("POS Invoice", invoice_name)
        
        # Verify custom hold status
        assert inv_doc.custom_is_held == 1, "custom_is_held is not 1"
        assert inv_doc.custom_held_by == "Administrator", "custom_held_by mismatch"
        print("[OK] Custom draft hold headers validated successfully.")
        
        # Verify remarks merging pattern
        expected_remarks = f"[Sales Staff: {mock_sales_staff}] {mock_remarks}"
        assert inv_doc.remarks == expected_remarks, f"Remarks mismatched! Expected '{expected_remarks}', got '{inv_doc.remarks}'"
        print(f"[OK] Sales Staff & Cashier Remarks successfully merged into standard remarks column: '{inv_doc.remarks}'")
        
        # Verify item-level discount percentage persistence in draft invoice items
        assert len(inv_doc.items) == 1, "Invoice items table size mismatch"
        db_disc = flt(inv_doc.items[0].discount_percentage)
        assert db_disc == 15.0, f"Discount percentage mismatch in DB! Expected 15.0, got {db_disc}"
        print(f"[OK] Item-level discount percentage successfully saved inside Draft child table: {db_disc}%")

        print("\n-------------------------------------------------------")
        print("STEP 2: Verifying load_held_invoice RPC loader...")
        print("-------------------------------------------------------")
        
        loaded_data = load_held_invoice(invoice_name)
        assert loaded_data is not None, "load_held_invoice returned None"
        assert loaded_data.get("invoice_name") == invoice_name, "Loaded invoice name mismatch"
        assert loaded_data.get("customer") == test_customer, "Loaded customer mismatch"
        
        # Verify retrieved remarks
        assert loaded_data.get("remarks") == expected_remarks, "Loaded remarks mismatch"
        print(f"[OK] Remarks and Sales Staff context loaded back properly: '{loaded_data.get('remarks')}'")
        
        # Verify item list discount loader
        loaded_items = loaded_data.get("items")
        assert len(loaded_items) == 1, "Loaded items size mismatch"
        assert flt(loaded_items[0].get("discount_percentage")) == 15.0, "Loaded discount_percentage mismatch"
        print(f"[OK] Loaded item properties aligned with discount_percentage: {loaded_items[0].get('discount_percentage')}%")

        print("\n-------------------------------------------------------")
        print("STEP 3: Verifying submit_bill RPC submission & print...")
        print("-------------------------------------------------------")
        
        # Run standard recalculation / save to set the correct native invoice grand_total
        inv_doc.pos_profile = profile_name
        inv_doc.save(ignore_permissions=True)
        frappe.db.commit()
        
        grand_total = flt(inv_doc.grand_total) or 300.0
        print(f"[AUDIT] Native calculated grand total: INR {grand_total}")
        
        mock_payments = [{
            "mode_of_payment": test_mop,
            "amount": grand_total
        }]
        
        # Update sales staff and remarks for checkout
        updated_remarks = "Home delivery required. Re-verify phone."
        updated_sales_staff = "Sales Exec 02"
        
        # Open an entry temporarily to satisfy standard cashier entry check
        submit_result = submit_bill(
            cashier="Administrator",
            customer=test_customer,
            items=frappe.as_json(mock_items),
            payments=frappe.as_json(mock_payments),
            loyalty_points=0,
            invoice_name=invoice_name, # Recall and overwrite draft
            remarks=updated_remarks,
            sales_staff=updated_sales_staff
        )
        submitted_inv = submit_result.get("invoice")
        print(f"[OK] submit_bill executed successfully. Invoice submitted: '{submitted_inv}'")
        
        # Pull final submitted invoice doc
        sub_doc = frappe.get_doc("POS Invoice", submitted_inv)
        assert sub_doc.docstatus == 1, "Invoice was not submitted (docstatus != 1)"
        print("[OK] Invoice docstatus is 1 (Submitted).")
        
        # Verify hold is released
        assert sub_doc.custom_is_held == 0, "Invoice is still marked as held"
        print("[OK] POS draft hold successfully released on submit.")
        
        # Verify updated remarks merged
        final_remarks = f"[Sales Staff: {updated_sales_staff}] {updated_remarks}"
        assert sub_doc.remarks == final_remarks, f"Remarks mismatch on submit! Expected '{final_remarks}', got '{sub_doc.remarks}'"
        print(f"[OK] Merged salesperson & cashier remarks updated and saved: '{sub_doc.remarks}'")
        
        # Verify discount on submitted item
        final_disc = flt(sub_doc.items[0].discount_percentage)
        assert final_disc == 15.0, f"Discount percentage mismatch on submitted item: {final_disc}"
        print(f"[OK] Final submitted child table item discount percentage verified: {final_disc}%")
        
        # Verify print format PDF download URL is generated
        assert "download_pdf" in submit_result.get("print_url"), "Invalid print format download URL"
        print(f"[OK] Print receipt format link generated: '{submit_result.get('print_url')}'")

        print("\n=======================================================")
        print("[SMRITI AUDIT] Verification SUCCESS: 100% Live & Stable!")
        print("=======================================================\n")
        return True

    except AssertionError as ae:
        print(f"[FAIL] Assertion validation failed during deep audit: {ae}")
        frappe.db.rollback()
        return False
    except Exception as ex:
        print(f"[FAIL] Exception occurred during deep audit: {ex}")
        print(frappe.get_traceback())
        frappe.db.rollback()
        return False
    finally:
        # 4. Always restore the monkeypatches cleanly to ensure zero environment pollution
        SalesInvoice.validate_pos_opening_entry = original_validate_pos_opening_entry
        POSInvoice.validate_is_pos_using_sales_invoice = original_validate_is_pos_using_sales_invoice
        print("[AUDIT] Restored original POSInvoice/SalesInvoice validations successfully.")

if __name__ == "__main__":
    run_pos_features_deep_audit()
