# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/www/purchase_order.py
# @desc:    Page controller for /purchase_order route.
#           - Dedicated standalone Purchase Order page without sidebar or topbar.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe
from smriti_retail_os.www.smriti_purchase_order import get_context as _get_context

no_cache = 1
title    = "SMRITI — Dedicated Purchase Order"

def get_context(context):
    return _get_context(context)
