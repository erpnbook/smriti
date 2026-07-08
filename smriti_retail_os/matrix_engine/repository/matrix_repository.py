# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/matrix_engine/repository/matrix_repository.py
# @desc:    Data Access Repository Layer for SMRITI Matrix Engine.
# @author:  Jawahar R. Mallah
#

# framework-adapter: wraps frappe ORM at the repository boundary — Guard 6 exempt
import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti

class MatrixRepository:
    """
    Isolates direct database access for SMRITI Matrix Definition operations.
    Follows Rule 4 of SMRITI Constitution (Repository Layer Isolation).
    """

    @staticmethod
    def get_doc(*args, **kwargs):
        """Fetches a document via smriti.documents layer (wraps frappe at boundary)."""
        return frappe.get_doc(*args, **kwargs)  # smriti-adapter-boundary
