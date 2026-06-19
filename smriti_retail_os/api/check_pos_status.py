# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/check_pos_status.py
# @description: SMRITI Check Pos Status — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
import frappe

def run():
    print("POS SETTINGS:")
    try:
        print(frappe.db.get_value("POS Settings", "POS Settings", ["invoice_type", "pos_closing_entry_validation_amount"], as_dict=True))
    except Exception as e:
        print("Error:", e)
