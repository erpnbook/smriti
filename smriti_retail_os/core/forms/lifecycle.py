# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/core/forms/lifecycle.py
# @desc:    SMRITI Form Engine — Form lifecycle hooks.
#           Defines the hook protocol that form definitions implement.
#           Lifecycle hooks connect form events (load, change, save, submit)
#           to business logic without platform-specific event wiring.
#
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

from typing import Any, Dict, Optional


class FormLifecycle:
    """
    SMRITI Form Lifecycle Hook Protocol.

    Subclass this in form definitions that need business logic at lifecycle
    events. All methods are optional — override only what you need.

    The Form Engine calls these hooks automatically via SmritiForm.

    Usage:
        class PurchaseLifecycle(FormLifecycle):
            def on_change(self, field_name, value, data):
                if field_name == "supplier":
                    return {"payment_terms": self._fetch_supplier_terms(value)}
                return {}

            def on_before_save(self, data):
                if not data.get("items"):
                    return (False, "Please add at least one item before saving.")
                return (True, None)

    Hook signatures:
        on_load(name)             -> dict  (initial data enrichments)
        on_change(field, val, data) -> dict  (dependent field updates)
        on_before_save(data)      -> (bool, error_msg|None)
        on_after_save(doc)        -> dict  (post-save enrichments)
        on_before_submit(data)    -> (bool, error_msg|None)
        on_after_submit(doc)      -> None
    """

    def on_load(self, name: str) -> Dict[str, Any]:
        """
        Called when an existing document is opened.
        Return a dict of field overrides / computed values to display.

        Args:
            name (str): Document name being loaded

        Returns:
            dict: {field_name: enriched_value}

        Example:
            def on_load(self, name):
                doc_data = smriti.documents.get("Purchase", name)
                return {
                    "supplier_display_name": _get_display_name(doc_data.get("supplier"))
                }
        """
        return {}

    def on_change(self, field_name: str, value: Any,
                  data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Called when a field value changes in the UI.
        Return a dict of dependent field updates.

        Args:
            field_name (str): Name of the field that changed
            value (Any):      New value
            data (dict):      Current full form data

        Returns:
            dict: {field_name: new_value} for any dependent fields to update

        Example:
            def on_change(self, field_name, value, data):
                if field_name == "supplier":
                    terms = smriti.db.get("Supplier", value, "payment_terms")
                    return {"payment_terms": terms}
                return {}
        """
        return {}

    def on_before_save(self, data: Dict[str, Any]) -> tuple:
        """
        Called before the form is saved. Acts as a final validation gate.

        Args:
            data (dict): Complete form data

        Returns:
            (bool, str|None): (is_valid, error_message_if_invalid)

        Example:
            def on_before_save(self, data):
                items = data.get("items") or []
                if not items:
                    return (False, "Please add at least one item to the order.")
                grand_total = sum(r.get("amount", 0) for r in items)
                if grand_total <= 0:
                    return (False, "Order total must be greater than zero.")
                return (True, None)
        """
        return (True, None)

    def on_after_save(self, doc) -> Dict[str, Any]:
        """
        Called after the document is successfully saved.
        Use for cache invalidation, event publishing, and post-save enrichments.

        Args:
            doc: The saved SmritiDocument (or raw frappe.Document within core/)

        Returns:
            dict: Any additional data to return to the caller / UI

        Example:
            def on_after_save(self, doc):
                smriti.cache.delete(f"smriti_purchase_{doc.name}")
                smriti.events.publish("smriti:purchase_saved", {"name": doc.name})
                return {"last_saved": datetime.now().isoformat()}
        """
        return {}

    def on_before_submit(self, data: Dict[str, Any]) -> tuple:
        """
        Called before the document is submitted (posted).
        Use for final business rule checks before the document is locked.

        Args:
            data (dict): Complete form data

        Returns:
            (bool, str|None): (can_submit, reason_if_not)

        Example:
            def on_before_submit(self, data):
                if data.get("approval_status") != "Approved":
                    return (False, "This purchase order must be approved before posting.")
                return (True, None)
        """
        return (True, None)

    def on_after_submit(self, doc) -> None:
        """
        Called after the document is successfully submitted.
        Use for notifications, downstream document creation, etc.

        Args:
            doc: The submitted SmritiDocument
        """
        pass
