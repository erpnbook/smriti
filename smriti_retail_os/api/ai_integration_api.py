# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/api/ai_integration_api.py
# @description: Whitelisted backend API endpoints for SMRITI AI integration.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.2.15
# @license: MIT
#

import frappe
from smriti_retail_os.services import ai_context_service

@frappe.whitelist()
def get_ai_context(query):
    """
    Returns the raw Markdown Ground Truth context pack resolved from SKE.
    """
    try:
        return ai_context_service.build_context_pack(query)
    except Exception as e:
        frappe.log_error(message=str(e), title="get_ai_context Failed")
        frappe.throw(f"Failed to compile AI Context: {str(e)}")

@frappe.whitelist()
def ask_smriti_ai(query):
    """
    RAG Chat endpoint: queries SKE, builds the context pack, and generates a response.
    
    ARCHITECTURE (Zero-Hallucination Compliance):
    - v1 (Curated RAG): In the absence of a live LLM API configuration, the assistant uses a 
      deterministic response parser that maps common retail queries (barcode troubleshooting, 
      weeks of cover calculations, inventory visibility layer constraints) directly to their 
      underlying SKE ground truth facts. For other queries, it dynamically extracts and summarizes 
      the resolved SKE primary objects.
    - v2 (Live LLM): Leverages the context pack as the sole ground truth block in a system prompt 
      to generate contextual answers.
    """
    try:
        context_pack, meta = ai_context_service.build_context_pack(query, return_metadata=True)
        
        # 1. Safety Gate: If no primary objects were resolved, decline to answer.
        if "WARNING: No primary" in context_pack or "ERROR" in context_pack:
            answer = (
                f"I cannot find any verified documentation or repository assets related to your query "
                f"\"**{query}**\" in the SMRITI Knowledge Base.\n\n"
                f"To prevent hallucinations and comply with the **SMRITI AI Content Policy (AI-GOV-01)**, "
                f"I am restricted from answering queries that lack ground-truth repository mapping.\n\n"
                f"**Suggestions:**\n"
                f"* Check for typos in your query.\n"
                f"* Search for exact glossary terms (e.g., `Article`, `WOC`, `PSV`).\n"
                f"* Search for exact field or DocType keys (e.g., `Item`, `custom_size_profile`)."
            )
            return {
                "answer": answer,
                "context_pack": context_pack,
                "evidence_badge": "❌ Unverified | 0 Graph Links | Scan: Today"
            }

        # 2. Extract context hints to write a specific answer
        answer_parts = []
        if "barcode" in query.lower() or "print" in query.lower():
            answer = (
                "Based on the **SMRITI Ground Truth context**, here is the solution for your query regarding **Barcode printing**:\n\n"
                "### 1. Key Technical Fields involved:\n"
                "* `print_job_id` (Primary Key in Reprint Queue)\n"
                "* `warehouse_id` (Ergonomic routing mapping)\n"
                "* `label_template` (Visual print layout template)\n\n"
                "### 2. Common Causes & Suggested Fixes:\n"
                "1. **Missing Warehouse ID Mapping**: If the print job lacks a `warehouse_id`, the system cannot route the queue to the correct terminal. Verify that the warehouse is configured and active in the master data.\n"
                "2. **Failed Job State**: Check the **Reprint Queue** inside the Barcode Studio. If a job is marked as `Failed` or `Pending`, select it and click **Retry Print**.\n"
                "3. **Layout Version Collision**: SMRITI Barcode Studio enforces layout dimension validation (`layout_version`). If you updated the layout design without updating the compiler version, print commands may fail. Re-compile the layout using the SDC CLI.\n\n"
                "Please review the SKE Ground Truth logs below to see the exact field and API definitions."
            )
        elif "woc" in query.lower() or "weeks of cover" in query.lower():
            answer = (
                "Based on the **SMRITI Ground Truth context**, here is the explanation for **Weeks of Cover (WOC)**:\n\n"
                "### 1. Business Definition:\n"
                "Weeks of Cover (WOC) measures how many weeks your current stock will last based on the average sales velocity. "
                "It is a core metric used in stores and distributor networks to prevent stockouts and manage capital lockup.\n\n"
                "### 2. Mathematical Formula Expression (Formula ID: `WOC-01`):\n"
                "```text\n"
                "WOC = Current Stock / Average Weekly Sales Velocity\n"
                "```\n"
                "### 3. Live Interpretation Bands:\n"
                "* **Critical (< 2 weeks)**: High stockout risk. Immediate replenishment recommended.\n"
                "* **Healthy (2 - 6 weeks)**: Optimal stock levels.\n"
                "* **Excess (> 6 weeks)**: Capital locked up. Consider transfer optimization.\n\n"
                "Please see the SKE Ground Truth logs below for the exact formulas and dependencies."
            )
        elif "psv" in query.lower() or "visibility" in query.lower():
            answer = (
                "Based on the **SMRITI Ground Truth context**, here is the explanation for **Party Stock Visibility (PSV)**:\n\n"
                "### 1. Core Concept:\n"
                "PSV (Party Stock Visibility) tracks stock levels, capital locked, and coverage days across distributor and channel networks. "
                "It is a **Business-Type Activated Core Extension** that remains hidden for standard retail stores but acts as the primary operational dashboard for brands selling through distributor networks.\n\n"
                "### 2. Sandbox Constraints (PSV Rule):\n"
                "PSV maintains its own **Inventory Visibility Layer**. It reads ERPNext masters (Customers, Items, Warehouses) but **must never modify** ERPNext Stock Ledger Entries or General Ledger Entries.\n\n"
                "Please refer to the SKE Ground Truth logs below to view details on the Inventory Visibility Layer database schemas."
            )
        else:
            # General answer summarizing retrieved SKE primary objects
            lines = [
                "I have compiled the conversational answer using verified SKE Ground Truth:\n",
                "### Mapped Knowledge Objects Found:"
            ]
            import re
            objs = re.findall(r"--- Primary Object: \[(.*?)\] ---", context_pack)
            titles = re.findall(r"Title: (.*?)\n", context_pack)
            summaries = re.findall(r"Summary: (.*?)\n", context_pack)
            
            for i, oid in enumerate(objs):
                title = titles[i] if i < len(titles) else "Reference Asset"
                summary = summaries[i] if i < len(summaries) else "No summary available."
                lines.append(f"* **{title}** (`{oid}`): {summary}")
                
            lines.append("\nFor detailed technical dependencies, API mappings, and manual references, expand the **SKE Ground Truth Used** section below.")
            answer = "\n".join(lines)

        return {
            "answer": answer,
            "context_pack": context_pack,
            "evidence_badge": f"✔ Verified | {meta['num_links']} Graph Links | {meta['validation_status']}"
        }

    except Exception as e:
        frappe.log_error(message=str(e), title="ask_smriti_ai Failed")
        frappe.throw(f"AI Assistant Error: {str(e)}")
