# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/page/smriti-shift/smriti-shift.py
# @description: SMRITI Shift Frappe page controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe

def get_context(context):
    context.no_cache = 1
