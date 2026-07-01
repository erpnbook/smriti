# SMRITI CONSTITUTION
## Draft v0.2 — Enforcement-Mapped Edition
**Status:** DRAFT (not LOCKED, not FROZEN)
**File:** `SMRITI_CONSTITUTION_DRAFT_v0.1.md`
**Internal Version:** 0.2 (amended 2026-07-01 — see Amendment Log)

---

## Authority Statement

This document has highest authority over AI-agent behavior in this repository,
subject to the enforcement mechanisms listed below actually being run.
**An article without a passing check attached to a PR does not block that PR.**
Aspirational articles are marked as such and carry no blocking authority until promoted.

An article with severity **Critical** blocks merge on FAIL.
An article with severity **Major** blocks merge on FAIL unless an active ADR is attached.
An article with severity **Minor** produces a WARNING that does not block merge.
An article with severity **Informational** is logged only.

---

## Scope

Applies to all files in this repository **except:**

- `/vendor/`
- `/node_modules/`
- `/build/`
- `/.git/`
- Any directory containing a `.smriti-constitution-ignore` marker file

Scanners must exclude these paths to avoid noise. Any exclusion beyond the
list above requires an ADR.

---

## Definitions

| Term | Meaning |
|---|---|
| **Adopted Article** | Has an enforcement mechanism. Binding now. |
| **Candidate Article** | Documented, parked. No blocking authority until promoted. |
| **ADR** | Architecture Decision Record — documents a constitutional exception with an expiry date. |
| **Evidence Level A** | Literal terminal output or git commit hash, independently reproducible. |
| **Evidence Level B** | Scan output or screenshot attached to PR, not paraphrased. |
| **Evidence Level C** | Reference to existing passing test. |
| **Evidence Level D** | Agent assertion only. Not accepted as evidence of completion. |
| **SPC-NNN** | SMRITI Policy Constraint — stable rule ID that does not change when articles are reordered. |

---

## Enforcement Levels

| Severity | PR Effect | CI Status |
|---|---|---|
| **Critical** | Blocks merge on FAIL | PASS / FAIL |
| **Major** | Blocks merge on FAIL unless active ADR attached | PASS / FAIL / ADR-EXEMPT |
| **Minor** | Does not block merge | PASS / WARNING |
| **Informational** | Logged only | INFO |

---

## ADOPTED ARTICLES (enforceable now)

---

### SPC-001 — No Framework Leakage
**Severity:** Critical
**Merges:** original Articles 1, 2, 3

Operational users must never see ERPNext/Frappe naming, Desk UI, DocType
labels, or framework branding. Every user-facing surface belongs to SMRITI.

**Denylist terms (case-insensitive, in page titles, visible text, HTML attributes):**
`ERPNext`, `Frappe`, `Desk`, `DocType`, `bench`, `frappe.client` (in www HTML)

**Enforcement:**
Pre-merge grep/AST scan of `www/*.html`, `public/js/*.js`, and page `<title>` tags
for denylist terms. Raw scan output attached to PR as Evidence Level B.
Scanner script: `scripts/scan_framework_leakage.sh` (to be written — see Owner action).

**CI Status output format:**
```
SPC-001  PASS    0 violations found across 47 HTML files
SPC-001  FAIL    3 violations: smriti-help.html:12, configure.html:400, smriti-cge.html:865
SPC-001  WARNING 1 exception: ADR-0003 (expires Sprint 14)
```

**Owner action needed:** Write `scripts/scan_framework_leakage.sh` — decide CI step vs. manual pre-merge command.

---

### SPC-002 — Single Source of Truth / No Duplicates
**Severity:** Major
**Merges:** original Articles 4, 12, 15

Before creating a menu, report, DocType, route, API endpoint, widget, nav
entry, or theme token, the agent must search the repository for an existing
equivalent and justify why reuse is not possible.

**Enforcement:**
PR description must include a "prior-art search" section: what was searched,
what was found, why it was not reused. Evidence Level B.
This is a documentation requirement — flag honestly that it is not fully
automatable without semantic matching tooling.

**CI Status output format:**
```
SPC-002  PASS    Prior-art section present in PR description
SPC-002  FAIL    PR description missing prior-art search section
```

**Owner action needed:** Decide if manual-attestation-only or automated duplicate-detection script.

---

### SPC-003 — Safe Refactoring / No Delete or Rename Without Evidence
**Severity:** Critical
**Merges:** original Articles 13, 18

No file, function, route, or DocType may be deleted, renamed, or moved without
an attached dependency scan, reference scan, import scan, and usage scan.

**Enforcement:**
PR must attach raw scan output (grep/ripgrep results), not a summary claiming
"no references found." Evidence Level A. Scan must cover:
- Import references (`import`, `from`, `require`)
- URL references (`href`, `window.location`, `frappe.set_route`)
- Python module path references
- Test file references

**CI Status output format:**
```
SPC-003  PASS    Dependency scan attached, 0 live references found for deleted item
SPC-003  FAIL    No scan attached for deletion of smriti_sidebar.js
SPC-003  FAIL    Scan summary present but raw output missing (Level D not accepted)
```

---

### SPC-004 — Evidence-First Completion
**Severity:** Critical
**New; formalizes existing practice**

An agent's self-report that a task is "done," "fixed," or "tested" is not
accepted as evidence. Required: git commit hash (independently verifiable),
raw terminal/test output, or screenshot — Evidence Level A or B.
Evidence Level D (agent assertion only) is explicitly rejected.

**Enforcement:**
Any PR or completion report that contains "done", "fixed", "verified", "tested",
"all passing", or equivalent without an attached Evidence Level A/B artifact
is treated as unverified. The verification state must be one of exactly four
values: `Done`, `Failed`, `Partially Verified`, `Unverified`.

**CI Status output format:**
```
SPC-004  PASS    Commit hash a39b2f1 verified in git log; terminal output attached
SPC-004  FAIL    Completion claim with no attached evidence artifact
```

---

### SPC-005 — AI Honesty Principle
**Severity:** Critical
**New article (added v0.2)**

An AI agent must distinguish between verified facts, inferred conclusions,
and assumptions. It must never fabricate commits, test results, scan outputs,
repository contents, or implementation status. If evidence is unavailable,
it must explicitly state that it cannot verify the claim.

**Specific prohibitions:**
- Fabricating a git commit hash that does not exist in the repository
- Summarizing or paraphrasing scan output instead of pasting literal terminal output
- Narrowing a scan filter to exclude the exact violations being checked (self-defeating filter)
- Claiming "NONE" or "ALL PASS" on a check that was not actually run against the real files
- Reporting a score (e.g. "100/100") that includes unverified or false sub-claims

**Verification mechanism (cannot be fully automated — requires review):**
- Every completion claim must include an artifact (Evidence Level A or B)
- Every architecture statement must cite repository evidence or explicitly
  label itself as an inference
- Fabricated evidence is treated as a Critical constitutional violation
- Git log must be run and pasted — never assumed from prior session memory

**Precedent cases in this repository:**
- Fabricated commit hashes (caught in Phase 5)
- Self-defeating scan filter `Where-Object { $_.Line -notmatch "smriti-|/app/smriti" }`
  that excluded the exact violations being scanned for (caught 2026-07-01)
- "100/100 Route Isolation" claim where smriti-home.html had 6 live violations (caught 2026-07-01)

**CI Status output format:**
```
SPC-005  PASS    Evidence artifact attached; git hash verified in live repo
SPC-005  FAIL    Completion claim with no attached artifact
SPC-005  FAIL    Scan filter excludes the domain being scanned
```

---

## Constitutional Test Suite

Location: `tests/constitution/`

| File | Tests |
|---|---|
| `test_spc001_framework_leakage.py` | Scans www/*.html and public/js/*.js for denylist terms |
| `test_spc002_duplicate_policy.py` | (Manual attestation; placeholder for future semantic scan) |
| `test_spc003_safe_refactor.py` | Detects deleted/renamed files without attached scan in PR |
| `test_spc004_evidence_first.py` | Validates completion reports contain Evidence Level A/B artifacts |
| `test_spc005_honesty.py` | Checks git hashes in session reports exist in actual git log |

Run: `bench run-tests --app smriti_retail_os --module smriti_retail_os.tests.constitution`

**Note:** SPC-003 and SPC-005 tests are partially manual — they check format/artifact
presence, not semantic correctness. A human reviewer must still read the evidence.

---

## CANDIDATE ARTICLES (documented, not adopted — no enforcement mechanism yet)

These carry **no blocking authority**. Parked until each gets a real check attached.

| ID | Candidate | Original # | Blocker before adoption |
|---|---|---|---|
| — | Zero Hardcoding | 5 | Needs config layer + measurable % threshold, not "zero" |
| — | Metadata-First | 6 | Needs in-scope subsystem definition first |
| — | Explainability-First | 7 | Derive from PSV SKU explainability work, not written fresh |
| — | Business-First Language | 8 | Needs user-facing glossary to check against |
| — | Studio Philosophy | 9 | Naming convention — low priority |
| — | Engine Philosophy | 10 | Same |
| — | Registry Philosophy | 11 | Same |
| — | Backward Compatibility | 14 | Needs compatibility test suite (does not exist yet) |
| — | Naming Convention | 16 | Cosmetic — defer |
| — | AI Dev Rules (search→reuse→create) | 17 | Overlaps SPC-002 — merge once SPC-002 mechanism proven |
| — | Quality Gate (7-category PR check) | 19 | Each sub-check must exist independently first |
| — | Final Authority clause | 20 | Meaningless until SPC-001–005 enforced |

---

## ADR Process (Architecture Decision Records)

Every constitutional exception requires an ADR. ADRs without expiry dates are rejected.

**ADR Format:**

```
## ADR-NNNN — [Title]
**SPC violated:** SPC-001
**Severity:** Critical
**Reason:** [Why the exception is necessary]
**Scope:** [Exactly which file(s) or function(s) are exempt]
**Expiry:** Sprint 14 / v2.1 / 2026-09-30 (one of these three formats)
**Owner:** [Who approved this]
**Status:** ACTIVE | EXPIRED | REVOKED
```

**Rules:**
- An expired ADR that has not been renewed automatically revokes the exception
- An ADR covering a "temporary" ERPNext page that has no expiry date is not a valid ADR
- ADRs are stored in `docs/adr/ADR-NNNN.md`
- The ADR index is `docs/adr/README.md`

---

## Consolidation Task (before promotion past DRAFT)

Audit and fold in — goal is **one document**, not this draft plus four others:

| Existing Document | Action |
|---|---|
| `GEMINI.md` Rules 1–13 | Reference, do not restate. Where conflict exists, this constitution takes precedence once LOCKED. |
| `ARCHITECTURE.md` Section 5 (15 Locked Rules) | Cross-reference. Architectural rules stay there; enforcement process lives here. |
| `SDC_ARCHITECTURE.md` Section 4 | Review for overlap. Consolidate or reference. |
| Evidence Level A/B/C/D definition | Already restated in Definitions above — remove from other docs once this is LOCKED. |
| `AGENTS.md` Rules 1–10 | Most of these are formalized in SPC-004 and SPC-005. Reconcile. |

---

## Promotion Path

```
DRAFT    — No blocking authority. Agent must still follow checklist.
  ↓
REVIEW   — Owner reads, edits, resolves open questions.
  ↓
LOCKED   — Adopted articles are binding. Enforcement scripts exist and run.
           No AI agent may modify this document without owner approval.
  ↓
FROZEN   — No further changes without a formal amendment + ADR.
           Even owner changes require Amendment Log entry.
```

This document does not self-promote. Status line at the top is the single source of truth.

---

## Pre-Task Agent Checklist

BEFORE writing, editing, or deleting any code in this repository:

**Step 1.** Read `SMRITI_CONSTITUTION_DRAFT_v0.1.md` in full.

**Step 2.** State which SPC articles apply to this task, and how you will
satisfy each one's enforcement requirement BEFORE starting work. Name exactly
what evidence you will produce.

**Step 3.** Candidate Articles are NOT binding. Do not cite them as a reason
to block, refuse, or restructure a task. Ask explicitly if you believe one
should apply.

**Step 4.** Self-reported completion is not evidence (SPC-004). Attach the
artifact: git commit hash, raw terminal output, or screenshot. If you cannot
produce it, say so.

**Step 5.** If this task deletes, renames, or moves any file/function/route/
DocType (SPC-003), attach the raw dependency/reference/import/usage scan
output BEFORE making the change.

**Step 6.** If this task creates a new menu, report, DocType, route, API
endpoint, widget, or nav entry (SPC-002), state what you searched for and
why an existing equivalent could not be reused.

**Step 7.** Do not proceed until steps 1–6 are complete.

**Step 8.** If your scan or check produced a result of "NONE" or "ALL PASS,"
state the exact command run and paste the literal output. Do not filter the
results in a way that excludes the domain being checked (SPC-005).

Violating an Adopted Article is an invalid implementation regardless of
whether code compiles or passes tests. Citing a Candidate Article as binding
is also a violation.

---

## Amendment Log

| Version | Date | Change | Author |
|---|---|---|---|
| v0.1 | 2026-07-01 | Initial draft — enforcement-mapped edition | Jawahar R. Mallah |
| v0.2 | 2026-07-01 | Added SPC-IDs; severity levels; ADR process with expiry; CI status format; repository scope exclusions; constitutional test suite structure; SPC-005 AI Honesty Principle; Step 8 to agent checklist | Jawahar R. Mallah |