#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SMRITI Retail OS — HTML Template Validator
TEMPLATE-01: HTML Comment Safety Rule Enforcement

Checks:
1. No JS-style comments (/** ... */ or /* ... */) outside script/style/jinja comment blocks
2. No leaked metadata (@file:, @author:, @license:, Copyright) outside HTML comments
3. No TODO/FIXME markers
4. No debug/testing markers (DEBUG_MARKER, TEMP_TESTING)
5. No console.log statements outside script blocks
"""

import sys
import os
import re

def validate_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    errors = []

    # 1. Strip style and script blocks from the raw HTML to check text/HTML body
    stripped_code = re.sub(r"<script.*?>.*?</script>", "", content, flags=re.DOTALL)
    stripped_code = re.sub(r"<style.*?>.*?</style>", "", stripped_code, flags=re.DOTALL)
    
    # Save a version where Jinja comments and HTML comments are also stripped
    stripped_all_comments = re.sub(r"<!--.*?-->", "", stripped_code, flags=re.DOTALL)
    stripped_all_comments = re.sub(r"\{#.*?#\}", "", stripped_all_comments, flags=re.DOTALL)
    # UI-MIDNIGHT-002: Strip Jinja block comments {%- comment -%} ... {%- endcomment -%}
    # These are valid Jinja2 comment blocks used in include files for file-level annotations.
    # Validator must strip these before metadata leak checks to avoid false positives.
    stripped_all_comments = re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", "", stripped_all_comments, flags=re.DOTALL)

    # 1. Check for JS-style comments (/** ... */ or /* ... */) outside script/style tags
    js_comment_match = re.search(r"/\*.*?\*/", stripped_all_comments, re.DOTALL)
    if js_comment_match:
        comment_text = js_comment_match.group(0)
        idx = js_comment_match.start()
        snippet = stripped_all_comments[max(0, idx - 40):min(len(stripped_all_comments), idx + 80 + len(comment_text))]
        errors.append(f"JS-style comment '{comment_text.strip()}' found outside script/style block. Snippet: ... {snippet.strip()} ...")


    # 2. Check for leaked metadata tags in the visible layout (outside HTML comments / Jinja comments)
    leak_markers = ["@file:", "@author:", "@license:", "Copyright", "/**"]
    for marker in leak_markers:
        if marker in stripped_all_comments:
            idx = stripped_all_comments.find(marker)
            snippet = stripped_all_comments[max(0, idx - 40):min(len(stripped_all_comments), idx + 80)]
            errors.append(f"Leaked source metadata '{marker}' found in HTML body/layout. Snippet: ... {snippet.strip()} ...")

    # 3. Check for TODOs / FIXMEs (case-insensitive) in the entire file
    todo_matches = re.findall(r"\b(TODO|FIXME)\b", content, re.IGNORECASE)
    if todo_matches:
        errors.append(f"Unresolved TODO/FIXME markers found: {set(todo_matches)}")

    # 4. Check for DEBUG markers in HTML body (outside script/style tags)
    debug_matches = re.findall(r"\b(DEBUG_MARKER|TEMP_TESTING|DEBUG)\b", stripped_code, re.IGNORECASE)
    if debug_matches:
        errors.append(f"Unresolved DEBUG/TESTING markers found: {set(debug_matches)}")

    # 5. Check for console.log / alert outside script blocks
    for statement in ["console.log", "alert"]:
        pattern = rf"\b{re.escape(statement)}\s*\("
        match = re.search(pattern, stripped_code, re.IGNORECASE)
        if match:
            idx = match.start()
            snippet = stripped_code[max(0, idx - 40):min(len(stripped_code), idx + 80)]
            errors.append(f"'{statement}' statement found outside script block. Snippet: ... {snippet.strip()} ...")

    return errors

def main():
    args = sys.argv[1:]
    if not args:
        print("No files specified for validation.")
        sys.exit(0)

    has_errors = False
    for filepath in args:
        if not filepath.endswith(".html"):
            continue
        if not os.path.exists(filepath):
            continue
        
        errors = validate_file(filepath)
        if errors:
            has_errors = True
            print(f"TEMPLATE-01 Violation in '{filepath}':")
            for err in errors:
                print(f"  - {err}")

    if has_errors:
        sys.exit(1)
    else:
        print("All HTML templates passed validation!")
        sys.exit(0)

if __name__ == "__main__":
    main()
