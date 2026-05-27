import os
import shutil
import frappe

def sync_assets():
    print("[SMRITI] Starting hard-sync of assets (No Symlinks)...")
    
    frappe.init(site="frontend")
    frappe.connect()

    bench_path = "/home/frappe/frappe-bench"
    assets_path = os.path.join(bench_path, "assets")
    
    # Standard apps to sync
    apps = ["frappe", "erpnext", "india_compliance", "smriti_retail_os"]
    
    # 1. Clean up app symlinks inside assets directory and copy physical files
    for app in apps:
        app_public_path = os.path.join(bench_path, "apps", app, app, "public")
        if not os.path.exists(app_public_path):
            continue
            
        target_path = os.path.join(assets_path, app)
        if os.path.islink(target_path):
            print(f"  - Unlinking symlink: {target_path}")
            os.unlink(target_path)
        elif os.path.isdir(target_path):
            shutil.rmtree(target_path, ignore_errors=True)
            
        print(f"  - Copying physical folder for {app} assets...")
        shutil.copytree(
            app_public_path, 
            target_path, 
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("node_modules", "*.pyc", "__pycache__", ".git", ".github")
        )
        
    # Ensure sites/assets points to the bench assets folder as a symlink
    sites_assets = os.path.join(bench_path, "sites", "assets")
    if os.path.islink(sites_assets):
        os.unlink(sites_assets)
    elif os.path.isdir(sites_assets):
        shutil.rmtree(sites_assets, ignore_errors=True)
        
    os.symlink(assets_path, sites_assets)
    print("[SMRITI] Asset sync complete. Real files are now in assets/ and symlinked from sites/assets.")

