# -*- coding: utf-8 -*-
import frappe
from smriti_retail_os.purchase_studio.service.purchase_order_service import PurchaseOrderService
from smriti_retail_os.purchase_studio.service.purchase_workflow_service import PurchaseWorkflowService
from smriti_retail_os.purchase_studio.service import purchase_service

def run():
    # Ensure GST HSN Code exists for India Compliance validator
    hsn_code = frappe.db.get_value("GST HSN Code", {}, "name")
    if not hsn_code:
        try:
            hsn = frappe.new_doc("GST HSN Code")
            hsn.name = "999999"
            hsn.hsn_code = "999999"
            hsn.insert(ignore_permissions=True)
            hsn_code = hsn.name
        except Exception:
            pass

    # Ensure test item exists
    item_code = "SMRITI-TEST-ITEM-1"
    if not frappe.db.exists("Item", item_code):
        item = frappe.new_doc("Item")
        item.item_code = item_code
        item.item_name = "SMRITI Test Item 1"
        item.item_group = "Products"
        item.stock_uom = "Nos"
        if hsn_code:
            item.gst_hsn_code = hsn_code
        item.insert(ignore_permissions=True)
    else:
        # Ensure HSN is set on existing item
        if hsn_code:
            frappe.db.set_value("Item", item_code, "gst_hsn_code", hsn_code)

    # 1. Create SMRITI Supplier
    sup_name = "SMRITI Test Supplier Cycle"
    # Clean up if exists
    frappe.db.delete("SMRITI Supplier", {"supplier_name": sup_name})
    frappe.db.delete("SMRITI Supplier", {"name": sup_name})

    sup_id = PurchaseOrderService.create_supplier({
        "supplier_name": sup_name,
        "email_id": "cycle_sup@smriti.com"
    })

    # 2. Create SMRITI Purchase Order
    po_res = PurchaseOrderService.create_purchase_order(
        supplier=sup_id,
        items_list=[{"item_code": item_code, "qty": 10.0, "rate": 150.0}],
        remarks="Test cycle PO"
    )
    po_name = po_res["name"]

    # Approve and transition PO to Ordered
    PurchaseWorkflowService.order(po_name)

    # 3. Create GRN (submits real Purchase Receipt via erp_adapter!)
    grn_res = purchase_service.create_grn(
        po_name=po_name,
        items_list=[{"item_code": item_code, "qty": 10.0}]
    )
    grn_name = grn_res["name"]

    # 4. Create Invoice (submits real Purchase Invoice!)
    inv_res = purchase_service.create_invoice(
        mode="grn_linked",
        supplier=sup_id,
        grn_name=grn_name
    )
    invoice_name = inv_res["name"]

    # 5. Create Return (submits real Purchase Receipt as Return!)
    ret_res = purchase_service.create_purchase_return(
        grn_name=grn_name,
        items_list=[{"item_code": item_code, "qty": 2.0}],
        return_reason="Damaged goods"
    )
    return_name = ret_res["return_name"]

    print("Cycle Created Successfully:")
    print(f"PO: {po_name}")
    print(f"GRN: {grn_name}")
    print(f"Invoice: {invoice_name}")
    print(f"Return: {return_name}")

    # Print erpnext_supplier of SMRITI Supplier (Step 7 Verification)
    smriti_sup = frappe.get_doc("SMRITI Supplier", sup_id)
    print(f"SMRITI Supplier: {smriti_sup.name}")
    print(f"ERPNext Supplier Link: {smriti_sup.erpnext_supplier}")

if __name__ == "__main__":
    run()
