# SMRITI Retail OS — Release Notes v2.1.6

**Release Date**: 2026-07-06
**Codename**: Security Remediation
**Previous Version**: v2.1.1

---

## Highlights

This release focuses on hardening SMRITI Retail OS security controls, integrating automated compliance linting and integration testing into the CI pipeline, and correcting persistence boundary violations.

---

## New Capabilities

### 1. Automated Compliance CI Workflows
- Integrated `check_ignore_permissions.py` (whitelisted permission check) into `.github/workflows/smriti_ci.yml`.
- Integrated `validate_architecture.py` (compliance linter audit) into `.github/workflows/smriti_ci.yml`.
- Added a self-hosted runner integration testing workflow to run the entire backend test suite.

### 2. Architecture Boundary Isolation
- Extracted persistence layer calls (`frappe.new_doc`, `frappe.get_doc`, `frappe.db.sql`) from services.
- Created `LookupRepository` and `MatrixRepository` classes, wrapping all direct database operations to keep boundaries clean.

---

## Fixes

- **Whitelisted API ignore-permissions Audit**: Reviewed and updated comments for all 161 endpoints that bypass standard permissions in whitelisted APIs, using unique contextual explanations.
- **Tally Integration Test Database Setup**: Corrected the test suite to automatically configure root and child Cost Centers and the Company's `round_off_account` defaults in the database during test setups, resolving precision loss validation errors.
- **Branding Integrity Tests**: Corrected expected SHA-256 hashes of the login page template and global logo SVG to match their current correct versions.

---

## Commits Since v2.1.1

7 commits covering API permission audits, repository extraction refactoring, CI workflow wiring, and test suite initialization corrections.

---

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
