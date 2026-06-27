# -*- coding: utf-8 -*-
#
# @file: scripts/fix_boilerplate_headers.py
# @description: Utility script to clean up boilerplate headers and replace descriptions.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 1.8.6
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 3 — Boilerplate Header Cleanup
Replaces the wrong @description: "Handles user login, registration, and JWT token generation"
in ~139 Python files with accurate descriptions derived from the file's path and purpose.

Run:
    python3 scripts/fix_boilerplate_headers.py [--dry-run] [--verbose]
"""

import os
import sys
import re
import argparse

APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WRONG_DESC = "Handles user login, registration, and JWT token generation"
BOILERPLATE_PATTERN = re.compile(
    r'(#\s*@description:\s*)' + re.escape(WRONG_DESC),
    re.IGNORECASE
)

# ── Description derivation map ─────────────────────────────────────────────────
# Maps relative path fragments to accurate descriptions.
# Checked in ORDER — first match wins.

PATH_DESCRIPTIONS = [
    # Tests
    ("tests/test_license.py",          "Unit tests for SMRITI License Key Validator — fail-closed behaviour"),
    ("tests/test_billing_api.py",       "Unit tests for SMRITI Billing API — invoice creation and payment flows"),
    ("tests/test_barcode_api.py",       "Unit tests for SMRITI Barcode API — item lookup and scan processing"),
    ("tests/test_psv_phase1_1.py",      "Integration tests for PSV Phase 1 — channel stock dispatch and sell-out"),
    ("tests/test_psv_phase1_2.py",      "Integration tests for PSV Phase 1 — balance, reorder, and snapshot"),
    ("tests/test_psv.py",               "Unit tests for PSV service — ledger, WOC, and redistribution"),
    ("tests/test_audit_remediation.py", "Audit remediation regression tests — security, perf, and doc checks"),
    ("tests/test_audit_fixes.py",       "Audit fix verification tests — validates remediation patches"),
    ("tests/test_cge_rules.py",         "Unit tests for CGE business rules — commission and pricing engines"),
    ("tests/test_cge_service.py",       "Unit tests for CGE service layer — channel gross earnings processing"),
    ("tests/test_cge_generic.py",       "Generic CGE test cases — edge cases and boundary conditions"),
    ("tests/test_cge_v2_constraints.py","CGE v2 constraint tests — data integrity and rule validation"),
    ("tests/test_item_master_api.py",   "Unit tests for SMRITI Item Master API — product and variant management"),
    ("tests/test_inventory_api.py",     "Unit tests for SMRITI Inventory API — stock queries and adjustments"),
    ("tests/test_reports.py",           "Unit tests for SMRITI Reports API — report generation and filters"),
    ("tests/test_purchase_api.py",      "Unit tests for SMRITI Purchase API — GRN and purchase order processing"),
    ("tests/test_transaction_kernel.py","Unit tests for SMRITI Transaction Kernel — core retail transaction logic"),
    ("tests/test_sizewise_invoice.py",  "Unit tests for SMRITI Sizewise Invoice — size-grouped billing"),
    ("tests/test_backup_security_hotfix.py", "Security regression tests for backup API hardening"),
    ("tests/test_branding_integrity.py","Branding integrity tests — SMRITI UI consistency checks"),
    ("tests/test_business_dictionary.py","Unit tests for SMRITI Business Dictionary (Sprint 3 KGF)"),
    ("tests/test_explain_modal.py",     "Unit tests for SMRITI Explain Engine — ⓘ modal content verification"),
    ("tests/test_formula_registry.py",  "Unit tests for SMRITI Formula Registry — formula CRUD and lookup"),
    ("tests/test_knowledge_center.py",  "Unit tests for SMRITI Knowledge Center — search and content APIs"),
    ("tests/test_pdt.py",               "Unit tests for SMRITI Product Digital Twin (PDT) dashboard"),
    ("tests/test_psv_analysis.py",      "Unit tests for PSV analytics — coverage, aging, and health score"),
    ("tests/test_psv_ledger.py",        "Unit tests for PSV Ledger Entry — balance and transaction accuracy"),
    ("tests/test_psv_upload.py",        "Unit tests for PSV party sales upload processing"),
    ("tests/test_hooks.py",             "Unit tests for SMRITI hooks_logic — event-driven lifecycle checks"),
    ("tests/test_company_api.py",       "Unit tests for SMRITI Company API — company settings and CRUD"),
    ("tests/benchmark_cge.py",          "Performance benchmark tests for CGE rule evaluation engine"),

    # API
    ("api/help_api.py",                 "SMRITI Knowledge Center API — search, manuals, formulas, dictionary"),
    ("api/license_api.py",              "SMRITI License Management API — license activation and status"),
    ("api/payment_api.py",              "SMRITI Payment API — payment recording and reconciliation"),
    ("api/golive_api.py",               "SMRITI Go-Live API — setup completion and onboarding checks"),
    ("api/coming_soon_api.py",          "SMRITI Coming Soon registry API — feature readiness tracking"),

    # Services
    ("services/knowledge_service.py",   "SMRITI Knowledge Center service — content indexing and retrieval"),
    ("services/pdt_service.py",         "SMRITI Product Digital Twin service — SKU analytics and health scores"),

    # CGE
    ("cge/api/cge_api.py",              "SMRITI CGE API — channel gross earnings endpoints"),
    ("cge/service/cge_service.py",      "SMRITI CGE service — commission calculation and rule engine"),

    # License
    ("license/key_validator.py",        "SMRITI License Key Validator — HMAC-SHA256 key generation and validation"),

    # Main API modules (root level)
    ("billing_api.py",                  "SMRITI Billing API — sales invoice creation, payment, and receipt generation"),
    ("barcode_api.py",                  "SMRITI Barcode API — item/variant lookup, barcode scan processing"),
    ("reports_api.py",                  "SMRITI Reports API — inventory, sales, and PSV report generation"),
    ("psv_service.py",                  "SMRITI PSV Service — channel stock ledger, WOC, and redistribution engine"),
    ("psv_api.py",                      "SMRITI PSV API — channel partner stock visibility endpoints"),
    ("item_master_api.py",              "SMRITI Item Master API — product, variant, and category management"),
    ("inventory_api.py",                "SMRITI Inventory API — stock balance queries and adjustment processing"),
    ("purchase_api.py",                 "SMRITI Purchase API — GRN receipt, purchase order, and supplier management"),
    ("master_api.py",                   "SMRITI Master Data API — customers, suppliers, and general master CRUD"),
    ("company_api.py",                  "SMRITI Company API — company settings, address, and multi-company support"),
    ("security_api.py",                 "SMRITI Security API — audit log, access control, and compliance checks"),
    ("backup_api.py",                   "SMRITI Backup API — database export, restore, and schedule management"),
    ("platform_api.py",                 "SMRITI Platform API — configuration, feature flags, and system settings"),
    ("setup_wizard_api.py",             "SMRITI Setup Wizard API — guided company and store onboarding"),
    ("shift_api.py",                    "SMRITI Shift API — cash register open/close and shift reconciliation"),
    ("sizewise_invoice_api.py",         "SMRITI Sizewise Invoice API — size-grouped retail billing"),
    ("transaction_kernel.py",           "SMRITI Transaction Kernel — core retail transaction processing engine"),
    ("balance_engine.py",               "SMRITI Balance Engine — ledger balance aggregation and reconciliation"),
    ("import_itemaster.py",             "SMRITI Item Master Import — bulk item/variant CSV import processor"),
    ("setup_demo_company.py",           "SMRITI Demo Company Setup — seeds a sample company for demonstration"),
    ("hooks_logic.py",                  "SMRITI hooks_logic — Frappe lifecycle event handlers and middleware"),
    ("hooks.py",                        "SMRITI hooks — Frappe hook registrations for apps, events, and overrides"),
    ("boot.py",                         "SMRITI boot — Frappe boot hooks, session info, and route guard"),

    # Utils
    ("utils/invoice_utils.py",          "SMRITI Invoice Utilities — shared invoice formatting and computation helpers"),

    # WWW pages (auth + context controllers)
    ("www/smriti_login.py",             "SMRITI Login page controller — session validation and auth redirect"),
    ("www/smriti_safe.py",              "SMRITI Safe page controller — authenticated context provider"),
    ("www/index.py",                    "SMRITI root index controller — entry-point redirect and session check"),
    ("www/smriti-cge.py",               "SMRITI CGE page controller — channel gross earnings UI context"),
    ("www/smriti-coming-soon.py",       "SMRITI Coming Soon page controller — feature roadmap display"),
    ("www/smriti-dictionary.py",        "SMRITI Business Dictionary page controller — KGF term lookup context"),
    ("www/smriti-formula-registry.py",  "SMRITI Formula Registry page controller — KGF formula display context"),
    ("www/smriti-go-live.py",           "SMRITI Go-Live page controller — onboarding completion UI context"),
    ("www/smriti-license.py",           "SMRITI License page controller — license key activation UI context"),
    ("www/brand_master.py",             "SMRITI Brand Master page controller — brand management UI context"),
    ("www/category_master.py",          "SMRITI Category Master page controller — product category UI context"),
    ("www/psv_dashboard.py",            "SMRITI PSV Dashboard page controller — channel stock UI context"),
    ("www/cge_generic.py",              "SMRITI CGE Generic page controller — CGE UI context and auth"),
    ("www/scheme_creator.py",           "SMRITI Scheme Creator page controller — pricing scheme UI context"),
    ("www/supplier_returns.py",         "SMRITI Supplier Returns page controller — returns management UI context"),

    # Page
    ("page/smriti_cge/smriti_cge.py",  "SMRITI CGE Frappe page — CGE desk page controller"),
    ("page/smriti_cge/__init__.py",     "SMRITI CGE page package init"),

    # Doctype stubs
    ("doctype/",                         "SMRITI DocType controller — Frappe document lifecycle handlers"),

    # Report stubs
    ("report/",                          "SMRITI Report controller — Frappe query report definition"),

    # Patches
    ("patches/seed_default_formulas.py", "SMRITI Formula Registry seed patch — populates core formula definitions"),
    ("patches/seed_default_terms.py",    "SMRITI Business Dictionary seed patch — populates KGF business terms"),
    # Tests (seed/utility)
    ("tests/seed_psv_uat.py",           "SMRITI PSV UAT seed — seeds channel partner test data and runs validation"),

    # Verification scripts
    ("verify_deep_audit.py",            "SMRITI deep audit verification — end-to-end compliance checks"),
    ("test_redirect.py",                "SMRITI redirect test — boot.py route guard verification"),
    ("test_db.py",                      "Direct database connection verification utility for SMRITI Retail OS"),

    # Scripts
    ("scripts/test_license_standalone.py", "Standalone test runner for SMRITI License Key Validator fail-closed behaviour"),
    ("scripts/test_psv_imports.py",      "Standalone test utility for PSV split service file import verification"),
    ("scripts/fix_boilerplate_headers.py", "Utility script to clean up boilerplate headers and replace descriptions"),
    ("scripts/",                         "SMRITI maintenance script — development and operations utility"),
]
def derive_description(rel_path: str) -> str:
    """
    Derive an accurate description for a Python file based on its relative path.
    Returns the first match from PATH_DESCRIPTIONS or a generic fallback.
    """
    rel_norm = rel_path.replace("\\", "/")
    for fragment, description in PATH_DESCRIPTIONS:
        fragment_norm = fragment.replace("\\", "/")
        if fragment_norm in rel_norm:
            return description

    # Generic fallback by module type
    if "/doctype/" in rel_norm:
        # Extract the doctype name
        parts = rel_norm.split("/doctype/")
        if len(parts) > 1:
            dt_parts = parts[1].strip("/").split("/")
            dt_name = dt_parts[0].replace("_", " ").title() if dt_parts else "Unknown"
            return f"SMRITI {dt_name} DocType controller"
    if "/report/" in rel_norm:
        parts = rel_norm.split("/report/")
        if len(parts) > 1:
            rpt_parts = parts[1].strip("/").split("/")
            rpt_name = rpt_parts[0].replace("_", " ").title() if rpt_parts else "Unknown"
            return f"SMRITI {rpt_name} report definition"
    if "/__init__.py" in rel_norm:
        module = rel_norm.split("/")[-2].replace("_", " ").title()
        return f"SMRITI {module} package initialisation"
    if "/tests/" in rel_norm:
        test_name = rel_norm.split("/")[-1].replace(".py", "").replace("_", " ").title()
        return f"SMRITI {test_name} — unit and integration test suite"

    # Last resort
    filename = os.path.basename(rel_norm).replace(".py", "").replace("_", " ").title()
    return f"SMRITI {filename} — retail operating system module"


def fix_file(file_path: str, rel_path: str, dry_run: bool, verbose: bool) -> bool:
    """Fix boilerplate header in a single file. Returns True if changed."""
    try:
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except Exception as e:
        print(f"  ERROR reading {rel_path}: {e}")
        return False

    if WRONG_DESC not in content:
        return False

    new_desc = derive_description(rel_path)
    new_content = BOILERPLATE_PATTERN.sub(
        lambda m: m.group(1) + new_desc,
        content
    )

    if new_content == content:
        return False

    if verbose:
        print(f"  FIX  {rel_path}")
        print(f"       → {new_desc}")

    if not dry_run:
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
        except Exception as e:
            print(f"  ERROR writing {rel_path}: {e}")
            return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Fix boilerplate @description headers")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without writing")
    parser.add_argument("--verbose", action="store_true", help="Show each file and its new description")
    args = parser.parse_args()

    changed = 0
    errors = 0
    scanned = 0

    print(f"{'DRY RUN — ' if args.dry_run else ''}Scanning {APP_ROOT} ...")
    print("=" * 70)

    ignore_dirs = {"__pycache__", "validation_reports", "client_tools", ".git", "node_modules", "overrides", "rollback"}

    for dirpath, dirnames, filenames in os.walk(APP_ROOT):
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]
        for fname in filenames:
            if not fname.endswith(".py"):
                continue
            full_path = os.path.join(dirpath, fname)
            rel = os.path.relpath(full_path, APP_ROOT)
            scanned += 1
            if fix_file(full_path, rel, args.dry_run, args.verbose):
                changed += 1

    print("=" * 70)
    print(f"Scanned:  {scanned}")
    print(f"Changed:  {changed}")
    print(f"Errors:   {errors}")
    if args.dry_run:
        print("DRY RUN — no files written.")
    else:
        print(f"✅ Boilerplate cleanup complete. {changed} files updated.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
