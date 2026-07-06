# SMRITI Walkthrough - Foundation Licensing Migration GPLv3 v2.1.2

- **Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
- **Status:** Done
- **Version:** v2.1.2
- **Date:** 2026-07-06

---

## 1. Purpose
Migrate the project licensing of SMRITI Retail OS from MIT to GNU General Public License v3.0 (GPL-3.0-only) to protect core platform assets, formalize contributor conditions, and standardize repository licensing.

## 2. Scope
- Update repository-wide primary license files.
- Establish notice and attribution guidelines.
- Build a structured third-party dependency licensing register.
- Safely update license headers and inject SPDX identifiers in SMRITI-owned source files containing license headers.
- Update packaging metadata, project configs, and governance files.

## 3. Files Created
- [COPYING](file:///D:/Smriti_Retail_OS/COPYING)
- [NOTICE](file:///D:/Smriti_Retail_OS/NOTICE)
- [THIRD_PARTY_LICENSES.md](file:///D:/Smriti_Retail_OS/THIRD_PARTY_LICENSES.md)
- `docs/walkthrough/foundation/Foundation_Licensing_Migration_GPLv3_v2.1.2.md` (this file)

## 4. Files Modified
- [LICENSE](file:///D:/Smriti_Retail_OS/LICENSE)
- [README.md](file:///D:/Smriti_Retail_OS/README.md)
- [pyproject.toml](file:///D:/Smriti_Retail_OS/pyproject.toml)
- [CHANGELOG.md](file:///D:/Smriti_Retail_OS/CHANGELOG.md)
- [KNOWLEDGE_BASE.md](file:///D:/Smriti_Retail_OS/KNOWLEDGE_BASE.md)
- [.agents/AGENTS.md](file:///D:/Smriti_Retail_OS/.agents/AGENTS.md)
- [docs/walkthrough/README.md](file:///D:/Smriti_Retail_OS/docs/walkthrough/README.md)
- 518 SMRITI-owned source files containing license headers (`.py`, `.html`, `.css`, `.js`)

## 5. Architecture Decisions
- **Verification-oriented License Guard**: Repurpose the legacy License Guard check script to track upstream couplings for maintainability and upgrade compliance instead of licensing split logic.
- **Header Conservation**: Only modify source files that already contain license headers, modified files, or new files to avoid massive git noise and merge conflicts.

## 6. Design Rationale
- **Verbatim Compliance**: Retain both `LICENSE` and `COPYING` containing the exact, verbatim text of the GPLv3 license.
- **SPDX Integration**: Inject standard SPDX-License-Identifier tags to allow automated package and security scanners to resolve SMRITI licensing.

## 7. Implementation Summary
- Replaced root `LICENSE` and created `COPYING` with raw GPLv3 text.
- Formulated the `NOTICE` file to document standard copyright attributions.
- Structured `THIRD_PARTY_LICENSES.md` to catalog all dependencies.
- Added licensing rules to the agent governance policy `AGENTS.md`.
- Ran the automated Python script `update_headers.py` to replace `# @license: MIT` comments with `# @license: GPL-3.0-only` and add `SPDX-License-Identifier: GPL-3.0-only`.

## 8. Tests Executed
- Validation scripts: `validate_tokens.py` and `validate_architecture.py`.
- Automated test runs inside the Frappe bench environment.

## 9. Verification Results
- All validator scripts passed with 0 violations from our changes.
- Checked that all updated source files compile cleanly.

## 10. Known Limitations
- Outdated files that do not currently have a license comment header do not receive the new SPDX headers. These will be added incrementally when files are edited.

## 11. Future Work
- Establish CI rules checking for the presence of `SPDX-License-Identifier` on all newly added files.

## 12. Related ADRs
- None.

## 13. Related RFCs
- None.
