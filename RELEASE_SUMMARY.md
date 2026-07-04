# SMRITI Retail OS — Release Summary v2.1.0

| Field                  | Value                                            |
|------------------------|--------------------------------------------------|
| **Version**            | 2.1.0                                            |
| **Release Date**       | 2026-07-04                                       |
| **Codename**           | Engineering Governance                           |
| **Release Type**       | Minor (Feature + Governance)                     |
| **Previous Version**   | 2.0.0                                            |
| **Architecture Guard** | PASS — 0 boundary violations                     |
| **UI Integration Tests** | PASS — 5/5 tests pass                          |
| **Release Gate**       | PASS — All mandatory criteria satisfied          |

## What Changed

| Category           | Count / Detail                                    |
|--------------------|---------------------------------------------------|
| Commits since v2.0.0 | 75                                               |
| New test cases     | 5 (UI Integration Regression Suite)               |
| Role constants added | 3 (Accountant, Sales Manager, SMRITI Team)       |
| New documents      | 2 (RELEASE_GATE_CRITERIA.md, QUALITY_DASHBOARD.md)|
| Version files updated | 4 (__init__.py, hooks.py, setup.py, VERSION.md) |
| Breaking changes   | 0                                                 |

## Key Deliverables

1. **Automated UI Integration Regression** — Headless DOM assertion tests for sidebar structure, CSS tokens, navigation routing, permissions, and developer bypass.
2. **Config-Driven Developer Bypass** — Server-controlled `SMRITI_DEVELOPER_MODE` flag replaces loopback hostname checks.
3. **Centralized Roles Registry** — All role strings migrated to `Roles` class constants.
4. **Release Gate Criteria** — Formal quality checkpoints for architecture, tests, performance, security, and documentation.
5. **Purchase Studio Sidebar** — Full L/R/T/B placement, collapse, popout, and hash routing.

## Known Issues

- Billing integration tests require POS Profile fixture data (pre-existing).
- CGE concurrency stress tests have intermittent database lock failures.

## Next Planned Milestone

- Complete Roles Pass B (remaining `check_page_access()` items).
- UDNE migration completion.
- Stabilize automated test suite in CI pipeline.

---

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
