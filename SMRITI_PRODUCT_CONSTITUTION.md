# SMRITI Product Constitution (SPC)
**Status:** DRAFT (not LOCKED, not FROZEN)
**File:** `/SMRITI_PRODUCT_CONSTITUTION.md`
**Internal Version:** 1.0.0 (Established 2026-07-01)

---

## Authority Statement

This document is the supreme law of SMRITI Retail OS development. All code changes, documentation, tests, and agent interactions are subject to the constraints defined herein. 

An article without a defined, active enforcement mechanism does not block pull requests, but must still be adhered to by developer agents in good faith. 

---

## Precedence Hierarchy

In the event of a conflict between SMRITI documents, rules, or instructions, the following hierarchy of authority shall determine which wins:

```
Level 1: SMRITI Product Constitution (SPC)  <-- Highest Authority
   ↓
Level 2: SMRITI Architecture Directive (ARCHITECTURE.md)
   ↓
Level 3: SMRITI Governance & CI Specifications (SMRITI_GOVERNANCE.md)
   ↓
Level 4: AI Agent Workflow Guides (SMRITI_AI_AGENT_GUIDE.md)
   ↓
Level 5: Sprint Instructions & Product Roadmap
   ↓
Level 6: User Prompts & Conversation Input    <-- Lowest Authority
```

*Note: A lower-level instruction (e.g. a user prompt or sprint instruction) can NEVER override a higher-level constitutional constraint (e.g. SPC-001 No Framework Leakage) unless a formal, active Architecture Decision Record (ADR) is created.*

---

## Scope

Applies to all files in this repository **except:**
- `/vendor/`
- `/node_modules/`
- `/build/`
- `/.git/`
- Any directory containing a `.smriti-constitution-ignore` marker file

---

## Adopted Articles (Enforceable Constraints)

### SPC-000 — The Golden Rule
**Severity:** Critical  
**Description:** SMRITI is the product. The Platform Engine (currently ERPNext + Frappe) is an internal implementation detail. If a feature exists only to operate the Platform Engine, keep it in the Platform Engine; if a feature is part of the business experience, SMRITI owns it. Operational users must never interact with the Platform Engine directly.  
**Enforcement:** Verified by SMRITI Architecture Guard (Persistence boundaries) and Navigation / Brand boundaries.

---

### SPC-001 — No Framework Leakage
**Severity:** Critical  
**Description:** Operational users must never see ERPNext/Frappe naming, Desk UI, DocType labels, or framework branding. Every user-facing surface belongs to SMRITI.  
**Enforcement:** Pre-merge grep/AST scan of `www/*.html`, `public/js/*.js`, and page `<title>` tags for denylist terms (`ERPNext`, `Frappe`, `Desk`, `DocType`, `bench`). See `SMRITI_GOVERNANCE.md` for execution.

---

### SPC-002 — Single Source of Truth / No Duplicates
**Severity:** Major  
**Description:** Before creating a menu, report, DocType, route, API endpoint, widget, nav entry, or theme token, the agent must search the repository for an existing equivalent and justify why reuse is not possible.  
**Enforcement:** Documentation of prior-art search in PR description. See `SMRITI_AI_AGENT_GUIDE.md` for step-by-step instructions.

---

### SPC-003 — Safe Refactoring
**Severity:** Critical  
**Description:** No file, function, route, or DocType may be deleted, renamed, or moved without an attached dependency scan, reference scan, import scan, and usage scan.  
**Enforcement:** Raw scan output attached to PR as Evidence Level A. No summary judgments allowed.

---

### SPC-004 — Evidence-First Completion
**Severity:** Critical  
**Description:** An agent's self-report that a task is "done," "fixed," or "tested" is not accepted as evidence. Every completion claim must include verifiable artifacts (git commit hash, raw terminal output, or screenshot).  
**Enforcement:** Validation of Evidence Level A/B artifacts on any completion report. See `SMRITI_GOVERNANCE.md` for definitions.

---

### SPC-005 — AI Honesty Principle
**Severity:** Critical  
**Description:** An AI agent must distinguish between verified facts, inferred conclusions, and assumptions. It must never fabricate commits, test results, scan outputs, repository contents, or implementation status. If evidence is unavailable, it must explicitly state so.  
**Enforcement:** Human review and verification of all logs and git commit hashes. Fabricating evidence is a critical constitutional violation.

---

### SPC-006 — Scope Integrity
**Severity:** Major  
**Description:** An AI agent shall not expand or narrow the scope of the assigned task without explicitly stating the change and obtaining approval. Additional changes outside the requested scope will block the PR unless explicitly cleared.  
**Enforcement:** Mandated scope section in PR description matching Requested vs. Implemented scope.

---

### SPC-007 — Single Source of Evidence
**Severity:** Major  
**Description:** No agent report or walkthrough may present summaries, scores, or conclusions without first presenting the raw evidence and findings that support them. Evidence must always precede interpretation.  
**Enforcement:** Validation of document structure: Evidence -> Finding -> Conclusion.

---

### SPC-008 — Standing Governance Principle
**Severity:** Major  
**Description:** Governance exists to simplify engineering, not to increase bureaucracy. Every governance artifact shall have one clear owner, one clear purpose, and one clear authority. Every new governance document, rule, or process must either replace an existing document, consolidate multiple documents, or resolve a verified governance gap.  
**Enforcement:** Reviewed via manual verification and documented change budgets.

---

### SPC-009 — Policy Before Implementation
**Severity:** Major  
**Description:** When multiple technically valid implementations exist, the business policy must be defined before selecting an implementation. AI agents shall not infer policy from framework defaults.  
**Enforcement:** Evaluated by Capability Ownership Matrix (Phase 2 SSDL) and human architecture review.

---

### SPC-010 — Ownership Before Construction
**Severity:** Major  
**Description:** Before creating any new module, page, service, API, workflow, or report, the AI agent shall identify whether the capability is owned by SMRITI, the underlying framework, shared, or currently unowned (Gap). New implementation shall not begin until ownership has been established.  
**Enforcement:** Checked by Capability Ownership Map during Phase 2 of SSDL.

---

### SPC-011 — Conflict Escalation
**Severity:** Major  
**Description:** AI agents shall not resolve business policy conflicts autonomously. When multiple valid policies exist, the conflict must be documented, options presented with trade-offs, and implementation paused pending human architectural decision. The resolution decision becomes an ADR entry.  
**Enforcement:** Validated at Phase 7 (Architecture Review) and documented in ADR registry.

---

### SPC-012 — Platform Adapter Boundary
**Severity:** Critical
**Description:** No SMRITI service, studio, API file, or www/ page may call `frappe.*` platform APIs directly.
All platform access must route through the SMRITI Core Framework (`smriti_retail_os/core/platform/`).
Business modules use the SMRITI Framework API (`from smriti_retail_os import smriti`) — never the internal adapter path.
This rule ensures the Platform Engine (currently Frappe + ERPNext) remains a replaceable implementation detail.

**Canonical pattern:**
```python
# Compliant — all business services and studios
from smriti_retail_os import smriti
customer = smriti.documents.get("Customer", name)

# Violation — must never appear outside core/platform/
import frappe
doc = frappe.get_doc("Customer", name)
```

**JavaScript equivalent:** All `www/` pages use `smriti.api.*`, `smriti.notify.*`, `smriti.navigation.*`.
Calling `frappe.call()`, `frappe.show_alert()`, or `frappe.set_route()` directly is a violation.

**Enforcement:** Guard 6 in `smriti_architecture_guard.py` (warning mode — transitioning to error mode as migration progresses).
Migration tracked in `ARCHITECTURE_MIGRATION_BACKLOG.md`.

---

## Candidate Articles (Documented, Not Adopted)

The following candidate articles carry **no blocking authority** until promoted to Adopted status via the formal amendment process:

| ID | Candidate Article | Focus | Blocker Before Adoption |
|---|---|---|---|
| — | Zero Hardcoding | Config Layer | Needs defined config layer + measurable % threshold |
| — | Metadata-First | Subsystems | Needs in-scope subsystem definition first |
| — | Explainability-First | Transparency | Overlaps with PSV explainability work — derive from that |
| — | Business-First Language | Glossary | Needs user-facing glossary to check against |
| — | Studio Philosophy | Conventions | Naming convention only |
| — | Engine Philosophy | Architecture | Architectural philosophy |
| — | Registry Philosophy | Database | Architectural registry pattern definition |
| — | Backward Compatibility | Tests | Needs compatibility test suite |
| — | Quality Gate | Checklists | Needs each sub-check to exist independently first |
| SPC-C-012 | SMRITI Component Library Standard | UI Components | Needs formal component library built; interim baseline is inline patterns in `www/` HTML files. See `SMRITI_UI_ARCHITECTURE.md` §Component Inventory. |
| SPC-C-013 | SMRITI Document Format Standard | Business Documents | Needs Print Studio scoped and implemented. Every business document must define Screen View, Print View, PDF, Email, and Mobile View. See `SMRITI_UI_ARCHITECTURE.md` §Document Format Matrix. |

---

## Amendment Log

| Version | Date | Change | Author |
|---|---|---|---|
| v1.0.0 | 2026-07-01 | Split from v0.2 draft. Added Hierarchy, SPC-006 (Scope Integrity), SPC-007 (Single Source of Evidence). | Jawahar R. Mallah |
| v1.1.0 | 2026-07-08 | Added Candidate Articles SPC-C-012 (SMRITI Component Library Standard) and SPC-C-013 (SMRITI Document Format Standard), derived from Independent Product Architecture Constitution review. | AI Architecture Agent |