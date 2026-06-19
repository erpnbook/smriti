# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_benefit_resolution_policy/smriti_benefit_resolution_policy.py
# @description: SMRITI DocType controller — Frappe document lifecycle handlers.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, AITDL and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SMRITIBenefitResolutionPolicy(Document):
    def validate(self):
        if self.is_active:
            # Deactivate all other policies
            frappe.db.sql(
                "update `tabSMRITI Benefit Resolution Policy` set is_active = 0 where name != %s",
                (self.name,)
            )
