# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/formula_api.py
# @description: SMRITI Formula Api — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from smriti_retail_os.services import formula_service

@frappe.whitelist()
def get_active_formulas(category=None):
    """
    Whitelisted API to retrieve all active approved formulas, optionally filtered by category.
    """
    return formula_service.get_active_formulas(category=category)

@frappe.whitelist()
def get_formula_detail(formula_id, version=None):
    """
    Whitelisted API to retrieve the detailed doc of a specific formula.
    """
    doc = formula_service.get_formula_detail(formula_id, version=version)
    return doc.as_dict()
