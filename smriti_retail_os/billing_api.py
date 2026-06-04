# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/billing_api.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.utils import flt, cint, now_datetime, nowdate
from frappe import _
from smriti_retail_os.utils.invoice_utils import get_barcode_candidates

@frappe.whitelist()
def add_item_by_barcode(barcode, price_list="Standard Selling"):
    """
    Looks up an item by barcode and returns item code, rate, MRP, tax details, and stock.
    """
    if not barcode:
        return None

    candidates = get_barcode_candidates(barcode)
    
    item_code = None
    for cand in candidates:
        item_code = frappe.db.get_value("Item Barcode", {"barcode": cand}, "parent")
        if item_code:
            break
            
    if not item_code:
        for cand in candidates:
            if frappe.db.exists("Item", cand):
                item_code = cand
                break

    if not item_code:
        return None

    item_doc = frappe.get_doc("Item", item_code)
    
    # Get standard selling price
    rate = frappe.db.get_value(
        "Item Price", 
        {"item_code": item_code, "price_list": price_list}, 
        "price_list_rate"
    ) or item_doc.valuation_rate or 0.0

    # Get MRP
    mrp = item_doc.custom_mrp or frappe.db.get_value(
        "Item Price", 
        {"item_code": item_code, "price_list": "MRP"}, 
        "price_list_rate"
    ) or rate

    # Resolve tax details (India Compliance Integration)
    gst_percentage = cint(item_doc.custom_gst_percentage) if item_doc.custom_gst_percentage else 0
    tax_template = ""
    if item_doc.taxes:
        tax_template = item_doc.taxes[0].item_tax_template

    # Fetch dynamic stock for the default warehouse using raw SQL to bypass strict SELECT sanitization
    stock_res = frappe.db.sql(
        "SELECT SUM(actual_qty) FROM `tabBin` WHERE item_code=%s",
        (item_code,)
    )
    stock_qty = stock_res[0][0] if stock_res and stock_res[0][0] is not None else 0.0

    return {
        "item_code": item_doc.name,
        "item_name": item_doc.item_name,
        "stock_uom": item_doc.stock_uom,
        "brand": item_doc.brand,
        "item_group": item_doc.item_group,
        "rate": flt(rate),
        "mrp": flt(mrp),
        "gst_percentage": gst_percentage,
        "tax_template": tax_template,
        "available_qty": flt(stock_qty)
    }


@frappe.whitelist()
def search_customer(query=None):
    """
    Searches for a customer by name or mobile number.
    Returns the first 20 active customers if query is empty.
    """
    filters = {"disabled": 0}
    or_filters = None
    if query:
        or_filters = {
            "customer_name": ["like", f"%{query}%"],
            "mobile_no": ["like", f"%{query}%"]
        }

    res = frappe.db.get_all(
        "Customer",
        filters=filters,
        or_filters=or_filters,
        fields=[
            "name", 
            "customer_name", 
            "mobile_no", 
            "loyalty_program", 
            "customer_group", 
            "customer_type",
            "custom_tax_inclusive_override",
            "custom_address_text",
            "custom_shipping_address_text"
        ],
        limit=20
    )
    
    # Map mobile_no to primary_mobile_no for frontend compatibility
    for r in res:
        r["primary_mobile_no"] = r.get("mobile_no")
        
    return res


@frappe.whitelist()
def hold_bill(cashier, customer, items, remarks=None, sales_staff=None):
    """
    Holds the active bill by creating a Draft POS Invoice (docstatus = 0) with:
    - custom_is_held = 1
    - custom_held_by = cashier
    - custom_hold_time = now_datetime()
    """
    if not items:
        frappe.throw(_("Cannot hold an empty bill."))

    items_list = frappe.parse_json(items)
    
    pos_invoice = frappe.new_doc("POS Invoice")
    pos_invoice.owner = cashier
    pos_invoice.customer = customer or "Walk-In Customer"
    pos_invoice.posting_date = nowdate()
    
    # Custom SMRITI Hold Fields
    pos_invoice.custom_is_held = 1
    pos_invoice.custom_held_by = cashier
    pos_invoice.custom_hold_time = now_datetime()
    
    # Set standard POS defaults
    pos_invoice.company = frappe.defaults.get_user_default("company") or frappe.get_all("Company", limit=1)[0].name
    pos_invoice.currency = "INR"
    pos_invoice.selling_price_list = "Standard Selling"
    
    # Prepend Sales Staff commission context cleanly to remarks
    final_remarks = ""
    if sales_staff:
        final_remarks += f"[Sales Staff: {sales_staff}] "
    if remarks:
        final_remarks += remarks
        
    if final_remarks:
        pos_invoice.remarks = final_remarks

    # Append items
    for it in items_list:
        pos_invoice.append("items", {
            "item_code": it.get("item_code"),
            "qty": flt(it.get("qty")),
            "rate": flt(it.get("rate")),
            "discount_percentage": flt(it.get("discount_percentage") or 0.0),
            "price_list_rate": flt(it.get("mrp")),
            "uom": it.get("stock_uom") or "Nos"
        })
        
    pos_invoice.docstatus = 0 # Draft
    pos_invoice.flags.ignore_validate = True # Bypass POS opening entry / profile checks for held draft holds!
    pos_invoice.flags.ignore_mandatory = True # Bypass standard database mandatory field checks!
    pos_invoice.save(ignore_permissions=True)
    frappe.db.commit()

    return {
        "invoice_name": pos_invoice.name,
        "message": _("Bill put on hold successfully.")
    }


@frappe.whitelist()
def recall_bill(cashier):
    """
    Returns the list of held draft invoices where custom_is_held = 1 and custom_held_by = cashier.
    """
    return frappe.db.get_all(
        "POS Invoice",
        filters={
            "docstatus": 0,
            "custom_is_held": 1,
            "custom_held_by": cashier
        },
        fields=["name", "customer", "posting_date", "grand_total", "custom_hold_time"],
        order_by="custom_hold_time desc"
    )


@frappe.whitelist()
def submit_bill(cashier, customer, items, payments, loyalty_points=0, invoice_name=None, remarks=None, sales_staff=None, on_credit=0, tax_override="Default", billing_address=None, shipping_address=None, billing_session_id=None):
    """
    Creates and submits a standard POS Invoice or falls back to Sales Invoice.
    Uses billing_session_id for idempotency to prevent double-billing.
    """
    # 0. Idempotency Check
    if billing_session_id:
        existing = frappe.db.get_value("POS Invoice", {"custom_billing_session_id": billing_session_id}, ["name", "grand_total"], as_dict=True)
        if not existing:
            existing = frappe.db.get_value("Sales Invoice", {"custom_billing_session_id": billing_session_id}, ["name", "grand_total"], as_dict=True)
        
        if existing:
            dt = "POS Invoice" if frappe.db.exists("POS Invoice", existing.name) else "Sales Invoice"
            return {
                "invoice": existing.name,
                "grand_total": flt(existing.grand_total),
                "print_url": f"/api/method/frappe.utils.print_format.download_pdf?doctype={dt}&name={existing.name}&format=Standard",
                "idempotent": True
            }
    if not items:
        frappe.throw(_("Cannot submit an empty bill."))

    items_list = frappe.parse_json(items)
    payments_list = frappe.parse_json(payments)
    on_credit = cint(on_credit)
    
    company = frappe.defaults.get_user_default("company") or frappe.get_all("Company", limit=1)[0].name
    
    # Check if there is an active open shift for this cashier
    has_open_shift = frappe.db.exists("POS Opening Entry", {
        "user": cashier,
        "status": "Open",
        "docstatus": 1
    })

    # If overwriting a recalled held draft POS Invoice
    is_recalled = bool(invoice_name and frappe.db.exists("POS Invoice", invoice_name))
    
    if on_credit:
        doctype = "Sales Invoice"
        use_pos = False
        if is_recalled:
            frappe.delete_doc("POS Invoice", invoice_name, ignore_permissions=True)
            is_recalled = False
    else:
        use_pos = is_recalled or has_open_shift
        doctype = "POS Invoice" if use_pos else "Sales Invoice"

    if is_recalled:
        invoice_doc = frappe.get_doc("POS Invoice", invoice_name)
        invoice_doc.custom_is_held = 0 # Release hold
        invoice_doc.items = []
        invoice_doc.payments = []
    else:
        invoice_doc = frappe.new_doc(doctype)
        invoice_doc.owner = cashier
        
    invoice_doc.customer = customer or "Walk-In Customer"
    invoice_doc.custom_billing_session_id = billing_session_id
    
    # Resolve and link Billing & Shipping Addresses (Bill To and Ship To)
    if invoice_doc.customer and invoice_doc.customer != "Walk-In Customer":
        billing_addr_name = frappe.db.get_value(
            "Address",
            {
                "links.link_doctype": "Customer",
                "links.link_name": invoice_doc.customer,
                "address_type": "Billing"
            },
            "name"
        )
        shipping_addr_name = frappe.db.get_value(
            "Address",
            {
                "links.link_doctype": "Customer",
                "links.link_name": invoice_doc.customer,
                "address_type": "Shipping"
            },
            "name"
        )
        
        if billing_addr_name:
            invoice_doc.customer_address = billing_addr_name
            invoice_doc.address_display = frappe.db.get_value("Address", billing_addr_name, "display")
        if shipping_addr_name:
            invoice_doc.shipping_address_name = shipping_addr_name
            invoice_doc.shipping_address = frappe.db.get_value("Address", shipping_addr_name, "display")

    # Resolve tax override from Customer doc if set to Default
    resolved_tax_override = tax_override
    if resolved_tax_override == "Default" and invoice_doc.customer and invoice_doc.customer != "Walk-In Customer" and frappe.db.exists("Customer", invoice_doc.customer):
        cust_override = frappe.db.get_value("Customer", invoice_doc.customer, "custom_tax_inclusive_override")
        if cust_override:
            resolved_tax_override = cust_override

    invoice_doc.posting_date = nowdate()
    invoice_doc.company = company
    invoice_doc.currency = "INR"
    invoice_doc.selling_price_list = "Standard Selling"
    invoice_doc.update_stock = 1 if (use_pos or on_credit) else 0
    invoice_doc.is_pos = 1 if use_pos else 0
    
    # Combine remarks and sales staff cleanly to bypass standard database migration overrides
    final_remarks = ""
    if sales_staff:
        final_remarks += f"[Sales Staff: {sales_staff}] "
    if remarks:
        final_remarks += remarks
        
    if final_remarks:
        invoice_doc.remarks = final_remarks

    # Pre-resolve a company-level fallback warehouse once (avoid repeated DB hits)
    _fallback_wh = frappe.defaults.get_user_default("warehouse")
    if _fallback_wh and frappe.db.get_value("Warehouse", _fallback_wh, "company") != company:
        _fallback_wh = None
        
    if not _fallback_wh:
        _fallback_wh = (
            frappe.db.get_value("Warehouse", {"warehouse_name": "Stores", "company": company}, "name")
            or frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")
        )

    # Resolve default taxes and charges template for the company if none set
    default_tax_template = frappe.db.get_value(
        "Sales Taxes and Charges Template",
        {"company": company, "is_default": 1},
        "name"
    )
    if default_tax_template:
        invoice_doc.taxes_and_charges = default_tax_template
        invoice_doc.run_method("set_taxes")

    for it in items_list:
        # Item Default child table holds per-company default warehouses
        item_wh = frappe.db.get_value(
            "Item Default",
            {"parent": it.get("item_code"), "company": company},
            "default_warehouse"
        ) or _fallback_wh

        # Resolve tax template — prefer caller-supplied, fall back to item's first matching template
        tax_template = it.get("tax_template") or it.get("item_tax_template")
        if not tax_template:
            item_doc = frappe.get_doc("Item", it.get("item_code"))
            for t in item_doc.taxes:
                # Verify this template actually exists and belongs to the company
                tmpl_company = frappe.db.get_value("Item Tax Template", t.item_tax_template, "company")
                if tmpl_company == company:
                    tax_template = t.item_tax_template
                    break

        # Final safety: verify the resolved template exists and belongs to this company
        if tax_template:
            tmpl_company = frappe.db.get_value("Item Tax Template", tax_template, "company")
            if not tmpl_company or tmpl_company != company:
                tax_template = None

        # Resolve cost center robustly to prevent validation failures on clean DBs
        item_cc = it.get("cost_center") or frappe.db.get_value("Company", company, "cost_center")
        if not item_cc:
            item_cc = frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")

        # Resolve rate backing out tax if override is set to Inclusive
        rate = flt(it.get("rate"))
        gst_pct = flt(it.get("gst_percentage") or it.get("custom_gst_percentage") or 0.0)
        if gst_pct <= 0.0:
            gst_pct = flt(frappe.db.get_value("Item", it.get("item_code"), "custom_gst_percentage") or 0.0)
            
        if resolved_tax_override == "Inclusive" and gst_pct > 0.0:
            rate = rate / (1.0 + (gst_pct / 100.0))

        invoice_doc.append("items", {
            "item_code": it.get("item_code"),
            "qty": flt(it.get("qty")),
            "rate": rate,
            "price_list_rate": flt(it.get("mrp")),
            "discount_percentage": flt(it.get("discount_percentage") or 0.0),
            "uom": it.get("stock_uom") or "Nos",
            "warehouse": item_wh,
            "item_tax_template": tax_template,
            "cost_center": item_cc
        })
        
    # 2. Split Payments
    for p in payments_list:
        if flt(p.get("amount")) > 0:
            mop = p.get("mode_of_payment")
            mop_account = frappe.db.get_value(
                "Mode of Payment Account",
                {"parent": mop, "company": company},
                "default_account"
            )
            invoice_doc.append("payments", {
                "mode_of_payment": mop,
                "amount": flt(p.get("amount")),
                "account": mop_account
            })
            
    # 3. Loyalty Points Redemption
    if loyalty_points and int(loyalty_points) > 0:
        loyalty_program = frappe.db.get_value("Customer", invoice_doc.customer, "loyalty_program")
        if loyalty_program:
            invoice_doc.redeem_loyalty_points = 1
            invoice_doc.loyalty_points = int(loyalty_points)
            invoice_doc.loyalty_program = loyalty_program

    # 4. Save and Submit
    if is_recalled:
        invoice_doc.save(ignore_permissions=True)
    else:
        invoice_doc.insert(ignore_permissions=True)
    
    invoice_doc.submit()
    
    # REL-02: Move non-critical post-billing tasks to background workers
    # This prevents UI blocking and DB lock contention
    frappe.enqueue(
        "smriti_retail_os.smriti_retail_os.billing_api.process_post_billing_tasks",
        invoice_name=invoice_doc.name,
        doctype=doctype,
        payments_list=payments_list,
        company=company,
        now=False
    )
    
    frappe.db.commit()
    
    # 5. Return success details with standard printing URL
    print_url = f"/api/method/frappe.utils.print_format.download_pdf?doctype={doctype}&name={invoice_doc.name}&format=Standard"
    
    return {
        "invoice": invoice_doc.name,
        "grand_total": flt(invoice_doc.grand_total),
        "print_url": print_url
    }

def process_post_billing_tasks(invoice_name, doctype, payments_list, company):
    """
    Background worker to handle non-critical billing tasks:
    1. Reconcile Payment Entries for Sales Invoices.
    """
    if doctype == "Sales Invoice":
        from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
        total_paid = sum(flt(p.get("amount")) for p in payments_list)
        if total_paid > 0:
            try:
                pe = get_payment_entry(doctype, invoice_name)
                if payments_list:
                    first_p = payments_list[0]
                    pe.mode_of_payment = first_p.get("mode_of_payment")
                    pe.paid_to = frappe.db.get_value(
                        "Mode of Payment Account",
                        {"parent": pe.mode_of_payment, "company": company},
                        "default_account"
                    ) or pe.paid_to
                pe.flags.ignore_permissions = True
                pe.insert(ignore_permissions=True)
                pe.submit()
                frappe.db.commit()
                frappe.logger().info(f"[SMRITI] Background Payment Entry created for {invoice_name}")
            except Exception as e:
                frappe.log_error(f"Post-Billing Payment Entry Error for {invoice_name}: {str(e)}")


@frappe.whitelist()
def search_items(query, price_list="Standard Selling"):
    """
    Searches items by code, name, brand, or group. Returns rates, MRPs, and GST details.
    """
    if not query:
        return []
    
    items = frappe.db.get_all(
        "Item",
        filters={
            "disabled": 0,
            "custom_is_retail_item": 1
        },
        or_filters={
            "item_code": ["like", f"%{query}%"],
            "item_name": ["like", f"%{query}%"],
            "brand": ["like", f"%{query}%"],
            "item_group": ["like", f"%{query}%"]
        },
        fields=["name", "item_name", "stock_uom", "brand", "item_group", "custom_mrp", "custom_gst_percentage", "valuation_rate"]
    )
    
    results = []
    for it in items:
        # Get standard selling price
        rate = frappe.db.get_value(
            "Item Price", 
            {"item_code": it.name, "price_list": price_list}, 
            "price_list_rate"
        ) or it.valuation_rate or 0.0
        
        # Get MRP
        mrp = it.custom_mrp or frappe.db.get_value(
            "Item Price", 
            {"item_code": it.name, "price_list": "MRP"}, 
            "price_list_rate"
        ) or rate
        
        gst_percentage = cint(it.custom_gst_percentage) if it.custom_gst_percentage else 0
        
        # Resolve tax template
        tax_template = ""
        item_doc = frappe.get_cached_doc("Item", it.name)
        if item_doc.taxes:
            tax_template = item_doc.taxes[0].item_tax_template
            
        results.append({
            "item_code": it.name,
            "item_name": it.item_name,
            "stock_uom": it.stock_uom,
            "brand": it.brand,
            "item_group": it.item_group,
            "rate": flt(rate),
            "mrp": flt(mrp),
            "gst_percentage": gst_percentage,
            "tax_template": tax_template
        })
    return results


@frappe.whitelist()
def load_held_invoice(invoice_name):
    """
    Loads a held Draft POS Invoice so the frontend can reconstruct its cart.
    """
    if not invoice_name:
        return None
    
    inv = frappe.get_doc("POS Invoice", invoice_name)
    if inv.docstatus != 0 or not inv.custom_is_held:
        frappe.throw(_("Invoice {0} is not a held draft invoice.").format(invoice_name))
        
    items = []
    for it in inv.items:
        item_doc = frappe.get_cached_doc("Item", it.item_code)
        
        # Get MRP
        mrp = item_doc.custom_mrp or frappe.db.get_value(
            "Item Price", 
            {"item_code": it.item_code, "price_list": "MRP"}, 
            "price_list_rate"
        ) or it.rate
        
        gst_percentage = cint(item_doc.custom_gst_percentage) if item_doc.custom_gst_percentage else 0
        
        # Resolve tax template
        tax_template = ""
        if item_doc.taxes:
            tax_template = item_doc.taxes[0].item_tax_template
            
        items.append({
            "item_code": it.item_code,
            "item_name": it.item_name,
            "stock_uom": it.uom,
            "qty": flt(it.qty),
            "rate": flt(it.rate),
            "discount_percentage": flt(it.discount_percentage or 0.0),
            "mrp": flt(mrp),
            "gst_percentage": gst_percentage,
            "tax_template": tax_template
        })
        
    return {
        "invoice_name": inv.name,
        "customer": inv.customer,
        "remarks": inv.remarks,
        "items": items
    }


@frappe.whitelist()
def validate_manager_override(pin, action_type, invoice_name=None):
    """
    Validates entered PIN against users with SMRITI Store Manager or System Manager role.
    Checks custom_smriti_pin first, then falls back to primary login password.
    """
    if not pin:
        return {"authorized": False, "message": _("PIN is required.")}

    from frappe.utils.password import check_password as check_smriti_pin
    import frappe.auth

    # Find users with manager roles
    managers = frappe.db.get_all(
        "Has Role",
        filters={"role": ["in", ["SMRITI Store Manager", "System Manager"]]},
        pluck="parent"
    )

    for mgr in set(managers):
        # Only active users
        if not frappe.db.get_value("User", mgr, "enabled"):
            continue

        authenticated = False
        try:
            # 1. Try SMRITI Dedicated PIN first
            if frappe.db.get_value("User", mgr, "custom_smriti_pin"):
                try:
                    check_smriti_pin(mgr, pin, fieldname="custom_smriti_pin")
                    authenticated = True
                except frappe.AuthenticationError:
                    pass

            # 2. Fallback to primary password
            if not authenticated:
                frappe.auth.check_password(mgr, pin)
                authenticated = True

            if authenticated:
                # Verify manager role after auth
                roles = frappe.get_roles(mgr)
                if "SMRITI Store Manager" in roles or "System Manager" in roles:
                    # Log override action using standard Comment
                    if invoice_name:
                        frappe.get_doc({
                            "doctype": "Comment",
                            "comment_type": "Comment",
                            "reference_doctype": "POS Invoice",
                            "reference_name": invoice_name,
                            "content": f"Manager Override approved by {mgr} for action: {action_type}",
                            "comment_email": frappe.session.user,
                            "comment_by": frappe.session.user
                        }).insert(ignore_permissions=True)
                    else:
                        # Generic Comment / Log
                        frappe.logger().info(f"SMRITI: Manager Override approved by {mgr} for action: {action_type}")

                    return {
                        "authorized": True,
                        "manager": mgr
                    }
        except frappe.AuthenticationError:
            pass
        except Exception as e:
            frappe.log_error(title="SMRITI Manager Password Authentication Error", message=frappe.get_traceback())

    return {"authorized": False, "message": _("Invalid PIN Code or unauthorized role.")}

@frappe.whitelist()
def generate_mock_eway_bill(invoice_name, vehicle_no=None, distance=None, mode_of_transport=None, gst_vehicle_type=None, transporter_name=None):
    """
    Generates a mock 12-digit E-way Bill number for the invoice to support
    Vyapar-style prints and standalone demo generations.
    """
    if not invoice_name:
        frappe.throw(_("Invoice name is required."))
        
    # Check if E-way bill already exists to support editing transport/vehicle details
    existing_eway = frappe.db.get_value("Sales Invoice", invoice_name, "ewaybill")
    if existing_eway:
        mock_no = existing_eway
        msg = _("E-way Bill {0} details updated successfully!").format(mock_no)
    else:
        import random
        # Format: 23 + 10 random digits (e.g. 232207255170)
        mock_no = f"23{random.randint(1000000000, 9999999999)}"
        msg = _("E-way Bill {0} generated successfully!").format(mock_no)
    
    # Direct DB set to avoid draft/submitted validations on historical records
    update_dict = {"ewaybill": mock_no}
    if vehicle_no is not None:
        update_dict["vehicle_no"] = vehicle_no
    if distance is not None:
        try:
            update_dict["distance"] = int(distance)
        except ValueError:
            pass
    if mode_of_transport is not None:
        update_dict["mode_of_transport"] = mode_of_transport
    if gst_vehicle_type is not None:
        update_dict["gst_vehicle_type"] = gst_vehicle_type
    if transporter_name is not None:
        update_dict["transporter_name"] = transporter_name
        
    frappe.db.set_value("Sales Invoice", invoice_name, update_dict)
    frappe.db.commit()
    
    return {
        "ewaybill": mock_no,
        "message": msg
    }

