# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/page/smriti_udne/smriti_udne.py
# @description: SMRITI UDNE Admin Page controller.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-27
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
#

import frappe

def get_page_context(wrapper):
    return {
        "title": "SMRITI Universal Numbering Settings"
    }
