# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/page/smriti_sales_return/smriti_sales_return.py
# @description: SMRITI Sales Return Desk Page controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-17
# @version: 1.8.6
# @license: MIT
#

import frappe

def get_page_context(wrapper):
    return {
        "title": "SMRITI Sales Returns & Credit Notes"
    }
