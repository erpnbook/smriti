#!/usr/bin/env python3
"""
tools/audit/check_phantom_references.py
=======================================
SMRITI Markdown Phantom Reference Linter.

Scans Markdown (.md) files in the repository for links, and verifies
that the target files actually exist on disk.
Specifically, it intercepts:
- Absolute file:/// links (e.g., file:///D:/Smriti_Retail_OS/SMRITI_PRODUCT_CONSTITUTION.md)
- Relative links (e.g., ./docs/08-architecture/DESIGN_SYSTEM.md)
- Root-relative links (e.g., SMRITI_GOVERNANCE.md)

Exit code: 0 = pass, 1 = phantom references found.
"""

import argparse
import os
import re
import sys
from pathlib import Path

# Config
REPO_ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", "node_modules", "vendor", "build", "env"}
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def normalize_link_path(link: str, current_file: Path) -> Path | None:
    """Normalizes a markdown link string to a target Path on disk, or returns None."""
    # Ignore web/URL links
    if link.startswith(("http://", "https://", "mailto:", "#", "asset_type:", "formula:", "dictionary:", "training:", "report:")):
        return None

    # Handle file:/// absolute Windows/Unix paths
    if link.startswith("file:///"):
        cleaned = link.replace("file:///", "")
        # Under windows, paths like D:/Smriti_Retail_OS/... or /D:/Smriti_Retail_OS/...
        if cleaned.startswith("/") and len(cleaned) > 2 and cleaned[2] == ":":
            cleaned = cleaned[1:]
        path = Path(cleaned)
        # Verify it points to something inside the repo root, or resolve relative
        return path

    # Resolve relative to the current file
    return (current_file.parent / link.split("#")[0]).resolve()


def scan_file(filepath: Path):
    violations = []
    try:
        content = filepath.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return violations

    lines = content.splitlines()
    for idx, line in enumerate(lines, start=1):
        for match in LINK_RE.finditer(line):
            link_target = match.group(1).strip()
            resolved_path = normalize_link_path(link_target, filepath)
            if resolved_path is not None:
                if not resolved_path.exists():
                    try:
                        rel_source = filepath.relative_to(REPO_ROOT)
                    except ValueError:
                        rel_source = filepath
                    violations.append((rel_source, idx, link_target, resolved_path))
    return violations


def scan_markdown_files(files=None):
    violations = []
    if files:
        for f in files:
            path = Path(f).resolve()
            if path.exists() and path.suffix == ".md":
                violations.extend(scan_file(path))
    else:
        for dirpath, dirnames, filenames in os.walk(REPO_ROOT):
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]

            for fname in filenames:
                if not fname.endswith(".md"):
                    continue
                violations.extend(scan_file(Path(dirpath) / fname))
    return violations


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help="Optional specific files to scan.")
    args = parser.parse_args()

    violations = scan_markdown_files(args.files)
    if violations:
        print("SMRITI PHANTOM REFERENCE VIOLATION DETECTED\n")
        print(f"Found {len(violations)} broken link(s) referencing non-existent files:\n")
        for source, line, link, resolved in violations:
            print(f"  {source}:{line} -> '{link}'")
            print(f"    Resolved Path: {resolved}")
        print("\nFix: Ensure the target file exists or correct the link path.")
        sys.exit(1)

    print("OK: All markdown link references exist on disk.")
    sys.exit(0)


if __name__ == "__main__":
    main()
