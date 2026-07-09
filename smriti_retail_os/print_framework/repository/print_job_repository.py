# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/print_framework/repository/print_job_repository.py
# @desc:    Data Access Repository Layer for SMRITI Print Jobs.
# @author:  Jawahar R. Mallah
#

# framework-adapter: wraps frappe ORM at the repository boundary — Guard 6 exempt
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti

class PrintJobRepository:
    """
    Isolates direct database access for SMRITI Print Job logs.
    Follows SMRITI layered architecture repository pattern.
    """

    @staticmethod
    def get_doc(*args, **kwargs):
        return smriti.documents.get(*args, **kwargs)  # smriti-adapter-boundary

    @staticmethod
    def new_doc(*args, **kwargs):
        return smriti.documents.new(*args, **kwargs)

    @staticmethod
    def set_value(*args, **kwargs):
        return smriti.db.set_value(*args, **kwargs)

    @staticmethod
    def delete(*args, **kwargs):
        return smriti.db.delete(*args, **kwargs)

    @staticmethod
    def delete_doc(*args, **kwargs):
        return smriti.documents.delete(*args, **kwargs)

    @staticmethod
    def commit(*args, **kwargs):
        return frappe.db.commit(*args, **kwargs)  # smriti-adapter-boundary
