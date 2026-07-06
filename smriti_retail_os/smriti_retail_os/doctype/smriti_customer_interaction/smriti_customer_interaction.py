# -*- coding: utf-8 -*-
#
# @file: smriti_customer_interaction.py
# @description: Document controller class for SMRITI Customer Interaction.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-22
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate

class SMRITICustomerInteraction(Document):
    def validate(self):
        if self.interaction_date and getdate(self.interaction_date) > getdate(frappe.utils.nowdate()):
            frappe.throw(
                _("Interaction Date ({0}) cannot be a future date.").format(self.interaction_date),
                frappe.ValidationError
            )
