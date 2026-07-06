# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/ai_context_service.py
# @description: SMRITI AI Context Builder — Retrieval-Augmented Context Generation.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
# @license: GPL-3.0-only
# SPDX-License-Identifier: GPL-3.0-only
#

import sys
import os
import datetime
import frappe

def _get_ske_engine():
    app_path = frappe.get_app_path("smriti_retail_os")
    
    # Check for packaged sdc directory inside custom app
    sdc_path = os.path.join(app_path, "sdc")
    if not os.path.exists(sdc_path):
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(app_path)))
        sdc_path = os.path.join(repo_root, "sdc")
    
    if sdc_path not in sys.path:
        sys.path.append(sdc_path)
        
    from ske import SMRITIKnowledgeEngine
    
    # Check for packaged docs/discovery inside custom app
    if os.path.exists(os.path.join(app_path, "docs", "discovery")):
        return SMRITIKnowledgeEngine(app_path)
    else:
        repo_root = os.path.dirname(os.path.dirname(os.path.dirname(app_path)))
        return SMRITIKnowledgeEngine(repo_root)

def build_context_pack(query, return_metadata=False):
    """
    SKE Retrieval Layer: Query SKE runtime, fetch resolved KnowledgeObjects
    and related dependencies, and compile them into a ground-truth Markdown context.
    """
    if not query:
        res_err = "ERROR: Query string cannot be empty."
        if return_metadata:
            return res_err, {"num_links": 0, "validation_status": "Unverified"}
        return res_err

    try:
        engine = _get_ske_engine()
        # Retrieve primary matching knowledge objects
        primary_objects = engine.resolve(query, output_format="structured")
        
        if not primary_objects:
            res_str = (
                "=== SMRITI GROUND TRUTH KNOWLEDGE CONTEXT PACK ===\n"
                "WARNING: No primary knowledge objects resolved from the repository for the query.\n"
                "=== END OF CONTEXT PACK ==="
            )
            if return_metadata:
                return res_str, {"num_links": 0, "validation_status": "Unverified"}
            return res_str

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
        context_str = "\n".join(lines)
        
        if return_metadata:
            # calculate validation_status and num_links dynamically
            validation_statuses = [obj.validation_status for obj in primary_objects if getattr(obj, "validation_status", None)]
            if "Draft" in validation_statuses:
                val_status = "Draft"
            elif all(s == "Certified" for s in validation_statuses) and validation_statuses:
                val_status = "Certified"
            else:
                val_status = "Verified"
                
            seen_edges = set()
            for obj in primary_objects:
                if obj.relations:
                    for rel_type, rel_id in obj.relations:
                        seen_edges.add((obj.id, rel_id, rel_type))
                if obj.dependencies:
                    for dep in obj.dependencies:
                        seen_edges.add((obj.id, dep, "DEPENDENCY"))
            num_links = len(seen_edges)
            
            return context_str, {"num_links": num_links, "validation_status": val_status}
            
        return context_str

    except Exception as e:
        frappe.log_error(message=str(e), title="SKE Context Builder Failed")
        res_err = f"ERROR: SKE Context Generation failed due to an exception: {str(e)}"
        if return_metadata:
            return res_err, {"num_links": 0, "validation_status": "Unverified"}
        return res_err

def explain_decision_context(decision_type, entity_id):
    """
    Specialized context extraction for 'Explain Decision' (Formulas, Validations, APIs, Labels)
    """
    if not decision_type or not entity_id:
        return "ERROR: Decision type and Entity ID are required."
        
    query = f"Explain {decision_type} {entity_id}"
    return build_context_pack(query)
