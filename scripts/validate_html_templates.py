#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SMRITI Retail OS -- HTML Template Validator
TEMPLATE-01: HTML Comment Safety Rule Enforcement

Checks:
1. No JS-style comments (/** ... */ or /* ... */) outside script/style/jinja comment blocks
2. No leaked metadata (@file:, @author:, @license:, Copyright) outside HTML comments
3. No TODO/FIXME markers
4. No debug/testing markers (DEBUG_MARKER, TEMP_TESTING)
5. No console.log statements outside script blocks

UI-GOV-006: Hardcoded Color Regression Gate
6. No new file may increase hardcoded hex (#RRGGBB) or rgba() count above its baseline.
   Baseline stored in: scripts/color_baseline.json
   Run: python scripts/validate_html_templates.py --update-baseline
        to update baseline after intentional cleanup.
"""

import sys
import os
import re
import json
import argparse

# ---------------------------------------------------------------------------
# UI-GOV-006: Baseline file path
# ---------------------------------------------------------------------------
BASELINE_FILE = os.path.join(os.path.dirname(__file__), "color_baseline.json")

# Established baseline from UI-MIDNIGHT-001 audit (2026-06-24)
# Source: grep across smriti_retail_os/www/*.html
DEFAULT_BASELINE = {
    "_meta": {
        "sprint":    "UI-MIDNIGHT-001",
        "date":      "2026-06-24",
        "hex_total":  1179,
        "rgba_total": 1199,
        "note":       "First measured baseline. Reduce each sprint."
    },
    "files": {}
}


def count_hardcoded_colors(content):
    """Count hardcoded hex + rgba occurrences (excluding SVG/HTTP/comments)."""
    # Strip HTML and Jinja comments first
    clean = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    clean = re.sub(r"\{#.*?#\}", "", clean, flags=re.DOTALL)
    clean = re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", "", clean, flags=re.DOTALL)

    # Count hex colors (exclude URLs, SVG gradient IDs, and data-* values)
    hex_matches = re.findall(r"#[0-9a-fA-F]{3,8}", clean)
    # Filter out non-color hexes (fragment URLs, IDs that are too short to be colors)
    hex_colors = [h for h in hex_matches
                  if len(h) in (4, 7, 9)  # #RGB, #RRGGBB, #RRGGBBAA
                  and not re.match(r"#[0-9a-fA-F]{5}$", h)]  # skip 5-char (not valid CSS color)

    rgba_matches = re.findall(r"rgba?\s*\(", clean)

    return len(hex_colors), len(rgba_matches)


def load_baseline():
    """Load the color baseline from file, or return defaults."""
    if os.path.exists(BASELINE_FILE):
        try:
            with open(BASELINE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return DEFAULT_BASELINE.copy()


def save_baseline(baseline):
    """Write updated baseline to file."""
    with open(BASELINE_FILE, "w", encoding="utf-8") as f:
        json.dump(baseline, f, indent=2)


def validate_file(filepath, baseline=None, gov006_enabled=True):
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

    # -----------------------------------------------------------------------
    # 6. UI-GOV-006: Hardcoded color regression gate
    #    No file may have MORE hardcoded colors than its recorded baseline.
    #    New files start with their current count as baseline.
    # -----------------------------------------------------------------------
    if gov006_enabled and baseline is not None:
        fname = os.path.basename(filepath)
        hex_count, rgba_count = count_hardcoded_colors(content)
        file_baseline = baseline.get("files", {}).get(fname, None)

        if file_baseline is None:
            # New file -- record baseline, no error
            baseline.setdefault("files", {})[fname] = {
                "hex": hex_count,
                "rgba": rgba_count,
                "note": "Auto-recorded on first validation"
            }
        else:
            base_hex  = file_baseline.get("hex", 0)
            base_rgba = file_baseline.get("rgba", 0)

            if hex_count > base_hex:
                errors.append(
                    f"UI-GOV-006 REGRESSION: hardcoded hex count increased. "
                    f"Baseline={base_hex}, Current={hex_count} (+{hex_count - base_hex}). "
                    f"Use var(--smriti-*) tokens instead of literal hex values."
                )
            if rgba_count > base_rgba:
                errors.append(
                    f"UI-GOV-006 REGRESSION: hardcoded rgba() count increased. "
                    f"Baseline={base_rgba}, Current={rgba_count} (+{rgba_count - base_rgba}). "
                    f"Use var(--smriti-*) tokens instead of literal rgba() values."
                )

    return errors


def build_baseline(www_dir):
    """Scan all HTML files and build a fresh baseline. Called with --update-baseline."""
    baseline = load_baseline()
    baseline.setdefault("files", {})
    total_hex = 0
    total_rgba = 0

    for fname in os.listdir(www_dir):
        if not fname.endswith(".html"):
            continue
        fpath = os.path.join(www_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            h, r = count_hardcoded_colors(content)
            baseline["files"][fname] = {"hex": h, "rgba": r}
            total_hex  += h
            total_rgba += r
        except Exception as e:
            print(f"  Warning: could not scan {fname}: {e}")

    baseline["_meta"]["hex_total"]  = total_hex
    baseline["_meta"]["rgba_total"] = total_rgba
    baseline["_meta"]["date"] = __import__("datetime").date.today().isoformat()
    save_baseline(baseline)
    print(f"Baseline updated: {total_hex} hex, {total_rgba} rgba across {len(baseline['files'])} files.")
    print(f"Saved to: {BASELINE_FILE}")


def main():
    parser = argparse.ArgumentParser(description="SMRITI HTML Template Validator")
    parser.add_argument("files", nargs="*", help="HTML files to validate")
    parser.add_argument("--update-baseline", action="store_true",
                        help="Rebuild UI-GOV-006 color baseline from www/ directory")
    parser.add_argument("--www-dir", default=None,
                        help="Path to www/ directory (used with --update-baseline)")
    parser.add_argument("--no-gov006", action="store_true",
                        help="Skip UI-GOV-006 color regression check")
    args = parser.parse_args()

    # --update-baseline mode
    if args.update_baseline:
        www_dir = args.www_dir or os.path.join(
            os.path.dirname(__file__), "..",
            "smriti_retail_os", "www"
        )
        build_baseline(os.path.abspath(www_dir))
        sys.exit(0)

    if not args.files:
        print("No files specified for validation.")
        sys.exit(0)

    baseline = None if args.no_gov006 else load_baseline()

    print("=" * 71)
    print("Running SMRITI HTML Template Validator (TEMPLATE-01)...")
    print("=" * 71)

    has_errors = False
    for filepath in args.files:
        if not filepath.endswith(".html"):
            continue
        if not os.path.exists(filepath):
            continue

        errors = validate_file(filepath, baseline=baseline, gov006_enabled=not args.no_gov006)
        if errors:
            has_errors = True
            print(f"TEMPLATE-01 Violation in '{filepath}':\r")
            for err in errors:
                print(f"  - {err}")

    # Save any newly recorded baselines (new files auto-enrolled)
    if baseline is not None:
        save_baseline(baseline)

    if has_errors:
        print("=" * 71)
        print("ERROR: HTML template validation failed. Commit aborted.")
        print("Please fix the presentation/metadata leak violations shown above.")
        print("=" * 71)
        sys.exit(1)
    else:
        print("All HTML templates passed validation!")
        print("=" * 71)
        print("SUCCESS: All staged HTML templates passed validation!")
        print("=" * 71)
        sys.exit(0)


if __name__ == "__main__":
    main()
