# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/page/smriti_negative_stock/smriti_negative_stock.py
# @description: SMRITI Negative Stock Management Page controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-29
# @version: 1.9.0
# @license: MIT
#

import frappe

def get_page_context(wrapper):
    return {
        "title": "SMRITI Negative Stock Management"
    }
