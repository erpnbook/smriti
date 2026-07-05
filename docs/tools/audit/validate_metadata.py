import os
import re
from pathlib import Path

def load_schema(schema_path):
    required = []
    optional = []
    current_list = None
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            for line in f:
                line_str = line.strip()
                if line_str.startswith("required:"):
                    current_list = required
                elif line_str.startswith("optional:"):
                    current_list = optional
                elif line_str.startswith("-") and current_list is not None:
                    val = line_str.split("-", 1)[1].strip().strip('"').strip("'")
                    current_list.append(val)
    except Exception as e:
        # Fallback to hardcoded list if schema fails to load
        required = [
            "Document ID", "Title", "Owner", "Audience", "Module", 
            "Version", "Status", "Primary Document", "Depends On", 
            "Related Modules", "Last Updated", "Last Reviewed", 
            "AI Generated", "Reviewed By"
        ]
    return required, optional

def parse_header(content):
    if not content.startswith("---"):
        return None
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    header_text = parts[1]
    metadata = {}
    for line in header_text.splitlines():
        if ":" in line:
            key, val = line.split(":", 1)
            key = key.strip().strip('"').strip("'")
            val = val.strip().strip('"').strip("'")
            metadata[key] = val
    return metadata

def validate_metadata(docs_dir, schema_path):
    required_fields, _ = load_schema(schema_path)
    allowed_statuses = {"Draft", "Review", "Approved", "Active", "Deprecated", "Archived", "Frozen"}
    
    errors = []
    warnings = []
    metadata_by_file = {}

    skip_dirs = {'node_modules', '.git', '__pycache__', '.vitepress', 'tools', 'images', 'reports', 'audit'}
    
    for root_dir, dirs, files in os.walk(docs_dir):
        # Exclude skip directories
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root_dir, file)
                rel_path = os.path.relpath(file_path, docs_dir).replace(os.sep, '/')
                
                # Skip generated index files at root or folder index files for metadata checks
                if file == "index.md" or file == "DOCUMENTATION_INDEX.md":
                    continue
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    errors.append({
                        "file": rel_path,
                        "check": "Read Error",
                        "message": f"Could not read file: {e}"
                    })
                    continue
                
                metadata = parse_header(content)
                if metadata is None:
                    errors.append({
                        "file": rel_path,
                        "check": "Missing Metadata Header",
                        "message": "File does not start with a valid YAML '---' frontmatter block."
                    })
                    continue
                
                metadata_by_file[rel_path] = metadata
                
                # Check for missing required fields
                for field in required_fields:
                    if field not in metadata:
                        errors.append({
                            "file": rel_path,
                            "check": "Missing Field",
                            "message": f"Required metadata field '{field}' is missing."
                        })
                    elif not metadata[field]:
                        # Depends On and Related Modules can be empty strings, others should have values
                        if field not in {"Depends On", "Related Modules"}:
                            errors.append({
                                "file": rel_path,
                                "check": "Empty Field",
                                "message": f"Required metadata field '{field}' is empty."
                            })

                # Check for valid status
                status = metadata.get("Status")
                if status and status not in allowed_statuses:
                    errors.append({
                        "file": rel_path,
                        "check": "Invalid Status",
                        "message": f"Status '{status}' is invalid. Must be one of: {', '.join(allowed_statuses)}"
                    })
                
                # Check for revision history in metadata/changes
                # Warnings gates
                if "Related Modules" not in metadata:
                    warnings.append({
                        "file": rel_path,
                        "check": "Missing Related Modules",
                        "message": "Field 'Related Modules' is missing from header."
                    })
                
                # Check for revision history table in content
                if "## Revision History" not in content:
                    warnings.append({
                        "file": rel_path,
                        "check": "Missing Revision History Table",
                        "message": "Document is missing a '## Revision History' section."
                    })

    return errors, warnings, metadata_by_file

if __name__ == "__main__":
    # Test script locally
    repo_root = Path(__file__).resolve().parents[3]
    docs_dir = repo_root / "docs"
    schema = docs_dir / "tools" / "documentation_schema.yaml"
    errs, warns, _ = validate_metadata(str(docs_dir), str(schema))
    print(f"Errors: {len(errs)}, Warnings: {len(warns)}")
