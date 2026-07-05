import os
import sys
from pathlib import Path

# Add current folder to sys.path to allow absolute/relative imports of peers
sys.path.append(os.path.dirname(__file__))

from validate_metadata import validate_metadata
from validate_links import validate_links
from validate_duplicates import validate_duplicates
from validate_examples import validate_examples
from build_health_report import generate_report_markdown

def main():
    # Reconfigure stdout/stderr to UTF-8 to handle emojis in Windows terminals safely
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except (AttributeError, Exception):
        pass

    # Resolve paths relative to this script
    script_dir = Path(__file__).resolve().parent
    docs_dir = script_dir.parents[1]  # docs/ root
    schema_path = docs_dir / "tools" / "documentation_schema.yaml"
    
    print("==================================================")
    print(" Running SMRITI Documentation Health Audit...")
    print("==================================================")
    
    # 1. Count total markdown files (excluding node_modules, tools, .git, etc.)
    total_files = 0
    skip_dirs = {'node_modules', '.git', '__pycache__', '.vitepress', 'tools', 'images', 'reports', 'audit'}
    for root, dirs, files in os.walk(str(docs_dir)):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for f in files:
            if f.endswith(".md"):
                # Skip subfolder indexes and index.md at root
                if f == "index.md" or f == "DOCUMENTATION_INDEX.md":
                    continue
                total_files += 1
                
    if total_files == 0:
        print("No markdown documentation files found to audit.")
        sys.exit(0)

    # 2. Run validations
    errors = []
    warnings = []
    
    # Metadata Validation
    meta_errors, meta_warnings, metadata_by_file = validate_metadata(str(docs_dir), str(schema_path))
    errors.extend(meta_errors)
    warnings.extend(meta_warnings)
    
    # Link Validation
    link_errors, link_warnings = validate_links(str(docs_dir))
    errors.extend(link_errors)
    warnings.extend(link_warnings)
    
    # Duplicates Validation
    dup_errors, dup_warnings = validate_duplicates(str(docs_dir), metadata_by_file)
    errors.extend(dup_errors)
    warnings.extend(dup_warnings)
    
    # Examples Validation
    ex_errors, ex_warnings = validate_examples(str(docs_dir))
    errors.extend(ex_errors)
    warnings.extend(ex_warnings)
    
    # 3. Calculate Compliance Score
    # We define 6 check gates per file: Header block existence, Metadata fields completeness, Status validity, Link integrity, ID uniqueness, Examples presence.
    total_checks = total_files * 6
    total_violations = len(errors) + len(warnings)
    compliance_score = max(0.0, 100.0 * (total_checks - total_violations) / total_checks)
    
    # 4. Print Summary to console
    print(f"Total Documents Scanned : {total_files}")
    print(f"Merge-Blocking Errors   : {len(errors)}")
    print(f"Quality Warnings        : {len(warnings)}")
    print(f"Overall Compliance      : {compliance_score:.2f}%")
    print("--------------------------------------------------")
    
    # Print list of blocking errors to console
    if errors:
        print("\n[BLOCKER ERRORS]")
        for e in errors:
            print(f"  ❌ {e['file']}: [{e['check']}] {e['message']}")
            
    if warnings:
        print("\n[QUALITY WARNINGS]")
        for w in warnings[:10]:  # Cap warnings output in console to keep it readable
            print(f"  ⚠️ {w['file']}: [{w['check']}] {w['message']}")
        if len(warnings) > 10:
            print(f"  ... and {len(warnings) - 10} more warnings.")
            
    # 5. Generate and save the health report markdown
    report_md = generate_report_markdown(total_files, errors, warnings, compliance_score)
    reports_dir = docs_dir / "reports"
    reports_dir.mkdir(exist_ok=True)
    report_file = reports_dir / "documentation_health_report.md"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_md)
        print(f"\nSaved detailed health report to: {report_file.relative_to(docs_dir.parent)}")
    except Exception as e:
        print(f"\nFailed to save health report: {e}")
        
    print("==================================================")
    if errors:
        print(" STATUS: [FAIL] Documentation has blocking errors.")
        sys.exit(1)
    else:
        print(" STATUS: [PASS] Documentation is healthy and compliant.")
        sys.exit(0)

if __name__ == "__main__":
    main()
