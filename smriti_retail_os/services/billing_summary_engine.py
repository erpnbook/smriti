# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/billing_summary_engine.py
# @description: Central monetary calculations authority (Monetary Authority Rule compliant).
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.0.0
# @license: MIT
#

import frappe
from frappe.utils import flt, cint

@frappe.whitelist()
def calculate_billing_summary(items, bill_discount_percentage=0.0, bill_discount_amount=0.0, tax_inclusive=True, company=None):
    """
    Applies the frozen monetary calculations hierarchy:
    Item Rate * Qty -> Item Discount -> Subtotal -> Bill Discount -> GST/Taxes -> Grand Total.
    """
    bill_discount_percentage = flt(bill_discount_percentage or 0.0)
    bill_discount_amount = flt(bill_discount_amount or 0.0)

    # 1. Resolve GST rates in batch if item details are missing tax parameters
    item_codes = [it.get("item_code") for it in items if it.get("item_code")]
    item_gst_map = {}
    if item_codes:
        rows = frappe.db.get_all(
            "Item",
            filters={"name": ["in", item_codes]},
            fields=["name", "custom_gst_percentage"]
        )
        item_gst_map = {r.name: flt(r.custom_gst_percentage or 0.0) for r in rows}

    subtotal = 0.0
    total_item_discount = 0.0
    processed_items = []

    # Calculate item-level subtotals and discounts
    for it in items:
        qty = flt(it.get("qty") or 0.0)
        rate = flt(it.get("rate") or 0.0)
        item_subtotal = rate * qty

        # Determine item-level discount
        disc_pct = flt(it.get("discount_percentage") or 0.0)
        disc_amt = flt(it.get("discount_amount") or 0.0)
        
        # Support dynamic discount type/value structure if present
        if it.get("discount_type") == "%":
            disc_pct = flt(it.get("discount_value") or 0.0)
            disc_amt = 0.0
        elif it.get("discount_type") == "₹":
            disc_amt = flt(it.get("discount_value") or 0.0)
            disc_pct = 0.0

        if disc_pct > 0.0:
            item_disc = flt(item_subtotal * (disc_pct / 100.0))
        else:
            item_disc = disc_amt

        item_net = item_subtotal - item_disc
        
        subtotal += item_subtotal
        total_item_discount += item_disc

        # Resolve GST percentage
        gst_pct = flt(it.get("gst_percentage") or it.get("custom_gst_percentage") or 0.0)
        if gst_pct <= 0.0:
            gst_pct = item_gst_map.get(it.get("item_code"), 0.0)

        processed_item = it.copy()
        processed_item["qty"] = qty
        processed_item["rate"] = rate
        processed_item["subtotal"] = item_subtotal
        processed_item["discount_amount"] = item_disc
        processed_item["net_amount"] = item_net
        processed_item["gst_percentage"] = gst_pct
        processed_items.append(processed_item)

    # Net total before bill discount
    net_total = subtotal - total_item_discount

    # Calculate bill-level discount
    if bill_discount_percentage > 0.0:
        bill_discount = flt(net_total * (bill_discount_percentage / 100.0))
    else:
        bill_discount = bill_discount_amount

    final_net_total = net_total - bill_discount

    # Calculate taxes and proportional discounts per item row
    total_tax = 0.0
    for pit in processed_items:
        item_net = pit["net_amount"]
        
        # Distribute bill discount proportionally
        if net_total > 0.0:
            prop_bill_disc = flt(bill_discount * (item_net / net_total))
        else:
            prop_bill_disc = 0.0

        item_tax_base = item_net - prop_bill_disc
        gst_pct = pit["gst_percentage"]

        # Calculate GST
        if tax_inclusive:
            tax = flt(item_tax_base * (gst_pct / (100.0 + gst_pct)))
            net_rate = item_tax_base - tax
        else:
            tax = flt(item_tax_base * (gst_pct / 100.0))
            net_rate = item_tax_base

        pit["bill_discount_proportion"] = prop_bill_disc
        pit["tax_base"] = item_tax_base
        pit["tax_amount"] = tax
        pit["net_rate"] = net_rate
        total_tax += tax

    # Final totals calculations
    if tax_inclusive:
        grand_total = final_net_total
    else:
        grand_total = final_net_total + total_tax

    rounded_grand_total = flt(round(grand_total))
    rounding_adjustment = flt(rounded_grand_total - grand_total)

    return {
        "subtotal": flt(subtotal),
        "total_item_discount": flt(total_item_discount),
        "bill_discount": flt(bill_discount),
        "net_total": flt(net_total),
        "final_net_total": flt(final_net_total),
        "total_tax": flt(total_tax),
        "grand_total": flt(grand_total),
        "rounded_grand_total": flt(rounded_grand_total),
        "rounding_adjustment": flt(rounding_adjustment),
        "items": processed_items
    }
