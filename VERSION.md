# VERSION — SMRITI Retail OS

## Application Version

| Field              | Value                          |
|--------------------|--------------------------------|
| Version            | 2.0.0                          |
| Release Date       | 2026-07-02                     |
| Release Type       | Major                          |
| Codename           | Platform Expansion             |
| Git Tag            | v2.0.0                         |
| Git Commit (HEAD)  | a8285cd                        |
| Previous Version   | 1.8.6                          |
| Previous Tag       | v1.8.6                         |

## Repository Versions

| Repository              | Version | Tag     | Remote                              |
|-------------------------|---------|---------|-------------------------------------|
| erpnbook/smriti         | 2.0.0   | v2.0.0  | git@github-erpnbook:erpnbook/smriti |
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

Version 2.0.0 was chosen because:

1. MAJOR bump (1.x → 2.x):
   Four entirely new product modules introduced in this cycle:
   - Purchase Studio — full purchase lifecycle UI + service layer
   - UIE (Universal Integration Engine) — TallyPrime connectivity framework
   - SNM (Navigation Manager) — database-driven nav with Redis caching
   - SNSM (Negative Stock Engine) — policy-based stock management
   Combined, these represent a qualitative platform expansion beyond
   incremental feature delivery. 23 new DocTypes were added.

2. No MINOR (patch) bump would be appropriate at this scale.
   84 commits, 325 files changed, +26,159 lines.

3. ZERO breaking changes confirmed:
   0 removed @frappe.whitelist endpoints.
   All API additions are additive.
   Existing data is preserved through all patches.

## __init__.py Update Required

Before tagging, update:

  File: smriti_retail_os/__init__.py
  Change: __version__ = "1.8.6"  →  __version__ = "2.0.0"

---

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
