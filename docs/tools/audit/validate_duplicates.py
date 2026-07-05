import os
from collections import defaultdict
from pathlib import Path
from validate_metadata import parse_header

def validate_duplicates(docs_dir, metadata_by_file=None):
    errors = []
    warnings = []
    
    # Map from Document ID to list of file paths
    id_map = defaultdict(list)
    # Map from lowercase Title to list of file paths
    title_map = defaultdict(list)
    # Map from basename to list of file paths
    name_map = defaultdict(list)

    if metadata_by_file is None:
        metadata_by_file = {}
        skip_dirs = {'node_modules', '.git', '__pycache__', '.vitepress', 'tools', 'images', 'reports', 'audit'}
        for root_dir, dirs, files in os.walk(docs_dir):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for file in files:
                if file.endswith(".md") and file != "index.md" and file != "DOCUMENTATION_INDEX.md":
                    file_path = os.path.join(root_dir, file)
                    rel_path = os.path.relpath(file_path, docs_dir).replace(os.sep, '/')
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        meta = parse_header(content)
                        if meta:
                            metadata_by_file[rel_path] = meta
                    except Exception:
                        pass

    for rel_path, meta in metadata_by_file.items():
        doc_id = meta.get("Document ID")
        title = meta.get("Title")
        basename = os.path.basename(rel_path).lower()

        if doc_id:
            id_map[doc_id.strip()].append(rel_path)
        if title:
            title_map[title.strip().lower()].append(rel_path)
        name_map[basename].append(rel_path)

    # 1. Validate Document IDs (Block merge if duplicates found)
    for doc_id, files in id_map.items():
        if len(files) > 1:
            errors.append({
                "file": ", ".join(files),
                "check": "Duplicate Document ID",
                "message": f"Document ID '{doc_id}' is defined in multiple files: {', '.join(files)}"
            })

    # 2. Check duplicate titles (Warning or Error)
    for title, files in title_map.items():
        if len(files) > 1:
            warnings.append({
                "file": ", ".join(files),
                "check": "Duplicate Title",
                "message": f"Multiple files share the same Title '{title}': {', '.join(files)}"
            })

    # 3. Check duplicate filenames
    for basename, files in name_map.items():
        if len(files) > 1:
            warnings.append({
                "file": ", ".join(files),
                "check": "Duplicate Filename",
                "message": f"Filename '{basename}' is repeated in multiple directories: {', '.join(files)}"
            })

    return errors, warnings

if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[3]
    docs_dir = repo_root / "docs"
    errs, warns = validate_duplicates(str(docs_dir))
    print(f"Errors: {len(errs)}, Warnings: {len(warns)}")
