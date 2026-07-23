# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti_demand_forecasts.py
# @description: SMRITI Demand Forecasts & Inventory Projections Web App Controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-07-23
# @version: 2.2.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from smriti_retail_os.api.demand_api import get_demand_forecasts

no_cache = 1


def get_context(context):
    context.title = "Demand Forecasts — SMRITI Retail OS"
    context.initial_forecasts = get_demand_forecasts()
    return context
