# SMRITI Retail OS — Release Notes (v2.0.1)

---
**DOCUMENT METADATA**
- **Document Owner**: Jawahar R. Mallah
- **Organization**: AITDL – AI Technology & Development Lab
- **Prepared By**: SMRITI Engineering Team
- **Reviewed By**: —
- **Approved By**: —
- **Status**: Draft
- **Version**: 2.0.1
- **Last Updated**: 04-Jul-2026
---

## Release Highlights
SMRITI v2.0.1 focuses on architectural integrity, cross-platform CI validation, and native dependency retirement.

### 1. Architecture Guard & CI
- Normalized path separators inside `smriti_architecture_guard.py` to support Windows and Linux environments.
- Regenerated `architecture_baseline.json` with forward slashes for full cross-platform portability.
- Integrated the architecture conformance guard into the GitHub Actions CI pipeline (`smriti_ci.yml`).

### 2. Native Dependency Retirement
- Deleted 21 legacy desk page directories under `smriti_retail_os/page/`.
- Replaced native List view redirects (`frappe.set_route("List", ...)`) in frontend JS scripts.
- Implemented HTTP/boot level path mappings and redirect rules for retired URLs.

### 3. Centralised Access Controls
- Adopted the central `Roles` class inside `security_api.py` and replaced raw string role checks with unified constants.
- Registered policies for newly added views in `security_api.py`.
- Rolled out unified `check_page_access()` validation to 4 more www page controllers.

---
**REVISION HISTORY**
- **Prepared By**: SMRITI Engineering Team
- **Reviewed By**: —
- **Approved By**: —
- **Status**: Draft
