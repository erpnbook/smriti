# -*- coding: utf-8 -*-
# SMRITI Variant Lifecycle / Provisioning Service
import frappe
from frappe import _
from smriti_retail_os.barcode.service.barcode_service import BarcodeService

class VariantLifecycleService:
    @staticmethod
    def ensure_attribute_and_value(attribute, value):
        if not value:
            return
        # Ensure Attribute exists
        if not frappe.db.exists("Item Attribute", attribute):
            doc = frappe.new_doc("Item Attribute")
            doc.attribute_name = attribute
            doc.numeric = 0
            doc.insert(ignore_permissions=True)
            frappe.publish_realtime("smriti_item_attribute_created", {"attribute": attribute})
        
        # Ensure Attribute Value exists
        if not frappe.db.exists("Item Attribute Value", {"parent": attribute, "attribute_value": value}):
            attr_doc = frappe.get_doc("Item Attribute", attribute)
            abbr = value[:5].strip()
            abbrs = [d.abbr for d in attr_doc.item_attribute_values if d.abbr]
            if abbr in abbrs or not abbr:
                import random
                abbr = f"{abbr[:3]}{random.randint(10,99)}"
            
            attr_doc.append("item_attribute_values", {
                "attribute_value": value,
                "abbr": abbr
            })
            attr_doc.save(ignore_permissions=True)

    @staticmethod
    def create_article_template(article_code, item_name, item_group=None, brand=None, hsn_code=None, gst_percentage=18, attributes=None):
        """
        Creates an Article template (Item with has_variants=1)
        """
        if frappe.db.exists("Item", article_code):
            return article_code

        if not item_group or not frappe.db.exists("Item Group", item_group):
            item_group = frappe.db.get_single_value("SMRITI Settings", "default_item_group") or "Products"

        if brand and not frappe.db.exists("Brand", brand):
            b = frappe.new_doc("Brand")
            b.brand = brand
            b.insert(ignore_permissions=True)

        item = frappe.new_doc("Item")
        item.item_code = article_code
        item.item_name = item_name
        item.item_group = item_group
        item.stock_uom = "Nos"
        item.is_stock_item = 1
        item.has_variants = 1

        from smriti_retail_os.item_master_api import _safe_set, _resolve_hsn_code_cached, _ensure_hsn_code, _ensure_item_attribute, _attach_tax_template
        _safe_set(item, "custom_is_retail_item", 1)
        _safe_set(item, "custom_gst_percentage", gst_percentage)
        _safe_set(item, "custom_style_code", article_code)

        resolved_hsn = _resolve_hsn_code_cached(hsn_code)
        if resolved_hsn:
            _ensure_hsn_code(resolved_hsn)
            item.gst_hsn_code = resolved_hsn
            _safe_set(item, "gn_hsn_code", resolved_hsn)

        if not attributes:
            attributes = ["Color", "Size"]

        for attr in attributes:
            _ensure_item_attribute(attr)
            item.append("attributes", {"attribute": attr})

        company = frappe.defaults.get_user_default("company") or frappe.get_all("Company", limit=1)[0].name
        _attach_tax_template(item, None, gst_percentage, company)
        item.insert(ignore_permissions=True)
        
        frappe.publish_realtime("smriti_article_created", {"article": item.name, "item_name": item.item_name})
        return item.name

    @staticmethod
    def resolve_or_create_variant(article, attribute_values):
        """
        Resolves or creates a variant Item matching attribute values.
        """
        if not frappe.db.exists("Item", {"name": article, "has_variants": 1}):
            frappe.throw(_("Article {0} is not a valid variant template item.").format(article))

        for attr, val in attribute_values.items():
            VariantLifecycleService.ensure_attribute_and_value(attr, val)

        from erpnext.controllers.item_variant import get_variant, create_variant
        
        variant_code = get_variant(article, attribute_values)
        if variant_code:
            return variant_code

        variant_doc = create_variant(article, attribute_values)
        variant_doc.insert(ignore_permissions=True)

        barcode = BarcodeService.generate("EAN13")
        variant_doc.append("barcodes", {
            "barcode": barcode,
            "uom": variant_doc.stock_uom or "Nos",
            "custom_is_primary": 1
        })
        variant_doc.save(ignore_permissions=True)

        from smriti_retail_os.item_master_api import _upsert_item_price
        template_mrp = frappe.db.get_value("Item", article, "custom_mrp") or 0.0
        if template_mrp:
            _upsert_item_price(variant_doc.name, "Standard Selling", template_mrp)
            _upsert_item_price(variant_doc.name, "MRP", template_mrp)

        # Clear Matrix Redis Cache
        from smriti_retail_os.matrix_engine.service.matrix_service import MatrixService
        MatrixService.clear_cache(article)

        frappe.publish_realtime("smriti_variant_created", {
            "item_code": variant_doc.name,
            "article": article,
            "barcode": barcode,
            "attribute_values": attribute_values
        })
        return variant_doc.name
