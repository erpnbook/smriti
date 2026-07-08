# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/sales_studio/repository/sales_repository.py
# @desc:    Data Access Repository Layer for SMRITI Sales Studio.
#           Encapsulates all database reads and writes to ERPNext Sales-related doctypes.
# @author:  Jawahar R. Mallah
#

import frappe
from frappe import _

class SalesRepository:
    """
    Isolates direct database access for SMRITI Sales Order and Quotation operations.
    Follows Rule 4 of SMRITI Constitution (Repository Layer Isolation).
    Targets existing ERPNext "Quotation" and "Sales Order" DocTypes.
    """

    @staticmethod
    def get_quotation(name):
        if not frappe.db.exists("Quotation", name):
            frappe.throw(_("Quotation {0} does not exist.").format(name), frappe.DoesNotExistError)
        return frappe.get_doc("Quotation", name)

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
        if not frappe.db.exists("Sales Order", name):
            frappe.throw(_("Sales Order {0} does not exist.").format(name), frappe.DoesNotExistError)
        return frappe.get_doc("Sales Order", name)

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
        """Wraps frappe.new_doc."""
        return frappe.new_doc(*args, **kwargs)

    @staticmethod
    def db_sql(*args, **kwargs):
        """Wraps frappe.db.sql."""
        return frappe.db.sql(*args, **kwargs)
