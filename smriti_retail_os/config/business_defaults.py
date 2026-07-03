# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/config/business_defaults.py
# @description: Single source of truth for SMRITI business defaults.
#               All setup paths MUST import from here - never re-declare these literals.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @architecture: H-4 remediation (hardcoding audit 2026-07-03)
#

# Payment modes auto-created for every new SMRITI company.
# To add a new mode, update this list ONLY - both setup.py and setup_wizard_api.py
# will pick it up automatically.
DEFAULT_PAYMENT_MODES = ["Cash", "Bank", "UPI", "Card"]

# Default item group used when no SMRITI Settings.default_item_group is configured.
# This is a last-resort safety net only - configure per-domain in SMRITI Settings.
FALLBACK_ITEM_GROUP = "Products"
