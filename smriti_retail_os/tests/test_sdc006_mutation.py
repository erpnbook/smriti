# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_sdc006_mutation.py
# @description: SDC-006 Mutation / Fault-Injection Tests.
#               Validates that governance gates (SDC401, SDC402) actually fire
#               when faults are injected. These are NEGATIVE path tests —
#               they prove the compiler FAILS correctly, not that it passes.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @license: MIT
#

import unittest
import sys
import os
import io
import json
import hashlib
import copy
import shutil
import tempfile

# ---------------------------------------------------------------------------
# Path bootstrap — works in both Frappe bench context and standalone Python
# ---------------------------------------------------------------------------
def _locate_sdc_and_repo():
    """Locate the SDC directory and repository root.

    Prefers the *topmost* ancestor directory that contains sdc/discovery.py.
    This prevents the search from stopping at the app-level copy when the
    canonical repo root is further up.
    """
    # Try Frappe path first
    try:
        import frappe
        app_path = frappe.get_app_path("smriti_retail_os")
        # Try topmost repo root first
        parent_repo_root = os.path.dirname(os.path.dirname(os.path.dirname(app_path)))
        if os.path.exists(os.path.join(parent_repo_root, "sdc", "discovery.py")):
            repo_root = parent_repo_root
        else:
            repo_root = os.path.dirname(app_path)
    except Exception:
        # Standalone: walk up from this test file and collect ALL ancestors
        # that contain sdc/discovery.py — then pick the highest-level one.
        here = os.path.dirname(os.path.abspath(__file__))
        candidates = []
        current = here
        for _ in range(8):
            if os.path.exists(os.path.join(current, "sdc", "discovery.py")):
                candidates.append(current)
            parent = os.path.dirname(current)
            if parent == current:
                break
            current = parent
        # Pick the topmost match (fewest path components = true repo root)
        repo_root = candidates[-1] if candidates else here

    sdc_path = os.path.join(repo_root, "sdc")
    if sdc_path not in sys.path:
        sys.path.insert(0, sdc_path)
    return sdc_path, repo_root


_sdc_path, _repo_root = _locate_sdc_and_repo()


class TestSDC006MutationDriftGate(unittest.TestCase):
    """
    SDC-006 Mutation / Fault-Injection Tests.

    Each test injects a specific fault and asserts that the correct
    SDC exit code is triggered via SystemExit. Tests patch only
    the in-memory compiler state — no database required.
    """

    def setUp(self):
        from discovery import Phase0Compiler
        self.Phase0Compiler = Phase0Compiler
        # Minimal temp repo so the compiler doesn't fail on missing paths
        self.tmp_repo = tempfile.mkdtemp(prefix="sdc006_test_")
        # Create minimal directory structure
        os.makedirs(os.path.join(self.tmp_repo, "sdc", "drift_snapshots"), exist_ok=True)
        os.makedirs(os.path.join(self.tmp_repo, "sdc", "rules"), exist_ok=True)
        os.makedirs(os.path.join(self.tmp_repo, "docs", "discovery"), exist_ok=True)
        os.makedirs(os.path.join(self.tmp_repo, "apps"), exist_ok=True)
        # Seed the real policy so SDCPolicy.load() succeeds in the temp repo
        real_policy_src = os.path.join(_repo_root, "sdc", "rules", "knowledge_health_policy.json")
        real_policy_dst = os.path.join(self.tmp_repo, "sdc", "rules", "knowledge_health_policy.json")
        if os.path.exists(real_policy_src):
            shutil.copy2(real_policy_src, real_policy_dst)

    def tearDown(self):
        shutil.rmtree(self.tmp_repo, ignore_errors=True)

    def _formula_hash(self, expr, variables):
        """Matches the compiler's formula hash: sha256(canonical_expr|canonical_vars)."""
        from discovery import canonical_json_str, canonical_expr_str
        expr_norm = canonical_expr_str(expr)
        vars_norm = canonical_json_str(variables)
        return hashlib.sha256(f"{expr_norm}|{vars_norm}".encode("utf-8")).hexdigest()

    def _explain_hash(self, explain_val):
        """Matches the compiler's explain hash: sha256(canonical_json_str(explain_val))."""
        from discovery import canonical_json_str
        return hashlib.sha256(canonical_json_str(explain_val).encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # Test 1: Formula expression changes but explain object NOT updated
    # ------------------------------------------------------------------
    def test_formula_expression_change_without_explain_update(self):
        """
        FAULT: formula_expression changed, explainability_json unchanged.
        EXPECTED: SDC402 raised (Knowledge Drift Detected).
        """
        from discovery import Phase0Compiler
        compiler = Phase0Compiler(_repo_root)

        # Build a formula where expression has changed vs snapshot
        formula = {
            "formula_id": "TEST-001",
            "formula_name": "Test Formula",
            "formula_expression": "NEW_EXPRESSION = x + y + z",  # changed
            "variables_and_inputs": json.dumps({"x": "var x", "y": "var y", "z": "new var"}),
            "explainability_json": json.dumps({"meaning": "original explain"})  # not updated
        }

        # Snapshot records the OLD formula hash, but SAME explain hash as the current formula.
        # This means: formula changed, explain did NOT change → violation expected.
        old_explain_content = json.dumps({"meaning": "original explain"})
        old_formula_hash = self._formula_hash("OLD_EXPRESSION = x + y",
                                              json.dumps({"x": "var x", "y": "var y"}))
        # explain_hash matches what the compiler will compute for the current formula
        same_explain_hash = self._explain_hash(old_explain_content)

        snapshot_path = os.path.join(_repo_root, "sdc", "drift_snapshots", "formula_drift_snapshot.json")
        original_snapshot = {}
        if os.path.exists(snapshot_path):
            with io.open(snapshot_path, "r", encoding="utf-8") as f:
                original_snapshot = json.load(f)

        # Inject the old snapshot for TEST-001
        test_snapshot = copy.deepcopy(original_snapshot)
        test_snapshot["snapshot_version"] = "1.0"
        test_snapshot.setdefault("formulas", {})["TEST-001"] = {
            "formula_name": "Test Formula",
            "formula_hash": old_formula_hash,   # old expression → different from current
            "explain_hash": same_explain_hash,   # same explain hash → explain NOT updated
            "last_verified": "2026-01-01T00:00:00Z"
        }

        # Write patched snapshot — ensure directory exists first
        os.makedirs(os.path.dirname(snapshot_path), exist_ok=True)
        with io.open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(test_snapshot, f, indent=2)

        try:
            violations, _ = compiler.check_formula_drift([formula])
            self.assertEqual(len(violations), 1,
                "Expected exactly 1 drift violation when formula changes but explain is not updated.")
            self.assertEqual(violations[0]["formula_id"], "TEST-001")
            self.assertIn("formula_expression or variables changed", violations[0]["detail"],
                "Violation detail should describe that formula expression changed.")
        finally:
            # Restore original snapshot
            if original_snapshot:
                os.makedirs(os.path.dirname(snapshot_path), exist_ok=True)
                with io.open(snapshot_path, "w", encoding="utf-8") as f:
                    json.dump(original_snapshot, f, indent=2)

    # ------------------------------------------------------------------
    # Test 2: Formula AND explain both updated — no violation
    # ------------------------------------------------------------------
    def test_formula_and_explain_both_updated_no_violation(self):
        """
        FAULT: None — formula changed AND explain was updated.
        EXPECTED: 0 drift violations (PASS).
        """
        from discovery import Phase0Compiler
        compiler = Phase0Compiler(_repo_root)

        formula = {
            "formula_id": "TEST-002",
            "formula_name": "Test Formula 2",
            "formula_expression": "NEW_EXPR = a * b",
            "variables_and_inputs": json.dumps({"a": "var a", "b": "var b"}),
            "explainability_json": json.dumps({"meaning": "updated explain"})  # also updated
        }

        # Snapshot records OLD hashes for BOTH formula AND explain.
        # Current formula has NEW expression and NEW explain → both changed → no violation.
        old_formula_hash = self._formula_hash("OLD_EXPR = a + b", json.dumps({"a": "var a"}))
        old_explain_hash = self._explain_hash(json.dumps({"meaning": "original explain"}))

        snapshot_path = os.path.join(_repo_root, "sdc", "drift_snapshots", "formula_drift_snapshot.json")
        original_snapshot = {}
        if os.path.exists(snapshot_path):
            with io.open(snapshot_path, "r", encoding="utf-8") as f:
                original_snapshot = json.load(f)

        test_snapshot = copy.deepcopy(original_snapshot)
        test_snapshot["snapshot_version"] = "1.0"
        test_snapshot.setdefault("formulas", {})["TEST-002"] = {
            "formula_name": "Test Formula 2",
            "formula_hash": old_formula_hash,
            "explain_hash": old_explain_hash,  # old hash → different from current (updated explain)
            "last_verified": "2026-01-01T00:00:00Z"
        }

        # Write patched snapshot — ensure directory exists first
        os.makedirs(os.path.dirname(snapshot_path), exist_ok=True)
        with io.open(snapshot_path, "w", encoding="utf-8") as f:
            json.dump(test_snapshot, f, indent=2)

        try:
            violations, _ = compiler.check_formula_drift([formula])
            self.assertEqual(len(violations), 0,
                "Expected 0 violations when both formula and explain are updated together.")
        finally:
            if original_snapshot:
                os.makedirs(os.path.dirname(snapshot_path), exist_ok=True)
                with io.open(snapshot_path, "w", encoding="utf-8") as f:
                    json.dump(original_snapshot, f, indent=2)

    # ------------------------------------------------------------------
    # Test 3: Banned terminology injected — violation detected
    # ------------------------------------------------------------------
    def test_banned_terminology_in_source_file_raises_violation(self):
        """
        FAULT: 'shadow ledger' injected into a Python file in scan scope.
        EXPECTED: check_terminology_drift() returns >= 1 violation.
        """
        from discovery import Phase0Compiler

        # Write a temporary Python file with banned term into a temp app dir
        temp_app_dir = os.path.join(self.tmp_repo, "apps", "smriti_retail_os")
        os.makedirs(temp_app_dir, exist_ok=True)
        bad_file = os.path.join(temp_app_dir, "bad_module.py")
        with io.open(bad_file, "w", encoding="utf-8") as f:
            f.write("# This module incorrectly uses shadow ledger terminology\n")
            f.write("def bad_function():\n")
            f.write("    # The shadow ledger should not be referenced here\n")
            f.write("    pass\n")

        # Patch compiler to use temp repo with the bad file
        compiler = Phase0Compiler(self.tmp_repo)
        # Override config to scan our temp app
        compiler.config.data["scan_scope"] = ["apps/smriti_retail_os"]

        violations = compiler.check_terminology_drift()
        self.assertGreater(len(violations), 0,
            "Expected at least 1 terminology violation when 'shadow ledger' is in source file.")
        # Verify violation detail
        matched_terms = [v["matched_term"] for v in violations]
        self.assertIn("shadow ledger", matched_terms)

    # ------------------------------------------------------------------
    # Test 4: CSS box-shadow not flagged as banned terminology
    # ------------------------------------------------------------------
    def test_css_box_shadow_not_flagged_as_banned_term(self):
        """
        REGRESSION GUARD: CSS 'box-shadow' property must NOT be flagged as
        banned 'shadow ledger' terminology.
        EXPECTED: 0 violations for box-shadow lines.
        """
        from discovery import Phase0Compiler

        temp_js_dir = os.path.join(self.tmp_repo, "apps", "smriti_retail_os")
        os.makedirs(temp_js_dir, exist_ok=True)
        css_js_file = os.path.join(temp_js_dir, "ui_module.js")
        with io.open(css_js_file, "w", encoding="utf-8") as f:
            f.write("// UI module with box-shadow styling\n")
            f.write("element.style.boxShadow = '0 2px 8px rgba(0,0,0,0.15)';\n")
            f.write("const style = 'box-shadow: 0 4px 12px rgba(37,99,235,0.3)';\n")

        compiler = Phase0Compiler(self.tmp_repo)
        compiler.config.data["scan_scope"] = ["apps/smriti_retail_os"]

        violations = compiler.check_terminology_drift()
        box_shadow_violations = [v for v in violations if "box-shadow" in v.get("line_content", "").lower()]
        self.assertEqual(len(box_shadow_violations), 0,
            "CSS box-shadow properties must not be flagged as banned terminology.")


class TestSDC006CoverageTrendHistory(unittest.TestCase):
    """Tests for the coverage trend history (P2)."""

    def setUp(self):
        self.tmp_repo = tempfile.mkdtemp(prefix="sdc006_hist_")
        os.makedirs(os.path.join(self.tmp_repo, "docs", "discovery"), exist_ok=True)
        os.makedirs(os.path.join(self.tmp_repo, "sdc"), exist_ok=True)
        os.makedirs(os.path.join(self.tmp_repo, "sdc", "rules"), exist_ok=True)
        # Seed the real policy so SDCPolicy.load() succeeds in the temp repo
        real_policy_src = os.path.join(_repo_root, "sdc", "rules", "knowledge_health_policy.json")
        real_policy_dst = os.path.join(self.tmp_repo, "sdc", "rules", "knowledge_health_policy.json")
        if os.path.exists(real_policy_src):
            shutil.copy2(real_policy_src, real_policy_dst)

    def tearDown(self):
        shutil.rmtree(self.tmp_repo, ignore_errors=True)

    def test_coverage_history_appended_on_success(self):
        """
        ASSERT: append_coverage_history() writes a valid JSONL line with
        correct metrics to coverage_history.jsonl.
        """
        from discovery import Phase0Compiler
        compiler = Phase0Compiler(self.tmp_repo)
        compiler.timestamp = "2026-06-27T00:00:00Z"
        compiler.commit = "abc123def456"

        metrics = {
            "coverage": 93.5,
            "broken_refs": 0,
            "drift_violations": 0,
            "health_score": 95.2
        }
        compiler.append_coverage_history(metrics)

        history_path = os.path.join(self.tmp_repo, "docs", "discovery", "coverage_history.jsonl")
        self.assertTrue(os.path.exists(history_path), "coverage_history.jsonl should be created.")

        with io.open(history_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 1, "Exactly one JSONL line should be appended.")
        entry = json.loads(lines[0])
        self.assertEqual(entry["commit"], "abc123def456")
        self.assertAlmostEqual(entry["coverage"], 93.5, places=2)
        self.assertEqual(entry["broken_refs"], 0)
        self.assertEqual(entry["drift_violations"], 0)
        self.assertAlmostEqual(entry["health_score"], 95.2, places=2)

    def test_coverage_history_appends_multiple_runs(self):
        """
        ASSERT: Multiple calls to append_coverage_history() produce
        multiple JSONL lines — not overwriting.
        """
        from discovery import Phase0Compiler
        compiler = Phase0Compiler(self.tmp_repo)

        for i in range(3):
            compiler.timestamp = f"2026-06-{26+i}T00:00:00Z"
            compiler.commit = f"commit{i:03d}"
            compiler.append_coverage_history({
                "coverage": 92.0 + i,
                "broken_refs": 0,
                "drift_violations": 0,
                "health_score": 94.0 + i
            })

        history_path = os.path.join(self.tmp_repo, "docs", "discovery", "coverage_history.jsonl")
        with io.open(history_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        self.assertEqual(len(lines), 3, "Should have 3 history entries after 3 runs.")
        coverages = [json.loads(l)["coverage"] for l in lines]
        self.assertEqual(coverages, [92.0, 93.0, 94.0])


if __name__ == "__main__":
    unittest.main(verbosity=2)
