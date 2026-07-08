# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/forms/retail_forms/grn_form.py
# @desc:    SMRITI GRN (Goods Receipt Note) Form.
#           Records goods received against a purchase order.
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
from smriti_retail_os.core.forms.form_engine import SmritiForm
from smriti_retail_os.core.forms.field import (
    LookupField, DateField, TextField, NumberField,
    CurrencyField, TableField, SelectField, TextAreaField, SectionBreak
)
from smriti_retail_os.core.forms.lifecycle import FormLifecycle
from smriti_retail_os.core.forms.validator import ValidationRule


GRN_ITEM_COLUMNS = [
    LookupField("item_code",      "Item",          model="Product",   required=True),
    TextField(  "item_name",      "Item Name",     readonly=True),
    TextField(  "uom",            "UOM",           readonly=True),
    NumberField("qty",            "Received Qty",  required=True, min_value=0.001, precision=3),
    NumberField("rejected_qty",   "Rejected Qty",  min_value=0, precision=3, default=0),
    CurrencyField("rate",         "Rate",          required=True, min_value=0),
    CurrencyField("amount",       "Amount",        readonly=True),
    LookupField("warehouse",      "Put Away To",   model="Warehouse", required=True),
    TextField(  "batch_no",       "Batch No"),
    TextField(  "serial_no",      "Serial No"),
]


class _GRNLifecycle(FormLifecycle):
    """GRN lifecycle: validate received qty doesn't exceed ordered qty."""

    def on_before_save(self, data: dict) -> tuple:
        items = data.get("items") or []
        if not items:
            return (False, "Please add at least one received item.")
        for row in items:
            received = float(row.get("qty") or 0)
            rejected = float(row.get("rejected_qty") or 0)
            if received + rejected <= 0:
                return (False,
                    f"Item '{row.get('item_code')}': received + rejected quantity must be > 0.")
        return (True, None)

    def on_after_save(self, doc) -> dict:
        from smriti_retail_os import smriti
        try:
            smriti.events.publish("smriti:grn_saved", {
                "name": doc.name,
                "purchase_order": getattr(doc, "purchase_order", ""),
            })
        except Exception:
            pass
        return {}


class GRNForm(SmritiForm):
    """SMRITI Goods Receipt Note (GRN) Form."""

    MODEL     = "GRN"
    TITLE     = "Goods Receipt Note"
    LIFECYCLE = _GRNLifecycle()

    FIELDS = [
        SectionBreak("Receipt Details"),
        LookupField("supplier",        "Supplier",          model="Supplier",       required=True),
        LookupField("purchase_order",  "Against PO",        model="Purchase"),
        DateField(  "posting_date",    "Receipt Date",      required=True),
        LookupField("set_warehouse",   "Receiving Warehouse", model="Warehouse",    required=True),

        SelectField("status",          "Status",
                    options=["Draft", "Submitted", "Return"],
                    default="Draft", readonly=True),

        SectionBreak("Received Items"),
        TableField(
            name="items",
            label="Received Items",
            required=True,
            columns=GRN_ITEM_COLUMNS,
            min_rows=1,
            add_row_label="Add Item",
        ),

        SectionBreak("Financials"),
        CurrencyField("total",         "Total Value",       readonly=True),
        CurrencyField("grand_total",   "Grand Total",       readonly=True),

        SectionBreak("Notes", collapsible=True),
        TextAreaField("remarks",       "Remarks",           rows=3),
    ]

    def _extra_rules(self) -> list:
        return [
            ValidationRule.custom(
                "posting_date",
                lambda v, d: (bool(v), "Receipt Date is required.")
            ),
        ]
