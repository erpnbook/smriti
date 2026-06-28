#!/usr/bin/env python3
"""
validate_tokens.py — SMRITI UI Contract Validation: CSS Token Layer

Catches the exact failure modes found in the 2026-06 token audit:
  1. Duplicate :root blocks in the same file (silent last-wins override)
  2. The same --custom-property declared more than once at the same
     nesting level (silent last-wins override)
  3. var(--token) references with no fallback where --token is not
     defined ANYWHERE in the CSS surface area scanned
  4. Hardcoded hex/rgb/rgba/hsl colors in files that are supposed to be
     token-only (configurable via TOKEN_ONLY_FILES below)

Usage:
    python3 validate_tokens.py /path/to/public/css [more/dirs ...]

Exit code 0 = clean. Exit code 1 = violations found (use in CI to block
merges, per Phase 3 of TOKEN_MIGRATION.md).

This does NOT replace human review of the design system — it only
catches mechanical contract violations of the kind that caused the
smriti_tokens.css corruption and the 17-token orphan list.
"""

import sys
import re
from pathlib import Path
from collections import defaultdict

VAR_DEF_RE = re.compile(r'^\s*(--[a-zA-Z0-9-]+)\s*:', re.MULTILINE)
VAR_USE_RE = re.compile(r'var\(\s*(--[a-zA-Z0-9-]+)\s*(,\s*([^)]+))?\)')
ROOT_BLOCK_RE = re.compile(r':root\s*{')
HARDCODED_COLOR_RE = re.compile(
    r'(?<!var\()\b(#[0-9a-fA-F]{3,8}\b|rgb\(|rgba\(|hsl\(|hsla\()'
)

# Files where every color MUST come from a var() — no raw hex/rgb allowed.
# Token-definition files themselves are intentionally excluded.
TOKEN_ONLY_FILES = set()  # populate per-project if/when Phase 3 enforcement begins

# Files explicitly exempt from "every var() must resolve in repo" because
# they are themselves the resolver/definition layer.
DEFINITION_FILES = {"smriti_tokens.css", "smriti-ui-hardening.css"}


def find_css_files(roots):
    files = []
    for root in roots:
        p = Path(root)
        if p.is_file() and p.suffix == ".css":
            files.append(p)
        elif p.is_dir():
            files.extend(sorted(p.rglob("*.css")))
    return files


def check_duplicate_root_blocks(path, text, errors):
    matches = list(ROOT_BLOCK_RE.finditer(text))
    if len(matches) > 1:
        lines = [text[:m.start()].count("\n") + 1 for m in matches]
        errors.append(
            f"{path}: {len(matches)} separate ':root {{' blocks found "
            f"(lines {lines}). Merge into a single :root block — "
            f"duplicate blocks silently override each other (last wins)."
        )


def check_duplicate_declarations(path, text, errors):
    # Walk each top-level block (:root, a class, etc.) independently so we
    # don't false-positive on the same token name legitimately appearing
    # in two different selectors' dark/light overrides.
    depth = 0
    block_start = None
    block_props = defaultdict(list)
    line_no = 1
    i = 0
    while i < len(text):
        ch = text[i]
        if ch == "\n":
            line_no += 1
        if ch == "{":
            depth += 1
            if depth == 1:
                block_start = i
                block_props = defaultdict(list)
        elif ch == "}":
            if depth == 1 and block_start is not None:
                block_text = text[block_start:i]
                for m in VAR_DEF_RE.finditer(block_text):
                    prop = m.group(1)
                    ln = text[:block_start + m.start()].count("\n") + 1
                    block_props[prop].append(ln)
                for prop, lines in block_props.items():
                    if len(lines) > 1:
                        errors.append(
                            f"{path}: '{prop}' declared {len(lines)} times "
                            f"in the same block (lines {lines}). Last "
                            f"declaration silently wins; remove the rest."
                        )
            depth -= 1
        i += 1


def collect_definitions(files):
    defined = set()
    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        for m in VAR_DEF_RE.finditer(text):
            defined.add(m.group(1))
    return defined


def check_orphaned_usages(path, text, all_defined, errors, warnings):
    for m in VAR_USE_RE.finditer(text):
        token, has_fallback = m.group(1), m.group(2)
        if token not in all_defined:
            if has_fallback:
                warnings.append(
                    f"{path}: var({token}, ...) has a fallback but '{token}' "
                    f"is not defined anywhere in the scanned CSS. Fallback "
                    f"will always be used — confirm this is intentional "
                    f"(e.g. a white-label override hook) and not a typo."
                )
            else:
                line_no = text[:m.start()].count("\n") + 1
                errors.append(
                    f"{path}:{line_no}: var({token}) used with NO fallback, "
                    f"but '{token}' is not defined anywhere in the scanned "
                    f"CSS. This declaration will be dropped as invalid by "
                    f"the browser (orphaned token)."
                )


def check_hardcoded_colors(path, text, errors):
    if path.name not in TOKEN_ONLY_FILES:
        return
    for m in HARDCODED_COLOR_RE.finditer(text):
        line_no = text[:m.start()].count("\n") + 1
        errors.append(
            f"{path}:{line_no}: hardcoded color '{m.group(0)}' found in a "
            f"token-only file. Use var(--smriti-color-*) instead."
        )


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    files = find_css_files(sys.argv[1:])
    if not files:
        print("No .css files found under the given path(s).")
        sys.exit(1)

    print(f"Scanning {len(files)} CSS file(s)...\n")

    all_defined = collect_definitions(files)

    errors = []
    warnings = []

    for f in files:
        text = f.read_text(encoding="utf-8", errors="ignore")
        check_duplicate_root_blocks(f, text, errors)
        check_duplicate_declarations(f, text, errors)
        check_orphaned_usages(f, text, all_defined, errors, warnings)
        check_hardcoded_colors(f, text, errors)

    if warnings:
        print(f"[WARNING] {len(warnings)} warning(s):\n")
        for w in warnings:
            print(f"  {w}")
        print()

    if errors:
        print(f"[ERROR] {len(errors)} error(s):\n")
        for e in errors:
            print(f"  {e}")
        print(f"\nFAILED — {len(errors)} contract violation(s) found.")
        sys.exit(1)

    print(f"[CLEAN] Clean — {len(files)} file(s), 0 errors, {len(warnings)} warning(s).")
    sys.exit(0)


if __name__ == "__main__":
    main()
