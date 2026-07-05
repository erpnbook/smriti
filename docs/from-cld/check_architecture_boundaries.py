#!/usr/bin/env python3
"""
SMRITI architecture boundary checker.

Enforces the rule documented in ARCHITECTURE.md §9, refined as follows:

  - api/*.py, www/*.py, and flat top-level *_api.py files
      MUST NOT contain persistence calls (they may still `import frappe`
      for @frappe.whitelist() and similar decorators/utilities).
  - services/*.py and flat top-level *_service.py / *_engine.py /
      *_integration.py / *_kernel.py files
      MUST NOT contain persistence calls either. They may use frappe
      framework utilities (frappe.throw, frappe.db.exists,
      frappe.get_cached_doc, frappe.permissions, frappe.utils, etc).
  - repositories/**, */repository/**, */adapter/** are exempt — that's
      where persistence is supposed to live.

"Persistence calls" = frappe.get_doc(, frappe.new_doc(, frappe.db.sql(,
frappe.db.set_value(, frappe.db.commit(, frappe.db.delete(,
frappe.delete_doc(.

USAGE
-----
  # One-time: capture today's known violations so CI doesn't break on
  # legacy code. Run this once, commit the resulting baseline file.
  python3 check_architecture_boundaries.py --write-baseline

  # Normal CI / pre-commit run: fails if there are NEW violations, or if
  # an existing baseline file's violation count went UP. Never fails on
  # baseline files whose count went down or stayed flat -- the backlog
  # can only shrink without extra config.
  python3 check_architecture_boundaries.py

  # Strict mode: fail on ANY violation, including baseline ones.
  # Use this once the migration backlog is cleared.
  python3 check_architecture_boundaries.py --strict

Exit code 0 = pass, 1 = violations found.
"""
import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent / "smriti_retail_os"
BASELINE_FILE = Path(__file__).resolve().parent / "architecture_baseline.json"

PERSISTENCE_PATTERNS = [
    r"frappe\.get_doc\(",
    r"frappe\.new_doc\(",
    r"frappe\.db\.sql\(",
    r"frappe\.db\.set_value\(",
    r"frappe\.db\.commit\(",
    r"frappe\.db\.delete\(",
    r"frappe\.delete_doc\(",
]
PERSIST_RE = re.compile("|".join(PERSISTENCE_PATTERNS))

EXEMPT_DIR_MARKERS = {"repositories", "repository", "adapter"}


def classify_layer(rel_path: Path) -> str | None:
    """Return 'api', 'service', or None (not covered by this rule)."""
    parts = rel_path.parts

    if any(p in EXEMPT_DIR_MARKERS for p in parts):
        return None

    if "tests" in parts or rel_path.name.startswith("test_"):
        return None

    if "api" in parts or "www" in parts:
        return "api"
    if "service" in parts or "services" in parts:
        return "service"

    # flat top-level files, e.g. billing_api.py, psv_service.py
    if len(parts) == 1:
        name = rel_path.name
        if name.endswith("_api.py"):
            return "api"
        if re.search(r"(_service|_engine|_integration|_kernel|_runner)\.py$", name):
            return "service"

    return None


def scan(root: Path) -> dict:
    """Return {relative_path: persistence_call_count} for all violations."""
    violations = {}
    for path in root.rglob("*.py"):
        rel = path.relative_to(root)
        layer = classify_layer(rel)
        if layer is None:
            continue
        try:
            text = path.read_text(errors="ignore")
        except OSError:
            continue
        hits = len(PERSIST_RE.findall(text))
        if hits > 0:
            violations[str(rel)] = hits
    return violations


def load_baseline() -> dict:
    if BASELINE_FILE.exists():
        return json.loads(BASELINE_FILE.read_text())
    return {}


def write_baseline(violations: dict) -> None:
    BASELINE_FILE.write_text(json.dumps(violations, indent=2, sort_keys=True))
    print(f"Baseline written: {BASELINE_FILE} ({len(violations)} files)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--write-baseline", action="store_true",
                         help="Capture current violations as the accepted baseline.")
    parser.add_argument("--strict", action="store_true",
                         help="Fail on any violation, including baseline ones.")
    args = parser.parse_args()

    current = scan(ROOT)

    if args.write_baseline:
        write_baseline(current)
        return 0

    if args.strict:
        if current:
            print(f"ARCHITECTURE VIOLATION: {len(current)} file(s) contain persistence "
                  f"calls outside repositories/adapter layers:\n")
            for path, count in sorted(current.items(), key=lambda kv: -kv[1]):
                print(f"  {path}: {count} persistence call(s)")
            print("\nMove persistence (frappe.get_doc/new_doc/db.sql/db.set_value/"
                  "db.commit/db.delete/delete_doc) into a repository or adapter module. "
                  "See ARCHITECTURE.md §9 and ARCHITECTURE_MIGRATION_BACKLOG.md.")
            return 1
        print("No architecture boundary violations found.")
        return 0

    baseline = load_baseline()
    new_violations = {}
    regressions = {}

    for path, count in current.items():
        if path not in baseline:
            new_violations[path] = count
        elif count > baseline[path]:
            regressions[path] = (baseline[path], count)

    if new_violations or regressions:
        print("ARCHITECTURE VIOLATION\n")
        if new_violations:
            print("New files with persistence calls outside repositories/adapter:")
            for path, count in sorted(new_violations.items(), key=lambda kv: -kv[1]):
                print(f"  {path}: {count} persistence call(s)  [NEW]")
        if regressions:
            print("\nFiles where persistence calls increased since baseline:")
            for path, (old, new) in sorted(regressions.items(), key=lambda kv: -(kv[1][1] - kv[1][0])):
                print(f"  {path}: {old} -> {new}  [+{new - old}]")
        print("\nUse api -> service -> repository/adapter (see pos_profile module for "
              "the reference implementation). If this is deliberate legacy code being "
              "migrated in place, do not add new persistence calls to it here -- move "
              "the ones you touch into a repository instead.")
        return 1

    improved = {p: (baseline[p], current.get(p, 0)) for p in baseline
                if p not in current or current[p] < baseline[p]}
    if improved:
        print(f"No new violations. {len(improved)} file(s) improved since baseline "
              f"-- consider running --write-baseline to lock in the progress.")
    else:
        print("No new architecture boundary violations found.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
