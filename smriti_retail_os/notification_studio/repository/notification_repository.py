# -*- coding: utf-8 -*-
"""
smriti_retail_os/notification_studio/repository/notification_repository.py
Repository layer for SMRITI Notification Studio database queries.
Author: Jawahar R. Mallah
"""
# framework-adapter: wraps frappe ORM at the repository boundary — Guard 6 exempt
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti

class NotificationRepository:
    @staticmethod
    def get_safety_stock_violations(limit=50) -> list[dict]:
        """Fetch items where actual stock level is below item-level safety stock."""
        return smriti.db.sql("""
            SELECT bin.item_code, bin.warehouse, bin.actual_qty, item.safety_stock as limit_qty
            FROM `tabBin` bin
            INNER JOIN `tabItem` item ON bin.item_code = item.name
            WHERE item.safety_stock > 0 AND bin.actual_qty < item.safety_stock
            LIMIT %s
        """, (int(limit),), as_dict=1)

    @staticmethod
    def get_reorder_level_violations(limit=50) -> list[dict]:
        """Fetch items where actual stock level is below warehouse-level reorder limit."""
        return smriti.db.sql("""
            SELECT bin.item_code, bin.warehouse, bin.actual_qty, ir.warehouse_reorder_level as limit_qty
            FROM `tabItem Reorder` ir
            INNER JOIN `tabBin` bin ON ir.parent = bin.item_code AND ir.warehouse = bin.warehouse
            WHERE ir.warehouse_reorder_level > 0 AND bin.actual_qty < ir.warehouse_reorder_level
            LIMIT %s
        """, (int(limit),), as_dict=1)

    @staticmethod
    def get_doc(*args, **kwargs):
        """Fetches a document via smriti.documents layer (wraps frappe at boundary)."""
        return smriti.documents.get(*args, **kwargs)  # smriti-adapter-boundary

    @staticmethod
    def delete_doc(*args, **kwargs):
        """Wraps frappe.delete_doc."""
        return smriti.documents.delete(*args, **kwargs)

    @staticmethod
    def commit(*args, **kwargs):
        """Commits the transaction via smriti.db layer (wraps frappe at boundary)."""
        return frappe.db.commit(*args, **kwargs)  # smriti-adapter-boundary

