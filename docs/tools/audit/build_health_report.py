import datetime

def generate_report_markdown(total_files, errors, warnings, compliance_score):
    report = []
    report.append("# Documentation Health Report\n")
    report.append(f"**Date**: {datetime.date.today().isoformat()}  ")
    report.append(f"**Overall Compliance**: {compliance_score:.1f}%\n")
    
    report.append("## Summary Metrics\n")
    report.append("| Metric | Value | Status |")
    report.append("| --- | --- | --- |")
    report.append(f"| Total Documents Scanned | {total_files} | - |")
    
    # Calculate duplicate errors
    duplicate_errors = sum(1 for e in errors if "Duplicate" in e["check"])
    report.append(f"| Duplicate IDs | {duplicate_errors} | {'❌ FAIL' if duplicate_errors > 0 else '✅ PASS'} |")
    
    # Calculate broken link errors
    broken_links = sum(1 for e in errors if "Link" in e["check"])
    report.append(f"| Broken Links | {broken_links} | {'❌ FAIL' if broken_links > 0 else '✅ PASS'} |")
    
    # Calculate missing metadata
    missing_metadata = sum(1 for e in errors if "Metadata" in e["check"] or "Field" in e["check"])
    report.append(f"| Missing Metadata | {missing_metadata} | {'❌ FAIL' if missing_metadata > 0 else '✅ PASS'} |")
    
    # Calculate missing examples
    missing_examples = sum(1 for w in warnings if "Examples" in w["check"])
    report.append(f"| Missing Examples | {missing_examples} | {'⚠️ Warning' if missing_examples > 0 else '✅ PASS'} |")
    
    # Calculate missing revision history
    missing_rev_hist = sum(1 for w in warnings if "Revision" in w["check"])
    report.append(f"| Missing Revision History | {missing_rev_hist} | {'⚠️ Warning' if missing_rev_hist > 0 else '✅ PASS'} |")
    
    report.append("\n---\n")
    
    if errors:
        report.append("## ❌ Block Merge Violations (Errors)\n")
        report.append("These violations must be resolved before changes can be merged.\n")
        report.append("| File | Check Gate | Violation Detail |")
        report.append("| --- | --- | --- |")
        for e in errors:
            report.append(f"| `{e['file']}` | **{e['check']}** | {e['message']} |")
        report.append("")
    else:
        report.append("## ✅ Block Merge Violations (Errors)\n")
        report.append("No blocking violations found. Documentation is clear for merge.\n")
        
    if warnings:
        report.append("## ⚠️ Warnings & Improvements\n")
        report.append("These items should be addressed to improve quality but will not block merges.\n")
        report.append("| File | Check Gate | Quality Suggestion |")
        report.append("| --- | --- | --- |")
        for w in warnings:
            report.append(f"| `{w['file']}` | *{w['check']}* | {w['message']} |")
        report.append("")
        
    return "\n".join(report)
