# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/page/smriti_supplier_returns/smriti_supplier_returns.py
# @description: SMRITI Supplier Returns Desk Page controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-17
# @version: 1.0.0
# @license: MIT
#

import frappe

def get_page_context(wrapper):
    return {
        "title": "SMRITI Supplier Returns"
    }
