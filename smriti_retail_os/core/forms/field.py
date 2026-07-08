# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/forms/field.py
# @desc:    SMRITI Form Engine — Field type definitions.
#           All retail form fields are defined using these classes.
#           The Form Engine uses field definitions to render, validate, and
#           serialize form data without touching the platform UI.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

from dataclasses import dataclass, field
from typing import Any, Callable, List, Optional


@dataclass
class SmritiField:
    """
    Base field definition for the SMRITI Form Engine.

    Every concrete field type subclasses this.
    Field definitions describe the field's metadata, constraints, and UI hints.
    They do NOT contain Frappe-specific rendering logic.

    Attributes:
        name (str):         Programmatic field name (matches document fieldname)
        label (str):        User-facing label
        required (bool):    Whether the field must have a non-empty value
        readonly (bool):    Whether the field is display-only
        hidden (bool):      Whether the field is hidden from the form
        default (Any):      Default value for new documents
        help_text (str):    User-facing hint text shown below the field
        depends_on (str):   Field name whose value controls visibility (optional)
    """
    name: str
    label: str
    required: bool = False
    readonly: bool = False
    hidden: bool = False
    default: Any = None
    help_text: str = ""
    depends_on: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "name":       self.name,
            "label":      self.label,
            "type":       self.__class__.__name__,
            "required":   self.required,
            "readonly":   self.readonly,
            "hidden":     self.hidden,
            "default":    self.default,
            "help_text":  self.help_text,
            "depends_on": self.depends_on,
        }


@dataclass
class TextField(SmritiField):
    """Single-line text input."""
    max_length: int = 255
    placeholder: str = ""

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"max_length": self.max_length, "placeholder": self.placeholder})
        return d


@dataclass
class TextAreaField(SmritiField):
    """Multi-line text input."""
    rows: int = 4
    max_length: int = 2000

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"rows": self.rows, "max_length": self.max_length})
        return d


@dataclass
class NumberField(SmritiField):
    """Integer or float number input."""
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    precision: int = 0          # decimal places; 0 = integer

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "min_value": self.min_value,
            "max_value": self.max_value,
            "precision": self.precision,
        })
        return d


@dataclass
class CurrencyField(SmritiField):
    """Currency amount — always 2 decimal places, uses site currency."""
    currency: str = "INR"
    min_value: float = 0.0

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"currency": self.currency, "min_value": self.min_value})
        return d


@dataclass
class DateField(SmritiField):
    """Date picker (no time)."""
    min_date: Optional[str] = None   # ISO format: "2026-01-01"
    max_date: Optional[str] = None

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"min_date": self.min_date, "max_date": self.max_date})
        return d


@dataclass
class DateTimeField(SmritiField):
    """Date + time picker."""
    pass


@dataclass
class SelectField(SmritiField):
    """Dropdown with a static list of options."""
    options: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"options": self.options})
        return d


@dataclass
class LookupField(SmritiField):
    """
    Linked field — points to another SMRITI model.
    The Form Engine resolves the SMRITI model name to its platform DocType
    via the registry; consumers never see the DocType name.

    Attributes:
        model (str):        SMRITI model name (e.g. "Supplier", "Warehouse")
        display_field (str): Field from the linked model to show as label
        filters (dict):     Static filters applied to the lookup query
    """
    model: str = ""
    display_field: str = "name"
    filters: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "model":         self.model,
            "display_field": self.display_field,
            "filters":       self.filters,
        })
        return d


@dataclass
class TableField(SmritiField):
    """
    Child table field (e.g. Purchase Order items).

    Attributes:
        columns (list):     List of SmritiField definitions for each column
        min_rows (int):     Minimum number of rows required
        add_row_label (str): Label for the "Add Row" button
    """
    columns: List[SmritiField] = field(default_factory=list)
    min_rows: int = 0
    add_row_label: str = "Add Item"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({
            "columns":       [col.to_dict() for col in self.columns],
            "min_rows":      self.min_rows,
            "add_row_label": self.add_row_label,
        })
        return d


@dataclass
class CheckboxField(SmritiField):
    """Boolean checkbox."""
    pass


@dataclass
class BarcodeField(SmritiField):
    """Barcode / QR scanner input."""
    format: str = "any"   # "any", "ean13", "qr", "code128"

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"format": self.format})
        return d


@dataclass
class ImageField(SmritiField):
    """Image upload field."""
    accept: str = "image/*"
    max_size_kb: int = 2048

    def to_dict(self) -> dict:
        d = super().to_dict()
        d.update({"accept": self.accept, "max_size_kb": self.max_size_kb})
        return d


@dataclass
class SectionBreak:
    """
    Visual section divider (not a data field).
    Groups related fields under a heading in the rendered form.
    """
    label: str
    collapsible: bool = False

    def to_dict(self) -> dict:
        return {
            "type":        "SectionBreak",
            "label":       self.label,
            "collapsible": self.collapsible,
        }
