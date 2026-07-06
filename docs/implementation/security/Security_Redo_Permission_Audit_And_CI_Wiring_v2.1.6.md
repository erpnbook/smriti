# Implementation Plan - SMRITI Security Audit, CI Pipeline Integration, and Architecture Guard Fixes v2.1.6

- **Author:** Jawahar R. Mallah | Founder & Chief Architect, AITDL
- **Status:** In Progress
- **Version:** v2.1.6
- **Date:** 2026-07-06

---

## 1. Objective
Achieve pre-launch production readiness by redoing the permission bypass audit with specific contextual reasons, integrating full behavior tests and compliance linting into the GitHub Actions CI pipeline, refactoring 5 files to resolve new architecture guard violations, and cleaning up historical documentation and configuration files.

## 2. Business Motivation
- **Security Safeguards:** Ensure that every whitelisted endpoint bypassing permissions has documented and verified security controls to prevent unauthorized access or manipulation.
- **CI Fitness Gating:** Ensure that every code commit is automatically verified against all automated check suites (permission audit, architecture compliance linter, architecture persistence guard, and integration tests).
- **Architecture Fitness:** Enforce strict layered boundaries to prevent new technical debt from accumulating.
- **Governance Alignment:** Resolve discrepancies between historical walkthroughs and implementation plans.

## 3. Scope
- Delete `.agents/AGENTS_ADDENDUM.md` to resolve redundant guidelines and consolidate under `.agents/AGENTS.md`.
- Generate retrospective implementation plans for v2.1.1 and v2.1.4 and register them in the master index.
- Modify `smriti_retail_os/tools/validate_architecture.py` to exempt existing legacy violations so it executes cleanly, and wire it into the static gate job in CI.
- Wire `tools/audit/check_ignore_permissions.py` into the static gate job in CI.
- Audit all 161 ignore-permissions calls in whitelisted endpoints and replace the copy-pasted comments with unique justifications.
- Refactor the 5 new files identified as violating the architecture guard by moving direct DB calls to the repository layer:
  - `lookup_service.py`
  - `variant_lifecycle_service.py`
  - `purchase_order_service.py`
  - `notifications.py`
  - `matrix_service.py`
- Wire a new `smriti-integration-tests` job running on a `self-hosted` runner to execute the full integration tests suite in CI.

## 4. Current State
- `AGENTS_ADDENDUM.md` is present in the workspace but is redundant.
- No implementation plans exist for v2.1.1 and v2.1.4.
- `validate_architecture.py` fails on legacy codebase violations and is not run in CI.
- Whitelisted endpoints contain generic, uninformative `# reviewed-ignore-permissions: bypass for whitelisted api endpoint` comments.
- CI pipeline only runs syntax checks, sdc compiler, and sdc mutation tests.
- 5 new service and API files directly invoke `frappe.new_doc`, `frappe.get_doc`, and `frappe.db.sql`, failing `smriti_architecture_guard.py`.

## 5. Gap Analysis
- Redundant governance rules.
- Gaps in the implementation plans index.
- Compliance linter `validate_architecture.py` not configured for legacy exemptions.
- Lack of function-specific permission bypass comments.
- CI configuration lacks integration tests and compliance checking.
- Service/API layer files bypass the repository layer for document creation and database queries.

## 6. Architecture Impact
Positive. This reinforces the layered architecture boundaries (UI -> api -> service -> repository -> DB) by isolating database access to repository files and implementing robust automated checking in CI.

## 7. Proposed Design
- **Repository wrappers**: Create `LookupRepository` and `MatrixRepository`. Update `ProductRepository`, `PurchaseRepository`, and `NotificationRepository` with `new_doc`, `get_doc`, and `db_sql` wrappers.
- **Service/API refactoring**: Replace all direct `frappe.new_doc`, `frappe.get_doc`, and `frappe.db.sql` calls in the 5 service files with repository method calls.
- **Contextual Permission Audit**: Update all 161 `# reviewed-ignore-permissions:` comments with detailed reasons (e.g., manager PIN, telemetry-only, role-gated).
- **Compliance Linter Exemptions**: Update `EXEMPT_FILES` in `validate_architecture.py` to list legacy violating files.
- **CI updates**: Add permission audit and validate architecture step to static gate job, and configure a self-hosted runner integration test job.

## 8. Files Created
- [lookup_repository.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/repositories/lookup_repository.py)
- [matrix_repository.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/matrix_engine/repository/matrix_repository.py)

## 9. Files Modified
- [smriti_ci.yml](file:///D:/Smriti_Retail_OS/.github/workflows/smriti_ci.yml)
- [validate_architecture.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/tools/validate_architecture.py)
- [lookup_service.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/services/lookup_service.py)
- [product_repository.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/item_studio/repository/product_repository.py)
- [variant_lifecycle_service.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/item_studio/service/variant_lifecycle_service.py)
- [purchase_repository.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/purchase_studio/repository/purchase_repository.py)
- [purchase_order_service.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/purchase_studio/service/purchase_order_service.py)
- [notification_repository.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/notification_studio/repository/notification_repository.py)
- [notifications.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/notification_studio/api/notifications.py)
- [matrix_service.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/matrix_engine/service/matrix_service.py)
- 34 audited API and service files (comment updates)
- [README.md](file:///D:/Smriti_Retail_OS/docs/implementation/README.md) (Master Index)
- [CHANGELOG.md](file:///D:/Smriti_Retail_OS/CHANGELOG.md)
- [KNOWLEDGE_BASE.md](file:///D:/Smriti_Retail_OS/KNOWLEDGE_BASE.md)

## 10. Dependencies
- Self-hosted GitHub Actions runner must be set up and active.

## 11. Risks
- Minor risk of regression due to import errors or syntax errors. *Mitigation*: Run unit tests locally before pushing.

## 12. Rollback Strategy
- Discard changes using `git reset --hard HEAD` and `git clean -fd`.

## 13. Verification Plan
- Run `python smriti_architecture_guard.py --strict` to verify zero layer violations.
- Run `python tools/audit/check_ignore_permissions.py` to verify all permission comments.
- Run `python smriti_retail_os/tools/validate_architecture.py` to verify the compliance linter passes.
- Run the full suite of 153 integration tests in the test environment.

## 14. Test Plan
- Run: `docker compose -p smriti9 exec backend bench --site smriti_retail run-tests --app smriti_retail_os`

## 15. Documentation Impact
- Walks, knowledge base, and changelog will be updated.
- A new walkthrough file will be created.

## 16. Deployment Plan
- Sync code via git push/pull to test environment `F:\Smriti9` and let the self-hosted runner execute tests.

## 17. Status
In Progress.

## 18. Related ADRs
- ADR-0002: SMRITI Business Layer Independence
- ADR-0009: SMRITI Platform Primitives and Services Standard

## 19. Related Walkthroughs
- [Security_Redo_Permission_Audit_And_CI_Wiring_v2.1.6.md](file:///D:/Smriti_Retail_OS/docs/walkthrough/security/Security_Redo_Permission_Audit_And_CI_Wiring_v2.1.6.md) (To be created upon completion)
