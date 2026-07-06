# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/matrix_engine/repository/matrix_repository.py
# @desc:    Data Access Repository Layer for SMRITI Matrix Engine.
# @author:  Jawahar R. Mallah
#

import frappe

class MatrixRepository:
    """
    Isolates direct database access for SMRITI Matrix Definition operations.
    Follows Rule 4 of SMRITI Constitution (Repository Layer Isolation).
    """

    @staticmethod
    def get_doc(*args, **kwargs):
        """Wraps frappe.get_doc."""
        return frappe.get_doc(*args, **kwargs)
