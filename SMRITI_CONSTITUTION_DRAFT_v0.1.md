# SMRITI CONSTITUTION
## Draft v0.1 — Enforcement-Mapped Edition
**Status:** DRAFT (not LOCKED, not FROZEN)
**File:** `/SMRITI_CONSTITUTION_DRAFT_v0.1.md`

---

## Why this draft differs from the v1.0 concept

The original 20-article proposal reads well but has three structural problems,
consistent with issues already caught in prior SMRITI audits:

1. **No enforcement mechanism per article.** A rule with no automated or
   evidence-based check is a suggestion, not a law — and agents in this
   project have a documented history of self-reporting completion without
   independent evidence (fabricated commits, fabricated index names,
   narrowed-scope "checks" that miss the real issue).

2. **Governance sprawl.** SMRITI already has GEMINI.md, the UI Configuration
   Engine principles (#01/#02), Rule 7, and the Evidence Level (A/B/C/D)
   system. Adding three more top-level documents before consolidating what
   exists violates the "Single Source of Truth" article it's trying to
   establish.

3. **Absolute language without measurable thresholds.** "Zero hardcoding,"
   "never," "always" — these read like law but can't be audited. The Theme
   sprint already demonstrated this trap: a token-adoption rate that *looked*
   compliant on paper flipped from CONDITIONAL GO to NO-GO once actually
   scanned.

This draft keeps only articles that have a concrete, checkable enforcement
mechanism attached. Everything else is listed as a **Candidate Article** —
same status as PSV Phase 1.3: documented, not adopted, blocked until a
mechanism is designed.

---

## Authority Statement

This document has highest authority over AI-agent behavior in this
repository, subject to the enforcement mechanisms listed below actually
being run. **An article without a passing check attached to a PR does not
block that PR.** Aspirational articles are marked as such and carry no
blocking authority until promoted.

---

## ADOPTED ARTICLES (enforceable now)

### Article 1 — No Framework Leakage
*(merges original Articles 1, 2, 3)*

Operational users must never see ERPNext/Frappe naming, Desk UI, DocType
labels, or framework branding. Every user-facing surface belongs to SMRITI.

**Enforcement:** Pre-merge grep/AST scan of templates, JS, and page titles
for a denylist of framework terms (`Desk`, `DocType`, `Workspace`, `Frappe`,
`ERPNext`, `bench`). Scan output attached to PR as Evidence Level B.
Already partially covered by Rule 7 — this article formalizes it as a
checked gate rather than a stated policy.

**Owner action needed:** write the scanner script; decide whether it's a
CI step or a manual pre-merge command.

---

### Article 2 — Single Source of Truth / No Duplicates
*(merges original Articles 4, 12, 15)*

Before creating a menu, report, DocType, route, API endpoint, widget, nav
entry, or theme token, the agent must search the repository for an existing
equivalent and justify why reuse isn't possible.

**Enforcement:** PR description must include a "prior-art search" section:
what was searched, what was found, why it wasn't reused. Evidence Level B.
This is a documentation requirement, not a blocking automated check — flag
this honestly rather than pretending it's automatable without more tooling.

**Owner action needed:** decide if this stays manual-attestation-only or if
you want a real duplicate-detection script (harder — would need semantic,
not just textual, matching).

---

### Article 3 — Safe Refactoring / No Delete or Rename Without Evidence
*(merges original Articles 13, 18)*

No file, function, route, or DocType may be deleted, renamed, or moved
without an attached dependency scan, reference scan, import scan, and usage
scan.

**Enforcement:** PR must attach raw scan output (grep/ripgrep results or
equivalent), not a summary claiming "no references found." Evidence Level A
— matches your existing standard for anything claimed "complete."
This is the article closest to what you already do manually; the only
change is making the scan output a hard PR-attachment requirement instead
of an on-request one.

---

### Article 4 — Evidence-First Completion
*(new; formalizes existing practice)*

An agent's self-report that a task is "done," "fixed," or "tested" is not
accepted as evidence. Required: git commit hash (independently verifiable),
raw terminal/test output, or screenshot — matching Evidence Level A/B
criteria already established for this project.

**Enforcement:** This is already your practice; codifying it here just
means new agents joining the project inherit the standard instead of
re-learning it after a fabrication incident.

---

## CANDIDATE ARTICLES (documented, not adopted — no enforcement mechanism yet)

These are not rejected — they are parked, same status as PSV Phase 1.3,
until each one gets a real check attached. They carry **no blocking authority**
in this draft.

| Candidate | Original Article # | Blocker before adoption |
|---|---|---|
| Zero Hardcoding | 5 | Needs a defined config layer + threshold |
| Metadata-First | 6 | Needs a definition of which subsystems are in-scope first |
| Explainability-First | 7 | Overlaps with PSV SKU explainability work — derive from that |
| Business-First Language | 8 | Needs a user-facing glossary to check against |
| Studio Philosophy | 9 | Naming convention, not a law — low priority |
| Engine Philosophy | 10 | Same as above |
| Registry Philosophy | 11 | Same as above |
| Backward Compatibility | 14 | Needs a compatibility test suite that does not exist yet |
| Naming Convention | 16 | Cosmetic — defer |
| AI Development Rules | 17 | Overlaps Article 2 — merge once Article 2 mechanism is proven |
| Quality Gate (7-category PR check) | 19 | Each sub-check must exist independently first |
| Final Authority clause | 20 | Meaningless without Articles 1-4 enforced first |

---

## Consolidation Task (do this before adding anything else)

Before this draft is promoted past DRAFT, audit and fold in:

- GEMINI.md (SMRITI UI wrapper mandate)
- SMRITI_UI_CONFIGURATION_ENGINE_V1.md, Architecture Principles #01/#02
- Rule 7 (no Frappe/ERPNext UI exposure)
- Evidence Level A/B/C/D system definition

The goal is **one document**, not this draft plus four others.

**Existing documents found (prior-art search, 2026-07-01):**

| File | Contains |
|---|---|
| ARCHITECTURE.md | Section 5: Architecture Constitution — 15 Locked Rules |
| README.md | References SMRITI Architecture Constitution |
| SDC_ARCHITECTURE.md | Section 4: Governance Constitutions |
| GEMINI.md | Rules 1-13 (UI mandate, PSV boundary, evidence standards) |

---

## Promotion Path

DRAFT
  -> REVIEW  (owner reads, edits, resolves open questions)
  -> LOCKED  (adopted articles binding, enforcement scripts exist and run)
  -> FROZEN  (no further changes without a formal amendment process)

This document does not self-promote. It stays DRAFT until the owner
explicitly changes the status line at the top.

---

## Pre-Task Agent Checklist

BEFORE writing, editing, or deleting any code in this repository:

1. Read /SMRITI_CONSTITUTION_DRAFT_v0.1.md in full.
2. State which Adopted Articles (1-4) apply to this task, and how you will
   satisfy each one's enforcement requirement BEFORE you start work.
   If an article requires attached evidence (scan output, git hash, terminal
   output), name exactly what evidence you will produce.
3. Candidate Articles (see table) are NOT binding. Do not cite them as a
   reason to block, refuse, or restructure a task. If you believe a
   Candidate Article should apply, say so explicitly and ask.
4. Self-reported completion ("done", "fixed", "tested", "verified") is not
   accepted as evidence under Article 4. Every completion claim must include
   the actual artifact: git commit hash, raw terminal/test output, or
   screenshot. If you cannot produce that artifact, say so.
5. If this task requires deleting, renaming, or moving any file, function,
   route, or DocType (Article 3), attach the dependency/reference/import/
   usage scan output BEFORE making the change.
6. If this task requires creating a new menu, report, DocType, route, API
   endpoint, widget, or nav entry (Article 2), state what you searched for
   in the existing codebase and why an existing equivalent could not be reused.
7. Do not proceed until steps 1-6 are complete.

Violating an Adopted Article is an invalid implementation regardless of
whether the code compiles or passes tests. Citing a Candidate Article as if
it were binding is also a violation of this instruction.

---

## Amendment Log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1 | 2026-07-01 | Initial draft — enforcement-mapped edition | Jawahar R. Mallah |