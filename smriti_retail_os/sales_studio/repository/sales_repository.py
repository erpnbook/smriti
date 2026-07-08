# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/sales_studio/repository/sales_repository.py
# @desc:    Data Access Repository Layer for SMRITI Sales Studio.
#           Encapsulates all database reads and writes to ERPNext Sales-related doctypes.
# @author:  Jawahar R. Mallah
#

# framework-adapter: wraps frappe ORM at the repository boundary — Guard 6 exempt
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from frappe import _
from smriti_retail_os import smriti

class SalesRepository:
    """
    Isolates direct database access for SMRITI Sales Order and Quotation operations.
    Follows Rule 4 of SMRITI Constitution (Repository Layer Isolation).
    Targets existing ERPNext "Quotation" and "Sales Order" DocTypes.
    """

    @staticmethod
    def get_quotation(name):
        if not smriti.db.exists("Quotation", name):
            frappe.throw(_("Quotation {0} does not exist.").format(name), frappe.DoesNotExistError)
        return smriti.documents.get("Quotation", name)

    @staticmethod
    def list_quotations(filters=None, fields=None, order_by="modified desc", limit=200):
        if filters is None:
            filters = {}
        if fields is None:
            fields = ["name", "customer", "customer_name", "transaction_date", "grand_total", "docstatus", "status"]
        return frappe.get_list(
            "Quotation",
            filters=filters,
            fields=fields,
            order_by=order_by,
            limit_page_length=int(limit)
        )

    @staticmethod
    def save_quotation(doc):
        doc.save(ignore_permissions=True)
        return doc.name

    @staticmethod
    def insert_quotation(doc):
        doc.insert(ignore_permissions=True)
        return doc.name

    @staticmethod
    def submit_quotation(doc):
        doc.docstatus = 1
        doc.save(ignore_permissions=True)
        return doc.name

    @staticmethod
    def cancel_quotation(doc):
        doc.docstatus = 2
        doc.save(ignore_permissions=True)
        return doc.name

    @staticmethod
    def get_sales_order(name):
        if not smriti.db.exists("Sales Order", name):
            frappe.throw(_("Sales Order {0} does not exist.").format(name), frappe.DoesNotExistError)
        return smriti.documents.get("Sales Order", name)

    @staticmethod
    def list_sales_orders(filters=None, fields=None, order_by="modified desc", limit=200):
        if filters is None:
            filters = {}
        if fields is None:
            fields = ["name", "customer", "customer_name", "transaction_date", "grand_total", "per_delivered", "status", "docstatus"]
        return frappe.get_list(
            "Sales Order",
            filters=filters,
            fields=fields,
            order_by=order_by,
            limit_page_length=int(limit)
        )

    @staticmethod
    def save_sales_order(doc):
        doc.save(ignore_permissions=True)
        return doc.name

    @staticmethod
    def insert_sales_order(doc):
        doc.insert(ignore_permissions=True)
        return doc.name

    @staticmethod
    def submit_sales_order(doc):
        doc.docstatus = 1
        doc.save(ignore_permissions=True)
        return doc.name

    @staticmethod
    def cancel_sales_order(doc):
        doc.docstatus = 2
        doc.save(ignore_permissions=True)
        return doc.name

    @staticmethod
    def new_doc(*args, **kwargs):
        """Creates a new document via smriti.documents layer (wraps frappe at boundary)."""
        return smriti.documents.new(*args, **kwargs)

    @staticmethod
    def db_sql(*args, **kwargs):
        """Executes raw SQL via smriti.db layer (wraps frappe at boundary)."""
        return smriti.db.sql(*args, **kwargs)
