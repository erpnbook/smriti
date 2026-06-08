# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_party_physical_snapshot/smriti_party_physical_snapshot.py
# @description: Handles user login, registration, and JWT token generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# -*- coding: utf-8 -*-
# Copyright (c) 2026, SMRITI Retail OS and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document

class SMRITIPartyPhysicalSnapshot(Document):
    def validate(self):
        from smriti_retail_os.psv_service import validate_physical_snapshot
        validate_physical_snapshot(self)

    def before_submit(self):
        from smriti_retail_os.psv_service import process_physical_snapshot_submit
        process_physical_snapshot_submit(self)

    def on_cancel(self):
        from smriti_retail_os.psv_service import process_physical_snapshot_cancel
        process_physical_snapshot_cancel(self)
