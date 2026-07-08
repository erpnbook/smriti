# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/forms/retail_forms/product_form.py
# @desc:    SMRITI Product (Item Master) Form.
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
from smriti_retail_os.core.forms.form_engine import SmritiForm
from smriti_retail_os.core.forms.field import (
    TextField, SelectField, LookupField, NumberField,
    CurrencyField, CheckboxField, BarcodeField,
    ImageField, TextAreaField, SectionBreak
)


class ProductForm(SmritiForm):
    """SMRITI Product (Item Master) Form."""

    MODEL = "Product"
    TITLE = "Product"

    FIELDS = [
        SectionBreak("Product Details"),
        TextField(  "item_name",       "Product Name",  required=True, max_length=140),
        TextField(  "item_code",       "SKU / Item Code", max_length=140),
        LookupField("item_group",      "Category",      model="ProductGroup", required=True),
        LookupField("brand",           "Brand",         model="Brand"),
        TextField(  "stock_uom",       "Base UOM",      required=True, default="Nos"),
        BarcodeField("barcodes",       "Barcode",       format="any"),
        ImageField( "image",           "Product Image"),

        SectionBreak("Pricing"),
        CurrencyField("standard_rate", "Selling Price", required=True, min_value=0),
        CurrencyField("valuation_rate","Cost Price",    min_value=0),
        CurrencyField("last_purchase_rate", "Last Purchase Price", readonly=True),

        SectionBreak("Stock Settings"),
        CheckboxField("is_stock_item",  "Tracked in Stock", default=True),
        CheckboxField("has_batch_no",   "Batch Tracking"),
        CheckboxField("has_serial_no",  "Serial Number Tracking"),
        NumberField(  "safety_stock",   "Safety Stock Level", min_value=0, precision=3),
        NumberField(  "reorder_level",  "Reorder Level",      min_value=0, precision=3),

        SectionBreak("Notes", collapsible=True),
        TextAreaField("description",   "Product Description", rows=4),
    ]
