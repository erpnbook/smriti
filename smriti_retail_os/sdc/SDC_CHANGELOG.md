# SMRITI Documentation Compiler (SDC) — Version History & Changelog

---

## 1. Versioning Semantics & Schema Evolution

SDC adheres to strict semantic versioning rules:
* **MAJOR (`X.y.z`)**: Denotes breaking changes in the Intermediate Representation (IR) schema, CLI contracts, or quality gate validations. Plugin migration handlers must be executed.
* **MINOR (`x.Y.z`)**: Denotes additive fields, new plugins, or backward-compatible schema enhancements.
* **PATCH (`x.y.Z`)**: Denotes editorial corrections, layout style updates, or non-breaking bug fixes.

---

## 2. SDC Changelog

### v1.1.2 GA (2026-06-25)
* **Initial GA Release**: Architecture frozen.
* **Refactored Folders**: Separated SDC compiler core (`sdc/`) from document output directory (`docs/`).
* **Intermediate Representation (IR)**: Declared `docs/discovery/*.json` as the immutable snapshot after Phase 0 completes.
* **Artifact Registry**: Established [sdc/artifact_registry.json](file:///d:/Smriti_Retail_OS/sdc/artifact_registry.json) to permanently log unique, stable Artifact IDs (e.g. `ART-DOCTYPE-XXXXX`).
* **Dependency Graph**: Added [dependency_graph.json](file:///d:/Smriti_Retail_OS/docs/discovery/dependency_graph.json) with strict edge relationship taxonomy (`USES`, `DEPENDS_ON`, `GENERATES`, `EXTENDS`, `IMPLEMENTS`, `REFERENCES`, `RENDERS`, `VALIDATES`).
* **Quality Gates**: Standardized exit codes (`SDC000`-`SDC401`) and expanded check gates (schema validation, link integrity, provenance checks, and graph cycle analysis).
* **Governance**: Added Rules #13, #14, #15, and #16.

---

## Revision History

| Version | Date | Author | Summary of Changes |
| :--- | :--- | :--- | :--- |
| 1.1.2-GA | 2026-06-25 | Jawahar R. Mallah | Initial version of the changelog document. |

---

## Author Profile

* **Author:** Jawahar R. Mallah
* **Designation:** Founder & Chief Architect
* **Organization:** AITDL – AI Technology & Development Lab
* **Professional Experience:** 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> 
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL
