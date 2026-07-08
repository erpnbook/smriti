# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/sales_studio/service/sales_workflow_service.py
# @desc:    Workflow service for SMRITI Sales Studio.
# @author:  Jawahar R. Mallah
#

import frappe
from frappe import _
from smriti_retail_os.sales_studio.repository.sales_repository import SalesRepository
from smriti_retail_os.sales_studio.service.sales_validation_service import SalesValidationService

class SalesWorkflowService:
    @staticmethod
    def submit_quotation(quotation_name):
        SalesValidationService.validate_store_manager_role()
        doc = SalesRepository.get_quotation(quotation_name)
        if doc.docstatus == 0:
            doc.docstatus = 1
            SalesRepository.save_quotation(doc)
        return doc

    @staticmethod
    def cancel_quotation(quotation_name):
        SalesValidationService.validate_store_manager_role()
        doc = SalesRepository.get_quotation(quotation_name)
        if doc.docstatus == 1:
            doc.docstatus = 2
            SalesRepository.save_quotation(doc)
        return doc

    @staticmethod
    def submit_sales_order(so_name):
        SalesValidationService.validate_store_manager_role()
        doc = SalesRepository.get_sales_order(so_name)
        if doc.docstatus == 0:
            # Validate live stock availability before submit
            SalesValidationService.validate_sales_order_stock(doc)
            doc.docstatus = 1
            SalesRepository.save_sales_order(doc)
        return doc

    @staticmethod
    def cancel_sales_order(so_name):
        SalesValidationService.validate_store_manager_role()
        doc = SalesRepository.get_sales_order(so_name)
        if doc.docstatus == 1:
            doc.docstatus = 2
            SalesRepository.save_sales_order(doc)
        return doc

    @staticmethod
    def make_sales_order_from_quotation(quotation_name):
        """
        Original clean mapping of Quotation to Sales Order.
        Converts a submitted Quotation (docstatus=1) to a draft Sales Order.
        """
        quotation = SalesRepository.get_quotation(quotation_name)
        if quotation.docstatus != 1:
            frappe.throw(_("Quotation {0} must be submitted before converting to Sales Order.").format(quotation_name))

        so = SalesRepository.new_doc("Sales Order")
        so.customer = quotation.customer
        so.company = quotation.company
        so.transaction_date = frappe.utils.nowdate()
        so.delivery_date = quotation.valid_till or frappe.utils.nowdate()
        so.remarks = quotation.remarks

        # Custom SMRITI fields mapping if any
        if hasattr(quotation, "custom_is_matrix_booked") and hasattr(so, "custom_is_matrix_booked"):
            so.custom_is_matrix_booked = quotation.custom_is_matrix_booked

        for item in quotation.items:
            so.append("items", {
                "item_code": item.item_code,
                "item_name": item.item_name,
                "qty": item.qty,
                "rate": item.rate,
                "uom": item.uom,
                "warehouse": item.warehouse,
                "delivery_date": so.delivery_date,
                "description": item.description
            })

        # Run tax calculations
        so.run_method("set_missing_values")
        so.run_method("calculate_taxes_and_totals")
        
        SalesRepository.insert_sales_order(so)
        return so
