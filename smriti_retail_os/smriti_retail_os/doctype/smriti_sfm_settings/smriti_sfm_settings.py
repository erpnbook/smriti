# -*- coding: utf-8 -*-
#
# @file: smriti_sfm_settings.py
# @description: Document controller class for SMRITI SFM Settings.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import flt

class SMRITISFMSettings(Document):
    def validate(self):
        # Validation: primary_split_pct + secondary_split_pct must equal 100
        p_pct = flt(self.primary_split_pct or 0.0)
        s_pct = flt(self.secondary_split_pct or 0.0)
        if p_pct + s_pct != 100.0:
            frappe.throw(
                _("Primary Split Percentage ({0}) and Secondary Split Percentage ({1}) must sum to exactly 100.").format(p_pct, s_pct),
                frappe.ValidationError
            )
