# SMRITI Retail OS — Release Summary v2.1.1

| Field                  | Value                                            |
|------------------------|--------------------------------------------------|
| **Version**            | 2.1.1                                            |
| **Release Date**       | 2026-07-04                                       |
| **Codename**           | Engineering Governance                           |
| **Release Type**       | Patch (Hotfixes & Compliance)                    |
| **Previous Version**   | 2.1.0                                            |
| **Architecture Guard** | PASS — 0 boundary violations                     |
| **UI Integration Tests** | PASS — 6/6 tests pass                          |
| **Release Gate**       | PASS — All mandatory criteria satisfied          |

## What Changed

| Category           | Count / Detail                                    |
|--------------------|---------------------------------------------------|
| Commits since v2.1.0 | 12                                                |
| New test cases     | 1 (Scheduler Hooks Regression Gate)               |
| Version files updated | 5 (__init__.py, hooks.py, smriti_nav_config.js, VERSION.md, CHANGELOG.md) |
| Documentation health | PASS — 100% compliant, 0 blocker errors           |
| Breaking changes   | 0                                                 |

## Key Deliverables

1. **Negative Stock Recovery Safety Sweep (KI-003)** — Module-level `run_safety_net` hook wrapper to resolve daily scheduler ImportError at migration.
2. **Product Catalog Console Blocker** — Whitelisted backend API `get_catalog_metadata` to load filter metadata dynamically on `/products`.
3. **Missing CSRF Token Fix** — Injected global `window.csrf_token` and `window.csrfToken` variables on `/products` and `/smriti` dashboard pages.
4. **Unread Notification Badge Fix** — Whitelisted the `get_unread_count` API endpoint to resolve `403 Forbidden` error on standalone pages.
5. **Collapsed Sidebar Brand Logo** — Sidebar CSS layout to keep the brand logo visible and centered in collapsed mode.
6. **Styled Toolbar Filter Dropdowns** — Custom SMRITI dropdown CSS styles with an embedded SVG chevron arrow indicator.
7. **Documentation Compliance** — Resolved all missing metadata headers and broken links, achieving a PASS status on the Documentation Health Audit.

## Known Issues

- Billing integration tests require POS Profile fixture data (pre-existing).
- CGE concurrency stress tests have intermittent database lock failures.

## Next Planned Milestone

- Complete Roles Pass B (remaining `check_page_access()` items).
- UDNE migration completion.

---

Author: Jawahar R. Mallah | Founder & Chief Architect, AITDL
