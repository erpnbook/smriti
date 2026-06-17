# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/page/smriti_customers/smriti_customers.py
# @description: SMRITI Customer Directory Frappe page controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-17
# @version: 1.0.0
# @license: MIT
#

import frappe

def get_page_context(wrapper):
    return {
        "title": "SMRITI Customer Directory"
    }
