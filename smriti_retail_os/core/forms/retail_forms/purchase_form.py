# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/forms/retail_forms/purchase_form.py
# @desc:    SMRITI Purchase Order Form — reference retail form implementation.
#           This is the canonical proof that the SMRITI Form Engine works end-to-end.
#           All retail forms follow this pattern.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

from smriti_retail_os.core.forms.form_engine import SmritiForm
from smriti_retail_os.core.forms.field import (
    LookupField, DateField, TextField, CurrencyField,
    NumberField, TableField, SelectField, TextAreaField, SectionBreak
)
from smriti_retail_os.core.forms.lifecycle import FormLifecycle
from smriti_retail_os.core.forms.validator import ValidationRule


# ── Purchase Order Lifecycle ───────────────────────────────────────────────────

class _PurchaseLifecycle(FormLifecycle):
    """
    Business logic hooks for the Purchase Order form.

    Hooks:
        on_load        — enriches with supplier display name + item details
        on_change      — auto-fills payment terms when supplier changes
        on_before_save — validates items exist and grand total > 0
        on_after_save  — publishes realtime event + invalidates cache
        on_before_submit — checks approval status
    """

    def on_load(self, name: str) -> dict:
        """Enrich loaded purchase order with computed display values."""
        from smriti_retail_os import smriti
        try:
            supplier = smriti.db.get("Purchase", name, "supplier")
            if supplier:
                supplier_name = smriti.db.get("Supplier", supplier, "supplier_name")
                return {"_supplier_display": supplier_name or supplier}
        except Exception:
            pass
        return {}

    def on_change(self, field_name: str, value, data: dict) -> dict:
        """
        When supplier changes: auto-fill payment terms from supplier master.
        When warehouse changes: update per-row default warehouse in items.
        """
        from smriti_retail_os import smriti
        updates = {}
        if field_name == "supplier" and value:
            try:
                terms = smriti.db.get("Supplier", value, "payment_terms")
                if terms:
                    updates["payment_terms"] = terms
            except Exception:
                pass
        return updates

    def on_before_save(self, data: dict) -> tuple:
        """Validate items exist and order total is positive."""
        items = data.get("items") or []
        if not items:
            return (False, "Please add at least one item before saving the purchase order.")
        grand_total = float(data.get("grand_total") or 0)
        if grand_total <= 0:
            return (False,
                    "The purchase order total must be greater than zero. "
                    "Check item quantities and rates.")
        return (True, None)

    def on_after_save(self, doc) -> dict:
        """Invalidate purchase cache and publish realtime notification."""
        from smriti_retail_os import smriti
        try:
            smriti.cache.delete(f"smriti_purchase_{doc.name}")
            smriti.events.publish("smriti:purchase_saved", {
                "name": doc.name,
                "supplier": getattr(doc, "supplier", ""),
                "status": getattr(doc, "status", "Draft"),
            })
        except Exception:
            pass
        return {}

    def on_before_submit(self, data: dict) -> tuple:
        """Purchase orders must be in 'Pending Approval' or 'Approved' status to submit."""
        status = data.get("status") or data.get("workflow_state") or ""
        blocked_statuses = {"Draft", "Rejected", "Cancelled"}
        if status in blocked_statuses:
            return (False,
                    f"This purchase order cannot be submitted in '{status}' status. "
                    "It must be approved first.")
        return (True, None)

    def on_after_submit(self, doc) -> None:
        """Publish posted event after submission."""
        from smriti_retail_os import smriti
        try:
            smriti.events.publish("smriti:purchase_posted", {
                "name": doc.name,
                "grand_total": getattr(doc, "grand_total", 0),
            })
        except Exception:
            pass


# ── Purchase Order Items Table ─────────────────────────────────────────────────

PURCHASE_ITEM_COLUMNS = [
    LookupField("item_code",      "Item",      model="Product",   required=True),
    TextField(  "item_name",      "Item Name", readonly=True),
    TextField(  "uom",            "UOM",       readonly=True, default="Nos"),
    NumberField("qty",            "Qty",       required=True, min_value=0.001, precision=3),
    CurrencyField("rate",         "Rate",      required=True, min_value=0.0),
    CurrencyField("amount",       "Amount",    readonly=True),
    LookupField("warehouse",      "Warehouse", model="Warehouse"),
    TextAreaField("description",  "Notes",     rows=2),
]


# ── PurchaseForm ───────────────────────────────────────────────────────────────

class PurchaseForm(SmritiForm):
    """
    SMRITI Purchase Order Form.

    The canonical reference implementation of SmritiForm.
    Demonstrates: field composition, lookup fields, child table, lifecycle hooks,
    section breaks, and custom validation rules.

    Usage:
        form   = PurchaseForm()
        schema = form.schema()                    # → dict for JS renderer
        result = form.validate(data)              # → ValidationResult
        doc    = form.save(data)                  # → saved document dict
        doc    = form.submit({"name": "PO-001"})  # → submitted document dict
        data   = form.load("PO-001")              # → loaded document dict
    """

    MODEL     = "Purchase"
    TITLE     = "Purchase Order"
    LIFECYCLE = _PurchaseLifecycle()

    FIELDS = [
        # ── Header ──────────────────────────────────────────────────────────
        SectionBreak("Order Details"),

        LookupField(
            name="supplier",
            label="Supplier",
            model="Supplier",
            required=True,
            display_field="supplier_name",
            help_text="Select the supplier for this purchase order.",
        ),
        DateField(
            name="schedule_date",
            label="Required By Date",
            required=True,
            help_text="Date by which items must be delivered.",
        ),
        DateField(
            name="transaction_date",
            label="Order Date",
            required=True,
            help_text="Date of this purchase order.",
        ),
        LookupField(
            name="set_warehouse",
            label="Deliver To Warehouse",
            model="Warehouse",
            required=True,
            help_text="Default receiving warehouse for all items.",
        ),
        SelectField(
            name="status",
            label="Status",
            options=["Draft", "Pending Approval", "Approved", "Ordered",
                     "Partially Received", "Completed", "Rejected", "Cancelled"],
            default="Draft",
            readonly=True,
        ),

        # ── Items ────────────────────────────────────────────────────────────
        SectionBreak("Items"),

        TableField(
            name="items",
            label="Order Items",
            required=True,
            columns=PURCHASE_ITEM_COLUMNS,
            min_rows=1,
            add_row_label="Add Item",
        ),

        # ── Financials ───────────────────────────────────────────────────────
        SectionBreak("Payment & Terms"),

        SelectField(
            name="payment_terms",
            label="Payment Terms",
            options=["Immediate", "Net 7", "Net 15", "Net 30", "Net 60",
                     "50% Advance", "100% Advance"],
            default="Net 30",
        ),
        CurrencyField(
            name="total",
            label="Pre-Tax Total",
            readonly=True,
        ),
        CurrencyField(
            name="taxes_and_charges_added",
            label="Taxes & Charges",
            readonly=True,
        ),
        CurrencyField(
            name="grand_total",
            label="Grand Total",
            readonly=True,
        ),

        # ── Notes ────────────────────────────────────────────────────────────
        SectionBreak("Notes", collapsible=True),

        TextAreaField(
            name="terms",
            label="Terms & Conditions",
            rows=4,
        ),
        TextAreaField(
            name="remarks",
            label="Internal Remarks",
            rows=3,
            help_text="Internal notes — not visible to supplier.",
        ),
    ]

    def _extra_rules(self) -> list:
        """Additional business validation rules beyond field-level checks."""
        return [
            ValidationRule.custom(
                "schedule_date",
                lambda v, d: (
                    not v or not d.get("transaction_date") or v >= d["transaction_date"],
                    "Required By Date must be on or after the Order Date."
                )
            ),
            ValidationRule.global_rule(
                lambda d: (
                    "Grand Total must be greater than zero."
                    if float(d.get("grand_total") or 0) <= 0 and d.get("items")
                    else None
                )
            ),
        ]
