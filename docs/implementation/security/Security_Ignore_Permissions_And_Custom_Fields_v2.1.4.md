# Implementation Plan - Security: Ignore Permissions & Custom Fields v2.1.4

- **Author:** Historical Retrospective
- **Status:** Completed
- **Version:** v2.1.4
- **Date:** 2026-07-06

---

## 1. Objective
Auditing and tagging all `ignore_permissions=True` calls within whitelisted endpoints, and resolving the custom field database schema mismatch in the test database.

## 2. Business Motivation
- **Security Audit**: Ensure all permission bypasses in whitelisted API endpoints are reviewed and tagged with a review label.
- **Database Schema Consistency**: Prevent custom fields from being overwritten during migrations.

## 3. Scope
- Audit all whitelisted endpoints for `ignore_permissions=True` calls.
- Fix custom fields updates overwrite bug in `setup.py`.
- Introduce `check_ignore_permissions.py` script.

## 4. Current State
- Missing audit trail on whitelisted API permission bypasses.
- User custom fields in `setup.py` overwrite each other during setup.

## 5. Gap Analysis
- Overwriting dict keys in `setup.py` causing database field drops.
- Linter lacks regression checks on `ignore_permissions=True`.

## 6. Architecture Impact
Improves build/security tooling and schema integrity.

## 7. Proposed Design
- Consolidate all `User` custom fields under a single configuration key in `setup.py`.
- Implement `tools/audit/check_ignore_permissions.py` to scan AST for whitelisted endpoints bypassing permissions.

## 8. Files Created
- [check_ignore_permissions.py](file:///D:/Smriti_Retail_OS/tools/audit/check_ignore_permissions.py)

## 9. Files Modified
- [setup.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/setup.py)
- [test_billing_api.py](file:///D:/Smriti_Retail_OS/smriti_retail_os/tests/test_billing_api.py)
- Whitelisted API files (comment additions)

## 10. Dependencies
None.

## 11. Risks
None.

## 12. Rollback Strategy
Git revert.

## 13. Verification Plan
- Run `python tools/audit/check_ignore_permissions.py`
- Run `bench --site smriti_retail run-tests --module smriti_retail_os.tests.test_billing_api`

## 14. Test Plan
- Run tests: `python tools/audit/check_ignore_permissions.py`

## 15. Documentation Impact
Walkthrough and implementation index update.

## 16. Deployment Plan
Deployed in v2.1.4.

## 17. Status
Completed.

## 18. Related ADRs
None.

## 19. Related Walkthroughs
- [Security_Ignore_Permissions_And_Custom_Fields_v2.1.4.md](file:///D:/Smriti_Retail_OS/docs/walkthrough/security/Security_Ignore_Permissions_And_Custom_Fields_v2.1.4.md)
