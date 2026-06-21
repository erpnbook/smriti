# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/smriti_formula_registry.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
#
# @file: smriti_formula_registry.py
# @description: SMRITI Formula Registry page controller — KGF formula display context.
#

import frappe
from smriti_retail_os.services import formula_service

no_cache = 1

def get_context(context):
    # Guest → redirect to login
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login"
        raise frappe.Redirect

    context.no_cache = 1
    context.title = "SMRITI Formula Registry"
    
    # Retrieve active formulas
    formulas = formula_service.get_active_formulas()
    context.formulas = formulas
    
    # Extract unique categories
    categories = sorted(list(set(f["formula_category"] for f in formulas)))
    context.categories = categories
