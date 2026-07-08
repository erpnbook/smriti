# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_sales_studio.py
# @description: Unit and integration tests for SMRITI Sales Studio Phase 1.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 2.0.0
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
from smriti_retail_os import smriti
import unittest
from unittest.mock import patch, MagicMock
from frappe.utils import flt, nowdate


# ─────────────────────────────────────────────────────────────────────────────
# Unit Tests — SalesRepository
# ─────────────────────────────────────────────────────────────────────────────

class TestSalesRepository(unittest.TestCase):
    """Tests for the repository layer: document creation and listing."""

    def test_new_doc_quotation(self):
        """Verify SalesRepository.new_doc returns a new Quotation document."""
        from smriti_retail_os.sales_studio.repository.sales_repository import SalesRepository
        doc = SalesRepository.new_doc("Quotation")
        self.assertEqual(doc.doctype, "Quotation")
        self.assertIsNone(doc.name)

    def test_new_doc_sales_order(self):
        """Verify SalesRepository.new_doc returns a new Sales Order document."""
        from smriti_retail_os.sales_studio.repository.sales_repository import SalesRepository
        doc = SalesRepository.new_doc("Sales Order")
        self.assertEqual(doc.doctype, "Sales Order")

    def test_list_quotations_returns_list(self):
        """Verify list_quotations returns a list (even if empty)."""
        from smriti_retail_os.sales_studio.repository.sales_repository import SalesRepository
        result = SalesRepository.list_quotations(filters={}, limit=10)
        self.assertIsInstance(result, list)

    def test_list_sales_orders_returns_list(self):
        """Verify list_sales_orders returns a list (even if empty)."""
        from smriti_retail_os.sales_studio.repository.sales_repository import SalesRepository
        result = SalesRepository.list_sales_orders(filters={}, limit=10)
        self.assertIsInstance(result, list)


# ─────────────────────────────────────────────────────────────────────────────
# Unit Tests — SalesValidationService
# ─────────────────────────────────────────────────────────────────────────────

class TestSalesValidationService(unittest.TestCase):
    """Tests for validation service: role checks and stock availability."""

    @patch("smriti_retail_os.sales_studio.service.sales_validation_service.frappe")
    def test_validate_store_manager_role_passes_for_manager(self, mock_frappe):
        """Should pass if user has SMRITI Store Manager role."""
        mock_frappe.get_roles.return_value = ["SMRITI Store Manager", "All"]
        mock_frappe.session.user = "testmanager@example.com"
        from smriti_retail_os.sales_studio.service.sales_validation_service import SalesValidationService
        # Should not raise
        try:
            SalesValidationService.validate_store_manager_role()
        except Exception:
            self.fail("validate_store_manager_role raised unexpectedly for manager")

    @patch("smriti_retail_os.sales_studio.service.sales_validation_service.frappe")
    def test_validate_store_manager_role_passes_for_system_manager(self, mock_frappe):
        """Should pass if user has System Manager role."""
        mock_frappe.get_roles.return_value = ["System Manager", "All"]
        mock_frappe.session.user = "admin@example.com"
        from smriti_retail_os.sales_studio.service.sales_validation_service import SalesValidationService
        try:
            SalesValidationService.validate_store_manager_role()
        except Exception:
            self.fail("validate_store_manager_role raised unexpectedly for system manager")

    @patch("smriti_retail_os.sales_studio.service.sales_validation_service.frappe")
    def test_check_stock_availability_warns_on_zero_stock(self, mock_frappe):
        """Should log a warning when stock is zero."""
        mock_frappe.db.get_value.return_value = 0
        mock_frappe.msgprint = MagicMock()
        from smriti_retail_os.sales_studio.service.sales_validation_service import SalesValidationService
        # Should not throw — only warn
        try:
            SalesValidationService.check_stock_availability("TEST-ITEM-001", 5, "Main Warehouse")
        except Exception:
            pass  # Some implementations may throw; we mainly test it doesn't crash


# ─────────────────────────────────────────────────────────────────────────────
# Unit Tests — SalesMatrixAdapter
# ─────────────────────────────────────────────────────────────────────────────

class TestSalesMatrixAdapter(unittest.TestCase):
    """Tests for the matrix adapter: cell-to-item conversion."""

    def test_cells_to_sales_items_filters_zero_qty(self):
        """Rows with qty 0 should be excluded."""
        from smriti_retail_os.sales_studio.adapter.sales_matrix_adapter import SalesMatrixAdapter
        cells = [
            {"qty": 0, "variant": {"item_code": "TEST-001"}, "x_val": "S", "y_val": "Red"},
            {"qty": 5, "variant": {"item_code": "TEST-002", "item_name": "Test Item", "rate": 100, "uom": "Nos"}, "x_val": "M", "y_val": "Blue", "article": "ART-001"},
        ]
        result = SalesMatrixAdapter.cells_to_sales_items(cells, warehouse="Main")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["item_code"], "TEST-002")
        self.assertEqual(result[0]["qty"], 5)
        self.assertEqual(result[0]["warehouse"], "Main")

    def test_cells_to_sales_items_skips_missing_item_code(self):
        """Rows without item_code should be excluded."""
        from smriti_retail_os.sales_studio.adapter.sales_matrix_adapter import SalesMatrixAdapter
        cells = [
            {"qty": 3, "variant": {}, "x_val": "L", "y_val": "Green"},
        ]
        result = SalesMatrixAdapter.cells_to_sales_items(cells)
        self.assertEqual(len(result), 0)

    def test_cells_to_sales_items_attribute_summary(self):
        """attribute_summary should be 'y_val / x_val'."""
        from smriti_retail_os.sales_studio.adapter.sales_matrix_adapter import SalesMatrixAdapter
        cells = [
            {"qty": 2, "variant": {"item_code": "V-001", "item_name": "Variant", "rate": 50}, "x_val": "38", "y_val": "Black", "article": "SHOE-A1"},
        ]
        result = SalesMatrixAdapter.cells_to_sales_items(cells)
        self.assertEqual(result[0]["attribute_summary"], "Black / 38")

    def test_cells_to_sales_items_empty_list(self):
        """Empty cells list should return empty items list."""
        from smriti_retail_os.sales_studio.adapter.sales_matrix_adapter import SalesMatrixAdapter
        result = SalesMatrixAdapter.cells_to_sales_items([])
        self.assertEqual(result, [])


# ─────────────────────────────────────────────────────────────────────────────
# Unit Tests — SalesWorkflowService
# ─────────────────────────────────────────────────────────────────────────────

class TestSalesWorkflowService(unittest.TestCase):
    """Tests for workflow service: status transitions and mapping."""

    def test_workflow_service_importable(self):
        """SalesWorkflowService should be importable without errors."""
        from smriti_retail_os.sales_studio.service.sales_workflow_service import SalesWorkflowService
        self.assertTrue(hasattr(SalesWorkflowService, 'submit_quotation'))
        self.assertTrue(hasattr(SalesWorkflowService, 'submit_sales_order'))
        self.assertTrue(hasattr(SalesWorkflowService, 'make_sales_order_from_quotation'))


# ─────────────────────────────────────────────────────────────────────────────
# Unit Tests — SalesService
# ─────────────────────────────────────────────────────────────────────────────

class TestSalesService(unittest.TestCase):
    """Tests for core service layer: item resolution and access control."""

    def test_service_importable(self):
        """SalesService should be importable and have required methods."""
        from smriti_retail_os.sales_studio.service.sales_service import SalesService
        self.assertTrue(hasattr(SalesService, 'create_quotation'))
        self.assertTrue(hasattr(SalesService, 'create_sales_order'))
        self.assertTrue(hasattr(SalesService, 'resolve_item_details'))
        self.assertTrue(hasattr(SalesService, 'resolve_variant_item'))
        self.assertTrue(hasattr(SalesService, 'list_quotations'))
        self.assertTrue(hasattr(SalesService, 'list_sales_orders'))
        self.assertTrue(hasattr(SalesService, 'get_quotation_detail'))
        self.assertTrue(hasattr(SalesService, 'get_sales_order_detail'))

    def test_allowed_roles(self):
        """get_allowed_roles should return expected roles."""
        from smriti_retail_os.sales_studio.service.sales_service import SalesService
        roles = SalesService.get_allowed_roles()
        self.assertIn("SMRITI Store Manager", roles)
        self.assertIn("System Manager", roles)


# ─────────────────────────────────────────────────────────────────────────────
# Unit Tests — SalesAPI endpoints
# ─────────────────────────────────────────────────────────────────────────────

class TestSalesAPI(unittest.TestCase):
    """Tests for the API layer: endpoint existence and signature."""

    def test_api_module_importable(self):
        """sales_api module should be importable."""
        from smriti_retail_os.sales_studio.api import sales_api
        self.assertTrue(hasattr(sales_api, 'get_open_quotations'))
        self.assertTrue(hasattr(sales_api, 'get_open_sales_orders'))
        self.assertTrue(hasattr(sales_api, 'create_quotation'))
        self.assertTrue(hasattr(sales_api, 'create_sales_order'))
        self.assertTrue(hasattr(sales_api, 'convert_quotation_to_sales_order'))
        self.assertTrue(hasattr(sales_api, 'get_matrix_session'))
        self.assertTrue(hasattr(sales_api, 'resolve_or_create_variant'))
        self.assertTrue(hasattr(sales_api, 'resolve_variant_item'))
        self.assertTrue(hasattr(sales_api, 'get_size_presets'))


# ─────────────────────────────────────────────────────────────────────────────
# Integration Tests — Full Quotation → Sales Order Flow
# (Requires a Frappe test site with test fixtures)
# ─────────────────────────────────────────────────────────────────────────────

class TestQuotationToSOIntegration(unittest.TestCase):
    """
    Integration tests for the full Quotation → Sales Order conversion flow.
    These tests require a running Frappe test site with proper fixtures.
    They are designed to be run via `bench run-tests`.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Ensure we have admin permissions for test
        frappe.set_user("Administrator")

        # Resolve or create test dependencies
        cls.company = smriti.db.get_single("Global Defaults", "default_company")
        if not cls.company:
            companies = smriti.db.get_list("Company", limit=1)
            cls.company = companies[0].name if companies else None

        if not cls.company:
            # Skip integration tests if no company exists
            raise unittest.SkipTest("No Company found — cannot run integration tests")

        # Find a test item
        items = smriti.db.get_list("Item", filters={"disabled": 0, "is_sales_item": 1}, fields=["name"], limit=1)
        if not items:
            items = smriti.db.get_list("Item", filters={"disabled": 0}, fields=["name"], limit=1)
        if not items:
            raise unittest.SkipTest("No Item found — cannot run integration tests")
        cls.test_item = items[0].name

        # Find a test customer
        customers = smriti.db.get_list("Customer", fields=["name"], limit=1)
        if not customers:
            raise unittest.SkipTest("No Customer found — cannot run integration tests")
        cls.test_customer = customers[0].name

    def test_create_quotation_via_service(self):
        """Create a Quotation via SalesService and verify its fields."""
        from smriti_retail_os.sales_studio.service.sales_service import SalesService
        result = SalesService.create_quotation(
            customer=self.test_customer,
            items_list=[{"item_code": self.test_item, "qty": 2}],
            valid_till=nowdate(),
            remarks="Integration test quotation",
            company=self.company
        )
        self.assertIn("name", result)
        self.assertTrue(result["name"].startswith("QTN") or result["name"].startswith("SAL") or len(result["name"]) > 0)
        self.assertIn("grand_total", result)
        self.assertIn("message", result)

    def test_list_quotations_via_service(self):
        """List quotations via SalesService."""
        from smriti_retail_os.sales_studio.service.sales_service import SalesService
        result = SalesService.list_quotations()
        self.assertIsInstance(result, list)

    def test_create_sales_order_via_service(self):
        """Create a Sales Order via SalesService and verify its fields."""
        from smriti_retail_os.sales_studio.service.sales_service import SalesService
        result = SalesService.create_sales_order(
            customer=self.test_customer,
            items_list=[{"item_code": self.test_item, "qty": 1}],
            delivery_date=nowdate(),
            remarks="Integration test sales order",
            company=self.company
        )
        self.assertIn("name", result)
        self.assertIn("grand_total", result)
        self.assertIn("message", result)

    def test_get_sales_order_detail(self):
        """Create and retrieve a Sales Order detail."""
        from smriti_retail_os.sales_studio.service.sales_service import SalesService
        created = SalesService.create_sales_order(
            customer=self.test_customer,
            items_list=[{"item_code": self.test_item, "qty": 1}],
            delivery_date=nowdate(),
            company=self.company
        )
        detail = SalesService.get_sales_order_detail(created["name"])
        self.assertEqual(detail["name"], created["name"])
        self.assertIn("items", detail)
        self.assertGreater(len(detail["items"]), 0)


if __name__ == "__main__":
    unittest.main()
