# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/services/knowledge_service.py
# @description: Knowledge Center service layer for SMRITI Retail OS.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-19
# @version: 1.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import frappe
import os
import re
import json

REDIS_INDEX_KEY = "smriti:knowledge:index"
CACHE_TTL = 86400  # 24 hours persistent cache for search index

TYPE_WEIGHTS = {
    "Dictionary Term": 100,
    "Formula Definition": 90,
    "Training Exercise": 80,
    "FAQ": 70,
    "Manual Section": 60,
    "About Page": 55,
    "Governance": 50,
    "KB Article": 50
}

def rebuild_knowledge_index():
    """
    Scans all SMRITI knowledge sources (Business Terms, Formula Definitions,
    Help Center registry, User Manuals, and KB articles), compiles them into
    a persistent search index, and caches it in Redis.
    """
    index = []

    # 1. Index Business Terms (Weight 100)
    terms = frappe.get_all(
        "SMRITI Business Term",
        filters={"is_active": 1, "status": "Approved"},
        fields=["name", "term_id", "term_name", "term_category", "term_aliases", "definition", "hinglish_definition", "faq", "common_mistakes", "manual_reference", "training_reference"]
    )
    for t in terms:
        # Resolve related terms and formulas
        related_formulas = [rf.formula_id for rf in frappe.get_all("SMRITI Related Formula", filters={"parent": t.name}, fields=["formula_id"])]
        related_terms = [rt.related_term_id for rt in frappe.get_all("SMRITI Related Term", filters={"parent": t.name}, fields=["related_term_id"])]
        
        metadata = {
            "term_id": t.term_id,
            "term_category": t.term_category,
            "term_aliases": json.loads(t.term_aliases) if t.term_aliases else [],
            "faq": json.loads(t.faq) if t.faq else [],
            "common_mistakes": json.loads(t.common_mistakes) if t.common_mistakes else [],
            "manual_reference": t.manual_reference,
            "training_reference": t.training_reference,
            "related_formulas": related_formulas,
            "related_terms": related_terms
        }
        
        searchable_content = " ".join(filter(None, [
            t.term_id,
            t.term_name,
            t.term_category,
            t.term_aliases,
            t.definition,
            t.hinglish_definition,
            t.faq,
            t.common_mistakes
        ]))

        index.append({
            "id": f"dict:{t.term_id}",
            "title": t.term_name,
            "type": "Dictionary Term",
            "weight": TYPE_WEIGHTS["Dictionary Term"],
            "content": searchable_content,
            "reference": f"/smriti-dictionary?term={t.term_id}",
            "metadata": metadata
        })

    # 2. Index Formula Definitions (Weight 90)
    formulas = frappe.get_all(
        "SMRITI Formula Definition",
        filters={"is_active": 1, "status": "Approved"},
        fields=["name", "formula_id", "formula_name", "formula_category", "formula_expression", "business_meaning", "worked_example", "interpretation_guide", "recommended_action"]
    )
    for f in formulas:
        metadata = {
            "formula_id": f.formula_id,
            "formula_category": f.formula_category,
            "formula_expression": f.formula_expression,
            "worked_example": f.worked_example,
            "interpretation_guide": f.interpretation_guide,
            "recommended_action": f.recommended_action
        }
        
        searchable_content = " ".join(filter(None, [
            f.formula_id,
            f.formula_name,
            f.formula_category,
            f.formula_expression,
            f.business_meaning,
            f.worked_example,
            f.interpretation_guide,
            f.recommended_action
        ]))

        index.append({
            "id": f"formula:{f.formula_id}",
            "title": f.formula_name,
            "type": "Formula Definition",
            "weight": TYPE_WEIGHTS["Formula Definition"],
            "content": searchable_content,
            "reference": f"/smriti-formula-registry?formula={f.formula_id}",
            "metadata": metadata
        })

    # 3. Index In-App Help Registry articles
    from smriti_retail_os.api.help_api import HELP_CENTER_REGISTRY
    for key, art in HELP_CENTER_REGISTRY.items():
        if key in ["formula_registry", "business_dictionary"]:
            # Skip database-backed ones that are already covered
            continue
            
        faqs_text = ""
        faqs_list = art.get("faqs", [])
        for faq in faqs_list:
            faqs_text += f" {faq.get('question', '')} {faq.get('answer', '')}"
            
        searchable_content = " ".join(filter(None, [
            art.get("title", ""),
            art.get("category", ""),
            art.get("description", ""),
            art.get("content", ""),
            faqs_text
        ]))

        index.append({
            "id": f"help:{key}",
            "title": art.get("title", ""),
            "type": "KB Article",
            "weight": TYPE_WEIGHTS["KB Article"],
            "content": searchable_content,
            "reference": f"/smriti-help?article={key}",
            "metadata": {
                "article_key": key,
                "category": art.get("category", "General"),
                "description": art.get("description", ""),
                "faqs": faqs_list
            }
        })

    # 4. Index User Manuals & KB Markdown Files
    docs_root = os.path.abspath(os.path.join(frappe.get_app_path("smriti_retail_os"), "..", "..", "..", "docs"))
    if os.path.exists(docs_root):
        _index_markdown_directory(docs_root, index)

    # Save to Redis
    frappe.cache().set_value(REDIS_INDEX_KEY, json.dumps(index), expires_in_sec=CACHE_TTL)
    return len(index)

def _index_markdown_directory(docs_dir, index):
    """
    Recursively scans docs/user_manual/ and docs/kb/ for markdown files and indexes sections.
    """
    for root, dirs, files in os.walk(docs_dir):
        # Only index user_manual and kb directories to prevent indexing node_modules, etc.
        relative_dir = os.path.relpath(root, docs_dir).replace("\\", "/")
        if not (relative_dir.startswith("user_manual") or relative_dir.startswith("kb") or relative_dir.startswith("about") or relative_dir.startswith("governance")):
            continue
            
        for file in files:
            if not file.endswith(".md"):
                continue
                
            file_path = os.path.join(root, file)
            _parse_and_index_markdown_file(file_path, docs_dir, index)

def _parse_and_index_markdown_file(file_path, docs_dir, index):
    """
    Parses a single markdown file, extracts YAML metadata, splits sections by headings,
    and categorizes them (Manual Section, KB Article, FAQ, or Training Exercise).
    """
    file_basename = os.path.splitext(os.path.basename(file_path))[0]
    rel_path = os.path.relpath(file_path, docs_dir).replace("\\", "/")

    from smriti_retail_os.api.help_api import DOCUMENT_REGISTRY
    registry_entry = DOCUMENT_REGISTRY.get(file_basename)
    
    # Skip indexing if the document is explicitly marked not searchable
    if registry_entry and not registry_entry.get("searchable", True):
        return
        
    is_user_manual = "user_manual" in rel_path
    
    # Determine the default type and weight
    if is_user_manual:
        default_type = "Manual Section"
    elif "about" in rel_path:
        default_type = "About Page"
    elif "governance" in rel_path:
        default_type = "Governance"
    else:
        default_type = "KB Article"
        
    default_weight = TYPE_WEIGHTS.get(default_type, 50)
    
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        
    # Parse YAML frontmatter
    title = file_basename.replace("_", " ").title()
    author = "SMRITI Team"
    start_line = 0
    
    if len(lines) > 0 and lines[0].strip() == "---":
        frontmatter = []
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                start_line = i + 1
                break
            frontmatter.append(lines[i])
            
        # Extract title/author from frontmatter
        for line in frontmatter:
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip().lower()
                v = v.strip().strip('"').strip("'")
                if k == "title":
                    title = v
                elif k == "author":
                    author = v

    # Split into heading-based sections
    current_section_title = title
    current_section_level = 1
    current_section_content = []
    
    def save_section(sec_title, content_lines, line_no):
        content_text = "".join(content_lines).strip()
        if not content_text:
            return
            
        # Determine exact type of section
        sec_type = default_type
        sec_weight = default_weight
        
        # Check if it is a training exercise
        if "volume_5_training_workbook" in file_basename and (sec_title.startswith("Exercise ") or "Exercise" in sec_title):
            sec_type = "Training Exercise"
            sec_weight = TYPE_WEIGHTS["Training Exercise"]
        # Check if it is an FAQ
        elif "volume_4_troubleshooting_faq" in file_basename and re.match(r"^\d+\.\s*Q:", sec_title):
            sec_type = "FAQ"
            sec_weight = TYPE_WEIGHTS["FAQ"]
        elif "faq" in rel_path or "FAQ" in sec_title:
            sec_type = "FAQ"
            sec_weight = TYPE_WEIGHTS["FAQ"]
            
        # Clean markdown syntax for search indexing
        clean_content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", content_text) # remove links
        clean_content = re.sub(r"[*`#_]", "", clean_content) # remove formatting characters
        
        slug = re.sub(r"[^a-z0-9]+", "-", sec_title.lower()).strip("-")
        
        # Build reference URL
        ref = f"/smriti-help?manual={file_basename}&section={slug}"
        if not is_user_manual:
            ref = f"/smriti-help?kb={file_basename}&section={slug}"
            
        index.append({
            "id": f"md:{file_basename}:{slug}:{line_no}",
            "title": sec_title,
            "type": sec_type,
            "weight": sec_weight,
            "content": f"{sec_title} {clean_content}",
            "reference": ref,
            "metadata": {
                "source_file": file_basename,
                "parent_title": title,
                "author": author,
                "raw_markdown": content_text,
                "visibility": registry_entry.get("visibility") if registry_entry else "all"
            }
        })

    section_lines = []
    for idx in range(start_line, len(lines)):
        line = lines[idx]
        heading_match = re.match(r"^(#{1,6})\s+(.+)$", line)
        if heading_match:
            # Save previous section
            save_section(current_section_title, section_lines, idx - len(section_lines))
            # Start new section
            level = len(heading_match.group(1))
            sec_title = heading_match.group(2).strip()
            
            current_section_title = sec_title
            current_section_level = level
            section_lines = []
        else:
            section_lines.append(line)
            
    # Save the last section
    if section_lines:
        save_section(current_section_title, section_lines, len(lines) - len(section_lines))

def search_knowledge_index(query):
    """
    Performs debounced fuzzy search on the Redis cached index.
    Sorts results by:
      1. Type weighting matrix
      2. Relevance matching score
    """
    if not query:
        return []
        
    query = query.strip().lower()
    
    # Load index from cache
    cached_data = frappe.cache().get_value(REDIS_INDEX_KEY)
    if not cached_data:
        rebuild_knowledge_index()
        cached_data = frappe.cache().get_value(REDIS_INDEX_KEY)
        
    if not cached_data:
        return []
        
    index = json.loads(cached_data)
    results = []
    
    query_words = query.split()
    
    for item in index:
        content = item["content"].lower()
        title = item["title"].lower()
        
        # Simple match scoring:
        # Title direct match = +500
        # Title word match = +100 per word
        # Content word match = +10 per word
        score = 0
        
        if query in title:
            score += 500
        if query in content:
            score += 200
            
        for word in query_words:
            if word in title:
                score += 100
            if word in content:
                score += 10
                
        # Fuzzy match alias array check for dictionary terms
        aliases = item.get("metadata", {}).get("term_aliases", [])
        for alias in aliases:
            if query in alias.lower():
                score += 300
                
        if score > 0:
            results.append({
                "id": item["id"],
                "title": item["title"],
                "type": item["type"],
                "weight": item["weight"],
                "reference": item["reference"],
                "metadata": item["metadata"],
                "score": score
            })
            
    # Sort by result weight descending, and score descending
    results.sort(key=lambda x: (x["score"], x["weight"]), reverse=True)
    return results

def calculate_knowledge_coverage():
    """
    Calculates KGF Coverage % (Formula GOV-001):
    Active terms with definition + FAQ + manual ref + training ref / total active terms * 100
    """
    terms = frappe.get_all(
        "SMRITI Business Term",
        filters={"is_active": 1, "status": "Approved"},
        fields=["definition", "faq", "manual_reference", "training_reference"]
    )
    if not terms:
        return 0.0
        
    complete_count = 0
    for t in terms:
        # Check completeness:
        # - Definition exists and has text
        # - FAQ exists, is valid JSON, and contains at least 1 FAQ item
        # - manual_reference is populated
        # - training_reference is populated
        has_def = bool(t.definition and len(t.definition.strip()) > 10)
        
        has_faq = False
        try:
            faq_list = json.loads(t.faq) if t.faq else []
            if isinstance(faq_list, list) and len(faq_list) > 0:
                has_faq = True
        except Exception:
            import sys
            _frappe = sys.modules.get('frappe')
            if _frappe: _frappe.logger().debug(f"SMRITI Debug: Silent exception in services/knowledge_service.py:387: {sys.exc_info()[1]}")
            
        has_manual = bool(t.manual_reference and len(t.manual_reference.strip()) > 0)
        has_training = bool(t.training_reference and len(t.training_reference.strip()) > 0)
        
        if has_def and has_faq and has_manual and has_training:
            complete_count += 1
            
    return round((complete_count / len(terms)) * 100.0, 2)

def get_governance_stats():
    """
    Aggregates stats for the Governance dashboard:
    - coverage_percent
    - terms_count
    - formulas_count
    - top_viewed_terms
    - top_viewed_formulas
    """
    terms_count = frappe.db.count("SMRITI Business Term", filters={"is_active": 1, "status": "Approved"})
    formulas_count = frappe.db.count("SMRITI Formula Definition", filters={"is_active": 1, "status": "Approved"})
    coverage = calculate_knowledge_coverage()
    
    # Query Activity Logs for views count
    # Action type matches from dictionary and explain service logs
    top_terms_data = frappe.get_all(
        "SMRITI PSV Activity Log",
        filters={"action_type": "Dictionary Accessed", "event_type": "DICTIONARY_ACCESSED"},
        fields=["reference_name"],
        limit=500
    )
    top_formulas_data = frappe.get_all(
        "SMRITI PSV Activity Log",
        filters={"action_type": "Formula Explained", "event_type": "FORMULA_EXPLAINED"},
        fields=["reference_name"],
        limit=500
    )
    
    # Aggregate counts
    terms_views = {}
    for entry in top_terms_data:
        ref = entry.reference_name
        terms_views[ref] = terms_views.get(ref, 0) + 1
        
    formulas_views = {}
    for entry in top_formulas_data:
        ref = entry.reference_name
        formulas_views[ref] = formulas_views.get(ref, 0) + 1
        
    # Get top 5 sorted
    sorted_terms = sorted(terms_views.items(), key=lambda x: x[1], reverse=True)[:5]
    sorted_formulas = sorted(formulas_views.items(), key=lambda x: x[1], reverse=True)[:5]
    
    # Enrich with names
    top_terms = []
    for term_id, count in sorted_terms:
        term_name = frappe.db.get_value("SMRITI Business Term", {"term_id": term_id}, "term_name") or term_id
        top_terms.append({"id": term_id, "name": term_name, "views": count})
        
    top_formulas = []
    for formula_id, count in sorted_formulas:
        formula_name = frappe.db.get_value("SMRITI Formula Definition", {"formula_id": formula_id}, "formula_name") or formula_id
        top_formulas.append({"id": formula_id, "name": formula_name, "views": count})
        
    return {
        "coverage_percent": coverage,
        "terms_count": terms_count,
        "formulas_count": formulas_count,
        "top_terms": top_terms,
        "top_formulas": top_formulas
    }
