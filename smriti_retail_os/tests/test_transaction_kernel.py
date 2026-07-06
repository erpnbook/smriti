# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_transaction_kernel.py
# @description: Unit tests for the Universal Transaction Kernel Engine
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-31
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import json
import unittest
from frappe.utils import nowdate

from smriti_retail_os.transaction_kernel import (
    execute_smriti_transaction,
    resolve_identifiers,
    get_doctype_schema,
    apply_pricing_rules,
    _resolve_company,
    _flatten_matrix_to_rows,
    _enrich_payload,
    _lookup_item_master,
    _resolve_fallback_warehouse,
    _coerce_field,
    _meta_has_field,
    _detect_party_doctype,
    _safe_parse_json,
    _resolve_item_code_from_matrix,
)


class TestTransactionKernelHelpers(unittest.TestCase):
    """Unit tests for pure helper functions."""

    @classmethod
    def setUpClass(cls):
        frappe.set_user("Administrator")
        # Resolve a real item for matrix tests (Fix 3 now throws for unknown items)
        cls.real_item = frappe.db.get_value(
            "Item", {"is_sales_item": 1, "disabled": 0}, "name"
        ) or "_SMRITI_GENERIC_ITEM_"

    # ── _safe_parse_json ───────────────────────────────────────────────────────

    def test_safe_parse_json_dict_passthrough(self):
        d = {"a": 1}
        self.assertEqual(_safe_parse_json(d), d)

    def test_safe_parse_json_valid_string(self):
        self.assertEqual(_safe_parse_json('{"x": 42}'), {"x": 42})

    def test_safe_parse_json_list_string(self):
        self.assertEqual(_safe_parse_json('[1, 2]'), [1, 2])

    def test_safe_parse_json_invalid_string(self):
        # Returns empty dict on bad JSON
        self.assertEqual(_safe_parse_json("not-json"), {})

    def test_safe_parse_json_none(self):
        self.assertEqual(_safe_parse_json(None), {})

    # ── _coerce_field ─────────────────────────────────────────────────────────

    def test_coerce_float(self):
        self.assertAlmostEqual(_coerce_field("12.5", "Float"), 12.5)
        self.assertEqual(_coerce_field(None, "Float"), None)

    def test_coerce_int(self):
        self.assertEqual(_coerce_field("3", "Int"), 3)
        self.assertEqual(_coerce_field(3.9, "Int"), 3)

    def test_coerce_check(self):
        self.assertEqual(_coerce_field("1", "Check"), 1)
        self.assertEqual(_coerce_field(0, "Check"), 0)

    def test_coerce_data(self):
        self.assertEqual(_coerce_field(123, "Data"), "123")
        self.assertEqual(_coerce_field(None, "Data"), None)

    def test_coerce_currency(self):
        self.assertAlmostEqual(_coerce_field("1899.00", "Currency"), 1899.0)

    def test_coerce_unknown_type_passthrough(self):
        self.assertEqual(_coerce_field({"k": "v"}, "JSON"), {"k": "v"})

    # ── Matrix flattening ─────────────────────────────────────────────────────

    def test_flatten_matrix_basic(self):
        data = {
            "_matrix": {
                "child_table": "items",
                "size_columns": ["36", "37", "38"],
                "rows": [
                    {
                        "article":  self.real_item,
                        "color":    "",
                        "sizes":    {"36": 0, "37": 9, "38": 5},
                        "mrp":      1899,
                        "rate":     1610.17,
                        "gst_pct":  18,
                        "hsn_code": "64041990",
                    }
                ],
            },
            "customer": "Test Customer",
        }

        meta = frappe.get_meta("Sales Invoice")
        result = _flatten_matrix_to_rows(data, meta)

        # _matrix key should be removed
        self.assertNotIn("_matrix", result)
        # customer header should be preserved
        self.assertEqual(result["customer"], "Test Customer")
        # items expanded: size 36 qty=0 skipped, size 37 qty=9, size 38 qty=5
        items = result.get("items", [])
        self.assertEqual(len(items), 2)

        sizes_in_rows = {r["_size"]: r["qty"] for r in items}
        self.assertEqual(sizes_in_rows["37"], 9.0)
        self.assertEqual(sizes_in_rows["38"], 5.0)

    def test_flatten_matrix_zero_qty_skipped(self):
        data = {
            "_matrix": {
                "size_columns": ["36", "37"],
                "rows": [
                    {"article": "X", "sizes": {"36": 0, "37": 0}}
                ],
            }
        }
        meta = frappe.get_meta("Sales Invoice")
        result = _flatten_matrix_to_rows(data, meta)
        self.assertEqual(result.get("items", []), [])

    def test_flatten_matrix_empty_rows(self):
        data = {"_matrix": {"size_columns": ["36"], "rows": []}}
        meta = frappe.get_meta("Sales Invoice")
        result = _flatten_matrix_to_rows(data, meta)
        self.assertEqual(result.get("items", []), [])

    def test_flatten_matrix_merges_existing_items(self):
        """Existing items in payload should be preserved alongside expanded rows."""
        data = {
            "_matrix": {
                "size_columns": ["36"],
                "rows": [{"article": self.real_item, "sizes": {"36": 2}}],
            },
            "items": [{"item_code": "EXISTING", "qty": 1}],
        }
        meta = frappe.get_meta("Sales Invoice")
        result = _flatten_matrix_to_rows(data, meta)
        items = result.get("items", [])
        item_codes = [r.get("item_code") or r.get("_article") for r in items]
        self.assertIn("EXISTING", item_codes)

    def test_flatten_matrix_numeric_size_keys(self):
        """sizes dict with integer keys should still work."""
        data = {
            "_matrix": {
                "size_columns": [36, 37],
                "rows": [{"article": self.real_item, "sizes": {36: 3, 37: 0}}],
            }
        }
        meta = frappe.get_meta("Sales Invoice")
        result = _flatten_matrix_to_rows(data, meta)
        items = result.get("items", [])
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["qty"], 3.0)

    # ── _resolve_item_code_from_matrix ────────────────────────────────────────

    def test_resolve_item_code_returns_none_on_miss(self):
        """
        After Fix 3: _resolve_item_code_from_matrix must return None for unknown articles.
        It must NOT silently create a ghost sentinel item in the Item master.
        Callers are responsible for raising a visible error.
        """
        code = _resolve_item_code_from_matrix(
            "ZZZNOTEXIST999", "BLUE", "99", ""
        )
        # Must return None — never a sentinel string, never raises
        self.assertIsNone(code)

    def test_flatten_matrix_unknown_article_raises_error(self):
        """
        After Fix 3: _flatten_matrix_to_rows must raise ValidationError when the
        article cannot be resolved to any existing Item in the master.
        """
        data = {
            "_matrix": {
                "size_columns": ["36"],
                "rows": [{"article": "ZZZNOTEXIST999", "color": "RED", "sizes": {"36": 1}}],
            }
        }
        meta = frappe.get_meta("Sales Invoice")
        with self.assertRaises(frappe.ValidationError):
            _flatten_matrix_to_rows(data, meta)


class TestTransactionKernelIntegration(unittest.TestCase):
    """
    Integration tests — require a live Frappe/ERPNext site with at least:
    - One Company
    - One Item (is_sales_item=1)
    - One Customer
    """

    @classmethod
    def setUpClass(cls):
        frappe.set_user("Administrator")

        # Resolve company
        cls.company = (
            frappe.defaults.get_user_default("company")
            or (frappe.get_all("Company", limit=1, pluck="name") or [None])[0]
        )

        # Resolve a real item
        cls.item = frappe.db.get_value(
            "Item",
            {"is_sales_item": 1, "disabled": 0},
            "name"
        )

        # Resolve a real customer
        cls.customer = frappe.db.get_value(
            "Customer",
            {"disabled": 0},
            "name"
        )

    # ── _resolve_company ──────────────────────────────────────────────────────

    def test_resolve_company_from_payload(self):
        company = _resolve_company({"company": self.company})
        self.assertEqual(company, self.company)

    def test_resolve_company_fallback(self):
        company = _resolve_company({})
        self.assertIsNotNone(company)
        self.assertIsInstance(company, str)
        self.assertGreater(len(company), 0)

    # ── get_doctype_schema ────────────────────────────────────────────────────

    def test_get_doctype_schema_sales_invoice(self):
        schema = get_doctype_schema("Sales Invoice")
        self.assertIn("fields", schema)
        self.assertIn("child_tables", schema)
        self.assertIn("mandatory_fields", schema)
        self.assertEqual(schema["doctype"], "Sales Invoice")

        field_names = [f["fieldname"] for f in schema["fields"]]
        self.assertIn("customer", field_names)
        self.assertIn("posting_date", field_names)

    def test_get_doctype_schema_unknown_doctype(self):
        with self.assertRaises(frappe.ValidationError):
            get_doctype_schema("THIS_DOCTYPE_DOES_NOT_EXIST_XYZ")

    def test_get_doctype_schema_missing_doctype(self):
        with self.assertRaises(frappe.ValidationError):
            get_doctype_schema("")

    # ── _meta_has_field / _detect_party_doctype ───────────────────────────────

    def test_meta_has_field_positive(self):
        meta = frappe.get_meta("Sales Invoice")
        self.assertTrue(_meta_has_field(meta, "customer"))
        self.assertTrue(_meta_has_field(meta, "posting_date"))

    def test_meta_has_field_negative(self):
        meta = frappe.get_meta("Sales Invoice")
        self.assertFalse(_meta_has_field(meta, "__nonexistent_field__"))

    def test_detect_party_doctype_customer(self):
        meta = frappe.get_meta("Sales Invoice")
        self.assertEqual(_detect_party_doctype(meta), "Customer")

    def test_detect_party_doctype_supplier(self):
        meta = frappe.get_meta("Purchase Order")
        self.assertEqual(_detect_party_doctype(meta), "Supplier")

    def test_detect_party_doctype_none(self):
        meta = frappe.get_meta("Item")
        self.assertIsNone(_detect_party_doctype(meta))

    # ── _lookup_item_master ───────────────────────────────────────────────────

    def test_lookup_item_master_returns_dict(self):
        if not self.item:
            self.skipTest("No sales item found on this site.")
        data = _lookup_item_master(self.item, self.company)
        self.assertIsInstance(data, dict)
        self.assertIn("stock_uom", data)
        self.assertIn("rate", data)
        self.assertIn("mrp", data)
        self.assertIn("warehouse", data)
        self.assertIn("cost_center", data)

    def test_lookup_item_master_nonexistent(self):
        data = _lookup_item_master("__NONEXISTENT_ITEM__", self.company)
        self.assertEqual(data, {})

    # ── _resolve_fallback_warehouse ───────────────────────────────────────────

    def test_resolve_fallback_warehouse(self):
        wh = _resolve_fallback_warehouse(self.company)
        # May be None on minimal installs — just ensure it doesn't raise
        self.assertTrue(wh is None or isinstance(wh, str))

    # ── execute_smriti_transaction — validate ─────────────────────────────────

    def test_execute_validate_minimal_payload(self):
        if not self.customer:
            self.skipTest("No customer found on this site.")

        result = execute_smriti_transaction(
            doctype="Sales Invoice",
            payload=json.dumps({
                "customer": self.customer,
                "posting_date": nowdate(),
            }),
            action="validate"
        )

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["action"], "validate")
        self.assertIn("enriched_payload", result)
        enriched = result["enriched_payload"]
        self.assertEqual(enriched["customer"], self.customer)
        self.assertEqual(enriched["currency"], "INR")
        self.assertIn("company", enriched)

    def test_execute_validate_with_matrix(self):
        if not self.customer or not self.item:
            self.skipTest("No customer or item found on this site.")

        payload = {
            "customer": self.customer,
            "posting_date": nowdate(),
            "_matrix": {
                "child_table": "items",
                "size_columns": ["36", "37"],
                "rows": [
                    {
                        "article":  self.item,
                        "color":    "",
                        "sizes":    {"36": 2, "37": 3},
                        "mrp":      500,
                        "rate":     423.73,
                        "gst_pct":  18,
                        "hsn_code": "64041990",
                    }
                ],
            }
        }

        result = execute_smriti_transaction(
            doctype="Sales Invoice",
            payload=json.dumps(payload),
            action="validate"
        )

        self.assertEqual(result["status"], "ok")
        enriched = result["enriched_payload"]
        items = enriched.get("items", [])
        # 2 sizes × 1 row (both qty > 0)
        self.assertEqual(len(items), 2)
        total_qty = sum(r["qty"] for r in items)
        self.assertAlmostEqual(total_qty, 5.0)

    def test_execute_invalid_action(self):
        with self.assertRaises(frappe.ValidationError):
            execute_smriti_transaction(
                doctype="Sales Invoice",
                payload=json.dumps({"customer": "X"}),
                action="INVALID_ACTION"
            )

    def test_execute_missing_doctype(self):
        with self.assertRaises(frappe.ValidationError):
            execute_smriti_transaction(
                doctype="",
                payload=json.dumps({}),
                action="validate"
            )

    def test_execute_unknown_doctype(self):
        with self.assertRaises(frappe.ValidationError):
            execute_smriti_transaction(
                doctype="NONEXISTENT_DOCTYPE_XYZ",
                payload=json.dumps({}),
                action="validate"
            )

    def test_execute_missing_payload(self):
        with self.assertRaises(frappe.ValidationError):
            execute_smriti_transaction(
                doctype="Sales Invoice",
                payload=None,
                action="validate"
            )

    # ── resolve_identifiers ───────────────────────────────────────────────────

    def test_resolve_identifiers_item_code(self):
        if not self.item:
            self.skipTest("No item found on this site.")

        results = resolve_identifiers(
            identifiers=json.dumps([{"type": "item_code", "value": self.item}]),
            company=self.company
        )

        self.assertEqual(len(results), 1)
        self.assertIsNotNone(results[0])
        self.assertIn("stock_uom", results[0])

    def test_resolve_identifiers_nonexistent_item(self):
        results = resolve_identifiers(
            identifiers=json.dumps([{"type": "item_code", "value": "__NO_SUCH_ITEM__"}]),
            company=self.company
        )
        self.assertEqual(len(results), 1)
        self.assertIsNone(results[0])

    def test_resolve_identifiers_unknown_type(self):
        results = resolve_identifiers(
            identifiers=json.dumps([{"type": "galaxy_brain", "value": "foo"}]),
            company=self.company
        )
        self.assertEqual(len(results), 1)
        self.assertIn("error", results[0])

    def test_resolve_identifiers_empty_list(self):
        results = resolve_identifiers(
            identifiers=json.dumps([]),
            company=self.company
        )
        self.assertEqual(results, [])

    def test_resolve_identifiers_customer_name(self):
        if not self.customer:
            self.skipTest("No customer found on this site.")

        results = resolve_identifiers(
            identifiers=json.dumps([{"type": "customer_name", "value": self.customer}]),
            company=self.company
        )
        self.assertEqual(len(results), 1)
        self.assertIsNotNone(results[0])

    # ── _enrich_payload ───────────────────────────────────────────────────────

    def test_enrich_payload_sets_defaults(self):
        meta = frappe.get_meta("Sales Invoice")
        enriched = _enrich_payload(
            {"customer": self.customer or "Test"},
            meta,
            "Sales Invoice",
            self.company
        )
        self.assertIn("posting_date", enriched)
        self.assertEqual(enriched["currency"], "INR")
        self.assertEqual(enriched["company"], self.company)
        self.assertEqual(enriched["selling_price_list"], "Standard Selling")

    def test_enrich_payload_item_rows_get_warehouse(self):
        if not self.item or not self.customer:
            self.skipTest("No item or customer found on this site.")

        meta = frappe.get_meta("Sales Invoice")
        data = {
            "customer": self.customer,
            "items": [
                {"item_code": self.item, "qty": 1, "rate": 100}
            ]
        }
        enriched = _enrich_payload(data, meta, "Sales Invoice", self.company)
        items = enriched.get("items", [])
        self.assertEqual(len(items), 1)
        # warehouse should be populated (may be empty on minimal installs)
        self.assertIn("warehouse", items[0])

    # ── apply_pricing_rules ───────────────────────────────────────────────────

    def test_apply_pricing_rules_returns_items(self):
        if not self.item or not self.customer:
            self.skipTest("No item or customer found on this site.")

        payload = {
            "customer": self.customer,
            "posting_date": nowdate(),
            "items": [{"item_code": self.item, "qty": 1, "rate": 500}]
        }
        result = apply_pricing_rules(
            doctype="Sales Invoice",
            payload=json.dumps(payload),
            company=self.company
        )
        self.assertIn("items", result)
        self.assertEqual(len(result["items"]), 1)


def load_tests(loader, tests, pattern):
    """Standard Python test loader hook."""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestTransactionKernelHelpers)
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTransactionKernelIntegration))
    return suite
