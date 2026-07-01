# SMRITI Software Development Lifecycle (SSDL)
**AITDL Engineering Standard: AES-002**  
**Version:** 1.0.0  
**Status:** ACTIVE  
**Effective Date:** 2026-07-01  
**Authority:** Jawahar R. Mallah, Founder & Chief Architect, AITDL  
**Supersedes:** None  
**Next Review:** After first SSDL-FULL project completion  
**Parent Standard:** AES-001 — SMRITI Product Constitution (SPC)

---

## About the Author

**Jawahar R. Mallah**  
Founder & Chief Architect, AITDL – AI Technology & Development Lab  
20+ Years of Experience in Software Development, Retail Technology, Distribution Systems,
POS Solutions, ERP Implementations, Business Process Automation, and Enterprise Application Design.

> *"Every implementation is the execution of a business decision. That decision must be
> explicitly documented, traceable, and approved before implementation begins.
> Code without a traceable business decision is a liability, not an asset."*
>
> — Jawahar R. Mallah

---

## Preamble

SSDL exists because **good engineering exists** — not because AI exists.

AI agents, human developers, code reviewers, QA engineers, and architects are all
participants in a single engineering process. The process must be consistent regardless
of which participant performs a given step.

The fundamental principle that governs every phase of this lifecycle:

> **Policy decision before code decision.**

Before any line of code is written, the business decision it executes must be explicitly
made, documented, owned, and approved. Software that exists without a traceable business
decision is a liability — it cannot be justified, maintained, or safely changed.

SSDL is the enforcement mechanism for this principle.

---

## Position in AITDL Engineering Standards Library

```
AES-001   SMRITI Product Constitution (SPC)       ← Supreme Law
AES-002   SMRITI Software Development Lifecycle (SSDL)  ← This Document
AES-003   SMRITI Evidence Standard
AES-004   SMRITI Architecture Decision Records (ADR) Guide
AES-005   SMRITI Engineering Naming Standards
AES-006   SMRITI Template Library
```

In the event of conflict between AES-002 and AES-001, AES-001 prevails.

---

## Architecture Model

SSDL governs all work within this architecture:

```
SMRITI Retail OS          ← UI / UX / Workflow / Intelligence
       ↓
Service Layer / APIs      ← SMRITI-owned service controllers
       ↓
Frappe Framework          ← Runtime and document engine
       ↓
ERPNext Core              ← Transaction engine and system of record
       ↓
Database
```

No phase of SSDL produces work that bypasses this stack.

---

## Track Selection

Not every task requires all 14 phases. The first act of every task is selecting the
correct SSDL track. The agent or developer documents the track selection and the
reason in the Phase 0 output.

| Track | Use Case | Mandatory Phases |
|---|---|---|
| **SSDL-PATCH** | Bug fixes, wording corrections, configuration changes | 0, 9, 10, 11 |
| **SSDL-STANDARD** | Enhancements to existing modules | 0, 1, 2, 6, 8, 9, 10, 11, 12 |
| **SSDL-FULL** | New modules, new pages, new APIs, architecture changes | All phases |

### Automatic SSDL-FULL Escalation Triggers

Any task matching one or more of the following **automatically** escalates to SSDL-FULL.
No agent or developer discretion applies:

- [ ] New DocType or database table introduced
- [ ] New `www/` page or API endpoint created
- [ ] Existing API contract changed (parameters, return shape, auth)
- [ ] User-facing URL routing changed
- [ ] New module or sub-module defined
- [ ] Capability Ownership assignment changed
- [ ] ERPNext hook added, modified, or removed
- [ ] SMRITI Product Constitution rule referenced or potentially impacted
- [ ] Cross-module dependency introduced
- [ ] Any change that alters what a user can or cannot do
- [ ] Business policy introduced, changed, or removed
- [ ] New domain entity introduced

---

## Phase Definitions

### Phase -1 — Problem Definition

**Purpose:** Define the business problem before any solution is considered.

**Required Outputs:**
- Problem statement (one paragraph, no solution language)
- Evidence (what observation, data, or user report established the problem)
- Business Impact (what fails, who is affected, how often)
- Desired Outcome (what success looks like, in business terms)
- Success Metrics (how success will be measured after deployment)

**Exit Criteria:**
- Problem is stated without referencing any implementation
- Evidence is cited, not assumed
- Success metrics are measurable, not descriptive
- Human stakeholder has confirmed the problem statement

**Artifact:** Problem Definition Document

---

### Phase 0 — Constitution Check

**Purpose:** Verify that the proposed work is permissible under AES-001 and confirm the SSDL track.

**Required Outputs:**
- Explicit statement of which SSDL track applies and why
- AES-002 version being followed
- Checklist confirming no SPC rules are violated by proceeding
- If SSDL-FULL: confirmation that all 13 subsequent phases will be executed

**Exit Criteria:**
- Track is selected and documented
- All SPC rules have been reviewed for applicability
- No SPC violation identified (if violation found: STOP, file ADR, await human decision)

**Artifact:** Constitution Compliance Statement

---

### Phase 1 — Discovery & Evidence

**Purpose:** Establish an accurate factual baseline of what currently exists.

**Required Outputs:**
- Inventory of existing implementations relevant to the problem
- Identification of duplicate or conflicting implementations
- Honest statement of what could not be determined and why
- No invented facts, no assumed histories

**Exit Criteria:**
- All findings are backed by direct observation (file read, API call, test output, screenshot)
- No claims made without cited evidence
- Gaps in knowledge are explicitly labeled "Unknown — not investigated" or "Unknown — not accessible"

**Artifact:** Discovery Report

---

### Phase 2 — Capability Ownership Map

**Purpose:** For every capability required to solve the problem, establish who owns it.

**Required Outputs:**
Capability Ownership Matrix with all seven columns completed:

| Capability | SMRITI | ERPNext | Shared | Gap | User-Facing | Adapter Required | Change Risk |
|---|---|---|---|---|---|---|---|

Column definitions:
- **SMRITI** ✅ — SMRITI owns and implements this capability
- **ERPNext** ✅ — ERPNext already fully implements this capability
- **Shared** ✅ — both systems participate; boundary must be defined
- **Gap** ✅ — no current owner; must be built
- **User-Facing** — does an end user interact with this directly?
- **Adapter Required** — if ERPNext owns it and SMRITI consumes it, an adapter is required
- **Change Risk** — HIGH (ERPNext-owned + adapter), MEDIUM (shared), LOW (SMRITI-owned), UNKNOWN (gap)

**Exit Criteria:**
- Every capability has exactly one primary owner assigned
- No capability is left without an ownership decision
- All ownership conflicts are documented and escalated (see SPC-011)
- No unresolved ownership conflicts remain

**Artifact:** Capability Ownership Matrix

---

### Phase 3 — Business Workflow Model

**Purpose:** Define the end-to-end business process — who does what, when, in what sequence,
and under what conditions.

**Required Outputs:**
- Workflow diagram or structured text: steps, roles, decision points, approval gates
- Role-action-permission table
- Approval thresholds (where applicable)
- Exception paths (what happens when the normal path fails)

**Exit Criteria:**
- Every workflow step has an assigned role
- Every approval gate is defined with its trigger condition
- Exception paths are documented (not implied)
- Workflow has been validated against the Capability Ownership Matrix (no step depends on a Gap capability)

**Artifact:** Business Workflow Model

---

### Phase 4 — Domain Model

**Purpose:** Define the business objects the system will manage, their structure, relationships,
lifecycle, and governing rules.

**Required Outputs:**
For every domain entity:

```
Entity Name
  Attributes    — fields and data types
  Relationships — links to other entities
  States        — all lifecycle states
  Transitions   — allowed state changes and conditions
  Invariants    — conditions that must be true at all times, in all states
  Owner         — which team or role is responsible for this entity
  Policies      — workflow rules that govern transitions
```

**Invariants vs Policies — Distinction:**
- **Invariants** govern existence: `total_amount = sum(line_items)` (always true)
- **Policies** govern transitions: `cannot cancel after payment` (governs a state change)

**Exit Criteria:**
- Every entity referenced in the workflow has a domain model entry
- Every entity has at least one state and one invariant defined
- No entity is modeled that duplicates ERPNext master data without justification

**Artifact:** Domain Model

---

### Phase 5 — UX Blueprint

**Purpose:** Define the user experience — what the user sees, what they can do, and how
the interface maps to the business workflow.

**Required Outputs:**
- Page inventory (every new page with its route and purpose)
- Navigation map (how the user reaches each page)
- Component inventory (forms, grids, modals, KPI cards, filters)
- User journey walkthrough (step-by-step narrative for each primary workflow)
- Accessibility and permission notes (who sees what)

**Exit Criteria:**
- Every page has a defined SMRITI route (`/smriti-*` or approved equivalent)
- No page routes to `/desk`, `/app/ERPNext-form`, or any Frappe native UI
- Every component maps to a capability in the Capability Ownership Matrix
- Design follows SMRITI design system (Navy #1A2B5C + Blue #2563EB + Arial)

**Artifact:** UX Blueprint

---

### Phase 6 — Service Contracts

**Purpose:** Define the API surface that connects the UI to the business logic, and the
service layer that connects business logic to ERPNext.

**Required Outputs:**
For every API endpoint:
```
Endpoint name
  Method, authentication, permissions
  Input parameters (name, type, required, validation)
  Output structure (fields, types, error codes)
  Side effects (what changes in the system)
  ERPNext dependency (if any — and the adapter pattern used)
```

**Mandatory Anti-Pattern Documentation:**
Every Service Contract must include an explicit list of what is forbidden:
```python
# FORBIDDEN — direct DocType insert from UI
frappe.client.insert({"doctype": "Purchase Invoice", ...})

# FORBIDDEN — direct GL manipulation from service
frappe.db.insert("GL Entry", ...)

# CORRECT
purchase_service.create_invoice_from_grn(grn_id, company)
```

**Exit Criteria:**
- Every user action in the UX Blueprint maps to exactly one service endpoint
- No endpoint bypasses the service layer
- No endpoint allows direct DocType manipulation from the frontend
- All ERPNext integrations are wrapped in named adapter functions

**Artifact:** Service Contract

---

### Phase 7 — Architecture Review

**Purpose:** Validate that the proposed design holds under real-world conditions — not just
in the happy path.

**Required Questions (must all be answered):**
- What happens if ERPNext upgrades and a field changes?
- What happens if the service is called concurrently?
- What happens if the user cancels mid-workflow?
- What is the rollback strategy for each destructive operation?
- Does this design create any new coupling between previously independent modules?
- Does any new capability duplicate something ERPNext already provides?
- Are all audit trail requirements satisfied?

**Exit Criteria:**
- All seven questions answered with specific, not generic, responses
- No unanswered "it depends" statements without documented conditions
- Architecture Review signed off by human architect for SSDL-FULL tasks

**Artifact:** Architecture Review Document

---

### Phase 8 — Implementation Plan

**Purpose:** Produce a concrete, sequenced plan for writing the code.

**Required Outputs:**
- File list: every file to be created, modified, or deleted
- Dependency order: which files must be created before others
- Test plan: what will be tested and how
- Rollback plan: how to safely revert if deployment fails
- Effort estimate: not a guarantee, but a calibrated forecast

**Exit Criteria:**
- Every file in the plan references a specific Phase 6 service contract or Phase 5 component
- Test plan covers at minimum: happy path, error path, permission boundary
- Rollback plan is documented (not "we'll figure it out")

**Artifact:** Implementation Plan

---

### Phase 9 — Source Code

**Purpose:** Implement the approved plan.

**Required Outputs:**
- All source code changes
- Git diff for every modified file (literal, not paraphrased)
- Commit message referencing the Problem Definition and Implementation Plan
- HTML template validation passed (TEMPLATE-01 pre-commit hook)

**Exit Criteria:**
- Every committed file has a corresponding entry in the Implementation Plan
- No file is committed that was not planned (if discovered during implementation, return to Phase 8)
- All pre-commit hooks pass
- Commit message is traceable to the business decision

**Artifact:** Source Code (committed to version control with traceable commit message)

---

### Phase 10 — Verification

Verification has two mandatory and distinct sub-phases. Both must pass before proceeding.

#### Phase 10A — Technical Verification

**Purpose:** Confirm the code does what the specification says.

**Required Outputs:**
- Literal test runner output (not summarized)
- Literal git diff for every changed file
- Linter / validator output (literal)
- Before-and-after measurements for any claimed metric

**Exit Criteria:**
- All automated tests pass
- No regressions in existing test suite
- All evidence is literal terminal output — no paraphrased summaries

#### Phase 10B — Business Validation

**Purpose:** Confirm that what the specification said is what the business needed.

**Required Outputs:**
- Walkthrough of each primary workflow against the Phase 3 Business Workflow Model
- Confirmation that every Success Metric from Phase -1 can now be measured
- Documentation of any workflow that passed technical tests but failed business validation

**Exit Criteria:**
- Every Phase -1 Success Metric has a measured result
- No workflow fails business validation (if failures found: return to Phase 8 with documented reason)

**Artifact:** Verification Report (Technical + Business sections)

---

### Phase 11 — Deployment

**Purpose:** Move verified code to the target environment safely and traceably.

**Required Outputs:**
- Deployment commands executed (literal)
- Output of deployment commands (literal)
- Smoke test results post-deployment
- Confirmation that rollback plan was reviewed before deployment

**Exit Criteria:**
- Deployment completed without errors
- Smoke tests pass in target environment
- Deployment record is committed or filed

**Artifact:** Deployment Record

---

### Phase 12 — Knowledge Update

**Purpose:** Close the learning loop. Update all standards, documentation, and institutional
knowledge so the next project starts smarter than this one did.

**Required Outputs:**
- Lessons learned (what the team now knows that it didn't at Phase -1)
- Capability Ownership Matrix updates (if any ownership changed during implementation)
- Domain Model updates (if any new entity or state was discovered)
- SPC amendments filed (if any rule gap was found)
- Problem Definition template improvements (if Phase -1 missed anything)

**Feedback Loop:**
Phase 12 outputs feed directly into Phase -1 of the next project:

```
Phase 12 (Knowledge Update)
    │
    ├── Updates SSDL templates (AES-006)
    ├── Updates Capability Ownership Matrix
    ├── Updates Domain Model
    ├── Proposes new SPC rules (filed as ADRs)
    └── Enriches Problem Definition template for next cycle
```

**Exit Criteria:**
- At least one lesson learned documented (even if the lesson is "the plan was correct")
- All discovered gaps in standards are filed as ADRs or SPC amendment proposals

**Artifact:** Knowledge Update Document

---

## Artifact Traceability Chain

Every artifact references the artifact that preceded it. This produces end-to-end traceability
from business problem to deployed code to institutional knowledge.

```
Problem Definition (Phase -1)
        │ referenced by
        ▼
Constitution Compliance Statement (Phase 0)
        │ referenced by
        ▼
Discovery Report (Phase 1)
        │ referenced by
        ▼
Capability Ownership Matrix (Phase 2)
        │ referenced by
        ▼
Business Workflow Model (Phase 3)
        │ referenced by
        ▼
Domain Model (Phase 4)
        │ referenced by
        ▼
UX Blueprint (Phase 5)
        │ referenced by
        ▼
Service Contract (Phase 6)
        │ referenced by
        ▼
Architecture Review (Phase 7)
        │ referenced by
        ▼
Implementation Plan (Phase 8)
        │ referenced by
        ▼
Source Code (Phase 9)
        │ referenced by
        ▼
Verification Report (Phase 10)
        │ referenced by
        ▼
Deployment Record (Phase 11)
        │ referenced by
        ▼
Knowledge Update (Phase 12)
        │ feeds back into
        ▼
Problem Definition — Next Project (Phase -1)
```

---

## Artifact Requirements by Track

| Phase | Artifact | PATCH | STANDARD | FULL |
|---|---|---|---|---|
| -1 | Problem Definition | ⚪ | ✅ | ✅ |
| 0 | Constitution Compliance Statement | ✅ | ✅ | ✅ |
| 1 | Discovery Report | ⚪ | ✅ | ✅ |
| 2 | Capability Ownership Matrix | ❌ | ✅ | ✅ |
| 3 | Business Workflow Model | ❌ | ⚪ | ✅ |
| 4 | Domain Model | ❌ | ⚪ | ✅ |
| 5 | UX Blueprint | ❌ | ⚪ | ✅ |
| 6 | Service Contract | ❌ | ✅ | ✅ |
| 7 | Architecture Review | ❌ | ⚪ | ✅ |
| 8 | Implementation Plan | ⚪ | ✅ | ✅ |
| 9 | Source Code + Diff | ✅ | ✅ | ✅ |
| 10 | Verification Report (10A + 10B) | ✅ | ✅ | ✅ |
| 11 | Deployment Record | ✅ | ✅ | ✅ |
| 12 | Knowledge Update | ⚪ | ⚪ | ✅ |

`✅ Required` `⚪ Required if applicable` `❌ Not required for this track`

---

## SPC Rules Referenced by SSDL

### SPC-009 — Policy Before Implementation

> When multiple technically valid implementations exist, the business policy must be defined
> before selecting an implementation. AI agents shall not infer policy from framework defaults.

### SPC-010 — Ownership Before Construction

> Before creating any new module, page, service, API, workflow, or report, the AI agent shall
> identify whether the capability is owned by SMRITI, the underlying framework, shared, or
> currently unowned (Gap). New implementation shall not begin until ownership has been established.

### SPC-011 — Conflict Escalation

> AI agents shall not resolve business policy conflicts autonomously. When multiple valid policies
> exist, the conflict must be documented, options presented with trade-offs, and implementation
> paused pending human architectural decision. The resolution decision becomes an ADR entry.

**Conflict Resolution Protocol:**
1. Agent documents the conflict in the Capability Ownership Matrix
2. Agent proposes 2–3 resolution options with trade-offs
3. Agent STOPS and escalates to human architect
4. Human documents the resolution (filed as ADR or SPC amendment)
5. Agent resumes from the Phase where the conflict was found

---

## AI Agent Directive

When this document is in scope, AI agents shall:

```
1. Read SSDL before beginning any task.
2. Select the correct track at Phase 0 and document the selection.
3. Cite this document version in the Constitution Compliance Statement.
4. Produce all mandatory artifacts for the selected track.
5. Not advance to the next phase until all exit criteria of the current phase are met.
6. Not write code before Phase 8 is complete and approved.
7. Not resolve business policy conflicts — escalate per SPC-011.
8. Produce all verification evidence as literal output, never as summaries.
9. Not declare a task "done" unless Phase 10B (Business Validation) is complete.
10. Produce a Knowledge Update artifact at Phase 12 for every SSDL-FULL task.
```

---

## Revision Protocol

SSDL v1.0 shall be revised when any of the following occur:

1. The first SSDL-FULL project completes — Phase 12 lessons learned incorporated
2. A phase is consistently bypassed with documented justification (signals a structural gap)
3. A new SPC rule is added that impacts phase sequencing
4. A new capability category arises not covered by the Capability Ownership Matrix
5. Revision requested by Chief Architect with documented rationale filed as ADR

**Version numbering:**
- Minor clarifications, template improvements: v1.x
- Phase additions, removals, or resequencing: v2.0

**Amendment process:** ADR filed → reviewed → approved by Authority → version incremented → old version archived

---

## Document History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-07-01 | Jawahar R. Mallah | Initial release |

---

*AITDL Engineering Standard AES-002 — SMRITI Software Development Lifecycle v1.0.0*  
*Authority: Jawahar R. Mallah, Founder & Chief Architect, AITDL*  
*"Always decision-ready."*
