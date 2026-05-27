import os
import shutil
import frappe

def sync_assets():
    print("[SMRITI] Starting hard-sync of assets into sites/assets (shared volume)...")
    
    frappe.init(site="frontend")
    frappe.connect()

    bench_path = "/home/frappe/frappe-bench"
    sites_assets_dir = os.path.join(bench_path, "sites", "assets")
    
    # Standard apps to sync
    apps = ["frappe", "erpnext", "india_compliance", "smriti_retail_os"]
    
    # 1. Remove the symlink if sites/assets is a symlink (it points to container-local /assets)
    if os.path.islink(sites_assets_dir):
        print(f"  - Removing symlink: {sites_assets_dir}")
        os.unlink(sites_assets_dir)
        os.makedirs(sites_assets_dir, exist_ok=True)
        print(f"  - Created real directory: {sites_assets_dir}")
    elif not os.path.isdir(sites_assets_dir):
        os.makedirs(sites_assets_dir, exist_ok=True)
        print(f"  - Created directory: {sites_assets_dir}")

    # 2. Copy assets.json and assets-rtl.json from bench assets dir
    bench_assets_dir = os.path.join(bench_path, "assets")
    for json_file in ["assets.json", "assets-rtl.json"]:
        src = os.path.join(bench_assets_dir, json_file)
        dst = os.path.join(sites_assets_dir, json_file)
        if os.path.exists(src):
            shutil.copy2(src, dst)
            print(f"  - Copied {json_file}")

    # 3. Copy css, js, locale directories from bench assets
    for subdir in ["css", "js", "locale"]:
        src = os.path.join(bench_assets_dir, subdir)
        dst = os.path.join(sites_assets_dir, subdir)
        if os.path.exists(src):
            if os.path.islink(dst):
                os.unlink(dst)
            elif os.path.isdir(dst):
                shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(src, dst, symlinks=False, dirs_exist_ok=True)
            print(f"  - Copied {subdir}/")

    # 4. Copy each app's public directory into sites/assets/<app>
    for app in apps:
        dst = os.path.join(sites_assets_dir, app)
        
        # Try container-local bench assets first (where bench build puts compiled output)
        bench_app_assets = os.path.join(bench_assets_dir, app)
        # Also check the app source public directory
        app_public_path = os.path.join(bench_path, "apps", app, app, "public")
        
        # Determine source: prefer bench assets (has compiled dist/) over raw public/
        if os.path.islink(bench_app_assets):
            # It's a symlink - resolve and copy from the target
            src = os.path.realpath(bench_app_assets)
        elif os.path.isdir(bench_app_assets):
            src = bench_app_assets
        elif os.path.isdir(app_public_path):
            src = app_public_path
        else:
            print(f"  - Source for {app} not found, skipping.")
            continue
        
        # Remove old destination
        if os.path.islink(dst):
            os.unlink(dst)
        elif os.path.isdir(dst):
            shutil.rmtree(dst, ignore_errors=True)
            
        print(f"  - Copying {app} assets from {src}...")
        shutil.copytree(
            src, 
            dst, 
            symlinks=False, 
            ignore=shutil.ignore_patterns("node_modules", "*.pyc", "__pycache__", ".git", ".github")
        )
        
        # Also copy the dist/ directory from bench assets if it exists separately
        bench_dist = os.path.join(bench_assets_dir, app, "dist")
        dst_dist = os.path.join(dst, "dist")
        if os.path.exists(bench_dist) and not os.path.exists(dst_dist):
            shutil.copytree(bench_dist, dst_dist, symlinks=False)
            print(f"    + Copied dist/ for {app}")
        
        print(f"    Done: {app}")
            
    print("[SMRITI] Asset sync complete. Physical files in sites/assets/ (shared volume).")

if __name__ == "__main__":
    sync_assets()
