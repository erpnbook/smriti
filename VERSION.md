# VERSION — SMRITI Retail OS

## Application Version

| Field              | Value                          |
|--------------------|--------------------------------|
| Version            | 2.1.1                          |
| Release Date       | 2026-07-04                     |
| Release Type       | Patch                          |
| Codename           | Engineering Governance          |
| Git Tag            | v2.1.1                         |
| Previous Version   | 2.1.0                          |
| Previous Tag       | v2.1.0                         |

## Repository Versions

| Repository              | Version | Tag     | Remote                              |
|-------------------------|---------|---------|-------------------------------------|
| erpnbook/smriti         | 2.1.1   | v2.1.1  | git@github-erpnbook:erpnbook/smriti |
| erpnbook/smriti-docker  | 2.4.0   | v2.4.0  | github-erpnbook:erpnbook/smriti-docker |

## Dependency Versions (Verified on this release)

| Dependency         | Version     |
|--------------------|-------------|
| Frappe Framework   | v16.19.1    |
| ERPNext            | v16.19.1    |
| India Compliance   | Latest      |
| MariaDB            | 11.8        |
| Redis              | 6.2-alpine  |
| Python             | 3.14        |

## Semantic Versioning Rationale

Version 2.1.0 was chosen because:

1. MINOR bump (2.0.x → 2.1.0):
   This release adds engineering governance capabilities, automated
   verification infrastructure, and release process tooling. No new
   product modules were introduced, and no breaking changes were made.
   Key additions:
   - Automated E2E UI Integration Regression Test Suite
   - Config-driven Developer Bypass (replaces hostname check)
   - Centralized Roles Constants Registry
   - RELEASE_GATE_CRITERIA.md
   - QUALITY_DASHBOARD.md
   - Purchase Studio sidebar integration (L/R/T/B, collapse, popout)

2. ZERO breaking changes confirmed:
   0 removed @frappe.whitelist endpoints.
   All API additions are additive.
   Existing data is preserved through all patches.

---

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
