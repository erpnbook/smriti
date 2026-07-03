# SMRITI Platform Roadmap

> **Status**: LOCKED — v1.0.0
> **Authority**: Jawahar R. Mallah, Founder & Chief Architect, AITDL
> **Applies to**: All Developers, Contributors, AI Agents, Product Managers
> **Scope**: SMRITI Release Phases and Version Matrix

---

## 1. Core Platform Version Matrix

To allow modular upgrades and independent evolutionary paths, all core SMRITI platform capabilities are version-locked as follows:

| Platform Component | Version | Status | Specification File |
|---|---|---|---|
| **SMRITI Retail OS** | v1.0.0 | Frozen | `ARCHITECTURE.md` |
| **SMRITI Connect** | v1.0.0 | Frozen | `SMRITI_CONNECT_ARCHITECTURE.md` |
| **SMRITI AI** | v1.0.0 | Frozen | `SMRITI_AI_ENGINEERING_CONSTITUTION.md` |
| **Architecture Guard** | v1.0.0 | Implemented | `smriti_architecture_guard.py` |
| **Platform Vision** | v2.0.0 | Frozen | `SMRITI_PLATFORM_VISION.md` |

---

## 2. Release Phases

The platform moves systematically through four execution phases. No phase may begin until the preceding phase is 100% complete and validated.

---

### Phase 1 — Repository Migration (P0 & P1)

**Objective:** Clean up the technical debt by enforcing the SMRITI Connect outbox pattern and moving all direct Platform Engine queries to the Repository Layer (Rule 4).

**Focus Areas:**
- **Security:** Migrate all user verification and access gates in `security_api.py` to `SecurityRepository`.
- **License & Trial:** Extract and modularize license keys, validation activity logs, and settings parameters.
- **Billing & Payments:** Decouple transaction creation and payment gateway logs.

---

### Phase 2 — Complete SMRITI Experience

**Objective:** Hide the Platform Engine UI completely from business users (Rule 7 and Rule 8).

**Focus Areas:**
- **Studios:** Consolidate and complete Item Studio, Customer Studio, Purchase Studio, and Stock Studio.
- **Console URLs:** Ensure all user navigation points to bare-noun paths (`/items`, `/customers`, `/billing`, `/connect`) instead of `/app/*` or `/desk/*`.
- **Statutory Wrapper:** Build SMRITI wrapper views for Category E1 compliance screens (GST, E-Way Bill) so that users never see native Frappe Desk elements.

---

### Phase 3 — Operational Hardening

**Objective:** Harden SMRITI Connect to enterprise-grade execution stability.

**Focus Areas:**
- **Deduplication & Idempotency:** Prevent duplicate event creation and enforce unique transactional hashes.
- **Metrics & Logging:** Expose connection latencies, sync execution duration, and payload stats on the `/connect` health dashboard.
- **Circuit Breaker:** Automatically halt queue attempts to offline servers (Tally, Busy, etc.) and transition to cooldowns.
- **Transport Security:** Enforce HTTPS parameters for all remote integration transport payloads.

---

### Phase 4 — GA Readiness

**Objective:** Quality assurance, benchmarking, and final deployment checklist.

**Focus Areas:**
- **Load Testing:** Run high-volume benchmarks (10,000+ invoices/hour) to measure database queue lock durations.
- **Security Review:** Run penetration checks and verify encryption for sensitive transaction payloads.
- **UAT & Documentation:** Gather user acceptance logs across Cashier, Manager, and Owner personas. Write final Release Notes.

---

*SMRITI Platform Roadmap v1.0.0*
*Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL*
*Status: LOCKED*
