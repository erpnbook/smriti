"""
DOC-AUDIT-001 — SMRITI 0-Byte Documentation Scanner
=====================================================
Governance: SMRITI_DOCUMENT_GOVERNANCE_RULE_001
Authority:  Jawahar R. Mallah, Founder & Chief Architect, AITDL
Rule:       0-byte files = FAIL before any readiness review gate
Applies to: All SMRITI modules (PSV, CGE, PDT, SFM, Themes, all future)

Usage:
    python docs/audit/doc_audit_001.py
    python docs/audit/doc_audit_001.py --path docs/
    python docs/audit/doc_audit_001.py --path docs/ --fail-on-empty

Exit codes:
    0  = PASS (no 0-byte .md files found)
    1  = FAIL (one or more 0-byte .md files found)
"""

import os
import sys
import argparse
from pathlib import Path


def scan_for_empty_docs(root_path: str, extensions: list = None) -> dict:
    """
    Scan directory tree for documentation files with 0 bytes.

    Args:
        root_path: Root directory to scan
        extensions: File extensions to check (default: ['.md'])

    Returns:
        dict with 'empty_files', 'total_files', 'pass' keys
    """
    if extensions is None:
        extensions = ['.md']

    root = Path(root_path)
    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root_path}")

    total_files = 0
    empty_files = []

    # Directories to skip
    skip_dirs = {
        'node_modules', '.git', '__pycache__', '.venv', 'venv',
        'env', 'dist', 'build', '.idea', '.vscode'
    }

    for file_path in root.rglob('*'):
        # Skip excluded directories
        if any(skip in file_path.parts for skip in skip_dirs):
            continue

        if file_path.is_file() and file_path.suffix.lower() in extensions:
            total_files += 1
            file_size = file_path.stat().st_size

            if file_size == 0:
                empty_files.append({
                    'path': str(file_path.relative_to(root)),
                    'absolute': str(file_path),
                    'size': file_size
                })

    return {
        'empty_files': empty_files,
        'total_files': total_files,
        'empty_count': len(empty_files),
        'pass': len(empty_files) == 0
    }


def print_report(result: dict, root_path: str) -> None:
    """Print audit report in SMRITI governance format."""

    print()
    print("=" * 60)
    print("  SMRITI Document Governance Audit — DOC-AUDIT-001")
    print("  Rule: SMRITI_DOCUMENT_GOVERNANCE_RULE_001")
    print("=" * 60)
    print(f"  Scan path    : {root_path}")
    print(f"  Total .md    : {result['total_files']}")
    print(f"  Empty files  : {result['empty_count']}")
    print()

    if result['pass']:
        print("  STATUS: [PASS] No 0-byte documentation files found.")
        print()
    else:
        print("  STATUS: [FAIL] 0-byte files found (treated as missing).")
        print()
        print("  Violations:")
        for f in result['empty_files']:
            print(f"    [EMPTY]  {f['path']}  (0 bytes)")
        print()
        print("  Action required before any readiness review gate:")
        print("    - Add content to each file above, OR")
        print("    - Delete the placeholder file if content is not yet ready")
        print("    - A file with 0 bytes CANNOT pass a governance review")
        print()

    print("=" * 60)
    print()


def main():
    parser = argparse.ArgumentParser(
        description="DOC-AUDIT-001: SMRITI 0-byte documentation scanner",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        '--path',
        default='docs/',
        help='Root path to scan (default: docs/)'
    )
    parser.add_argument(
        '--extensions',
        nargs='+',
        default=['.md'],
        help='File extensions to check (default: .md)'
    )
    parser.add_argument(
        '--fail-on-empty',
        action='store_true',
        default=True,
        help='Exit with code 1 if empty files found (default: True)'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )

    args = parser.parse_args()

    # Resolve path relative to repo root (where script is run from)
    scan_path = Path(args.path)
    if not scan_path.is_absolute():
        scan_path = Path.cwd() / scan_path

    try:
        result = scan_for_empty_docs(str(scan_path), args.extensions)
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print_report(result, str(scan_path))

    # Exit with appropriate code
    if args.fail_on_empty and not result['pass']:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == '__main__':
    main()
