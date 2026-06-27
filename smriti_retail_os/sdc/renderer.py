# -*- coding: utf-8 -*-
#
# @file: sdc/renderer.py
# @description: Document Renderers & Quality Gate Validation for SMRITI SDC v1.1.2 GA
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
#

import os
import json
import io
from compiler import SDCLogger, SDCException, sdc_exit

class SDCRenderer(object):
    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.discovery_dir = os.path.join(self.repo_path, "docs", "discovery")
        self.output_dir = os.path.join(self.repo_path, "docs", "generated")

    def run_rendering_and_validation(self):
        SDCLogger.info("Starting SDC Documentation Rendering & Quality Gate Verification...")

        # 1. Ensure output directory exists
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # 2. Render inventories to Markdown
        self.render_doctypes()
        self.render_apis()
        self.render_glossary()

        # 3. Quality Gate Validation Checks
        self.run_quality_gates()

    def render_doctypes(self):
        json_path = os.path.join(self.discovery_dir, "doctype_inventory.json")
        md_path = os.path.join(self.output_dir, "doctype_inventory.md")

        if not os.path.exists(json_path):
            raise SDCException("SDC201", f"Cannot render: doctype_inventory.json not found.")

        with io.open(json_path, "r", encoding="utf-8") as f:
            ir = json.load(f)

        lines = [
            u"# SMRITI Custom DocType Inventory",
            u"",
            f"* **Compiler Version:** {ir.get('compiler_version')}",
            f"* **Snapshot Commit:** `{ir.get('repository_commit')}`",
            f"* **Compiled At:** {ir.get('generated_at')}",
            u"",
            u"## Custom DocTypes List",
            u""
        ]

        for dt in ir.get("data", []):
            lines.append(f"### {dt['doctype_name']}")
            lines.append(f"* **Artifact ID:** `{dt['artifact_id']}`")
            lines.append(f"* **Schema Origin:** `{dt['schema_path']}`")
            lines.append(f"* **Evidence Type:** `{dt['evidence_type']}`")
            lines.append(u"")
            lines.append(u"| Fieldname | Label | Fieldtype | Mandatory |")
            lines.append(u"| :--- | :--- | :--- | :--- |")
            for f in dt.get("fields", []):
                lines.append(f"| {f['fieldname']} | {f['label']} | {f['fieldtype']} | {f['mandatory']} |")
            lines.append(u"")

        with io.open(md_path, "w", encoding="utf-8") as f:
            f.write(u"\n".join(lines))
        SDCLogger.info(f"Rendered Markdown to: {md_path}")

    def render_apis(self):
        json_path = os.path.join(self.discovery_dir, "api_inventory.json")
        md_path = os.path.join(self.output_dir, "api_inventory.md")

        if not os.path.exists(json_path):
            raise SDCException("SDC201", f"Cannot render: api_inventory.json not found.")

        with io.open(json_path, "r", encoding="utf-8") as f:
            ir = json.load(f)

        lines = [
            u"# SMRITI Whitelisted API Reference",
            u"",
            f"* **Compiler Version:** {ir.get('compiler_version')}",
            f"* **Snapshot Commit:** `{ir.get('repository_commit')}`",
            f"* **Compiled At:** {ir.get('generated_at')}",
            u"",
            u"## Whitelisted Methods",
            u""
        ]

        for api in ir.get("data", []):
            lines.append(f"### `{api['method']}`")
            lines.append(f"* **Artifact ID:** `{api['artifact_id']}`")
            lines.append(f"* **Source Reference:** `{api['source_file']}`")
            lines.append(f"* **Arguments:** {', '.join(api.get('arguments', []))}")
            if api.get("db_references"):
                lines.append(f"* **Database References:** {', '.join(api['db_references'])}")
            lines.append(f"* **Evidence Type:** `{api['evidence_type']}`")
            lines.append(u"")

        with io.open(md_path, "w", encoding="utf-8") as f:
            f.write(u"\n".join(lines))
        SDCLogger.info(f"Rendered Markdown to: {md_path}")

    def render_glossary(self):
        json_path = os.path.join(self.discovery_dir, "business_dictionary.json")
        md_path = os.path.join(self.output_dir, "business_dictionary.md")

        if not os.path.exists(json_path):
            raise SDCException("SDC201", f"Cannot render: business_dictionary.json not found.")

        with io.open(json_path, "r", encoding="utf-8") as f:
            ir = json.load(f)

        lines = [
            u"# SMRITI Business Dictionary Glossary",
            u"",
            f"* **Compiler Version:** {ir.get('compiler_version')}",
            f"* **Snapshot Commit:** `{ir.get('repository_commit')}`",
            f"* **Compiled At:** {ir.get('generated_at')}",
            u"",
            u"## Glossary Terms",
            u""
        ]

        for term in ir.get("data", []):
            lines.append(f"### {term['term_name']} (`{term['term_id']}`)")
            lines.append(f"* **Artifact ID:** `{term['artifact_id']}`")
            lines.append(f"* **Category:** `{term['term_category']}`")
            lines.append(f"* **Definition:** {term['definition']}")
            lines.append(f"* **Hinglish Definition:** *{term['hinglish_definition']}*")
            if term.get("term_aliases"):
                lines.append(f"* **Aliases:** {', '.join(term['term_aliases'])}")
            if term.get("manual_reference"):
                lines.append(f"* **Manual Reference:** `{term['manual_reference']}`")
            lines.append(u"")

        with io.open(md_path, "w", encoding="utf-8") as f:
            f.write(u"\n".join(lines))
        SDCLogger.info(f"Rendered Glossary to: {md_path}")

    def run_quality_gates(self):
        """Enforces all Quality Gate criteria defined in SDC v1.1.2 GA."""
        SDCLogger.info("Executing Quality Gate Verification...")

        # A. Check Artifact ID Uniqueness & Provenance
        artifact_ids = set()
        
        inventories = ["doctype_inventory.json", "field_inventory.json", "api_inventory.json", "business_dictionary.json", "dependency_graph.json"]
        for inv in inventories:
            path = os.path.join(self.discovery_dir, inv)
            if not os.path.exists(path):
                raise SDCException("SDC201", f"Missing inventory file required for Quality Gate validation: {inv}")
            
            with io.open(path, "r", encoding="utf-8") as f:
                ir = json.load(f)
            
            # Verify Provenance header presence
            prov = ir.get("provenance")
            if not prov or "artifact_id" not in prov:
                raise SDCException("SDC401", f"Quality Gate Failed: Missing provenance metadata in {inv}")
            
            p_id = prov["artifact_id"]
            if p_id in artifact_ids:
                raise SDCException("SDC401", f"Quality Gate Failed: Duplicate Artifact ID found: {p_id}")
            artifact_ids.add(p_id)

            # Check individual records inside data
            data = ir.get("data", [])
            if isinstance(data, list):
                for record in data:
                    if isinstance(record, dict) and "artifact_id" in record:
                        r_id = record["artifact_id"]
                        if r_id in artifact_ids:
                            raise SDCException("SDC401", f"Quality Gate Failed: Duplicate Artifact ID found: {r_id}")
                        artifact_ids.add(r_id)

        SDCLogger.info("Artifact ID uniqueness checks passed successfully.")

        # B. Dependency Graph Cycle Detection
        self.detect_graph_cycles()

    def detect_graph_cycles(self):
        """Validates that there are no circular loops in the dependency graph."""
        graph_path = os.path.join(self.discovery_dir, "dependency_graph.json")
        with io.open(graph_path, "r", encoding="utf-8") as f:
            graph_data = json.load(f)

        data = graph_data.get("data", {})
        nodes = [n["id"] for n in data.get("nodes", [])]
        edges = data.get("edges", [])

        # Build adjacency list
        adj = {n: [] for n in nodes}
        for e in edges:
            if e.get("relation") == "RELATED_TO":
                continue
            source = e["source"]
            target = e["target"]
            if source in adj:
                adj[source].append(target)

        # Depth-First Search for cycle detection
        visited = {n: 0 for n in nodes} # 0=unvisited, 1=visiting, 2=visited

        def dfs(node):
            visited[node] = 1 # visiting
            for neighbor in adj.get(node, []):
                if neighbor not in visited:
                    continue
                if visited[neighbor] == 1:
                    return True # Cycle found!
                if visited[neighbor] == 0:
                    if dfs(neighbor):
                        return True
            visited[node] = 2 # visited
            return False

        for node in nodes:
            if visited[node] == 0:
                if dfs(node):
                    raise SDCException("SDC301", "Quality Gate Failed: Dependency graph contains a circular reference loop.")

        SDCLogger.info("Dependency graph cycle checks passed successfully (DAG verified).")
        SDCLogger.info("Quality Gate Verification: ALL CHECKS PASSED.")


if __name__ == "__main__":
    import sys
    repo_root = "d:\\Smriti_Retail_OS"
    if len(sys.argv) > 1:
        repo_root = sys.argv[1]

    try:
        renderer = SDCRenderer(repo_root)
        renderer.run_rendering_and_validation()
        sdc_exit("SDC000", "Documentation rendering and quality gates passed.")
    except SDCException as se:
        sdc_exit(se.code, str(se))
    except Exception as e:
        sdc_exit("SDC401", f"Unhandled Quality Gate compiler exception: {str(e)}")
