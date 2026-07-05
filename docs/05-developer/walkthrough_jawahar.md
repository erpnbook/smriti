---
Document ID: "DEV-066"
Title: "Smriti Retail OS — Installation Improvement Walkthrough"
Owner: "Development Team"
Audience: "Developer"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-25"
Last Reviewed: "2026-06-25"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# Smriti Retail OS — Installation Improvement Walkthrough

## Summary

Users were struggling to install Smriti Retail OS due to hardcoded paths, missing validation, and a multi-step manual process. We've added **automated installers**, a **health checker**, and fixed the core blocker (hardcoded Windows paths in `pwd.yml`).

---

## Changes Made

### 1. Fixed Hardcoded Paths — [pwd.yml](../../pwd.yml)

**The #1 installation blocker.** The compose file had `D:/Smriti_Retail_OS/assets` hardcoded in **8 places** across 8 service definitions. This broke the setup on every machine except the original developer's.

```diff
-      - D:/Smriti_Retail_OS/assets:/home/frappe/frappe-bench/assets
+      - ./assets:/home/frappe/frappe-bench/assets
```

All 8 occurrences replaced. Now works on any machine, any OS.

---

### 2. Windows Installer — [install.ps1](../../install.ps1) `[NEW]`

One-command installer that runs **7 automated phases**:

| Phase | What it does |
|---|---|
| 1. Pre-flight | Checks Docker, Git, port 8080, compose file |
| 2. App Source | Clones `smriti_retail_os` and `india_compliance` into `apps/` |
| 3. Environment | Creates `.env` from `example.env` if missing |
| 4. Launch | Runs `docker compose -f pwd.yml up -d` |
| 5. Site Wait | Polls `create-site` container until done (timeout: 10 min) |
| 6. Post-Install | Runs SMRITI setup, asset sync, cache clear |
| 7. Health Check | Verifies containers + HTTP connectivity |

**Usage:**
```powershell
.\install.ps1                          # Standard install
.\install.ps1 -AdminPassword "MyPass"  # Custom password
.\install.ps1 -Force                   # Fresh start (deletes volumes)
.\install.ps1 -SkipClone               # Skip git clone if apps/ already populated
```

---

### 3. Linux/macOS Installer — [install.sh](../../install.sh) `[NEW]`

Mirrors `install.ps1` feature-for-feature in bash. Supports Linux and macOS.

```bash
bash install.sh
bash install.sh --password MyPass --force
```

---

### 4. Health Checker — [check.ps1](../../check.ps1) `[NEW]`

Standalone diagnostic script with **4 sections, 20+ checks**:

| Section | Checks |
|---|---|
| A. Prerequisites | Docker, Docker Compose, Git, port 8080 |
| B. Project Files | `pwd.yml`, `.env`, `apps/smriti_retail_os/`, `apps/india_compliance/`, `assets/` |
| C. Container Health | All 9 containers (backend, frontend, db, etc.) |
| D. Connectivity | HTTP 200 from `localhost:8080`, login page reachable |

Produces a clear pass/warn/fail summary:
```
  Summary: 18 passed  |  1 warnings  |  0 failed  (of 19 checks)
  🎉  Everything looks great!
```

---

### 5. Installation Guide — [INSTALL.md](../04-installation/install.md) `[NEW]`

Comprehensive guide covering:
- ⚡ One-command install (Windows + Linux)
- 📋 Prerequisites table
- 🗂️ Manual 7-step walkthrough for advanced users
- ✅ Verification instructions
- 🔄 Update procedure
- 🧨 Full reset procedure
- ❓ Common issues quick-ref table
- 🏗️ Architecture diagram

---

### 6. Rewritten README — [README.md](../../README.md)

**Before:** 6-step manual process buried in the middle, no mention of installers.

**After:**
- One-command install **at the very top** (first thing users see)
- Links to `INSTALL.md` for details
- Prerequisites table
- Quick troubleshooting table
- Health checker mention

---

## Before vs After — User Experience

````carousel
### ❌ Before (6+ manual steps, errors everywhere)
```
1. git clone ...
2. mkdir -p apps && git clone ... apps/smriti_retail_os
3. git clone ... apps/india_compliance
4. docker compose -f pwd.yml up -d
5. docker logs -f smriti_retail_os-create-site-1   ← wait, hope
6. docker exec ... bench --site frontend execute smriti_retail_os.setup.setup_smriti_retail_os
7. docker exec ... bench --site frontend execute smriti_retail_os.sync_assets.sync_assets
```
Users often missed steps 5-7, got wrong container names, hit hardcoded path errors.
<!-- slide -->
### ✅ After (2 commands)
```powershell
git clone https://github.com/erpnbook/smriti-docker.git smriti_retail
cd smriti_retail
.\install.ps1
```
Installer handles everything automatically with progress feedback and error recovery.
````

---

## Files Changed Summary

| File | Status | Purpose |
|---|---|---|
| [pwd.yml](../../pwd.yml) | Modified | Fixed 8 hardcoded asset paths; built in automated SMRITI setup & asset hard-sync hooks in `create-site` container and default localhost CORS origin in `configurator` container. |
| [install.ps1](../../install.ps1) | New | Windows one-command installer (rewritten for 100% pure ASCII to avoid encoding issues; handles stderr gracefully with Continue preference). |
| [install.sh](../../install.sh) | New | Linux/macOS one-command installer (updated with corrected india-compliance repository URL). |
| [check.ps1](../../check.ps1) | New | Pre-flight validator + health checker (fully ASCII-fied). |
| [INSTALL.md](../04-installation/install.md) | New | Detailed installation guide (updated with corrected repository URL). |
| [README.md](../../README.md) | Rewritten | Quick-install first, cleaner structure. |
| [RELEASE_NOTES.md](../09-release-notes/release_notes.md) | Modified | Updated release installation commands with corrected repository URL. |
| [sync_assets.py](../../sync_assets.py) | Modified | Rewritten to physically copy assets (dist, css, js, locale, app-specific) to the shared `sites/assets` volume, resolving frontend 404 errors in multi-container setups. |
| [apps/smriti_retail_os/smriti_retail_os/sync_assets.py](../../apps/smriti_retail_os/smriti_retail_os/sync_assets.py) | Modified | App-specific sync script updated to use the same robust physical-copy logic. |


---

## What to Test

1. **Clone to a different directory** (e.g. `D:\test_install\smriti\`) and run `.\install.ps1` — should work without any edits
2. **Run `.\check.ps1`** to verify the health checker output
3. **Try with empty `apps/`** — installer should auto-clone from GitHub
4. **Try with `-Force`** flag to test fresh-start path

---

*Completed: May 27, 2026*


## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL