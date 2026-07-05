# -*- coding: utf-8 -*-
# SMRITI Purchase Studio — Purchase Calculation Service
from frappe.utils import flt

class PurchaseCalculationService:
    @staticmethod
    def calculate_row_amounts(po_doc):
        """Calculates amount = qty * rate for all item rows."""
        for item in po_doc.get("items") or []:
            item.amount = flt(item.qty) * flt(item.rate)

    @staticmethod
    def calculate_totals(po_doc):
        """Calculates grand total and total qty."""
        PurchaseCalculationService.calculate_row_amounts(po_doc)
        total_qty = 0.0
        grand_total = 0.0
        for item in po_doc.get("items") or []:
            total_qty += flt(item.qty)
            grand_total += flt(item.amount)
        po_doc.total_qty = total_qty
        po_doc.grand_total = grand_total

    @staticmethod
    def calculate_pending_qty(po_doc):
        """Calculates pending_qty for each item row."""
        for item in po_doc.get("items") or []:
            item.pending_qty = max(0.0, flt(item.qty) - flt(item.received_qty))

    @staticmethod
    def calculate_per_received(po_doc):
        """Computes the overall percentage received."""
        PurchaseCalculationService.calculate_pending_qty(po_doc)
        total_qty = 0.0
        total_received = 0.0
        for item in po_doc.get("items") or []:
            total_qty += flt(item.qty)
            total_received += flt(item.received_qty)
        if total_qty > 0:
            po_doc.per_received = flt(total_received / total_qty) * 100.0
        else:
            po_doc.per_received = 0.0
