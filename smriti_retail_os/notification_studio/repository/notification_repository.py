# -*- coding: utf-8 -*-
"""
smriti_retail_os/notification_studio/repository/notification_repository.py
Repository layer for SMRITI Notification Studio database queries.
Author: Jawahar R. Mallah
"""
import frappe

class NotificationRepository:
    @staticmethod
    def get_safety_stock_violations(limit=50) -> list[dict]:
        """Fetch items where actual stock level is below item-level safety stock."""
        return frappe.db.sql("""
            SELECT bin.item_code, bin.warehouse, bin.actual_qty, item.safety_stock as limit_qty
            FROM `tabBin` bin
            INNER JOIN `tabItem` item ON bin.item_code = item.name
            WHERE item.safety_stock > 0 AND bin.actual_qty < item.safety_stock
            LIMIT %s
        """, (int(limit),), as_dict=1)

    @staticmethod
    def get_reorder_level_violations(limit=50) -> list[dict]:
        """Fetch items where actual stock level is below warehouse-level reorder limit."""
        return frappe.db.sql("""
            SELECT bin.item_code, bin.warehouse, bin.actual_qty, ir.warehouse_reorder_level as limit_qty
            FROM `tabItem Reorder` ir
            INNER JOIN `tabBin` bin ON ir.parent = bin.item_code AND ir.warehouse = bin.warehouse
            WHERE ir.warehouse_reorder_level > 0 AND bin.actual_qty < ir.warehouse_reorder_level
            LIMIT %s
        """, (int(limit),), as_dict=1)
