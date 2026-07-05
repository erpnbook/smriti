---
Document ID: CONST-001
Title: SMRITI Documentation Constitution
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

# SMRITI Documentation Constitution

**Governance Version**: 1.0.0  
**Status**: FROZEN  
**Effective Date**: 2026-06-25  
**Change Control**: Chief Architect Approval Required  

---

## Purpose

This document defines the mandatory documentation governance rules for every AI agent, developer, contributor, and automation working on SMRITI Retail OS. These rules ensure documentation remains consistent, searchable, maintainable, and explainable. Routine AI agents and developers may write or update documentation but are strictly prohibited from changing these governance rules.

---

## Zero Duplicate Policy (DRY Knowledge)

**Principle:** SMRITI Retail OS follows a **Single Source of Truth (SSOT)** documentation model. **Duplicate Knowledge is prohibited.** 

There shall be only one authoritative document for each topic. Rather than duplicating explanations (e.g., copying the same authentication details across both a Developer Guide and an API Reference), keep the canonical explanation in the primary document and use repository-relative cross-references.

---

## AI Agent Permission Matrix

| Action | AI Allowed | Description |
| --- | --- | --- |
| **Create new document** | ✅ Only if topic doesn't exist | Search the index to check if topic exists first. |
| **Update document** | ✅ | Allowed for minor corrections or enhancements. |
| **Expand document** | ✅ | Allowed for adding new sections or details. |
| **Move document** | ✅ | Use `git mv` to preserve commit history. |
| **Rename document** | ⚠️ Requires index update | Document ID must remain stable. |
| **Delete document** | ❌ Never | Deleting documentation is strictly prohibited for AI. |
| **Archive document** | ⚠️ With approval | Update file status to `Archived` in the YAML header. |
| **Merge document** | ⚠️ Only after conflict report | Prepare conflict report and get architect approval first. |

---

## "Knowledge Before Files" Philosophy

AI agents must search the knowledge base before creating new files. Do not default to file creation:

```text
Need knowledge
      │
      ▼
Search knowledge base
      │
      ▼
Knowledge exists?
 ├── YES ──► Update existing document (append, expand, cross-reference)
 └── NO  ──► Create new document
```

---

## Documentation Change Workflow

Every documentation modification must follow the pipeline below:

```text
Search Index & Locate Primary Document
                  │
                  ▼
         Update File Content
                  │
                  ▼
       Append Revision History
                  │
                  ▼
Re-compile Index (Run generator script)
                  │
                  ▼
  Verify Links & Validate Syntax (PASS)
```

---

## AI Self-Validation Checklist

Before an AI agent saves or completes a document modification, it must run and answer this checklist:
- [ ] Did I search `docs/DOCUMENTATION_INDEX.md`?
- [ ] Did I find an existing document covering the topic?
- [ ] Did I update instead of duplicating?
- [ ] Did I use relative paths (never absolute `file:///` paths) for all links?
- [ ] Did I update the Revision History table?
- [ ] Did I run `generate_documentation_index.py` to update the index files?
- [ ] Did I run `doc_health_audit.py` to verify formatting and links?

---

## Core Governance Rules

### Rule 1 — Single Source of Truth
Every topic must have exactly one primary document. Duplicate documentation or copying identical knowledge blocks across documents is prohibited.

### Rule 2 — Audience First
Every document must target a single primary audience (Product/Executive, End User, Administrator, Installer, Developer, API Integrator, Support Engineer, Architect) specified in its metadata header.

### Rule 3 — Documentation Categories
Every document must belong to exactly one of the 9 defined categories under `docs/` (`01-product` to `09-release-notes`).

### Rule 4 — Standard Document Structure
Every document must follow the standard metadata header defined in `DOCUMENTATION_STYLE_GUIDE.md` and use the templates under `docs/tools/templates/`.

### Rule 5 — Never Delete Knowledge
AI agents must never remove useful documentation. Instead, merge, update, or archive. Physical deletion requires explicit human approval.

### Rule 6 — Append Before Rewrite
When expanding documentation, append new sections whenever practical. Do not rewrite an entire document unless requested. Preserve git history.

### Rule 7 — Formula & Metric Explainability
Any document describing a computed KPI, formula, or score must include: Business Meaning, Formula Expression, Worked Example, Data Sources, Interpretation Guide, and Recommended Actions.

### Rule 8 — Cross-Reference Rules
Rather than duplicating information, reference the authoritative document ID using repository-relative paths (e.g., `As documented in: [ARCH-011](./08-architecture/clienteling_architecture_blueprint.md) See Section 5`).

### Rule 9 — Naming Conventions
Use descriptive lowercase names using underscores. Avoid terms like `final`, `v2`, `draft`, or `copy`.

### Rule 10 — Repository-Relative Links
All markdown links must be repository-relative. **The use of absolute `file:///` links is strictly prohibited.**

### Rule 11 — Images
Store all image assets under `docs/images/`. Do not store images in the same folder as documentation content.

### Rule 12 — Examples
Include realistic sample data, commands, expected results, and common mistakes in all manuals.

### Rule 13 — Developer Documents
Developer documents must include architecture, data flows, hooks, testing instructions, and extension points.

### Rule 14 — User Documents
User guides should focus on workflows, tasks, and configurations. Do not mix code or database queries in user-facing manuals.

### Rule 15 — API Documents
Every endpoint documentation must include: HTTP Method, Endpoint URL, Request Parameters, Response JSON, Error Codes, and a worked example.

### Rule 16 — Troubleshooting Format
Troubleshooting articles must follow: Problem Description, Symptoms, Cause, Resolution Steps, Verification, and Prevention.

### Rule 17 — Release Notes
Never edit historical release notes. Append new versions only.

### Rule 18 — Version History
Every document must maintain a Revision History table (Version, Date, Author, Summary of Changes) at the end of the file.

### Rule 19 — AI Change Log
Whenever an AI agent edits documentation, it must record the modification in the document's Revision History. Silent changes are forbidden.

### Rule 20 — Automated Index Only
`DOCUMENTATION_INDEX.md` and folder `index.md` files are read-only for developers and AI agents. They must be compiled using the `generate_documentation_index.py` tool.

### Rule 21 — Merge Rules
When merging, compare documents, extract unique information, append to the primary document, update relative links, and mark the duplicate as archived.

### Rule 22 — Quality Checklist
Before saving a document, verify metadata schema, relative paths, folder paths, examples, and revision history.

### Rule 23 — Zero-Tolerance CI Gates
All documentation changes must pass the automated validation audit (no duplicates, no missing mandatory metadata, no broken internal links, and no invalid status values) before merging.

### Rule 24 — Success Criteria
Documentation is compliant only when every topic has one authoritative document, no duplicate knowledge exists, all documents are indexed, and links are valid.

### Rule 25 — Index Search First
Before creating any document, the AI agent must search the index to ensure the topic or a similar file does not exist.

### Rule 26 — Update Over Create
If a matching topic exists in the index, the AI agent must update the existing document rather than creating a new file.

### Rule 27 — Forbidden Filenames
AI agents must never create filenames containing `copy`, `copy2`, `v2`, `new`, `updated`, `final`, `latest`, `draft`, `revision`.

### Rule 28 — No Topic Splitting
Never split one topic across multiple documents without explicit architecture approval.

### Rule 29 — Atomic Commits & Index Sync
Every commit that modifies any documentation file must also include updates to the generated index files.

### Rule 30 — Governance Escalation
If unsure where a document belongs or how to merge overlapping contents, the AI agent must stop and request human approval.

---

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Initial frozen release of SMRITI Documentation Constitution v1.0.0 |

**Author**: Jawahar R. Mallah  
**Designation**: Founder & Chief Architect  
**Organization**: AITDL – AI Technology & Development Lab  
**Experience**: 20+ Years of Experience in Software Development, Retail Technology, POS Solutions, and Enterprise Application Design.  

> "Always decision-ready."  
> — Jawahar R. Mallah
