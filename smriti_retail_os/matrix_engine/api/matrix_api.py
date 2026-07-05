# -*- coding: utf-8 -*-
# SMRITI Matrix Platform API Endpoints
import frappe
import json
from frappe import _
from smriti_retail_os.matrix_engine.service.matrix_service import MatrixService
from smriti_retail_os.item_studio.service.variant_lifecycle_service import VariantLifecycleService
from smriti_retail_os.barcode.service.barcode_service import BarcodeService

@frappe.whitelist()
def get_matrix_session(article, matrix_name=None):
    """
    Returns the dynamic matrix session metadata and cells for an article.
    """
    session = MatrixService.build_session(article, matrix_name)
    return session.to_dict()

@frappe.whitelist()
def resolve_or_create_variant(article, attribute_values):
    """
    Resolves or creates a variant on the fly and returns its details.
    """
    if isinstance(attribute_values, str):
        attribute_values = json.loads(attribute_values)
        
    variant_code = VariantLifecycleService.resolve_or_create_variant(article, attribute_values)
    
    # Load details
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
def create_article_template(article_code, item_name, item_group=None, brand=None, hsn_code=None, gst_percentage=18, attributes=None):
    """
    Creates an Article template Item.
    """
    if isinstance(attributes, str):
        attributes = json.loads(attributes)
        
    article = VariantLifecycleService.create_article_template(
        article_code=article_code,
        item_name=item_name,
        item_group=item_group,
        brand=brand,
        hsn_code=hsn_code,
        gst_percentage=frappe.utils.cint(gst_percentage or 18),
        attributes=attributes
    )
    return {
        "article": article,
        "item_name": item_name
    }

@frappe.whitelist()
def parse_pasted_grid(tsv_content):
    """
    Parses tab-separated clipboard TSV into matrix cell coordinates on the backend.
    """
    return MatrixService.parse_excel_grid(tsv_content)
