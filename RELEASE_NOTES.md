# SMRITI Retail OS — Release Notes v2.2.0

**Release Date**: 2026-07-09
**Codename**: Architecture Compliance
**Previous Version**: v2.1.6

---

## 📢 Announcement: Complete UI Persistence Boundary Clean and Enforced!

We are thrilled to announce that we have successfully completed the migration of all legacy platform persistence dependencies on the client-side of the SMRITI Retail OS experience layer.

With this release, **Guard 6 (UI Persistence Boundary)** has been promoted from WARNING MODE to **ERROR MODE** in the development and CI environments. Any direct access to client-side Frappe persistence methods from within standalone SMRITI pages will now trigger a build/check failure.

---

## Highlights of this Release

This release focuses entirely on code compliance, architectural isolation, and engineering governance.

---

## New Capabilities

### 1. UI Persistence Boundary Enforcement (ERROR MODE)
- Configured `smriti_architecture_guard.py` to enforce Guard 6 as a build-breaking failure on any new violations.
- Created `smriti_retail_os.api.platform_data_api` as a compliant backend data adapter that safely wraps and sanitizes raw data calls for standalone pages.

---

## Fixes & Refactoring

- **UI Boundary Violations Cleared**: Successfully resolved all **188 violations** across 47 SMRITI pages (`www/*.html`), migrating them to use `smriti.api.call()`, `smriti.api.getList()`, `smriti.notify.*`, and other framework primitives.
- **Removed Polyfills**: Cleaned redundant backend connection polyfills and customized local wrappers in favor of canonical `smriti.api` methods.
- **Tuning and Documentation**: Addressed edge case false positives in release notes and presentations to keep the compliance check strictly accurate.

---

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
