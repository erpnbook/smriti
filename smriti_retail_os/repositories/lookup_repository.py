# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/repositories/lookup_repository.py
# @desc:    Data Access Repository Layer for SMRITI Universal Lookup.
# @author:  Jawahar R. Mallah
#

import frappe

class LookupRepository:
    """
    Isolates direct database document instantiation for SMRITI Universal Lookup.
    Fits the layered architecture persistence boundary.
    """

    @staticmethod
    def new_doc(doctype, *args, **kwargs):
        """Wraps frappe.new_doc to prevent direct service-layer instantiation."""
        return frappe.new_doc(doctype, *args, **kwargs)

    @staticmethod
    def get_doc(doctype, name=None, *args, **kwargs):
        """Wraps frappe.get_doc."""
        return frappe.get_doc(doctype, name, *args, **kwargs)
