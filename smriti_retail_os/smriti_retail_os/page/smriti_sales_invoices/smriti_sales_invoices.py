# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/page/smriti_sales_invoices/smriti_sales_invoices.py
# @description: SMRITI Sales Invoices Desk Page controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-17
# @version: 1.0.0
# @license: MIT
#

import frappe

def get_page_context(wrapper):
    return {
        "title": "SMRITI Billing Invoices Tracker"
    }
