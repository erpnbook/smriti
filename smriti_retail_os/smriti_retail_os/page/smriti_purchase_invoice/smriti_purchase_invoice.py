# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/page/smriti_purchase_invoice/smriti_purchase_invoice.py
# @description: SMRITI Purchase Invoices Desk Page controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-17
# @version: 1.8.6
# @license: MIT
#

import frappe

def get_page_context(wrapper):
    return {
        "title": "SMRITI Purchase Invoices Tracker"
    }
