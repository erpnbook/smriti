# Implementation Plan - Foundation Licensing Migration GPLv3 v2.1.2

- **Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
- **Status:** Completed
- **Version:** v2.1.2
- **Date:** 2026-07-06

---

## 1. Objective
Migrate SMRITI Retail OS primary repository licensing from the MIT License to the **GNU General Public License v3.0 (GPL-3.0-only)**.

## 2. Business Motivation
Provide strong copyleft protection for core SMRITI engineering innovations, formalize contributor conditions, and align licensing with standard ERPNext and India Compliance components.

## 3. Scope
- Update repository-wide primary licensing documents (`LICENSE` and `COPYING`).
- Formulate notice and dependency license registries.
- Safely migrate source code comment headers in SMRITI-owned files already containing license headers.
- Register all changes under governance guidelines.

## 4. Current State
The project was previously licensed under the permissive MIT License. Source code files contained `# @license: MIT` headers. No central upstream license register or NOTICE file existed.

## 5. Gap Analysis
- **LICENSE**: Contained MIT text instead of GPLv3.
- **Header Comments**: 518 files referenced MIT instead of GPL-3.0-only.
- **SPDX Identification**: Absent from repository files.
- **Upstream License Inventory**: Lacked `THIRD_PARTY_LICENSES.md` and `NOTICE` files.

## 6. Architecture Impact
- **Upstream Internals Analysis**: The License Guard check script is repurposed to monitor and flag direct coupling on ERPNext or upstream framework internals for maintainability and upgrade risk reviews, rather than licensing splits.

## 7. Proposed Design
- Retain official canonical GPLv3 text in `LICENSE` and `COPYING`.
- Modify header comments in SMRITI files that already contain license declarations to keep diff churn minimal.
- Catalog all dependencies in a separate register.

## 8. Files Created
- [COPYING](file:///D:/Smriti_Retail_OS/COPYING)
- [NOTICE](file:///D:/Smriti_Retail_OS/NOTICE)
- [THIRD_PARTY_LICENSES.md](file:///D:/Smriti_Retail_OS/THIRD_PARTY_LICENSES.md)

## 9. Files Modified
- [LICENSE](file:///D:/Smriti_Retail_OS/LICENSE)
- [README.md](file:///D:/Smriti_Retail_OS/README.md)
- [pyproject.toml](file:///D:/Smriti_Retail_OS/pyproject.toml)
- [CHANGELOG.md](file:///D:/Smriti_Retail_OS/CHANGELOG.md)
- [KNOWLEDGE_BASE.md](file:///D:/Smriti_Retail_OS/KNOWLEDGE_BASE.md)
- [.agents/AGENTS.md](file:///D:/Smriti_Retail_OS/.agents/AGENTS.md)
- [docs/walkthrough/README.md](file:///D:/Smriti_Retail_OS/docs/walkthrough/README.md)
- 518 SMRITI-owned source files containing license headers (`.py`, `.html`, `.css`, `.js`)

## 10. Dependencies
- No external code or logic dependencies are affected.

## 11. Risks
- Mass changes to 500+ files present a git diff/noise risk. *Mitigation*: Restrict header changes strictly to lines containing existing license tags.

## 12. Rollback Strategy
- In case of compile failures or script errors: `git reset --hard HEAD~1` or revert the specific commit `546063d`.

## 13. Verification Plan
- Run automated architecture and token linters.
- Verify package metadata matches GPL-3.0-only.
- Verify that standard pages load without exceptions.

## 14. Test Plan
- Run `python smriti_retail_os/tools/validate_tokens.py smriti_retail_os/public/css`.
- Run `python smriti_retail_os/tools/validate_architecture.py`.

## 15. Documentation Impact
- Walks walkthrough, walkthrough index, knowledge base, and docs registry updated.

## 16. Deployment Plan
- Push to origin development and pull into test environment `F:\Smriti9`.

## 17. Status
Completed.

## 18. Related ADRs
- None.

## 19. Related Walkthroughs
- [Walkthrough](file:///D:/Smriti_Retail_OS/docs/walkthrough/foundation/Foundation_Licensing_Migration_GPLv3_v2.1.2.md)
