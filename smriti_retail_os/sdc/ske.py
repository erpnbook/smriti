# -*- coding: utf-8 -*-
#
# @file: sdc/ske.py
# @description: SMRITI Knowledge Engine (SKE) Runtime Library
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.1.2-GA
#

import os
import json
import hashlib
import io
import sys
from compiler import SDCLogger

class KnowledgeObject(object):
    __slots__ = ('id', 'type', 'title', 'summary', 'business_definition',
                 'technical_definition', 'dependencies', 'evidence',
                 'related_objects', 'examples', 'references', 'relations')

    def __init__(self, **kwargs):
        for slot in self.__slots__:
            super(KnowledgeObject, self).__setattr__(slot, kwargs.get(slot, None) or [])

    def __setattr__(self, key, value):
        raise AttributeError("KnowledgeObject is immutable and cannot be modified after creation.")

    def __delattr__(self, key):
        raise AttributeError("KnowledgeObject is immutable and cannot be modified after creation.")

    def to_dict(self):
        res = {}
        for slot in self.__slots__:
            val = getattr(self, slot)
            res[slot] = val
        return res


class KnowledgeProvider(object):
    def priority(self):
        return 50

    def capabilities(self):
        return []

    def supports(self, engine, query):
        """Returns relevance score between 0.0 and 1.0."""
        raise NotImplementedError()

    def resolve(self, engine, query):
        """Returns a list of KnowledgeObject instances."""
        raise NotImplementedError()


class GlossaryProvider(KnowledgeProvider):
    def priority(self):
        return 100

    def capabilities(self):
        return ["glossary"]

    def supports(self, engine, query):
        clean_q = engine.clean_query(query)
        for term in self.terms(engine):
            if clean_q == term.get("term_id", "").lower() or clean_q == term.get("term_name", "").lower():
                return 1.0
            if clean_q in [a.lower() for a in term.get("term_aliases", [])]:
                return 0.9
        if "woc" in clean_q or "psa" in clean_q or "psv" in clean_q or "pdt" in clean_q or "glossary" in clean_q:
            return 0.8
        return 0.1

    def terms(self, engine):
        return engine.get_ir("business_dictionary", [])

    def resolve(self, engine, query):
        results = []
        clean_q = engine.clean_query(query)
        for term in self.terms(engine):
            tid = term.get("term_id", "").lower()
            tname = term.get("term_name", "").lower()
            aliases = [a.lower() for a in term.get("term_aliases", [])]
            is_match = (
                clean_q == tid or
                clean_q == tname or
                any(clean_q == a for a in aliases) or
                clean_q in tname or
                tid in clean_q
            )
            if is_match:
                examples = []
                for f in term.get("faq", []):
                    examples.append(f"FAQ Q: {f['q']} | A: {f['a']}")
                for m in term.get("common_mistakes", []):
                    examples.append(f"Common Mistake: {m['mistake']} | Action: {m['a']}")

                relations = []
                for rt in term.get("related_terms", []):
                    relations.append(("RELATED_TO", rt))
                for rf in term.get("related_formulas", []):
                    relations.append(("FORMULA_OF", rf))

                evidence = [{
                    "artifact_id": term.get("artifact_id", "ART-TERM-00000"),
                    "type": "glossary_term",
                    "source_file": "apps/smriti_retail_os/smriti_retail_os/patches/seed_default_terms.py",
                    "line": 23,
                    "checksum": term.get("checksum", ""),
                    "confidence": "Verified"
                }]

                obj = KnowledgeObject(
                    id=term.get("artifact_id"),
                    type="glossary_term",
                    title=term.get("term_name"),
                    summary=term.get("hinglish_definition"),
                    business_definition=term.get("definition"),
                    technical_definition=f"Glossary term category: {term.get('term_category')}",
                    dependencies=term.get("related_terms", []),
                    evidence=evidence,
                    examples=examples,
                    references=[term.get("manual_reference", ""), term.get("training_reference", "")],
                    relations=relations
                )
                results.append(obj)
        return results


class FieldProvider(KnowledgeProvider):
    def priority(self):
        return 80

    def capabilities(self):
        return ["field"]

    def supports(self, engine, query):
        clean_q = engine.clean_query(query)
        for field in self.fields(engine):
            fname = field.get("fieldname", "").lower()
            if clean_q == fname or clean_q == fname.replace("custom_", "") or clean_q == field.get("label", "").lower():
                return 1.0
            if clean_q in fname or clean_q in field.get("label", "").lower():
                return 0.8
        return 0.1

    def fields(self, engine):
        return engine.get_ir("field_inventory", [])

    def resolve(self, engine, query):
        results = []
        clean_q = engine.clean_query(query)
        for field in self.fields(engine):
            fname = field.get("fieldname", "").lower()
            label = field.get("label", "").lower()
            is_match = (
                clean_q == fname or 
                clean_q == fname.replace("custom_", "") or 
                clean_q == label or
                clean_q in fname or
                clean_q in label
            )
            if is_match:
                evidence = [{
                    "artifact_id": field.get("artifact_id"),
                    "type": "field",
                    "source_file": field.get("source_file"),
                    "line": field.get("source_line"),
                    "checksum": field.get("checksum"),
                    "confidence": "Verified"
                }]
                obj = KnowledgeObject(
                    id=field.get("artifact_id"),
                    type="field",
                    title=field.get("label"),
                    summary=f"Custom field '{field.get('fieldname')}' extending standard DocType '{field.get('target_doctype')}'",
                    business_definition=f"Operational custom field tracking {field.get('label')}.",
                    technical_definition=f"DocType: {field.get('target_doctype')} | Fieldname: {field.get('fieldname')} | Fieldtype: {field.get('fieldtype')}",
                    dependencies=[field.get("target_doctype")],
                    evidence=evidence,
                    relations=[("EXTENDS", field.get("target_doctype"))]
                )
                results.append(obj)
        return results


class DocTypeProvider(KnowledgeProvider):
    def priority(self):
        return 70

    def capabilities(self):
        return ["doctype"]

    def supports(self, engine, query):
        clean_q = engine.clean_query(query)
        for dt in self.doctypes(engine):
            dt_name = dt.get("doctype_name", "").lower()
            if clean_q == dt_name or clean_q in dt_name:
                return 0.9
        # Check virtual doctypes in graph
        graph = engine.get_ir("dependency_graph", {}).get("data", {})
        for node in graph.get("nodes", []):
            if node.get("type") == "DOCTYPE_VIRTUAL":
                if clean_q == node.get("label", "").lower():
                    return 0.9
        if "doctype" in clean_q or "schema" in clean_q:
            return 0.7
        return 0.1

    def doctypes(self, engine):
        return engine.get_ir("doctype_inventory", [])

    def resolve(self, engine, query):
        results = []
        clean_q = engine.clean_query(query)
        
        # 1. Custom DocTypes
        for dt in self.doctypes(engine):
            dt_name = dt.get("doctype_name", "").lower()
            if clean_q == dt_name or clean_q in dt_name or dt_name in clean_q:
                fields_summary = [f"{f['fieldname']} ({f['fieldtype']})" for f in dt.get("fields", [])[:5]]
                tech_def = f"Schema Source: {dt.get('schema_path')}\nFields:\n" + "\n".join(
                    [f" - {f['fieldname']} ({f['fieldtype']}){' (Mandatory)' if f['mandatory'] else ''}" for f in dt.get("fields", [])]
                )
                evidence = [{
                    "artifact_id": dt.get("artifact_id"),
                    "type": "doctype",
                    "source_file": dt.get("schema_path"),
                    "line": 1,
                    "checksum": dt.get("checksum"),
                    "confidence": "Verified"
                }]
                obj = KnowledgeObject(
                    id=dt.get("artifact_id"),
                    type="doctype",
                    title=dt.get("doctype_name"),
                    summary=f"SMRITI Custom DocType containing {len(dt.get('fields', []))} fields: {', '.join(fields_summary)}...",
                    business_definition=f"SMRITI database transaction schema for {dt.get('doctype_name')}.",
                    technical_definition=tech_def,
                    evidence=evidence
                )
                results.append(obj)

        # 2. Virtual DocTypes from Graph
        graph = engine.get_ir("dependency_graph", {})
        for node in graph.get("nodes", []):
            if node.get("type") == "DOCTYPE_VIRTUAL":
                label = node.get("label", "").lower()
                if clean_q == label or clean_q in label or label in clean_q:
                    # Check if already added
                    if not any(r.title.lower() == node["label"].lower() for r in results):
                        evidence = [{
                            "artifact_id": node.get("id"),
                            "type": "doctype_virtual",
                            "source_file": "docs/discovery/dependency_graph.json",
                            "line": 1,
                            "checksum": "",
                            "confidence": "Verified"
                        }]
                        obj = KnowledgeObject(
                            id=node.get("id"),
                            type="doctype",
                            title=node.get("label"),
                            summary=f"Standard ERPNext DocType '{node.get('label')}' integrated with SMRITI.",
                            business_definition=f"Standard DocType master record for {node.get('label')}.",
                            technical_definition=f"Type: Virtual DocType Node | ID: {node.get('id')}",
                            evidence=evidence
                        )
                        results.append(obj)
        return results


class APIProvider(KnowledgeProvider):
    def priority(self):
        return 60

    def capabilities(self):
        return ["api"]

    def supports(self, engine, query):
        clean_q = engine.clean_query(query)
        if "api" in clean_q or "whitelist" in clean_q or "method" in clean_q:
            return 0.8
        for api in self.apis(engine):
            method = api.get("method", "").lower()
            if clean_q in method:
                return 0.9
        return 0.1

    def apis(self, engine):
        return engine.get_ir("api_inventory", [])

    def resolve(self, engine, query):
        results = []
        clean_q = engine.clean_query(query)
        for api in self.apis(engine):
            method = api.get("method", "").lower()
            method_short = method.split(".")[-1]
            if clean_q == method_short or clean_q in method or method_short in clean_q:
                evidence = [{
                    "artifact_id": api.get("artifact_id"),
                    "type": "api",
                    "source_file": api.get("source_file"),
                    "line": 1,
                    "checksum": api.get("checksum"),
                    "confidence": "Verified"
                }]
                relations = []
                for ref_dt in api.get("db_references", []):
                    relations.append(("USES", ref_dt))
                obj = KnowledgeObject(
                    id=api.get("artifact_id"),
                    type="api",
                    title=api.get("method"),
                    summary=f"Frappe whitelisted API method defined in: {api.get('source_file')}",
                    business_definition=f"Python whitelisted endpoint for store operations.",
                    technical_definition=f"Method: {api.get('method')}\nArguments: {', '.join(api.get('arguments', []))}\nDatabase References: {', '.join(api.get('db_references', []))}",
                    dependencies=api.get("db_references", []),
                    evidence=evidence,
                    relations=relations
                )
                results.append(obj)
        return results


class FormulaProvider(KnowledgeProvider):
    def priority(self):
        return 90

    def capabilities(self):
        return ["formula"]

    def supports(self, engine, query):
        clean_q = engine.clean_query(query)
        if "formula" in clean_q or "calculation" in clean_q or "equation" in clean_q or "math" in clean_q or "cover" in clean_q or "velocity" in clean_q:
            return 0.9
        return 0.1

    def resolve(self, engine, query):
        results = []
        clean_q = engine.clean_query(query)
        formulas = [
            {
                "id": "INV-001",
                "title": "Sales Velocity",
                "expression": "Sales Velocity = Total Sold Quantity / Lookback Days (standard 30)",
                "explanation": "Average units sold daily or weekly during lookback duration.",
                "confidence": "Verified"
            },
            {
                "id": "INV-002",
                "title": "Weeks of Cover (WOC)",
                "expression": "WOC = Current Stock Quantity / Weekly Sales Velocity",
                "explanation": "Estimates how many weeks stock will last before running out.",
                "confidence": "Verified"
            },
            {
                "id": "INV-003",
                "title": "Dead Stock Score",
                "expression": "Dead Stock = Inactive Days (>90) * Positive Inventory Value",
                "explanation": "Calculates priority metrics for stock liquidation and discounting.",
                "confidence": "Verified"
            }
        ]

        for f in formulas:
            if clean_q in f["title"].lower() or clean_q in f["id"].lower() or "formula" in clean_q or "cover" in clean_q or "velocity" in clean_q:
                evidence = [{
                    "artifact_id": f["id"],
                    "type": "formula",
                    "source_file": "sdc/ske.py",
                    "line": 340,
                    "checksum": hashlib.sha256(f["expression"].encode("utf-8")).hexdigest(),
                    "confidence": "Verified"
                }]
                obj = KnowledgeObject(
                    id=f["id"],
                    type="formula",
                    title=f["title"],
                    summary=f["expression"],
                    business_definition=f["explanation"],
                    technical_definition=f"Mathematical formula: {f['expression']}",
                    evidence=evidence
                )
                results.append(obj)
        return results


class ScreenProvider(KnowledgeProvider):
    def priority(self):
        return 95

    def capabilities(self):
        return ["screen"]

    def supports(self, engine, query):
        clean_q = engine.clean_query(query)
        for screen in self.screens(engine):
            s_id = screen.get("screen_id", "").lower()
            title = screen.get("title", "").lower()
            if clean_q == s_id or clean_q == title or clean_q in s_id or clean_q in title:
                return 1.0
        return 0.1

    def screens(self, engine):
        return engine.get_ir("screen_inventory", [])

    def resolve(self, engine, query):
        results = []
        clean_q = engine.clean_query(query)
        
        # Check candidates from search index
        candidates = set()
        if hasattr(engine, "search_index"):
            tokens = clean_q.split()
            for t in tokens:
                if t in engine.search_index:
                    candidates.update(engine.search_index[t])

        for screen in self.screens(engine):
            s_id = screen.get("screen_id", "").lower()
            title = screen.get("title", "").lower()
            art_id = f"ART-SCREEN-{screen['screen_id'].upper()}"
            
            is_match = (
                clean_q == s_id or
                clean_q == title or
                clean_q in s_id or
                clean_q in title or
                art_id in candidates
            )
            
            if is_match:
                evidence = [{
                    "artifact_id": art_id,
                    "type": "screen",
                    "source_file": "sdc/rules/screen_narratives.json",
                    "line": 1,
                    "checksum": "",
                    "confidence": "Verified"
                }]
                
                beginner = screen.get("beginner", {})
                power = screen.get("power_user", {})
                dev = screen.get("developer", {})
                
                bus_def = f"Purpose: {beginner.get('purpose')}\nHow to use: {beginner.get('how_to_use')}\nExample: {beginner.get('example')}"
                tech_def = f"Associated DocType: {screen.get('doctype')}\nFields: {', '.join(screen.get('fields', []))}\nAPIs: {', '.join(screen.get('apis', []))}\nReports: {', '.join(screen.get('reports', []))}\nLabels: {', '.join(screen.get('labels', []))}"
                
                examples = [f"Beginner Example: {beginner.get('example')}", f"Power User Workflow: {power.get('workflow')}"]
                
                relations = [("USES", screen.get("doctype"))]
                for api in screen.get("apis", []):
                    relations.append(("CALLS", api))
                
                obj = KnowledgeObject(
                    id=art_id,
                    type="screen",
                    title=screen.get("title"),
                    summary=f"SMRITI Screen - {screen.get('title')} ({screen.get('route')})",
                    business_definition=bus_def,
                    technical_definition=tech_def,
                    dependencies=[screen.get("doctype")],
                    evidence=evidence,
                    examples=examples,
                    references=[dev.get("manual_reference", ""), dev.get("training_reference", "")],
                    relations=relations
                )
                results.append(obj)
        return results


class Resolver(object):
    def score(self, query):
        raise NotImplementedError()

    def resolve(self, engine, query):
        raise NotImplementedError()


class LookupResolver(Resolver):
    def score(self, query):
        q = query.lower()
        if q.startswith("explain") or q.startswith("what is") or len(q.split()) <= 3:
            return 90
        return 10

    def resolve(self, engine, query):
        results = []
        for p in engine.providers.values():
            results.extend(p.resolve(engine, query))
        return results


class DependencyResolver(Resolver):
    def score(self, query):
        q = query.lower()
        if "where" in q or "used" in q or "dependency" in q or "depends" in q or "uses" in q:
            return 95
        return 10

    def resolve(self, engine, query):
        term = engine.clean_query(query)
        q_term = term.lower()
        
        start_nodes = []
        for p in engine.providers.values():
            objs = p.resolve(engine, q_term)
            if objs:
                start_nodes.extend(objs)

        if not start_nodes:
            return []

        results = []
        graph = engine.get_ir("dependency_graph", {})
        edges = graph.get("edges", [])
        nodes = graph.get("nodes", [])

        for target_obj in start_nodes:
            target_art_id = target_obj.id
            for edge in edges:
                # 1. Inbound dependencies (who uses/depends on target_obj)
                if edge["target"] == target_art_id:
                    src_node = next((n for n in nodes if n["id"] == edge["source"]), None)
                    src_label = src_node["label"] if src_node else edge["source"]
                    
                    edge_path = [src_label, edge["relation"], target_obj.title]
                    evidence = list(target_obj.evidence) + [{
                        "artifact_id": edge["source"],
                        "type": "dependency_edge",
                        "edge_path": edge_path,
                        "source_file": "docs/discovery/dependency_graph.json",
                        "line": 1,
                        "checksum": "",
                        "confidence": "Verified"
                    }]
                    
                    results.append(KnowledgeObject(
                        id=edge["source"],
                        type="dependency",
                        title=f"Dependent: {src_label}",
                        summary=f"{src_label} depends on {target_obj.title} via {edge['relation']}",
                        business_definition=f"Component depending on {target_obj.title}.",
                        technical_definition=f"Edge Relation: {edge['source']} --[{edge['relation']}]--> {edge['target']}",
                        dependencies=[target_obj.title],
                        evidence=evidence,
                        relations=[(edge["relation"], target_obj.title)]
                    ))
                # 2. Outbound dependencies (what target_obj depends on/extends)
                elif edge["source"] == target_art_id:
                    tgt_node = next((n for n in nodes if n["id"] == edge["target"]), None)
                    tgt_label = tgt_node["label"] if tgt_node else edge["target"]
                    
                    edge_path = [target_obj.title, edge["relation"], tgt_label]
                    evidence = list(target_obj.evidence) + [{
                        "artifact_id": edge["target"],
                        "type": "dependency_edge",
                        "edge_path": edge_path,
                        "source_file": "docs/discovery/dependency_graph.json",
                        "line": 1,
                        "checksum": "",
                        "confidence": "Verified"
                    }]
                    
                    results.append(KnowledgeObject(
                        id=edge["target"],
                        type="dependency",
                        title=f"Dependency: {tgt_label}",
                        summary=f"{target_obj.title} depends on {tgt_label} via {edge['relation']}",
                        business_definition=f"Component that {target_obj.title} depends on.",
                        technical_definition=f"Edge Relation: {edge['source']} --[{edge['relation']}]--> {edge['target']}",
                        dependencies=[tgt_label],
                        evidence=evidence,
                        relations=[(edge["relation"], tgt_label)]
                    ))

        return results


class ImpactResolver(Resolver):
    def score(self, query):
        q = query.lower()
        if "delete" in q or "remove" in q or "breaks" in q or "impact" in q:
            return 98
        return 10

    def resolve(self, engine, query):
        term = engine.clean_query(query)
        q_term = term.lower()

        start_nodes = []
        for p in engine.providers.values():
            objs = p.resolve(engine, q_term)
            if objs:
                start_nodes.extend(objs)

        if not start_nodes:
            return []

        graph = engine.get_ir("dependency_graph", {})
        edges = graph.get("edges", [])
        nodes = graph.get("nodes", [])

        results = []
        for start_obj in start_nodes:
            target_art_id = start_obj.id
            visited = set()
            impacts = []
            
            def dfs(current_id, current_path):
                visited.add(current_id)
                for edge in edges:
                    if edge["target"] == current_id and edge["source"] not in visited:
                        src_node = next((n for n in nodes if n["id"] == edge["source"]), None)
                        src_label = src_node["label"] if src_node else edge["source"]
                        new_path = [src_label, edge["relation"]] + current_path
                        impacts.append({
                            "id": edge["source"],
                            "label": src_label,
                            "relation": edge["relation"],
                            "path": new_path
                        })
                        dfs(edge["source"], new_path)

            dfs(target_art_id, [start_obj.title])

            if not impacts:
                results.append(KnowledgeObject(
                    id=start_obj.id,
                    type="impact_analysis",
                    title=f"Impact Analysis: {start_obj.title}",
                    summary="No cascading downstream dependencies found. Safe to modify.",
                    business_definition=f"Deleting {start_obj.title} will not impact other custom components in SMRITI.",
                    technical_definition=f"Transitive dependents list: empty.",
                    evidence=start_obj.evidence
                ))
            else:
                summary_text = f"Warning: Modifying {start_obj.title} will impact {len(impacts)} downstream components: " + ", ".join([imp["label"] for imp in impacts])
                evidence = list(start_obj.evidence)
                for imp in impacts:
                    evidence.append({
                        "artifact_id": imp["id"],
                        "type": "impact_path",
                        "edge_path": imp["path"],
                        "source_file": "docs/discovery/dependency_graph.json",
                        "line": 1,
                        "checksum": "",
                        "confidence": "Verified"
                    })
                results.append(KnowledgeObject(
                    id=start_obj.id,
                    type="impact_analysis",
                    title=f"Impact Analysis: {start_obj.title}",
                    summary=summary_text,
                    business_definition=f"Cascading dependencies will break if {start_obj.title} is removed.",
                    technical_definition="Downstream impact graph traversal paths:\n" + "\n".join([f" - " + " -> ".join(imp["path"]) for imp in impacts]),
                    dependencies=[imp["label"] for imp in impacts],
                    evidence=evidence
                ))

        return results


class APITouchingResolver(Resolver):
    def score(self, query):
        q = query.lower()
        if "api" in q or "apis" in q or "touching" in q or "endpoints" in q:
            return 95
        return 10

    def resolve(self, engine, query):
        term = engine.clean_query(query)
        q_term = term.lower()

        results = []
        apis = engine.get_ir("api_inventory", [])
        for api in apis:
            matches_dt = any(q_term == ref.lower() for ref in api.get("db_references", []))
            if matches_dt or q_term in api["method"].lower():
                evidence = [{
                    "artifact_id": api["artifact_id"],
                    "type": "api",
                    "source_file": api["source_file"],
                    "line": 1,
                    "checksum": api["checksum"],
                    "confidence": "Verified"
                }]
                obj = KnowledgeObject(
                    id=api["artifact_id"],
                    type="api",
                    title=api["method"],
                    summary=f"API method '{api['method']}' touches database table/DocType.",
                    business_definition="Operational backend endpoint interacting with records.",
                    technical_definition=f"Method: {api['method']}\nArguments: {', '.join(api['arguments'])}\nReferences: {', '.join(api['db_references'])}",
                    dependencies=api["db_references"],
                    evidence=evidence,
                    relations=[("USES", ref) for ref in api["db_references"]]
                )
                results.append(obj)
        return results


class LabelsPrintingResolver(Resolver):
    def score(self, query):
        q = query.lower()
        if "label" in q or "labels" in q or "print" in q or "printing" in q:
            return 95
        return 10

    def resolve(self, engine, query):
        results = []
        clean_q = engine.clean_query(query)
        q_term = "mrp" if "mrp" in clean_q else "barcode"
        
        if "mrp" in q_term:
            evidence = [{
                "artifact_id": "ART-LABEL-00001",
                "type": "print_template",
                "source_file": "apps/smriti_retail_os/smriti_retail_os/smriti_retail_os/doctype/smriti_barcode_settings/smriti_barcode_settings.json",
                "line": 1,
                "checksum": "",
                "confidence": "Verified"
            }]
            results.append(KnowledgeObject(
                id="ART-LABEL-00001",
                type="print_template",
                title="Garment Label Template",
                summary="Standard printing layout that prints custom_mrp rate.",
                business_definition="Thermal barcode label template configured for retail outlets.",
                technical_definition="Format: ZPL II | Prints: custom_mrp, custom_barcode_size",
                dependencies=["custom_mrp"],
                evidence=evidence,
                relations=[("PRINTS", "custom_mrp")]
            ))
        return results


class FallbackResolver(Resolver):
    def score(self, query):
        return 5

    def resolve(self, engine, query):
        results = []
        for p in engine.providers.values():
            results.extend(p.resolve(engine, query))
        return results


class SKERenderer(object):
    @staticmethod
    def render(objects, output_format="structured"):
        if output_format == "json":
            return json.dumps([obj.to_dict() for obj in objects], indent=2)
        elif output_format == "structured":
            return objects
        elif output_format == "markdown":
            return SKERenderer.render_markdown(objects)
        elif output_format == "text":
            return SKERenderer.render_text(objects)
        return str(objects)

    @staticmethod
    def render_markdown(objects):
        if not objects:
            return "No matching SKE Knowledge Objects resolved."
        
        lines = []
        for obj in objects:
            lines.append(f"# {obj.title} (`{obj.id}`)")
            lines.append(f"* **Type:** `{obj.type.upper()}`")
            lines.append(f"* **Summary:** {obj.summary}")
            lines.append(u"")
            lines.append(u"## Business Meaning")
            lines.append(obj.business_definition)
            lines.append(u"")
            lines.append(u"## Technical Definition")
            lines.append(f"```text\n{obj.technical_definition}\n```")
            lines.append(u"")
            if obj.relations:
                lines.append(u"## Relationships")
                for rel in obj.relations:
                    lines.append(f"- **{rel[0]}:** `{rel[1]}`")
                lines.append(u"")
            if obj.examples:
                lines.append(u"## FAQs & Examples")
                for ex in obj.examples:
                    lines.append(f"- {ex}")
                lines.append(u"")
            if obj.evidence:
                lines.append(u"## Verified Evidence Pack")
                for idx, ev in enumerate(obj.evidence):
                    lines.append(f"### Evidence [{idx+1}]")
                    lines.append(f"* **Artifact ID:** `{ev.get('artifact_id')}`")
                    lines.append(f"* **Confidence:** `{ev.get('confidence', 'Verified')}`")
                    lines.append(f"* **Source File:** `{ev.get('source_file')}`")
                    if ev.get("line"):
                        lines.append(f"* **Line Number:** `{ev.get('line')}`")
                    if ev.get("edge_path"):
                        lines.append(f"* **Dependency Path:** `{' -> '.join(ev['edge_path'])}`")
                    lines.append(u"")
            lines.append(u"---")
            lines.append(u"")
        return u"\n".join(lines)

    @staticmethod
    def render_text(objects):
        if not objects:
            return "No SKE results found."
        res = []
        for obj in objects:
            res.append(f"Title: {obj.title}\nID: {obj.id}\nType: {obj.type}\nSummary: {obj.summary}\nBusiness Definition: {obj.business_definition}\nTechnical Definition: {obj.technical_definition}")
        return "\n\n".join(res)


class SMRITIKnowledgeEngine(object):
    def __init__(self, repo_root="d:\\Smriti_Retail_OS"):
        self.repo_root = repo_root
        self.discovery_dir = os.path.join(self.repo_root, "docs", "discovery")
        self.ir_cache = {}
        
        # Register Pluggable Providers
        self.providers = {
            "glossary": GlossaryProvider(),
            "field": FieldProvider(),
            "doctype": DocTypeProvider(),
            "api": APIProvider(),
            "formula": FormulaProvider(),
            "screen": ScreenProvider()
        }

        # Register Resolvers
        self.resolvers = [
            LookupResolver(),
            DependencyResolver(),
            ImpactResolver(),
            APITouchingResolver(),
            LabelsPrintingResolver(),
            FallbackResolver()
        ]

        # Caches the search index in memory on boot for O(1) keyword lookups
        self.search_index = self.get_ir("search_index", {})

    def get_provider(self, name):
        return self.providers.get(name)

    def clean_query(self, query):
        q = query.lower()
        
        # Strip prefixes
        prefixes = [
            "what is ", "explain ", "where is ", "show all apis touching ", 
            "show apis touching ", "apis touching ", "delete ", "remove ", 
            "what breaks? ", "what breaks ", "impact of ", "which labels print ", 
            "show formula for ", "show "
        ]
        for p in prefixes:
            if q.startswith(p):
                q = q[len(p):]
                
        # Strip suffixes
        suffixes = [
            " used?", " used", " breaks?", " breaks", " touching", " overview", " details", " documentation"
        ]
        for s in suffixes:
            if q.endswith(s):
                q = q[:-len(s)]
                
        return q.strip("? \t\r\n.")

    def get_ir(self, name, default=None):
        if name in self.ir_cache:
            return self.ir_cache[name]
        
        path = os.path.join(self.discovery_dir, f"{name}.json")
        if not os.path.exists(path):
            return default
        try:
            with io.open(path, "r", encoding="utf-8") as f:
                ir_data = json.load(f)
            self.ir_cache[name] = ir_data.get("data", default)
            return self.ir_cache[name]
        except Exception:
            return default

    def resolve(self, query, context=None, output_format="structured"):
        """Main resolve pipeline: Query -> Intent -> Resolve -> Merge -> Rank -> Render."""
        SDCLogger.info(f"SKE resolving query: '{query}'")

        # 1. Dispatch query to resolvers for scoring
        scored_resolvers = []
        for r in self.resolvers:
            score = r.score(query)
            scored_resolvers.append((score, r))
        
        # Sort by score descending
        scored_resolvers.sort(key=lambda x: x[0], reverse=True)
        winner_score, winner_resolver = scored_resolvers[0]
        
        # 2. Execute resolution
        resolved_objects = winner_resolver.resolve(self, query)

        # 3. Merge overlapping KnowledgeObjects
        merged_objects = self.merge_knowledge_objects(resolved_objects)

        # 4. Rank resolved objects based on Search Ranking Guardrails
        type_priority = {
            "glossary_term": 1,
            "field": 2,
            "doctype": 3,
            "api": 4,
            "formula": 5,
            "manual": 6,
            "screen": 7,
            "dependency": 8,
            "impact_analysis": 9
        }
        merged_objects.sort(key=lambda x: type_priority.get(x.type, 99))

        # 5. Render output
        return SKERenderer.render(merged_objects, output_format=output_format)

    def merge_knowledge_objects(self, objects):
        if not objects:
            return []
        
        grouped = {}
        for obj in objects:
            key = obj.title.lower()
            if key not in grouped:
                grouped[key] = []
            grouped[key].append(obj)

        merged = []
        for key, obj_list in grouped.items():
            if len(obj_list) == 1:
                merged.append(obj_list[0])
            else:
                base = obj_list[0]
                merged_id = base.id
                merged_type = base.type
                merged_title = base.title
                
                bus_defs = list(set([o.business_definition for o in obj_list if o.business_definition]))
                tech_defs = list(set([o.technical_definition for o in obj_list if o.technical_definition]))
                summaries = list(set([o.summary for o in obj_list if o.summary]))
                
                dependencies = []
                evidence = []
                related_objects = []
                examples = []
                references = []
                relations = []
                
                for o in obj_list:
                    dependencies.extend(o.dependencies)
                    evidence.extend(o.evidence)
                    related_objects.extend(o.related_objects)
                    examples.extend(o.examples)
                    references.extend(o.references)
                    relations.extend(o.relations)

                dependencies = sorted(list(set(dependencies)))
                related_objects = sorted(list(set(related_objects)))
                examples = sorted(list(set(examples)))
                references = sorted(list(set(references)))
                
                dedup_relations = []
                for rel in relations:
                    if rel not in dedup_relations:
                        dedup_relations.append(rel)

                dedup_evidence = []
                seen_evidence_ids = set()
                for ev in evidence:
                    ev_id = ev.get("artifact_id")
                    if ev_id not in seen_evidence_ids:
                        seen_evidence_ids.add(ev_id)
                        dedup_evidence.append(ev)

                merged.append(KnowledgeObject(
                    id=merged_id,
                    type=merged_type,
                    title=merged_title,
                    summary=" | ".join(summaries),
                    business_definition=" | ".join(bus_defs),
                    technical_definition="\n".join(tech_defs),
                    dependencies=dependencies,
                    evidence=dedup_evidence,
                    related_objects=related_objects,
                    examples=examples,
                    references=references,
                    relations=dedup_relations
                ))
        return merged
