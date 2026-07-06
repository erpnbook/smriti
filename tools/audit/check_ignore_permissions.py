#!/usr/bin/env python3
"""
Fails CI if a @frappe.whitelist() endpoint calls something with
ignore_permissions=True and the line above it isn't tagged
`# reviewed-ignore-permissions: <reason>`.

This turns "1,070 ignore_permissions calls, unreviewed" into a gate where
every NEW one in a real API endpoint has to be a deliberate, documented
decision instead of a silent default.

Usage: python3 tools/audit/check_ignore_permissions.py
Exit code 0 = pass, 1 = fail (prints offending file:line).
"""
import ast
import os
import sys

REVIEW_TAG = "reviewed-ignore-permissions:"
SKIP_DIRS = {"tests", "node_modules", ".git"}


def find_violations(root="smriti_retail_os"):
    violations = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            path = os.path.join(dirpath, fname)
            try:
                src = open(path, encoding="utf-8", errors="ignore").read()
                tree = ast.parse(src)
            except SyntaxError:
                continue
            lines = src.splitlines()

            for node in ast.walk(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                is_whitelisted = any(
                    (isinstance(d, ast.Attribute) and d.attr == "whitelist")
                    or (
                        isinstance(d, ast.Call)
                        and isinstance(d.func, ast.Attribute)
                        and d.func.attr == "whitelist"
                    )
                    for d in node.decorator_list
                )
                if not is_whitelisted:
                    continue

                start, end = node.lineno, node.end_lineno
                for i in range(start - 1, end):
                    line = lines[i] if i < len(lines) else ""
                    if "ignore_permissions=True" in line or "ignore_permissions = True" in line:
                        prev_line = lines[i - 1] if i > 0 else ""
                        if REVIEW_TAG not in prev_line:
                            violations.append((path, i + 1, node.name))
    return violations


def main():
    violations = find_violations()
    if violations:
        print(f"FAIL: {len(violations)} unreviewed ignore_permissions call(s) "
              f"in whitelisted endpoints:\n")
        for path, lineno, func in violations:
            print(f"  {path}:{lineno}  in {func}()")
        print(
            f"\nAdd a comment directly above the call explaining why, e.g.:\n"
            f'  # {REVIEW_TAG} system-level restore, no user doc context exists\n'
            f"  frappe.delete_doc(..., ignore_permissions=True)\n"
        )
        sys.exit(1)
    print("OK: all ignore_permissions usages in whitelisted endpoints are reviewed/tagged.")
    sys.exit(0)


if __name__ == "__main__":
    main()
