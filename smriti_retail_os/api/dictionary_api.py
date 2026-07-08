# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/dictionary_api.py
# @description: SMRITI Dictionary Api — retail operating system module.
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
from smriti_retail_os.services import dictionary_service

@frappe.whitelist()
def get_active_terms(category=None):
    """
    Whitelisted API to retrieve the list of active business terms.
    """
    return dictionary_service.get_active_terms(category=category)

@frappe.whitelist()
def get_term_detail(term_id, version=None):
    """
    Whitelisted API to retrieve the dictionary term detail payload.
    """
    return dictionary_service.get_term_detail(term_id, version=version)
