# -*- coding: utf-8 -*-
#
# @file:    smriti_retail_os/tests/test_purchase_studio.py
# @desc:    Test suite for SMRITI Purchase Studio — business logic + API layer.
#           Covers all 14 service contracts (SC-01 to SC-14) and edge cases.
# @author:  Jawahar R. Mallah <jawahar.mallah@gmail.com>
# @std:     AES-002 SSDL v1.0.0 — Layer 9 (Tests)
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK. All rights reserved.
#

import frappe
import unittest
from frappe.utils import nowdate


class TestPurchaseSettings(unittest.TestCase):
    """Tests for purchase_settings_service.py"""

    def setUp(self):
        from smriti_retail_os.purchase_studio.service import purchase_settings_service as svc
        self.svc = svc

    def test_get_settings_returns_defaults_when_not_configured(self):
        """get_settings() must never throw — returns safe defaults."""
        s = self.svc.get_settings()
        self.assertIn("purchase_invoice_policy", s)
        self.assertIn(s["purchase_invoice_policy"], ["grn_only", "standalone", "both"])
        self.assertGreaterEqual(s["approval_threshold"], 0)

    def test_check_invoice_policy_returns_valid_value(self):
        pol = self.svc.check_invoice_policy()
        self.assertIn(pol, ["grn_only", "standalone", "both"])

    def test_approval_required_zero_threshold(self):
        """Zero threshold means no approval ever required."""
        self.svc.save_settings({"approval_threshold": 0})
        result = self.svc.check_approval_required(999999)
        self.assertFalse(result)

    def test_approval_required_above_threshold(self):
        """Amount above threshold must require approval."""
        self.svc.save_settings({"approval_threshold": 10000})
        result = self.svc.check_approval_required(15000)
        self.assertTrue(result)

    def test_approval_not_required_below_threshold(self):
        """Amount at or below threshold must not require approval."""
        self.svc.save_settings({"approval_threshold": 10000})
        result = self.svc.check_approval_required(9999)
        self.assertFalse(result)

    def test_save_settings_invalid_policy_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.save_settings({"purchase_invoice_policy": "INVALID"})

    def test_save_settings_negative_threshold_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.save_settings({"approval_threshold": -1})

    def test_save_settings_tolerance_out_of_range_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.save_settings({"tolerance_percent": 150})

    def test_save_settings_invalid_lc_rule_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.save_settings({"landed_cost_rule": "auto"})

    def test_save_settings_nonexistent_warehouse_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.save_settings({"default_warehouse": "NONEXISTENT-WH-SMRITI-TEST"})

    def tearDown(self):
        # Reset to safe defaults after each test
        try:
            self.svc.save_settings({
                "purchase_invoice_policy": "both",
                "approval_threshold": 0,
                "tolerance_percent": 0
            })
        except Exception:
            pass


class TestAuditService(unittest.TestCase):
    """Tests for audit_service.py"""

    def setUp(self):
        from smriti_retail_os.purchase_studio.service import audit_service as svc
        self.svc = svc

    def test_log_creates_audit_record(self):
        """log() must create a SMRITI Purchase Audit Log record."""
        before_count = frappe.db.count("SMRITI Purchase Audit Log",
                                        {"event_type": "TEST_EVENT"})
        self.svc.log(
            event_type="TEST_EVENT",
            payload={"doctype": "Test", "name": "TEST-001"},
            before={"status": "before"},
            after={"status": "after"},
            reason="Unit test"
        )
        after_count = frappe.db.count("SMRITI Purchase Audit Log",
                                       {"event_type": "TEST_EVENT"})
        self.assertEqual(after_count, before_count + 1)

    def test_log_does_not_raise_on_payload_failure(self):
        """log() must never raise — it catches its own exceptions."""
        # Pass an unserializable payload — log() must absorb the error
        import datetime
        try:
            self.svc.log(
                event_type="TEST_SAFE",
                payload={"doctype": "Test", "name": "X",
                         "dt": datetime.datetime.now()}
            )
        except Exception as e:
            self.fail(f"audit_service.log() raised unexpectedly: {e}")

    def test_event_type_constants_are_strings(self):
        """All event type constants must be non-empty strings."""
        for const in [
            self.svc.PO_SUBMITTED, self.svc.PO_APPROVED, self.svc.GRN_SUBMITTED,
            self.svc.PI_SUBMITTED, self.svc.RETURN_SUBMITTED, self.svc.SETTINGS_CHANGED
        ]:
            self.assertIsInstance(const, str)
            self.assertTrue(len(const) > 0)


class TestErpAdapter(unittest.TestCase):
    """Tests for erp_adapter.py — mock-safe utility functions."""

    def setUp(self):
        from smriti_retail_os.purchase_studio.adapter import erp_adapter
        self.adapter = erp_adapter

    def test_resolve_company_returns_string_or_none(self):
        result = self.adapter.resolve_company()
        self.assertTrue(result is None or isinstance(result, str))

    def test_get_default_warehouse_none_company(self):
        result = self.adapter.get_default_warehouse(None)
        self.assertIsNone(result)

    def test_get_item_flags_empty_list(self):
        result = self.adapter.get_item_flags([])
        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), 0)

    def test_get_po_not_found_raises(self):
        with self.assertRaises(frappe.DoesNotExistError):
            self.adapter.get_po("NONEXISTENT-PO-SMRITI-9999")

    def test_get_grn_not_found_raises(self):
        with self.assertRaises(frappe.DoesNotExistError):
            self.adapter.get_grn("NONEXISTENT-GRN-SMRITI-9999")

    def test_get_pi_not_found_raises(self):
        with self.assertRaises(frappe.DoesNotExistError):
            self.adapter.get_pi("NONEXISTENT-PI-SMRITI-9999")

    def test_list_purchase_orders_returns_dict(self):
        result = self.adapter.list_purchase_orders({}, ["name", "supplier"], 1, 5)
        self.assertIn("total", result)
        self.assertIn("items", result)
        self.assertIsInstance(result["items"], list)

    def test_list_grns_returns_dict(self):
        result = self.adapter.list_grns({"docstatus": 1, "is_return": 0}, ["name"], 1, 5)
        self.assertIn("total", result)

    def test_list_purchase_invoices_returns_dict(self):
        result = self.adapter.list_purchase_invoices({"docstatus": 1}, ["name"], 1, 5)
        self.assertIn("total", result)

    def test_get_supplier_outstanding_returns_float(self):
        company = self.adapter.resolve_company()
        if company:
            result = self.adapter.get_supplier_outstanding("__nonexistent__", company)
            self.assertIsInstance(result, float)


class TestPurchaseServiceValidation(unittest.TestCase):
    """Tests for purchase_service.py input validation — no ERPNext write operations."""

    def setUp(self):
        from smriti_retail_os.purchase_studio.service import purchase_service as svc
        self.svc = svc

    def test_create_po_empty_items_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.create_purchase_order(
                supplier="__nonexistent__",
                items_list=[],
            )

    def test_create_po_no_supplier_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.create_purchase_order(
                supplier="SUPPLIER_DOES_NOT_EXIST_SMRITI_TEST",
                items_list=[{"item_code": "TEST-ITEM", "qty": 1, "rate": 100}]
            )

    def test_create_grn_empty_items_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.create_grn(supplier="__nonexistent__", items_list=[])

    def test_create_grn_no_supplier_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.create_grn(
                supplier="SUPPLIER_DOES_NOT_EXIST_SMRITI_TEST",
                items_list=[{"item_code": "TEST", "qty": 1, "rate": 10}]
            )

    def test_create_return_no_reason_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.create_purchase_return(
                grn_name="NONEXISTENT-GRN",
                return_reason=""
            )

    def test_create_return_blank_reason_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.create_purchase_return(
                grn_name="NONEXISTENT-GRN",
                return_reason="   "
            )

    def test_create_return_nonexistent_grn_raises(self):
        with self.assertRaises(Exception):
            self.svc.create_purchase_return(
                grn_name="MAT-PRE-NONEXISTENT-9999",
                return_reason="Test reason"
            )

    def test_resolve_po_approval_invalid_action_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.resolve_po_approval("PO-001", "invalid_action")

    def test_resolve_po_approval_reject_no_reason_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.resolve_po_approval("PO-001", "reject", reason=None)

    def test_get_supplier_ledger_no_supplier_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.get_supplier_ledger(
                supplier="", from_date=nowdate(), to_date=nowdate()
            )

    def test_get_supplier_ledger_no_dates_raises(self):
        with self.assertRaises(frappe.ValidationError):
            self.svc.get_supplier_ledger(
                supplier="TEST", from_date="", to_date=""
            )

    def test_search_suppliers_short_query_returns_empty(self):
        result = self.svc.search_suppliers("X")  # too short
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_search_items_short_query_returns_empty(self):
        result = self.svc.search_items("A")  # too short
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 0)

    def test_search_suppliers_valid_query_returns_list(self):
        result = self.svc.search_suppliers("test")
        self.assertIsInstance(result, list)

    def test_create_invoice_policy_grn_only_blocks_standalone(self):
        from smriti_retail_os.purchase_studio.service import purchase_settings_service as s
        s.save_settings({"purchase_invoice_policy": "grn_only"})
        with self.assertRaises(frappe.ValidationError):
            self.svc.create_invoice(mode="standalone", supplier="TEST")
        s.save_settings({"purchase_invoice_policy": "both"})

    def test_create_invoice_policy_standalone_blocks_grn_linked(self):
        from smriti_retail_os.purchase_studio.service import purchase_settings_service as s
        s.save_settings({"purchase_invoice_policy": "standalone"})
        with self.assertRaises(frappe.ValidationError):
            self.svc.create_invoice(mode="grn_linked", grn_name="MAT-PRE-TEST")
        s.save_settings({"purchase_invoice_policy": "both"})

    def test_validate_grn_lines_no_po_returns_none(self):
        """Standalone GRN — no PO validation needed, must return without error."""
        result = self.svc.validate_grn_lines(
            [{"item_code": "X", "qty": 5}],
            po_name=None,
            allow_over_receipt=False
        )
        self.assertIsNone(result)

    def test_get_dashboard_returns_expected_keys(self):
        data = self.svc.get_dashboard_data()
        for key in ["open_pos", "pending_grns", "unpaid_invoices_amt", "month_spend", "recent_activity"]:
            self.assertIn(key, data)

    def test_list_purchase_orders_returns_paginated_dict(self):
        result = self.svc.list_purchase_orders(page=1, page_size=5)
        self.assertIn("total", result)
        self.assertIn("items", result)
        self.assertIsInstance(result["items"], list)

    def test_list_grns_returns_paginated_dict(self):
        result = self.svc.list_grns(page=1, page_size=5)
        self.assertIn("total", result)

    def test_list_invoices_returns_paginated_dict(self):
        result = self.svc.list_invoices(page=1, page_size=5)
        self.assertIn("total", result)

    def test_list_returns_returns_paginated_dict(self):
        result = self.svc.list_returns(page=1, page_size=5)
        self.assertIn("total", result)


class TestBackwardCompatibility(unittest.TestCase):
    """
    Regression: existing purchase_api.py functions must still be callable.
    purchase.html depends on get_open_purchase_orders and get_po_details.
    """

    def test_get_open_purchase_orders_still_callable(self):
        """Legacy endpoint in new api must delegate to service layer."""
        from smriti_retail_os.purchase_studio.api.purchase_api import get_open_purchase_orders
        # Should not raise — returns list (possibly empty)
        result = get_open_purchase_orders()
        self.assertIsInstance(result, list)

    def test_new_api_endpoints_are_whitelisted(self):
        """All 14 SC endpoints must exist and be callable in purchase_api."""
        import smriti_retail_os.purchase_studio.api.purchase_api as api_module
        endpoints = [
            "get_purchase_dashboard", "get_purchase_orders", "get_purchase_order_detail",
            "create_purchase_order", "resolve_po_approval", "get_grns", "get_grn_detail",
            "create_grn", "create_invoice", "get_invoices", "get_invoice_detail",
            "get_returns", "create_purchase_return", "get_supplier_ledger",
            "get_purchase_settings", "save_purchase_settings",
            "search_suppliers", "search_items"
        ]
        for ep in endpoints:
            fn = getattr(api_module, ep, None)
            self.assertIsNotNone(fn, f"Endpoint {ep} not found in purchase_api")
            self.assertTrue(callable(fn), f"Endpoint {ep} is not callable")
            # Verify whitelisted — attribute name varies by Frappe version
            is_whitelisted = (
                getattr(fn, "whitelisted", False)
                or getattr(fn, "is_whitelisted", False)
                or getattr(getattr(fn, "__wrapped__", fn), "whitelisted", False)
            )
            self.assertTrue(
                is_whitelisted,
                f"Endpoint {ep} does not appear to be @frappe.whitelist() decorated "
                f"(checked: whitelisted, is_whitelisted, __wrapped__.whitelisted)"
            )

