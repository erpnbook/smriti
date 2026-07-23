# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti_crm.py
# @description: SMRITI CRM & Customer Insights Web App Controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-07-23
# @version: 2.2.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from smriti_retail_os.api.crm_api import get_crm_insights

no_cache = 1


def get_context(context):
    context.title = "CRM & Customer Insights — SMRITI Retail OS"
    context.initial_crm = get_crm_insights()
    return context
