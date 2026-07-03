# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/roles.py
# @description: Central Roles Registry for SMRITI Retail OS.
#               Avoid hardcoded string comparisons for role checks.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @architecture: H-5 remediation (hardcoding audit 2026-07-03)
#

class Roles:
    ADMIN           = "Administrator"
    SYSTEM_MANAGER  = "System Manager"
    STORE_MANAGER   = "SMRITI Store Manager"
    CASHIER         = "SMRITI Cashier"
    SYSTEM_ADMIN    = "SMRITI System Admin"
    ACCOUNTANT      = "Accountant"
    SALES_MANAGER   = "Sales Manager"
    SMRITI_TEAM     = "SMRITI Team"
