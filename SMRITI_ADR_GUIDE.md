# SMRITI Architecture Decision Record (ADR) Guide
**Status:** DRAFT
**File:** `/SMRITI_ADR_GUIDE.md`
**Internal Version:** 1.0.0 (Established 2026-07-01)

---

## Architectural Decision Records (ADRs)

Every constitutional exception, major architectural change, or temporary bypass of an Adopted Article (SPC-001 through SPC-007) requires a formal Architecture Decision Record.

### ADR Rules
1. **Mandatory Expiry Date:** Every ADR that grants a temporary exception to an SPC must define a clear, non-negotiable expiry condition (e.g. Sprint number, version, or calendar date).
2. **Auto-Revocation:** When an ADR reaches its expiry condition, the exception is automatically revoked. The CI engine or human reviewer must treat any remaining violation as an active failure.
3. **No Permanent Exceptions:** Any permanent exception to a constitutional constraint requires a formal amendment to the SMRITI Product Constitution (SPC), not an ADR.
4. **Storage Location:** ADRs are stored as individual markdown files under `/docs/adr/ADR-NNNN.md` (where `NNNN` is a sequential 4-digit number starting at `0001`).
5. **Single Source of Index:** All active and historical ADRs must be listed in `/docs/adr/README.md`.

---

## ADR Template

All ADR files must strictly follow this structure:

```markdown
# ADR-NNNN — [Title of the Decision]

- **Status:** [PROPOSED | ACTIVE | EXPIRED | REVOKED | SUPERSEDED]
- **SPC Violated:** [SPC-NNN or "None" if general architecture]
- **Severity Level:** [Critical | Major | Minor]
- **Author:** [Developer name]
- **Date Created:** [YYYY-MM-DD]
- **Expiry Condition:** [Sprint N | Version X.Y.Z | YYYY-MM-DD]

---

## Context and Problem Statement
[Describe the problem, constraints, and why a temporary exception or specific architecture is required.]

## Decision
[Document the decision, chosen solution, and the exact files/functions exempt from the SPC.]

## Consequences
[Describe what becomes possible or difficult as a result. Outline the path to resolution before the expiry condition is met.]
```

---

## Consolidated ADR Registry Index

The ADR registry index lives in `/docs/adr/README.md` and contains this layout:

| ADR ID | Title | Status | Violates | Expiry | Status Checked |
|---|---|---|---|---|---|
| ADR-0001 | [Example ADR] | ACTIVE | SPC-001 | Sprint 14 | 2026-07-01 |
| ADR-0002 | [Example ADR] | EXPIRED | SPC-003 | v2.1.0 | 2026-07-01 |