# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/ai_context_service.py
# @description: SMRITI AI Context Builder — Retrieval-Augmented Context Generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.0.0
# @license: MIT
#

import sys
import os
import datetime
import frappe

def _get_ske_engine():
    app_path = frappe.get_app_path("smriti_retail_os")
    repo_root = os.path.dirname(os.path.dirname(os.path.dirname(app_path)))
    sdc_path = os.path.join(repo_root, "sdc")
    if sdc_path not in sys.path:
        sys.path.append(sdc_path)
    from ske import SMRITIKnowledgeEngine
    return SMRITIKnowledgeEngine(repo_root)

def build_context_pack(query):
    """
    SKE Retrieval Layer: Query SKE runtime, fetch resolved KnowledgeObjects
    and related dependencies, and compile them into a ground-truth Markdown context.
    """
    if not query:
        return "ERROR: Query string cannot be empty."

    try:
        engine = _get_ske_engine()
        # Retrieve primary matching knowledge objects
        primary_objects = engine.resolve(query, output_format="structured")
        
        if not primary_objects:
            return (
                "=== SMRITI GROUND TRUTH KNOWLEDGE CONTEXT PACK ===\n"
                "WARNING: No primary knowledge objects resolved from the repository for the query.\n"
                "=== END OF CONTEXT PACK ==="
            )

        lines = []
        lines.append("=== SMRITI GROUND TRUTH KNOWLEDGE CONTEXT PACK ===")
        lines.append(f"Generated At: {datetime.datetime.now().isoformat()}")
        lines.append("IR Spec Version: 1.0")
        lines.append("SKE Version: 1.1.2-GA")
        lines.append("System Safety Directive: Answer the query ONLY using the facts in this context pack. "
                     "If the required facts are not found, state that the information is not documented.")
        lines.append("")
        
        lines.append("PRIMARY KNOWLEDGE OBJECTS RESOLVED:")
        
        seen_ids = set()
        related_lookups = []

        for obj in primary_objects:
            seen_ids.add(obj.id)
            lines.append(f"\n--- Primary Object: [{obj.id}] ---")
            lines.append(f"Type: {obj.type}")
            lines.append(f"Title: {obj.title}")
            lines.append(f"Summary: {obj.summary}")
            
            if obj.business_definition:
                lines.append(f"Business Definition: {obj.business_definition}")
            if obj.technical_definition:
                lines.append(f"Technical Description: {obj.technical_definition}")
                
            if obj.examples:
                lines.append("Examples / FAQs:")
                for ex in obj.examples:
                    lines.append(f"  * {ex}")
            if obj.references:
                lines.append("Manual / Training References:")
                for ref in obj.references:
                    if ref:
                        lines.append(f"  * {ref}")
            
            # Queue related links for traversal
            if obj.relations:
                for rel_type, rel_id in obj.relations:
                    if rel_id not in seen_ids:
                        related_lookups.append((rel_type, rel_id))
            if obj.dependencies:
                for dep in obj.dependencies:
                    if dep not in seen_ids:
                        related_lookups.append(("DEPENDENCY", dep))

        # Retrieve 1st-degree related context from the SKE graph
        if related_lookups:
            lines.append("\n=========================================")
            lines.append("RELATED CONTEXTUAL GRAPH REFERENCES:")
            
            # Limit related lookups to avoid huge contexts
            for rel_type, rel_id in related_lookups[:6]:
                if rel_id in seen_ids:
                    continue
                seen_ids.add(rel_id)
                
                # Resolve the linked asset specifically
                linked_objs = engine.resolve(rel_id, output_format="structured")
                for l_obj in linked_objs:
                    lines.append(f"\n--- Related Reference: [{l_obj.id}] (Relationship: {rel_type}) ---")
                    lines.append(f"Type: {l_obj.type}")
                    lines.append(f"Title: {l_obj.title}")
                    lines.append(f"Summary: {l_obj.summary}")
                    if l_obj.business_definition:
                        lines.append(f"Definition: {l_obj.business_definition}")
                    if l_obj.technical_definition:
                        lines.append(f"Technical: {l_obj.technical_definition}")

        lines.append("\n=== END OF CONTEXT PACK ===")
        return "\n".join(lines)

    except Exception as e:
        frappe.log_error(message=str(e), title="SKE Context Builder Failed")
        return f"ERROR: SKE Context Generation failed due to an exception: {str(e)}"

def explain_decision_context(decision_type, entity_id):
    """
    Specialized context extraction for 'Explain Decision' (Formulas, Validations, APIs, Labels)
    """
    if not decision_type or not entity_id:
        return "ERROR: Decision type and Entity ID are required."
        
    query = f"Explain {decision_type} {entity_id}"
    return build_context_pack(query)
