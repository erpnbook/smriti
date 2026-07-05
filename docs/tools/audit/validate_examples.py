import os
import re
from pathlib import Path

def validate_examples(docs_dir):
    errors = []
    warnings = []
    
    skip_dirs = {'node_modules', '.git', '__pycache__', '.vitepress', 'tools', 'images', 'reports', 'audit'}
    
    # Matches `## Examples` or `### Worked Example` etc.
    example_heading_pattern = re.compile(
        r'^#{2,4}\s+.*(?:example|sample|walkthrough|demo).*$', 
        re.IGNORECASE | re.MULTILINE
    )

    for root_dir, dirs, files in os.walk(docs_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root_dir, file)
                rel_path = os.path.relpath(file_path, docs_dir).replace(os.sep, '/')
                
                # Skip index files
                if file == "index.md" or file == "DOCUMENTATION_INDEX.md":
                    continue
                
                # Read content past the frontmatter
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception:
                    continue
                
                # Split off frontmatter
                body = content
                if content.startswith("---"):
                    parts = content.split("---", 2)
                    if len(parts) >= 3:
                        body = parts[2]
                
                # Check for example headings
                has_example_heading = bool(example_heading_pattern.search(body))
                
                # Check for code blocks
                # Use regex to find markdown code blocks (```python, ```bash, etc.)
                has_code_block = "```" in body
                
                if not (has_example_heading or has_code_block):
                    warnings.append({
                        "file": rel_path,
                        "check": "Missing Examples",
                        "message": "File does not contain an example heading (e.g. '## Example') or any code blocks."
                    })

    return errors, warnings

if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[3]
    docs_dir = repo_root / "docs"
    errs, warns = validate_examples(str(docs_dir))
    print(f"Errors: {len(errs)}, Warnings: {len(warns)}")
