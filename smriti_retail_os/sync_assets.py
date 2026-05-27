import os
import shutil


def sync_assets():
    """
    Hard-syncs SMRITI Retail OS and all core app assets from the app's
    public/ directory (and bench/assets/) into the shared sites/assets volume.

    Called automatically in THREE places so manual runs are NEVER needed:
      1. Fresh install  — via pwd.yml create-site service
      2. bench migrate  — via after_migrate hook in hooks.py
      3. Container boot — via backend entrypoint startup script in pwd.yml

    No frappe.init() required — runs standalone from bash or Python context.
    """
    _run_sync()


def _run_sync():
    print("[SMRITI] Starting hard-sync of assets into sites/assets (shared volume)...")

    bench_path       = os.environ.get("BENCH_PATH", "/home/frappe/frappe-bench")
    sites_assets_dir = os.path.join(bench_path, "sites", "assets")
    bench_assets_dir = os.path.join(bench_path, "assets")

    # Apps whose assets must be present in the shared volume
    apps = ["frappe", "erpnext", "india_compliance", "smriti_retail_os"]

    # ── Step 1: Ensure sites/assets is a real directory (never a symlink) ──
    if os.path.islink(sites_assets_dir):
        print(f"  - Removing symlink: {sites_assets_dir}")
        os.unlink(sites_assets_dir)
        os.makedirs(sites_assets_dir, exist_ok=True)
        print(f"  - Created real directory: {sites_assets_dir}")
    elif not os.path.isdir(sites_assets_dir):
        os.makedirs(sites_assets_dir, exist_ok=True)
        print(f"  - Created directory: {sites_assets_dir}")

    # ── Step 2: Merge assets.json / assets-rtl.json ──
    for json_file in ["assets.json", "assets-rtl.json"]:
        src = os.path.join(bench_assets_dir, json_file)
        dst = os.path.join(sites_assets_dir, json_file)
        if os.path.exists(src):
            if os.path.exists(dst):
                try:
                    import json
                    with open(src, "r") as f:
                        src_data = json.load(f)
                    with open(dst, "r") as f:
                        dst_data = json.load(f)
                    merged = {}
                    merged.update(dst_data)
                    merged.update(src_data)
                    with open(dst, "w") as f:
                        json.dump(merged, f, indent=4)
                    print(f"  - Merged {json_file}")
                except Exception as e:
                    print(f"  - Error merging {json_file}: {e}, falling back to copy")
                    shutil.copy2(src, dst)
            else:
                shutil.copy2(src, dst)
                print(f"  - Copied {json_file}")

    # ── Step 3: Copy css / js / locale from bench/assets/ ──
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

    # ── Step 4: Copy each app's public assets ──
    for app in apps:
        dst = os.path.join(sites_assets_dir, app)

        # Prefer bench/assets/<app> (compiled output); fall back to app/public/
        bench_app_assets = os.path.join(bench_assets_dir, app)
        app_public_path  = os.path.join(bench_path, "apps", app, app, "public")

        if os.path.islink(bench_app_assets):
            src = os.path.realpath(bench_app_assets)
        elif os.path.isdir(bench_app_assets):
            src = bench_app_assets
        elif os.path.isdir(app_public_path):
            src = app_public_path
        else:
            print(f"  - Source for {app} not found, skipping.")
            continue

        # Remove stale destination
        if os.path.islink(dst):
            os.unlink(dst)
        elif os.path.isdir(dst):
            shutil.rmtree(dst, ignore_errors=True)

        print(f"  - Copying {app} assets from {src}...")
        shutil.copytree(
            src, dst,
            symlinks=False,
            ignore=shutil.ignore_patterns(
                "node_modules", "*.pyc", "__pycache__", ".git", ".github"
            ),
        )

        # Also copy dist/ from bench assets if it exists separately
        bench_dist = os.path.join(bench_assets_dir, app, "dist")
        dst_dist   = os.path.join(dst, "dist")
        if os.path.exists(bench_dist) and not os.path.exists(dst_dist):
            shutil.copytree(bench_dist, dst_dist, symlinks=False)
            print(f"    + Copied dist/ for {app}")

        print(f"    Done: {app}")

    print("[SMRITI] Asset sync complete — physical files now in sites/assets/ (shared volume).")


if __name__ == "__main__":
    _run_sync()
