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
            requested_fields = [
                "name", "item_name", "brand", "item_group", "custom_mrp",
                "valuation_rate", "custom_gst_percentage", "stock_uom",
                "custom_style_code", "variant_of", "custom_sub_category",
                "custom_gender", "custom_purchase_class",
                "custom_department", "custom_heels", "custom_upper_material",
                "custom_outsole", "gst_hsn_code"
            ]
            try:
                raw_cols = frappe.db.sql("DESCRIBE `tabItem`", as_dict=True)
                db_cols = {r.get("Field") for r in raw_cols if r.get("Field")}
            except Exception:
                db_cols = set()

            if db_cols:
                fields = [f for f in requested_fields if f in db_cols or f == "name"]
            else:
                fields = ["name", "item_name", "brand", "item_group", "custom_mrp", "valuation_rate", "stock_uom"]

        items = smriti.db.get_list(
            "Item",
            filters=filters,
            fields=fields,
            order_by=order_by,
            limit=int(limit)
        )

        if items:
            item_names = [i.get("name") if hasattr(i, "get") else getattr(i, "name", None) for i in items]
            item_names = [name for name in item_names if name]

            barcode_map = {}
            has_barcode_table = False
            try:
                has_barcode_table = bool(frappe.db.table_exists("Item Barcode") or frappe.db.table_exists("tabItem Barcode"))
            except Exception:
                has_barcode_table = False

            if item_names and has_barcode_table:
                try:
                    barcodes = smriti.db.get_list(
                        "Item Barcode",
                        filters={"parent": ["in", item_names]},
                        fields=["parent", "barcode", "custom_is_primary"]
                    )
                    for b in barcodes:
                        parent = b.get("parent") if hasattr(b, "get") else getattr(b, "parent", None)
                        if not parent:
                            continue
                        if parent not in barcode_map:
                            barcode_map[parent] = []
                        barcode_map[parent].append(b)
                except Exception:
                    pass

            # Assign primary (or first available) barcode to each item
            for i in items:
                item_name = i.get("name") if hasattr(i, "get") else getattr(i, "name", None)
                if not item_name:
                    continue
                item_barcodes = barcode_map.get(item_name) or []
                primary = [
                    (b.get("barcode") if hasattr(b, "get") else getattr(b, "barcode", None))
                    for b in item_barcodes
                    if (hasattr(b, "get") and b.get("custom_is_primary")) or getattr(b, "custom_is_primary", False)
                ]
                primary = [p for p in primary if p]
                if primary:
                    i["barcode"] = primary[0]
                elif item_barcodes:
                    first_b = item_barcodes[0]
                    first_bc = first_b.get("barcode") if hasattr(first_b, "get") else getattr(first_b, "barcode", None)
                    i["barcode"] = first_bc or ""
                else:
                    i["barcode"] = ""

        return items

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
            "variant_of": doc.variant_of or "",
            "hsn_code": doc.get("gst_hsn_code") or ""
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

        if "hsn_code" in item_data and item_data["hsn_code"]:
            hsn = str(item_data["hsn_code"]).strip()
            if not smriti.db.exists("GST HSN Code", hsn):
                hsn_doc = smriti.documents.new("GST HSN Code")
                hsn_doc.name = hsn
                hsn_doc.hsn_code = hsn
                hsn_doc.description = "Auto-created HSN"
                hsn_doc.insert(ignore_permissions=True)
            doc.gst_hsn_code = hsn

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
    def bulk_delete(item_codes):
        """Disables/Soft-deletes multiple items in batch."""
        if not item_codes:
            return 0
        valid_codes = [c for c in item_codes if c and smriti.db.exists("Item", c)]
        if not valid_codes:
            return 0
        for code in valid_codes:
            smriti.db.set_value("Item", code, "disabled", 1)
        smriti.db.commit()
        return len(valid_codes)

    @staticmethod
    def set_price(item_code, price_list, rate):
        """Helper to create/update Item Price records."""
        if not smriti.db.exists("Price List", price_list):
            pl = smriti.documents.new("Price List")
            pl.price_list_name = price_list
            pl.selling = 1 if "Selling" in price_list else 0
            pl.buying = 1 if "Buying" in price_list else 0
            pl.currency = "INR"
            pl.insert(ignore_permissions=True)
            smriti.db.commit()

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
        return smriti.documents.get(*args, **kwargs)  # smriti-adapter-boundary

