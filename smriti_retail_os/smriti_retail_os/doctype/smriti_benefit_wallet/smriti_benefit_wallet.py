# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_benefit_wallet/smriti_benefit_wallet.py
# @description: Handles user login, registration, and JWT token generation.
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
from frappe import _
from frappe.model.document import Document

class SMRITIBenefitWallet(Document):
    def validate(self):
        # Programmatic check for unique (customer, company, benefit_instrument)
        existing = frappe.db.exists("SMRITI Benefit Wallet", {
            "customer": self.customer,
            "company": self.company,
            "benefit_instrument": self.benefit_instrument,
            "name": ["!=", self.name]
        })
        if existing:
            frappe.throw(
                _("A Benefit Wallet already exists for Customer {0}, Company {1}, and Instrument {2}.")
                .format(self.customer, self.company, self.benefit_instrument),
                frappe.ValidationError
            )
