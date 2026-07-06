# SMRITI Retail OS — Release Notes v2.1.6

**Release Date**: 2026-07-06
**Codename**: Security Remediation
**Previous Version**: v2.1.1

---

## 📢 Announcement: Official SMRITI Wiki Documentation Portal is Live!

We are thrilled to announce the official launch of the **SMRITI Retail OS Documentation Wiki**! 

This new documentation portal serves as the single source of truth for customers, partners, developers, and administrators deploying and managing SMRITI Retail OS.

### 🌟 Highlights of the New Wiki
The wiki covers all core modules, engines, and configuration interfaces of the standalone SMRITI enterprise retail platform:

1. **Getting Started & Deployments**: Step-by-step setup guides, installation instructions, and quick-start checklists.
2. **Product Studios**: Complete guides to:
   - **Product Studio**: Catalog and variant lifecycle management.
   - **Purchase Studio**: Procurement workflows and supplier relationships.
   - **Sales Studio**: POS cashier sessions, terminal management, and sales checkout.
   - **Inventory Studio**: Multi-warehouse stock receipts, transfers, and physical snapshots.
   - **Label Studio**: Queue-based barcode generation and printing.
   - **Customer Studio**: Loyalty programs, demographic segmentation, and CRM.
3. **Core Engines**:
   - **Matrix Engine**: High-dimensional size/color grid configurations.
   - **Customer Growth Engine**: Real-time customer lifetime value and campaign automation.
   - **Theme Engine & Navigation Engine**: Custom branding stylesheets and role-based navigation access policies.
   - **Explain Engine & Formula Registry**: Interactive explanation tooltips and locked mathematical equations for transparency.
   - **Integration Engine**: Sales and inventory synchronization pipelines.
4. **Administration & Security**: User roles, security hardening, REST API references, and system configuration guidelines.

### 🔗 Quick Links
- **SMRITI Wiki**: https://github.com/erpnbook/smriti/wiki
- **Latest Release (v2.1.6)**: https://github.com/erpnbook/smriti/releases/tag/v2.1.6
- **Documentation Home**: https://github.com/erpnbook/smriti/wiki/Home
- **SMRITI Codebase**: https://github.com/erpnbook/smriti

---

## Highlights of this Release

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
