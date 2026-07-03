# SMRITI Retail OS — Release Notes (v2.0.1)

---
**DOCUMENT METADATA**
- **Author & Chief Architect**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Document Generation**: Prepared by SMRITI Engineering Agent
- **Review Status**: Draft – Pending Human Review
- **Approval Status**: Pending Human Approval
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
**SIGN-OFF & STATUS**
- **Prepared By**: SMRITI Engineering Agent
- **Human Reviewer**: Pending Assignment
- **Approval Date**: Pending
- **Status**: Draft
