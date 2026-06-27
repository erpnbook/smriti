# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/invoice_mapper.py
# @description: Decoupled translation service mapping SMRITI session states to ERPNext invoice schemas.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.0.0
# @license: MIT
#

import frappe
from frappe.utils import flt, cint

def map_smriti_session_to_invoice(invoice_doc, summary_data, sales_staff=None, remarks=None, company=None):
    """
    Pure mapping function translating the calculated SMRITI session summary state to ERPNext doc.
    Reserves raw ERPNext transaction layer for transactional commitment only.
    """
    if not company:
        company = invoice_doc.company

    # 1. Map header additional discount
    bill_discount = flt(summary_data.get("bill_discount") or 0.0)
    if bill_discount > 0.0:
        invoice_doc.apply_discount_on = "Net Total"
        invoice_doc.discount_amount = bill_discount
    else:
        invoice_doc.discount_amount = 0.0
        invoice_doc.additional_discount_percentage = 0.0

    # 2. Map Sales Persons to sales_team table
    salesperson_shares = {}
    total_sales_value = 0.0

    for pit in summary_data.get("items") or []:
        sp = pit.get("custom_sales_person")
        if sp:
            item_val = flt(pit.get("rate") or 0.0) * flt(pit.get("qty") or 0.0)
            salesperson_shares[sp] = salesperson_shares.get(sp, 0.0) + item_val
            total_sales_value += item_val

    # If no salespersons found on items, fallback to header sales_staff
    if not salesperson_shares and sales_staff:
        salesperson_shares[sales_staff] = 1.0
        total_sales_value = 1.0

    invoice_doc.sales_team = []
    invoice_grand_total = flt(summary_data.get("grand_total") or 0.0)
    
    for sp, val in salesperson_shares.items():
        allocated_pct = (val / total_sales_value * 100.0) if total_sales_value > 0.0 else (100.0 / len(salesperson_shares))
        commission_rate = frappe.db.get_value("Sales Person", sp, "commission_rate") or 0.0
        allocated_amt = invoice_grand_total * (allocated_pct / 100.0)
        
        invoice_doc.append("sales_team", {
            "sales_person": sp,
            "allocated_percentage": flt(allocated_pct),
            "allocated_amount": flt(allocated_amt),
            "commission_rate": commission_rate,
            "incentive_amount": flt(allocated_amt) * (flt(commission_rate) / 100.0)
        })

    if sales_staff:
        invoice_doc.custom_sales_person = sales_staff
    elif salesperson_shares:
        invoice_doc.custom_sales_person = list(salesperson_shares.keys())[0]
    else:
        invoice_doc.custom_sales_person = None

    # 3. Map items and item-level details
    # Clear and map items according to the computed items list
    mapped_items = []
    for idx, pit in enumerate(summary_data.get("items") or []):
        item_code = pit.get("item_code")
        qty = flt(pit.get("qty") or 0.0)
        rate = flt(pit.get("rate") or 0.0)
        item_disc = flt(pit.get("discount_amount") or 0.0)
        
        # Resolve default item details
        item_details = {
            "item_code": item_code,
            "qty": qty,
            "rate": rate,
            "price_list_rate": flt(pit.get("mrp") or pit.get("price_list_rate") or 0.0),
            "warehouse": pit.get("warehouse"),
            "item_tax_template": pit.get("item_tax_template"),
            "cost_center": pit.get("cost_center")
        }

        # Apply item-level discount mapping
        if item_disc > 0.0:
            item_details["discount_percentage"] = flt(pit.get("discount_percentage") or 0.0)
            if item_details["discount_percentage"] <= 0.0:
                # If calculated from value, map to discount_amount or compute percentage
                item_subtotal = rate * qty
                if item_subtotal > 0.0:
                    item_details["discount_percentage"] = flt((item_disc / item_subtotal) * 100.0)
                else:
                    item_details["discount_amount"] = item_disc

            # Map SMRITI discount reason
            item_details["custom_discount_reason"] = pit.get("custom_discount_reason") or pit.get("discount_reason")
        else:
            item_details["discount_percentage"] = 0.0
            item_details["discount_amount"] = 0.0
            item_details["custom_discount_reason"] = None

        # Map SMRITI item sales person override/inheritance
        item_details["custom_sales_person"] = pit.get("custom_sales_person")

        mapped_items.append(item_details)

    invoice_doc.items = []
    for mi in mapped_items:
        invoice_doc.append("items", mi)

    # 4. Map payment rows
    # Payment row mapping is handled during submit_bill directly, but we sync remarks
    final_remarks = ""
    if sales_staff:
        final_remarks += f"[Sales Staff: {sales_staff}] "
    if remarks:
        final_remarks += remarks
    if final_remarks:
        invoice_doc.remarks = final_remarks

    # Force tax and totals recalculation by ERPNext engine
    invoice_doc.run_method("calculate_taxes_and_totals")

    return invoice_doc
