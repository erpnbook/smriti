---
Document ID: MANIFEST-001
Title: SMRITI Documentation Manifest
Owner: Chief Architect
Audience: Product / User / Admin / Developer / Architect
Module: Core
Version: 1.0.0
Status: Frozen
Primary Document: Yes
Depends On: ""
Related Modules: ""
Last Updated: 2026-06-25
Last Reviewed: 2026-06-25
AI Generated: Yes
Reviewed By: Jawahar R. Mallah
---

# SMRITI Documentation Manifest

**Governance Version**: 1.0.0  
**Status**: FROZEN  
**Effective Date**: 2026-06-25  
**Change Control**: Chief Architect Approval Required  

---

## Welcome to the SMRITI Retail OS Documentation Hub

This manifest serves as the entry point and structural blueprint for all documentation within the SMRITI Retail OS repository. Any developer, AI agent, or contributor must read this manifest and the associated governance files before creating, editing, moving, or deleting any documentation.

---

## Documentation Architecture

All documentation is organized into **nine (9) structured folders** and **four (4) core governance files** at the root of the `docs/` directory.

### Core Governance Roots
- [DOCUMENTATION_MANIFEST.md](./DOCUMENTATION_MANIFEST.md) *(This file)* — Overall architecture, folder mappings, and entry guide.
- [DOCUMENTATION_CONSTITUTION.md](./DOCUMENTATION_CONSTITUTION.md) — Mandatory governance rules, permission matrix, decision tree, and zero-duplicate policies.
- [DOCUMENTATION_STYLE_GUIDE.md](./DOCUMENTATION_STYLE_GUIDE.md) — Writing standards, markdown formats, heading structures, worked example layouts, and YAML frontmatter templates.
- [DOCUMENTATION_INDEX.md](./DOCUMENTATION_INDEX.md) — The authoritative registry cataloging every document, stable IDs, statuses, and ownership metadata. (Automatically generated; do not edit manually).

### Folder Mapping & Taxonomy

```text
docs/
├── 01-product/          # Product overview, features, roadmap, licensing, commercial
├── 02-user-guide/       # Cashier, billing, inventory, POS, daily operations
├── 03-admin-guide/      # Users, permissions, trial administration, company setup, backup, scheduler
├── 04-installation/     # Installation, Docker, Bench setup, migration, upgrade
├── 05-developer/        # Services, source code, hooks, testing, coding standards
├── 06-api/              # REST APIs, whitelisted methods, integration, webhooks
├── 07-kb/               # Errors, troubleshooting, FAQ, recovery guides
├── 08-architecture/     # Core architecture, formula registry, KGF, explainability, state machines
├── 09-release-notes/    # Version history, sprint notes, migration guides, breaking changes
```

---

## Documentation Lifecycle

All documents cycle through the following status values:
1. **Draft**: Newly created files undergoing initial writing.
2. **Review**: Completed files awaiting architect or peer review.
3. **Approved**: Verified files ready for publication.
4. **Active**: The official current documentation for a feature.
5. **Deprecated**: Outdated but preserved for historical context.
6. **Archived**: Moved out of active circulation but retained in history.

---

## Naming Conventions
- All folder names must follow the `##-slug` format (e.g., `01-product`, `05-developer`).
- All document filenames must be lowercase, using underscores instead of spaces or hyphens (e.g., `backup_strategy.md`, `billing_integration.md`).
- Filenames containing placeholder suffixes like `_copy`, `_v2`, `_latest`, `_draft`, or `_final` are strictly prohibited.

---

## Automated Compilation & Tooling
Tooling for the documentation system resides under the `docs/tools/` folder:
- `docs/tools/generate_documentation_index.py`: Parses YAML headers of all markdown files and compiles the root `DOCUMENTATION_INDEX.md` and subfolder `index.md` tables of contents automatically.
- `docs/tools/documentation_schema.yaml`: The single source of truth defining mandatory and optional metadata fields.
- `docs/tools/audit/doc_health_audit.py`: The validation script executed during CI/CD to verify compliance against metadata, link accuracy, duplicates, and example presence.

---

## Maintenance & Auditing Process

The documentation workspace is verified automatically using the health check script. Once per sprint, a **Documentation Health Report** is generated to detail compliance metrics and ensure the repository remains clean, DRY, and accurate.

> "Always decision-ready."  
> — Jawahar R. Mallah, Founder & Chief Architect, AITDL

---

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Initial frozen release of SMRITI Documentation Governance v1.0.0 |

**Author**: Jawahar R. Mallah  
**Designation**: Founder & Chief Architect  
**Organization**: AITDL – AI Technology & Development Lab  
**Experience**: 20+ Years of Experience in Software Development, Retail Technology, POS Solutions, and Enterprise Application Design.  

> "Always decision-ready."  
> — Jawahar R. Mallah
