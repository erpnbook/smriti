# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/page/smriti_item_master/smriti_item_master.py
# @description: SMRITI Item Master Frappe page controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe

def get_page_context(wrapper):
    return {
        "title": "Item Master Import"
    }
