# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/item_studio/service/product_service.py
# @desc:    Business Logic / Service Layer for SMRITI Product Studio.
#           Coordinates validation and interacts with ProductRepository.
# @author:  Jawahar R. Mallah
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti
from smriti_retail_os.item_studio.repository.product_repository import ProductRepository


class ProductService:
    """
    Implements business rules and validation logic for SMRITI Item Catalog.
    Coordinates between SMRITI services and the repository.
    """

    @staticmethod
    def get_products(filters=None, fields=None, order_by="creation desc", limit=200):
        """Fetches active catalog products using repository."""
        return ProductRepository.get_list(filters, fields, order_by, limit)

    @staticmethod
    def get_product_detail(item_code):
        """Gets complete product information by EAN/code."""
        return ProductRepository.get_detail(item_code)

    @staticmethod
    def save_product(item_data, item_code=None):
        """
        Validates product data and creates or updates a product.
        - Enforces validation: cost_price <= mrp
        - Enforces alphanumeric barcode/item_code format
        """
        # 1. Validation Checks
        if not item_code and not item_data.get("item_name"):
            frappe.throw(_("Product Name is required."))

        mrp = float(item_data.get("mrp") or 0)
        cost = float(item_data.get("cost_price") or 0)
        if cost > mrp:
            frappe.throw(_("Cost Price ({0}) cannot exceed MRP Price ({1}).").format(cost, mrp))

        # Barcode validation
        code = item_data.get("item_code")
        if not item_code:
            if not code:
                frappe.throw(_("Barcode / Item Code is required."))
            # Verify code is alphanumeric without spaces
            if not code.isalnum():
                frappe.throw(_("Barcode / Item Code must be alphanumeric with no spaces or special characters."))
            if smriti.db.exists("Item", code):
                frappe.throw(_("Product with Barcode {0} already exists.").format(code))
        else:
            code = item_code

        # Seeding defaults
        if not item_data.get("item_group"):
            item_data["item_group"] = smriti.db.get_single("SMRITI Settings", "default_item_group") or "Products"

        if not item_data.get("gst_percentage"):
            item_data["gst_percentage"] = "18"

        raw_hsn = item_data.get("hsn_code")
        if raw_hsn:
            import re
            hsn_digits = "".join(re.findall(r"\d+", str(raw_hsn)))
            if not hsn_digits or len(hsn_digits) < 4 or len(hsn_digits) > 8:
                frappe.throw(_("HSN Code '{0}' is invalid. HSN Code must contain between 4 and 8 numeric digits (e.g. 6402, 640299, 64029990).").format(raw_hsn))
            item_data["hsn_code"] = hsn_digits
        else:
            item_data["hsn_code"] = smriti.db.get_single("SMRITI Settings", "default_hsn_code") or "64029990"

        # 2. Invoke persistence layer
        if item_code:
            return ProductRepository.update(item_code, item_data)
        else:
            return ProductRepository.create(item_data)

    @staticmethod
    def delete_product(item_code):
        """Soft deletes product by disabling it in catalog."""
        return ProductRepository.delete(item_code)

    @staticmethod
    def bulk_delete_products(item_codes):
        """Batch disables selected or filtered items in catalog."""
        return ProductRepository.bulk_delete(item_codes)
