# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/page/smriti_suppliers/smriti_suppliers.py
# @description: SMRITI Supplier Registry Frappe page controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-17
# @version: 1.8.6
# @license: MIT
#

import frappe

def get_page_context(wrapper):
    return {
        "title": "SMRITI Supplier Registry"
    }
