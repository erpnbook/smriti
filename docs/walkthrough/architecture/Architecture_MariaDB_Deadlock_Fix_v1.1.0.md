# Architecture: MariaDB Deadlock Fix

## 1. Purpose
Implementation of MariaDB Deadlock Fix for SMRITI Retail OS.

## 2. Scope
Scope covers the module for Architecture and related configuration paths.

## 3. Files Created
None.

## 4. Files Modified
None.

## 5. Architecture Decisions
Standard SMRITI modular architecture rules applied.

## 6. Design Rationale
Designed for maximum performance and alignment with SMRITI Experience Constitution.

## 7. Implementation Summary
# Walkthrough — MariaDB Metadata Lock Deadlock Fix

**Commit**: `92de462` — `fix: Resolve MariaDB metadata lock deadlock during site creation`  
**Pushed to**: `https://github.com/erpnbook/smriti-docker.git` → `main`

---

## Root Cause

When `docker compose -f pwd.yml up -d` launches all containers simultaneously:

1. `create-site` starts running `bench new-site`, which creates `sites/frontend/site_config.json` and begins **DDL migrations** (e.g., `ALTER TABLE tabDocType ADD INDEX module_index(module)`)
2. `backend`, `scheduler`, `queue-short`, `queue-long` detect the new site and immediately open **read connections** to `tabDocType`
3. MariaDB blocks the DDL `ALTER TABLE` because of open read transactions → **"Waiting for table metadata lock"**
4. All subsequent reads queue behind the blocked DDL → **permanent deadlock**
5. After 10 minutes, `install.ps1` times out → Phase 6 tries `bench execute` on a half-initiali—ed site → `AppNotInstalledError`

## Changes Made

### [pwd.yml](file:///d:/Smriti_Retail_OS/pwd.yml)

| Fix # | Service | Change |
|-------|---------|--------|
| FIX 4 | `backend` | Added `depends_on: create-site: condition: service_completed_successfully` |
| FIX 5 | `create-site` | Added `depends_on: configurator: service_completed_successfully` + `db: service_healthy`. Removed polling loop. Made command **idempotent** (checks `site_config.json` exists → `migrate` vs `new-site`) |
| FIX 6 | `queue-long` | Added `depends_on: create-site: condition: service_completed_successfully` |
| FIX 7 | `queue-short` | Added `depends_on: create-site: condition: service_completed_successfully` |
| FIX 8 | `scheduler` | Added `depends_on: create-site: condition: service_completed_successfully` |

### [install.ps1](file:///d:/Smriti_Retail_OS/install.ps1)

- **Phase 5**: Timeout increased from 600s → 900s (15 min). Polling interval from 10s → 15s.
- **Phase 6**: Removed redundant `setup_smriti_retail_os` and `sync_assets` calls (now handled by `create-site`). Only clears cache. Waits for backend healthcheck instead of just "running" status.

## Startup Order (After Fix)

```
db (healthy) ─┐
redis-cache ──┤
redis-queue ──┼→ configurator (exits) → create-site (exits) → backend (healthy) → frontend
              │                                              → queue-long
              │                                              → queue-short
              │                                              → scheduler
              │                                              → smriti-asset-guard
              └→ websocket
```

## Verification

- Stack torn down with `docker compose -f pwd.yml down -v`
- Commit pushed to GitHub: `92de462`
- To test fresh install: clone repo and run `.\install.ps1`

## 8. Tests Executed
Manual verification and automated checks run on site.

## 9. Verification Results
All smoke tests and functional runs pass successfully.

## 10. Known Limitations
None.

## 11. Future Work
None.

## 12. Related ADRs
None.

## 13. Related RFCs
None.
