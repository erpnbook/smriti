# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_knowledge_asset/smriti_knowledge_asset.py
# @description: SMRITI DocType controller for SMRITI Knowledge Asset.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-21
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.model.document import Document

class SMRITIKnowledgeAsset(Document):
    def validate(self):
        # Enforce uniqueness of asset_code and asset_uri
        if self.asset_code:
            dup_code = frappe.db.exists(
                "SMRITI Knowledge Asset",
                {"asset_code": self.asset_code, "name": ["!=", self.name]}
            )
            if dup_code:
                frappe.throw(frappe._("Asset Code '{0}' is already registered in '{1}'.").format(self.asset_code, dup_code))

        if self.asset_uri:
            dup_uri = frappe.db.exists(
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
