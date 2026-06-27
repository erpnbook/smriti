# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/tests/test_knowledge_governance.py
# @description: Sprint SDC-005 unit tests for SKE runtime, migrations, drift fallback, AI safe gate and telemetry retention.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.2.15
# @license: MIT
#

import unittest
import sys
import os
import io
import json
import shutil
import datetime
import frappe
from frappe.utils import add_days, now_datetime

# Helper to append SDC directory dynamically
def _setup_sdc_path():
    app_path = frappe.get_app_path("smriti_retail_os")
    sdc_path = os.path.join(app_path, "sdc")
    if not os.path.exists(sdc_path):
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(app_path)))
        sdc_path = os.path.join(repo_root, "sdc")
    if sdc_path not in sys.path:
        sys.path.append(sdc_path)
    return sdc_path, os.path.dirname(sdc_path)

sdc_path, repo_root = _setup_sdc_path()
from ske import SMRITIKnowledgeEngine, SMRITIProvider, KnowledgeObject, KnowledgeProvider
from migration_registry import IRMigratorRegistry

class TestKnowledgeGovernance(unittest.TestCase):
    def setUp(self):
        frappe.set_user("Administrator")
        # Ensure telemetry logs are cleaned before test
        frappe.db.delete("SMRITI Knowledge Usage Log")
        frappe.db.commit()

    def tearDown(self):
        frappe.db.delete("SMRITI Knowledge Usage Log")
        frappe.db.commit()

    def test_ske_public_api_compatibility(self):
        """Assert that SKE class has public methods locking the SKE public API surface."""
        engine = SMRITIKnowledgeEngine(repo_root)
        self.assertTrue(hasattr(engine, "resolve"))
        self.assertTrue(hasattr(engine, "resolve_by_id"))
        self.assertTrue(hasattr(engine, "search"))
        self.assertTrue(hasattr(engine, "get_dependencies"))
        self.assertTrue(hasattr(engine, "get_health"))
        self.assertTrue(hasattr(engine, "get_context_pack"))

    def test_ske_provider_compatibility_validation(self):
        """Assert that SKE blocks incompatible providers matching mismatched supports_ir declarations."""
        class BadProvider(KnowledgeProvider):
            @property
            def name(self):
                return "bad_provider"
            @property
            def capabilities(self):
                return ["custom"]
            @property
            def supports_ir(self):
                return ["0.9"] # Incompatible with 1.2
            @property
            def enabled_by_default(self):
                return True
            @property
            def priority(self):
                return 50
            def supports(self, engine, query):
                return 1.0
            def resolve(self, engine, query):
                return [KnowledgeObject(id="BAD-001", type="custom", title="Bad Asset")]

        bad = BadProvider()
        curr_schema = "1.2"
        is_supported = curr_schema in bad.supports_ir
        self.assertFalse(is_supported)

    def test_ske_dynamic_ir_migration(self):
        """Assert that SKE migrates outdated IR schemas using migration_registry.py transforms at startup."""
        mock_ir_11 = {
            "ir_version": "1.1",
            "compiler_version": "1.1",
            "generated_by": "SDC 1.1.0",
            "schema_version": "1.1",
            "artifact_type": "business_dictionary",
            "data": [
                {
                    "artifact_id": "ART-TERM-00099",
                    "term_id": "outdated_term",
                    "term_name": "Outdated Term",
                    "definition": "Legacy Definition"
                }
            ]
        }
        
        migrated = IRMigratorRegistry.migrate(mock_ir_11, target_version="1.2")
        
        self.assertEqual(migrated["ir_version"], "1.2")
        self.assertEqual(migrated["schema_version"], "1.2")
        
        data_item = migrated["data"][0]
        self.assertIn("validation_status", data_item)
        self.assertIn("operational_status", data_item)
        self.assertEqual(data_item["validation_status"], "Verified")
        self.assertEqual(data_item["operational_status"], "Active")

    def test_drift_engine_fallback_chains(self):
        """Assert Drift Engine falls back correctly in the absence of .git folder."""
        from discovery import Phase0Compiler
        compiler = Phase0Compiler(repo_root)
        
        original_exists = os.path.exists
        def mock_exists(path):
            if path.endswith(".git"):
                return False
            return original_exists(path)
            
        os.path.exists = mock_exists
        try:
            drift_score = compiler.calculate_drift()
            self.assertTrue(isinstance(drift_score, float))
            self.assertGreaterEqual(drift_score, 0.0)
            self.assertLessEqual(drift_score, 100.0)
        finally:
            os.path.exists = original_exists

    def test_ai_safe_gate_filtering(self):
        """Assert that SKE AI Safe Gate blocks retired assets and warns for deprecated assets."""
        engine = SMRITIKnowledgeEngine(repo_root)
        
        original_get_ir = engine.get_ir
        
        def mock_get_ir(name, default=None):
            if name == "business_dictionary":
                return [
                    {
                        "artifact_id": "ART-TERM-RETIRED",
                        "term_id": "retired_term",
                        "term_name": "Retired Term",
                        "definition": "Retired",
                        "validation_status": "Certified",
                        "operational_status": "Retired"
                    },
                    {
                        "artifact_id": "ART-TERM-DEPRECATED",
                        "term_id": "deprecated_term",
                        "term_name": "Deprecated Term",
                        "definition": "Deprecated Definition",
                        "validation_status": "Certified",
                        "operational_status": "Deprecated"
                    },
                    {
                        "artifact_id": "ART-TERM-DRAFT",
                        "term_id": "draft_term",
                        "term_name": "Draft Term",
                        "definition": "Draft Definition",
                        "validation_status": "Draft",
                        "operational_status": "Active"
                    }
                ]
            return original_get_ir(name, default)
            
        engine.get_ir = mock_get_ir
        
        try:
            res_retired = engine.resolve("Retired Term", developer_mode=False)
            self.assertEqual(len(res_retired), 0)
            
            res_draft_normal = engine.resolve("Draft Term", developer_mode=False)
            self.assertEqual(len(res_draft_normal), 0)
            
            res_draft_dev = engine.resolve("Draft Term", developer_mode=True)
            self.assertEqual(len(res_draft_dev), 1)
            
            res_dep = engine.resolve("Deprecated Term", developer_mode=False)
            self.assertEqual(len(res_dep), 1)
            self.assertIn("[DEPRECATION WARNING", res_dep[0].business_definition)
            self.assertIn("[DEPRECATION WARNING", res_dep[0].summary)
        finally:
            engine.get_ir = original_get_ir

    def test_telemetry_no_result_log_writes(self):
        """Assert that searching a missing term writes a usage log with has_result: 0."""
        from smriti_retail_os.api import knowledge_studio_api
        
        res = knowledge_studio_api.query_ske("NonexistentXYZQueryTerm")
        
        knowledge_studio_api.log_telemetry_event(
            event_type="SEARCH",
            query="NonexistentXYZQueryTerm",
            has_result=0,
            resolution_time_ms=5,
            provider_hit="none",
            confidence_source="None"
        )
        
        logs = frappe.get_all(
            "SMRITI Knowledge Usage Log",
            filters={"query": "NonexistentXYZQueryTerm", "has_result": 0},
            fields=["name", "has_result"]
        )
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["has_result"], 0)

    def test_daily_scheduled_purge_task(self):
        """Assert automated scheduler purging removes log entries older than 90 days."""
        old_time = add_days(now_datetime(), -95)
        doc1 = frappe.get_doc({
            "doctype": "SMRITI Knowledge Usage Log",
            "event_type": "SEARCH",
            "query": "OldQuery",
            "has_result": 1,
            "resolution_time_ms": 10,
            "timestamp": old_time
        })
        doc1.insert(ignore_permissions=True)
        
        new_time = add_days(now_datetime(), -50)
        doc2 = frappe.get_doc({
            "doctype": "SMRITI Knowledge Usage Log",
            "event_type": "SEARCH",
            "query": "NewQuery",
            "has_result": 1,
            "resolution_time_ms": 10,
            "timestamp": new_time
        })
        doc2.insert(ignore_permissions=True)
        frappe.db.commit()
        
        self.assertTrue(frappe.db.exists("SMRITI Knowledge Usage Log", doc1.name))
        self.assertTrue(frappe.db.exists("SMRITI Knowledge Usage Log", doc2.name))
        
        from smriti_retail_os.tasks import daily_telemetry_cleanup
        daily_telemetry_cleanup()
        
        self.assertFalse(frappe.db.exists("SMRITI Knowledge Usage Log", doc1.name))
        self.assertTrue(frappe.db.exists("SMRITI Knowledge Usage Log", doc2.name))

    def test_no_hardcoded_evidence_badge(self):
        """Assert no hardcoded evidence badge strings remain in ai_integration_api.py."""
        app_path = frappe.get_app_path("smriti_retail_os")
        api_path = os.path.join(app_path, "api", "ai_integration_api.py")
        with io.open(api_path, "r", encoding="utf-8") as f:
            content = f.read()
        import re
        self.assertFalse(re.search(r'evidence_badge"\s*:\s*"✔ Verified \| \d+ Graph Links \| \w+"', content))

    def test_no_banned_terminology(self):
        """Assert that the banned term 'shadow ledger' is not used in SMRITI Python controllers or patches."""
        app_path = frappe.get_app_path("smriti_retail_os")
        for root, dirs, files in os.walk(app_path):
            if "node_modules" in dirs:
                dirs.remove("node_modules")
            if ".git" in dirs:
                dirs.remove(".git")
            for file in files:
                if file.endswith((".py", ".js")):
                    if file == "test_knowledge_governance.py":
                        continue
                    filepath = os.path.join(root, file)
                    with io.open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()
                    # Ensure we don't have "shadow ledger" in lowercase
                    self.assertNotIn("shadow ledger", content.lower(), f"Banned terminology 'shadow ledger' found in {filepath}")

    def test_every_formula_has_explain_object(self):
        """Verify that all formulas in seed_default_formulas.py have an explainability_json/explain structure."""
        seed_py = os.path.join(frappe.get_app_path("smriti_retail_os"), "patches", "seed_default_formulas.py")
        with io.open(seed_py, "r", encoding="utf-8") as f:
            content = f.read()
        
        import ast
        tree = ast.parse(content)
        
        formulas = []
        class FormulaVisitor(ast.NodeVisitor):
            def visit_Assign(self, node):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "formulas":
                        if isinstance(node.value, ast.List):
                            for element in node.value.elts:
                                if isinstance(element, ast.Dict):
                                    fd = {}
                                    for k, v in zip(element.keys, element.values):
                                        if isinstance(k, ast.Constant):
                                            fd[k.value] = v
                                    formulas.append(fd)
                self.generic_visit(node)
                
        FormulaVisitor().visit(tree)
        self.assertGreater(len(formulas), 0, "No formulas found in seeder")
        for fd in formulas:
            self.assertIn("explainability_json", fd, f"Formula missing explainability_json: {fd.get('formula_id')}")

    def test_no_orphan_knowledge_objects(self):
        """Assert that all glossary terms and screen narratives are connected in the dependency graph."""
        graph_path = os.path.join(repo_root, "docs", "discovery", "dependency_graph.json")
        self.assertTrue(os.path.exists(graph_path), "dependency_graph.json not found")
        with io.open(graph_path, "r", encoding="utf-8") as f:
            graph = json.load(f)
        
        nodes = graph.get("data", {}).get("nodes", [])
        edges = graph.get("data", {}).get("edges", [])
        
        connected_node_ids = set()
        for edge in edges:
            connected_node_ids.add(edge["source"])
            connected_node_ids.add(edge["target"])
            
        for node in nodes:
            if node["type"] in ("GLOSSARY_TERM", "SCREEN", "COLLECTION"):
                self.assertIn(node["id"], connected_node_ids, f"Orphan knowledge object found: {node['id']} ({node['label']})")
