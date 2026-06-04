# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/page/smriti-desk/smriti-desk.py
# @description: SMRITI Desk Frappe page controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe

def get_context(context):
    context.no_cache = 1
