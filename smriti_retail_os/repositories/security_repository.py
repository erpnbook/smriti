# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/repositories/security_repository.py
# @desc:    Data Access Repository Layer for SMRITI Security and User Management.
#           Encapsulates all database reads and writes to ERPNext User and Role-related doctypes.
# @author:  Jawahar R. Mallah
#

import frappe

class SecurityRepository:
    """
    Isolates direct database access for SMRITI User, Role, and Workflow operations.
    Follows SMRITI layered architecture repository pattern.
    """

    @staticmethod
    def get_doc(*args, **kwargs):
        return frappe.get_doc(*args, **kwargs)

    @staticmethod
    def new_doc(*args, **kwargs):
        return frappe.new_doc(*args, **kwargs)

    @staticmethod
    def set_value(*args, **kwargs):
        return frappe.db.set_value(*args, **kwargs)

    @staticmethod
    def delete(*args, **kwargs):
        return frappe.db.delete(*args, **kwargs)

    @staticmethod
    def delete_doc(*args, **kwargs):
        return frappe.delete_doc(*args, **kwargs)

    @staticmethod
    def commit(*args, **kwargs):
        return frappe.db.commit(*args, **kwargs)
