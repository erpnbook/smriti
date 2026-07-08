# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/services/base_service.py
# @desc:    BaseService — SMRITI service contract.
#           All SMRITI services must extend BaseService.
#           Provides: validation hooks, error handling, audit logging.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#
# Usage:
#   class CustomerService(BaseService):
#       MODEL = "Customer"
#
#       def get_customer(self, name: str):
#           self._require_permission("read")
#           return documents.get(self.MODEL, name)
#


from smriti_retail_os.core.platform import permissions, errors


class BaseService:
    """
    SMRITI Base Service Contract.

    All SMRITI services extend this class. It provides:
    - MODEL declaration (SMRITI model name this service manages)
    - Permission guard helpers
    - Standardised error raising (HREP-compliant)
    - Error logging utilities

    Example:
        class PurchaseService(BaseService):
            MODEL = "Purchase"

            def create_purchase_order(self, supplier: str, items: list):
                self._require_permission("create")
                self._validate_required({"supplier": supplier, "items": items})

                po = documents.new(self.MODEL)
                po.supplier = supplier
                po.items = items
                documents.save(po)
                return po
    """

    # Subclasses declare their primary SMRITI model name.
    MODEL: str = None

    # ── Permission guards ──────────────────────────────────────────────────────

    def _require_permission(self, ptype: str = "read", doc=None):
        """Raise PermissionError if current user lacks the given permission."""
        if not self.MODEL:
            return
        permissions.require(self.MODEL, ptype=ptype, doc=doc)

    def _require_read(self, doc=None):
        self._require_permission("read", doc)

    def _require_write(self, doc=None):
        self._require_permission("write", doc)

    def _require_create(self):
        self._require_permission("create")

    def _require_delete(self, doc=None):
        self._require_permission("delete", doc)

    # ── Validation helpers ─────────────────────────────────────────────────────

    def _validate_required(self, fields: dict):
        """
        Raise a HREP-compliant validation error if any required field is empty.

        Args:
            fields (dict): {field_label: value} — raises for any None/empty value

        Example:
            self._validate_required({
                "Supplier": supplier,
                "Purchase Date": purchase_date,
            })
        """
        missing = [label for label, val in fields.items() if not val]
        if missing:
            errors.raise_validation(
                "Required Fields Missing",
                f"The following fields are required: {', '.join(missing)}. "
                f"Please fill them in and try again."
            )

    # ── Error helpers ──────────────────────────────────────────────────────────

    def _raise_validation(self, title: str, message: str, error_code: str = None):
        errors.raise_validation(title, message, error_code)

    def _raise_business_error(self, title: str, message: str, error_code: str = None):
        errors.raise_business_error(title, message, error_code)

    def _raise_not_found(self, identifier: str):
        errors.raise_not_found(self.MODEL or "Record", identifier)

    def _log_error(self, title: str, exc: Exception = None, context: dict = None):
        errors.log_error(title, exc=exc, context=context)

    # ── Identity ───────────────────────────────────────────────────────────────

    def _current_user(self) -> str:
        return permissions.current_user()

    def _get_roles(self) -> list:
        return permissions.get_roles()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} model={self.MODEL!r}>"
