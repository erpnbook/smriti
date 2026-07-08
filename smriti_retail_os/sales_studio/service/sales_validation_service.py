# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/sales_studio/service/sales_validation_service.py
# @desc:    Validation service for SMRITI Sales Studio.
# @author:  Jawahar R. Mallah
#

import frappe
from frappe import _
from frappe.utils import flt

class SalesValidationError(frappe.ValidationError):
    pass

class SalesValidationService:
    @staticmethod
    def validate_store_manager_role():
        """
        Enforces that only SMRITI Store Manager or System Manager can perform submissions.
        """
        roles = frappe.get_roles(frappe.session.user)
        if "SMRITI Store Manager" not in roles and "System Manager" not in roles:
            frappe.throw(
                _("Access Denied: Only SMRITI Store Managers or System Managers can submit Quotations or Sales Orders."),
                frappe.PermissionError
            )

    @staticmethod
    def check_stock_availability(item_code, qty, warehouse):
        """
        Reads live actual_qty from tabBin for validation.
        """
        if not warehouse:
            return True # If no warehouse specified, skip stock validation (e.g. drop ship or service)

        actual_qty = frappe.db.get_value("Bin", {"item_code": item_code, "warehouse": warehouse}, "actual_qty")
        actual_qty = flt(actual_qty or 0.0)
        
        if actual_qty < flt(qty):
            return {
                "available": False,
                "actual_qty": actual_qty,
                "message": _("Item {0} has insufficient stock in warehouse {1}. Requested: {2}, Available: {3}").format(
                    item_code, warehouse, qty, actual_qty
                )
            }
        return {"available": True, "actual_qty": actual_qty}

    @staticmethod
    def validate_sales_order_stock(so_doc):
        """
        Validates all items in the Sales Order against live stock availability.
        Throws a validation error if insufficient stock.
        """
        for item in so_doc.items:
            res = SalesValidationService.check_stock_availability(item.item_code, item.qty, item.warehouse)
            if isinstance(res, dict) and not res["available"]:
                frappe.throw(res["message"], SalesValidationError)
