import os
import re
from pathlib import Path

def validate_links(docs_dir):
    errors = []
    warnings = []
    
    skip_dirs = {'node_modules', '.git', '__pycache__', '.vitepress', 'tools', 'images'}
    
def extract_markdown_links(content):
    links = []
    start = 0
    while True:
        pos = content.find('[', start)
        if pos == -1:
            break
        end_label = content.find(']', pos)
        if end_label == -1:
            break
        
        if end_label + 1 < len(content) and content[end_label + 1] == '(':
            label = content[pos+1:end_label]
            url_start = end_label + 2
            url_end = url_start
            paren_count = 1
            while url_end < len(content) and paren_count > 0:
                char = content[url_end]
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                url_end += 1
            
            if paren_count == 0:
                url = content[url_start:url_end-1]
                is_image = (pos > 0 and content[pos-1] == '!')
                if not is_image:
                    links.append((label, url))
            start = url_end
        else:
            start = pos + 1
    return links

def validate_links(docs_dir):
    errors = []
    warnings = []
    
    skip_dirs = {'node_modules', '.git', '__pycache__', '.vitepress', 'tools', 'images', 'reports', 'audit'}

    for root_dir, dirs, files in os.walk(docs_dir):
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root_dir, file)
                rel_path = os.path.relpath(file_path, docs_dir).replace(os.sep, '/')
                
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                except Exception as e:
                    continue
                
                links = extract_markdown_links(content)
                for label, url in links:
                    url = url.strip().strip('<>')
                    
                    # 1. Check for forbidden file:/// absolute links
                    if url.startswith("file:///"):
                        errors.append({
                            "file": rel_path,
                            "check": "Absolute Link Prohibited",
                            "message": f"Link '{url}' uses absolute file:/// protocol. Must use relative links."
                        })
                        continue
                    
                    # Skip external URLs, email links, page-local anchor links, and custom protocols
                    if url.startswith(("http://", "https://", "mailto:", "#", "asset_type:", "formula:", "dictionary:", "training:", "report:")):
                        continue
                    
                    # 2. Check relative links
                    # Strip query parameters or anchors
                    path_part = url.split("?")[0].split("#")[0]
                    if not path_part:
                        continue
                    
                    # Clean up backslashes if any (though relative links should use forward slash)
                    path_part = path_part.replace("\\", "/")
                    
                    # Resolve path relative to the current file
                    current_dir = Path(root_dir)
                    target_path = (current_dir / path_part).resolve()
                    
                    # Check if file exists
                    if not target_path.exists():
                        errors.append({
                            "file": rel_path,
                            "check": "Broken Internal Link",
                            "message": f"Link to '{url}' is broken. Target file '{path_part}' does not exist."
                        })

    return errors, warnings

if __name__ == "__main__":
    repo_root = Path(__file__).resolve().parents[3]
    docs_dir = repo_root / "docs"
    errs, warns = validate_links(str(docs_dir))
    print(f"Errors: {len(errs)}, Warnings: {len(warns)}")
