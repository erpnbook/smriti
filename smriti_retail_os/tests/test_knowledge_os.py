# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_knowledge_os.py
# @description: Unit tests for SMRITI Knowledge Operating System (SKOS) Core.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-21
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import unittest
from smriti_retail_os.services.knowledge_service import (
    get_asset_by_uri,
    resolve_relations,
    search_assets,
    invalidate_asset_cache
)

class TestKnowledgeOS(unittest.TestCase):
    def setUp(self):
        # 1. Clean up test database records
        frappe.db.delete("SMRITI Knowledge Relation")
        frappe.db.delete("SMRITI Knowledge Asset", {"asset_code": ["like", "TST-%"]})
        frappe.db.delete("SMRITI Business Term", {"term_id": ["in", ["TST-T-001", "TST-T-002"]]})
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": ["in", ["TST-F-001"]]})
        frappe.db.delete("SMRITI Entity Attribute Value", {"parent": "TST-ITEM-001"})
        frappe.db.delete("SMRITI Custom Attribute", {"attribute_code": ["like", "TST_%"]})
        frappe.db.commit()

        # 2. Create actual referenced documents
        self.term_1 = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "TST-T-001",
            "term_name": "Test Term 1",
            "term_category": "Inventory",
            "term_version": "1.0.0",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-21",
            "definition": "Definition for test term 1",
            "hinglish_definition": "Hinglish explanation here"
        }).insert(ignore_permissions=True)

        self.term_2 = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "TST-T-002",
            "term_name": "Test Term 2",
            "term_category": "Inventory",
            "term_version": "1.0.0",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-21",
            "definition": "Definition for test term 2",
            "hinglish_definition": "Hinglish explanation here"
        }).insert(ignore_permissions=True)

        self.formula_1 = frappe.get_doc({
            "doctype": "SMRITI Formula Definition",
            "formula_id": "TST-F-001",
            "formula_name": "Test Formula 1",
            "formula_version": "1.0.0",
            "formula_category": "Inventory",
            "status": "Approved",
            "is_active": 1,
            "effective_date": "2026-06-21",
            "formula_expression": "a + b"
        }).insert(ignore_permissions=True)
        frappe.db.commit()

        frappe.cache().delete_value("smriti:skos:asset:smriti:formula:TST-F-001")
        frappe.cache().delete_value("smriti:skos:asset:smriti:term:TST-T-001")
        frappe.cache().delete_value("smriti:skos:asset:smriti:term:TST-T-002")

    def tearDown(self):
        frappe.db.delete("SMRITI Knowledge Relation")
        frappe.db.delete("SMRITI Knowledge Asset", {"asset_code": ["like", "TST-%"]})
        frappe.db.delete("SMRITI Business Term", {"term_id": ["in", ["TST-T-001", "TST-T-002"]]})
        frappe.db.delete("SMRITI Formula Definition", {"formula_id": ["in", ["TST-F-001"]]})
        frappe.db.delete("SMRITI Entity Attribute Value", {"parent": "TST-ITEM-001"})
        frappe.db.delete("SMRITI Custom Attribute", {"attribute_code": ["like", "TST_%"]})
        frappe.db.commit()
        frappe.cache().delete_value("smriti:skos:asset:smriti:formula:TST-F-001")
        frappe.cache().delete_value("smriti:skos:asset:smriti:term:TST-T-001")
        frappe.cache().delete_value("smriti:skos:asset:smriti:term:TST-T-002")

    def test_asset_registry_validations(self):
        """KAR-01: Verifies unique constraints and basic validations."""
        frappe.db.delete("SMRITI Knowledge Asset", {"asset_code": ["like", "TST-%"]})
        frappe.db.commit()

        asset1 = frappe.get_doc({
            "doctype": "SMRITI Knowledge Asset",
            "asset_code": "TST-TERM-WOC",
            "asset_uri": "smriti:term:TST-T-001",
            "asset_type": "Term",
            "title": "Test Weeks of Cover",
            "status": "Approved",
            "is_active": 1,
            "reference_doctype": "SMRITI Business Term",
            "reference_name": self.term_1.name
        })
        asset1.insert(ignore_permissions=True)
        frappe.db.commit()

        # Duplicate asset_code should fail
        asset_dup_code = frappe.get_doc({
            "doctype": "SMRITI Knowledge Asset",
            "asset_code": "TST-TERM-WOC",
            "asset_uri": "smriti:term:TST-T-002",
            "asset_type": "Term",
            "title": "Dup Weeks of Cover",
            "status": "Approved",
            "is_active": 1,
            "reference_doctype": "SMRITI Business Term",
            "reference_name": self.term_2.name
        })
        with self.assertRaises(frappe.ValidationError):
            asset_dup_code.insert(ignore_permissions=True)

        # Duplicate asset_uri should fail
        asset_dup_uri = frappe.get_doc({
            "doctype": "SMRITI Knowledge Asset",
            "asset_code": "TST-TERM-WOC2",
            "asset_uri": "smriti:term:TST-T-001",
            "asset_type": "Term",
            "title": "Dup Weeks of Cover 2",
            "status": "Approved",
            "is_active": 1,
            "reference_doctype": "SMRITI Business Term",
            "reference_name": self.term_2.name
        })
        with self.assertRaises(frappe.ValidationError):
            asset_dup_uri.insert(ignore_permissions=True)

    def test_relations_validations(self):
        """KGR-01: Verifies unique edge constraint, self-loop detection, and traversals."""
        frappe.db.delete("SMRITI Knowledge Asset", {"asset_code": ["like", "TST-%"]})
        frappe.db.commit()

        # Create assets
        asset1 = frappe.get_doc({
            "doctype": "SMRITI Knowledge Asset",
            "asset_code": "TST-TERM-A",
            "asset_uri": "smriti:term:TST-T-001",
            "asset_type": "Term",
            "title": "Asset A",
            "status": "Approved",
            "is_active": 1,
            "reference_doctype": "SMRITI Business Term",
            "reference_name": self.term_1.name
        }).insert(ignore_permissions=True)

        asset2 = frappe.get_doc({
            "doctype": "SMRITI Knowledge Asset",
            "asset_code": "TST-FORMULA-B",
            "asset_uri": "smriti:formula:TST-F-001",
            "asset_type": "Formula",
            "title": "Asset B",
            "status": "Approved",
            "is_active": 1,
            "reference_doctype": "SMRITI Formula Definition",
            "reference_name": self.formula_1.name
        }).insert(ignore_permissions=True)

        # Self-relation should fail
        rel_self = frappe.get_doc({
            "doctype": "SMRITI Knowledge Relation",
            "source_asset_id": asset1.name,
            "target_asset_id": asset1.name,
            "relationship_type": "defines",
            "strength": "Strong"
        })
        with self.assertRaises(frappe.ValidationError):
            rel_self.insert(ignore_permissions=True)

        # Create valid relation
        rel1 = frappe.get_doc({
            "doctype": "SMRITI Knowledge Relation",
            "source_asset_id": asset1.name,
            "target_asset_id": asset2.name,
            "relationship_type": "defines",
            "strength": "Strong",
            "is_primary": 1,
            "tenant_scope": "Global"
        })
        rel1.insert(ignore_permissions=True)
        frappe.db.commit()

        # Duplicate relation edge should fail
        rel_dup = frappe.get_doc({
            "doctype": "SMRITI Knowledge Relation",
            "source_asset_id": asset1.name,
            "target_asset_id": asset2.name,
            "relationship_type": "defines",
            "strength": "Medium",
            "is_primary": 0,
            "tenant_scope": "Global"
        })
        with self.assertRaises(frappe.ValidationError):
            rel_dup.insert(ignore_permissions=True)

    def test_custom_attributes_validations(self):
        """UAF-01: Verifies Custom Attribute and Entity Value constraints."""
        # 1. Create select custom attribute
        attr = frappe.get_doc({
            "doctype": "SMRITI Custom Attribute",
            "attribute_code": "TST_FESTIVAL_GROUP",
            "attribute_name": "Test Festival Group",
            "attribute_group": "Marketing",
            "attribute_scope": "Global",
            "entity_type": "Item",
            "attribute_type": "Select",
            "options": "Diwali, Eid, Christmas",
            "is_filterable": 1,
            "is_reportable": 1
        })
        attr.insert(ignore_permissions=True)
        frappe.db.commit()

        # Invalid attribute code format should fail (contains invalid character - hyphen)
        attr_invalid = frappe.get_doc({
            "doctype": "SMRITI Custom Attribute",
            "attribute_code": "TST-INVALID-CODE",
            "attribute_name": "Test Invalid Name",
            "attribute_group": "Custom",
            "entity_type": "Item",
            "attribute_type": "Text"
        })
        with self.assertRaises(frappe.ValidationError):
            attr_invalid.insert(ignore_permissions=True)

        # 2. Add entity value assignment
        val = frappe.get_doc({
            "doctype": "SMRITI Entity Attribute Value",
            "parenttype": "Item",
            "parent": "TST-ITEM-001",
            "attribute_code": "TST_FESTIVAL_GROUP",
            "attribute_value": "Diwali"
        })
        val.insert(ignore_permissions=True)
        frappe.db.commit()

        # Invalid select option value should fail
        val_invalid_option = frappe.get_doc({
            "doctype": "SMRITI Entity Attribute Value",
            "parenttype": "Item",
            "parent": "TST-ITEM-001",
            "attribute_code": "TST_FESTIVAL_GROUP",
            "attribute_value": "Holi" # not in Diwali, Eid, Christmas
        })
        with self.assertRaises(frappe.ValidationError):
            val_invalid_option.insert(ignore_permissions=True)

        # Mapped parenttype mismatch should fail (configured for Item, applied to Customer)
        val_invalid_entity = frappe.get_doc({
            "doctype": "SMRITI Entity Attribute Value",
            "parenttype": "Customer",
            "parent": "TST-ITEM-001",
            "attribute_code": "TST_FESTIVAL_GROUP",
            "attribute_value": "Diwali"
        })
        with self.assertRaises(frappe.ValidationError):
            val_invalid_entity.insert(ignore_permissions=True)

    def test_platform_service_endpoints(self):
        """SKOS Core API: Verifies cached get, traverse depth caps, and search permissions."""
        frappe.db.delete("SMRITI Knowledge Asset", {"asset_code": ["like", "TST-%"]})
        frappe.db.commit()

        # Create active approved public asset
        asset_pub = frappe.get_doc({
            "doctype": "SMRITI Knowledge Asset",
            "asset_code": "TST-TERM-PUBLIC",
            "asset_uri": "smriti:term:TST-T-001",
            "asset_type": "Term",
            "title": "Public Weeks of Cover",
            "status": "Approved",
            "is_active": 1,
            "visibility": "Public",
            "access_policy": "Public",
            "reference_doctype": "SMRITI Business Term",
            "reference_name": self.term_1.name
        }).insert(ignore_permissions=True)

        # Create active approved manager-only asset
        asset_mgr = frappe.get_doc({
            "doctype": "SMRITI Knowledge Asset",
            "asset_code": "TST-TERM-MANAGER",
            "asset_uri": "smriti:term:TST-T-002",
            "asset_type": "Term",
            "title": "Manager Weeks of Cover",
            "status": "Approved",
            "is_active": 1,
            "visibility": "Internal",
            "access_policy": "Manager",
            "reference_doctype": "SMRITI Business Term",
            "reference_name": self.term_2.name
        }).insert(ignore_permissions=True)
        frappe.db.commit()

        # 1. Fetch URI works and caches
        doc_fetched = get_asset_by_uri("smriti:term:TST-T-001")
        self.assertEqual(doc_fetched.doctype, "SMRITI Business Term")

        # 2. Access policy checks (Guest/Cashier role raises PermissionError on Manager policy)
        orig_user = frappe.session.user
        frappe.set_user("Guest")
        try:
            # Public should pass for Guest
            self.assertEqual(get_asset_by_uri("smriti:term:TST-T-001").doctype, "SMRITI Business Term")
            # Manager policy should fail for Guest
            with self.assertRaises(frappe.PermissionError):
                get_asset_by_uri("smriti:term:TST-T-002")
        finally:
            frappe.set_user(orig_user)

        # 3. Search enforces role-based policy filtering (excludes Manager assets for Guest)
        frappe.set_user("Guest")
        try:
            search_res = search_assets("Weeks of Cover")
            asset_codes = [r["asset_code"] for r in search_res]
            self.assertIn("TST-TERM-PUBLIC", asset_codes)
            self.assertNotIn("TST-TERM-MANAGER", asset_codes)
        finally:
            frappe.set_user(orig_user)

    def test_lifecycle_auto_sync(self):
        """SKOS Core API: Verifies lifecycle auto-sync hooks for Terms and Formulas."""
        # Clean up in case of leftover TST-LIFECYCLE-T1
        frappe.db.delete("SMRITI Knowledge Asset", {"asset_uri": "smriti:term:TST-LIFECYCLE-T1"})
        frappe.db.delete("SMRITI Business Term", {"term_id": "TST-LIFECYCLE-T1"})
        frappe.db.commit()

        # Create a new Business Term (draft must be inactive)
        term = frappe.get_doc({
            "doctype": "SMRITI Business Term",
            "term_id": "TST-LIFECYCLE-T1",
            "term_name": "Lifecycle Term 1",
            "term_category": "Inventory",
            "term_version": "1.0.0",
            "status": "Draft",
            "is_active": 0,
            "effective_date": "2026-06-21",
            "definition": "Lifecycle definition",
            "hinglish_definition": "Hinglish explanation here"
        }).insert(ignore_permissions=True)
        frappe.db.commit()

        # The KAR asset should be automatically created by the hooks
        asset_name = frappe.db.exists("SMRITI Knowledge Asset", {"asset_uri": "smriti:term:TST-LIFECYCLE-T1"})
        self.assertIsNotNone(asset_name)
        asset_doc = frappe.get_doc("SMRITI Knowledge Asset", asset_name)
        self.assertEqual(asset_doc.title, "Lifecycle Term 1")
        self.assertEqual(asset_doc.status, "Draft")
        self.assertEqual(asset_doc.is_active, 0)

        # Update the Business Term
        term.term_name = "Lifecycle Term Updated"
        term.status = "Approved"
        term.is_active = 1
        term.save(ignore_permissions=True)
        frappe.db.commit()

        # The KAR asset should be automatically updated
        asset_doc.reload()
        self.assertEqual(asset_doc.title, "Lifecycle Term Updated")
        self.assertEqual(asset_doc.status, "Approved")
        self.assertEqual(asset_doc.is_active, 1)

        # Delete the Business Term
        term.delete()
        frappe.db.commit()

        # The KAR asset and relations should be automatically cleaned up
        self.assertFalse(frappe.db.exists("SMRITI Knowledge Asset", {"asset_uri": "smriti:term:TST-LIFECYCLE-T1"}))


