# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/forms/form_engine.py
# @desc:    SMRITI Form Engine — SmritiForm core class.
#           The central object that ties together fields, validator, lifecycle,
#           and the platform adapter. Business code defines forms by subclassing
#           SmritiForm and declaring fields declaratively.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
# Usage:
#   from smriti_retail_os.core.forms import SmritiForm, SmritiField
#   from smriti_retail_os.core.forms.field import LookupField, CurrencyField, TableField
#
#   class PurchaseForm(SmritiForm):
#       MODEL  = "Purchase"
#       TITLE  = "Purchase Order"
#       FIELDS = [
#           LookupField("supplier", "Supplier", model="Supplier", required=True),
#           CurrencyField("grand_total", "Grand Total", readonly=True),
#       ]
#
#   form   = PurchaseForm()
#   schema = form.schema()             # → dict for JS renderer
#   result = form.validate(data)       # → ValidationResult
#   doc    = form.save(data)           # → saved document dict
#

from __future__ import annotations
from typing import Any, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from smriti_retail_os.core.forms.field import SmritiField
    from smriti_retail_os.core.forms.lifecycle import FormLifecycle
    from smriti_retail_os.core.forms.validator import ValidationResult


class SmritiForm:
    """
    SMRITI Form Engine — Base form class.

    Subclass this to define a SMRITI form. Declare your fields in FIELDS,
    override lifecycle methods as needed, and the engine handles the rest.

    Class Attributes:
        MODEL (str):   SMRITI model name this form manages (e.g. "Purchase")
        TITLE (str):   User-facing form title (e.g. "Purchase Order")
        FIELDS (list): Ordered list of SmritiField / SectionBreak definitions
        LIFECYCLE (FormLifecycle | None): Optional lifecycle hook class instance

    Instance Methods:
        schema()         → dict    — serializable form definition for JS renderer
        validate(data)   → ValidationResult
        load(name)       → dict    — document data + lifecycle enrichments
        save(data)       → dict    — validated save, returns saved document dict
        submit(data)     → dict    — validated submit, returns submitted document dict

    Example (minimal form):
        class SupplierForm(SmritiForm):
            MODEL  = "Supplier"
            TITLE  = "Supplier"
            FIELDS = [
                TextField("supplier_name", "Supplier Name", required=True),
                TextField("mobile_no", "Mobile Number"),
                LookupField("supplier_group", "Group", model="SupplierGroup"),
            ]
    """

    MODEL: str = ""
    TITLE: str = ""
    FIELDS: List["SmritiField"] = []
    LIFECYCLE: Optional["FormLifecycle"] = None

    # ── Schema ─────────────────────────────────────────────────────────────────

    def schema(self) -> Dict[str, Any]:
        """
        Return a serializable form definition.

        The schema is consumed by the JS Form Renderer (Phase D) to build
        the UI without any server round-trip for structure. It is also used
        by automated tests to inspect form shape without rendering.

        Returns:
            dict with keys: model, title, fields (list of field dicts)
        """
        return {
            "model":  self.MODEL,
            "title":  self.TITLE,
            "fields": [f.to_dict() for f in self.FIELDS if hasattr(f, "to_dict")],
        }

    # ── Validation ─────────────────────────────────────────────────────────────

    def validate(self, data: dict) -> "ValidationResult":
        """
        Validate form data against field definitions and any custom rules.

        Automatically runs:
        1. Field-level checks (required, type constraints, min/max)
        2. Custom rules registered via self._extra_rules()
        3. Lifecycle.on_before_save() gate

        Returns:
            ValidationResult — never raises; callers inspect result.ok
        """
        from smriti_retail_os.core.forms.validator import FormValidator
        validator = FormValidator()

        # Subclasses may add extra rules via this method
        for rule in self._extra_rules():
            validator.add_rule(rule)

        result = validator.validate(self.FIELDS, data)

        # Run lifecycle before-save gate (returns (bool, str|None))
        if result.ok and self.LIFECYCLE:
            can_save, error_msg = self.LIFECYCLE.on_before_save(data)
            if not can_save:
                result.add_global_error(error_msg or "Validation failed.")

        return result

    def _extra_rules(self) -> list:
        """
        Override in subclasses to add ValidationRule objects.
        Called automatically by validate().

        Example:
            def _extra_rules(self):
                from smriti_retail_os.core.forms.validator import ValidationRule
                return [
                    ValidationRule.custom("grand_total",
                        lambda v, d: (float(v or 0) > 0, "Total must be positive."))
                ]
        """
        return []

    # ── Load ───────────────────────────────────────────────────────────────────

    def load(self, name: str) -> Dict[str, Any]:
        """
        Load an existing document and apply lifecycle enrichments.

        Args:
            name (str): Document name / ID

        Returns:
            dict: Document data merged with lifecycle on_load() overrides
        """
        from smriti_retail_os.core.platform import documents as _docs
        doc = _docs.get(self.MODEL, name)
        data = doc.as_dict()

        if self.LIFECYCLE:
            enrichments = self.LIFECYCLE.on_load(name)
            if enrichments:
                data.update(enrichments)

        return data

    # ── Save ───────────────────────────────────────────────────────────────────

    def save(self, data: dict) -> Dict[str, Any]:
        """
        Validate and save a document.

        Flow:
            1. validate(data) — raises if invalid
            2. documents.get or documents.new
            3. doc.update(data)
            4. doc.save()
            5. lifecycle.on_after_save(doc)

        Args:
            data (dict): Form data to save (must pass validate())

        Returns:
            dict: Saved document data

        Raises:
            frappe.ValidationError (via smriti.errors) if validation fails
        """
        from smriti_retail_os.core.platform import documents as _docs, errors

        result = self.validate(data)
        if not result.ok:
            first_error = (
                next(iter(result.errors.values()), ["Validation failed."])[0]
                if result.errors else (result.global_errors or ["Validation failed."])[0]
            )
            errors.raise_validation("Form Validation Failed", first_error)

        name = data.get("name")
        from smriti_retail_os.core.platform import db as _db
        if name and _db.exists(self.MODEL, name):
            doc = _docs.get(self.MODEL, name)
            doc.update(data)
        else:
            doc = _docs.new(self.MODEL)
            doc.update(data)

        doc.save(ignore_permissions=False)
        saved_data = doc.as_dict()

        if self.LIFECYCLE:
            enrichments = self.LIFECYCLE.on_after_save(doc)
            if enrichments:
                saved_data.update(enrichments)

        return saved_data

    # ── Submit ─────────────────────────────────────────────────────────────────

    def submit(self, data: dict) -> Dict[str, Any]:
        """
        Validate and submit (post) a document.

        Flow:
            1. validate(data)
            2. lifecycle.on_before_submit(data) gate
            3. documents.submit(doc)
            4. lifecycle.on_after_submit(doc)

        Args:
            data (dict): Form data or {"name": "DOC-001"} for existing document

        Returns:
            dict: Submitted document data
        """
        from smriti_retail_os.core.platform import documents as _docs, errors

        # Lifecycle pre-submit gate
        if self.LIFECYCLE:
            can_submit, msg = self.LIFECYCLE.on_before_submit(data)
            if not can_submit:
                errors.raise_validation("Cannot Submit", msg or "Submit conditions not met.")

        name = data.get("name")
        doc = _docs.get(self.MODEL, name)
        _docs.submit(doc)
        submitted_data = doc.as_dict()

        if self.LIFECYCLE:
            self.LIFECYCLE.on_after_submit(doc)

        return submitted_data

    # ── Repr ───────────────────────────────────────────────────────────────────

    def __repr__(self) -> str:
        return f"<SmritiForm model={self.MODEL!r} title={self.TITLE!r} fields={len(self.FIELDS)}>"
