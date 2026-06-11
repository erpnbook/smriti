# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/billing_api.py
# @description: Backend API for the SMRITI Retail Billing terminal.
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

    # Resolve tax details (India Compliance Integration — HSN-first)
    gst_percentage = cint(item_doc.custom_gst_percentage) if item_doc.custom_gst_percentage else 0
    if not gst_percentage and item_doc.gst_hsn_code:
        from smriti_retail_os.hooks_logic import get_gst_rate_from_hsn
        gst_percentage = get_gst_rate_from_hsn(item_doc.gst_hsn_code) or 0
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
        "gst_hsn_code": item_doc.gst_hsn_code or "",
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
        # NOTE: Do NOT delete the recalled POS Invoice here.
        # It will be cancelled/deleted AFTER the Sales Invoice is committed (see below).
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

    # Resolve and link Company Address (mandatory for Indian GST transactions)
    if not invoice_doc.company_address:
        company_addr_name = frappe.db.get_value(
            "Address",
            {
                "links.link_doctype": "Company",
                "links.link_name": company,
                "is_your_company_address": 1
            },
            "name"
        )
        if not company_addr_name:
            company_addr_name = frappe.db.get_value(
                "Address",
                {
                    "links.link_doctype": "Company",
                    "links.link_name": company
                },
                "name"
            )
        if company_addr_name:
            invoice_doc.company_address = company_addr_name

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

    # ── Pre-fetch all per-item data in batch to eliminate N+1 DB queries ─────
    item_codes = [it.get("item_code") for it in items_list]

    # Batch 1: Item Default warehouses — one query, not one per item
    item_defaults_rows = frappe.db.get_all(
        "Item Default",
        filters={"parent": ["in", item_codes], "company": company},
        fields=["parent", "default_warehouse"]
    )
    item_wh_map = {r.parent: r.default_warehouse for r in item_defaults_rows}

    # Batch 2: Item Tax Template assignments for these items
    item_tax_rows = frappe.db.get_all(
        "Item Tax",
        filters={"parent": ["in", item_codes]},
        fields=["parent", "item_tax_template"]
    )
    # Only first matching tax per item (same behaviour as previous per-item frappe.get_doc)
    item_tax_map = {}
    for r in item_tax_rows:
        if r.parent not in item_tax_map:
            item_tax_map[r.parent] = r.item_tax_template

    # Batch 3: Item Tax Template company ownership (to validate they belong to this company)
    all_templates = list(set(item_tax_map.values()))
    if all_templates:
        tmpl_rows = frappe.db.get_all(
            "Item Tax Template",
            filters={"name": ["in", all_templates]},
            fields=["name", "company"]
        )
        tmpl_company_map = {r.name: r.company for r in tmpl_rows}
    else:
        tmpl_company_map = {}

    # Batch 4: GST percentage per item (for tax-inclusive rate calculation)
    gst_rows = frappe.db.get_all(
        "Item",
        filters={"name": ["in", item_codes]},
        fields=["name", "custom_gst_percentage"]
    )
    item_gst_map = {r.name: flt(r.custom_gst_percentage or 0.0) for r in gst_rows}

    # Resolve company cost_center once (used as fallback for all items)
    company_cc = frappe.db.get_value("Company", company, "cost_center")
    if not company_cc:
        company_cc = frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")
    # ─────────────────────────────────────────────────────────────────────────

    for it in items_list:
        item_code = it.get("item_code")

        # Warehouse: pre-fetched item default → fallback warehouse
        item_wh = item_wh_map.get(item_code) or _fallback_wh

        # Tax template: caller-supplied → pre-fetched item tax → None
        tax_template = it.get("tax_template") or it.get("item_tax_template")
        if not tax_template:
            tax_template = item_tax_map.get(item_code)

        # Validate tax template belongs to this company (using pre-fetched map)
        if tax_template:
            if tmpl_company_map.get(tax_template) != company:
                tax_template = None

        # Cost center: caller-supplied → company default (pre-fetched)
        item_cc = it.get("cost_center") or company_cc

        # GST rate for tax-inclusive rate calculation (pre-fetched)
        rate = flt(it.get("rate"))
        gst_pct = flt(it.get("gst_percentage") or it.get("custom_gst_percentage") or 0.0)
        if gst_pct <= 0.0:
            gst_pct = item_gst_map.get(item_code, 0.0)

        if resolved_tax_override == "Inclusive" and gst_pct > 0.0:
            rate = rate / (1.0 + (gst_pct / 100.0))

        invoice_doc.append("items", {
            "item_code": item_code,
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
    try:
        if is_recalled:
            invoice_doc.save(ignore_permissions=True)
        else:
            invoice_doc.insert(ignore_permissions=True)

        invoice_doc.submit()
    except Exception:
        frappe.db.rollback()
        raise

    # C-02 FIX: Delete the recalled POS Invoice AFTER the replacement SI is committed.
    # If we deleted it before (as before), any failure during SI creation would result
    # in zero invoices with no recovery. Now the POS Invoice survives until SI is safe.
    if on_credit and invoice_name and frappe.db.exists("POS Invoice", invoice_name):
        try:
            frappe.delete_doc("POS Invoice", invoice_name, ignore_permissions=True)
        except Exception as del_ex:
            frappe.log_error(f"[SMRITI] Could not delete recalled POS Invoice {invoice_name}: {del_ex}")
    
    # REL-02: Move non-critical post-billing tasks to background workers
    # This prevents UI blocking and DB lock contention
    frappe.enqueue(
        "smriti_retail_os.billing_api.process_post_billing_tasks",
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
    1. Reconcile Payment Entries for Sales Invoices (idempotent — will not create duplicate PEs).
    """
    if doctype == "Sales Invoice":
        from erpnext.accounts.doctype.payment_entry.payment_entry import get_payment_entry
        total_paid = sum(flt(p.get("amount")) for p in payments_list)
        if total_paid > 0:
            try:
                # C-03 FIX: Idempotency check — do not create a PE if one already exists
                # for this invoice. Background workers can retry on failure, so this
                # prevents duplicate Payment Entries and double-payment in the ledger.
                existing_pe = frappe.db.get_value(
                    "Payment Entry Reference",
                    {"reference_name": invoice_name, "docstatus": 1},
                    "parent"
                )
                if existing_pe:
                    frappe.logger().info(f"[SMRITI] PE already exists ({existing_pe}) for {invoice_name}. Skipping.")
                    return

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
                frappe.log_error(f"Post-Billing Payment Entry Error for {invoice_name}: {frappe.get_traceback()}")


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
        fields=["name", "item_name", "stock_uom", "brand", "item_group", "custom_mrp", "custom_gst_percentage", "valuation_rate", "gst_hsn_code"]
    )
    
    # ── Batch-fetch all selling prices and MRP prices — eliminates N+1 per item ──
    item_names = [it.name for it in items]

    price_rows = frappe.db.get_all(
        "Item Price",
        filters={"item_code": ["in", item_names], "price_list": ["in", [price_list, "MRP"]]},
        fields=["item_code", "price_list", "price_list_rate"]
    )
    selling_price_map = {}   # item_code → selling rate
    mrp_price_map = {}       # item_code → MRP rate
    for pr in price_rows:
        if pr.price_list == price_list:
            selling_price_map[pr.item_code] = flt(pr.price_list_rate)
        elif pr.price_list == "MRP":
            mrp_price_map[pr.item_code] = flt(pr.price_list_rate)
    # ──────────────────────────────────────────────────────────────────────────

    results = []
    for it in items:
        # Prices now resolved from pre-fetched maps — zero DB hits per item
        rate = selling_price_map.get(it.name) or flt(it.valuation_rate) or 0.0
        mrp = flt(it.custom_mrp) or mrp_price_map.get(it.name) or rate

        gst_percentage = cint(it.custom_gst_percentage) if it.custom_gst_percentage else 0
        if not gst_percentage and it.gst_hsn_code:
            from smriti_retail_os.hooks_logic import get_gst_rate_from_hsn
            gst_percentage = get_gst_rate_from_hsn(it.gst_hsn_code) or 0

        # Resolve tax template — use cached doc (no extra DB hit)
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
            "tax_template": tax_template,
            "gst_hsn_code": it.gst_hsn_code or ""
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
            "tax_template": tax_template,
            "gst_hsn_code": item_doc.gst_hsn_code or ""
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
    Strictly requires custom_smriti_pin (no fallback to login password).
    """
    if not pin:
        return {"authorized": False, "message": _("PIN is required.")}

    # Redis rate limit check
    rate_limit_key = f"smriti_pin_attempts:{frappe.session.user}"
    attempts = frappe.cache().get(rate_limit_key)
    if attempts and int(attempts) >= 5:
        frappe.throw(_("Too many failed PIN attempts. Please try again in 10 minutes."), frappe.PermissionError)

    from frappe.utils.password import check_password as check_smriti_pin

    # Find users with manager roles
    managers = frappe.db.get_all(
        "Has Role",
        filters={"role": ["in", ["SMRITI Store Manager", "System Manager"]]},
        pluck="parent"
    )

    authenticated = False
    auth_manager = None
    for mgr in set(managers):
        # Only active users
        if not frappe.db.get_value("User", mgr, "enabled"):
            continue

        try:
            # Strictly use SMRITI Dedicated PIN
            if frappe.db.get_value("User", mgr, "custom_smriti_pin"):
                try:
                    check_smriti_pin(mgr, pin, fieldname="custom_smriti_pin")
                    # Verify manager role after auth
                    roles = frappe.get_roles(mgr)
                    if "SMRITI Store Manager" in roles or "System Manager" in roles:
                        authenticated = True
                        auth_manager = mgr
                        break
                except frappe.AuthenticationError:
                    pass
        except Exception:
            frappe.log_error(title="SMRITI Manager Override Error", message=frappe.get_traceback())

    if authenticated and auth_manager:
        # Clear attempts on success
        frappe.cache().delete(rate_limit_key)
        # Log override action using standard Comment
        if invoice_name:
            frappe.get_doc({
                "doctype": "Comment",
                "comment_type": "Comment",
                "reference_doctype": "POS Invoice",
                "reference_name": invoice_name,
                "content": f"Manager Override approved by {auth_manager} for: {action_type}",
                "comment_email": frappe.session.user,
                "comment_by": frappe.session.user
            }).insert(ignore_permissions=True)
        return {"authorized": True, "manager": auth_manager}

    # Increment failed attempts
    if attempts:
        frappe.cache().incr(rate_limit_key)
    else:
        frappe.cache().set(rate_limit_key, 1, ex=600)

    # Log failed PIN attempt to Error Log
    frappe.log_error(
        title="SMRITI Failed PIN Override Attempt",
        message=f"Failed PIN override attempt by user {frappe.session.user} for action {action_type}."
    )
    return {"authorized": False, "message": _("Manager authorization failed. Invalid PIN.")}

@frappe.whitelist()
def generate_mock_eway_bill(invoice_name, vehicle_no=None, distance=None, mode_of_transport=None, gst_vehicle_type=None, transporter_name=None):
    """
    Generates a mock 12-digit E-way Bill number for the invoice to support
    optimized retail layouts and standalone demo generations.
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

    # Audit: db.set_value bypasses on_update hooks on submitted invoices — log explicitly
    try:
        from smriti_retail_os.backup_api import log_audit_event
        action_label = "E-way Bill Updated" if existing_eway else "E-way Bill Generated"
        log_audit_event(
            action_label,
            f"{action_label}: Invoice={invoice_name}, EWB={mock_no}, User={frappe.session.user}, VehicleNo={vehicle_no or '-'}"
        )
    except Exception:
        frappe.log_error("SMRITI E-way Bill Audit Log Error", frappe.get_traceback())

    return {
        "ewaybill": mock_no,
        "message": msg
    }


@frappe.whitelist()
def create_return_invoice(invoice_name):
    """
    Creates and submits a return invoice (Sales/POS Return) against the original invoice.
    """
    docstatus = frappe.db.get_value("Sales Invoice", invoice_name, "docstatus")
    if docstatus is None:
        docstatus = frappe.db.get_value("POS Invoice", invoice_name, "docstatus")
        
    if docstatus is None:
        frappe.throw(_("Invoice {0} not found.").format(invoice_name))
        
    if docstatus != 1:
        frappe.throw(_("Invoice {0} must be submitted to create a return.").format(invoice_name))

    from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_sales_return
    
    return_doc = make_sales_return(invoice_name)
    
    try:
        return_doc.insert(ignore_permissions=True)
        return_doc.submit()
        frappe.db.commit()
    except Exception:
        frappe.db.rollback()
        raise

    return {
        "name": return_doc.name,
        "message": _("Return Invoice {0} created and submitted successfully.").format(return_doc.name)
    }


@frappe.whitelist()
def create_custom_sales_return(customer, items, return_against_invoice=None, remarks=None, company=None, draft=0):
    """
    Creates a Sales Return (Sales Invoice with is_return=1 and update_stock=1).
    Supports:
    1. Against a single bill (if return_against_invoice is provided).
    2. Standalone/without bills (if return_against_invoice is None).
    3. Against multiple bills (if items specify their respective parent invoice in return_against).
    """
    items_list = frappe.parse_json(items)
    draft = cint(draft)
    
    if not company:
        company = frappe.defaults.get_user_default("company") or frappe.get_all("Company", limit=1)[0].name

    if return_against_invoice:
        # 1. Against single bill
        from erpnext.accounts.doctype.sales_invoice.sales_invoice import make_sales_return
        return_doc = make_sales_return(return_against_invoice)
        
        # We need to filter and adjust return_doc.items based on user input
        matched_items = []
        for input_item in items_list:
            item_code = input_item.get("item_code")
            req_qty = flt(input_item.get("qty"))
            rate = input_item.get("rate")
            
            # Find matching item in return_doc.items
            found = False
            for row in return_doc.items:
                if row.item_code == item_code:
                    row.qty = -abs(req_qty)
                    if rate is not None:
                        row.rate = flt(rate)
                    matched_items.append(row)
                    found = True
                    break
        
        return_doc.items = matched_items
    else:
        # 2. Standalone or Multiple bills
        return_doc = frappe.new_doc("Sales Invoice")
        return_doc.is_return = 1
        return_doc.update_stock = 1
        return_doc.customer = customer or "Walk-In Customer"
        return_doc.company = company
        return_doc.posting_date = nowdate()
        return_doc.currency = "INR"
        return_doc.selling_price_list = "Standard Selling"
        
        # Pre-resolve default warehouse
        _fallback_wh = frappe.defaults.get_user_default("warehouse")
        if _fallback_wh and frappe.db.get_value("Warehouse", _fallback_wh, "company") != company:
            _fallback_wh = None
        if not _fallback_wh:
            _fallback_wh = (
                frappe.db.get_value("Warehouse", {"warehouse_name": "Stores", "company": company}, "name")
                or frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")
            )
            
        # Resolve default taxes template
        default_tax_template = frappe.db.get_value(
            "Sales Taxes and Charges Template",
            {"company": company, "is_default": 1},
            "name"
        )
        if default_tax_template:
            return_doc.taxes_and_charges = default_tax_template
            return_doc.run_method("set_taxes")
            
        company_cc = frappe.db.get_value("Company", company, "cost_center")
        if not company_cc:
            company_cc = frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")
            
        for it in items_list:
            item_code = it.get("item_code")
            qty = flt(it.get("qty"))
            rate = flt(it.get("rate") or 0.0)
            mrp = flt(it.get("mrp") or rate)
            wh = it.get("warehouse") or _fallback_wh
            
            item_row = {
                "item_code": item_code,
                "qty": -abs(qty), # Negative qty for returns
                "rate": rate,
                "price_list_rate": mrp,
                "uom": it.get("stock_uom") or "Nos",
                "warehouse": wh,
                "cost_center": it.get("cost_center") or company_cc,
            }
            
            if it.get("sales_invoice") and it.get("sales_invoice_item"):
                item_row["sales_invoice_item"] = it.get("sales_invoice_item")
                item_row["return_against"] = it.get("sales_invoice")
                
            return_doc.append("items", item_row)
            
    if remarks:
        return_doc.remarks = remarks
        
    return_doc.flags.ignore_permissions = True
    return_doc.insert(ignore_permissions=True)
    
    if not draft:
        return_doc.submit()
        
    frappe.db.commit()
    
    return {
        "name": return_doc.name,
        "docstatus": return_doc.docstatus,
        "message": _("Sales Return {0} created successfully as {1}.").format(
            return_doc.name, 
            "Draft" if draft else "Submitted"
        )
    }


@frappe.whitelist()
def update_sales_return(name, items, remarks=None, draft=0):
    """
    Updates a draft Sales Return invoice.
    Can also submit it if draft=0.
    """
    draft = cint(draft)
    if not frappe.db.exists("Sales Invoice", name):
        frappe.throw(_("Sales Return {0} not found.").format(name))
        
    doc = frappe.get_doc("Sales Invoice", name)
    if doc.docstatus != 0:
        frappe.throw(_("Only Draft Sales Returns can be edited."))
        
    if not doc.is_return:
        frappe.throw(_("Invoice {0} is not a return invoice.").format(name))
        
    items_list = frappe.parse_json(items)
    
    company = doc.company
    _fallback_wh = frappe.defaults.get_user_default("warehouse")
    if _fallback_wh and frappe.db.get_value("Warehouse", _fallback_wh, "company") != company:
        _fallback_wh = None
    if not _fallback_wh:
        _fallback_wh = (
            frappe.db.get_value("Warehouse", {"warehouse_name": "Stores", "company": company}, "name")
            or frappe.db.get_value("Warehouse", {"company": company, "is_group": 0}, "name")
        )
        
    company_cc = frappe.db.get_value("Company", company, "cost_center")
    if not company_cc:
        company_cc = frappe.db.get_value("Cost Center", {"company": company, "is_group": 0}, "name")

    doc.items = []
    for it in items_list:
        item_code = it.get("item_code")
        qty = flt(it.get("qty"))
        rate = flt(it.get("rate") or 0.0)
        mrp = flt(it.get("mrp") or rate)
        wh = it.get("warehouse") or _fallback_wh
        
        item_row = {
            "item_code": item_code,
            "qty": -abs(qty),
            "rate": rate,
            "price_list_rate": mrp,
            "uom": it.get("stock_uom") or "Nos",
            "warehouse": wh,
            "cost_center": it.get("cost_center") or company_cc,
        }
        
        if it.get("sales_invoice") and it.get("sales_invoice_item"):
            item_row["sales_invoice_item"] = it.get("sales_invoice_item")
            item_row["return_against"] = it.get("sales_invoice")
            
        doc.append("items", item_row)
        
    if remarks is not None:
        doc.remarks = remarks
        
    doc.flags.ignore_permissions = True
    doc.save(ignore_permissions=True)
    
    if not draft:
        doc.submit()
        
    frappe.db.commit()
    
    return {
        "name": doc.name,
        "docstatus": doc.docstatus,
        "message": _("Sales Return {0} updated successfully.").format(doc.name)
    }


@frappe.whitelist()
def delete_sales_return(name, manager_pin=None):
    """
    Deletes or cancels a Sales Return.
    If Draft: deletes the document.
    If Submitted: cancels the document.
    Requires SMRITI Store Manager or System Manager role, or a valid manager PIN override.
    """
    if not frappe.db.exists("Sales Invoice", name):
        frappe.throw(_("Sales Return {0} not found.").format(name))
        
    doc = frappe.get_doc("Sales Invoice", name)
    if not doc.is_return:
        frappe.throw(_("Invoice {0} is not a return invoice.").format(name))
        
    user = frappe.session.user
    roles = frappe.get_roles(user)
    has_manager_role = "SMRITI Store Manager" in roles or "System Manager" in roles
    
    if not has_manager_role:
        if not manager_pin:
            frappe.throw(_("Manager PIN override is required to cancel or delete a Sales Return."))
            
        override_res = validate_manager_override(manager_pin, f"Cancel/Delete Sales Return {name}", invoice_name=name)
        if not override_res.get("authorized"):
            frappe.throw(_("Invalid Manager PIN: Access Denied."))

    doc.flags.ignore_permissions = True
    if doc.docstatus == 0:
        frappe.delete_doc("Sales Invoice", name, ignore_permissions=True)
        message = _("Draft Sales Return {0} deleted successfully.").format(name)
    elif doc.docstatus == 1:
        doc.cancel()
        message = _("Sales Return {0} cancelled successfully.").format(name)
    else:
        frappe.throw(_("Sales Return {0} is already cancelled.").format(name))
        
    frappe.db.commit()
    return {
        "name": name,
        "message": message
    }



