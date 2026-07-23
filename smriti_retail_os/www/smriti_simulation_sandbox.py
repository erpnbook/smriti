# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti_simulation_sandbox.py
# @description: SMRITI Product Twin Simulation Sandbox Web App Controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-07-23
# @version: 2.2.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from smriti_retail_os.api.simulation_api import get_simulation_presets, run_simulation

no_cache = 1


def get_context(context):
    context.title = "Simulation Sandbox — SMRITI Retail OS"
    context.presets = get_simulation_presets()
    context.initial_simulation = run_simulation({})
    return context
