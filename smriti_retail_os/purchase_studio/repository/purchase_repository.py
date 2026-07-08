# -*- coding: utf-8 -*-
# SMRITI Purchase Studio — Data Access Repository Layer
# framework-adapter: wraps frappe ORM at the repository boundary — Guard 6 exempt
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti

class PurchaseRepository:
    """
    Isolates direct database access for SMRITI Supplier, SMRITI Purchase Order,
    and SMRITI Purchase Order Item.
    Follows Rule 4 of SMRITI Constitution (Repository Layer Isolation).
    """

    @staticmethod
    def get_supplier(supplier_id):
        if not smriti.db.exists("SMRITI Supplier", supplier_id):
            frappe.throw(_("Supplier {0} does not exist.").format(supplier_id), frappe.DoesNotExistError)
        return smriti.documents.get("SMRITI Supplier", supplier_id)

    @staticmethod
    def list_suppliers(filters=None, fields=None, order_by="modified desc", limit=200):
        if filters is None:
            filters = {}
        if fields is None:
            fields = ["name", "supplier_name", "supplier_type", "supplier_group", "disabled"]
        return frappe.get_list(
            "SMRITI Supplier",
            filters=filters,
            fields=fields,
            order_by=order_by,
            limit_page_length=int(limit)
        )

    @staticmethod
    def save_supplier(supplier_doc):
        supplier_doc.save(ignore_permissions=True)
        return supplier_doc.name

    @staticmethod
    def get_po(po_name):
        if not smriti.db.exists("SMRITI Purchase Order", po_name):
            frappe.throw(_("Purchase Order {0} does not exist.").format(po_name), frappe.DoesNotExistError)
        return smriti.documents.get("SMRITI Purchase Order", po_name)

    @staticmethod
    def list_pos(filters=None, fields=None, order_by="modified desc", limit=200):
        if filters is None:
            filters = {}
        if fields is None:
            fields = ["name", "supplier", "supplier_name", "transaction_date", "schedule_date", "grand_total", "total_qty", "per_received", "status"]
        return frappe.get_list(
            "SMRITI Purchase Order",
            filters=filters,
            fields=fields,
            order_by=order_by,
            limit_page_length=int(limit)
        )

    @staticmethod
    def save_po(po_doc):
        po_doc.save(ignore_permissions=True)
        return po_doc.name

    @staticmethod
    def insert_po(po_doc):
        po_doc.insert(ignore_permissions=True)
        return po_doc.name

    @staticmethod
    def submit_po(po_doc):
        po_doc.docstatus = 1
        po_doc.save(ignore_permissions=True)
        return po_doc.name

    @staticmethod
    def cancel_po(po_doc):
        po_doc.docstatus = 2
        po_doc.save(ignore_permissions=True)
        return po_doc.name

    @staticmethod
    def new_doc(*args, **kwargs):
        """Creates a new document via smriti.documents layer (wraps frappe at boundary)."""
        return smriti.documents.new(*args, **kwargs)

    @staticmethod
    def db_sql(*args, **kwargs):
        """Executes raw SQL via smriti.db layer (wraps frappe at boundary)."""
        return smriti.db.sql(*args, **kwargs)

