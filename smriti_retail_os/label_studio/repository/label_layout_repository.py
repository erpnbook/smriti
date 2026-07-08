# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/label_studio/repository/label_layout_repository.py
# @desc:    Data Access Repository Layer for SMRITI Label Layout sizes.
# @author:  Jawahar R. Mallah
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti

class LabelLayoutRepository:
    """
    Isolates direct database access for SMRITI Label Layout and page dimension settings.
    """

    @staticmethod
    def get_layout(layout_name):
        """Retrieves page size layout specs."""
        return smriti.documents.get("SMRITI Label Layout", layout_name)

    @staticmethod
    def get_layouts_list(filters=None):
        """Fetches list of active layouts."""
        return frappe.get_list("SMRITI Label Layout", filters=filters, fields=["name", "width_mm", "height_mm", "columns"])
