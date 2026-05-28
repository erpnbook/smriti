# -*- coding: utf-8 -*-
#
# @file: smriti_retail_os/sync_assets.py
# @description: Hard-syncs all app assets into the shared sites/assets volume.
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @date: 2026-05-28
# @version: 2.0.0
# @license: MIT
# * Copyright (c) 2026 AITDL NETWORK & ERPNbook.com. All rights reserved.
#

import json
import os
import re
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

    # ── Step 2: Copy top-level css / js / locale from bench/assets/ ──
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

    # ── Step 3: Copy each app's assets from bench/assets/<app>/ ──
    for app in apps:
        src_dir = os.path.join(bench_assets_dir, app)
        dst_dir = os.path.join(sites_assets_dir, app)

        # Resolve symlinks in source
        if os.path.islink(src_dir):
            src_dir = os.path.realpath(src_dir)

        if not os.path.isdir(src_dir):
            # Fallback: use app/public/ directory
            src_dir = os.path.join(bench_path, "apps", app, app, "public")

        if not os.path.isdir(src_dir):
            print(f"  - Source for {app} not found, skipping.")
            continue

        # Remove stale destination
        if os.path.islink(dst_dir):
            os.unlink(dst_dir)
        elif os.path.isdir(dst_dir):
            shutil.rmtree(dst_dir, ignore_errors=True)

        print(f"  - Copying {app} assets from {src_dir}...")
        shutil.copytree(
            src_dir, dst_dir,
            symlinks=False,
            ignore=shutil.ignore_patterns(
                "node_modules", "*.pyc", "__pycache__", ".git", ".github"
            ),
        )
        print(f"    Done: {app}")

    # ── Step 4: Build assets.json by merging bench manifest + auto-discovery ──
    _build_assets_json(sites_assets_dir, bench_assets_dir, apps)

    print("[SMRITI] Asset sync complete — physical files now in sites/assets/ (shared volume).")


def _build_assets_json(sites_assets_dir, bench_assets_dir, apps):
    """
    Merges bench/assets/assets.json with auto-discovered hashed bundles from
    each app's dist/ directory.  Frappe maps `<name>.bundle.js` → hashed URL.
    Apps like india_compliance whose bundles are never in the bench manifest
    will be auto-registered here so the browser never gets a 404.
    """
    # Pattern: <stem>.bundle.<HASH8>.<ext>
    hashed_re = re.compile(r"^(.+\.(bundle|chunk))\.[A-Z0-9]{6,8}\.(js|css)$", re.IGNORECASE)

    # Start with the bench manifest (frappe/erpnext entries)
    bench_manifest_path = os.path.join(bench_assets_dir, "assets.json")
    data = {}
    if os.path.exists(bench_manifest_path):
        try:
            with open(bench_manifest_path, "r") as f:
                data = json.load(f)
            print(f"  - Loaded bench assets.json ({len(data)} entries)")
        except Exception as e:
            print(f"  - Warning: could not load bench assets.json: {e}")

    # Auto-discover hashed bundles from each app's dist/ and register them
    added = 0
    for app in apps:
        app_assets_dir = os.path.join(sites_assets_dir, app)
        dist_path      = os.path.join(app_assets_dir, "dist")
        if not os.path.isdir(dist_path):
            continue

        for kind in ["js", "css"]:
            kind_dir = os.path.join(dist_path, kind)
            if not os.path.isdir(kind_dir):
                continue
            for fname in os.listdir(kind_dir):
                m = hashed_re.match(fname)
                if not m:
                    continue
                # Key = unhashed bundle name, e.g. "india_compliance.bundle.js"
                bundle_key = f"{m.group(1)}.{m.group(3)}"
                asset_url  = f"/assets/{app}/dist/{kind}/{fname}"
                if bundle_key not in data:
                    data[bundle_key] = asset_url
                    print(f"  + Registered: {bundle_key} -> {asset_url}")
                    added += 1

    if added:
        print(f"  - Auto-registered {added} missing bundle entries.")

    # Write the merged manifest to sites/assets/assets.json
    sites_manifest_path = os.path.join(sites_assets_dir, "assets.json")
    with open(sites_manifest_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"  - Wrote sites/assets/assets.json ({len(data)} total entries)")

    # Keep bench/assets/assets.json in sync too (for bench commands)
    try:
        shutil.copy2(sites_manifest_path, bench_manifest_path)
    except Exception:
        pass

    # Handle RTL variant
    bench_rtl_path = os.path.join(bench_assets_dir, "assets-rtl.json")
    sites_rtl_path = os.path.join(sites_assets_dir, "assets-rtl.json")
    if os.path.exists(bench_rtl_path):
        try:
            with open(bench_rtl_path, "r") as f:
                rtl_data = json.load(f)
            # Inject missing entries into RTL manifest too
            for k, v in data.items():
                if k not in rtl_data:
                    rtl_data[k] = v
            with open(sites_rtl_path, "w") as f:
                json.dump(rtl_data, f, indent=4)
            print("  - Updated assets-rtl.json")
        except Exception as e:
            print(f"  - Warning: RTL manifest update failed: {e}")
            shutil.copy2(bench_rtl_path, sites_rtl_path)


if __name__ == "__main__":
    _run_sync()
