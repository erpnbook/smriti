# SMRITI Governance & CI Specification
**Status:** DRAFT
**File:** `/SMRITI_GOVERNANCE.md`
**Internal Version:** 1.0.0 (Established 2026-07-01)

---

## Evidence Levels

SMRITI utilizes a structured evidence framework to categorize and evaluate all verification claims made by developer agents:

### Evidence Level A (Verifiable Live Artifacts)
- **Definition:** Raw, reproducible log outputs directly from the system, or a verifiable Git commit hash.
- **Examples:**
  - Standard output/error of a test runner (e.g. `pytest` or `bench run-tests`)
  - A real, pushed git commit hash (e.g. `39cdcfb` verified in `git log`)
  - Actual console output of an AST linter or validator
- **Usage:** Required for SPC-003 (Refactoring) and SPC-004 (Completion).

### Evidence Level B (Attached Visual/Static Artifacts)
- **Definition:** Human-verifiable attachments that document a state but are not directly executable in a terminal.
- **Examples:**
  - Raw directory scan outputs (grep / ripgrep logs)
  - Browser screenshots showing UI rendering
  - Video recordings of automated browser tests
- **Usage:** Required for SPC-001 (Leakage) and SPC-002 (Prior-Art).

### Evidence Level C (Reference to Existing Passing Test)
- **Definition:** Pointing to an automated test that is already integrated into the main branch test suite.
- **Usage:** Used for verifying regression safety.

### Evidence Level D (Agent Assertion Only)
- **Definition:** Pure prose statements, summaries, or assertions made by the agent without attached logs, hashes, or screenshots.
- **Usage:** **EXPLICITLY REJECTED** as evidence of completion or correctness.

---

## Enforcement Levels & CI Actions

Each SMRITI Policy Constraint (SPC) is mapped to a severity level that defines its behavior in the CI/CD pipeline:

| Severity | PR Merge Effect | CI Status | Action on FAIL |
|---|---|---|---|
| **Critical** | Blocks merge automatically | FAIL | PR cannot be merged. Exit 1. |
| **Major** | Blocks merge unless exempt | FAIL | PR blocked unless a valid ADR is attached. |
| **Minor** | Warning only | WARNING | PR can merge. Issues logged in summary. |
| **Informational** | No block, logged | INFO | Educational logging only. |

---

## CI Status Reporting Format

When the test suite or CI engine runs the SMRITI Product Constitution tests, it must output a structured, parsable status table at the end of the log:

```text
=======================================================================
SMRITI PRODUCT CONSTITUTION TEST STATUS REPORT
=======================================================================
RULE     SEVERITY   STATUS        DETAILS
-----------------------------------------------------------------------
SPC-001  Critical   PASS          0 violations across 47 HTML files
SPC-002  Major      ADR-EXEMPT    ADR-0012 bypasses duplicate check
SPC-003  Critical   PASS          Refactor scan attached, 0 references
SPC-004  Critical   PASS          Commit hash verified in live log
SPC-005  Critical   PASS          No fabrication flags detected
SPC-006  Major      WARNING       Scope mismatch: 2 additional files (Cleared)
SPC-007  Major      PASS          Evidence-first structure validated
-----------------------------------------------------------------------
RESULT: PASS (with 1 Warning, 0 Blocks)
=======================================================================
```

---

## Constitutional Test Suite Structure

Enforcement scripts live in `tests/constitution/` and are integrated into the Frappe bench test suite:

- `test_spc001_framework_leakage.py`: Scans all templates in `www/` and scripts in `public/js/` for framework leaks.
- `test_spc002_duplicate_policy.py`: Checks for existence of the `Prior-Art Search` header in the PR description markdown.
- `test_spc003_safe_refactor.py`: Scans git diff for deleted files and verifies a matching `.log` dependency scan exists in `/scratch/`.
- `test_spc004_evidence_first.py`: Validates that any report containing the word "done" or "fixed" also contains a commit hash or test log block.
- `test_spc005_honesty.py`: Connects to `git` to verify that all commit hashes cited in the agent's report actually exist in the repository log.
- `test_spc006_scope_integrity.py`: Compares modified file lists from git against the "Implemented Scope" list in the PR description.
- `test_spc007_evidence_first_doc.py`: Parses the agent's final report to ensure the `# Evidence` section precedes the `# Conclusion` section.

Run command:
`bench run-tests --app smriti_retail_os --module smriti_retail_os.tests.constitution`