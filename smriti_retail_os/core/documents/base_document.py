# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/documents/base_document.py
# @desc:    SmritiDocument — base document wrapper class.
#           Services work with SmritiDocument, which wraps a frappe.Document
#           and exposes a clean, SMRITI-vocabulary API.
#
#           The underlying frappe.Document is accessible via .raw if needed,
#           but should only be used within core/platform/ for persistence calls.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

from smriti_retail_os.core.platform import documents as _doc_adapter
from smriti_retail_os.core.platform.registry import resolve


class SmritiDocument:
    """
    SMRITI Document wrapper.

    Wraps a frappe.Document and exposes a platform-agnostic API
    using SMRITI vocabulary. Services should create and use SmritiDocument
    instances instead of accessing frappe.Document directly.

    Usage:
        from smriti_retail_os.core.documents import SmritiDocument

        # Load an existing document
        cust = SmritiDocument.load("Customer", "CUST-001")
        print(cust.get("customer_name"))

        # Create a new document
        po = SmritiDocument.create("Purchase")
        po.set("supplier", "SUP-001")
        po.save()

    Attributes:
        model_name (str): SMRITI model name (e.g. "Customer")
        raw: The underlying frappe.Document (use sparingly)
    """

    def __init__(self, model_name: str, raw_doc):
        self.model_name = model_name
        self.raw = raw_doc

    # ── Factory methods ────────────────────────────────────────────────────────

    @classmethod
    def load(cls, model_name: str, name: str) -> "SmritiDocument":
        """Load an existing document from the database."""
        raw = _doc_adapter.get(model_name, name)
        return cls(model_name, raw)

    @classmethod
    def create(cls, model_name: str) -> "SmritiDocument":
        """Create a new, unsaved document."""
        raw = _doc_adapter.new(model_name)
        return cls(model_name, raw)

    # ── Field accessors ────────────────────────────────────────────────────────

    def get(self, fieldname: str, default=None):
        """Get the value of a field."""
        return getattr(self.raw, fieldname, default)

    def set(self, fieldname: str, value):
        """Set the value of a field."""
        setattr(self.raw, fieldname, value)
        return self

    def update(self, data: dict) -> "SmritiDocument":
        """Set multiple fields from a dict."""
        for k, v in data.items():
            self.set(k, v)
        return self

    @property
    def name(self) -> str:
        """Document name / ID."""
        return self.raw.name

    @property
    def doctype(self) -> str:
        """Underlying platform DocType name (use only in platform adapter code)."""
        return resolve(self.model_name)

    @property
    def is_new(self) -> bool:
        """True if this document has not been saved yet."""
        return self.raw.is_new()

    # ── Lifecycle methods ──────────────────────────────────────────────────────

    def save(self) -> "SmritiDocument":
        """Save the document (insert if new, update if existing)."""
        _doc_adapter.save(self.raw)
        return self

    def insert(self) -> "SmritiDocument":
        """Insert a new document explicitly."""
        _doc_adapter.insert(self.raw)
        return self

    def submit(self) -> "SmritiDocument":
        """Submit the document."""
        _doc_adapter.submit(self.raw)
        return self

    def cancel(self) -> "SmritiDocument":
        """Cancel a submitted document."""
        _doc_adapter.cancel(self.raw)
        return self

    def reload(self) -> "SmritiDocument":
        """Reload from database, discarding unsaved changes."""
        _doc_adapter.reload(self.raw)
        return self

    def delete(self):
        """Delete this document."""
        _doc_adapter.delete(self.model_name, self.name)

    # ── Representation ─────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return the document as a plain Python dict."""
        return self.raw.as_dict()

    def __repr__(self) -> str:
        return f"<SmritiDocument model={self.model_name!r} name={self.name!r}>"
