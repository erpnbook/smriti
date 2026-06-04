# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/page/smriti-inventory/smriti-inventory.py
# @description: SMRITI Inventory Frappe page controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe

def get_page_context(wrapper):
    return {
        "title": "SMRITI Retail Inventory"
    }
