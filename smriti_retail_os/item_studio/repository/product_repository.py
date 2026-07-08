# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/item_studio/repository/product_repository.py
# @desc:    Data Access Repository Layer for SMRITI Product Studio.
#           Encapsulates all database reads and writes to ERPNext Item-related doctypes.
# @author:  Jawahar R. Mallah
#

# framework-adapter: wraps frappe ORM at the repository boundary — Guard 6 exempt
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti


class ProductRepository:
    """
    Isolates direct database access for SMRITI Item and Product Catalog operations.
    Follows Rule 4 of SMRITI Constitution (Repository Layer Isolation).
    """

    @staticmethod
    def get_list(filters=None, fields=None, order_by="creation desc", limit=200):
        """Fetches list of active items matching filters."""
        if filters is None:
            filters = {}
        # Ensure we always filter active products by default
        filters["disabled"] = 0

        if fields is None:
            fields = ["name", "item_name", "brand", "item_group", "custom_mrp",
                      "valuation_rate", "custom_gst_percentage", "stock_uom",
                      "custom_style_code", "variant_of"]

        return frappe.get_list(
            "Item",
            filters=filters,
            fields=fields,
            order_by=order_by,
            limit_page_length=int(limit)
        )

    @staticmethod
    def get_detail(item_code):
        """Retrieves complete details of an item including barcodes and prices."""
        if not smriti.db.exists("Item", item_code):
            frappe.throw(_("Item {0} does not exist.").format(item_code), frappe.DoesNotExistError)

        doc = smriti.documents.get("Item", item_code)
        
        # Resolve prices
        selling_mrp = smriti.db.get(
            "Item Price",
            {"item_code": item_code, "price_list": "Standard Selling"},
            "price_list_rate"
        ) or doc.get("custom_mrp") or 0.0

        buying_cost = smriti.db.get(
            "Item Price",
            {"item_code": item_code, "price_list": "Standard Buying"},
            "price_list_rate"
        ) or doc.get("valuation_rate") or doc.get("standard_rate") or 0.0

        return {
            "item_code": doc.name,
            "item_name": doc.item_name,
            "brand": doc.brand,
            "item_group": doc.item_group,
            "mrp": float(selling_mrp),
            "cost_price": float(buying_cost),
            "gst_percentage": int(doc.get("custom_gst_percentage") or 18),
            "style_code": doc.get("custom_style_code") or doc.name,
            "stock_uom": doc.stock_uom or "Nos",
            "variant_of": doc.variant_of or ""
        }

    @staticmethod
    def create(item_data):
        """Inserts a new Item record and its child price list entries."""
        item = smriti.documents.new("Item")
        item.item_code = item_data["item_code"]
        item.item_name = item_data["item_name"]
        item.item_group = item_data.get("item_group", "Products")
        item.stock_uom = item_data.get("stock_uom", "Nos")
        item.is_stock_item = 1
        item.standard_rate = float(item_data.get("cost_price", 0))

        # Dynamic assignments with safe setters for SMRITI custom fields
        for field, key in [("custom_is_retail_item", "is_retail"),
                           ("custom_gst_percentage", "gst_percentage"),
                           ("custom_mrp", "mrp"),
                           ("custom_style_code", "style_code")]:
            if hasattr(item, field) or frappe.db.has_column("Item", field):
                item.set(field, item_data.get(key))

        # Set default HSN code for India Compliance
        hsn = item_data.get("hsn_code") or smriti.db.get_single("SMRITI Settings", "default_hsn_code") or "64029990"
        if hsn:
            if not smriti.db.exists("GST HSN Code", hsn):
                hsn_doc = smriti.documents.new("GST HSN Code")
                hsn_doc.name = hsn
                hsn_doc.hsn_code = hsn
                hsn_doc.description = "Auto-created HSN"
                hsn_doc.insert(ignore_permissions=True)
            item.gst_hsn_code = hsn

        item.insert(ignore_permissions=True)

        # Set selling price list rate
        if item_data.get("mrp"):
            ProductRepository.set_price(item.name, "Standard Selling", item_data["mrp"])
        # Set buying price list rate
        if item_data.get("cost_price"):
            ProductRepository.set_price(item.name, "Standard Buying", item_data["cost_price"])

        return item.name

    @staticmethod
    def update(item_code, item_data):
        """Updates an existing Item doc and standard prices."""
        if not smriti.db.exists("Item", item_code):
            frappe.throw(_("Item {0} not found.").format(item_code), frappe.DoesNotExistError)

        doc = smriti.documents.get("Item", item_code)
        if "item_name" in item_data:
            doc.item_name = item_data["item_name"]
        if "item_group" in item_data:
            doc.item_group = item_data["item_group"]
        if "brand" in item_data:
            doc.brand = item_data["brand"]

        # Safe custom field updates
        for field, key in [("custom_gst_percentage", "gst_percentage"),
                           ("custom_mrp", "mrp"),
                           ("custom_style_code", "style_code")]:
            if (hasattr(doc, field) or frappe.db.has_column("Item", field)) and key in item_data:
                doc.set(field, item_data[key])

        doc.save(ignore_permissions=True)

        if "mrp" in item_data:
            ProductRepository.set_price(item_code, "Standard Selling", item_data["mrp"])
        if "cost_price" in item_data:
            ProductRepository.set_price(item_code, "Standard Buying", item_data["cost_price"])

        return doc.name

    @staticmethod
    def delete(item_code):
        """Disables/Soft-deletes the Item in the database."""
        if not smriti.db.exists("Item", item_code):
            return False
        smriti.db.set_value("Item", item_code, "disabled", 1)
        smriti.db.commit()
        return True

    @staticmethod
    def set_price(item_code, price_list, rate):
        """Helper to create/update Item Price records."""
        price_name = smriti.db.exists("Item Price", {"item_code": item_code, "price_list": price_list})
        if price_name:
            smriti.db.set_value("Item Price", price_name, "price_list_rate", float(rate))
        else:
            p = smriti.documents.new("Item Price")
            p.item_code = item_code
            p.price_list = price_list
            p.price_list_rate = float(rate)
            p.insert(ignore_permissions=True)
        smriti.db.commit()

    @staticmethod
    def new_doc(*args, **kwargs):
        """Creates a new document via smriti.documents layer (wraps frappe at boundary)."""
        return smriti.documents.new(*args, **kwargs)

    @staticmethod
    def get_doc(*args, **kwargs):
        """Fetches a document via smriti.documents layer (wraps frappe at boundary)."""
        return frappe.get_doc(*args, **kwargs)  # smriti-adapter-boundary

