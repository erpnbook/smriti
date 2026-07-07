# SMRITI Implementation Plan — Governance Consolidation & Validation Gates v1.0.0

- **Area:** Foundation
- **Version:** v1.0.0
- **Status:** Draft
- **Author:** Jawahar Ramkripal Mallah
- **Owner:** AITDL NETWORK

---

## 1. Objective
Consolidate the fragmented SMRITI governance system into a single authoritative root Constitution and a mapped Governance Matrix. Introduce automated pre-commit validation checkers for phantom references and authority hierarchy validation to ensure long-term document hygiene.

## 2. Business Motivation
SMRITI governance files currently contain duplicate rules, phantom references (such as to `GEMINI.md` and `SMRITI_DESIGN_SYSTEM.md`), circular dependencies, and a completely missing test suite for constitutional rules. By simplifying and validating this layer, we reduce cognitive overhead for developers and eliminate artificial pipeline drag from unenforced or incorrect rules.

## 3. Scope
* **Documents Consolidated/Modified:**
  * Modify `SMRITI_PRODUCT_CONSTITUTION.md` to be the sole root authority, incorporating the Golden Rule from SPV and the lifecycle principles from SSDL (SPC-009, 010, 011).
  * Retire/Consolidate duplicate rules from `SMRITI_EXPERIENCE_CONSTITUTION.md`, `SMRITI_PLATFORM_VISION.md`, `SMRITI_SSDL.md`, `SMRITI_GOVERNANCE.md`, and `SMRITI_ADR_GUIDE.md`.
  * Update `docs/walkthrough/README.md` and `docs/implementation/README.md` indices.
* **Validation Checkers:**
  * Create `tools/audit/check_phantom_references.py` to flag references to non-existent files or directories.
  * Create `tools/audit/check_authority_hierarchy.py` to validate document precedence claims.
  * Wire both scripts into the git pre-commit hook.

## 4. Current State
As documented in the Phase 1 Audit Report:
- Precedence hierarchy lists missing `GEMINI.md`.
- Platform Vision Golden Rule asserts independent supremacy.
- SSDL references SPC-009, 010, 011, which are missing from the master Constitution.
- Missing `tests/constitution` directory makes all 7 SPC tests phantom.
- absolute `file:///` links are used despite bans.
- Empty placeholders exist for multiple architecture documents.

## 5. Gap Analysis
* **G1: No Single-Root Precedence Hierarchy** -> Map all documents cleanly to Level 1 (Constitution), Level 2 (Architecture Directive), Level 3 (Governance Specifications), or Level 4 (Workflow Guides).
* **G2: Broken File References** -> Implement automated linting for phantom file and directory references.
* **G3: Missing Enforcement for SPC-001 to 007** -> Explicitly label them as "Unenforced" or "CI-Verified" in a consolidated Governance Matrix.

## 6. Architecture Impact
None on backend transactional services. Improves pre-commit and CI/CD validation gating for repository documentation.

## 7. Proposed Design
* **The Unified Constitution:** Set up `SMRITI_PRODUCT_CONSTITUTION.md` as the sole root authority containing 10-15 core articles, including the Golden Rule (Article 1) and SSDL principles.
* **The Governance Matrix:** Maintain a mapped table matching each active control to its repository-relative target, its enforcement checker, and its ownership role.
* **The Checkers:** Write lightweight AST/regex scripts under `tools/audit` that scan Markdown links and reference declarations against actual disk files.

## 8. Files Created
* [check_phantom_references.py](file:///D:/Smriti_Retail_OS/tools/audit/check_phantom_references.py)
* [check_authority_hierarchy.py](file:///D:/Smriti_Retail_OS/tools/audit/check_authority_hierarchy.py)

## 9. Files Modified
* [SMRITI_PRODUCT_CONSTITUTION.md](file:///D:/Smriti_Retail_OS/SMRITI_PRODUCT_CONSTITUTION.md)
* [SMRITI_PLATFORM_VISION.md](file:///D:/Smriti_Retail_OS/SMRITI_PLATFORM_VISION.md)
* [SMRITI_SSDL.md](file:///D:/Smriti_Retail_OS/SMRITI_SSDL.md)
* [SMRITI_GOVERNANCE.md](file:///D:/Smriti_Retail_OS/SMRITI_GOVERNANCE.md)
* [SMRITI_EXPERIENCE_CONSTITUTION.md](file:///D:/Smriti_Retail_OS/SMRITI_EXPERIENCE_CONSTITUTION.md)
* [SMRITI_ADR_GUIDE.md](file:///D:/Smriti_Retail_OS/SMRITI_ADR_GUIDE.md)
* [tools/git-hooks/pre-commit](file:///D:/Smriti_Retail_OS/tools/git-hooks/pre-commit)

## 10. Dependencies
None.

## 11. Risks
Incorrectly configured pre-commit scripts could block developers from committing changes. Mitigation: Maintain a fallback option to bypass hooks during emergency local overrides (`git commit -n`).

## 12. Rollback Strategy
`git reset --hard HEAD` and `git checkout` on modified files.

## 13. Verification Plan
* Re-run `python smriti_architecture_guard.py` to ensure zero boundary failures.
* Execute both new validation scripts directly:
  `python tools/audit/check_phantom_references.py`
  `python tools/audit/check_authority_hierarchy.py`

## 14. Test Plan
Write simple mock file scenarios to verify that the phantom reference checker successfully flags missing markdown file linkages.

## 15. Documentation Impact
Update the walkthough indices and write the release changelog.

## 16. Deployment Plan
Commit and push to development repository (`D:\Smriti_Retail_OS`), pull into the testing workspace (`F:\Smriti9`), and reload bench configurations.

## 17. Status
Draft.

## 18. Related ADRs
None.

## 19. Related Walkthroughs
None.
