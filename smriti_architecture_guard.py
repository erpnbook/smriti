#!/usr/bin/env python3
"""
smriti_architecture_guard.py
============================
SMRITI Platform Architecture Guard.

Enforces the layered architecture defined in ARCHITECTURE.md §9:

    UI -> api -> service -> Persistence Adapter -> Platform Engine

Rules:
  - api/*.py, www/*.py, and flat *_api.py files
      MUST NOT contain persistence calls.
      (They may still `import frappe` for @frappe.whitelist() and utilities.)
  - service/*.py, services/*.py, and flat *_service.py / *_engine.py /
      *_integration.py / *_kernel.py / *_runner.py files
      MUST NOT contain persistence calls.
      (They may use frappe utilities: frappe.throw, frappe.db.exists,
      frappe.get_cached_doc, frappe.permissions, frappe.utils, etc.)
  - repositories/**, */repository/**, */adapter/** are EXEMPT.
      That is where persistence is supposed to live.

"Persistence calls" means direct Platform Engine database operations:
    frappe.get_doc(    frappe.new_doc(    frappe.db.sql(
    frappe.db.set_value(    frappe.db.commit(    frappe.db.delete(
    frappe.delete_doc(

Note: frappe.db.exists(), frappe.get_cached_doc(), frappe.get_all(), and
frappe framework utilities are NOT flagged — they are permitted in service layers.

USAGE
-----
  # Capture today's known violations as the accepted baseline (run once, commit):
  python smriti_architecture_guard.py --write-baseline

  # Ratchet mode (default, for CI/pre-commit):
  #   Passes if no NEW violations appear and no existing file gets WORSE.
  #   The backlog can only shrink — never grow — from this point forward.
  python smriti_architecture_guard.py

  # Report mode: print full progress summary, always exits 0.
  #   Use for weekly CI dashboards, sprint reviews, and progress tracking.
  python smriti_architecture_guard.py --report

  # Strict mode: fail on ANY violation, including baseline ones.
  #   Switch to this once the migration backlog is cleared.
  python smriti_architecture_guard.py --strict

Exit code: 0 = pass, 1 = violations found.

GUARDS ROADMAP
--------------
  Guard 1 (this file): Persistence Boundary Guard   — ACTIVE
  Guard 2 (planned):   Navigation Guard     — no /app/* or /desk/* in UI code
  Guard 3 (planned):   UI Vocabulary Guard  — no DocType/Workspace/Repository in user-facing text
  Guard 4 (planned):   Brand Guard          — no 'ERPNext' in page titles or footers
  Guard 5 (planned):   UX Guard             — mandatory Search/Save/Cancel/Breadcrumb on every screen
  Guard 6 (this file): UI Persistence Boundary — no frappe.* in www/ JS/HTML (ERROR MODE)
                        Flags: frappe.call, frappe.client, frappe.show_alert,
                               frappe.msgprint, frappe.set_route, frappe.new_doc
                        Compliant pattern: smriti.api.call(), smriti.notify.*, smriti.navigation.*
                        Reference: SMRITI Core Framework v1.0
"""
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
GUARD_DIR    = Path(__file__).resolve().parent
ROOT         = GUARD_DIR / "smriti_retail_os"
BASELINE_FILE = GUARD_DIR / "architecture_baseline.json"

# ── Persistence patterns (Platform Engine direct DB calls) ─────────────────
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

# ── Allowed utilities in service layers (NOT flagged) ─────────────────────
# frappe.db.exists, frappe.get_cached_doc, frappe.get_all, frappe.permissions,
# frappe.utils, frappe.throw, frappe._ — these are framework utilities, not
# persistence operations. They do not write or directly read the DB schema.

EXEMPT_DIR_MARKERS = {"repositories", "repository", "adapter"}


# ── Layer classifier ───────────────────────────────────────────────────────
def classify_layer(rel_path: Path) -> str | None:
    """Return 'api', 'service', or None (not subject to this guard)."""
    parts = rel_path.parts

    if any(p in EXEMPT_DIR_MARKERS for p in parts):
        return None

    if "tests" in parts or rel_path.name.startswith("test_"):
        return None

    if "api" in parts or "www" in parts:
        return "api"
    if "service" in parts or "services" in parts:
        return "service"

    # Flat top-level files: billing_api.py, psv_service.py, etc.
    if len(parts) == 1:
        name = rel_path.name
        if name.endswith("_api.py"):
            return "api"
        if re.search(r"(_service|_engine|_integration|_kernel|_runner)\.py$", name):
            return "service"

    return None


# ── Scanner ────────────────────────────────────────────────────────────────
def scan(root: Path) -> dict:
    """Return {relative_path_str: persistence_call_count} for all violations."""
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
            violations[str(rel).replace("\\", "/")] = hits
    return violations


# ── Baseline helpers ───────────────────────────────────────────────────────
def load_baseline() -> dict:
    """Load the violations dict from the baseline file (returns {} if absent)."""
    if BASELINE_FILE.exists():
        data = json.loads(BASELINE_FILE.read_text())
        # Support both legacy flat format and new versioned format
        raw_violations = data["violations"] if "violations" in data else data
        return {k.replace("\\", "/"): v for k, v in raw_violations.items()}
    return {}


def write_baseline(violations: dict) -> None:
    """Write violations as a versioned baseline file."""
    payload = {
        "version": 1,
        "created": datetime.now(timezone.utc).isoformat(),
        "platform": "SMRITI Retail OS",
        "engine": "ERPNext + Frappe (Platform Engine)",
        "description": (
            "Accepted baseline of known architecture boundary violations. "
            "Ratchet mode compares against this snapshot — the backlog can only shrink. "
            "Re-run with --write-baseline after each sprint to lock in progress."
        ),
        "violations": violations,
    }
    BASELINE_FILE.write_text(json.dumps(payload, indent=2, sort_keys=True))
    print(f"Baseline written -> {BASELINE_FILE}  ({len(violations)} files, "
          f"{sum(violations.values())} persistence calls)")


# ── Report helpers ─────────────────────────────────────────────────────────
def print_report(current: dict, baseline: dict) -> None:
    """Print a human-readable progress dashboard. Always exits 0."""
    total_baseline_files  = len(baseline)
    total_baseline_calls  = sum(baseline.values())
    total_current_files   = len(current)
    total_current_calls   = sum(current.values())

    cleared_files = total_baseline_files - total_current_files
    cleared_calls = total_baseline_calls - total_current_calls
    new_files     = [p for p in current if p not in baseline]
    regressed     = [(p, baseline[p], current[p]) for p in current
                     if p in baseline and current[p] > baseline[p]]

    pct_files = (cleared_files / total_baseline_files * 100) if total_baseline_files else 100
    pct_calls = (cleared_calls / total_baseline_calls * 100) if total_baseline_calls else 100

    print("=" * 64)
    print("  SMRITI Architecture Guard — Progress Report")
    print("=" * 64)
    print(f"  Layer: UI -> api -> service -> Persistence Adapter -> Platform Engine")
    print()
    print(f"  Baseline   {total_baseline_files:>4} files  {total_baseline_calls:>5} legacy calls")
    print(f"  Current    {total_current_files:>4} files  {total_current_calls:>5} legacy calls")
    if cleared_calls > 0 or cleared_files > 0:
        print(f"  Progress   {cleared_files:>4} files cleared  "
              f"({pct_files:.1f}%)   {cleared_calls:>5} calls removed  ({pct_calls:.1f}%)")
    elif cleared_calls == 0 and cleared_files == 0:
        print(f"  New Violations:    0 [OK]")
        print(f"  Legacy Violations: {total_current_calls}")
        print(f"  Status:            Boundary Maintained")
    else:
        print(f"  Progress   {abs(cleared_files):>4} files added    "
              f"({pct_files:.1f}%)   {abs(cleared_calls):>5} calls added    ({pct_calls:.1f}%)")
    print()

    if new_files:
        print(f"  [!]  {len(new_files)} NEW violation(s) since baseline:")
        for p in sorted(new_files):
            print(f"       {p}: {current[p]} call(s)  [NEW]")
        print()

    if regressed:
        print(f"  [!]  {len(regressed)} file(s) got WORSE since baseline:")
        for p, old, new in sorted(regressed, key=lambda x: -(x[2] - x[1])):
            print(f"       {p}: {old} -> {new}  [+{new - old}]")
        print()

    improved = [(p, baseline[p], current.get(p, 0))
                for p in baseline if p not in current or current[p] < baseline[p]]
    if improved:
        print(f"  [OK]  {len(improved)} file(s) improved since baseline")

    if not new_files and not regressed:
        print("  [OK]  No regressions. Architecture boundary is holding.")
    print("=" * 64)


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    # Guard: verify ROOT exists before scanning
    if not ROOT.exists():
        print(f"ERROR: SMRITI source root not found at {ROOT}")
        print("Run this script from the repository root "
              "(the directory that contains smriti_retail_os/).")
        return 2

    parser = argparse.ArgumentParser(
        description="SMRITI Architecture Guard — Persistence Boundary Checker"
    )
    parser.add_argument(
        "--write-baseline", action="store_true",
        help="Capture current violations as the accepted baseline (run once, then commit)."
    )
    parser.add_argument(
        "--strict", action="store_true",
        help="Fail on ANY violation, including baseline ones. Use after the backlog is cleared."
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Print a full progress report and exit 0. Use for dashboards and sprint reviews."
    )
    args = parser.parse_args()

    current = scan(ROOT)

    # ── Write-baseline mode ───────────────────────────────────────────────
    if args.write_baseline:
        write_baseline(current)
        return 0

    baseline = load_baseline()

    # ── Report mode ───────────────────────────────────────────────────────
    if args.report:
        print_report(current, baseline)
        # Guard 6 runs in all modes — ERROR MODE: fails the build on violations
        g6_violations = guard_6_ui_persistence()
        g6_failed = print_guard6_report(g6_violations)
        return 1 if g6_failed else 0

    # ── Strict mode ───────────────────────────────────────────────────────
    if args.strict:
        if current:
            total_calls = sum(current.values())
            print(f"ARCHITECTURE VIOLATION — {len(current)} file(s), "
                  f"{total_calls} persistence call(s) outside repository/adapter layers:\n")
            for path, count in sorted(current.items(), key=lambda kv: -kv[1]):
                print(f"  {path}: {count} call(s)")
            print(
                "\nRule: frappe.get_doc / new_doc / db.sql / db.set_value / db.commit / "
                "db.delete / delete_doc must live in a repository or adapter module only.\n"
                "Reference implementation: api/pos_profile_api.py -> "
                "services/pos_profile_service.py -> repositories/pos_profile_repository.py\n"
                "See ARCHITECTURE.md §9 and ARCHITECTURE_MIGRATION_BACKLOG.md."
            )
            return 1
        print("[OK] No architecture boundary violations found.")
        return 0

    # ── Ratchet mode (default) ────────────────────────────────────────────
    new_violations = {p: c for p, c in current.items() if p not in baseline}
    regressions    = {p: (baseline[p], current[p])
                      for p in current
                      if p in baseline and current[p] > baseline[p]}

    if new_violations or regressions:
        print("SMRITI ARCHITECTURE VIOLATION\n")
        print("Layer rule:  UI -> api -> service -> repository -> Platform Engine\n")
        if new_violations:
            print("New files with persistence calls outside repository/adapter:")
            for path, count in sorted(new_violations.items(), key=lambda kv: -kv[1]):
                print(f"  {path}: {count} call(s)  [NEW]")
        if regressions:
            print("\nFiles where persistence calls increased since baseline:")
            for path, (old, new) in sorted(regressions.items(),
                                           key=lambda kv: -(kv[1][1] - kv[1][0])):
                print(f"  {path}: {old} -> {new}  [+{new - old}]")
        print(
            "\nDo not add persistence calls to api or service layers. "
            "Move them into a repository or adapter module instead.\n"
            "Reference: api/pos_profile_api.py -> services/pos_profile_service.py "
            "-> repositories/pos_profile_repository.py\n"
            "See ARCHITECTURE.md §9 and ARCHITECTURE_MIGRATION_BACKLOG.md."
        )
        return 1

    improved = [(p, baseline[p], current.get(p, 0))
                for p in baseline if p not in current or current[p] < baseline[p]]
    if improved:
        print(f"[OK] No new violations. {len(improved)} file(s) improved since baseline — "
              f"run --write-baseline to lock in the progress.")
    else:
        print("[OK] No new architecture boundary violations.")

    # Guard 6 always runs — ERROR MODE: fails the build on violations
    g6_violations = guard_6_ui_persistence()
    g6_failed = print_guard6_report(g6_violations)
    return 1 if g6_failed else 0


# ── Guard 6 — UI Persistence Boundary (Error Mode) ───────────────────────────
# Flags any www/ HTML or JS file that calls frappe.* directly instead of smriti.*
# Status: ERROR MODE — violations WILL fail the build.
# Transition to ERROR MODE once all www/ pages are migrated to smriti.api.*

GUARD6_JS_PATTERNS = [
    (r"frappe\.call\s*\(",        "frappe.call()",        "smriti.api.call()"),
    (r"frappe\.client\b",         "frappe.client",        "smriti.api.*"),
    (r"frappe\.show_alert\s*\(",  "frappe.show_alert()",  "smriti.notify.*"),
    (r"frappe\.msgprint\s*\(",    "frappe.msgprint()",    "smriti.dialog.alert()"),
    (r"frappe\.set_route\s*\(",   "frappe.set_route()",   "smriti.navigation.go()"),
    (r"frappe\.new_doc\s*\(",     "frappe.new_doc()",     "smriti.api.save()"),
    (r"frappe\.confirm\s*\(",     "frappe.confirm()",     "smriti.dialog.confirm()"),
    (r"frappe\.prompt\s*\(",      "frappe.prompt()",      "smriti.dialog.prompt()"),
]
GUARD6_RE = [(re.compile(pat), old, new) for pat, old, new in GUARD6_JS_PATTERNS]

# Python-side: flag frappe.* ORM calls outside core/platform/
GUARD6_PY_EXEMPT = {"core/platform", "core\\platform"}
GUARD6_PY_PATTERN = re.compile(
    r"frappe\.(get_doc|get_all|new_doc|delete_doc|db\.get_value|db\.set_value|"
    r"db\.sql|db\.delete|db\.exists|enqueue|publish_realtime|cache|has_permission)\s*\("
)


def guard_6_ui_persistence() -> list:
    """
    Guard 6 — UI Persistence Boundary (Warning Mode).

    Scans:
      1. www/*.html, www/*.js — flags any frappe.* call that should be smriti.*
      2. *.py outside core/platform/ — flags frappe.* ORM calls that should
         route through smriti.core.platform

    Returns:
        list of (file, line_number, violation_description, replacement_hint) tuples
    """
    violations = []
    www_dir = ROOT / "www"

    # ── Scan 1: JS and HTML in www/ ──────────────────────────────────────────
    if www_dir.exists():
        for ext in ("*.js", "*.html"):
            for path in www_dir.rglob(ext):
                try:
                    lines = path.read_text(errors="ignore").splitlines()
                except OSError:
                    continue
                for lineno, line in enumerate(lines, 1):
                    for compiled_re, old_api, new_api in GUARD6_RE:
                        if compiled_re.search(line):
                            rel = str(path.relative_to(GUARD_DIR)).replace("\\", "/")
                            violations.append((
                                rel, lineno,
                                f"Forbidden: {old_api}",
                                f"Use: {new_api}"
                            ))
                            break  # one violation per line

    # ── Scan 2: Python files with frappe.* ORM calls outside core/platform/ ──
    for path in ROOT.rglob("*.py"):
        rel_str = str(path.relative_to(ROOT)).replace("\\", "/")
        # Exempt core/platform itself, tests, and platform_data_api (bridge layer)
        if "core/platform" in rel_str or rel_str.startswith("tests/") or \
                "/tests/" in rel_str or path.name.startswith("test_") or \
                path.name == "platform_data_api.py":
            continue
        try:
            lines = path.read_text(errors="ignore").splitlines()
        except OSError:
            continue
        for lineno, line in enumerate(lines, 1):
            if GUARD6_PY_PATTERN.search(line):
                rel = str(path.relative_to(GUARD_DIR)).replace("\\", "/")
                violations.append((
                    rel, lineno,
                    "Direct frappe.* call outside core/platform/",
                    "Route through: from smriti_retail_os.core.platform import documents, db, ..."
                ))

    return violations


def print_guard6_report(violations: list) -> bool:
    """Print a formatted Guard 6 report. Returns True if violations found."""
    print()
    print("=" * 64)
    print("  Guard 6 — UI Persistence Boundary (ERROR MODE)")
    print("=" * 64)
    if not violations:
        print("  [OK] No Guard 6 violations found.")
        print("       All scanned files use smriti.* APIs correctly.")
        return False

    # Group by file
    by_file: dict = {}
    for (fpath, lineno, violation, hint) in violations:
        by_file.setdefault(fpath, []).append((lineno, violation, hint))

    print(f"  ERROR: {len(violations)} violation(s) in {len(by_file)} file(s).")
    print(f"  Status:  Error mode — build WILL FAIL.")
    print(f"  Action:  Replace frappe.* calls with smriti.* equivalents.")
    print(f"  Guide:   public/js/smriti_core.js")
    print()
    shown = 0
    for fpath, hits in sorted(by_file.items()):
        print(f"  {fpath}  ({len(hits)} violation(s))")
        for lineno, violation, hint in hits[:5]:  # show first 5 per file
            print(f"    Line {lineno:>4}: {violation}")
            print(f"             => {hint}")
        if len(hits) > 5:
            print(f"    ... and {len(hits) - 5} more")
        shown += 1
        if shown >= 20:  # cap output at 20 files
            remaining = len(by_file) - 20
            if remaining > 0:
                print(f"  ... and {remaining} more file(s) not shown.")
            break
    print()
    print("  Migration guide: see walkthrough.md from P5 sprint.")
    print("  Platform bridge: api/platform_data_api.py")
    return True


if __name__ == "__main__":
    sys.exit(main())
