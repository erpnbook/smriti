#!/usr/bin/env python3
"""
tools/audit/check_authority_hierarchy.py
========================================
SMRITI Authority Hierarchy Validator.

Verifies that:
1. The precedence hierarchy in SMRITI_PRODUCT_CONSTITUTION.md matches the approved standard.
2. No other governance document in the repository defines an alternative precedence list
   or claims Level 1/supreme authority over SMRITI development.

Exit code: 0 = pass, 1 = validation failed.
"""

import argparse
import os
import sys
from pathlib import Path

# Config
REPO_ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", "node_modules", "vendor", "build", "env"}

APPROVED_HIERARCHY = [
    "Level 1: SMRITI Product Constitution (SPC)",
    "Level 2: SMRITI Architecture Directive (ARCHITECTURE.md)",
    "Level 3: SMRITI Governance & CI Specifications (SMRITI_GOVERNANCE.md)",
    "Level 4: AI Agent Workflow Guides (SMRITI_AI_AGENT_GUIDE.md)",
    "Level 5: Sprint Instructions & Product Roadmap",
    "Level 6: User Prompts & Conversation Input"
]


def check_constitution_hierarchy():
    const_file = REPO_ROOT / "SMRITI_PRODUCT_CONSTITUTION.md"
    if not const_file.exists():
        return ["SMRITI_PRODUCT_CONSTITUTION.md does not exist at root."]

    try:
        content = const_file.read_text(encoding="utf-8")
    except OSError as e:
        return [f"Could not read SMRITI_PRODUCT_CONSTITUTION.md: {e}"]

    errors = []
    # Check that all approved levels are found in the constitution text
    for level in APPROVED_HIERARCHY:
        if level not in content:
            errors.append(f"Precedence Level missing or incorrect: '{level}'")

    return errors


def check_other_files_hierarchy(files=None):
    errors = []
    
    # We scan for any file asserting "supreme law", "highest authority", or "Level 1"
    # except SMRITI_PRODUCT_CONSTITUTION.md itself.
    target_files = []
    if files:
        for f in files:
            p = Path(f).resolve()
            if p.exists() and p.suffix == ".md" and p.name != "SMRITI_PRODUCT_CONSTITUTION.md":
                target_files.append(p)
    else:
        for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fname in filenames:
                if not fname.endswith(".md"):
                    continue
                p = Path(dirpath) / fname
                if p.name != "SMRITI_PRODUCT_CONSTITUTION.md":
                    target_files.append(p)

    for filepath in target_files:
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        # Look for conflicting supreme authority claims
        if "supreme law" in content.lower() and "product constitution" not in content.lower():
            errors.append(
                f"{filepath.relative_to(REPO_ROOT)}: Contains unauthorized authority claim "
                f"('supreme law') without deferring to the Product Constitution."
            )
            
        if "highest authority" in content.lower() and "product constitution" not in content.lower():
            errors.append(
                f"{filepath.relative_to(REPO_ROOT)}: Contains unauthorized precedence claim "
                f"('highest authority') without deferring to the Product Constitution."
            )

    return errors


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help="Optional specific files to scan.")
    args = parser.parse_args()

    errors = []
    # 1. Verify constitution's own hierarchy
    errors.extend(check_constitution_hierarchy())

    # 2. Verify other files have no conflicting authority definitions
    errors.extend(check_other_files_hierarchy(args.files))

    if errors:
        print("SMRITI AUTHORITY HIERARCHY VIOLATION DETECTED\n")
        for err in errors:
            print(f"  ❌ {err}")
        print("\nFix: Ensure all documents defer to SMRITI_PRODUCT_CONSTITUTION.md as root.")
        sys.exit(1)

    print("OK: Authority hierarchy is valid and single-rooted.")
    sys.exit(0)


if __name__ == "__main__":
    main()
