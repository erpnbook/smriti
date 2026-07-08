# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_knowledge_asset/smriti_knowledge_asset.py
# @description: SMRITI DocType controller for SMRITI Knowledge Asset.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-21
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe  # frappe.whitelist, frappe.throw, frappe.session, frappe.logger — framework utilities
from smriti_retail_os import smriti
from frappe.model.document import Document

class SMRITIKnowledgeAsset(Document):
    def validate(self):
        # Enforce uniqueness of asset_code and asset_uri
        if self.asset_code:
            dup_code = smriti.db.exists(
                "SMRITI Knowledge Asset",
                {"asset_code": self.asset_code, "name": ["!=", self.name]}
            )
            if dup_code:
                frappe.throw(frappe._("Asset Code '{0}' is already registered in '{1}'.").format(self.asset_code, dup_code))

        if self.asset_uri:
            dup_uri = smriti.db.exists(
                "SMRITI Knowledge Asset",
                {"asset_uri": self.asset_uri, "name": ["!=", self.name]}
            )
            if dup_uri:
                frappe.throw(frappe._("Asset URI '{0}' is already registered in '{1}'.").format(self.asset_uri, dup_uri))

    def on_update(self):
        # Clear redis caches on modification
        from smriti_retail_os.services.knowledge_service import invalidate_asset_cache
        invalidate_asset_cache(self)

    def on_trash(self):
        # Clear redis caches on deletion
        from smriti_retail_os.services.knowledge_service import invalidate_asset_cache
        invalidate_asset_cache(self)
