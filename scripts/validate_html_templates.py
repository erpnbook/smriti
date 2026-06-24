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
    """Count hardcoded hex + rgba occurrences (excluding SVG/HTTP/comments).

    Exclusions:
    - HTML and Jinja comments
    - CSS :root { } variable DECLARATIONS (--varname: #value) -- these are
      token definitions, not hardcoded colors. A token bridge like
      '--color-white: #ffffff' is governance-compliant; it's the canonical
      single source of truth, not a violation.
    - CSS variable fallback values: var(--token, #fallback)
    """
    # Strip HTML and Jinja comments first
    clean = re.sub(r"<!--.*?-->", "", content, flags=re.DOTALL)
    clean = re.sub(r"\{#.*?#\}", "", clean, flags=re.DOTALL)
    clean = re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}", "", clean, flags=re.DOTALL)

    # Strip CSS :root { } blocks — these are token DEFINITIONS, not violations.
    # A file that properly declares --color-white: #ffffff; in :root is doing
    # the right thing; the hex lives in one place as a named token.
    clean = re.sub(r":root\s*\{[^}]*\}", "", clean, flags=re.DOTALL)

    # Strip var() fallback values: var(--token, #fallback) — the fallback is
    # part of the token contract, not a standalone hardcoded value.
    clean = re.sub(r"var\s*\([^)]*\)", "", clean)

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


def build_baseline(www_dir, force=False):
    """
    Scan all HTML files and build a fresh baseline.
    Called with --update-baseline.

    UI-GOV-008: Baseline may only be updated when total debt DECREASES.
    Increase is forbidden -- prevents developers from gaming the gate.
    Use --force to override (requires explicit intent).
    """
    import datetime
    old_baseline = load_baseline()
    old_hex   = old_baseline.get("_meta", {}).get("hex_total",  999999)
    old_rgba  = old_baseline.get("_meta", {}).get("rgba_total", 999999)

    new_baseline = old_baseline.copy()
    new_baseline.setdefault("files", {})
    total_hex  = 0
    total_rgba = 0
    file_count = 0

    for fname in sorted(os.listdir(www_dir)):
        if not fname.endswith(".html"):
            continue
        fpath = os.path.join(www_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            h, r = count_hardcoded_colors(content)
            new_baseline["files"][fname] = {"hex": h, "rgba": r}
            total_hex  += h
            total_rgba += r
            file_count += 1
        except Exception as e:
            print("  Warning: could not scan " + fname + ": " + str(e))

    # --- UI-GOV-008 + UI-GOV-009 enforcement ---
    if not force:
        old_combined = old_hex + old_rgba
        new_combined = total_hex + total_rgba

        # UI-GOV-008: Debt must not increase
        if total_hex > old_hex:
            print("")
            print("UI-GOV-008 BLOCKED: Baseline update REJECTED.")
            print("  Hex violations INCREASED: " + str(old_hex) + " -> " + str(total_hex) + " (+" + str(total_hex - old_hex) + ")")
            print("  Baseline may only be updated after debt DECREASES.")
            print("  Fix violations first, then re-run --update-baseline.")
            print("  To override (not recommended): add --force flag.")
            return False
        if total_rgba > old_rgba:
            print("")
            print("UI-GOV-008 BLOCKED: Baseline update REJECTED.")
            print("  RGBA violations INCREASED: " + str(old_rgba) + " -> " + str(total_rgba) + " (+" + str(total_rgba - old_rgba) + ")")
            print("  Baseline may only be updated after debt DECREASES.")
            print("  Fix violations first, then re-run --update-baseline.")
            print("  To override (not recommended): add --force flag.")
            return False

        # UI-GOV-009: Minimum 5% combined reduction required
        # Prevents accidental baseline drift from trivial cleanups.
        # Use --approve="Reason" to bypass with recorded justification.
        if old_combined > 0:
            reduction_pct = (old_combined - new_combined) / old_combined * 100
            if reduction_pct < 5.0:
                approval = getattr(build_baseline, "_approval", None)
                if not approval:
                    print("")
                    print("UI-GOV-009 BLOCKED: Minimum 5% debt reduction required.")
                    print("  Combined before: " + str(old_combined))
                    print("  Combined after:  " + str(new_combined))
                    print("  Reduction:       " + str(round(reduction_pct, 2)) + "% (required >= 5%)")
                    print("  To approve with justification: add --approve=\"Sprint X cleanup\"")
                    print("  Founder approval overrides: add --force flag.")
                    return False
                else:
                    print("UI-GOV-009 APPROVED: Reduction=" + str(round(reduction_pct, 2)) + "% < 5% but approved.")
                    print("  Justification: " + str(approval))

    new_baseline["_meta"]["hex_total"]       = total_hex
    new_baseline["_meta"]["rgba_total"]      = total_rgba
    new_baseline["_meta"]["hex_prev"]        = old_hex
    new_baseline["_meta"]["rgba_prev"]       = old_rgba
    new_baseline["_meta"]["hex_delta"]       = total_hex  - old_hex
    new_baseline["_meta"]["rgba_delta"]      = total_rgba - old_rgba
    new_baseline["_meta"]["combined_prev"]   = old_hex + old_rgba
    new_baseline["_meta"]["combined_total"]  = total_hex + total_rgba
    new_baseline["_meta"]["combined_delta"]  = (total_hex + total_rgba) - (old_hex + old_rgba)
    new_baseline["_meta"]["date"]            = datetime.date.today().isoformat()
    # UI-GOV-009 audit trail
    if old_hex + old_rgba > 0:
        reduction_pct = ((old_hex + old_rgba) - (total_hex + total_rgba)) / (old_hex + old_rgba) * 100
        new_baseline["_meta"]["reduction_pct"] = round(reduction_pct, 2)
    approval = getattr(build_baseline, "_approval", None)
    if approval:
        import datetime as _dt
        new_baseline["_meta"].setdefault("gov009_approvals", []).append({
            "date":          datetime.date.today().isoformat(),
            "justification": approval,
            "reduction_pct": round(reduction_pct, 2) if old_hex + old_rgba > 0 else 0,
        })
    if force:
        new_baseline["_meta"]["force_used"] = datetime.date.today().isoformat()
    save_baseline(new_baseline)

    hex_delta  = total_hex  - old_hex
    rgba_delta = total_rgba - old_rgba
    comb_delta = (total_hex + total_rgba) - (old_hex + old_rgba)
    print("Baseline updated (UI-GOV-008 PASS):")
    print("  hex:  " + str(old_hex)  + " -> " + str(total_hex)  + " (" + ("+" if hex_delta  >= 0 else "") + str(hex_delta)  + ")")
    print("  rgba: " + str(old_rgba) + " -> " + str(total_rgba) + " (" + ("+" if rgba_delta >= 0 else "") + str(rgba_delta) + ")")
    if old_hex + old_rgba > 0:
        print("  reduction: " + str(round(reduction_pct, 2)) + "%  (UI-GOV-009 gate = 5%)")
    print("  Files scanned: " + str(file_count))
    print("  Saved to: " + BASELINE_FILE)
    return True




def compute_metrics(www_dir):
    """
    Compute Metric A-F for sprint reporting.
    Metric A: Total hardcoded hex count
    Metric B: Total hardcoded rgba count
    Metric C: Pages using smriti_sidebar include
    Metric D: Pages using smriti_token_loader include
    Metric E: Files at zero violations (hex + rgba = 0)
    Metric F: Theme Compliance Coverage % (token_loader pages / total * 100)
              Founder-defined KPI. Formula: Compliant Pages / Total Pages x 100.
    """
    import datetime
    metric_a = 0  # hex total
    metric_b = 0  # rgba total
    metric_c = 0  # pages with sidebar include
    metric_d = 0  # pages with token loader include
    metric_e = 0  # files at zero
    total_files = 0

    sidebar_pattern = re.compile(r'include.*smriti_sidebar')
    loader_pattern  = re.compile(r'include.*smriti_token_loader')

    for fname in sorted(os.listdir(www_dir)):
        if not fname.endswith(".html"):
            continue
        fpath = os.path.join(www_dir, fname)
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            h, r = count_hardcoded_colors(content)
            metric_a += h
            metric_b += r
            if h + r == 0:
                metric_e += 1
            if sidebar_pattern.search(content):
                metric_c += 1
            if loader_pattern.search(content):
                metric_d += 1
            total_files += 1
        except Exception:
            pass

    # Metric F: Theme Compliance Coverage %
    metric_f_pct = round(metric_d / total_files * 100, 1) if total_files > 0 else 0.0

    print("")
    print("=" * 60)
    print("SMRITI Midnight — UI Debt Metrics " + datetime.date.today().isoformat())
    print("=" * 60)
    print("Metric A  Hardcoded hex count         : " + str(metric_a))
    print("Metric B  Hardcoded rgba() count       : " + str(metric_b))
    print("Metric C  Pages using sidebar include  : " + str(metric_c) + " / " + str(total_files))
    print("Metric D  Pages using token loader     : " + str(metric_d) + " / " + str(total_files))
    print("Metric E  Files at zero violations     : " + str(metric_e) + " / " + str(total_files))
    print("Metric F  Theme Compliance Coverage    : " + str(metric_f_pct) + "%"
          + "  (" + str(metric_d) + "/" + str(total_files) + " pages)"
          + "  [target: 60%+]")
    print("          Combined debt (A+B)          : " + str(metric_a + metric_b))
    print("=" * 60)
    print("Run after each sprint to measure progress.")
    print("")



def main():
    parser = argparse.ArgumentParser(description="SMRITI HTML Template Validator")
    parser.add_argument("files", nargs="*", help="HTML files to validate")
    parser.add_argument("--update-baseline", action="store_true",
                        help="Rebuild UI-GOV-006 color baseline (UI-GOV-008: decrease only, UI-GOV-009: >=5%%)")
    parser.add_argument("--force", action="store_true",
                        help="Force baseline update even if debt increases (use with caution)")
    parser.add_argument("--approve", default=None, metavar="REASON",
                        help="UI-GOV-009: Approve baseline update with <5%% reduction. Requires justification string.")
    parser.add_argument("--www-dir", default=None,
                        help="Path to www/ directory (used with --update-baseline or --metrics)")
    parser.add_argument("--no-gov006", action="store_true",
                        help="Skip UI-GOV-006 color regression check")
    parser.add_argument("--metrics", action="store_true",
                        help="Print Metric A-E sprint progress report")
    args = parser.parse_args()

    www_dir = args.www_dir or os.path.join(
        os.path.dirname(__file__), "..",
        "smriti_retail_os", "www"
    )

    # --metrics mode
    if args.metrics:
        compute_metrics(os.path.abspath(www_dir))
        sys.exit(0)

    # --update-baseline mode
    if args.update_baseline:
        if args.approve:
            build_baseline._approval = args.approve
        build_baseline(os.path.abspath(www_dir), force=args.force)
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
