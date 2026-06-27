# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/doctype/smriti_knowledge_relation/smriti_knowledge_relation.py
# @description: SMRITI DocType controller for SMRITI Knowledge Relation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-21
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from frappe.model.document import Document

class SMRITIKnowledgeRelation(Document):
    def validate(self):
        # 1. Prevent self-relationships (self-loops in graph)
        if self.source_asset_id == self.target_asset_id:
            frappe.throw(frappe._("An asset cannot have a relationship with itself."))

        # 2. Database uniqueness constraint to prevent duplicate edges
        dup = frappe.db.exists(
            "SMRITI Knowledge Relation",
            {
                "source_asset_id": self.source_asset_id,
                "target_asset_id": self.target_asset_id,
                "relationship_type": self.relationship_type,
                "tenant_scope": self.tenant_scope,
                "name": ["!=", self.name]
            }
        )
        if dup:
            frappe.throw(
                frappe._("A duplicate relationship edge already exists in the graph: '{0}' -> '{1}' ({2}).")
                .format(self.source_asset_id, self.target_asset_id, dup)
            )

    def on_update(self):
        # Clear redis cache for both linked assets
        self._clear_linked_caches()

    def on_trash(self):
        # Clear redis cache for both linked assets
        self._clear_linked_caches()

    def _clear_linked_caches(self):
        from smriti_retail_os.services.knowledge_service import invalidate_asset_cache
        for asset_id in (self.source_asset_id, self.target_asset_id):
            if asset_id:
                uri = frappe.db.get_value("SMRITI Knowledge Asset", asset_id, "asset_uri")
                if uri:
                    doc_stub = frappe._dict(asset_uri=uri)
                    invalidate_asset_cache(doc_stub)
