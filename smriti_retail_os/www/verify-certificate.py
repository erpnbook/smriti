# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/www/verify-certificate.py
# @description: Public verification page controller for SMRITI Certifications.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-23
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from smriti_retail_os.api.help_api import verify_psv_certificate

no_cache = 1

def get_context(context):
    context.no_cache = 1
    context.title = "Verify Certificate — SMRITI Retail OS"
    context.base_template_path = "smriti_retail_os/templates/blank.html"

    cert_hash = frappe.form_dict.get("hash") or frappe.form_dict.get("certificate_hash")
    context.cert_hash = cert_hash

    # Call public verification API
    context.result = {"valid": False, "error": "No certificate hash provided"}
    if cert_hash:
        try:
            res = verify_psv_certificate(cert_hash)
            context.result = res
        except Exception as e:
            context.result = {"valid": False, "error": str(e)}
