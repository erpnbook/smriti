#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 4 — PSV Service File Splitter (v2)
Extracts large sections from psv_service.py into dedicated sub-service files.

Run:
    python3 scripts/split_psv_service.py [--dry-run]
"""

import os
import sys
import re
import argparse

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SMRITI = os.path.join(APP_ROOT, "smriti_retail_os")
PSV_SERVICE = os.path.join(SMRITI, "psv_service.py")

HEADER_TMPL = """\
# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/smriti_retail_os/{fname}
# @description: {desc}
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-06-20
# @version: 2.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
# NOTE: Extracted from psv_service.py (Phase 4 remediation).
#       psv_service.py re-imports all public names for backward compatibility.
#

"""


def read_source():
    with open(PSV_SERVICE, "r", encoding="utf-8") as f:
        return f.read()


def find_all_toplevel_starts(lines):
    """
    Returns dict: func_name -> line_index of the DEF line (0-indexed).
    Also returns list of (line_index, kind) for ALL top-level boundaries
    to help compute end-of-function.
    """
    func_line = {}   # name -> def line index
    boundaries = []  # [(line_idx, 'def'|'class'|'constant'|'comment_section')]

    for i, raw in enumerate(lines):
        line = raw.rstrip()
        m = re.match(r'^def (\w+)\s*\(', line)
        if m:
            func_line[m.group(1)] = i
            boundaries.append((i, "def"))
            continue
        m = re.match(r'^class (\w+)', line)
        if m:
            boundaries.append((i, "class"))
            continue
        # Top-level constants / assignment (not indented, not blank, not comment)
        if line and not line[0].isspace() and not line.startswith("#") and "=" in line:
            boundaries.append((i, "constant"))

    return func_line, boundaries


def func_extent(func_def_line, boundaries, total_lines):
    """
    Returns (start, end) line indices (inclusive) for the function at func_def_line.
    Searches backward from func_def_line to include decorators, then forward to the
    next top-level boundary.
    """
    lines_source = None  # filled externally

    # Start: walk back to include consecutive decorator/blank lines
    start = func_def_line
    # (decorators handled outside)

    # End: next top-level boundary after func_def_line
    next_boundary = total_lines
    for (bline, bkind) in boundaries:
        if bline > func_def_line:
            next_boundary = bline
            break

    end = next_boundary - 1
    # Trim trailing blank lines
    return (start, end)


def extract_funcs(source, func_names):
    """
    Extracts complete function blocks (including decorators) for each func_name.
    Returns (blocks_text, [(start, end), ...]) where ranges are SORTED ascending.
    Uses a line-scanning approach that properly handles @frappe.whitelist() decorators.
    """
    lines = source.split("\n")
    total = len(lines)

    func_line, boundaries = find_all_toplevel_starts(lines)

    # Build a lookup: for any def line, what decorators precede it?
    # A decorator block is consecutive @... lines immediately before the def
    def get_block_start(def_line):
        start = def_line
        while start > 0:
            prev = lines[start - 1].strip()
            if prev.startswith("@"):
                start -= 1
            elif prev == "":
                # Allow one blank line between two decorators / before first decorator
                # But don't consume blank lines that separate two functions
                if start >= 2 and lines[start - 2].strip().startswith("@"):
                    start -= 1
                else:
                    break
            else:
                break
        return start

    def get_block_end(def_line):
        """
        Find the last line (inclusive) of the function starting at def_line.
        Stops at the NEXT top-level boundary (def/class/constant).
        Also stops at any bare @decorator line that starts the next function.
        Trailing blank lines and dangling decorators are NOT included.
        """
        best = total - 1
        for (bline, bkind) in sorted(boundaries):
            if bline > def_line:
                best = bline - 1
                break
        # Walk backwards: remove trailing blank lines
        while best > def_line and lines[best].strip() == "":
            best -= 1
        # Also remove any trailing decorator lines that belong to the NEXT func
        while best > def_line and lines[best].strip().startswith("@"):
            best -= 1
        # Trim trailing blank lines again after stripping decorators
        while best > def_line and lines[best].strip() == "":
            best -= 1
        return best

    blocks = []
    ranges = []

    for fname in func_names:
        if fname not in func_line:
            print(f"  WARNING: '{fname}' not found in psv_service.py")
            continue
        def_line = func_line[fname]
        start = get_block_start(def_line)
        end = get_block_end(def_line)
        block_text = "\n".join(lines[start:end + 1])
        blocks.append(block_text)
        ranges.append((start, end))

    return "\n\n\n".join(blocks), sorted(ranges)


def collapse_blanks(text, max_consecutive=2):
    """Collapse > max_consecutive blank lines into max_consecutive."""
    pattern = r'\n{' + str(max_consecutive + 1) + r',}'
    replacement = "\n" * (max_consecutive + 1)
    return re.sub(pattern, replacement, text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    source = read_source()
    src_lines = source.split("\n")
    print(f"psv_service.py source: {len(src_lines)} lines")

    all_ranges = []

    # ─── 1. psv_snapshot_service.py ──────────────────────────────────────────
    snap_funcs = ["get_landing_cost", "_get_landing_cost_from_db",
                  "calculate_aging_for_variant", "get_aging_alert", "generate_snapshots"]
    snap_body, snap_ranges = extract_funcs(source, snap_funcs)
    all_ranges.extend(snap_ranges)
    snap_content = (
        HEADER_TMPL.format(
            fname="psv_snapshot_service.py",
            desc="SMRITI PSV Snapshot Service — landing cost resolution, inventory aging, and snapshot generation."
        )
        + "import frappe\n"
        + "from frappe import _\n"
        + "from frappe.utils import today, now_datetime, get_datetime\n\n\n"
        + snap_body + "\n"
    )

    # ─── 2. psv_health_service.py ────────────────────────────────────────────
    health_funcs = ["find_open_alert", "create_or_update_alert",
                    "run_psv_daily_health_check", "validate_sales_invoice_cancel"]
    health_body, health_ranges = extract_funcs(source, health_funcs)
    all_ranges.extend(health_ranges)
    health_content = (
        HEADER_TMPL.format(
            fname="psv_health_service.py",
            desc="SMRITI PSV Health Service — operational alerts, health checks, and exception management."
        )
        + "import frappe\n"
        + "from frappe import _\n"
        + "from frappe.utils import today, now_datetime\n\n"
        + "from smriti_retail_os.balance_engine import get_party_balance\n\n\n"
        + health_body + "\n"
    )

    # ─── 3. psv_analytics_service.py ─────────────────────────────────────────
    analytics_funcs = [
        "get_redistribution_suggestions", "get_channel_health_score",
        "get_sellin_sellout_summary", "get_stock_cover_risks",
        "get_channel_stock_trend", "get_inventory_productivity_metrics",
        "get_inventory_productivity_methodology",
    ]
    # Grab ACTION_ constants from source
    action_lines = [l for l in src_lines if l.startswith("ACTION_")]
    action_block = "\n".join(action_lines)

    analytics_body, analytics_ranges = extract_funcs(source, analytics_funcs)
    all_ranges.extend(analytics_ranges)
    analytics_content = (
        HEADER_TMPL.format(
            fname="psv_analytics_service.py",
            desc="SMRITI PSV Analytics Service — redistribution, WOC risks, sell-in/out, productivity metrics."
        )
        + "import frappe\n"
        + "from frappe import _\n"
        + "from frappe.utils import today, now_datetime, add_days\n\n"
        + "from smriti_retail_os.psv_snapshot_service import get_landing_cost\n\n\n"
        + action_block + "\n\n\n"
        + analytics_body + "\n"
    )

    # ─── 4. psv_migration_service.py ─────────────────────────────────────────
    migration_funcs = ["create_reversal_entry", "migrate_to_new_psv_partner"]
    migration_body, migration_ranges = extract_funcs(source, migration_funcs)
    all_ranges.extend(migration_ranges)
    migration_content = (
        HEADER_TMPL.format(
            fname="psv_migration_service.py",
            desc="SMRITI PSV Migration Service — ledger reversal and legacy PSA to Channel Partner migration."
        )
        + "import hashlib\n\n"
        + "import frappe\n"
        + "from frappe import _\n"
        + "from frappe.utils import today, now_datetime\n\n\n"
        + migration_body + "\n"
    )

    # ─── 5. Trim psv_service.py ───────────────────────────────────────────────
    trimmed_lines = list(src_lines)
    # Remove extracted ranges in reverse order (so indices stay valid)
    for start, end in sorted(all_ranges, reverse=True):
        del trimmed_lines[start:end + 1]

    # Remove ACTION_ constants (moved to analytics)
    trimmed_lines = [l for l in trimmed_lines if not l.startswith("ACTION_")]
    trimmed = "\n".join(trimmed_lines)
    trimmed = collapse_blanks(trimmed, max_consecutive=2)

    # Add re-export block for backward compatibility
    compat = (
        "\n\n\n# ─── BACKWARD-COMPAT RE-EXPORTS ──────────────────────────────────────────────\n"
        "# These names moved to dedicated sub-service modules in Phase 4 (file split).\n"
        "# Re-imported here so existing callers of psv_service.<name>() are not broken.\n\n"
        "from smriti_retail_os.psv_snapshot_service import (  # noqa: F401\n"
        "    get_landing_cost, calculate_aging_for_variant, get_aging_alert, generate_snapshots\n"
        ")\n"
        "from smriti_retail_os.psv_health_service import (  # noqa: F401\n"
        "    find_open_alert, create_or_update_alert, run_psv_daily_health_check,\n"
        "    validate_sales_invoice_cancel\n"
        ")\n"
        "from smriti_retail_os.psv_analytics_service import (  # noqa: F401\n"
        "    get_redistribution_suggestions, get_channel_health_score,\n"
        "    get_sellin_sellout_summary, get_stock_cover_risks, get_channel_stock_trend,\n"
        "    get_inventory_productivity_metrics, get_inventory_productivity_methodology,\n"
        "    ACTION_INCREASE_STOCK, ACTION_MAINTAIN, ACTION_IMPROVE_MARGIN,\n"
        "    ACTION_LIQUIDATE, ACTION_REPLENISH_URGENT\n"
        ")\n"
        "from smriti_retail_os.psv_migration_service import (  # noqa: F401\n"
        "    create_reversal_entry, migrate_to_new_psv_partner\n"
        ")\n"
    )
    trimmed = trimmed.rstrip() + compat

    # ─── Report ───────────────────────────────────────────────────────────────
    outputs = {
        "psv_snapshot_service.py": snap_content,
        "psv_health_service.py": health_content,
        "psv_analytics_service.py": analytics_content,
        "psv_migration_service.py": migration_content,
        "psv_service.py (trimmed)": trimmed,
    }
    print("\n=== Split Summary ===")
    for name, content in outputs.items():
        lc = len(content.split("\n"))
        print(f"  {name}: {lc} lines")

    if args.dry_run:
        print("\nDRY RUN — no files written.")
        return 0

    for fname, content in [
        ("psv_snapshot_service.py", snap_content),
        ("psv_health_service.py", health_content),
        ("psv_analytics_service.py", analytics_content),
        ("psv_migration_service.py", migration_content),
    ]:
        dest = os.path.join(SMRITI, fname)
        with open(dest, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"  WROTE {fname} ({len(content.split(chr(10)))} lines)")

    with open(PSV_SERVICE, "w", encoding="utf-8") as f:
        f.write(trimmed)
    tc = len(trimmed.split("\n"))
    print(f"  TRIMMED psv_service.py -> {tc} lines")

    print("\nPhase 4 split complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
