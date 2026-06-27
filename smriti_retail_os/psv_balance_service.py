# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/psv_balance_service.py
# @description: SMRITI Psv Balance Service — retail operating system module.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, Smriti Retail OS and contributors
# For license information, please see license.txt

import frappe
from smriti_retail_os.balance_engine import get_party_balance, get_bulk_party_balances

def get_channel_balance(customer: str, item_code: str = None):
    """
    Returns the stock balance for a given channel/customer.
    If item_code is provided, returns float balance.
    Otherwise, returns dict of {item_code: qty}.
    """
    psas = frappe.get_all("SMRITI Party Stock Account", filters={"customer": customer, "active": 1}, fields=["name"])
    if not psas:
        return 0.0 if item_code else {}

    if item_code:
        total = 0.0
        for psa in psas:
            total += get_party_balance(psa.name, item_code)
        return total
    else:
        balances = {}
        for psa in psas:
            psa_bal = get_bulk_party_balances(psa.name)
            for item, qty in psa_bal.items():
                balances[item] = balances.get(item, 0.0) + qty
        return balances
