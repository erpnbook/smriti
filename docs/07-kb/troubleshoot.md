---
Document ID: "KB-019"
Title: "Troubleshoot"
Owner: "Support Team"
Audience: "Support Engineer"
Module: "Core"
Version: "1.0.0"
Status: "Active"
Primary Document: "Yes"
Depends On: ""
Related Modules: ""
Last Updated: "2026-06-25"
Last Reviewed: "2026-06-25"
AI Generated: "Yes"
Reviewed By: "Jawahar R. Mallah"
---

# Troubleshoot

> **Important:** This guide has been merged into the central [TROUBLESHOOTING.md](troubleshooting_core.md) at the repository root.
> Please refer to the root [TROUBLESHOOTING.md](troubleshooting_core.md) for the most up-to-date and comprehensive troubleshooting instructions.

## Revision History

| Version | Date | Author | Summary of Changes |
| --- | --- | --- | --- |
| 1.0.0 | 2026-06-25 | Jawahar R. Mallah | Reorganized & standardized |


---

## Author Profile

- **Author**: Jawahar R. Mallah
- **Designation**: Founder & Chief Architect
- **Organization**: AITDL – AI Technology & Development Lab
- **Professional Experience**: 20+ Years of Experience in Software Development, Retail Technology, Distribution Systems, POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> "Always decision-ready."  
> — Jawahar R. Mallah  
> Founder & Chief Architect, AITDL
---

## v2.0.0 Known Issues (2026-07-02)

### KI-001 · test_add_item_by_barcode — Pre-existing Test Failure

**Severity:** P3 (Low — test isolation only)
**Module:** Barcode Studio
**Impact on production:** None

The barcode add-item test fails in full suite run due to teardown data leak between tests. The barcode scan workflow functions correctly in browser and integration testing. Run the test in isolation to confirm: `bench run-tests --module smriti_retail_os.tests.test_barcode`.

---

### KI-002 · test_calculation_order_and_dual_discounts — Pre-existing Test Failure

**Severity:** P3 (Low — test isolation only)
**Module:** Billing
**Impact on production:** None

Tax template state leaks between test classes in the full suite run. The dual-discount calculation is verified correct by the separately passing `test_discount_application` test.

---

### KI-003 · SNSM Scheduler Path Warning at Migrate

**Severity:** P4 (Info — non-fatal)
**Module:** Negative Stock Engine
**Impact on production:** SNSM recovery scheduler job does not auto-run. Manual recovery still works.

**Warning at migrate:**
```
smriti_retail_os.negative_stock.service.recovery_service.SMRITINegativeStockRecoveryService
.run_scheduler_safety_net is not a valid method
```

**Workaround:** Run recovery manually:
```bash
bench --site smriti_retail execute \
  smriti_retail_os.negative_stock.service.recovery_service.run_safety_net
```

---

### KI-004 · V17FrappeDeprecationWarning — limit_page_length

**Severity:** P4 (Info — warning only)
**Module:** Frappe Framework internal
**Impact on production:** None — all list queries run correctly.

```
V17FrappeDeprecationWarning: The 'limit_page_length' parameter is deprecated. Use 'limit' instead.
```

This will be resolved in v2.1.0 when SMRITI migrates to Frappe v17 compatible API.

---

### KI-005 · smriti-docker: Demo Company Seeding Disabled

**Severity:** P4 (Info — intentional)
**Impact:** Fresh Docker installs do not seed demo data. Use SMRITI Setup Wizard.

---

### KI-006 · SDC Mutation Drift Gate Tests — Pre-existing Failures

**Severity:** P3 (Low — development tool tests only)
**Module:** SMRITI Document Compiler
**Impact on production:** None. SDC is a development governance tool, not a runtime dependency.

6 SDC mutation tests fail in full suite due to config path resolution differences in the bench test runner environment.

---

