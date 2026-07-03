# SMRITI Master Blueprint v1.1

---
**DOCUMENT METADATA**
- **Author & Chief Architect**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Document Generation**: Prepared by SMRITI Engineering Agent
- **Review Status**: Draft – Pending Human Review
- **Approval Status**: Pending Human Approval
---

## 1. Target State
The target architecture of SMRITI Retail OS demands:
- **Strict Presentation Decoupling (Rule 9)**: 100% of user-facing retail views reside in canonical, standalone www pages. No Frappe `/desk` or `/app` routes are ever exposed to the user.
- **Service-First Architecture**: All database persistence is routed through dedicated Service Layers and Repositories rather than direct frontend insertion.
- **Centralised Role and Permission Management**: Unified enforcement of page permissions and access controls via `security_api.py`.

## 2. Current State
As of Version 2.0.1:
- **UI Decoupling**: 21 of 22 legacy desk pages are retired. Standalone www routes now serve all corresponding frontend actions.
- **Role Adoption**: The central `Roles` class is imported and adopted inside `security_api.py`. Standard helper guards (such as `check_store_manager_or_admin()`) utilize `Roles` constants.
- **Routing and Redirection**: Fallback Desk routes are intercepted at the Boot HTTP level in `boot.py` and redirected to canonical SMRITI routes.
- **Guard Validation**: The Architecture Guard scans the codebase to lock in persistence boundaries, passing with exit code 0.

## 3. Remaining Work
- **Incremental Roles Migration**: Complete Pass B of the Roles rollout. Replace the remaining raw literal role strings in the remaining Python files with `Roles.X` constants.
- **UDNE Page Migration (Task 4.1)**: Build a dedicated www page equivalent for the Numbering Engine (UDNE) and retire the last remaining desk page.

---
**SIGN-OFF & STATUS**
- **Prepared By**: SMRITI Engineering Agent
- **Human Reviewer**: Pending Assignment
- **Approval Date**: Pending
- **Status**: Draft
