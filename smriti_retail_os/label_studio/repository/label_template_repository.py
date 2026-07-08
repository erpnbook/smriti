# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/label_studio/repository/label_template_repository.py
# @desc:    Data Access Repository Layer for SMRITI Label Templates.
# @author:  Jawahar R. Mallah
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti

class LabelTemplateRepository:
    """
    Isolates direct database access for SMRITI Label Templates.
    Follows SMRITI repository layer rules.
    """

    @staticmethod
    def get_template(template_name):
        """Retrieves raw print template document."""
        return smriti.documents.get("SMRITI Print Template", template_name)

    @staticmethod
    def get_templates_list(filters=None):
        """Fetches list of active templates."""
        if filters is None:
            filters = {}
        filters["disabled"] = 0
        return frappe.get_list("SMRITI Print Template", filters=filters, fields=["name", "template_name", "label_type"])
