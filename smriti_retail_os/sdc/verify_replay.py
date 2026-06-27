# -*- coding: utf-8 -*-
#
# @file: sdc/verify_replay.py
# @description: Automated Deterministic Replay and Quality Gate Verification for SDC
# @author: Jawahar R Mallah <jawahar.mallah@gmail.com>
# @version: 1.8.6
#

import os
import json
import io
import sys
import subprocess
from compiler import SDCLogger, sdc_exit

def read_inventory_without_timestamp(filepath):
    if not os.path.exists(filepath):
        raise Exception(f"File not found: {filepath}")
    with io.open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "generated_at" in data:
        data["generated_at"] = "STATIC_TIMESTAMP_FOR_REPLAY"
    return data

def run_verify(repo_root):
    SDCLogger.info("Starting Milestone 5: Deterministic Replay Validation...")

    discovery_dir = os.path.join(repo_root, "docs", "discovery")
    files_to_check = [
        "file_inventory.json",
        "doctype_inventory.json",
        "field_inventory.json",
        "api_inventory.json",
        "business_dictionary.json",
        "screen_inventory.json",
        "search_index.json",
        "dependency_graph.json",
        "discovery_manifest.json"
    ]

    # --- Run 1 ---
    SDCLogger.info("Executing Run 1 of Phase 0 Discovery...")
    p1 = subprocess.run([sys.executable, "sdc/discovery.py", repo_root], capture_output=True, text=True)
    if p1.returncode != 0:
        SDCLogger.error(f"Run 1 failed with exit code {p1.returncode}\nSTDOUT:\n{p1.stdout}\nSTDERR:\n{p1.stderr}")
        sys.exit(p1.returncode)

    # Cache run 1 data
    run1_data = {}
    for f in files_to_check:
        run1_data[f] = read_inventory_without_timestamp(os.path.join(discovery_dir, f))

    # --- Run 2 ---
    SDCLogger.info("Executing Run 2 of Phase 0 Discovery (Deterministic Replay)...")
    p2 = subprocess.run([sys.executable, "sdc/discovery.py", repo_root], capture_output=True, text=True)
    if p2.returncode != 0:
        SDCLogger.error(f"Run 2 failed with exit code {p2.returncode}\nSTDOUT:\n{p2.stdout}\nSTDERR:\n{p2.stderr}")
        sys.exit(p2.returncode)

    # Compare run 2 against run 1
    for f in files_to_check:
        path = os.path.join(discovery_dir, f)
        run2_item = read_inventory_without_timestamp(path)
        if run1_data[f] != run2_item:
            SDCLogger.error(f"DETERMINISM BREAK: Output of {f} is different between run 1 and run 2.")
            # Print diff for debug
            import difflib
            r1_str = json.dumps(run1_data[f], indent=2).splitlines()
            r2_str = json.dumps(run2_item, indent=2).splitlines()
            diff = difflib.unified_diff(r1_str, r2_str, fromfile="run1", tofile="run2")
            print("\n".join(diff))
            sdc_exit("SDC401", f"Deterministic replay check failed on {f}")
        else:
            SDCLogger.info(f"Determinism Check Passed for {f}")

    SDCLogger.info("Replay determinism successfully verified.")

    # --- Run Renderer & Quality Gate ---
    SDCLogger.info("Executing SDCRenderer and Quality Gate validation...")
    p3 = subprocess.run([sys.executable, "sdc/renderer.py", repo_root], capture_output=True, text=True)
    if p3.returncode != 0:
        SDCLogger.error(f"Quality Gate / Renderer failed with exit code {p3.returncode}\nSTDOUT:\n{p3.stdout}\nSTDERR:\n{p3.stderr}")
        sys.exit(p3.returncode)

    SDCLogger.info(p3.stdout.strip())
    sdc_exit("SDC000", "Milestone 5 complete: Deterministic replay and Quality Gates verified successfully!")

if __name__ == "__main__":
    repo_root = "d:\\Smriti_Retail_OS"
    if len(sys.argv) > 1:
        repo_root = sys.argv[1]
    run_verify(repo_root)
