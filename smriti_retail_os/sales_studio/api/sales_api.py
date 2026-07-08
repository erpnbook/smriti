# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/sales_studio/api/sales_api.py
# @desc:    Whitelisted API endpoints for SMRITI Sales Studio.
# @author:  Jawahar R. Mallah
#

import frappe
from smriti_retail_os.sales_studio.service.sales_service import SalesService
from smriti_retail_os.sales_studio.service.sales_workflow_service import SalesWorkflowService

@frappe.whitelist()
def get_open_quotations(customer=None, status=None, limit=50):
    return SalesService.list_quotations(customer=customer, status=status, limit=frappe.utils.cint(limit))

@frappe.whitelist()
def get_open_sales_orders(customer=None, status=None, limit=50):
    return SalesService.list_sales_orders(customer=customer, status=status, limit=frappe.utils.cint(limit))

@frappe.whitelist()
def get_quotation_details(quotation_name):
    return SalesService.get_quotation_detail(quotation_name)

@frappe.whitelist()
def get_sales_order_details(so_name):
    return SalesService.get_sales_order_detail(so_name)

@frappe.whitelist()
def create_quotation(customer, items, valid_till=None, remarks=None):
    items_list = frappe.parse_json(items) if isinstance(items, str) else items
    return SalesService.create_quotation(
        customer=customer,
        items_list=items_list,
        valid_till=valid_till,
        remarks=remarks
    )

@frappe.whitelist()
def create_sales_order(customer, items, delivery_date=None, remarks=None):
    items_list = frappe.parse_json(items) if isinstance(items, str) else items
    return SalesService.create_sales_order(
        customer=customer,
        items_list=items_list,
        delivery_date=delivery_date,
        remarks=remarks
    )

@frappe.whitelist()
def convert_quotation_to_sales_order(quotation_name):
    so_doc = SalesWorkflowService.make_sales_order_from_quotation(quotation_name)
    return {
        "name": so_doc.name,
        "message": frappe._("Sales Order {0} created from Quotation {1}.").format(so_doc.name, quotation_name)
    }

@frappe.whitelist()
def get_matrix_session(article, matrix_name=None):
    from smriti_retail_os.matrix_engine.service.matrix_service import MatrixService
    return MatrixService.build_session(article, matrix_name).to_dict()

@frappe.whitelist()
def resolve_or_create_variant(article, attribute_values):
    from smriti_retail_os.item_studio.service.variant_lifecycle_service import VariantLifecycleService
    import json
    if isinstance(attribute_values, str):
        attribute_values = json.loads(attribute_values)
    
    variant_code = VariantLifecycleService.resolve_or_create_variant(article, attribute_values)
    
    from smriti_retail_os.barcode.item_service import get_item_print_details
    details = get_item_print_details(variant_code, 1)
    
    return {
        "item_code": variant_code,
        "item_name": details.get("item_name"),
        "barcode": details.get("barcode"),
        "rate": details.get("mrp") or 0.0,
        "uom": details.get("uom") or "Nos"
    }

@frappe.whitelist()
def resolve_variant_item(article, color, size):
    return SalesService.resolve_variant_item(article, color, size)

@frappe.whitelist()
def get_size_presets():
    from smriti_retail_os.purchase_studio.service.purchase_service import get_size_presets as _get_presets
    return _get_presets()
