# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_loyalty_rule/smriti_loyalty_rule.py
# @description: SMRITI DocType controller — Frappe document lifecycle handlers.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# @file: smriti_retail_os/doctype/smriti_loyalty_rule/smriti_loyalty_rule.py
# @description: Controller for SMRITI Loyalty Rule.
# @author: Antigravity AI
# @date: 2026-06-18
#

import frappe
from frappe.model.document import Document

class SMRITILoyaltyRule(Document):
    def before_insert(self):
        # Default version initialization
        if not self.version:
            self.version = 1

    def before_save(self):
        # Auto-increment version if it's an existing document being edited
        if not self.is_new():
            self.version = (self.version or 0) + 1
