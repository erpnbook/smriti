# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_party_sales_upload/smriti_party_sales_upload.py
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
from frappe import _

class SMRITIPartySalesUpload(Document):
    def validate(self):
        from smriti_retail_os.psv_service import validate_sales_upload
        validate_sales_upload(self)

    def on_submit(self):
        from smriti_retail_os.psv_service import process_sales_upload_submit
        process_sales_upload_submit(self)

    def on_cancel(self):
        from smriti_retail_os.psv_service import process_sales_upload_cancel
        process_sales_upload_cancel(self)
